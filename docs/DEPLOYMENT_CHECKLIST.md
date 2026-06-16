# Deployment Checklist

Use before any live production event.

---

## 30 Minutes Before Event

### Environment

- [ ] `.env` file present and correct (`HOST_IP`, camera sources, credentials)
- [ ] `videos/` directory contains all required media files (break loop, pause slide, offline slide, intro, background music)
- [ ] `images/` directory contains overlay PNG files
- [ ] Sufficient disk space for logs (`df -h .`)

### Network

- [ ] LAN connectivity between all PCs (scenario 2) or Docker bridge healthy
- [ ] Ports 9999, 14000-14005, 5672 not occupied by other processes
- [ ] Firewall rules allow required ports (scenario 2)

---

## System Startup

### Docker (Scenario 3)

```bash
xhost +local:$(id -un)
./launch_docker_studio.sh
```

- [ ] `docker compose ps` — all 10 services healthy
- [ ] No `exited (1)` or `unhealthy` containers

### Native (Scenario 1/2)

```bash
./start_studio_single_pc.sh   # or scenario 2 scripts
```

- [ ] voctocore started and listening on 9999
- [ ] voctogui connected (no "Connection refused" in console)

---

## voctogui Verification

- [ ] All 6 source preview windows are visible and showing video
- [ ] Source A and B buttons respond (switch in < 200ms)
- [ ] Composite mode buttons work (fullscreen, side-by-side, PIP)
- [ ] LIVE / PAUSE / NOSTREAM buttons respond correctly
- [ ] Audio levels visible and non-zero on active source
- [ ] Overlay PNG loads and appears on program output

---

## Telemetry Verification

```bash
# Native:
tail -f registros/gui_state.json     # should update every 1 second

# Docker:
curl http://localhost:8080/health
# Browser: http://localhost:15672 → RabbitMQ web UI, check message rate
```

- [ ] JSON telemetry updating at 1Hz
- [ ] RabbitMQ shows incoming messages (Docker only)

---

## Program Output Verification

```bash
# Verify program output stream is active:
ffprobe tcp://localhost:15000 2>&1 | grep "Stream"
```

- [ ] `:15000` shows video stream
- [ ] Stream blanker starts in LIVE mode
- [ ] Switching to PAUSE shows correct pause video
- [ ] Switching back to LIVE shows program

---

## During Event

- [ ] Monitor `docker compose ps` or `top` for CPU spikes
- [ ] Check preview quality (no pixelation, freezing)
- [ ] Confirm audio follows video on source switches

---

## After Event

```bash
docker compose down
# or kill native processes

# Archive logs:
cp registros/gui_state.json registros/gui_state_$(date +%Y%m%d_%H%M).json
```

- [ ] Export `registros/gui_state.json` for telemetry analysis
- [ ] Note any issues for TROUBLESHOOTING.md
