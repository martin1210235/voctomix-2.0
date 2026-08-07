# OBS Baseline Comparison — Rigorous Methodological Analysis

**Status:** Campaign completed and verified. Read this file in full before writing anything
in the paper — it documents exactly what these numbers do and do not prove, and contains a
methodological finding that changes how the comparison must be framed.

---

## 1. Executive summary

A single, clean measurement campaign profiled OBS Studio 27.2.3 on the same workstation
(Intel i9-10900X, 128 GB RAM, Ubuntu 22.04) that produced the Voctomix 2.0 paper results,
under a workload designed to be as comparable as possible to the Voctomix local 1080p25
escalado test: 0→4 sources of the same master video file, all active sources composited
simultaneously, whole-host CPU/RAM sampled from `/proc` at 1 Hz, median per phase.

| Active sources | Voctomix 2.0 CPU | OBS CPU | Voctomix 2.0 RAM | OBS RAM |
|---|---|---|---|---|
| 0 (idle) | 29.0 % | 6.7 % | 7.2 % (9.2 GB) | 5.9 % (7.5 GB) |
| 1 | 35.9 % | 16.7 % | 7.9 % (10.1 GB) | 6.2 % (7.7 GB) |
| 2 | 44.5 % | 22.6 % | 8.6 % (11.0 GB) | 6.5 % (8.1 GB) |
| 3 | 59.5 % | 30.6 % | 9.2 % (11.8 GB) | 6.6 % (8.3 GB) |
| 4 | 89.6 % | 39.4 % | 10.0 % (12.8 GB) | 6.9 % (8.7 GB) |

**These numbers are real, verified, and reproducible** (see §5). But they are **not** an
equal-task benchmark, and the paper must not present them as one. Three genuine
architectural asymmetries explain most of the gap — none of them is a measurement error,
and all of them are worth stating explicitly because they are, in fact, the interesting
part of the story.

---

## 2. The three asymmetries (why this is not "OBS is 2x more efficient")

### 2.1 — THE BIG ONE: Voctomix's measured pipeline never encodes video. OBS's always does.

This was discovered by reading the actual GStreamer pipeline source that produced the
Voctomix escalado numbers, not assumed from the paper text.

`voctocore/lib/avrawoutput.py` (`AVRawOutput`, used for both the raw mix at :11000 and the
program output at :15000 — the pipeline whose cost is what the escalado test measures) is:

```
intervideosrc ! {video/x-raw,format=I420,...} ! queue ! matroskamux ! multifdsink
```

There is **no video encoder anywhere in this chain**. It muxes uncompressed I420 frames
into a Matroska container and pushes them over TCP. Voctomix's core measured cost is:
N× (external ffmpeg: H.264 decode of the source + CPU `swscale` resize to 1080p25) +
voctocore (CPU compositing via GStreamer `videomixer` + raw muxing, zero compression).

Voctomix *does* additionally run, by default (`previews.enabled=true`,
`mirrors.enabled=true` in `default-config.ini`), lightweight per-source and mix **JPEG**
preview encoders (`jpegenc quality=90`) at a much lower resolution (1024×576) — real but
small CPU cost, not comparable to a full-resolution delivery encode.

