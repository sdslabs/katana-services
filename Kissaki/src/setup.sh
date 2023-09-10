#!/bin/bash
source /etc/profile
tar -xf "/opt/kissaki/kissaki_${1}.tar.gz" -C /opt/kissaki/challenge-data
rm -rf "/opt/kissaki/kissaki_${1}.tar.gz"

