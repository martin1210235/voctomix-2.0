# MDPI Electronics Submission Precheck

Guia viva para someter el paper Voctomix 2.0 a una revision previa dura antes
del envio a MDPI/Electronics. Generado el 2026-07-09 a partir de las paginas
oficiales de MDPI/Electronics y de herramientas externas de pre-check.

## 1. Fuentes oficiales que mandan

Consultar siempre estas paginas antes de enviar, porque las normas editoriales
pueden cambiar:

| Fuente | Uso |
|---|---|
| https://www.mdpi.com/journal/electronics/instructions | Instrucciones oficiales para autores de Electronics. |
| https://www.mdpi.com/journal/electronics/about | Alcance de la revista; sirve para defender el venue fit. |
| https://www.mdpi.com/authors | Portal general de autores MDPI. |
| https://www.mdpi.com/authors/latex | Plantillas LaTeX y normas practicas para preparar el manuscrito. |
| https://www.mdpi.com/authors/english | Servicios MDPI de edicion en ingles; no sustituyen peer review. |
| https://www.mdpi.com/ethics | Politicas editoriales y eticas de MDPI. |

Regla interna: si hay conflicto entre este fichero y una pagina oficial de MDPI,
gana MDPI.

## 2. Servicios externos donde subirlo para revision previa

Ninguno garantiza aceptacion. Sirven para encontrar problemas antes del envio.

| Servicio | Que puede detectar | Utilidad para nuestro paper | Riesgo / limite |
|---|---|---|---|
| Paperpal Preflight, https://paperpal.com/preflight | Checks de readiness, idioma, estructura, referencias y posibles incumplimientos de journal. | Buena primera pasada automatica sobre PDF/DOCX si acepta el formato exportado. | No valida que las cifras sean reales ni que el codigo respalde el texto. |
| MDPI English Editing, https://www.mdpi.com/authors/english | Edicion linguistica y claridad del ingles. | Util si queremos reducir riesgo por redaccion no nativa. | Es servicio linguistico; no es revision tecnica ni garantia editorial. |
| AJE, https://www.aje.com | Edicion cientifica, formato, cover letter, revision de lenguaje. | Segunda opinion de lenguaje/formato. | Coste; no sustituye reglas especificas de Electronics. |
| Editage, https://www.editage.com | Edicion, formatting, presubmission review. | Puede revisar si el texto es publicable y si la historia esta clara. | Recomendaciones genericas; comprobar todo contra MDPI. |
| Enago, https://www.enago.com | Edicion, pre-submission peer review y journal support. | La opcion mas parecida a "que lo lea un revisor externo". | Puede ser caro; hay que pedir revision tecnica, no solo copyediting. |
| Writefull for Overleaf, https://www.writefull.com/overleaf | Correccion linguistica integrada con LaTeX/Overleaf. | Buen ultimo pase de ingles academico sin salir de Overleaf. | No revisa reproducibilidad ni exactitud tecnica. |
| iThenticate / Turnitin institucional | Similitud textual y posible solapamiento. | Recomendable antes de envio si UPM da acceso. | No es una herramienta de calidad; solo similitud. |
| chktex / lacheck / latexmk local | Problemas LaTeX, warnings, referencias. | Automatizable en el repo. | No conoce normas MDPI ni calidad cientifica. |

Recomendacion practica obligatoria antes de enviar: hacer, en este orden,
(1) auditoria local estricta, (2) Paperpal Preflight o equivalente,
(3) Writefull/MDPI English Editing si el ingles preocupa, (4) Enago/AJE/Editage
solo si se quiere pagar una lectura humana externa, y (5) similitud con
iThenticate/Turnitin si la universidad lo permite.

### 2.1 Que evalua cada tipo de prueba

| Tipo de prueba | Que evalua | Dureza esperable | Que NO evalua |
|---|---|---|---|
| Auditoria local del repo | Compilacion, citas definidas, referencias, paginas, URLs, valores descartados, back matter, trazas obvias de TODO/placeholders. | Alta para errores mecanicos; implacable si se automatiza con fallo. | Calidad cientifica, originalidad, ingles fino o criterio editorial. |
| Paperpal Preflight | Readiness editorial: estructura, lenguaje, formato, posibles problemas de journal, referencias y metadatos. | Media-alta como filtro automatico; detecta muchos problemas de presentacion. | No verifica datos crudos, codigo, ni si las afirmaciones son verdaderas. |
| Writefull / MDPI English Editing | Ingles academico, gramatica, estilo, claridad, frases largas, terminologia. | Media para idioma; muy util para evitar rechazo por redaccion pobre. | No decide si la contribucion es suficiente ni si las metricas son correctas. |
| Enago / AJE / Editage presubmission review | Lectura humana de estructura, novedad percibida, claridad, journal fit, debilidades antes de revision. | Alta si se contrata revision tecnica; puede parecerse a una pre-revision. | No garantiza aceptacion y puede no conocer el codigo ni el TFG. |
| iThenticate / Turnitin | Similitud textual, solapamiento con fuentes previas, riesgo de autoplagio o copia excesiva. | Alta para similitud; muy usado por editoriales. | No mide calidad ni validez cientifica. |
| Revision del tutor/coautores | Coherencia tecnica, overclaim, contribucion real, encaje con TFG y proyecto. | La mas importante para contenido cientifico. | Puede no detectar todos los fallos formales pequenos. |

