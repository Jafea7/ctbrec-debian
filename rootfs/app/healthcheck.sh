#!/bin/bash
port=`grep -Po '"httpPort":\s(\d+)' "/app/config/${CTBVER}/server.json" | grep -Po '(\d+)$'`

curl -f http://localhost:$port || exit 1
