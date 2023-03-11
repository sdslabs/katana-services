mkdir challenge
cd challenge
typ=("web" "pwn")
for item in "${typ[@]}"
do
	mkdir "$item"
done
apt upgrade
apt-get update -y
apt install git -y
apt install curl -y
apt install nano -y
mv /opt/katana/patch_challenge.sh /usr/bin/patch_challenge
mv /opt/katana/setup.sh /usr/bin/setup
chmod +x /usr/bin/patch_challenge
chmod +x /usr/bin/setup
git config --global user.email $HOSTNAME\@katana.com
git config --global user.name $HOSTNAME
apt install vim -y
rm -rf /opt/katana/requirements.txt
