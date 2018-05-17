#!/usr/bin/env bash
/etc/init.d/cron start
python3 /usr/src/scripts/db_update_daemon.py start
python3 -m swagger_server

