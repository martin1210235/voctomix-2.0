# Output integrity — delivered frames and content freshness

**Scenarios:** local, Docker and Kubernetes · **Formats:** 1080p25, 1080p50, 2160p25, 2160p50
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).
**Measured on port 11000** (raw compositor output, before the stream blanker).

## What is measured

Whether the mixer actually delivers the video it is supposed to deliver, in two steps.

**Cadence.** Frames arriving at the programme sink over a 60 s window with four active sources,
compared against the nominal count, together with the sustained output frame rate. Three repetitions
per cell, across two independent campaigns, for 72 measurements in total.

**Content freshness.** Frame counting alone is not sufficient: a compositor whose inputs are starved
keeps emitting at the nominal rate by repeating its last frame, which produces a perfect frame count
over a frozen picture. Each capture was therefore also analysed for consecutive duplicate frames with
`mpdecimate`, and cross-checked on one cell with a per-frame MD5 comparison, which agreed exactly.

Frames are counted in flight and never written to disk. The raw mix is 78 MB/s at 1080p25 and
622 MB/s at 2160p50, so a storage backend that could not keep up would stall the reader, and
`multifdsink` drops clients it considers too slow, which would have manufactured the very frame loss
the measurement was meant to detect.

## Result

### Cadence: no frames are lost anywhere

| Format | Frames delivered / expected | Drop rate | Output rate |
|---|---|---|---|
| 1080p25 | 1500 / 1500 | 0.00% | 25.0 fps |
| 1080p50 | 3000 / 3000 | 0.00% | 50.0 fps |
| 2160p25 | 1500 / 1500 | 0.00% | 25.0 fps |
| 2160p50 | 3000 / 3000 | 0.00% | 50.0 fps |

Identical in the three deployment tiers, and reproduced across both campaigns.

### Freshness: only the baseline profile is fully fresh

| Format | Distinct frames per second (median) |
|---|---|
| 1080p25 | 22.0 of 25 |
| 1080p50 | 1.5 of 50 |
| 2160p25 | 1.1 of 25 |
| 2160p50 | 0.7 of 50 |

At 1080p25 the shortfall from 25 corresponds to brief repetitions at the instant the looping test
clips restart, an artefact of the synthetic source that would not occur with a continuous live camera
feed.

### Where the limit actually is

Replacing the simulated cameras with pre-rendered raw frames, so that producing the input costs
almost nothing, restores full freshness at two of the three affected profiles:

| Format | Simulated cameras | Pre-rendered input |
|---|---|---|
| 1080p50 | 1.8 | **50.0 of 50** |
| 2160p25 | 1.2 | **25.0 of 25** |
| 2160p50 | 0.8 | 1.3, still stale |

The limitation at 1080p50 and 2160p25 therefore lies in the test harness, where each simulated camera
decodes a 4K master and four run concurrently on the same host as the mixer, rather than in the
mixing pipeline. At 2160p50 the ceiling persists under the reduced-cost input and belongs to the host.

## Files

`datos.csv` (raw data, 72 measurements, both campaigns), `resumen.csv` (statistics per format),
`frescura.csv` and `frescura_campana2.csv` (distinct-frame analysis, including the isolation
experiments), `logs/` (campaign transcripts). The measurement scripts are in
`experiments/measure_output_integrity.sh` and `experiments/measure_frame_freshness.sh`.
