# 24 h Sustained — Local (native) · 1080p25

**Scenario:** Local (native) · **Format:** 1080p25 (1920×1080 @ 25 fps) · **Duration:** 24 h
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
System CPU (%) and RAM (%) usage (read from /proc, the same source as htop) with 4 active
cameras over 24 continuous hours. Analogous to the Docker 2160p50 24 h sustained run, used
here to study long-term RAM behaviour on the native scenario (memory-leak check).

## Result (median / trend)
Median CPU: **88.5%** · RAM: 10.4% → 10.4% → 10.5% (start→middle→end).
RAM trend: **FLAT (no leak, as expected on Local)**. Samples: 16962 (~24.0 h), 100% of the time with 4 cameras.

## Files
`datos.csv` (raw, incremental writes), `resumen.csv` (statistics), `datos.xlsx` (Excel).
