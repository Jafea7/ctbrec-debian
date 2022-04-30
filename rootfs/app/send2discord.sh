#!/bin/sh

# send2discord.sh ${absolutePath} [${modelDisplayName} ${localDateTime(yyyyMMdd-HHmmss)} ...]

file="$1"
sheet="${file%.*}.jpg"
length=`/app/ffmpeg/ffmpeg -i "$file" 2>&1 | grep "Duration" | cut -d ' ' -f 4 | sed s/,// | sed 's@\..*@@g'`
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
content=`echo "${content}: ${length}"`

curl -F 'payload_json={"username": "CTBRec", "content":"'"$content"'"}' -F "file1=@$sheet" $DISCORDHOOK
