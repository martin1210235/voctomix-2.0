# Development Workflow

How to develop and contribute to this project.

---

## Setup

```bash
git clone <repo-url>
cd voctomix
cp .env.example .env

# Install native dependencies (for running tests without Docker):
sudo apt install python3-gi python3-gi-cairo python3-numpy python3-scipy \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
  gstreamer1.0-libav pycodestyle
```

## Install Git Hooks (optional but recommended)

```bash
cp .claude/automations/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

This runs PEP8 lint and voctocore tests automatically before each commit.

---

## Making Changes

### voctocore

1. Edit module in `voctocore/lib/`
2. Run tests: `./voctocore/test.sh`
3. Lint: `./check_pep8.sh`
4. Test manually: `./start_studio_single_pc.sh` or Docker

### voctogui

1. Edit in `voctogui/lib/` or `voctogui/ui/`
2. Run manually: `./voctogui/voctogui.py` (requires voctocore running)
3. Lint: `./check_pep8.sh`

### Thesis (LaTeX)

```bash
cd memoria_tfg
latexmk -pdf main.tex       # full compile
latexmk -pdf -pvc main.tex  # continuous preview (auto-recompile on save)
latexmk -C                  # clean all build artifacts
```

### Docker

```bash
docker compose build        # rebuild images after code changes
docker compose up --build   # rebuild and start
docker compose logs -f <service>  # follow logs for a service
```

---

## Commit Workflow

```bash
git add voctocore/lib/audiomix.py voctocore/tests/commands/test_set_audio.py
git commit -m "fix(audiomix): correct fade duration on rapid source switch

The fade timer was not cancelled before starting a new fade,
causing volume overshoots when switching sources quickly."
```

Rules:
- Conventional Commits prefix: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
- Message in English
- Explain *what* and *why*, not just *how*
- Scope in parentheses is optional but helpful: `fix(audiomix):`, `docs(cap3):`

---

## Branch Strategy

- `main` — stable, production-ready
- Feature branches: `feat/kubernetes-deployment`, `fix/audio-fade`
- Merge via PR using [.claude/templates/PULL_REQUEST_TEMPLATE.md](../.claude/templates/PULL_REQUEST_TEMPLATE.md)

---

## Code Style

- PEP8 enforced via `check_pep8.sh` (pycodestyle)
- No comments unless strictly necessary — code should be self-explanatory
- Comments always in English, formal, minimal
- No `print()` — use `logging.getLogger('ClassName')`
- Strict module separation: `voctocore/` ↔ `voctogui/` never import each other

---

## Quick Reference

```bash
./voctocore/test.sh           # run all unit tests
./check_pep8.sh               # run PEP8 lint
./launch_docker_studio.sh     # start full Docker stack
docker compose ps             # check service health
echo "get_video" | nc localhost 9999   # test control port
```
