#!/bin/sh

# Simple shell script that will send the contact sheet to a designated Discord channel

# send2discord.sh ${modelDisplayName} ${siteName} ${localDateTime(yyyyMMdd-HHmmss)} ${absolutePath}

# To set your Discord Webhook, create an environment variable called DISCORDHOOK that contains the webhook address

model="$1"
site="$2"
rectime="$3"
file="$4"

content="${model} - ${site} - ${rectime}"
sheet="${file%.*}.jpg"

curl -F 'payload_json={"username": "CTBRec", "content":"'"$content"'"}' -F "file1=@$sheet" $DISCORDHOOK