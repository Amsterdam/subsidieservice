#!/usr/bin/env python3
from lockfile.pidlockfile import PIDLockFile
import lockfile
import sys
import os
import signal
import time
import click
import multiprocessing as mp
import warnings
import logging
import functools
import graypy
import atexit

#
# Filter deluge of Bunq warnings
warnings.filterwarnings('ignore', message='[bunq SDK beta]*')

# Options
MAX_RESTART_RETRIES = 5  # Watchdog attempts to restart cleanly before forcing
TIMEOUT = 60  # Time before watchdog attempts to restart

# Globals
FILEDIR = os.path.split(os.path.realpath(__file__))[0]
WORKDIR = os.path.realpath(os.path.join(FILEDIR, '..'))
PID_PATH = os.path.join(FILEDIR, 'db_update_daemon.pidfile')
WATCHDOG_PATH = os.path.join(FILEDIR, 'db_update_watchdog.pidfile')
UPDATE_PATH = os.path.join(FILEDIR, 'db_update_daemon.updated')
LOG_PATH = os.path.join(FILEDIR, 'db_update_daemon.log')

# kibana
LOGSTASH_HOST = os.getenv('LOGSTASH_HOST', '127.0.0.1')
LOGSTASH_PORT = int(os.getenv('LOGSTASH_GELF_UDP_PORT', 12201))

DAEMONLOCK = PIDLockFile(PID_PATH)
WATCHDOGLOCK = PIDLockFile(WATCHDOG_PATH)

PROCESS = 'Launch Script'

LOGGER = logging.getLogger('db_update_daemon')
LOGGER.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_PATH)
formatter = logging.Formatter(
    '%(asctime)s - Daemon -  %(levelname)s - %(message)s'
)
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
LOGGER.addHandler(fh)

# write to stderr
sh = logging.StreamHandler()
sh.setFormatter(formatter)
LOGGER.addHandler(sh)

gh = graypy.GELFHandler(LOGSTASH_HOST, LOGSTASH_PORT)
gh.setLevel(logging.DEBUG)
LOGGER.addHandler(gh)


class DaemonStatus:
    """
    Object to track status of the daemon process and display nicely.
    """
    def __init__(self, status='Not yet started'):
        self.status = status

        self.total_items = 0
        self.current_item = 0
        self.started = ''
        self.total_updates = 0
        self.last_update = ''
        self.last_update_unix = time.time()

        self._sigterm = False

    def increment_total_updates(self):
        """Record an update and write to the updatefile."""
        self.total_updates += 1
        self.last_update = self.now()
        self.last_update_unix = time.time()

        write_update()

    def mark_started(self):
        """Indicate that the daemon has started running"""
        self.started = self.now()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, stat: str):
        """Changing the status implies resetting the number of items being
        looped over."""
        self.total_items = 0
        self._status = stat
        LOGGER.debug(f'Status: {stat}')

    @property
    def pid(self):
        return DAEMONLOCK.read_pid()

    @property
    def sigterm(self):
        return self._sigterm

    @sigterm.setter
    def sigterm(self, sig: bool):
        if sig:
            LOGGER.info('Daemon sigterm received')
        self._sigterm = sig

    @staticmethod
    def now():
        """Return the current time."""
        return time.strftime('%D %T')

    def __str__(self):
        msg = f'Current status: {self.status}'
        if self.total_items:
            msg += f' (now on item {self.current_item+1} of {self.total_items})'

        if self.started:
            msg += f'.\ndb_update_daemon running since {self.started}'

        if self.total_updates:
            msg += f'.\nTotal updates made: {self.total_updates} '\
                + f'(last update at {self.last_update})'

        msg += f'.\ndb_update_daemon\'s PID is {self.pid}.\n'
        return msg


STATUS = DaemonStatus()


class AbortException(Exception):
    """Exception to be raised on SIGABRT (force kill)."""
    pass


