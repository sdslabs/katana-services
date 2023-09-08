#!/bin/bash
source /etc/profile
tar -xf "/opt/kashira/kashira_${1}.tar.gz" -C /opt/kashira/flag-data
rm -rf "/opt/kashira/kashira_${1}.tar.gz"

