# Auditoria final del paper - 2026-07-08

Revision del manuscrito `paper/main.tex` para envio a MDPI Electronics.
Este documento no aplica cambios al paper; prioriza riesgos y mejoras con evidencia.

## Veredicto

No lo enviaria todavia en el estado actual. El paper esta bastante avanzado y la
historia cientifica es defendible, pero quedan varios riesgos formales y factuales
que un revisor o editor puede detectar facilmente.

Nota actual estimada: 7.2/10.

Nota esperable tras corregir los bloqueantes: 8.4-8.7/10.

Fortalezas principales:

- Encaje tematico bueno con Electronics: el alcance oficial incluye Computer
  Science & Engineering, Networks, Systems & Control Engineering, Circuit and
  Signal Processing y Electronic Multimedia.
- Estructura IMRaD completa, con arquitectura, despliegue, resultados,
  discusion, limitaciones, seguridad y conclusiones.
- Compila sin referencias ni citas indefinidas.
- Las cifras principales de CPU, RAM, latencia y resiliencia estan alineadas
  con los ficheros experimentales locales y la memoria del TFG.
- El trabajo tiene contribucion clara: Voctomix abierto, modular, con Docker,
  Kubernetes, telemetria RabbitMQ, AFV, blanker y overlays.

## Evidencia objetiva

Script creado: `docs/paper-workbench/audit_paper.py`.

Salida principal del auditor:

- Abstract: 239 palabras.
- Bibliografia: 36 entradas.
- Claves citadas: 24.
- Figuras: 7.
- Tablas: 6.
- Secciones: Introduction, Background and Related Work, System Architecture,
  Deployment Scenarios, Results and Validation, Discussion, Conclusions.
- Referencias/citas indefinidas: 0.
- Overfull hbox: 14 avisos, algunos grandes: 91.02 pt, 91.70 pt, 85.83 pt.
- Texto sensible detectado: `six composite modes` aparece 1 vez; ORCID
  placeholder `0000-0000` aparece 8 veces en comentarios.

## Bloqueantes antes de enviar

### 1. Author Contributions incompleto

Problema: `paper/main.tex:1297` solo asigna contribuciones a M.H.S. y A.L.,
pero el manuscrito tiene cuatro autores. MDPI exige un parrafo con contribucion
individual para varios autores.

Evidencia:

- `paper/main.tex:34` lista a Martin, Alvaro, Alberto y David.
- `paper/main.tex:1297` no asigna tareas a Alberto ni David.
- MDPI Instructions: Author Contributions debe especificar contribuciones
  individuales de cada autor.

Mejor solucion:

- Confirmar con los autores reales y rellenar CRediT para los cuatro.
- Si Alberto o David no cumplen autoria sustancial, moverlos a acknowledgments;
  si si la cumplen, asignar roles reales, por ejemplo Resources, Supervision,
  Project administration, Funding acquisition, Writing-review and editing,
  Validation, segun corresponda.

### 2. Data Availability posiblemente falsa o excesiva

Problema: el paper afirma que codigo, scripts y raw experimental logs estan
publicamente disponibles en GitHub. En el repo local los logs brutos estan en
`sessions/`, pero esa carpeta no parece formar parte del paquete publico principal
si se usa el flujo de exportacion; los resultados resumidos si estan en
`experiments/`.

Evidencia:

- `paper/main.tex:1321` afirma disponibilidad publica de raw experimental logs.
- Datos brutos locales: `sessions/session1.jsonl`,
  `sessions/session1_k8s.jsonl`, `sessions/composite_latency_docker.json`,
  `sessions/resilience_cam1.json`, etc.
- `tools/export_public.sh` no incluye claramente `sessions/`.
- MDPI recomienda hacer disponibles materiales, datos, protocolos y codigo;
  para codigo novel pide repositorio publico o suplemento.

Mejor solucion:

- Opcion preferida: publicar un dataset pequeno y limpio en GitHub o Zenodo:
  `experiments/results/raw/` con JSON/JSONL/CSV, README de medicion y hashes.
- Actualizar `\dataavailability{}` con URL exacta y, si existe, DOI de Zenodo.
- Si no se publican logs brutos, cambiar la frase a: codigo y scripts publicos;
  raw data available on request. Menos fuerte, pero verdadero.

### 3. Abstract demasiado largo para la guia oficial de MDPI

