# Proposed replacement text for the Discussion section (paste manually into Overleaf)

**Location:** the paragraph Álvaro quoted on 2026-08-07 in the Teams thread, which begins
*"And finally, although the quantitative data provide a comprehensive description..."* and
currently ends *"...such comparative performance analyses will be left for future
evaluations."* This is the paragraph that must be **replaced in full**.

I do not have direct access to the paper's current Overleaf project (the git remote for
`paper/` was lost when the folder was converted from a submodule; only the text pasted by
Álvaro in the Teams thread was used to locate this paragraph precisely). Locate it by
searching for the sentence above in the live document before pasting.

---

## OLD TEXT (to delete in full)

```latex
And finally, although the quantitative data provide a comprehensive description of the
proposed architecture, no direct, parallel empirical comparison has been conducted with
tools such as OBS Studio or vMix under an identical orchestrated workload. The fact that
these established systems are exclusive to desktop computers and are closed-source
significantly complicates direct comparisons without a graphical user interface; therefore,
such comparative performance analyses will be left for future evaluations.
```

---

## NEW TEXT (paste in its place)

```latex
Finally, to move this comparison from a qualitative to an empirical basis, a single
controlled measurement was carried out on the same workstation used throughout the
evaluation, profiling OBS Studio~27 under a workload designed to be as comparable as
possible to Voctomix~2.0's own resource-footprint test: the same 1080p25 source material,
0 to 4 concurrently active sources, and whole-host CPU and RAM sampled from \texttt{/proc}
at $1\text{ Hz}$, median per phase (Table~\ref{tab:obs_comparison}). OBS Studio was
configured to encode exclusively with the software x264 encoder, never the GPU-accelerated
NVENC path, and to record continuously in every phase, including idle, so that its measured
cost reflects genuine, delivery-ready operation rather than a lighter preview-only mode.

\begin{table}[H]
\caption{Whole-host CPU and RAM utilization of Voctomix 2.0 and OBS Studio~27.2.3 under a
comparable ingest-and-composite workload (same workstation, identical 1080p25 source
material, single measurement pass; OBS software-encoded via x264, never NVENC).}
\label{tab:obs_comparison}
\small
\begin{tabularx}{\textwidth}{XCCCC}
\toprule
\textbf{Active Sources} & \textbf{Voctomix 2.0 CPU (\%)} & \textbf{OBS Studio CPU (\%)} & \textbf{Voctomix 2.0 RAM (\%)} & \textbf{OBS Studio RAM (\%)}\\
\midrule
0 (idle) & 29.0 & 6.7 & 7.2 & 5.9\\
1 & 35.9 & 16.7 & 7.9 & 6.2\\
2 & 44.5 & 22.6 & 8.6 & 6.5\\
3 & 59.5 & 30.6 & 9.2 & 6.6\\
4 & 89.6 & 39.4 & 10.0 & 6.9\\
\bottomrule
\end{tabularx}
\end{table}

Under this workload, OBS Studio exhibits a consistently lower whole-host CPU footprint,
ranging from $6.7\%$ at idle to $39.4\%$ with four active sources, against $29.0\%$ and
$89.6\%$ for Voctomix~2.0, respectively. This gap does not indicate an inefficiency in
Voctomix's implementation; it reflects two deliberate architectural differences rather than
raw engineering quality. First, OBS composites video on the GPU via OpenGL, whereas
Voctomix's compositor executes entirely on the CPU by design, keeping the mixing core
deployable on GPU-less, minimal, and horizontally orchestrated containers, a requirement
OBS does not share. Second, and more fundamentally, the measured Voctomix pipeline never
performs a full-resolution delivery encode: its raw mixing and program outputs are muxed
and transmitted uncompressed, consistent with a microservice philosophy that decouples
compositing from encoding, the latter deferred to an independently scaled downstream stage.
OBS, being a monolithic desktop application with no equivalent raw-passthrough mode, always
pays the cost of a full $1920\times1080$ software H.264 encode, even while idle. RAM usage
is comparatively less affected by these two factors and is therefore fairer to compare
directly: Voctomix consumes roughly $2$--$4\text{ GB}$ more than OBS across all camera
counts, consistent with holding uncompressed frame buffers for a larger number of
concurrent raw streams. Taken together, these results should not be read as a verdict on
raw computational efficiency, but as a quantification of the trade-off this paper argues
for: a lighter, GPU-independent, and horizontally orchestrable compositing core, obtained in
exchange for a higher, but predictable and scalable, CPU cost.
```

---

## Notes for Martín before pasting

1. **Check `\S\ref{}` targets:** the new text does not hard-reference any other section by
   `\label`, precisely because I could not re-verify current section numbering/labels
   against the live Overleaf file. If you want to add a cross-reference (e.g., to wherever
   the architecture/methodology describes the raw mix/program outputs, or to the resource
   footprint results), you know the current labels and can add `\S\ref{sec:...}` yourself;
   I deliberately avoided guessing one.
2. **Table position:** placed inline where the paragraph is, using `[H]` like the paper's
   other small tables. Move it (e.g., to `[t]`) if it creates an awkward page break, per
   your own existing rule on float placement.
3. **This paragraph is intentionally more hedged than a simple "OBS wins" table.** That is
   not caution for its own sake: the full reasoning for why it must be worded this way is in
   `experiments/obs_baseline/ANALYSIS.md` (§2, "the three asymmetries"). The short version:
   Voctomix's measured pipeline never encodes video (raw passthrough), while OBS's does by
   necessity (it has no other mode) — omitting that fact would make the comparison
   defensible-looking but actually wrong, and an MDPI reviewer with video engineering
   background is very likely to catch it.
