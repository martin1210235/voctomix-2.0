#!/usr/bin/env python3
"""Submission-oriented audit for the Voctomix 2.0 MDPI paper.

This complements check_paper.sh: it does not decide scientific quality, but it
surfaces measurable risks before submission.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper"
TEX = PAPER / "main.tex"
BIB = PAPER / "references.bib"
LOG = PAPER / "main.log"
PDF = PAPER / "main.pdf"
MAX_PAGES = 20


def strip_tex_commands(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\cite[tp]?\{[^}]*\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", r" \1 ", text)
    text = re.sub(r"[{}$]", " ", text)
    return text


def find_block(text: str, command: str) -> str:
    needle = "\\" + command + "{"
    start = text.find(needle)
    if start < 0:
        return ""
    i = start + len(needle)
    depth = 1
    out: list[str] = []
    while i < len(text) and depth:
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        out.append(ch)
        i += 1
    return "".join(out)


def extract_urls(text: str) -> list[str]:
    urls = re.findall(r"https?://[^} )\]\n]+", text)
    return sorted(set(url.rstrip(".,;") for url in urls))


def pdf_pages() -> int | None:
    if not PDF.exists():
        return None
    try:
        proc = subprocess.run(
            ["pdfinfo", str(PDF)],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return None
    match = re.search(r"^Pages:\s+(\d+)", proc.stdout, flags=re.M)
    return int(match.group(1)) if match else None


def bib_entry_blocks(bib: str) -> list[tuple[str, str, str]]:
    entries: list[tuple[str, str, str]] = []
    starts = list(re.finditer(r"@\s*(\w+)\s*\{\s*([^,\s]+)\s*,", bib))
    for idx, match in enumerate(starts):
        start = match.start()
        end = starts[idx + 1].start() if idx + 1 < len(starts) else len(bib)
        entries.append((match.group(1).lower(), match.group(2), bib[start:end]))
    return entries


def check_url(url: str, timeout: int = 12) -> tuple[str, str]:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "voctomix-paper-audit/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return "OK", str(response.status)
    except urllib.error.HTTPError as exc:
        if exc.code in {403, 405}:
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "voctomix-paper-audit/1.0"})
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    return "OK", str(response.status)
            except Exception as retry_exc:  # noqa: BLE001 - report exact external failure
                if exc.code == 403:
                    return "WARN", f"HTTP 403 or bot-blocked: {retry_exc}"
                return "FAIL", f"{type(retry_exc).__name__}: {retry_exc}"
        return "FAIL", f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001 - report exact external failure
        return "FAIL", f"{type(exc).__name__}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Submission-oriented audit for the MDPI paper.")
    parser.add_argument(
        "--check-urls",
        action="store_true",
        help="Perform live HTTP checks for URLs in main.tex and references.bib.",
    )
    args = parser.parse_args()

    tex = TEX.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")
    log = LOG.read_text(encoding="utf-8", errors="ignore") if LOG.exists() else ""
    failures = 0
    warnings = 0

    abstract = strip_tex_commands(find_block(tex, "abstract"))
    abstract_words = re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]*", abstract)

    entries = bib_entry_blocks(bib)
    bib_entries = re.findall(r"^\s*@\w+\{", bib, flags=re.M)
    cite_keys = sorted(set(k.strip() for m in re.findall(r"\\cite[tp]?\{([^}]*)\}", tex)
                           for k in m.split(",") if k.strip()))
    figures = re.findall(r"\\begin\{figure\}", tex)
    tables = re.findall(r"\\begin\{table\}", tex)
    sections = re.findall(r"^\\section\{([^}]*)\}", tex, flags=re.M)
    subsections = re.findall(r"^\\subsection\{([^}]*)\}", tex, flags=re.M)

    print("# Paper Audit Metrics\n")
    print(f"- Abstract words: {len(abstract_words)}")
    print(f"- Bibliography entries: {len(bib_entries)}")
    print(f"- Cited keys: {len(cite_keys)}")
    print(f"- Figures: {len(figures)}")
    print(f"- Tables: {len(tables)}")
    print(f"- Sections: {len(sections)} -> {', '.join(sections)}")
    print(f"- Subsections: {len(subsections)}")
    pages = pdf_pages()
    if pages is None:
        print("- PDF pages: UNKNOWN (pdfinfo/main.pdf unavailable)")
        warnings += 1
    else:
        status = "OK" if pages <= MAX_PAGES else "FAIL"
        print(f"- PDF pages: {pages} / {MAX_PAGES} ({status})")
        if pages > MAX_PAGES:
            failures += 1

    print("\n## MDPI Back Matter\n")
    for command in [
        "authorcontributions",
        "funding",
        "institutionalreview",
        "informedconsent",
        "dataavailability",
        "acknowledgments",
        "conflictsofinterest",
        "abbreviations",
    ]:
        present = ("\\" + command + "{") in tex
        print(f"- {command}: {'OK' if present else 'MISSING'}")

    print("\n## Build Log Signals\n")
    overfull = re.findall(r"Overfull \\hbox \(([^)]*)\).*?lines ([0-9\\-]+)", log)
    undefined = re.findall(r"(Citation .* undefined|Reference .* undefined)", log, flags=re.I)
    print(f"- Undefined refs/citations: {len(undefined)}")
    print(f"- Overfull hbox warnings: {len(overfull)}")
    if undefined:
        failures += 1
    if overfull:
        warnings += 1
    for amount, lines in overfull[:20]:
        print(f"  - lines {lines}: {amount}")

    print("\n## Bibliography Metadata\n")
    missing_locator: list[str] = []
    uncited = sorted(set(key for _, key, _ in entries) - set(cite_keys))
    for kind, key, block in entries:
        has_doi = re.search(r"\bdoi\s*=", block, flags=re.I)
        has_url = re.search(r"\burl\s*=", block, flags=re.I) or "http" in block
        if kind not in {"book", "manual", "misc"} and not (has_doi or has_url):
            missing_locator.append(key)
    print(f"- Uncited bibliography entries: {len(uncited)}")
    for key in uncited[:20]:
        print(f"  - {key}")
    print(f"- Cited non-book/manual entries without DOI or URL: {len(missing_locator)}")
    for key in missing_locator[:20]:
        print(f"  - {key}")
    if uncited or missing_locator:
        warnings += 1

    print("\n## Sensitive Text Hits\n")
    patterns = [
        "six composite modes",
        "CHANGE and STATE queues",
        "source-switching latency below 5",
        "not instrumented",
        "No containerisation path",
        "No containerization path",
        "No data",
        "No TODO",
        "0000-0000",
    ]
    for pat in patterns:
        hits = [m.start() for m in re.finditer(re.escape(pat), tex, flags=re.I)]
        print(f"- {pat}: {len(hits)}")

    print("\n## Data Availability\n")
    dataavailability = find_block(tex, "dataavailability")
    data_urls = extract_urls(dataavailability)
    print(f"- URLs in dataavailability: {len(data_urls)}")
    for url in data_urls:
        print(f"  - {url}")
    if not data_urls:
        print("  - FAIL: no repository/data URL found in dataavailability")
        failures += 1

    print("\n## URLs Mentioned\n")
    urls = extract_urls(tex + "\n" + bib)
    for url in urls:
        print(f"- {url}")
    if args.check_urls:
        print("\n## Live URL Check\n")
        for url in urls:
            status, detail = check_url(url)
            print(f"- {status} {url} ({detail})")
            if status == "FAIL":
                failures += 1
            elif status == "WARN":
                warnings += 1
    else:
        print("\n## Live URL Check\n")
        print("- SKIPPED: run with --check-urls when network access is available.")

    print("\n## Submission Gate\n")
    print(f"- Failures: {failures}")
    print(f"- Warnings: {warnings}")
    if failures:
        print("- RESULT: FAIL")
        return 1
    print("- RESULT: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
