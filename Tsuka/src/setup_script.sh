mkdir challenge
cd challenge
apt upgrade
apt-get update -y
apt install git curl nano vim -y
mv /opt/katana/patch_challenge.sh /usr/bin/patch-challenge
mv /opt/katana/setup.sh /usr/bin/setup
chmod +x /usr/bin/patch-challenge
chmod +x /usr/bin/setup
git config --global user.email $HOSTNAME@katana.com
git config --global user.name $HOSTNAME
rm -rf /opt/katana/requirements.txt
