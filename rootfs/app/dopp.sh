#!/bin/bash
# dopp.sh
# Defers post-processing if file /app/config/dopp does not exist by failing

[[ -f "/app/config/dopp" ]] || exit 1
