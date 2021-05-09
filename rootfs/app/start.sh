#!/bin/sh -e

cd ${HOME}
java -Xmx256m -cp ctbrec-server-4.2.1-final.jar -Dfile.encoding=utf-8 -Dctbrec.config.dir=/app/config -Dctbrec.config=server.json ctbrec.recorder.server.HttpServer
