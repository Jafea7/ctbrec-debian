#!/bin/sh -e

cd ${HOME}
java -Xmx192m -cp ctbrec-server-4.1.2-final.jar -Dctbrec.config.dir=/app/config -Dctbrec.config=server.json ctbrec.recorder.server.HttpServer
