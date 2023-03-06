#!/bin/bash
tar -xf "katana_${2}_${1}.tar.gz" -C challenge/${2}
cd "/opt/katana/challenge/${2}/${1}"
git init
git config --global --add safe.directory "/opt/katana/challenge/${2}/${1}"
git remote add origin https://Personalaccesstokenhere@github.com/Perseus-Jackson477/notekeeper.git
git branch -M main
git add .
git stash
git pull origin main --allow-unrelated-histories