Problema: el abstract tiene 239 palabras. La guia interna aceptaba 200-250, pero
MDPI Electronics dice "about 200 words maximum".

Evidencia:

- Auditor: 239 palabras.
- `paper/main.tex:45`.
- MDPI Instructions: abstract de unas 200 palabras maximo, una sola parrafo,
  sin exagerar resultados.

Mejor solucion:

- Reducir a 190-205 palabras.
- Mantener solo una metrica de CPU, una de latencia y una frase de validacion
  CyberNEMO. Quitar redundancias de contexto comercial.

### 4. Capturas con personas identificables y posible copyright/consent

Problema: `figures/cybernemo_operator.png` muestra personas identificables y
contenido audiovisual de evento/senal. MDPI pide considerar copyright, etica y
permisos de figuras. Aunque no sea investigacion con sujetos humanos, publicar
imagenes identificables puede requerir permiso o sustitucion.

Evidencia:

- Figura inspeccionada: `paper/figures/cybernemo_operator.png`.
- `paper/main.tex:1028` la incluye.
- MDPI checklist exige considerar copyright, publication ethics y figure formats.

Mejor solucion:

- Obtener permiso escrito/consentimiento de publicacion y documentarlo.
- Si no se puede garantizar, sustituir por captura anonimizada: blur de caras,
  recorte que muestre GUI/overlay, o screenshot con fuentes sinteticas propias.
- Revisar tambien `cybernemo_output.png`.

### 5. Hay errores o imprecisiones factuales en la descripcion de voctogui

Problema: el paper dice que el panel izquierdo muestra cinco thumbnails: cam1-cam4
y mix output, recibidos por 14000-14005; y que el derecho muestra full-resolution
programme monitor. La arquitectura real distingue previews de fuentes 14000-14005,
preview de mix 12000 y program output 15000.

Evidencia:

- `paper/main.tex:563`.
- `voctocore/README.md` documenta 14000... como previews de fuentes y 12000 como
  Main Mixer Output preview.
- `voctogui/lib/videodisplay.py` suma 1000 al puerto cuando usa previews.
- `voctogui/lib/videopreviews.py` crea previews de fuentes con base 13000, que
  pasan a 14000 cuando previews estan activas.
- `k8s/studio.yaml` expone `mix-preview` en 12000, `preview-0..5` en 14000-14005
  y `program-out` en 15000.

Mejor solucion:

- Reescribir la frase asi:
  "The source preview column displays JPEG previews for the operator-selectable
  sources; source previews are served on ports 14000-14005 when preview encoding
  is enabled, while the mixer preview and programme output are exposed separately
  on ports 12000 and 15000, respectively."
- Ajustar "five" a la configuracion real de la captura o decir "source preview
  thumbnails" sin numero fijo.

### 6. "Six composite modes" no coincide con la interfaz de operador

Problema: el motor contiene composiciones internas y variantes, pero la GUI expone
cuatro modos principales: Full Screen, Side by Side, PIP y Lecture, mas mirror.
Decir "six composite modes" puede parecer contradictorio.

Evidencia:

- `paper/main.tex:466` y `paper/main.tex:1004`.
- `voctogui/default-config.ini` expone `fs`, `sbs`, `pip`, `lec` en
  `[toolbar.composites]` y `mirror` en `[toolbar.mods]`.
- `voctocore/default-config.ini` contiene composiciones internas adicionales
  (`fs-b`, `lec_43`, transiciones, variantes mirror).

Mejor solucion:

- Hablar de "four operator-facing composite modes plus mirror and internal
  transition variants".
- En la tabla funcional cambiar "Composite mode changes (6 modes)" por
  "Composite mode changes (4 primary modes + mirror variants)".

### 7. Figura RabbitMQ: caption/interpretacion debe ser exacta

Problema: la captura `rabbitmq_queues.png` muestra colas CyberNEMO
`vcompressor-uc-media`, `vproduction-uc-media` y `vqprobe-uc-media`, no colas
llamadas `CHANGE` y `STATE`. En el sistema, `CHANGE` y `STATE` son tipos de evento.

Evidencia:

- Imagen inspeccionada: `paper/figures/rabbitmq_queues.png`.
- Codigo: `example-scripts/ffmpeg/telemetry_service.py` publica eventos con
  tipos `CHANGE` y `STATE` a exchange `voctomix_events`.