def log_exceptions(func: callable):
    """Decorator for the top level functions (main & watchdog loop) to
    ensure that all exceptions are logged."""

    @functools.wraps(func)
    def _wrapped(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            LOGGER.exception("Uncaught exception, exiting")
            os._exit(-1)

    return _wrapped


# ## Update functions
# These functions are to be called sequentially in the main daemon loop. Each
# update function should update one set of database objects and be considerate
# of external rate limits.

def update_masters():
    """
    For each master in db.masters, get the balance and transactions from Bunq,
    and update these in the database, along with the last updated time.

    Masters that cannot be found are not updated.

    :return:
    """
    global STATUS, service, CTX
    STATUS.status = 'Updating Master Accounts'

    master_list = service.mongo.get_collection(CTX.db.masters)
    STATUS.total_items = len(master_list)

    for i, master in enumerate(master_list):
        STATUS.current_item = i
        updated_master = master.copy()

        try:
            acct = service.bunq.read_account(master['bunq_id'])
            sleep_or_terminate(2)
            if STATUS.sigterm:
                break
            payments = service.bunq.get_payments(master['bunq_id'])

        except service.exceptions.NotFoundException as e:
            LOGGER.exception(
                f'Error in looking up master with id {master["id"]}, continuing'
            )
            sleep_or_terminate(3)
            continue

        updated_master['balance'] = acct['balance']
        updated_master['description'] = acct['description']
        updated_master['transactions'] = payments
        updated_master['last_updated'] = service.utils.now()

        service.mongo.update_by_id(
            master['id'],
            updated_master,
            CTX.db.masters
        )

        STATUS.increment_total_updates()

        sleep_or_terminate(2)
        if STATUS.sigterm:
            break


def update_subsidies():
    global STATUS, service, CTX
    import subsidy_service as service
    STATUS.status = 'Updating subsidies'

    STATUSCODE = service.subsidies.STATUSCODE

    subsidy_list = service.mongo.get_collection(CTX.db.subsidies)
    STATUS.total_items = len(subsidy_list)

    for i, subsidy in enumerate(subsidy_list):
        STATUS.current_item = i
        updated_subsidy = subsidy.copy()

        if subsidy['status'] == STATUSCODE.CLOSED:
            # skip updating
            continue

        # only need shares for PENDING_ACCEPT and OPEN subsidies
        get_share_statuscodes = [STATUSCODE.PENDING_ACCEPT, STATUSCODE.OPEN]
        full_read = (subsidy['status'] in get_share_statuscodes)

        master = service.mongo.get_by_id(
            subsidy['master']['id'],
            CTX.db.masters
        )

        if not master:
            # master not found -> no access, don't update
            LOGGER.warning(
                f'Master not found for subsidy {subsidy["id"]}, continuing'
            )
            sleep_or_terminate(2)
            continue
        else:
            updated_subsidy['master'] = master

        try:
            acct = service.bunq.read_account(
                subsidy['account']['bunq_id'],
                full=full_read
            )
            sleep_or_terminate(2)

            if STATUS.sigterm:
                break

            payments = service.bunq.get_payments(subsidy['account']['bunq_id'])

        except Exception as e:
            LOGGER.exception(
                f'Unable to update account info for subsidy {subsidy["id"]}, continuing'
            )
            sleep_or_terminate(2)
            continue

        if STATUS.sigterm:
            break

        acct['transactions'] = payments

        acct['bunq_id'] = acct.pop('id')

        if full_read and 'shares' in acct:
            if len(acct['shares']) > 0:
                share_status = acct['shares'][0]['status']

                if share_status == 'ACCEPTED':
                    updated_subsidy['status'] = STATUSCODE.OPEN
                elif share_status in ['CANCELLED', 'REVOKED',
                                      'REJECTED']:
                    updated_subsidy['status'] = STATUSCODE.SHARE_CLOSED
            acct.pop('shares')

        if subsidy['status'] == STATUSCODE.PENDING_ACCOUNT:
            sleep_or_terminate(1)
            try:
                # check for new account creation
                new_share = service.bunq.create_share(
                    subsidy['account']['bunq_id'],
                    subsidy['recipient']['phone_number']
                )
                updated_subsidy['status'] = STATUSCODE.PENDING_ACCEPT
                sleep_or_terminate(1)
            except:
                pass

        updated_subsidy['account'] = acct
        updated_subsidy['last_updated'] = service.utils.now()
        service.mongo.update_by_id(
            subsidy['id'],
            updated_subsidy,
            CTX.db.subsidies
        )

        STATUS.increment_total_updates()
        sleep_or_terminate(1)
        if STATUS.sigterm:
            break


# ## Daemon loops
# The main loops that are spawned as background processes on daemon start.
@log_exceptions
def watchdog_loop(timeout: float):
    """Watch the main loop and restart if no progress is being made. Relies on
    main_loop writing regularly to the update file. After the max retries,
    will force restart.
    """
    global STATUS, WATCHDOGLOCK, DAEMONLOCK, PROCESS

    PROCESS = 'Watchdog'

    # only one watchdog
    WATCHDOGLOCK.acquire()

    # log on exit
    atexit.register(lambda: LOGGER.info('Watchdog exiting'))

    # no terminal output
    sys.stdout = open(os.devnull)
    sys.stderr = open(os.devnull)

    tries = 0

    while not STATUS.sigterm:
        # get the last update time
        try:
            with open(UPDATE_PATH, 'r') as h:
                raw = h.read()
        except FileNotFoundError:
            continue

        if raw:
            last_update = float(raw)
            current_time = time.time()

            # take action if required
            if current_time - last_update > timeout:
                tries += 1

                # Unlock if process is dead
                if DAEMONLOCK.is_locked():
                    try:
                        os.kill(DAEMONLOCK.read_pid(), 0)
                    except ProcessLookupError:
                        LOGGER.warning('Daemon process dead, respawning')
                        os.remove(PID_PATH)

                # force restart
                if tries > MAX_RESTART_RETRIES:
                    LOGGER.error('Max retries reached, force killing')
                    if DAEMONLOCK.is_locked():
                        kill_daemon(watchdog=False, force=True)

                    try:
                        spawn_daemon()
                        tries = 0
                    except:
                        LOGGER.exception("Error in starting daemon, will retry")

                # gently restart
                else:
                    LOGGER.warning(
                        'Timeout, trying to restart daemon '
                        + f'({tries}/{MAX_RESTART_RETRIES})...'
                    )
                    kill_daemon(watchdog=False, force=False)
                    try:
                        spawn_daemon()
                        tries = 0
                    except:
                        # If process hasn't exited yet, try again on next iter
                        # Don't wait on process dying in case it has hung
                        LOGGER.exception(
                            "Daemon not successfully respawned, will retry"
                        )

        sleep_or_terminate(timeout)

    LOGGER.info('Kill signal received, watchdog exiting gracefully')
    WATCHDOGLOCK.release()


@log_exceptions
# @wait_for_connection
def main_loop():
    """Update the database entries continually.

    Assumes that update functions are patient and won't overload external APIs.
    If a RateLimitException is raised, back off and sleep for a long time.

    :return:
    """
    global service, CTX, STATUS, PROCESS

    # no terminal output
    sys.stdout = open(os.devnull)
    sys.stderr = open(os.devnull)

    # log on exit
    atexit.register(lambda: LOGGER.info('Daemon exiting'))

    PROCESS = 'Daemon'

    try:
        DAEMONLOCK.acquire()
    except lockfile.AlreadyLocked:
        if str(os.getpid()) == DAEMONLOCK.read_pid():
            LOGGER.info('Restarting main loop within existing process')
        else:
            raise

    STATUS.status = 'Initializing daemon'

    if STATUS.sigterm:
        LOGGER.info('Kill signal recieved, daemon exiting gracefully')
        DAEMONLOCK.release()
        return

    # only import service after forking, as otherwise external connections
    # (e.g. to mongo) can become unstable.
    service = __import__('subsidy_service', globals(), locals())
    CTX = service.config.Context

    write_update()

    # indicate startup
    STATUS.status = 'Starting subsidy service'
    STATUS.mark_started()

    while not STATUS.sigterm:
        try:
            update_masters()

            sleep_or_terminate(10)
            if STATUS.sigterm:
                break

            update_subsidies()

        except service.exceptions.RateLimitException:
            sleep_mins = 15
            LOGGER.exception(
                f'Rate limit hit, sleeping for {sleep_mins} minutes'
            )
            STATUS.total_items = None
            STATUS.status = \
                f'Rate Limit Exception - sleeping for {sleep_mins} minutes.'
            time.sleep(sleep_mins*60)
            continue

    LOGGER.info('Kill signal recieved, daemon exiting gracefully')
    DAEMONLOCK.release()


# ## Signal Handlers
# See docs for signal.signal for more info. Each signal handler should be
# registered in start_daemon using signal.signal(<signal>, <handler>).

def handle_cont(signum, frame):
    """Print the status message"""
    global STATUS
    LOGGER.info(STATUS.__str__().replace('\n', ' '))


def handle_hup(signum, frame):
    """Don't exit if terminal closed"""
    pass


def handle_term(signum, frame):
    """Signal that the daemon should terminate at next opportunity"""
    global STATUS
    STATUS.sigterm = True


def handle_abort(signum, frame):
    """Remove the current PID and update files, and raise AbortException."""
    LOGGER.error('Force Kill signal recieved, raising AbortException')

    pid = os.getpid()

    if pid == DAEMONLOCK.read_pid():
        DAEMONLOCK.break_lock()
        raise AbortException('Daemon force killed')

    elif pid == WATCHDOGLOCK.read_pid():
        WATCHDOGLOCK.break_lock()

        if os.path.exists(UPDATE_PATH):
            os.remove(UPDATE_PATH)
        raise AbortException('Watchdog force killed')

    raise AbortException


# ## File actions and responses
def write_update():
    """Record the current time in the update file."""
    with open(UPDATE_PATH, 'w') as h:
        h.write(str(time.time())+'\n')


def touch(path):
    """Create empty file if it doesn't exist."""
    with open(path, 'a'):
        pass


def exit_if_locked():
    """Exit with status 1 if the daemon is running"""
    if DAEMONLOCK.is_locked():
        LOGGER.warning(
            'db_update_daemon already running '
            + f'with with PID {DAEMONLOCK.read_pid()}.'
        )
        os._exit(1)


def exit_if_unlocked():
    """Exit with status 1 if the daemon is not running"""
    if not DAEMONLOCK.is_locked():
        LOGGER.warning(
            'db_update_daemon is not running.'
        )
        os._exit(1)


# ## Blocking calls
# These are functions that will halt execution until some condition is met

def wait_until_unlocked(watchdog=False):
    while DAEMONLOCK.is_locked():
        time.sleep(0.1)

    while WATCHDOGLOCK.is_locked() and watchdog:
        time.sleep(0.1)


def wait_until_locked(watchdog=False):
    while not DAEMONLOCK.is_locked():
        time.sleep(0.1)

    while not WATCHDOGLOCK.is_locked() and watchdog:
        time.sleep(0.1)


def sleep_or_terminate(seconds):
    """Sleep for the inidcated time. Returns early if a sigterm is detected."""
    global STATUS
    start = time.time()
    while (time.time() - start < seconds) and not STATUS.sigterm:
        time.sleep(0.1)


# ## Non blocking process calls
# These functions should send signals or spawn processes and return immediately,
# allowing the current thread to continue execution. If a break is required,
# use the blocking calls

def spawn_daemon():
    """Spawn a new process for main_loop if DAEMONLOCK is not locked"""
    if DAEMONLOCK.is_locked():
        raise lockfile.AlreadyLocked('Daemon already running')
    main_proc = mp.Process(target=main_loop)
    main_proc.start()
    LOGGER.info(f'Started main process on {main_proc.pid}')


def spawn_watchdog():
    """Spawn a new process for watchdog_loop if WATCHDOGLOCK is not locked"""
    if WATCHDOGLOCK.is_locked():
        raise lockfile.AlreadyLocked('Watchdog already runing')
    watchdog_proc = mp.Process(target=watchdog_loop, args=(TIMEOUT,))
    watchdog_proc.start()
    LOGGER.info(f'Started watchdog process on {watchdog_proc.pid}')


def start_daemon(watchdog=True):
    """Initialize the update file, set up signal handlers, and spawn the main
    loop (and watchdog if requested).
    """
    touch(UPDATE_PATH)
    write_update()

    os.chdir(WORKDIR)

    signal.signal(signal.SIGTERM, handle_term)
    signal.signal(signal.SIGCONT, handle_cont)
    signal.signal(signal.SIGHUP, handle_hup)
    signal.signal(signal.SIGTSTP, handle_hup)
    signal.signal(signal.SIGABRT, handle_abort)

    spawn_daemon()

    if watchdog:
        time.sleep(0.5)
        spawn_watchdog()


def kill_daemon(watchdog=False, force=False):
    """Kill the daemon and optionally the watchdog. If force=True, sends a
    SIGABRT, else sends a SIGTERM. Attempts cleanup of persisting .pidfiles."""
    global STATUS

    if force:
        sig = signal.SIGABRT
    else:
        sig = signal.SIGTERM

    if watchdog and WATCHDOGLOCK.is_locked():
        STATUS.status = 'Killing watchdog'
        try:
            os.remove(UPDATE_PATH)
        except FileNotFoundError:
            pass

        try:
            os.kill(WATCHDOGLOCK.read_pid(), sig)
        except ProcessLookupError:
            WATCHDOGLOCK.break_lock()

    if DAEMONLOCK.is_locked():
        STATUS.status = 'Killing daemon'
        try:
            os.kill(DAEMONLOCK.read_pid(), sig)
        except ProcessLookupError:
            DAEMONLOCK.break_lock()

    if force:
        # Force remove the pidfiles
        time.sleep(1)
        if watchdog and WATCHDOGLOCK.is_locked():
            os.remove(WATCHDOG_PATH)
        if DAEMONLOCK.is_locked():
            os.remove(PID_PATH)


def restart_daemon(watchdog=True, force=False):
    """Kill db_update_daemon and restart it. Will block until successful exit.
    """
    kill_daemon(watchdog, force)
    wait_until_unlocked(watchdog)
    start_daemon(watchdog)


# ## Command line interface functions

@click.group()
def cli():
    """
    CLI for the Subsidy Service database update daemon.

    The DB Update Daemon spawns two background processes before exiting.
    The main process is the update loop, which will get information on various
    database objects from external sources and cache this in the database. In
    case this process hangs or dies, a second watchdog process monitors the
    progress and restarts the main process if necessary.

    Only one daemon may run at a time to prevent too many concurrent calls to
    external APIs. This is achieved using locking .pidfiles in the same
    directory as this script. An additional file (.update) is used to
    communicate progress of the main process to the watchdog.

    BUGS: Output only appears in the terminal where the script was initially
    called. If this terminal is closed, the daemon will continue running but
    the output from `db_update_daemon.py status` and the other commands will
    no longer be visible.

    Run `db_update_daemon.py COMMAND --help` for more information on the
    commands.
    """
    pass


@cli.command('start')
@click.option('-d', '--debug', is_flag=True, help='Log DEBUG messages')
def start_command(debug):
    """Start daemon if not already running.
    """
    exit_if_locked()
    if debug:
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.debug('Logging at DEBUG level')
    start_daemon(watchdog=True)
    wait_until_locked(watchdog=True)
    print('Daemon started with PID', DAEMONLOCK.read_pid())
    print('Watchdog started with PID', WATCHDOGLOCK.read_pid())
    os._exit(0)


@cli.command('status')
def info_command():
    """Display the status of the daemon if running."""
    exit_if_unlocked()
    os.kill(DAEMONLOCK.read_pid(), signal.SIGCONT)
    os._exit(0)


@cli.command('kill')
@click.option('-f', '--force', is_flag=True, help='Kill aggressively')
def kill_command(force):
    """Kill the daemon.

    Default behaviour is patient, sending a signal and waiting for the daemon's
    loop to reach an acceptable termination point (this may take around a
    minute). If the daemon is hanging for some reason, the --force option will
    interrupt the process. This will still attempt some cleanup but ongoing
    operations are not guaranteed to exit cleanly. Leftover .pidfiles may
    prevent future starts."""
    if not force:
        exit_if_unlocked()
    kill_daemon(watchdog=True, force=force)
    wait_until_unlocked(watchdog=True)
    os._exit(0)


@cli.command('restart')
@click.option('-d', '--debug', is_flag=True, help='Log DEBUG messages')
@click.option('-f', '--force', is_flag=True,
              help='Kill aggressively (see `db_update_daemon.py kill --help`)')
def restart_command(force, debug):
    """Kill the daemon if running and restart."""
    if debug:
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.debug('Logging at DEBUG level')

    if not force:
        exit_if_unlocked()

    restart_daemon(watchdog=True, force=force)
    wait_until_locked(watchdog=True)
    print('Daemon started with PID', DAEMONLOCK.read_pid())
    print('Watchdog started with PID', WATCHDOGLOCK.read_pid())
    os._exit(0)


if __name__ == '__main__':
    cli()
