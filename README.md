# Docker container for CTBRec server based on Debian/OpenJDK19

---

CTBRec is a streaming media recorder.

---

## Table of Content

   * [Docker container for CTBRec server](#docker-container-for-ctbrec-server)
      * [Table of Content](#table-of-content)
      * [Quick Start](#quick-start)
      * [Usage](#usage)
         * [Environment Variables](#environment-variables)
         * [Data Volumes](#data-volumes)
         * [Ports](#ports)
         * [Changing Parameters of a Running Container](#changing-parameters-of-a-running-container)
      * [Docker Compose File](#docker-compose-file)
      * [QNap Installs](#qnap-installs)
      * [Docker Image Update](#docker-image-update)
         * [Synology](#synology)
         * [unRAID](#unraid)
      * [Accessing the GUI](#accessing-the-gui)
      * [Shell Access](#shell-access)
      * [Default Web Interface Access](#default-web-interface-access)
      * [Persistent Log File](#persistent-log-file)
      * [Extras](#extras)

## Quick Start

**NOTE**: The Docker command provided in this quick start is given as an example
and parameters should be adjusted to your need.

Launch the CTBRec server docker container with the following command:
```
docker run -d \
    --name=ctbrec-debian \
    -p 8080:8080 \
    -p 8443:8443 \
    -v /home/ctbrec/media:/app/captures:rw \
    -v /home/ctbrec/.config/ctbrec:/app/config:rw \
    -e TZ=Australia/Sydney \
    -e PGID=1000 \
    -e PUID=1000 \
    jafea7/ctbrec-debian
```

Where:
  - `/home/ctbrec/.config/ctbrec`: This is where the application stores its configuration and any files needing persistency.
  - `/home/ctbrec/media`:          This is where the application stores recordings.
  - `TZ`:                          The timezone you want the application to use, files created will be referenced to this.
  - `PGID`:                        The Group ID that CTBRec will run under.
  - `PUID`:                        The User ID that CTBRec will run under.

Browse to `http://your-host-ip:8080` to access the CTBRec web interface, (or `https://your-host-ip:8443` if TLS is enabled).

**NOTE**: If it's your initial use of this image then a default config is copied that already has the web interface enabled along with TLS.

## Usage

```
docker run [-d] \
    --name=ctbrec-debian \
    [-e <VARIABLE_NAME>=<VALUE>]... \
    [-v <HOST_DIR>:<CONTAINER_DIR>[:PERMISSIONS]]... \
    [-p <HOST_PORT>:<CONTAINER_PORT>]... \
    jafea7/ctbrec-debian
```
| Parameter | Description |
|-----------|-------------|
| -d        | Run the container in the background.  If not set, the container runs in the foreground. |
| -e        | Pass an environment variable to the container.  See the [Environment Variables](#environment-variables) section for more details. |
| -v        | Set a volume mapping (allows to share a folder/file between the host and the container).  See the [Data Volumes](#data-volumes) section for more details. |
| -p        | Set a network port mapping (exposes an internal container port to the host).  See the [Ports](#ports) section for more details. |

### Environment Variables

To customize some properties of the container, the following environment
variables can be passed via the `-e` parameter (one for each variable).  Value
of this parameter has the format `<VARIABLE_NAME>=<VALUE>`.

| Variable       | Description                                  | Default |
|----------------|----------------------------------------------|---------|
|`TZ`| [TimeZone] of the container.  Timezone can also be set by mapping `/etc/localtime` between the host and the container. | `UTC` |
|`PGID`| Group ID that will be used to run CTBRec within the container. | `1000` |
|`PUID`| User ID that will be used to run CTBRec within the container. | `1000` |

### Data Volumes

The following table describes data volumes used by the container.  The mappings
are set via the `-v` parameter.  Each mapping is specified with the following
format: `<HOST_DIR>:<CONTAINER_DIR>[:PERMISSIONS]`.

| Container path  | Permissions | Description |
|-----------------|-------------|-------------|
|`/app/config`| rw | This is where the application stores its configuration, log and any files needing persistency. |
|`/app/captures`| rw | This is where the application stores recordings. |

### Ports

Here is the list of ports used by the container.  They can be mapped to the host
via the `-p` parameter (one per port mapping).  Each mapping is defined in the
following format: `<HOST_PORT>:<CONTAINER_PORT>`.  The port number inside the
container cannot be changed, but you are free to use any port on the host side.

| Port | Mapping to host | Description |
|------|-----------------|-------------|
| 8080 | Mandatory | Port used to serve HTTP requests. |
| 8443 | Mandatory | Port used to serve HTTPs requests. |

### Changing Parameters of a Running Container

As seen, environment variables, volume mappings and port mappings are specified
while creating the container.

The following steps describe the method used to add, remove or update
parameter(s) of an existing container.  The generic idea is to destroy and
re-create the container:

  1. Stop the container (if it is running):
```
docker stop ctbrec-debian
```
  2. Remove the container:
```
docker rm ctbrec-debian
```
  3. Create/start the container using the `docker run` command, by adjusting
     parameters as needed.

**NOTE**: Since all application's data is saved under the `/app/config` and
`/app/captures` container folders, destroying and re-creating a container is not
a problem: nothing is lost and the application comes back with the same state
(as long as the mapping of the `/app/config` and `/app/captures` folders
remain the same).

## Docker Compose File

Here is an example of a `docker-compose.yml` file that can be used with
[Docker Compose](https://docs.docker.com/compose/overview/).

Make sure to adjust according to your needs.  Note that only mandatory network
ports are part of the example.

```yaml
version: '2.1'
services:
  ctbrec-debian:
    image: jafea7/ctbrec-debian
    container_name: "CTBRec-Debian"
    environment:
      - TZ=Australia/Sydney
      - PGID=1000
      - PUID=1000
    ports:
      - "8080:8080"
      - "8443:8443"
    volumes:
      - "/home/ctbrec/.config/ctbrec:/app/config:rw"
      - "/home/ctbrec/media:/app/captures:rw"
    restart: "unless-stopped"
```

## QNap Installs

When you create the container using Container Station specify the PUID and PGID environment variables, (you can't do this later).

You may need to set `PGID = 0` and `PUID = 0`, ie. CTBRec runs as root within the container.

## Docker Image Update

If the system on which the container runs doesn't provide a way to easily update
the Docker image, the following steps can be followed:

  1. Fetch the latest image:
```
docker pull jafea7/ctbrec-debian
```
  2. Stop the container:
```
docker stop jafea7/ctbrec-debian
```
  3. Remove the container:
```
docker rm jafea7/ctbrec-debian
```
  4. Start the container using the `docker run` command.


**Updating using docker-compose:**
```
docker-compose pull && docker-compose up -d
```

### Synology

For owners of a Synology NAS, the following steps can be used to update a
container image.

  1.  Open the *Docker* application.
  2.  Click on *Registry* in the left pane.
  3.  In the search bar, type the name of the container (`jafea7/ctbrec-debian`).
  4.  Select the image, click *Download* and then choose the `latest` tag.
  5.  Wait for the download to complete.  A  notification will appear once done.
  6.  Click on *Container* in the left pane.
  7.  Select your CTBRec server container.
  8.  Stop it by clicking *Action*->*Stop*.
  9.  Clear the container by clicking *Action*->*Clear*.  This removes the
      container while keeping its configuration.
  10. Start the container again by clicking *Action*->*Start*.
  
  **NOTE**:  The container may temporarily disappear from the list while it is re-created.
---

### unRAID

For unRAID, a container image can be updated by following these steps:

  1. Select the *Docker* tab.
  2. Click the *Check for Updates* button at the bottom of the page.
  3. Click the *update ready* link of the container to be updated.

## Accessing the GUI

Assuming that container's ports are mapped to the same host's ports, the
interface of the application can be accessed with a web browser at:

```
http://<HOST IP ADDR>:8080
```
Or if TLS is enabled:

```
https://<HOST IP ADDR>:8443
```

## Shell Access

To get shell access to the running container, execute the following command:

```
docker exec -ti CONTAINER sh
```

Where `CONTAINER` is the ID or the name of the container used during its
creation (e.g. `ctbrec-debian`).

## Default Web Interface Access

After a fresh install and the web interface is enabled, the default login is:
  - Username: `ctbrec`
  - Password: `sucks`

Change the username/password via the WebUI, you will need to log into it again after saving.

**NOTE**: A fresh start of the image will include a current default server.json, (if it doesn't exist already), with the following options set:
  - `"downloadFilename": "$sanitize(${modelName})_$sanitize(${siteName})_$format(${localDateTime},yyyyMMdd-hhmmss).${fileSuffix}"`
  - `"recordingsDirStructure": "ONE_PER_MODEL"`
  - `"totalModelCountInTitle": true`
  - `"transportLayerSecurity": true`
  - `"webinterface": true`

Three post-processing steps will be set:
  - Remux/Transcode to a matroska container.
  - Rename to the following: `"$sanitize(${modelName})_$sanitize(${siteName})_$format(${localDateTime},yyyyMMdd-hhmmss).${fileSuffix}"`
  - Create contact sheet: 8x7 images, 2560px wide, timecodes enabled, same file name format as the Rename step.

## Persistent Log File

A persistent log file can be enabled by copying the following files from the GitHub repo into your mapped configuration directory:
  - `server.log`
  - `logback.xml`

Make sure they have the correct permissions so that the container can read the `logback.xml` file and write to the `server.log` file.

Include volume mappings for the two files in the `docker run` command or the `docker-compose.yml`.
```
docker run -d \
    --name=ctbrec-debian \
    -p 8080:8080 \
    -p 8443:8443 \
    -v /home/ctbrec/media:/app/captures:rw \
    -v /home/ctbrec/.config/ctbrec:/app/config:rw \
    -v /home/ctbrec/.config/ctbrec/logback.xml:/app/config/logback.xml:rw \
    -v /home/ctbrec/.config/ctbrec/server.log:/app/config/server.log:rw \
    -e TZ=Australia/Sydney \
    -e PGID=1000 \
    -e PUID=1000 \
    jafea7/ctbrec-debian
```

```yaml
version: '2.1'
services:
  ctbrec-debian:
    image: jafea7/ctbrec-debian
    container_name: "CTBRec-Debian"
    environment:
      - TZ=Australia/Sydney
      - PGID=1000
      - PUID=1000
    ports:
      - "8080:8080"
      - "8443:8443"
    volumes:
      - "/home/ctbrec/.config/ctbrec:/app/config:rw"
      - "/home/ctbrec/media:/app/captures:rw"
      - "/home/ctbrec/.config/ctbrec/logback.xml:/app/logback.xml"
      - "/home/ctbrec/.config/ctbrec/server.log:/app/config/server.log"
    restart: "unless-stopped"
```

**NOTE:** With the persistent log enabled the container log output will only be available up until the CTBRec server starts, it's then redirected to the `server.log` file.

## Extras

Included are four scripts that will send a contact sheet created by post-processing to a designated Discord, Telegram channel, email address, or POST to HTTP site.

The scripts are called `send2discord.sh`, `send2telegram.sh`, `send2email.sh`, and `send2http.sh` respectively, they reside in the `/app` directory, they are designed to be called as the last step in post-processing, (no point calling them before a contact sheet is created).

The relevant entries for post-processing are, for example:
```
    {
      "type": "ctbrec.recorder.postprocessing.Script",
      "config": {
        "script.params": "${absolutePath} ${modelDisplayName} $format(${localDateTime},yyyyMMdd-hhmmss)}",
        "script.executable": "/app/send2discord.sh"
      }
    }
```
```
    {
      "type": "ctbrec.recorder.postprocessing.Script",
      "config": {
        "script.params": "${absolutePath} ${modelDisplayName} $sanitize(${siteName}) $format(${localDateTime},yyyyMMdd-hhmmss)}",
        "script.executable": "/app/send2telegram.sh"
      }
    }
```
```
    {
      "type": "ctbrec.recorder.postprocessing.Script",
      "config": {
        "script.params": "${absolutePath} ${modelDisplayName} $sanitize(${siteName}) $format(${localDateTime},yyyyMMdd-hhmmss)}",
        "script.executable": "/app/send2email.sh"
      }
    }
```

```
    {
      "type": "ctbrec.recorder.postprocessing.Script",
      "config": {
        "script.params": "${absolutePath} ${modelDisplayName} $sanitize(${siteName}) $format(${localDateTime},yyyyMMdd-hhmmss)}",
        "script.executable": "/app/send2http.sh"
      }
    }
```

The first variable needs to be `${absolutePath}`, (needed to determine the contact sheet path/name), the following arguments can be anything and any number, (within reason), they will be concatenated with ` - ` and used as the subject.

The duration of the video will be concatenated at the end as `: hh:mm:ss`.

To designate the Discord channel it is to be sent to, create an environment variable called `DISCORDHOOK` with the Discord Webhook.

See [here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) for how to get it.

For example:
```
docker run -d \
    --name=ctbrec-debian \
    -p 8080:8080 \
    -p 8443:8443 \
    -v /home/ctbrec/media:/app/captures:rw \
    -v /home/ctbrec/.config/ctbrec:/app/config:rw \
    -e TZ=Australia/Sydney \
    -e PGID=1000 \
    -e PUID=1000 \
    -e DISCORDHOOK=https://discordapp.com/api/webhooks/<channelID>/<token> \
    jafea7/ctbrec-debian
```

```yaml
version: '2.1'
services:
  ctbrec-debian:
    image: jafea7/ctbrec-debian
    container_name: "CTBRec-Debian"
    environment:
      - TZ=Australia/Sydney
      - PGID=1000
      - PUID=1000
      - DISCORDHOOK=https://discordapp.com/api/webhooks/<channelID>/<token>
    ports:
      - "8080:8080"
      - "8443:8443"
    volumes:
      - "/home/ctbrec/.config/ctbrec:/app/config:rw"
      - "/home/ctbrec/media:/app/captures:rw"
    restart: "unless-stopped"
```

To designate the Telegram channel you need to set two environment variables, `CHAT_ID` and `TOKEN`.

See [here](https://www.shellhacks.com/telegram-api-send-message-personal-notification-bot/) on how to get both.

For example:
```
docker run -d \
    --name=ctbrec-debian \
    -p 8080:8080 \
    -p 8443:8443 \
    -v /home/ctbrec/media:/app/captures:rw \
    -v /home/ctbrec/.config/ctbrec:/app/config:rw \
    -e TZ=Australia/Sydney \
    -e PGID=1000 \
    -e PUID=1000 \
    -e CHAT_ID=<chat_id> \
    -e TOKEN=<bot token> \
    jafea7/ctbrec-debian
```

```yaml
version: '2.1'
services:
  ctbrec-debian:
    image: jafea7/ctbrec-debian
    container_name: "CTBRec-Debian"
    environment:
      - TZ=Australia/Sydney
      - PGID=1000
      - PUID=1000
      - CHAT_ID=<chat_id>
      - TOKEN=<bot token>
    ports:
      - "8080:8080"
      - "8443:8443"
    volumes:
      - "/home/ctbrec/.config/ctbrec:/app/config:rw"
      - "/home/ctbrec/media:/app/captures:rw"
    restart: "unless-stopped"
```

To send to an email address you need to set four environment variables, `MAILSERVER`, `MAILFROM`, `MAILTO`, and `MAILPASS`.

| Variable | Required | Meaning |
|----------|----------|---------|
| MAILSERVER | Mandatory | Address of the mail server in the form: `smtps://smtp.<domain>:<port>` |
| MAILFROM | Mandatory | Email address the emails are sent from. |
| MAILTO | Mandatory | Email address to send the emails to. |
| MAILPASS | Mandatory | Password for email account sending the emails. |

For example:
```
docker run -d \
    --name=ctbrec-debian \
    -p 8080:8080 \
    -p 8443:8443 \
    -v /home/ctbrec/media:/app/captures:rw \
    -v /home/ctbrec/.config/ctbrec:/app/config:rw \
    -e TZ=Australia/Sydney \
    -e PGID=1000 \
    -e PUID=1000 \
    -e MAILSERVER=smtps://smtp.gmail.com:465 \
    -e MAILFROM=my_really_cool_email@gmail.com \
    -e MAILTO=woohoo_another_capture@gmail.com \
    -e MAILPASS=my_really_super_secret_p4ssw0rd \
    jafea7/ctbrec-debian
```

```yaml
version: '2.1'
services:
  ctbrec-debian:
    image: jafea7/ctbrec-debian
    container_name: "CTBRec-Debian"
    environment:
      - TZ=Australia/Sydney
      - PGID=1000
      - PUID=1000
      - MAILSERVER=smtps://smtp.gmail.com:465
      - MAILFROM=my_really_cool_email@gmail.com
      - MAILTO=woohoo_another_capture@gmail.com
      - MAILPASS=my_really_super_secret_p4ssw0rd
    ports:
      - "8080:8080"
      - "8443:8443"
    volumes:
      - "/home/ctbrec/.config/ctbrec:/app/config:rw"
      - "/home/ctbrec/media:/app/captures:rw"
    restart: "unless-stopped"
```

**NOTE: The following was a request by someone to add to the image and was written by them.
        I have no way to test it so I don't know if it works or not.**

Send a POST request to an URL with postprocessing parameters.

Data will be sent as `multipart/form-data`.

| Form Field | Description |
|------------|-------------|
| file | relative path of the recording |
| sheet | the contact sheet file |
| duration | recording file length, format: `hh:mm:ss` |
| argv | `script.params` string set in server.json, base64encoded |

You need three environment Variables: `HTTP_URL`, `CURL_ARGS`, and `CURL_GET`.

| Variable | Required | Meaning |
|----------|----------|---------|
| HTTP_URL  | Mandatory | the url will send the http request to |
| CURL_ARGS | Optional | extra CURL arguments |
| CURL_GET  | Optional | Send GET requests instead, no contact sheet |

For example:
```
docker run -d \
    --name=ctbrec-debian \
    -p 8080:8080 \
    -p 8443:8443 \
    -v /home/ctbrec/media:/app/captures:rw \
    -v /home/ctbrec/.config/ctbrec:/app/config:rw \
    -e TZ=Australia/Sydney \
    -e PGID=1000 \
    -e PUID=1000 \
    -e HTTP_URL=http://some.url.org \
    -e CURL_ARGS=some_args \
    -e CURL_GET=true \
    jafea7/ctbrec-debian
```

```yaml
version: '2.1'
services:
  ctbrec-debian:
    image: jafea7/ctbrec-debian
    container_name: "CTBRec-Debian"
    environment:
      - TZ=Australia/Sydney
      - PGID=1000
      - PUID=1000
      - HTTP_URL=http://some.url.org
      - CURL_ARGS=some_args
      - CURL_GET=true
    ports:
      - "8080:8080"
      - "8443:8443"
    volumes:
      - "/home/ctbrec/.config/ctbrec:/app/config:rw"
      - "/home/ctbrec/media:/app/captures:rw"
    restart: "unless-stopped"
```

For `docker-compose` you can also add the variables to the `.env` file and reference them from within the `docker-compose.yml` file.


**plcheck.sh**

A simple script that will check if `playlist.m3u8` is terminated correctly, only useful if you don't record as a single file.

If the container is terminated without existing captures being finished correctly the `playlist.m3u8` file won't be terminated with `#EXT-X-ENDLIST` which will cause ffmpeg to truncate the recording and take excessive time to process.

Add this script as the **first step** in post-processing, if `playlist.m3u8` doesn't exist or is correctly terminated it will exit otherwise it will append `#EXT-X-ENDLIST` to the file which will allow post-processing to be re-run without causing problems.

The relevant entry for post-processing is:
```
    {
      "type": "ctbrec.recorder.postprocessing.Script",
      "config": {
        "script.params": "${absolutePath}",
        "script.executable": "/app/plcheck.sh"
      }
    }
```