- Memoria TFG: CyberNEMO recibia eventos en `vproduction-uc-media` y
  `vqprobe-uc-media`.

Mejor solucion:

- Caption recomendado: "RabbitMQ management interface during the CyberNEMO
  integration, showing downstream consumer queues receiving Voctomix telemetry
  events."
- En texto, aclarar: `CHANGE` y `STATE` son tipos de mensaje JSON, no nombres
  de cola.

### 8. Overfull hbox grandes: riesgo visual/editorial

Problema: hay 14 overfull hbox, varios muy grandes. Aunque compile, el PDF puede
mostrar tablas/figuras que se salen del ancho.

Evidencia:

- `paper/main.log`: 14 overfull hbox.
- Grandes en lineas de tablas/diagramas: 596-606, 663, 931-937, 1013, etc.

Mejor solucion:

- Revisar visualmente el PDF en las paginas correspondientes.
- Reducir texto de tablas, usar `\small`, `tabularx` con columnas `X`, partir
  tablas anchas o mover detalles a suplemento.
- En la figura TikZ de arquitectura, reducir escala o convertir a PDF/vector
  preparado externamente.

## Mejoras importantes de calidad cientifica

### 9. Metodologia: falta tabla/README de scripts exactos usados para medir

Problema: el paper explica metodologia, pero no deja suficientemente claro que
programa produce cada metrica.

Evidencia local:

- `experiments/run_camera_experiment.sh`
- `experiments/run_k8s_experiment.sh`
- `experiments/analyze_cameras.py`
- `experiments/measure_latency.py`
- `experiments/rapl_scraper.py`
- `tools/analyze_stability.py`

Mejor solucion:

- Anadir una tabla en Methods o Supplementary Materials:
  metrica, script, entrada, n, warm-up descartado, salida.
- Publicar esa tabla tambien en `experiments/README.md`.

### 10. K8s latency y composite-transition latency necesitan mas evidencia visible

Problema: la figura de latencia solo muestra Docker, pero el texto afirma Docker
y Kubernetes. Composite transition tiene valores 2.8 ms y 79.8 ms sin tabla/figura.

Evidencia:

- `paper/main.tex:949` figura Docker.
- `paper/main.tex:971` afirma ambos escenarios.
- `sessions/composite_latency_docker.json` y `sessions/composite_latency_kubernetes.json`
  existen localmente.

Mejor solucion:

- Anadir una tabla pequena: Docker/K8s, n, median, min, max, p95 para source
  switching y composite transition.
- Mantener la figura Docker si no hay espacio, pero la tabla debe soportar todas
  las afirmaciones.

### 11. Power/RAPL necesita explicar tratamiento de outliers

Problema: la tabla presenta Kubernetes 25-27 W. En las notas experimentales del
TFG hubo outlier alrededor de 36.1 W. Si se excluyo, debe decirse.

Evidencia:

- `paper/main.tex:880`.
- `experiments/RESULTADOS_CAP5.md` y notas previas mencionan criterio de
  medianas/warm-up; revisar outlier K8s antes de publicar.

Mejor solucion:

- Usar median/IQR en vez de rango si hay outlier.
- O declarar: "one initialization outlier was excluded according to the warm-up
  rule described above".

### 12. Bibliografia correcta en numero, pero mejorable en peso academico

Problema: hay 36 entradas, numero aceptable, pero varias son webs/productos.
Para reducir riesgo de revisor duro, faltan 4-6 referencias academicas/estandares
directamente relacionadas con video-over-IP, cloud/media containerization,
low-latency live production, AMQP/telemetry o GStreamer performance.

Evidencia:

- Auditor: 36 entradas, 24 citadas.
- MDPI indica que el article debe incluir referencias recientes y relevantes.
- MDPI References pide URLs con fecha de acceso.

Mejor solucion:

- Mantener webs oficiales para productos.
- Anadir papers/estandares primarios donde las afirmaciones tecnicas dependan
  de ellos.
- Revisar `references.bib`: toda URL web con `urldate`/accessed date y DOI donde exista.

### 13. Comparacion con OBS/vMix/ATEM debe matizarse

Problema: la tabla comparativa es util, pero algunas celdas pueden ser demasiado
absolutas. OBS si tiene API/WebSocket y plugins; Blackmagic ATEM si permite SDK
y control por Ethernet; vMix tiene ediciones y scripting. Lo diferencial real de
Voctomix es la combinacion open-source + Linux headless + backend de mezcla
servidor + despliegue containerizado/K8s + AMQP.

