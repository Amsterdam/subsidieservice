#!/bin/sh

#!/bin/sh
curl https://public-api.sandbox.bunq.com/v1/sandbox-user -X POST \
    --header "Content-Type: application/json" \
    --header "Cache-Control: none" \
    --header "User-Agent: curl-request" \
    --header "X-Bunq-Client-Request-Id: $(date)randomId" \
    --header "X-Bunq-Language: nl_NL" \
    --header "X-Bunq-Region: nl_NL" \
    --header "X-Bunq-Geolocation: 0 0 0 0 000"
