#!/bin/sh -e
# Added updates by @tigobitties

cd ${HOME}
JAVA_HOME="/opt/java/openjdk"
JAVA="/opt/java/openjdk/bin/java"

echo "`date '+%T.%3N'` [Defaults]"
cp --verbose --no-clobber "/app/defaults/server.json" "/app/config/"
chmod 666 /app/config/server.json

/app/migrate-config-v5.sh

# If logback.xml/server.log exists then redirect output to server.log on the host
# requires the server.log to be mapped by Docker.
if [ -f /app/config/logback.xml ] && [ -f /app/config/server.log ]; then
  $JAVA -Xmx256m -cp ctbrec-server-5.0.1-final.jar -Dfile.encoding=utf-8 -Dctbrec.config.dir=/app/config -Dctbrec.config=server.json ctbrec.recorder.server.HttpServer >> /app/config/server.log
else
  $JAVA -Xmx256m -cp ctbrec-server-5.0.1-final.jar -Dfile.encoding=utf-8 -Dctbrec.config.dir=/app/config -Dctbrec.config=server.json ctbrec.recorder.server.HttpServer
fi
