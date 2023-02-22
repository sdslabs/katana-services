#!/bin/bash
tar -xf "${1}.tar.gz" -C challenge
cd challenge
eval "$(ssh-agent -s)"
ssh-add /tmp/ssh
ssh -o StrictHostKeyChecking=no git@github.com
cd "/opt/katana/challenge/${1}/"
git init
git config --global --add safe.directory "/opt/katana/challenge/${1}"
git remote add origin git@github.com:Perseus-Jackson477/notekeeper.git
git branch -M main
git add .
git stash
git pull origin main --allow-unrelated-histories