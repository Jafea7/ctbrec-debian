#!/bin/bash
dir="/app/config/${CTBVER}/recordings/"
json=$(find "$dir" -name "*.json")

for file in $json; do
  media=$(jq -r '.absoluteFile' "$file")
  stats=$(jq -r '.status' "$file")

  if [ ! -d "$media" ] && [ ! -e "$media" ] && [ "$stats" = "FINISHED" ]; then
    rm "$file"
  fi
done
