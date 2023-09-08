#!/bin/bash
source /etc/profile
if [ ! -d "/opt/katana/challenge/${2}" ]; then
    mkdir "/opt/katana/challenge/${2}"
fi
tar -zxf "/opt/katana/katana_${2}_${1}.tar.gz" -C /opt/katana/challenge/${2}
rm -rf "/opt/katana/katana_${2}_${1}.tar.gz"
cd "/opt/katana/challenge/${2}/${1}"
if [ ! -d "/opt/katana/challenge/${2}/${1}/.git" ]; then
git init
git config --global --add safe.directory "/opt/katana/challenge/${2}/${1}"
curl -H "Content-Type: application/json" -X POST -d '{"name":"'${1}'","description":"'${1}'","private":true}' "http://$GOGS/api/v1/user/repos?token=$PASSWORD"
git remote add origin "http://$PASSWORD@$GOGS/$USERNAME/${1}.git"
git branch -M master
git checkout master
git add .
git commit -m "${1} challenge of $USERNAME" 
git push -u origin master -f
curl -H "Content-Type: application/json" -X POST -d '{ "type": "gogs", "config": { "url": "'"$BACKEND_URL"'","content_type": "json"},"events": ["push"],"active": true}' "http://$GOGS/api/v1/repos/$USERNAME/${1}/hooks?token=$PASSWORD"
curl -X PUT -H "Authorization: token $PASSWORD" -H "Content-Type: application/json" -d '{"permission": "admin"}' http://$GOGS/api/v1/repos/$USERNAME/${1}/collaborators/$ADMIN
fi