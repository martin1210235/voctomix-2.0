<<<<<<< HEAD
# HowTo use the Docker version of Voctomix
## build the docker container locally
- checkout branch: 
```
git checkout quickstart-docker
```
- build docker
```
docker build -t local/voctomix .
```
- rebuild docker after changes
```
docker tag local/voctomix:latest local/voctomix:old; \
docker build -t local/voctomix . && docker rmi local/voctomix:old
```

## Test the docker
the entrypoint script of the container provides some commands to ease the startup of the individual components. get a list by running
```docker run --rm -it --name=voctocore local/voctomix core```

## Run the components
### CORE
```
docker run --rm -it --name=voctocore local/voctomix core
```
### Source example scripts
```
docker run -it --rm --name=cam1 --link=voctocore:corehost local/voctomix gstreamer/source-videotestsrc-as-cam1.sh
docker run -it --rm --name=bg --link=voctocore:corehost local/voctomix gstreamer/source-videotestsrc-as-background-loop.sh
```

### GUI
to run the GUI in a docker the docker user needs access to the local X server. This is done by sharing the ```/tmp/.X11-unix``` socket with the container. Depending on your X11 setup you have to allow access to the X-Server session by running: ```xhost +local:$(id -un)```
The example below maps the local voctogui config file ```/tmp/vocto/configgui.ini``` into the container. Please create and change this file to change the voctogui configuration.
```
docker run -it --rm --name=gui --env=gid=$(id -g) --env=uid=$(id -u) --env=DISPLAY=:0 --link=voctocore:corehost \
  -v /tmp/vocto/configgui.ini:/opt/voctomix/voctogui/config.ini -v /tmp/.X11-unix:/tmp/.X11-unix -v /tmp/.docker.xauth:/tmp/.docker.xauth local/voctomix gui
```
=======
# Docker Deployment

The supported Docker path for Voctomix 2.0 is the Compose stack defined in
`docker-compose.yml` and launched by `launch_docker_studio.sh`.

## Quick Start

```bash
xhost +local:$(id -un)
./launch_docker_studio.sh
```

Stop the stack:

```bash
sudo docker compose down
```

The launcher builds the local image, starts RabbitMQ, `voctocore`, telemetry,
camera sources and auxiliary media sources, waits for the `voctocore`
healthcheck, then opens `voctogui` and a program monitor on the host.

## Required Media Assets

Create `videos/` in the repository root and place the VTR and continuity assets
there before launching:

```text
videos/intro.mp4
videos/SLIDES_video_starting_soon.mp4
videos/stream_offline.mp4
videos/musica_pausa.mp3
videos/video_cuenta_regresiva_10s.mp4
```

Camera test sources can be overridden through `.env` using `CAM1_SOURCE`,
`CAM2_SOURCE`, `CAM3_SOURCE` and `CAM4_SOURCE`.

## Details

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the complete scenario
description and [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common
Docker/X11 issues.
>>>>>>> 920adf625f85240b9410c616f7c7c875f625df30
