# Paper Guide — Voctomix 2.0 (MDPI Electronics)

Complete reference for writing and formatting the scientific paper. Read this before touching `paper/template.tex`.

---

## 1. Journal and Template Facts

- **Journal**: Electronics (MDPI) — `https://www.mdpi.com/journal/electronics`
- **Template file**: `paper/template.tex` (class from `paper/Definitions/mdpi.cls`)
- **CRITICAL — fix documentclass**: The cloned template has `apajournal` as first option, which forces APA author-date citations. Electronics uses **numbered citations** `[1]`. Change line 5 to:
  ```latex
  \documentclass[electronics,article,submit,pdftex,moreauthors]{Definitions/mdpi}
  ```
- **Citation format**: Numeric `[N]`, NOT author-date. Use `\cite{}` not `\citep{}`.
- **Reference style**: `Definitions/mdpi.bst` (not `mdpi_apacite.bst`). Use `\bibliography{references}` with an external `.bib` file — do not use the internal `thebibliography` environment from the template.
- **Target length**: 15–20 pages (Sofia's paper: exactly 20 pages, 40 references).
- **Number of figures**: aim for 6–10 (Sofia: 8 figures). Architecture diagram mandatory.
- **Number of tables**: 2–4 (Sofia: 2 tables with real metrics).
- **Language**: English, academic, impersonal. Never first person singular.

---

## 2. Template: Complete Field-by-Field Guide

### 2.1 Frontmatter (before `\begin{document}`)

```latex
\Title{Full Paper Title in Title Case}
```
- Keep under 20 words. Front-load the key contribution.
- Our title candidate: *Voctomix 2.0: An Open-Source Modular Architecture for Real-Time Remote Video Production*

```latex
\newcommand{\orcidauthorA}{0000-0000-0000-000X}
```
- One `\orcidauthorA`, `\orcidauthorB`, etc. per author who has ORCID. Get real ORCID IDs.

```latex
\Author{Firstname Lastname $^{1}$\orcidA{}, Firstname Lastname $^{1,}$*}
```
- `$^{1}$` = affiliation superscript. `*` = corresponding author. `\orcidA{}` after name if ORCID defined.
- `moreauthors` class option already set (correct for 2+ authors).

```latex
\AuthorNames{Firstname Lastname, Firstname Lastname}
```
- Same authors, plain text, for PDF metadata. No superscripts.

```latex
\address{%
$^{1}$ \quad Affiliation; email@domain.com}
```
- Full institutional address. For UPM: *Departamento de Señales, Sistemas y Radiocomunicaciones, Escuela Técnica Superior de Ingenieros de Telecomunicación, Universidad Politécnica de Madrid, 28040 Madrid, Spain*

```latex
\corres{Correspondence: email@domain.com}
```
- Corresponding author email only (no phone required).

```latex
\abstract{Single paragraph, 150–250 words. No blank lines inside.}
```
- **Structure** (no headings, just flow): (1) Background — why this matters; (2) Methods — what we built/did; (3) Results — key measurable outcome; (4) Conclusions — main takeaway.
- Sofia's abstract: ~250 words, very dense, ends with two concrete metrics (MOS > 3 72.92% of the time; Precision 93.6%, Recall 80.4%).
- Our abstract must end with at least one concrete metric (e.g., pipeline latency, CPU usage, number of simultaneous sources handled).

```latex
\keyword{keyword1; keyword2; keyword3; ...}
```
- 5–10 keywords, separated by semicolons. Sofia used 8.
- Candidates: GStreamer; live video production; remote production; open-source; Docker; Kubernetes; real-time video mixing; broadcast automation

---

## 3. Section Structure (Electronics journal — confirmed from Sofia's paper)

The real Electronics structure differs from the generic template. Follow this order:

### Section 0 — DELETE
Remove entirely:
```latex
\setcounter{section}{-1}
\section{How to Use this Template}
```

### Section 1 — Introduction
**Length**: ~1.5–2 pages (500–700 words).
**Structure**:
1. Opening: broad context (live video production, cost of professional hardware, democratization).
2. Problem statement: what existing tools lack (proprietary, expensive, non-containerizable).
3. Related work overview: cite key papers (OBS, vMix, prior Voctomix uses — including Sofia's paper).
4. Our contribution: explicit bullet-point list (4–6 items) of what this paper contributes.
5. Paper structure sentence: "The remainder of this paper is organized as follows: Section 2 describes..."

**Contributions bullet format** (copy Sofia's style):
```latex
\begin{itemize}
\item Modular GStreamer-based pipeline supporting N simultaneous sources...
\item Containerized deployment via Docker and Kubernetes enabling...
\item Real-time telemetry via RabbitMQ AMQP...
\item ...
\end{itemize}
```

### Section 2 — Background and Related Work
**Length**: ~1.5 pages. **Not in generic template but present in Electronics papers.**
**Subsections**:
- `2.1` Live Video Production Systems (OBS Studio, vMix, hardware mixers — ATEM, Roland)
- `2.2` Open-Source Media Pipelines (GStreamer, FFmpeg-based systems)
- `2.3` Containerized Media Workflows (prior work on Docker/K8s for media)

End each subsection with a sentence explaining the gap our work fills.

### Section 3 — System Architecture
**This is our "Materials and Methods".** ~4–5 pages. Most important section.
**Subsections**:
- `3.1` Architecture Overview — block diagram figure here (mandatory, like Sofia's Figure 1)
- `3.2` voctocore: the Processing Core
  - `3.2.1` GStreamer Pipeline Design
  - `3.2.2` Source Management and Input Handling
  - `3.2.3` Composite Modes and Video Mixing
  - `3.2.4` Audio Follows Video (AFV)
  - `3.2.5` Stream Blanker and Output Control
  - `3.2.6` Overlay System
- `3.3` voctogui: the Control Interface — include screenshot (like Sofia's Figure 4)
- `3.4` TCP Control Protocol
- `3.5` Telemetry and Monitoring (RabbitMQ / AMQP)

### Section 4 — Deployment
**Length**: ~2 pages.
**Subsections**:
- `4.1` Single-PC Deployment (native, development scenario)
- `4.2` Docker Compose Stack — include docker-compose architecture diagram
- `4.3` Kubernetes Deployment (multi-node scenario)

### Section 5 — Results and Validation
**Length**: ~2–3 pages. **Must contain real measured data.**
**Required content**:
- Table with performance metrics (CPU, memory, latency — measured)
- Latency measurements (end-to-end pipeline delay)
- Multi-source switching tests
- Comparison table: Voctomix vs. OBS vs. vMix vs. hardware (cost, features, containerizable)

**Subsections**:
- `5.1` Test Environment and Methodology
- `5.2` Pipeline Performance Metrics (table with real numbers)
- `5.3` Multi-Scenario Validation (single-PC, 2-PC, Docker, K8s)

### Section 6 — Discussion
**Length**: ~1 page.
- Interpret results: what do the metrics mean?
- Compare with related work.
- Limitations: what does Voctomix 2.0 not do well?
- Future work (brief, 1 paragraph).

### (Optional) Section 7 — Conclusions
Sofia's paper does NOT have a separate Conclusions section — it is absorbed into Discussion. The template marks it as optional. We can skip it or keep it very short (3–5 sentences).

---

## 4. Backmatter — Mandatory Fields

Fill these exactly as shown. Sofia's paper is the reference for wording.

```latex
\authorcontributions{Conceptualization, X.X. and Y.Y.; Methodology, X.X.; 
Software, X.X.; Validation, X.X. and Y.Y.; Formal analysis, X.X.; 
Investigation, X.X.; Writing---original draft preparation, X.X.; 
Writing---review and editing, Y.Y.; Supervision, Y.Y.; 
All authors have read and agreed to the published version of the manuscript.}
```
Use initials (e.g., M.H.S. for Martín Herranz Sánchez). Use the CRediT taxonomy terms exactly.

```latex
\funding{This research received no external funding.}
```
Or mention grant if applicable. Also declare APC funding if covered.

```latex
\institutionalreview{Not applicable.}
\informedconsent{Not applicable.}
```
Standard for purely technical/engineering papers with no human subjects.

```latex
\dataavailability{The source code supporting the results of this article 
is publicly available at \url{https://github.com/...}.}
```
Point to the GitHub repo.

```latex
\acknowledgments{The authors wish to thank [tutor name] for supervision 
and guidance throughout this work.}
```

```latex
\conflictsofinterest{The authors declare no conflicts of interest.}
```

```latex
\abbreviations{Abbreviations}{
The following abbreviations are used in this manuscript:\\
\noindent
\begin{tabular}{@{}ll}
AFV  & Audio Follows Video\\
AMQP & Advanced Message Queuing Protocol\\
...
\end{tabular}
}
```

---

## 5. Figures and Tables — Style Rules

### Figures
```latex
\begin{figure}[H]
\includegraphics[width=\textwidth]{figures/architecture_overview}
\caption{System architecture overview of Voctomix 2.0.\label{fig:arch}}
\end{figure}
```
- Use `[H]` float specifier (required by MDPI).
- Caption: sentence case, ends with period. No bold except subfigure labels.
- Subfigures: `(\textbf{a})` Description. `(\textbf{b})` Description.
- All figures must be cited in text before they appear: `(see Figure~\ref{fig:arch})`.
- Minimum resolution: 300 DPI for raster images. Prefer vector (PDF/EPS/SVG).
- **Mandatory figures for our paper**:
  - Fig 1: Full system block diagram (draw.io or TikZ)
  - Fig 2: voctocore GStreamer pipeline diagram
  - Fig 3: Voctogui screenshot (real screenshot from running system)
  - Fig 4: Docker Compose architecture diagram
  - Fig 5: K8s deployment diagram
  - Fig 6+: Performance charts (latency over time, CPU usage)

### Tables
```latex
\begin{table}[H]
\caption{Performance comparison.\label{tab:perf}}
\begin{tabularx}{\textwidth}{LCCC}
\toprule
\textbf{Metric} & \textbf{Value A} & \textbf{Value B} & \textbf{Value C}\\
\midrule
Entry & Data & Data & Data\\
\bottomrule
\end{tabularx}
\end{table}
```
- Use `booktabs` style: `\toprule`, `\midrule`, `\bottomrule`. Never use vertical lines.
- Column alignment codes for `tabularx`: `L` (left), `C` (center), `R` (right), `X` (fill).
- Caption above the table (MDPI style).

---

## 6. Citation Rules

- **Format in text**: `[1]`, `[1,2]`, `[1--3]`. Never author-date.
- **Command**: `\cite{key}` (NOT `\citep{}`).
- **Bibliography**: use external `.bib` file with `\bibliography{references}`. Copy `memoria_tfg/biblio.bib` as starting point.
- **Reference format in .bib** (Electronics style):
  - Journal: Author, F.S.; Author2, F.S. Title. *Journal* **Year**, *Vol*, pages. DOI.
  - Conference: Author, F.S. Title. In Proceedings of Conference, City, Country, Date; pp. X--Y.
  - Online: Author, F.S. Title. Year. Available online: URL (accessed on Day Month Year).
- **Minimum references**: 25–30. Sofia used 40.
- **Sofia's paper must be cited** as a related work that deployed Voctomix v1.3 as Production Core.

---

## 7. Writing Style Rules (Electronics / MDPI)

1. **Impersonal voice**: "The system processes..." not "We process...". Occasional "we" acceptable in methodology.
2. **Present tense** for describing the system; **past tense** for describing experiments.
3. **No padding**: every sentence must add information. No "it is worth noting that...".
4. **Abbreviations**: define at first use: "Audio Follows Video (AFV)". After first use, always abbreviation.
5. **Numbers**: spell out one–nine; use digits for 10 and above. Exception: always digits before units ("5 ms", "4 cameras").
6. **Units**: always SI. Use thin space before unit: `5~ms`, `1920~×~1080`, `25~fps`.
7. **Software names**: italicise or keep plain — be consistent. GStreamer, Docker, Kubernetes (capitals as official names).
8. **Equations**: only if truly needed for a technical description. Punctuate as regular text.
9. **Subsection depth**: maximum `\subsubsection` (3 levels). Do not go deeper.
10. **Paragraph length**: 4–8 sentences. Never a 1-sentence paragraph (except in lists).

---

## 8. Key Observations from Sofia's Paper (Electronics 2025, 14, 4115)

This paper is the closest published reference — same journal, same domain, uses Voctomix v1.3 as a component.

| Aspect | Sofia's paper | Our target |
|---|---|---|
| Total pages | 20 | 15–20 |
| Sections | 6 + backmatter | 6–7 + backmatter |
| References | 40 | 25–40 |
| Figures | 8 | 6–10 |
| Tables | 2 | 2–4 |
| Abstract length | ~250 words | 200–250 words |
| Introduction | 3 pages, bullet contributions | same |
| Metrics in results | MOS values, Precision/Recall | latency, CPU, throughput |

**Sofia's section naming vs. template**: she uses "Background and Related Work" (not in template), "Smart Media City Use Case" instead of "Materials and Methods", and "Results and Validation" instead of plain "Results". Section names are flexible — choose descriptive names over generic ones.

**Critical connection to cite**: Sofia's paper cites Voctomix/Voctocore v1.3 (`github.com/voc/voctomix/tree/voctomix2/voctocore`) and Voctogui v1.3 as the Production Core in a real trial. Our paper extends this: we are the authors of the system that their paper uses. This must be stated clearly in Introduction and Discussion.

---

## 9. Our Paper — Content Checklist

Before submitting to tutor for review, verify:

- [ ] `\documentclass[electronics,...]` — NOT `apajournal`
- [ ] Abstract: 200–250 words, structured, ends with a concrete metric
- [ ] Introduction: ends with explicit bullet-point contribution list
- [ ] Section 2 "Background and Related Work" included
- [ ] Architecture block diagram (Figure 1) — complete system overview
- [ ] Voctogui screenshot included
- [ ] At least one table with real measured performance data
- [ ] Sofia's paper cited as related work
- [ ] GitHub repo URL in Data Availability Statement
- [ ] All abbreviations defined at first use AND listed in Abbreviations section
- [ ] `\institutionalreview{Not applicable.}` and `\informedconsent{Not applicable.}`
- [ ] No `\section{How to Use this Template}` remaining
- [ ] References compiled with `mdpi.bst` (not `mdpi_apacite.bst`)
- [ ] All figures cited in text before they appear
- [ ] All figures use `[H]` float specifier
