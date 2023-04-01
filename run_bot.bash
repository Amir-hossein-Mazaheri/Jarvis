#!/bin/bash

db=`cat /run/secrets/db`
db_user=`cat /run/secrets/db_user` 
db_pass=`cat /run/secrets/db_pass` 

db_host="db"
db_port=5432

bot_token=`cat /run/secrets/bot_token`
bot_secret=`cat /run/secrets/bot_secret`

server_ip=`cat /run/secrets/server_ip`

export DB_URL="postgresql://$db_user:$db_pass@$db_host:$db_port/$db?schema=public"
export BOT_TOKEN=$bot_token
export BOT_SECRET=$bot_secret
export SERVER_IP=$server_ip

prisma generate
prisma migrate deploy

python main.py