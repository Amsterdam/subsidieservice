#!/usr/bin/env bash

set -u
set -e

MONGO_HOST=${MONGO_HOST:-subsidieservice-mongo.service.consul}
MONGO_DB=${MONGO_DB:-subsidieservice}
MONGO_PORT=${MONGO_PORT:-"27017"}
MONGO_USER=${MONGO_USER:-subsidieservice}
MONGO_PASSWORD=${MONGO_PASSWORD:-secret}
ENVIRONMENT=${ENVIRONMENT:-develop}

echo Generate Service Config
cat > /etc/subsidy_service/config/subsidy_service.ini <<EOF
;subsidy_service default configuration
[mongo]
    host=${MONGO_HOST}
    port=${MONGO_PORT}
[bunq]
    conf_path=/etc/subsidy_service/config/bunq.conf
[logging]
    server_path=/etc/subsidy_service/logs/server.log
    audit_path=/etc/subsidy_service/logs/audit.log
EOF

echo Start server
python3 -m swagger_server
