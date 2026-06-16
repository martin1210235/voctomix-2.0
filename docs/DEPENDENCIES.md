# Dependencies — Minimum Version Requirements

## System (native installation)

| Package | Min. version | Install |
|---------|-------------|---------|
| Python | 3.8 | `sudo apt install python3` |
| GStreamer | 1.20 | `sudo apt install gstreamer1.0-tools` |
| gst-plugins-base | 1.20 | `sudo apt install gstreamer1.0-plugins-base` |
| gst-plugins-good | 1.20 | `sudo apt install gstreamer1.0-plugins-good` |
| gst-plugins-bad | 1.20 | `sudo apt install gstreamer1.0-plugins-bad` |
| gst-plugins-ugly | 1.20 | `sudo apt install gstreamer1.0-plugins-ugly` |
| python3-gi | 3.42 | `sudo apt install python3-gi python3-gi-cairo` |
| GTK 3 | 3.24 | `sudo apt install python3-gi gir1.2-gtk-3.0` |
| FFmpeg | 4.4 | `sudo apt install ffmpeg` |
| numpy | 1.21 | `sudo apt install python3-numpy` |
| scipy | 1.7 | `sudo apt install python3-scipy` |

## Docker

| Tool | Min. version |
|------|-------------|
| Docker Engine | 24.0 |
| Docker Compose (plugin) | 2.20 |

## Kubernetes (optional)

| Tool | Min. version |
|------|-------------|
| kubectl | 1.28 |
| minikube | 1.32 |

## Python (from pip, if not using apt)

```bash
pip3 install pycodestyle  # for check_pep8.sh
```

## Verify Installation

```bash
# GStreamer
gst-launch-1.0 --version

# Python bindings
python3 -c "import gi; gi.require_version('Gst', '1.0'); from gi.repository import Gst; print(Gst.version_string())"

# FFmpeg
ffmpeg -version | head -1

# Docker
docker --version && docker compose version
```
