# Contributing to Voctomix 2.0

Thanks for your interest in contributing. This guide covers the development
setup, conventions and review flow.

## Project layout

Voctomix 2.0 keeps a strict separation between the processing core and the
operator interface:

- `voctocore/` — Python + GStreamer mixing engine (has unit tests).
- `voctogui/` — Python + GTK operator interface (no tests).
- `vocto/` — shared library (e.g. the composite-mode enum). Import shared
  definitions from here; never duplicate them in either component.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full picture.

## Development setup

Install the native prerequisites listed in the [README](README.md#prerequisites)
(Python 3.10+, GStreamer 1.20+, GTK 3, FFmpeg). For most changes the Docker
stack is the fastest way to run the whole system:

```bash
pip3 install -r requirements-dev.txt
```

```bash
./launch_docker_studio.sh    # build + launch the full stack
sudo docker compose down     # stop everything
docker compose logs -f       # follow logs
```

## Before opening a pull request

```bash
sh voctocore/test.sh   # voctocore unit tests (mock GI bindings)
sh check_pep8.sh       # pycodestyle (ignores E402 for gi import order, E501 in tests)
```

Run a single test from `voctocore/`:

```bash
python3 -m unittest tests.commands.test_set_video_a
```

## Coding conventions

- **Language:** all source code, identifiers and commit messages in **English**.
- **Comments:** avoid comments unless strictly necessary; when needed, keep them
  in formal, minimal English.
- **Style:** clean and modular; respect the core/GUI separation.
- **Infrastructure as code:** keep Docker/Kubernetes manifests minimal and image
  sizes small.
- **Resilience:** assume the network can fail (telemetry, stream blanker).

## Commit messages (Conventional Commits)

Use standard prefixes:

- `feat:` new feature — e.g. `feat(telemetry): add RabbitMQ consumer`
- `fix:` bug fix
- `docs:` documentation only
- `refactor:` code improvement with no behaviour change

Messages should explain the *what* and the *why*, not only the *how*.

## Reporting issues

Open an issue at <https://github.com/martin1210235/voctomix-2.0/issues> with:
what you expected, what happened, the deployment scenario (single-PC, two-PC,
Docker, Kubernetes), and relevant logs.
For setup problems, check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) first.
