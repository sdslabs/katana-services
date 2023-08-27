#!/bin/bash
if [ $# -ne 2 ]; then
    echo "Usage: $0 <team_name> <flag>"
    exit 1
fi

team_name=$USERNAME
challenge_name=$1
flag=$2
namespace="katana"
service_name="kashira-svc"
url="http://$service_name.$namespace.svc.cluster.local/receive-flag"
encrypted_flag=$(echo -n "$flag" | openssl enc -e -aes256 -pass "pass:${PASSWORD}" -pbkdf2 -a)


data="{\"challenge_name\": \"$challenge_name\", \"encrypted_flag\": \"$encrypted_flag\",\"team_name\": \"$team_name\"}"

response=$(curl -s -X POST -H "Content-Type: application/json" -d "$data" $url)

if [ $? -eq 0 ]; then
    echo "POST request successful: $response"
else
    echo "POST request failed"
fi
