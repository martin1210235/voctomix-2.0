FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-gi \
    python3-gi-cairo \
    python3-scipy \
    python3-numpy \
    gir1.2-gstreamer-1.0 \
    gir1.2-gst-plugins-base-1.0 \
    gir1.2-gtk-3.0 \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    ffmpeg \
    netcat-openbsd \
    iproute2 \
    && pip3 install --no-cache-dir pika==1.3.2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/voctomix

COPY . /opt/voctomix/

HEALTHCHECK --interval=5s --timeout=3s --retries=12 \
    --start-period=20s \
    CMD bash -c "echo '' | nc -zw1 localhost ${VOCTOCORE_PORT:-9999}" || exit 1
