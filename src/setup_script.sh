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
mv /opt/katana/patch_challenge.sh /usr/bin/patch_challenge
chmod +x /usr/bin/patch_challenge
git config --global user.email "vanshuppal2002@gmail.com"
git config --global user.name "Perseus-Jackson477"
