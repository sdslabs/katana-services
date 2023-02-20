#!/bin/bash
mv patch_challenge.sh /usr/bin/patch_challenge
mkdir $1
tar -xf $2 -C $1
cd $1
mkdir $2
result= 'ls'
cd $result
git init 
git branch --set-upstream-to "branch name comes here"