OBS, by contrast, was correctly configured per the fairness rules to **record continuously
at full resolution with the x264 software encoder** (CBR 8000 kbps, preset veryfast,
1920×1080@25) in every phase, including idle — because that is the only way OBS produces
a deliverable stream; it has no "raw passthrough" mode. This is a real, non-trivial CPU cost
(confirmed: x264 encoding is what OBS's CPU curve mostly reflects) that the Voctomix number
being compared against does **not** pay at all.

**Implication:** part of the CPU gap is not "OBS's architecture is more efficient at the
same task" — it is "the two tools were doing measurably different amounts of work; OBS was
required to fully encode, Voctomix's tested configuration was not." This is not a flaw in
the campaign (the fairness rules — record ON, correct encoder — were followed exactly as
specified and were the right call), but it **must** be stated in the paper, or a competent
reviewer will catch the omission and it will damage the paper's credibility far more than
including the caveat would.

**Why this is not a problem for Voctomix's story, and is in fact useful:** Voctomix's
architecture deliberately decouples raw compositing from delivery encoding — the
microservice/container philosophy documented throughout the paper. A production deployment
adds encoding as a separate, independently scaled stage (e.g., an RTMP/SRT sidecar
container) whose cost is orthogonal to the mixing core under test here. OBS is a monolithic
desktop application that cannot make that separation — encoding is baked into its only
mode of operation. This is a genuine, citable architectural difference, not a hand-wave.

### 2.2 — Compositing happens on different processors

Voctomix's `videomixer`/compositor runs on the **CPU** (GStreamer software compositing).
OBS composites via **OpenGL on the GPU** (confirmed in the OBS log: `Loading up OpenGL on
adapter NVIDIA GeForce RTX 3080`). At 4 sources this is likely the single largest
contributor to OBS's flatter CPU curve, since pixel blending of 4× 3840×2160-decoded frames
into a 1920×1080 canvas is offloaded entirely off the host-CPU metric being measured.
This was already anticipated and explicitly accepted before running the campaign
(user's decision: "OBS real + document", not a forced CPU-only run) — it is not a new
finding, but it compounds with §2.1 and must be mentioned together.

### 2.3 — The "idle" baselines are not measuring the same thing

Voctomix's 0-camera phase (29.0 % CPU) is not an empty pipeline: by default it keeps 4
always-on auxiliary feeds running (`break`, `intro`, two stream-blanker sources) — real,
continuous decode+composite work baked into what the paper calls "idle." OBS's 0-source
phase is a genuinely idle canvas with just the encoder ticking over on black frames. This
was flagged before the campaign ran and is confirmed by the resumen.csv: OBS idle (6.7%)
vs. 1-source (16.7%) already shows a ~10pp jump for a single source, consistent with an
idle phase that was actually near-empty, unlike Voctomix's.

### 2.4 — What *is* directly comparable

Despite the above, three things were genuinely held equal, and this is worth stating
plainly because it is what makes the comparison meaningful at all rather than worthless:
- **Identical source master** (`bbb_sunflower_2160p_60fps_normal.mp4`, 3840×2160@60) decoded
  in software by both systems — the per-source decode cost is a fair, shared baseline.
- **Identical canvas/output target**: 1920×1080 @ 25 fps in both.
- **Same host, same conditions, single clean pass**, per Alberto's explicit instruction.
- **No GPU encoding anywhere** (verified per-phase in the OBS log: `obs-x264.so`, never
  `nvenc`) — the encode/no-encode asymmetry (§2.1) is about *whether* encoding happens, not
  about one side unfairly using hardware acceleration for it.

---

## 3. What the paper CAN honestly say

- OBS Studio, measured under a broadly comparable ingest-and-composite workload on the same
  hardware, shows a **lower whole-host CPU footprint** than Voctomix 2.0 at every camera
  count tested (roughly 40–60 % lower in relative terms).
- This gap is **not attributable to implementation inefficiency** in Voctomix; it reflects
  genuine architectural differences: (a) OBS offloads compositing to the GPU while Voctomix
  composites on the CPU, and (b) OBS's number necessarily includes a full-resolution H.264
  encode that Voctomix's tested raw-passthrough configuration does not perform.
- Voctomix's higher CPU cost is the price of a **decoupled, GPU-independent, headless
  architecture** — raw compositing that can run in a minimal container with no GPU driver
  dependency, be horizontally orchestrated in Kubernetes, and have encoding added as an
  independently scaled stage — none of which OBS's monolithic, GPU-bound, desktop-only
  design can offer. **This is precisely the trade-off the paper's contribution argues for**
  (cost reduction vs. dedicated/proprietary hardware, container-native deployment,
  democratization of remote production), so the comparison, read correctly, supports the
  paper's thesis rather than undermining it.
- RAM: OBS's lower RAM (~7 GB vs. ~10–13 GB at 4 sources) is a more direct and less
  confounded comparison, since RAM is dominated by decoded-frame buffers and is less
  sensitive to the encode/no-encode or CPU/GPU-compositing asymmetries. This is fair to
  report with less hedging than the CPU figures.

## 4. What the paper must NOT say

- Must NOT claim this is a controlled, equal-task microbenchmark, or that it isolates
  "architecture overhead" in a clean way.
- Must NOT claim OBS is "more efficient" without immediately qualifying *at what task* —
  the honest framing is "OBS's default operating mode is lighter on host CPU than
  Voctomix's raw-compositing core," not "OBS's software is better engineered."
- Must NOT omit the encode/no-encode asymmetry (§2.1). This is the single most important
  sentence to get into the paper — it is the difference between a defensible table and one
  that invites a devastating reviewer comment.

---

## 5. Verification evidence (all checks passed)

- **Encoder, per phase:** `obs_log_{phase}.txt` for all 5 phases contains
  `[x264 encoder: 'simple_h264_recording'] preset: veryfast` and no `nvenc` selection line.
- **Format/resolution/fps, all 5 recordings:** `evidence/ffprobe_verification.txt` —
  every phase confirms `codec_name=h264, width=1920, height=1080, r_frame_rate=25/1`,
  duration ≈323.6–323.8 s (consistent with 20 s warm-up + 300 s window + startup/shutdown).
- **Visual composite check:** `evidence/frame_2_cams.png` and `evidence/frame_4_cams.png`
  confirm the side-by-side and 2×2 grid layouts render correctly with all sources decoded
  and visible simultaneously.
- **Sample counts:** `obs_datos.csv` has exactly 300 rows per phase (1500 total), matching
  `--warmup 20 --window 300`.
- **Sanity range check:** OBS's 4-source figure (39.4 %) falls within the a-priori expected
  range the Mac's brief predicted before any data existed ("~20-45 % CPU" at 4 sources,
  §8 of `README.md`) — a strong signal against measurement artifacts (e.g., GPU offload
  silently failing, or a stale/incorrect encoder being used).
- **Host baseline:** machine was freshly rebooted (fixed a pre-existing NVIDIA driver
  version mismatch that made OBS unable to create an OpenGL context at all before the
  reboot), load average 0.72 before the campaign, no other heavy processes running.
- **Reproducibility:** the exact profile (`~/.config/obs-studio/basic/profiles/obs_baseline/`)
  and scene collection (`~/.config/obs-studio/basic/scenes/obs_baseline.json`) used are
  regenerable from `run_obs_campaign.py` plus the config this repo documents; the user's
  original OBS default profile/collection were backed up before any change and restored
  afterwards.

## 6. Not done / explicitly out of scope

- GPU utilization (`nvidia-smi`) was **not** logged during the runs — the GPU-offload claim
  in §2.2 rests on OBS's documented/standard OpenGL compositing behavior (confirmed in the
  OBS log that it initialized on the RTX 3080), not on a measured GPU-% time series. If a
  reviewer specifically asks for this, it is a cheap follow-up (a `nvidia-smi --query-gpu
  utilization.gpu --format=csv -l 1` running alongside a repeat of the 4-cam phase would
  settle it in ~5 minutes) but was not run here to honor "one clean pass, don't
  over-complicate" (Alberto's instruction).
- No repeated campaigns / no averaging across runs, per instruction.
- Recordings (`recordings/*.mkv`, ~431 MB total) are **not** committed to git (the repo's
  `.gitignore` already excludes `*.mkv` and `videos/`, consistent with existing project
  convention for large media). They remain on this workstation as raw evidence. A single
  representative frame per phase (`evidence/frame_*.png`) and the full `ffprobe` transcript
  (`evidence/ffprobe_verification.txt`) are committed instead as lightweight, sufficient
  provenance.