## 3. Checklist MDPI/Electronics para Voctomix 2.0

### 3.1 Alcance y tipo de articulo

- El manuscrito debe encajar claramente en Electronics: sistemas electronicos,
  procesamiento de senal/video, comunicaciones, infraestructura software para
  flujos multimedia, sistemas embebidos o redes.
- El titulo, abstract, keywords e introduccion deben dejar claro que no es solo
  una herramienta software, sino un sistema reproducible de produccion de video
  en tiempo real con validacion experimental.
- Evitar overclaim: "broadcast-quality" solo si se define tecnicamente; si no,
  preferir "core live-production workflows".

### 3.2 Estructura obligatoria y front matter

- Titulo conciso y especifico.
- Autores, afiliaciones y autor de correspondencia correctos.
- ORCID reales si se incluyen. No dejar placeholders ni comentarios de ORCID.
- Abstract autonomo, sin citas, sin abreviaturas no definidas y con metricas
  principales. Objetivo interno: 180-220 palabras.
- 3-10 keywords, no repetir solo palabras del titulo.
- Estructura IMRaD o equivalente:
  Introduction, Background/Related Work, System Architecture/Methods,
  Deployment Scenarios, Results, Discussion, Conclusions.

### 3.3 Back matter MDPI

Comprobar que existen y dicen algo coherente:

- Author Contributions, idealmente alineado con CRediT.
- Funding.
- Institutional Review Board Statement.
- Informed Consent Statement.
- Data Availability Statement.
- Acknowledgments.
- Conflicts of Interest.
- Abbreviations, si se usa la seccion.

Para este paper, el punto mas sensible es Data Availability: no debe prometer
"raw experimental logs publicly available" si esos logs no estan realmente
subidos en el repositorio publico. La version actual mas prudente es indicar
codigo/deployment publico y logs disponibles bajo peticion razonable, salvo que
se publiquen los logs antes del envio.

### 3.4 Figuras y tablas

- Toda figura debe citarse en el texto antes de aparecer.
- Cada caption debe ser autonomo y explicar que se ve.
- Ejes con unidades en todas las graficas.
- No incluir capturas de la memoria del TFG si contienen texto en espanol,
  datos personales o logos no explicados, salvo que se redibujen o recorten.
- Las figuras de resultados no pueden venir de pruebas distintas a las descritas
  en Results.
- Mantener el paper en 20 paginas si es posible; si sube a 21, justificarlo
  con una mejora fuerte de reproducibilidad o evidencia.

### 3.5 Referencias y citas

- Toda afirmacion tecnica externa debe tener cita.
- Priorizar normas, documentacion primaria y papers revisados por pares:
  GStreamer, Docker, Kubernetes, RabbitMQ, ITU-R BT.1359-1, SRT, container
  overhead, remote/live production.
- No citar paginas comerciales para afirmaciones cientificas si existe una
  fuente academica o estandar.
- Cada entrada de `references.bib` debe estar citada o eliminarse.
- Comprobar URLs y DOI antes de envio.

### 3.6 Reproducibilidad

Minimo que debe quedar claro en el paper:

- Hardware exacto.
- Sistema operativo y kernel.
- Versiones de Docker, Compose, Minikube, kubectl, GStreamer y Python.
- Numero de fuentes, resolucion, fps, formato I420, tipo de fuente FFmpeg.
- Que escenarios fueron medidos y cuales solo validados funcionalmente.
- Numero de repeticiones por metrica.
- Metodo de calculo: mediana, p95, maximo, warm-up descartado.
- Script o fuente de datos usada para cada metrica.
- Repositorio publico real y accesible.

### 3.7 Consistencia tecnica especifica de Voctomix 2.0

Estos puntos son bloqueantes si fallan:

- I420 4:2:0, no UYVY.
- 622 Mbps por camara 1080p25 I420.
- 2.49 Gbps para 4 fuentes.
- CPU/RAM Docker y Kubernetes coinciden con `DATA_CONSISTENCY.md`.
- Latencia de conmutacion: n=30, Docker median 1.5 ms, K8s median 1.8 ms, todas
  por debajo de 5 ms.
