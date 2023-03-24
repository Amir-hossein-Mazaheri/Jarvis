#!/bin/bash

ls -la
echo here is requirements:
cat requirements.txt

db=`cat /run/secrets/db`
db_user=`cat /run/secrets/db_user` 
db_pass=`cat /run/secrets/db_pass` 

db_host="db"
db_port=5432

bot_token=`cat /run/secrets/bot_token`

export DB_URL="postgresql://$db_user:$db_pass@$db_host:$db_port/$db?schema=public"
export BOT_TOKEN=$bot_token

prisma generate
prisma migrate deploy

python main.py