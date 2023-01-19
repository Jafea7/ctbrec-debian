#!/bin/sh

# send2http.sh ${absolutePath} [${modelName} ${localDateTime(YYYYMMDD-HHmmss)} ...]

file="$1"
rel=`echo ${file} | cut -c 15-`
sheet="${file%.*}.jpg"

length=`/app/ffmpeg/ffmpeg -i "$file" 2>&1 | grep "Duration" | cut -d ' ' -f 4 | sed s/,// | sed 's@\..*@@g'`
shift

args=`echo $@ | base64`

if [ -z ${CURL_GET} ]; then
    args="-F file=${rel} -F sheet=@$sheet -F duration=${length} -F argv=${args}" 
else
    args="-G --data-urlencode file=${rel} --data-urlencode duration=${length} --data-urlencode argv=${args}" 
fi

curl ${args} ${CURL_ARGS} "${HTTP_URL}"