#!/bin/sh

#Util for REST request - see the YAML for example calls.

USER=${1:-ricky}
PASS=${2:-7654321}
HOST=${3:-localhost}
PORT=${4:-8080}
BASE=${5:-v1}
ENDPOINT=${6:-master-accounts}
PAYLOAD=${7}
METHOD=${8:-POST}

if [ ! -z "$PAYLOAD" ]; then
    payload="-H \"Content-Type: application/json\" -d @$PAYLOAD"
else
    payload=""
fi

request="curl -u ${USER}:${PASS} $payload -X $METHOD http://$HOST:$PORT/$BASE/$ENDPOINT"

echo Submitting request: $request

$request

