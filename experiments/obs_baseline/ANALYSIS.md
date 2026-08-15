# OBS Studio comparison: what the numbers mean

This document explains the reasoning behind the OBS Studio comparison used in
the paper's Discussion section (Table 4). It is here so the numbers are fully
auditable: how they were obtained, what they do and do not prove, and why the
paper describes the CPU gap the way it does.

## Summary

We profiled OBS Studio 27.2.3 on the same workstation used for every other
result in the paper (Intel i9-10900X, 128 GB RAM, Ubuntu 22.04), under a
workload built to match the Voctomix local 1080p25 scaling test as closely as
possible: 0 to 4 sources of the same video file, all active sources
composited at once, whole-host CPU and RAM sampled from `/proc` once per
second, median per phase.

| Active sources | Voctomix 2.0 CPU | OBS CPU | Voctomix 2.0 RAM | OBS RAM |
|---|---|---|---|---|
| 0 (idle) | 29.0 % | 6.7 % | 7.2 % (9.2 GB) | 5.9 % (7.5 GB) |
| 1 | 35.9 % | 16.7 % | 7.9 % (10.1 GB) | 6.2 % (7.7 GB) |
| 2 | 44.5 % | 22.6 % | 8.6 % (11.0 GB) | 6.5 % (8.1 GB) |
| 3 | 59.5 % | 30.6 % | 9.2 % (11.8 GB) | 6.6 % (8.3 GB) |
| 4 | 89.6 % | 39.4 % | 10.0 % (12.8 GB) | 6.9 % (8.7 GB) |

These numbers are real and reproducible (see the verification section below).
But they are not a same-task benchmark, and the paper does not present them as
one. There are two real architectural reasons for most of the gap, and they
are worth explaining clearly, because they are actually part of the paper's
argument, not a weakness to hide.

## Why OBS uses less CPU: two real reasons

### 1. Voctomix's measured pipeline never encodes video; OBS always does

This is the most important point, and it came from reading the actual
GStreamer pipeline that produces the Voctomix scaling numbers, not from
assuming anything.

`voctocore/lib/avrawoutput.py` (`AVRawOutput`), which is what the escalado
test measures, is simply:

```
intervideosrc ! {video/x-raw,format=I420,...} ! queue ! matroskamux ! multifdsink
```

There is no video encoder in this chain. It packages uncompressed I420 frames
into a Matroska container and sends them over TCP. So the CPU cost being
measured for Voctomix is: decoding the source video plus scaling it to
1080p25 (done by an external ffmpeg process feeding each camera), plus
Voctomix's own CPU compositing, with zero compression involved.

By default, Voctomix also runs small JPEG preview encoders at a much lower
resolution (1024x576), but that cost is minor compared to a full-resolution
delivery encode.

OBS, on the other hand, was set up to record continuously at full resolution
with the x264 software encoder in every phase, including idle, because that
is the only way OBS produces a usable output; it has no raw-passthrough mode.
Encoding video is real, non-trivial CPU work, and it is work that the
Voctomix number being compared against simply does not do.

In short: part of the CPU gap is not "OBS's architecture is more efficient at
the same task." It is that the two tools were not doing the same amount of
work: OBS had to fully encode its output, and the Voctomix configuration
being measured did not. This does not make the comparison invalid, since the
fairness rules for the OBS side (recording on, correct software encoder) were
followed exactly as intended, but it does need to be stated plainly in the
paper. Leaving it out is the kind of thing a reviewer with video engineering
knowledge would notice immediately, and it would hurt the paper's credibility
far more than including the explanation does.

This is also not bad news for Voctomix's story. Its architecture deliberately
keeps raw compositing separate from delivery encoding, in line with the
microservice approach used throughout the paper: a real deployment adds
encoding as its own, independently scaled stage (for example, a separate
RTMP or SRT container), instead of baking it into the mixing core. OBS cannot
make that separation because encoding is built into its only mode of
operation. That is a genuine, useful architectural difference, not an excuse.

### 2. Compositing runs on different hardware

