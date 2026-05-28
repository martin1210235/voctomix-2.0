# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 📚 Reference Files — Read When Needed

All Claude reference files live in [.claude/](.claude/). Consult them when relevant:

| File | Purpose | When to read |
|------|---------|-------------|
| [.claude/MEMORY.md](.claude/MEMORY.md) | Project context, ports, architecture, TFG structure | Always (project overview) |
| [.claude/users.md](.claude/users.md) | Your profile, preferences, technical skills | Always (workflow optimization) |
| [.claude/GLOSSARY.md](.claude/GLOSSARY.md) | Technical terminology (AFV, compositor, stream-blanker, etc.) | When unsure about terminology |
| [.claude/TROUBLESHOOTING.md](.claude/TROUBLESHOOTING.md) | Known issues and solutions | When something breaks |
| [.claude/rules/voctocore_rules.md](.claude/rules/voctocore_rules.md) | Module-specific rules for voctocore | When editing voctocore |
| [.claude/rules/voctogui_rules.md](.claude/rules/voctogui_rules.md) | Module-specific rules for voctogui | When editing voctogui |
| [.claude/rules/kubernetes_rules.md](.claude/rules/kubernetes_rules.md) | K8s-specific rules | When editing k8s_escenario/ |
| [.claude/paper_guide.md](.claude/paper_guide.md) | MDPI Electronics journal rules: template fields, section structure, style, figures, citations | **Always** when working on `paper/` |

**Freedom to edit:** I can freely update `.claude/MEMORY.md`, `.claude/users.md`, `.claude/GLOSSARY.md`, and `.claude/TROUBLESHOOTING.md` whenever I discover:
- New project information or structural changes
- Common problems and their solutions
- Updates to terminology or architecture
- Changes to your preferences or workflow

Simply update the relevant .md file immediately—**no approval needed** for documentation files.

> **Note:** This CLAUDE.md must remain at the project root — Claude Code requires it here. All other Claude reference files are in `.claude/`.

---

# Contexto del Proyecto y Arquitectura
* Proyecto: Trabajo Fin de Grado (TFG) - Desarrollo y optimización de Voctomix 2.0 (Sistema modular de código abierto para la producción remota de vídeo en tiempo real).
* Institución: ETSIT (UPM).
* Stack Tecnológico: Python 3, GStreamer, GTK 3, FFmpeg, Bash, TCP, JSON.
* Infraestructura: Docker, Docker Compose, Kubernetes, RabbitMQ (Telemetría AMQP).
* Documentación: LaTeX (compilación con latexmk).

# Commands

**Run (Docker — recommended):**
```bash
xhost +local:$(id -un)
./launch_docker_studio.sh
docker compose down   # stop
```

**Run (single PC, native):**
```bash
./start_studio_single_pc.sh
```

**Run (two PCs, native):**
```bash
# PC1: ./2pc_escenario2/start_voctocore_pc1.sh
# PC2: IP_SERVER=<IP> ./2pc_escenario2/start_voctogui_pc2.sh
```

**Tests** (voctocore only; voctogui has no tests):
```bash
make test                                                # all tests (alias for ./voctocore/test.sh)
python3 -m unittest tests.commands.test_set_video_a      # single test (from voctocore/)
```
Tests use mock GI bindings (`fake-gi.sh`) — no display or GStreamer install needed.

**Lint:**
```bash
make lint   # pycodestyle; ignores E402 (gi import order) and E501 in tests
```

**Thesis (LaTeX):**
```bash
make thesis        # compile PDF
make thesis-watch  # watch mode (latexmk -pvc)
make thesis-clean  # remove build artifacts
```

**Other `make` targets:** `docker-build`, `docker-logs`, `docker-ps`.

# Architecture

**`vocto/`** (shared library at project root): `composite_commands.py` defines the composite mode enum shared by both voctocore and voctogui. Import from here — do not duplicate in either component.

**voctocore** (Python + GStreamer, port 9999 control):
- Sources cam1-4, break, intro connect on TCP 10000-10005
- `lib/sources/`: source plugin system — `tcpavsource.py` (network), `imgvsource.py` (static image), `decklinkavsource.py` (capture card); source type set via `kind=` in config
- `lib/videomix.py` + `lib/composites.py`: compositor with fullscreen, PIP, side-by-side, lecture modes
- `lib/audiomix.py`: Audio Follows Video — auto-fades audio on source switches
- `lib/streamblanker.py`: three-state output (LIVE / PAUSE / NOSTREAM)
- `lib/overlay.py`: real-time graphic/text overlay injection
- `lib/commands.py` + `lib/controlserver.py`: line-based TCP control protocol
- `lib/transitions.py` + `lib/scene.py`: transition engine and scene graph
- Outputs: `:15000` program, `:11000` raw mix, `:12000` mix preview (JPEG), `:14000-14005` source previews

