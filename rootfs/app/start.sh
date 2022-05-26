#!/bin/sh -e

cd ${HOME}
# If logback.xml/server.log exists then redirect output to server.log on the host
# requires the server.log to be mapped by Docker.
if [ -f /app/config/logback.xml ] && [ -f /app/config/server.log ]; then
  java -Xmx256m -cp ctbrec-server-4.7.8-final.jar -Dfile.encoding=utf-8 -Dctbrec.config.dir=/app/config -Dctbrec.config=server.json ctbrec.recorder.server.HttpServer >> /app/config/server.log
else
  java -Xmx256m -cp ctbrec-server-4.7.8-final.jar -Dfile.encoding=utf-8 -Dctbrec.config.dir=/app/config -Dctbrec.config=server.json ctbrec.recorder.server.HttpServer
fi