Voctomix's compositor runs on the CPU (GStreamer software compositing). OBS
composites through OpenGL on the GPU (confirmed in the OBS log: "Loading up
OpenGL on adapter NVIDIA GeForce RTX 3080"). At four sources, this is likely
the biggest single contributor to OBS staying flatter on the CPU curve, since
blending four decoded frames into one 1080p canvas is offloaded entirely to
the graphics card, outside what the host-CPU measurement captures. This was
expected before running the test: the decision was to measure OBS as it
normally runs (with GPU compositing) and explain the difference in writing,
rather than force an artificial CPU-only mode that nobody uses in practice.

### A note on the "idle" baseline

Voctomix's 0-camera phase (29.0% CPU) is not a fully empty pipeline: by
default it keeps four always-on auxiliary feeds running (break, intro, and
two stream-blanker sources), which is real, continuous work happening even
when the paper calls it "idle." OBS's 0-source phase is a genuinely empty
canvas, with only the encoder ticking over black frames. This is consistent
with the data: OBS jumps from 6.7% idle to 16.7% with just one source, a
larger relative jump than Voctomix shows at the same step, which fits with
OBS's idle phase being closer to truly empty.

## What was actually held equal

Despite the differences above, several things were kept identical, which is
what makes the comparison meaningful in the first place:

- Same source video (`bbb_sunflower_2160p_60fps_normal.mp4`, 3840x2160 at 60
  fps), decoded in software by both systems.
- Same output target: 1920x1080 at 25 fps for both.
- Same workstation, same conditions, one clean measurement pass.
- No GPU encoding anywhere. Every OBS log confirms the software x264 encoder
  was used, never NVENC. The encode/no-encode difference described above is
  about whether encoding happens at all, not about one side using hardware
  acceleration to cheat at it.

## What the paper can honestly say

- Under this workload, OBS Studio shows a lower whole-host CPU footprint than
  Voctomix 2.0 at every camera count, roughly 40-60% lower in relative terms.
- This gap is not a sign of worse engineering in Voctomix. It comes from two
  real architectural choices: OBS offloads compositing to the GPU while
  Voctomix composites on the CPU, and OBS's number necessarily includes a
  full-resolution H.264 encode that the tested Voctomix configuration does
  not perform.
- Voctomix's higher CPU cost is the price of a decoupled, GPU-independent,
  headless design: compositing that can run in a minimal container with no
  GPU driver, be orchestrated across a Kubernetes cluster, and have encoding
  added later as its own scalable stage. None of that is available in OBS's
  desktop-only, GPU-bound design. This is exactly the trade-off the paper
  argues for.
- RAM is a fairer comparison to make directly, since it is dominated by
  decoded-frame buffers and is much less affected by the encode/no-encode or
  CPU/GPU-compositing differences above.

## What the paper should not say

- It should not present this as a controlled, same-task benchmark, or claim
  it isolates "architecture overhead" cleanly.
- It should not say OBS is simply "more efficient" without saying at what
  task. The honest framing is that OBS's default mode is lighter on host CPU
  than Voctomix's raw-compositing core, not that OBS is better software.
- It should not leave out the encode/no-encode difference. That single point
  is what turns this into a defensible comparison instead of one that invites
  a serious reviewer objection.

## How this was checked

- **Encoder, every phase:** the OBS logs for all five phases show the x264
  software encoder in use, and no NVENC selection anywhere.
- **Format, resolution, frame rate, every recording:** verified with
  `ffprobe` (see `evidence/ffprobe_verification.txt`); every phase confirms
  H.264, 1920x1080, 25 fps, with durations consistent with the warm-up and
  measurement window used.
- **Visual check:** `evidence/frame_2_cams.png` and `evidence/frame_4_cams.png`
  show the scenes composited correctly, with all sources visible at once.
- **Sample counts:** the raw data file has exactly 300 samples per phase,
  matching the warm-up and window settings used.
- **Sanity check:** the measured four-source CPU value (39.4%) falls inside
  the range that had been predicted beforehand (roughly 20-45%), which is a
  good sign against measurement mistakes such as GPU offload silently
  kicking in.
- **Host state:** the machine was freshly rebooted before the campaign (this
  also fixed an unrelated NVIDIA driver mismatch), with a low load average
  and no other heavy processes running.
- **Reproducibility:** the exact OBS profile and scene collection used are
  regenerable from `run_obs_campaign.py`; the previous default OBS profile
  was backed up before any change and restored afterward.

## What was left out on purpose

- GPU usage was not logged during the runs. The GPU-compositing point above
  is based on OBS's documented behaviour and the OpenGL initialization line
  in its log, not on a measured GPU utilization graph. If a reviewer asks for
  this specifically, it is a short follow-up to add.
- No repeated campaigns or averaging across runs, as instructed.
- The raw recordings (about 431 MB total) are not committed to the
  repository, consistent with how other large media files are handled here.
  One representative frame per phase and the full `ffprobe` output are kept
  instead, which is enough to verify the results without the large files.
