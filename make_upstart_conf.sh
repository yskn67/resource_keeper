#! /bin/bash

workspace=$(cd $(dirname $0) && pwd)

cat > resource_keeper.conf << EOS
description "slackbot for resource keeper"

start on runlevel [2345]
stop on runlevel [016]

chdir $workspace
exec python resource_keeper/app.py >> /var/log/resource_keeper.log 2>&1
respawn
EOS
