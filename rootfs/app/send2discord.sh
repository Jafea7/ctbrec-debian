#!/bin/sh

# send2discord.sh ${absolutePath} [${modelDisplayName} ${siteName} ${localDateTime(yyyyMMdd-HHmmss)} ...]

file="$1"
sheet="${file%.*}.jpg"
shift

if [ -z "$1" ]; then
  content="Contact sheet"
else
  content="$1"
  shift
  for i in $@
  do
    content=`echo "${content} - ${i}"`
  done
fi

curl -F 'payload_json={"username": "CTBRec", "content":"'"$content"'"}' -F "file1=@$sheet" $DISCORDHOOK
