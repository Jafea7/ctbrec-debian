#!/bin/bash
# note2txt.sh ${absolutePath} ${modelName} ${siteName} ${modelNotes} [${recordingNotes}|"Misc text"]
txtfile="${1%.*}.txt"
model=$2
site=$3
modnote=$4
recnote=$5

{
  echo "Model: $model  Site: $site"
  echo "Model notes:"
  [ -n "$modnote" ] && echo "$modnote" || echo "None"
  echo "Other notes:"
  [ -n "$recnote" ] && echo "$recnote" || echo "None"
} > "$txtfile"
