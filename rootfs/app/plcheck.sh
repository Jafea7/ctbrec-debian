#!/bin/bash
# Server non-single file use only.
# plcheck.sh ${absolutePath}

[[ -d "${1}" ]] && [[ -f "${1%/}/playlist.m3u8" ]] && echo "#EXT-X-ENDLIST" >> "${1%/}/playlist.m3u8" || exit 0
