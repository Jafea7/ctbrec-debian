#
# ctbrec-debian Dockerfile
#
# https://github.com/jafea7/ctbrec-debian
#

FROM debian:bookworm-slim AS builder

ARG TARGETPLATFORM

# Install curl & tar to get ffmpeg static
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl xz-utils && \
    rm -rf /var/lib/apt/lists/*

# Copy the rootfs layout including files
COPY rootfs/ /

# Install ffmpeg static build, set permissions
RUN useradd -u 1000 -U -G users -d /app -s /bin/false ctbrec && \
    mkdir -p /app/captures /app/config /app/ffmpeg && \
    if [ "$TARGETPLATFORM" = "linux/amd64" ]; then curl -k -v --http1.1 https://www.johnvansickle.com/ffmpeg/old-releases/ffmpeg-5.1.1-amd64-static.tar.xz | tar --strip-components=1 -C /app/ffmpeg -xvJ --wildcards "ffmpeg-*/ffmpeg"; fi && \
    if [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then curl -k -v --http1.1 https://www.johnvansickle.com/ffmpeg/old-releases/ffmpeg-5.1.1-armhf-static.tar.xz | tar --strip-components=1 -C /app/ffmpeg -xvJ --wildcards "ffmpeg-*/ffmpeg"; fi && \
    if [ "$TARGETPLATFORM" = "linux/arm64" ]; then curl -k -v --http1.1 https://www.johnvansickle.com/ffmpeg/old-releases/ffmpeg-5.1.1-arm64-static.tar.xz | tar --strip-components=1 -C /app/ffmpeg -xvJ --wildcards "ffmpeg-*/ffmpeg"; fi && \
    chmod -R a+rwX /app/ && \
    chmod a+x /app/*.sh /app/*.py /app/ffmpeg/ffmpeg

# Pull base image.
FROM eclipse-temurin:19-jre

# Copy app folder with ffmpeg from builder
COPY --from=builder /app /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends less inetutils-ping python3 python3-pip && \
    pip3 install urllib3 requests && \
    apt-get -y remove python3-pip && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*

ARG CTBVER
ENV CTBVER=${CTBVER}

# Expose server non-SSL and SSL ports
EXPOSE 8080 8443

# Initialise
ENTRYPOINT ["/app/init.sh"]

HEALTHCHECK --interval=20s --retries=3 --timeout=3s \
        CMD curl -f http://localhost:8080 || exit 1
