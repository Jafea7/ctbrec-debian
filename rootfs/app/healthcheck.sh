#!/bin/bash
port=`grep -Po '"httpPort":\s(\d+)' "./config/$ctbver/server.json" | grep -Po '(\d+)$'`

curl -f http://localhost:$port || exit 1
