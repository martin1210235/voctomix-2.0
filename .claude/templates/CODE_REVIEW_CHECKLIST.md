# Code Review Checklist

Use before merging any PR into `main`.

---

## General

- [ ] Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)
- [ ] Commit messages are in English
- [ ] No commented-out code left in the diff
- [ ] No `print()` calls — use `logging`
- [ ] No hardcoded ports, resolutions, or file paths (use `Config` or env vars)

## voctocore

- [ ] New commands have a corresponding test in `voctocore/tests/commands/`
- [ ] `./voctocore/test.sh` passes with exit code 0
- [ ] GStreamer caps are explicit (`format=UYVY`, `rate=48000`, etc.)
- [ ] Pipeline state changes tested manually (source switch, composite change, overlay)

## voctogui

- [ ] No imports from `voctocore/` (strict client/server separation)
- [ ] GTK main loop not blocked (no `time.sleep()` or sync I/O)
- [ ] Telemetry exporter still exports correct JSON after change

## Docker

- [ ] `docker compose build` succeeds
- [ ] `./launch_docker_studio.sh` brings up all 10 services healthy
- [ ] `docker compose ps` shows no `unhealthy` or `exited` containers
- [ ] New env variables added to `.env.example`

## Kubernetes

- [ ] `kubectl apply -f k8s_escenario/` applies without errors
- [ ] All pods reach `Running` state within 60s
- [ ] No credentials hardcoded in YAML (use Secrets)

## Thesis (if docs: commit)

- [ ] `cd memoria_tfg && latexmk -pdf main.tex` compiles without errors
- [ ] No dashes (— or -) used as parenthetical markers (use commas)
- [ ] Sources cited are IEEE / academic / RFC-level, not blogs
- [ ] Academic tone: plural of modesty, no first-person singular

## Lint

- [ ] `./check_pep8.sh` passes (exit code 0)
