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
