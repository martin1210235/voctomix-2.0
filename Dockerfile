# Usamos la última versión estable de Ubuntu (LTS)
FROM ubuntu:22.04

# Evitamos que la instalación nos haga preguntas interactivas
ENV DEBIAN_FRONTEND=noninteractive

# Actualizamos repositorios e instalamos todas las dependencias
RUN apt-get update && apt-get install -y \
    python3 \
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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir pika==1.3.2


# Creamos el directorio de trabajo
WORKDIR /opt/voctomix

# Copiamos todo nuestro proyecto dentro de la imagen
COPY . /opt/voctomix/

# Healthcheck base: el servicio que lo sobreescriba en compose puede refinarlo.
# Por defecto comprueba que el puerto de control de voctocore escucha.
HEALTHCHECK --interval=5s --timeout=3s --retries=12 --start-period=20s \
    CMD bash -c 'echo "" | nc -zw1 localhost 9999' || exit 1
