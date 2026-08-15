# Discussion text used for the OBS comparison

This is the text that was added to the paper's Discussion section (Table 4
and the paragraph that introduces and interprets it), kept here for
reference alongside the raw data and the reasoning in `ANALYSIS.md`.

## Where it went

It replaced the closing sentence of the paragraph on page limitations, the
one that used to say a direct comparison with OBS Studio or vMix had not
been carried out and was left for future work. That sentence is no longer
accurate once the comparison below existed, so the Discussion section was
updated instead.

## Final text (as applied in the paper)

```latex
And finally, a single controlled measurement against OBS Studio was
additionally carried out on the same workstation to move part of this
comparison onto an empirical footing (Table~\ref{tab:obs_comparison},
discussed below); vMix was excluded because its Windows-only, GUI-driven
design precludes the same scripted, single-pass measurement.

The workload was designed to resemble Voctomix~2.0's own resource-footprint
test: the same 1080p25 source material, zero to four concurrently active
sources, and whole-host CPU and RAM sampled from \texttt{/proc} at 1~Hz,
median per phase. OBS was configured to encode exclusively with the software
x264 encoder, never NVENC, and to record continuously in every phase,
including idle, so that its measured cost reflects genuine delivery-ready
operation.

\begin{table}[t]
\caption{Whole-host CPU and RAM utilization of Voctomix 2.0 and OBS
Studio~27.2.3 under a comparable workload on the same workstation, OBS
software-encoded via x264.\label{tab:obs_comparison}}
\begin{tabularx}{\textwidth}{lCCCC}
\toprule
\textbf{Active sources} & \textbf{Voctomix 2.0 CPU (\%)} & \textbf{OBS Studio CPU (\%)} & \textbf{Voctomix 2.0 RAM (\%)} & \textbf{OBS Studio RAM (\%)}\\
\midrule
0 (idle) & 29.0 & 6.7  & 7.2  & 5.9\\
1        & 35.9 & 16.7 & 7.9  & 6.2\\
2        & 44.5 & 22.6 & 8.6  & 6.5\\
3        & 59.5 & 30.6 & 9.2  & 6.6\\
4        & 89.6 & 39.4 & 10.0 & 6.9\\
\bottomrule
\end{tabularx}
\end{table}

Under this workload, OBS Studio shows a consistently lower whole-host CPU
footprint, from 6.7\% at idle to 39.4\% with four active sources, against
29.0\% and 89.6\% for Voctomix~2.0. This gap reflects two architectural
differences rather than an implementation inefficiency. First, OBS composites
video on the GPU via OpenGL, whereas Voctomix's compositor executes entirely
on the CPU by design, keeping the mixing core deployable on GPU-less,
orchestrated containers. Second, the measured Voctomix pipeline never
performs a full-resolution delivery encode, muxing and transmitting raw
frames, consistent with a microservice philosophy that decouples compositing
from encoding; OBS, lacking an equivalent raw-passthrough mode, always pays
for a full 1920$\times$1080 software H.264 encode. RAM, less affected by
these factors, is fairer to compare directly: Voctomix consumes roughly
2--4~GB more than OBS across all camera counts, consistent with holding
uncompressed buffers for more concurrent raw streams. These results should
be read not as a verdict on raw computational efficiency, but as a
quantification of this paper's core trade-off: a lighter, GPU-independent,
horizontally orchestrable compositing core in exchange for a higher, but
predictable, CPU cost.
```

## Why it is written this way

The paragraph could have simply said "OBS uses less CPU than Voctomix" and
stopped there, but that would be misleading on its own: OBS was recording a
full H.264 stream while the measured Voctomix pipeline sends raw,
uncompressed video, so the two are not doing quite the same amount of work.
Leaving that detail out would make the comparison look clean while actually
being incomplete, and a reviewer with video engineering background would very
likely catch it. The full reasoning is in `ANALYSIS.md`.

The numbers in the table come directly from `obs_resumen.csv` in this same
folder, and match the Voctomix values already published elsewhere in the
paper (`paper/pruebas/local_1080p25/1-1_escalado/resumen.csv`).
