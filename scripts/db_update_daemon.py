#!/usr/bin/env python3
import daemon
from daemon.pidfile import PIDLockFile
import sys
import os
import signal
import time
import click

# Globals
filedir = os.path.split(os.path.realpath(__file__))[0]
PID_PATH = os.path.join(filedir, 'db_update_daemon.pidfile')
PIDFILE = PIDLockFile(PID_PATH, timeout=1)
PID = PIDFILE.read_pid()


class DaemonStatus():
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
        self.pid = PID

    def increment_total_updates(self):
        self.total_updates += 1
        self.last_update = self.now()

    def mark_started(self):
        self.started = self.now()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, stat: str):
        self.total_items = 0
        self._status = stat


    @staticmethod
    def now():
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

        msg += f'.\ndb_update_daemon\'s PID is {self.pid}.'
        return msg


STATUS = DaemonStatus()


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
            time.sleep(1)
            payments = service.bunq.get_payments(master['bunq_id'])

        except service.exceptions.NotFoundException:
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

        if i < len(master_list)-1:
            # don't both sleeping on laast list entry
            time.sleep(1)


def update_subsidies():
    global STATUS, service, CTX
    STATUS.status = 'Updating subsidies'
    time.sleep(10)
    pass


def info_handler(signum, frame):
    """Print the status message"""
    global STATUS
    print(STATUS.__str__())


def main_loop():
    # only do imports after fork
    global service, CTX

    try:
        service = __import__('subsidy_service', globals(), locals())
        CTX = service.config.Context
    except SystemExit:
        print('Terminating graciously')
        raise

    global STATUS

    STATUS.status = 'Starting subsidy service'
    STATUS.mark_started()

    while True:
        try:
            update_masters()
            time.sleep(1)
            update_subsidies()
            time.sleep(1)
        except SystemExit:
            print('Terminating graciously')
            raise
        except service.exceptions.RateLimitException:
            sleep_mins = 15
            STATUS.total_items = None
            STATUS.status = \
                f'Rate Limit Exception - sleeping for {sleep_mins} minutes.'
            time.sleep(sleep_mins*60)
            continue


def exit_if_locked():
    """Exit with status 1 if the daemon is running"""
    if PIDFILE.is_locked():
        print(
            'db_update_daemon already running '
            + f'with with PID {PIDFILE.read_pid()}.'
        )
        sys.exit(1)


def exit_if_unlocked():
    """Exit with status 1 if the daemon is not running"""
    if not PIDFILE.is_locked():
        print(
            'db_update_daemon is not running.'
        )
        sys.exit(1)


def start_daemon():
    """Run main_loop() until SIGTERM is received, then raise SystemExit
    exception (should be caught and handled in main_loop before
    breaking out of the loop).
    """
    global STATUS
    STATUS.status = 'Initializing daemon'

    exit_if_locked()

    context = daemon.DaemonContext(
        detach_process=True,
        stdout=sys.stdout,
        pidfile=PIDFILE,
        working_directory=os.path.realpath(os.path.join(filedir, '..'))
    )

    context.signal_map[signal.SIGINFO] = info_handler
    # context.signal_map[signal.SIGABRT] = context.terminate
    # context.signal_map[signal.SIGKILL] = context.terminate
    # context.signal_map[signal.SIGTERM] = context.terminate
    # context.signal_map[signal.SIGSTOP] = context.terminate

    context.open()
    with context:
        print(
            'Starting db_update_daemon started '
            + f'with with PID {context.pidfile.read_pid()}.'
        )
        STATUS.pid = context.pidfile.read_pid()
        main_loop()


# set up command line interface
@click.group()
def cli():
    pass


@cli.command('start')
def start_command():
    """Start db_update_daemon if not already running"""
    exit_if_locked()
    start_daemon()


@cli.command('status')
def info_command():
    """Display the status of the db_update_daemon if running"""
    exit_if_unlocked()
    os.kill(PID, signal.SIGINFO)


@cli.command('kill')
def kill_command():
    """Kill db_update_daemon if running"""
    exit_if_unlocked()
    os.kill(PID, signal.SIGTERM)
    PIDFILE.break_lock()


@cli.command('restart')
def restart_command():
    """Kill db_update_daemon if running and restart it"""
    exit_if_unlocked()
    os.kill(PID, signal.SIGTERM)
    PIDFILE.break_lock()
    start_daemon()


if __name__ == '__main__':
    cli()
