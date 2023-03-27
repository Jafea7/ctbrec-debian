#!/bin/bash
# Server non-single file use only.
# plcheck.sh ${absolutePath}

path="${1%/}/playlist.m3u8"
if [[ -f "${path}" ]]; then
  if [[ $(tail -1 "${path}" | xargs) != "#EXT-X-ENDLIST" ]]; then
    echo "#EXT-X-ENDLIST" >> "${path}"
  fi
fi
