# Performance Baseline

Reference metrics for Voctomix 2.0 under normal operating conditions.

*Update this file after each benchmark run.*

---

## Test Environment

| Component | Spec |
|-----------|------|
| CPU | AMD Ryzen 7 / Intel Core i7 (4+ cores recommended) |
| RAM | 8 GB minimum, 16 GB recommended |
| OS | Ubuntu 22.04 LTS |
| GStreamer | 1.20.x |
| Docker | 24.x |
| Scenario | Docker Compose (10 services) |

---

## Latency

| Path | Measured | Target |
|------|----------|--------|
| Source → voctocore input | < 50 ms | < 100 ms |
| voctocore → program output (:15000) | < 100 ms | < 200 ms |
| voctocore → GUI preview (:14000) | < 200 ms | < 500 ms |
| TCP command roundtrip (set_video_a) | < 5 ms | < 20 ms |
| Telemetry JSON export cycle | 1 s | 1 s |
| Audio fade on source switch (AFV) | 100 ms | ≤ 200 ms |

---

## CPU Usage (Docker, 1920×1080 @ 25fps, 4 sources)

| Service | Idle | Active (4 sources) |
|---------|------|-------------------|
| voctocore | ~5% | ~35-60% (depends on composite mode) |
| cam1-cam4 (FFmpeg) | ~2% each | ~8-12% each |
| stream_blanker | ~1% | ~3% |
| telemetry | < 1% | < 1% |
| RabbitMQ | < 1% | ~1% |
| **Total** | ~20% | ~60-80% |

---

## Network Usage (internal Docker network)

| Stream | Bitrate |
|--------|---------|
| cam source → voctocore (UYVY raw, Matroska) | ~750 Mbps per source |
| voctocore → program output (:15000, raw) | ~750 Mbps |
| voctocore → preview (:12000, JPEG) | ~5-15 Mbps |
| voctocore → source previews (:14000-14005, JPEG) | ~3-8 Mbps each |
| Telemetry JSON | < 0.1 Mbps |

> Note: Raw Matroska streams are uncompressed — they are intended for localhost/LAN use only. For WAN output, add an H.264 encoding stage.

---

## Memory Usage (Docker)

| Service | RSS |
|---------|-----|
| voctocore | ~200-400 MB |
| voctogui | ~80-120 MB |
| RabbitMQ | ~80-150 MB |
| telemetry | ~30-50 MB |

---

## How to Measure

```bash
# CPU and memory per container:
docker stats --no-stream

# Network throughput on program output:
tcpdump -i any port 15000 -c 1000 2>/dev/null | grep -c "length" | awk '{print $1 * 1500 * 8 / 1000000 " Mbps (approx)"}'

# Latency: command roundtrip
time echo "get_video" | nc localhost 9999

# GStreamer pipeline stats:
GST_DEBUG=GST_TRACER:7 ./voctocore/voctocore.py 2>&1 | grep -i "latency\|fps"
```
