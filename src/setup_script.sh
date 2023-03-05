mkdir challenge
cd challenge
typ=("web" "pwn")
for item in "${typ[@]}"
do
	mkdir "$item"
done
apt upgrade
apt-get update -y
apt install ssh -y -y -y
apt install git -y
ssh-keygen -t ed25519 -f /tmp/ssh -N ""
mv /opt/katana/patch_challenge.sh /usr/bin/patch_challenge
chmod +x /usr/bin/patch_challenge
git config --global user.email "123@idkwhatdayitisanymore.com"
git config --global user.name "KMN"
