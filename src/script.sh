#!/bin/bash
tar -xf "katana_${2}_${1}.tar.gz" -C challenge/${2}
cd "/opt/katana/challenge/${2}/${1}"
git init
git config --global --add safe.directory "/opt/katana/challenge/${2}/${1}"
git remote add origin https://$password@$gogs/$usernmame/${1}.git
git branch -M main
git checkout main
git add .
git commit -m "initial commit"
git push -u origin main -f