#!/bin/bash
tar -xf "katana_${2}_${1}.tar.gz" -C challenge/${2}
eval "$(ssh-agent -s)"
ssh-add /tmp/ssh
ssh -o StrictHostKeyChecking=no git@github.com
cd "/opt/katana/challenge/${2}/${1}"
git init
git config --global --add safe.directory "/opt/katana/challenge/${2}/${1}"
git remote add origin git@github.com:Perseus-Jackson477/notekeeper.git
git branch -M main
git add .
git stash
git pull origin main --allow-unrelated-histories