**voctogui** (Python + GTK, connects to voctocore at 9999):
- `lib/gui_state_exporter.py`: exports full mixer state as JSON every second → `registros/gui_state.json` (native) or HTTP POST to port 8080 (Docker)
- `lib/toolbar/streamblank.py`: LIVE / PAUSE / NOSTREAM toolbar buttons
- `lib/toolbar/overlay.py`: dynamic lower-thirds + auto-off on every cut

**Docker stack** (`docker-compose.yml`, 10 services): voctocore, rabbitmq (5672/15672), telemetry (8080), cam1-4, stream_blanker, intro, audio_manager. Camera containers use `network_mode: service:voctocore` (shared namespace, zero-overhead localhost communication).

**Key config files:** `voctocore/default-config.ini` (video: 1920×1080 I420 25fps; audio: 48kHz S16LE stereo), `voctogui/default-config.ini` (GUI layout).

---

# 💻 Reglas de Desarrollo del Proyecto (Código e Infraestructura)
1. Código Limpio y Modular: Al escribir o refactorizar código en Python o Bash, prioriza la modularidad. Mantén la separación estricta entre el núcleo de procesamiento (`voctocore`) y la interfaz (`voctogui`).
2. Al modificar y/o revisar cualquier fichero tienes que asegurarte de que no hay ningún comentario en el código salvo que sea estrictamente imprescindible, y en ese caso que este SIEMPRE en Inglés, formal, limpio y minimalista.
3. Infraestructura como Código: Los manifiestos de Docker y Kubernetes deben estar optimizados para un despliegue rápido y sin fricciones. Minimiza el tamaño de las imágenes.
4. Resiliencia: Al implementar la telemetría con RabbitMQ o sistemas como el Stream Blanker, asume que la red puede fallar.

# 🐙 Reglas de Control de Versiones (GitHub)
1. Commits Semánticos (Conventional Commits): Usa siempre prefijos estándar para el historial de GitHub. 
   - `feat:` para nuevas características (ej. `feat(telemetry): añadir consumidor de RabbitMQ`).
   - `fix:` para solución de errores.
   - `docs:` para cambios exclusivos en la memoria o el paper en LaTeX.
   - `refactor:` para mejoras de código que no añaden características nuevas.
2. Claridad en el Repositorio: Los mensajes de commit deben explicar el *qué* y el *por qué*, no solo el *cómo*. 
3. Idioma: Los mensajes de commit y el código fuente (variables, funciones, comentarios) deben ir siempre en inglés para mantener un estándar profesional. La documentación académica TFG irá en español, y el paper científico irá en inglés.

# 📝 Reglas de Redacción Académica (Memoria del TFG)
1. Estilo de Puntuación: Queda terminantemente prohibido usar guiones ortográficos o barras verticales ( | o - ) para incisos. Utiliza exclusivamente comas (,) para separar las ideas secundarias.
2. Fuentes y Bibliografía: Prioriza fuentes oficiales, papers académicos (Google Scholar), IEEE y estándares (RFCs, ISO/SMPTE). Si una fuente es informal (blogs/foros), busca un reemplazo de mayor autoridad académica.
3. Tono: Registro académico, objetivo y técnico. Evita la primera persona del singular (usa plural de modestia o formas impersonales).
4. Considera la posibilidad de utilizar tablas, gráficas, figuras o efectos visuales simepre que sea necesario y útil para la explicación.
5. Idioma: Español (a pesar de que proyecto, Github y paper científico en Inglés).

# 🔬 Reglas de Redacción del Paper Científico
1. Estructura IEEE/ACM: El formato del paper debe ser altamente denso y directo. Sigue la estructura: Abstract, Introducción (Estado del Arte), Metodología/Arquitectura, Resultados (Métricas/Latencia) y Conclusiones.
2. Foco en la Contribución: Destaca constantemente la "democratización de la producción", la "reducción de costes frente al hardware dedicado" y el "despliegue mediante contenedores".
3. Síntesis Extrema: A diferencia del TFG, el paper exige eliminar cualquier explicación redundante. Ve directo a los datos técnicos, la arquitectura de microservicios y los resultados empíricos obtenidos en las pruebas (ej. consumo de red, latencias sub-segundo con SRT).

# 🤖 Reglas de Comportamiento y Flujo de Trabajo
1. Rol: Actúa como mi Tutor Técnico, Arquitecto de Software Senior y Revisor Académico.
2. Archivos Completos: Salvo cambios triviales de una línea, devuelve SIEMPRE el archivo COMPLETO modificado, listo para sobreescribir, sin omitir bloques de código.
3. Justificación de Ingeniería: Explica brevemente el "porqué" de cada decisión arquitectónica para la defensa de mi TFG.
4. Paso a paso: Si una tarea afecta a varios archivos, propón un plan numerado, modifica el primero y espera mi confirmación.
5. Autonomía Máxima: Ejecuta la mayor cantidad de pasos posible de forma independiente, encadena comandos y herramientas para procesar el flujo automáticamente y solo detente si falta información crítica o permisos, para retomar la ejecución autónoma inmediatamente después de mi respuesta.