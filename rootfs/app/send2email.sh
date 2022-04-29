#!/bin/sh

# send2email.sh ${absolutePath} [${modelDisplayName} ${siteName} ${localDateTime(yyyyMMdd-HHmmss)} ...]

file="$1"
sheet="${file%.*}.jpg"
name=`basename $sheet`
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

encoded=`base64 $sheet`

echo -e "MIME-Version: 1.0\nSubject: $content\nContent-Type: multipart/mixed;\n  boundary=\"Delimiter\"\n\n--Delimiter\nContent-Type: image/jpeg;\n  name=$name\nContent-Disposition: attachment;\n  filename=$name\nContent-Transfer-Encoding: base64\n\n$encoded\n--Delimiter--\n" > /app/captures/temp.txt

curl --url "$MAILSERVER" --ssl-reqd --mail-from "$MAILFROM" --mail-rcpt "$MAILTO" --upload-file '/app/captures/temp.txt' --user "$MAILFROM:$MAILPASS"

rm /app/captures/temp.txt