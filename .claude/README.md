# .claude/ — Claude Code Reference Files

Index of all files that Claude Code reads automatically in this project.

---

## Core Context (read every session)

| File | Purpose |
|------|---------|
| [MEMORY.md](MEMORY.md) | Project overview, ports, modules, TFG chapter structure |
| [users.md](users.md) | User profile, technical skills, work preferences |
| [GLOSSARY.md](GLOSSARY.md) | Technical terminology — AFV, compositor, stream-blanker, etc. |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Known errors and their solutions (copy-paste commands) |
| [HOW_CLAUDE_READS.md](HOW_CLAUDE_READS.md) | How the auto-memory system works |

## Module Rules (read when editing that module)

| File | Scope |
|------|-------|
| [rules/voctocore_rules.md](rules/voctocore_rules.md) | voctocore/ — GStreamer pipeline, modules, tests |
| [rules/voctogui_rules.md](rules/voctogui_rules.md) | voctogui/ — GTK interface, telemetry exporter |
| [rules/kubernetes_rules.md](rules/kubernetes_rules.md) | k8s_escenario/ — Kubernetes manifests |

## PR / Issue Templates

| File | Use |
|------|-----|
| [templates/PULL_REQUEST_TEMPLATE.md](templates/PULL_REQUEST_TEMPLATE.md) | Fill when opening a PR |
| [templates/BUG_REPORT_TEMPLATE.md](templates/BUG_REPORT_TEMPLATE.md) | Fill when reporting a bug |
| [templates/FEATURE_REQUEST_TEMPLATE.md](templates/FEATURE_REQUEST_TEMPLATE.md) | Fill when proposing a feature |
| [templates/CODE_REVIEW_CHECKLIST.md](templates/CODE_REVIEW_CHECKLIST.md) | Checklist before merging |

## Automations

| File | Purpose |
|------|---------|
| [automations/hooks.json](automations/hooks.json) | Claude Code hooks (post-tool, pre-tool) |
| [automations/settings.json](automations/settings.json) | Claude Code project settings |
| [automations/pre-commit.sh](automations/pre-commit.sh) | Git pre-commit hook (lint + test) |

---

## Project Documentation (in docs/)

| File | Purpose |
|------|---------|
| [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) | Deep-dive system architecture |
| [../docs/API_REFERENCE.md](../docs/API_REFERENCE.md) | TCP :9999 control protocol |
| [../docs/DEPLOYMENT_GUIDE.md](../docs/DEPLOYMENT_GUIDE.md) | Step-by-step deployment for all 3 scenarios |
| [../docs/DEPENDENCIES.md](../docs/DEPENDENCIES.md) | Minimum version requirements |
| [../docs/TESTING_STRATEGY.md](../docs/TESTING_STRATEGY.md) | Testing approach and coverage |
| [../docs/PERFORMANCE_BASELINE.md](../docs/PERFORMANCE_BASELINE.md) | Benchmarks and metrics |
| [../docs/DEPLOYMENT_CHECKLIST.md](../docs/DEPLOYMENT_CHECKLIST.md) | Pre-production checklist |
| [../docs/DEVELOPMENT_WORKFLOW.md](../docs/DEVELOPMENT_WORKFLOW.md) | How to develop and contribute |
