#!/usr/bin/env bash

function require () {
  if ! type -p "$1" >/dev/null; then
    echo "$1" binary is missing
    exit 1
  fi
}

require diff
require patch

any5=/app/config/$(find /app/config -mindepth 1 -maxdepth 1 -type d -name '5.*' ! -name '*_backup_*' | cut -f4 -d/ | tail -1)

# a v5 config folder already exists, we've been through this
[ "$any5" != "/app/config/" ] && exit 0

latest5=/app/config/${CTBVER:-5.0.0}
latest5_config="$latest5/server.json"

# if the base config file is the same as the default, this must be a new install
diff /app/{defaults,config}/server.json >/dev/null && exit 0

# find the latest v4 config
latest4=/app/config/$(find /app/config -mindepth 1 -maxdepth 1 -type d -name '4.*' ! -name '*_backup_*' | cut -f4 -d/ | sort -t. -k2,2n -k 3,3n | tail -1)

# couldn't find a v4 config, but /app/config/server.json differs from defaults
[ "$latest4" = "/app/config/" ] && exit 0

# copy the latest v4 config folder to v5
if [ ! -d "$latest5" ]; then
  echo - attempting to migrate v4 config to v5

  latest4_config="$latest4/server.json"
  if [ -f "$latest4_config" ]; then
    echo - found the most recent config at "$latest4_config"
  else
    echo - unable to locate the server.json file in "$latest4"/
    exit 1
  fi

  echo - copying "$latest4" to "$latest5"
  cp -rp "$latest4" "$latest5" || exit 1
fi

# apply the diff
if [ ! -f "$latest5_config".v4 ]; then
  echo - applying configuration changes for v5
  patch -lz.v4 "$latest5_config" < ${0%.sh}.diff >/dev/null
fi

# check for patch failure
if [ -f "$latest5_config".rej ]; then
  echo =============================================================
  echo One or more configuration changes failed to apply.  You\'ll
  echo need to manually apply the changes below to the file:
  echo
  echo "$latest5_config"
  echo
  echo Refer to: https://bit.ly/3n0Ya6f
  echo =============================================================
  cat "$latest5_config".rej
  echo =============================================================
  echo When you\'re done, remove this file and restart the container:
  echo
  echo "$latest5_config".rej
  echo =============================================================
  exit 1
fi

exit 0
