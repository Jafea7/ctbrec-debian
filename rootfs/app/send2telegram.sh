#!/bin/sh

# send2telegram.sh ${absolutePath} ${modelName} ${siteName} ${localDateTime(YYYYMMDD-HHmmss)}

file="$1"
sheet="${file%.*}.jpg"
shift

content="$1"
shift
for i in $@
do
  content=`echo "${content} - ${i}"`
  echo "|${content}|"
done

curl --form photo=@$sheet --form caption="${content%%*( - )}" --form-string chat_id=$CHAT_ID "https://api.telegram.org/bot${TOKEN}/sendPhoto"