- Latencia de transicion: Docker 2.8 ms; K8s alrededor de 78.9/79.8 ms segun la
  fuente canonica final. No dejar dos valores distintos.
- Estabilidad: 31 minutos, sin fuga de CPU/RAM; no usar graficas de 68 minutos
  si el paper afirma 31 minutos.
- Resiliencia: recuperacion cam1 aproximadamente 520 ms en Docker; K8s solo si
  esta respaldado por datos.
- Single-PC y Two-PC son validacion funcional, no resultados instrumentados.
- `network_mode: service:voctocore` descrito exactamente como en Docker Compose.
- Puertos de control, preview, mixer y programa verificados contra codigo/config.

### 3.8 Idioma y estilo

- Ingles academico sobrio.
- Presente para describir el sistema; pasado para experimentos.
- No vender como producto comercial.
- No usar "zero cost" sin matizar: mejor "zero software licence cost".
- No usar "real-time" de forma vaga: vincularlo a 25 fps, 40 ms por frame,
  latencias medidas y ausencia de encoding en el camino medido.

## 4. Pruebas locales que debemos correr antes de enviar

Desde la raiz del repo:

```bash
bash docs/paper-workbench/check_paper.sh
python3 docs/paper-workbench/audit_paper.py
python3 docs/paper-workbench/audit_paper.py --check-urls
git -C paper diff --check
pdfinfo paper/main.pdf
rg -n "TODO|FIXME|XXX|PENDIENTE|CAMBIAR|placeholder|0000-0000|000X" paper/main.tex paper/references.bib
rg -n "829|3\\.32|22~ms|i7-8750|UYVY|WiFi|802\\.11" paper/main.tex
```

Estado de automatizacion:

- Verificar que todas las URLs de `main.tex` y `references.bib` responden:
  implementado en `audit_paper.py --check-urls`.
- Verificar que toda entrada BibTeX citada tiene DOI/URL cuando proceda:
  implementado como aviso en `audit_paper.py`.
- Fallar si `pdfinfo` informa mas de 20 paginas:
  implementado en `audit_paper.py`.
- Fallar si `dataavailability` no contiene una URL:
  implementado en `audit_paper.py`.

Pruebas recomendadas pendientes:

- Extraer todas las cifras del paper y compararlas contra `DATA_CONSISTENCY.md`
  de forma semiautomatica.
- Convertir el check de URL publica de Data Availability en fallo especifico
  cuando `--check-urls` este disponible.

## 5. Mapa de ficheros actuales del paper/workbench

| Fichero | Funcion |
|---|---|
| `paper/main.tex` | Manuscrito real sincronizado con Overleaf. |
| `paper/references.bib` | Bibliografia BibTeX del manuscrito. |
| `paper/cover_letter.md` | Borrador de cover letter para el envio. |
| `paper/figures/` | Figuras incluidas en el manuscrito. |
| `docs/paper-workbench/README.md` | Indice del workbench y flujo de uso. |
| `docs/paper-workbench/PAPER_STATUS.md` | Panel de control: bloqueos, estado, pendientes. |
| `docs/paper-workbench/DATA_CONSISTENCY.md` | Fuente canonica de cifras paper/TFG/datos crudos. |
| `docs/paper-workbench/PAPER_REVIEW_CHECKLIST.md` | Checklist interno de revision cientifica estricta. |
| `docs/paper-workbench/PAPER_PATTERNS.md` | Patrones observados en papers comparables. |
| `docs/paper-workbench/RELATED_WORK_NOTES.md` | Notas de bibliografia y venue fit. |
| `docs/paper-workbench/PAPER_FINAL_AUDIT_2026-07-08.md` | Auditoria final previa existente. |
| `docs/paper-workbench/PAPER_POST_CHANGES_REVIEW_2026-07-08.md` | Revision posterior a cambios recientes. |
| `docs/paper-workbench/MDPI_SUBMISSION_PRECHECK.md` | Este fichero: reglas externas y preflight. |
| `docs/paper-workbench/check_paper.sh` | Script automatizado y hook pre-commit del repo `paper/`. |
| `docs/paper-workbench/audit_paper.py` | Auditoria metrica local: abstract, figuras, tablas, back matter, overfulls, URLs. |

## 6. Decision recomendada antes de pulsar Submit

No enviar hasta que se cumpla todo esto:

- `check_paper.sh` pasa.
- `audit_paper.py` revisado manualmente y sin senales graves.
- PDF en 20 paginas o decision explicita de aceptar 21.
- Repo publico accesible desde una ventana anonima.
- ORCID resueltos o eliminados limpiamente si no se van a usar.
- Data Availability coherente con lo que realmente esta publicado.
- Una herramienta externa tipo Paperpal Preflight no marca problemas graves.
- Al menos una revision humana externa o del tutor centrada en overclaim,
  reproducibilidad y venue fit.
