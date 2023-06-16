mkdir challenge
cd challenge
apt upgrade
apt-get update -y
apt install git curl nano vim -y
mv $ROOT_DIRECTORY/patch_challenge.sh /usr/bin/patch-challenge
mv $ROOT_DIRECTORY/setup.sh /usr/bin/setup
chmod +x /usr/bin/patch_challenge
chmod +x /usr/bin/setup
git config --global user.email $HOSTNAME@katana.com
git config --global user.name $HOSTNAME
rm -rf $ROOT_DIRECTORY/requirements.txt