Evidencia externa:

- OBS oficial: gratuito/open-source, multiplataforma, mezcla audio/video en tiempo
  real y WebSocket integrado desde OBS 28.
- vMix oficial: Basic HD 60 USD, HD 350 USD, 4K 700 USD, Pro 1200 USD, MAX
  50 USD/mes.
- Blackmagic oficial: ATEM Mini Pro 345 USD, Extreme 1225 USD, Extreme ISO G2
  2195 USD; Ethernet permite paneles y SDK.

Mejor solucion:

- Cambiar celdas "No" por "not native", "desktop-oriented", "limited/proprietary"
  cuando proceda.
- Citar fuentes oficiales y evitar tono de marketing contra competidores.

## Mejoras de forma y envio

### 14. Preparar cover letter

Problema: no he encontrado carta de presentacion. MDPI la exige.

Mejor solucion:

- Crear `paper/cover_letter.md` o `.tex` con:
  1. por que encaja en Electronics;
  2. contribuciones principales;
  3. confirmacion de originalidad/no envio simultaneo;
  4. aprobacion de todos los autores.

### 15. ORCID placeholders

Problema: hay ORCID placeholders comentados. No rompen el paper, pero son ruido
y pueden olvidarse.

Mejor solucion:

- Rellenar ORCID reales o eliminar el bloque comentado antes de enviar.

### 16. Funding/APC

Problema: funding menciona CyberNEMO, pero no indica si el APC esta financiado.
MDPI pide declarar funding de APC si aplica.

Mejor solucion:

- Confirmar con el tutor.
- Si aplica: "The APC was funded by ...".
- Si no: "The APC was not externally funded" o formula que indique el estado real.

### 17. Conflicts of Interest y rol del financiador

Problema: "The authors declare no conflicts of interest" es formalmente valido,
pero con un proyecto financiado conviene declarar el rol/no rol del financiador.

Mejor solucion:

- Anadir frase: "The funders had no role in the design of the study; in the
  collection, analyses, or interpretation of data; in the writing of the
  manuscript; or in the decision to publish the results." Solo si es verdad.

### 18. Figuras: resolucion y texto

Problema: MDPI prefiere figuras de al menos 600 dpi en PNG/JPEG/TIFF, texto en
ingles, caracteres no enmascarados. Hay PNG de capturas; deben verificarse.

Mejor solucion:

- Comprobar resolucion y legibilidad al 100%.
- Exportar diagramas como PDF/vector o PNG 600 dpi.
- En capturas, evitar textos diminutos si son parte de evidencia.

## Orden recomendado de trabajo

1. Confirmar authorship/contribuciones/ORCID/APC/consentimientos con el tutor.
2. Corregir factualidad: voctogui ports/previews, composite modes, RabbitMQ caption.
3. Publicar o preparar raw data/supplementary dataset y arreglar Data Availability.
4. Reducir abstract a unas 200 palabras.
5. Anadir tabla metodologica de scripts y tabla compacta de latencias.
6. Arreglar overfull hbox y revisar PDF visualmente.
7. Matizar tabla comparativa OBS/vMix/ATEM con fuentes oficiales.
8. Preparar cover letter y ZIP LaTeX final.
9. Ejecutar `bash docs/paper-workbench/check_paper.sh` y
   `python3 docs/paper-workbench/audit_paper.py`.

## Fuentes externas consultadas

- MDPI Electronics Instructions for Authors:
  https://www.mdpi.com/journal/electronics/instructions
- MDPI Electronics Aims & Scope:
  https://www.mdpi.com/journal/electronics/about
- MDPI Author Layout Style:
  https://www.mdpi.com/authors/layout
- MDPI Reference List and Citations:
  https://www.mdpi.com/authors/references
- OBS official site:
  https://obsproject.com/
- OBS Remote Control Guide:
  https://obsproject.com/kb/remote-control-guide
- vMix official purchase/comparison:
  https://www.vmix.com/purchase/
- Blackmagic ATEM Mini official product page:
  https://www.blackmagicdesign.com/products/atemmini
- Appear/LaLiga remote production reference:
  https://www.appear.net/blog/2025/08/27/laliga-distribution-network/

