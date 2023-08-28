#!/bin/bash
if [ $# -ne 2 ]; then
    echo "Usage: $0 <team_name> <flag>"
    exit 1
fi

source /etc/profile
team_name=$USERNAME
challenge_name=$1
flag=$2
url="http://kashira-svc.katana.svc.cluster.local/receive-flag"
hashed_password=$(echo -n "${PASSWORD}" | openssl dgst -sha256 -hex| awk '{print $2}')
encrypted_flag=$(echo -n "$flag" | openssl aes-256-cbc -e -a -salt -pbkdf2 -iter 10000 -pass "pass:${hashed_password}")

data="{\"challenge_name\": \"$challenge_name\", \"encrypted_flag\": \"$encrypted_flag\",\"team_name\": \"$team_name\"}"

response=$(curl -s -X POST -H "Content-Type: application/json" -d "$data" $url)

if [ $? -eq 0 ]; then
    echo "$response"
else
    echo "Flag submission failed"
fi
