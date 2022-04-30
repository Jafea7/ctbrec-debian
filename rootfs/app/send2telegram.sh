#!/bin/sh

# send2telegram.sh ${absolutePath} [${modelName} ${localDateTime(YYYYMMDD-HHmmss)} ...]

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

curl --form photo=@$sheet --form caption="${content}" --form-string chat_id=$CHAT_ID "https://api.telegram.org/bot${TOKEN}/sendPhoto"
