#!/bin/sh -e
# Added updates by @tigobitties

cd ${HOME}
JAVA_HOME="/opt/java/openjdk"
JAVA="/opt/java/openjdk/bin/java"

# Copy default settings if it doesn't exist
echo "`date '+%T.%3N'` [Defaults]"
cp --verbose --no-clobber "/app/defaults/server.json" "/app/config/"
chmod 666 /app/config/server.json

# Enable post-processing by default
[ ! -f "/app/config/dopp" ] && touch "/app/config/dopp"

$JAVA -Xms256m -Xmx768m -cp ctbrec-server-$CTBVER-final.jar -Dfile.encoding=utf-8 -Dctbrec.config.dir=/app/config -Dctbrec.config=server.json ctbrec.recorder.server.HttpServer
