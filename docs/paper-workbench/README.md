# Paper Workbench

Working knowledge base and tooling for the scientific paper (`paper/`, an
Overleaf-mirrored manuscript). These files live **here**, in the main GitHub
repo, so they are version-controlled and backed up — deliberately kept **out of
the Overleaf manuscript** to avoid cluttering the submission.

## Files

| File | Role |
|---|---|
| [PAPER_STATUS.md](PAPER_STATUS.md) | **Hub** — status, blockers, pending external data, file map |
| [DATA_CONSISTENCY.md](DATA_CONSISTENCY.md) | Canonical figures paper ↔ TFG ↔ raw data |
| [PAPER_REVIEW_CHECKLIST.md](PAPER_REVIEW_CHECKLIST.md) | Review rules (adapted from the TFG checklist, for the English paper) |
| [PAPER_PATTERNS.md](PAPER_PATTERNS.md) | Presentation patterns from analysed comparable papers (grows over time) |
| [RELATED_WORK_NOTES.md](RELATED_WORK_NOTES.md) | Citation candidates / venue-fit notes |
| [check_paper.sh](check_paper.sh) | Automated guardian (the automatable part of the checklist) |

## Automation

`check_paper.sh` is installed as the **git pre-commit hook** of the paper repo,
so every `git commit` inside `paper/` automatically runs the consistency checks
(citations defined, zero broken references, no stray notes/merge markers, no
discarded values) and blocks the commit on failure.

Re-install after cloning:

```bash
ln -sf "$(pwd)/docs/paper-workbench/check_paper.sh" paper/.git/hooks/pre-commit
```

Run the checks manually at any time:

```bash
bash docs/paper-workbench/check_paper.sh
```
