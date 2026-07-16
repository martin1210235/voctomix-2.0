# Brief de la presentación de defensa — Voctomix 2.0 (TFG ETSIT-UPM)

Documento canónico y siempre vigente con lo que el usuario quiere en la
presentación. Consultar SIEMPRE antes de tocar el deck. Actualizar cuando el
usuario dé nuevas indicaciones.

## Registro de preferencias (actualizar SIEMPRE que el usuario pida algo)
Cada vez que Martín indique cómo quiere algo, anotarlo aquí. Datos fijos:
- **Título de la presentación**: "Producción remota de vídeo en tiempo real con software
  libre" (grande y estético). Subtítulo: "Voctomix 2.0".
- **Tutor**: **David Jiménez Bermejo** (no Álvaro).
- **Estilo**: directo, conciso, sin rodeos, simple (ver [[estilo-comunicacion-martin]]).
- **Paleta**: azul + cian predominantes; poca variedad de color.
- **Divisor de sección** (diapositiva entera tipo "Portadilla", como Mar) antes de CADA
  sección: Introducción, Arquitectura, Implementación, Resultados, Conclusiones,
  Contenido adicional.
- **Resultados uno a uno**: una diapositiva por resultado, con la **figura original de la
  memoria** (se generan en `figuras/resultados/` compilando el TikZ del cap.5) y el
  esquema **POR QUÉ SE MIDE / CÓMO / RESULTADO**. Resultados: CPU, RAM, energía, latencia
  de conmutación, latencia de transición, estabilidad, resiliencia.
- **Escenarios uno a uno** con su diagrama draw.io (Monopuesto, Dos PCs, Docker, K8s).
- **CyberNEMO + Méritos** fusionados en una sola diapositiva ("Impacto y méritos"), antes
  de Conclusiones.
- **Guiones**: `GUION_PRESENTACION.md` (con tabla de tiempos + **script literal**),
  `GUION_VIDEO.md` (segundo a segundo + **script literal seguido**) y un **Word**
  `GUION_Presentacion_Voctomix.docx` (generado con `make_word.py`, más visual para él).
  Los tres + el pptx se suben a GitHub `entregables/` en cada cambio.
- **Vídeo**: montaje a dos ventanas (voctogui + salida :15000 "lo que ve el espectador");
  incluir telemetría/RabbitMQ breve (~25 s).
- **Resultados en directo = 3** (CPU, latencia de conmutación, resiliencia). RAM, energía,
  latencia de transición y estabilidad van al contenido adicional (aligerar los 15 min).
- **Ficheros nuevos** = una diapositiva monospace con los ficheros incorporados
  (`Ficheros incorporados`, Anexo C).
- **Herramientas de medición** = una diapositiva compacta con los scripts usados para
  obtener los datos.
- **Estado del arte**: la comparativa de mezcladores queda como backup para preguntas;
  la tabla extensa de protocolos/códecs se retiró del deck final para aligerar.
- **Ficheros nuevos por versión**: `backups/` guarda v1..vN. Estado actual:
  **51 diapositivas** (29 principales + 22 de apoyo).
- Config: se creó `.claude/settings.json` con `permissions.defaultMode: "auto"` (menos prompts).
- **PENDIENTE para "definitiva"**: grabar el vídeo demo, ensayo cronometrado, feedback de tutores,
  y decidir ODS (dejar/simplificar/quitar).

## Decisión de formato
- **Formato único elegido: PowerPoint** (`presentacion_voctomix_etsit.pptx`).
  El usuario ha revisado el deck y le ha gustado; a partir de ahora se trabaja
  sobre ese `.pptx`. Se descartan LaTeX/Beamer y (previsiblemente) Canva para no
  mantener tres versiones.
- La presentación se **retiró de la memoria de Overleaf**: la memoria vuelve a
  sus **100 páginas** originales. No volver a incrustarla salvo petición expresa.
- Plantilla base obligatoria: **`SFS17721.pptx`** (plantilla oficial de TFG de la
  ETSIT). Reutilizar su master, layouts, colores y tipografía.

## Condiciones del acto (fijadas por los tutores)
- **15 min de presentación + 5 min de preguntas.**
- Se presenta en una pantalla de sala; llevar **portátil propio con HDMI**.
- Parte de implementación apoyada en un **vídeo pregrabado (~4 min)** de Voctomix
  mostrando cada funcionalidad, narrado en directo por el ponente.

