eval "$(ssh-agent -s)" > /dev/null 2>&1
ssh-add /tmp/ssh > /dev/null 2>&1
git add . > /dev/null 2>&1
git commit -m $1 > /dev/null 2>&1
git push -u origin main > /dev/null 2>&1