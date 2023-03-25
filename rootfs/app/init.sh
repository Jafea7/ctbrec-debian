#!/bin/sh -e
# Added updates by @tigobitties

echo "`date '+%T.%3N'` [Start]"
# Grab passed env variables or set defaults
PUID="${PUID:-1000}"
PGID="${PGID:-1000}"
TZ="${TZ:-UTC}"

# Set the home directory
export HOME=/app

echo "`date '+%T.%3N'` [Group]"
# Use existing group if GID exists, create ctbrec if not
if [ $(getent group ${PGID} | cut -d: -f3) ]; then
  grp="$(getent group ${PGID} | cut -d: -f1)"
else
  addgroup --gid "${PGID}" --system ctbrec
  grp="ctbrec"
fi

echo "`date '+%T.%3N'` [User]"
# Use existing user if UID exists, create ctbrec if not
if [ $(getent passwd ${PUID} | cut -d: -f1) ]; then
  usr="$(getent passwd ${PUID} | cut -d: -f1)"
else
  adduser --disabled-password --gecos "" --no-create-home --home "${HOME}" --ingroup "${grp}" --uid "${PUID}" ctbrec
  usr="ctbrec"
fi

echo "`date '+%T.%3N'` [Directories]"
# Set the owner/permissions of the home directory
if ! chown -R $PUID:$PGID "$HOME" 2>/dev/null; then
  echo - unable to change ownership of $HOME
fi
su -p $usr -c "chmod -R a+rwx,g+s $HOME" || true

# Loop while an internet connection is not available
echo "`date '+%T.%3N'` [Internet]"
while ! curl -Is -m 5  http://www.google.com | head -n 1 | grep 200
do
  echo "`date '+%T.%3N'` [Internet failed]: Waiting 30 seconds ..."
  sleep 30
done

echo "`date '+%T.%3N'` [CTBRec]"
# Start CTBRec as the user
su -p -c "${HOME}/start.sh" ${usr}
