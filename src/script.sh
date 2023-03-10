#!/bin/bash
source /etc/profile
tar -xf "katana_${2}_${1}.tar.gz" -C challenge/${2}
cd "/opt/katana/challenge/${2}/${1}"
git init
git config --global --add safe.directory "/opt/katana/challenge/${2}/${1}"
curl -H "Content-Type: application/json" -X POST -d '{"name":"'${1}'","description":"'${1}'","private":true}' "http://$GOGS/api/v1/user/repos?token=$PASSWORD"
curl -H "Content-Type: application/json" -X POST -d '{ "type": "gogs", "config": { "url": "https://random.free.beeceptor.com","content_type": "json"},"events": ["push"],"active": true}' "http://$GOGS/api/v1/repos/$USERNAME/${1}/hooks?token=$PASSWORD"
git remote add origin "http://$PASSWORD@$GOGS/$USERNAME/${1}.git"
git branch -M master
git checkout master
git add .
git commit -m "initial commit"
git push -u origin master -f                                                                                                                                                                                 ~                                       