#!/bin/sh -e

PUID="${PUID:-1000}"
PGID="${PGID:-1000}"
TZ="${TZ:-UTC}"

export HOME=/app

# Use existing group if GID exists, create ctbrec if not
if [ $(getent group ${PGID} | cut -d: -f3) ]; then
  grp="$(getent group ${PGID} | cut -d: -f1)"
else
  addgroup --gid "${PGID}" --system ctbrec
  grp="ctbrec"
fi

# Use existing user if UID exists, create ctbrec if not
if [ $(getent passwd ${PUID} | cut -d: -f1) ]; then
  usr="$(getent passwd ${PUID} | cut -d: -f1)"
else
  adduser --disabled-password --gecos "" --no-create-home --home "${HOME}" --ingroup "${grp}" --uid "${PUID}" ctbrec
  usr="ctbrec"
fi

mkdir -p /app/config
chown -R ${PUID}:${PGID} ${HOME}
chmod -R ugo=rwx ${HOME} && chmod -R g+s ${HOME}
cp --verbose --no-clobber "/app/defaults/server.json" "/app/config/"
chmod 666 /app/config/server.json

# Start CTBRec
su -p -c "${HOME}/start.sh" ${usr}
