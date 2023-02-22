#!/bin/bash
tar -xf $1 -C challenge
cd challenge
result= 'ls'
cd $result
eval "$(ssh-agent -s)"
ssh-add /tmp/ssh
ssh -o StrictHostKeyChecking=no git@github.com
git init /opt/katana/challenge/$result
git --git-dir /opt/katana/challenge/$result/.git remote add origin git@github.com:Perseus-Jackson477/notekeeper.git
git config --global --add safe.directory /opt/katana/challenge/$result
git pull origin main --allow-unrelated-histories