## Estilo deseado (guía para todo cambio futuro)
- **Dinámica, poco texto, nada aburrida.** Evitar diapositivas densas de bullets.
- Incluir **dibujos, iconos, esquemas y recursos visuales**; más agradable de ver.
- Preferir una idea por diapositiva, apoyada en imagen/diagrama.
- **Paleta: azul (#08447C) + cian (#2899F9) predominantes** + grises. Poca variedad
  de color (petición explícita del usuario). Fuera el color por entidad.
- **Profundizar**: no basta con decir "se implementó X"; explicar el CÓMO. El detalle
  fino va en la sección **"Contenido adicional"** (backup para preguntas), como Mar/Mónica.
- Ficheros vivos que se actualizan en CADA iteración: `GUION_PRESENTACION.md` (guion
  slide a slide con tiempos), `GUION_VIDEO.md` (guion del vídeo segundo a segundo) y
  las **notas del orador** de cada diapositiva del `.pptx`. Los tres guiones + el pptx
  se suben a GitHub `entregables/` en cada cambio.
- **Estilo del usuario**: directo, conciso, sin rodeos, simple. Aplicar a todo texto.
- Estado actual: **51 diapositivas** (29 principales + 22 de contenido
  adicional). Escenarios explicados uno a uno con su diagrama draw.io; sección de
  contenido adicional con índice propio, ficheros incorporados, herramientas de
  medición y resultados ampliados. Vídeo (~4 min): incluye telemetría/RabbitMQ breve y
  muestra la salida :15000 (lo que ve el espectador) en una segunda ventana.

## Backups y GitHub
- Antes de cambios grandes, **copia de seguridad** en `presentacion_tfg/backups/`
  (hecho: `presentacion_voctomix_etsit_v1_2026-07-06.pptx`).
- **NO crear repo nuevo.** Destino: repo **`martin1210235/voctomix-2.0`**, carpeta
  **`entregables/`** (junto al TFG y el paper), fichero
  **`entregables/Presentacion_Defensa_Voctomix2.0.pptx`** (el usuario la llamó
  "/escenarios"). Subir el `.pptx` ahí **SIEMPRE que se modifique** para tenerlo
  actualizado. `entregables/` se gestiona vía el proceso de publicación del repo
  público (no existe en el working tree local); definir mecanismo de push al aplicar v2.
- **Mecanismo de push** (funciona por SSH, sin tocar el working tree local):
  `git clone --depth 1 git@github.com:martin1210235/voctomix-2.0.git` en scratchpad,
  copiar el `.pptx` a `entregables/Presentacion_Defensa_Voctomix2.0.pptx`, commit y
  `git push origin HEAD`. (NO usar el repo local padre: su historial diverge del público.)
- Estado: v2 (rediseño visual, 18 slides) subida. Backups v1 y v2 en `backups/`.

## Canva / LaTeX — DESCARTADOS
- Formato único = PowerPoint. Canva y Beamer/LaTeX quedan descartados; no
  mantener versiones paralelas.

## Lecciones de presentaciones de referencia (Mar Vivanco, Mónica Ferrer)
Patrones a imitar (ambas eran muy visuales y dinámicas):
- **Una idea por slide, sostenida por un VISUAL** (diagrama, icono, chart, tabla);
  casi nada de texto en bullets.
- **Iconos en vez de bullets** por todas partes; procesos como **timelines/chevrons**.
- **Entidades con color consistente** en todo el deck (Mónica: cada modelo un color;
  Mar: cada material). Aplicar a nuestras 4 contribuciones.
- **Gancho inicial fuerte** (Mónica: titular emotivo "Seis minutos pueden cambiar
  una vida"; Mar: iconos ODS). Añadir hook + ODS (democratización).
- **Motivo de marca en las esquinas** en cada slide (cohesión visual).
- **Tablas con cabecera de color**; **logos de tecnologías** (mostrar GStreamer,
  Docker, K8s, RabbitMQ, Python como hacían con CST/MATLAB/Ollama).
- **Slide de cierre tipo recap** con cajas (resumen de objetivos) y **slide de
  méritos/publicaciones** (¡tenemos el paper MDPI! usarlo como mérito).
- La plantilla oficial `SFS17721.pptx` YA tiene layouts de Infografía, Timeline,
  SmartArt y numeración: usarlos para lograr ese estilo sin abandonar lo oficial.

## Identidad corporativa (colores oficiales ETSIT)
- Azul cabecera `#08447C` (accent5), cian acento `#2899F9` (accent1),
  texto gris `#464747`. Tipografía **Arial**.

## Contenido correcto del TFG (para pulir el deck; fuente: memoria)
- **6 objetivos específicos** OE-1..OE-6 (producción profesional, telemetría,
  Docker, Kubernetes, validación multi-escenario, despliegue real CyberNEMO).
- **4 modos de composición** con transiciones animadas + rótulos dinámicos.
- Stream Blanker (LIVE/PAUSE/NOSTREAM), Audio Follows Video.
- Telemetría: eventos `CHANGE` + estado `STATE` (cada 5 s) en JSON Lines a RabbitMQ (AMQP).
- **11 contenedores** Docker (voctocore, 6 fuentes, stream blanker, audio, RabbitMQ,
  telemetría). OJO: en el deck ponía "10 servicios"; corregir a 11.
- Validación en **4 escenarios**: monopuesto, 2 PCs LAN, Docker Compose, Kubernetes.
  Pruebas extra: latencia de conmutación y de transición entre modos, **estabilidad
  a largo plazo (sin fugas de memoria)** y **resiliencia ante fallo de cámara**.
- Resultados clave: CPU 33,5→38,8 % (Docker, 4 cám.); latencia mediana 1,5 ms
  (Docker) / 1,8 ms (K8s), muy por debajo del umbral 45 ms (ITU-R BT.1359-1).
- CyberNEMO: proyecto europeo de **ciberseguridad** en la UPM; producción real.

## Estructura actual del deck (51 diapositivas)
- **1–29 principal:** portada, índice, introducción, arquitectura, demo, escenarios,
  tres resultados clave, conclusiones, líneas futuras, impacto y cierre.
- **30–51 apoyo:** índice de apoyo, puertos, implementación, ficheros incorporados,
  herramientas de medición, resultados ampliados, comparativa de mezcladores y presupuesto.

## Cómo se genera
- `build_pptx.py` (python-pptx) construye el deck sobre `SFS17721.pptx`.
- Verificación visual: exportar con LibreOffice a PDF y revisar páginas.
