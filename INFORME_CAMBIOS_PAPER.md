# Informe de cambios del paper — respuesta a los revisores

**Artículo:** *Beyond Hardware Mixers: A Resilient Cloud-Native Architecture for Real-Time Remote Video Production*
**Revista:** MDPI Electronics · **Fecha del informe:** 1 de septiembre de 2026
**Versión del manuscrito:** Overleaf, commit `2a9136e`

Este documento recoge, uno por uno, los cambios realizados en el manuscrito para responder a los dos
revisores. De cada cambio se indica la línea del fichero, el comentario del revisor que lo motiva, una
explicación breve, y el texto literal antes y después.

---

## 1. Situación general

Ninguno de los dos revisores rechaza el trabajo.

| Revisor | Tipo de revisión | Comentarios | Resueltos | Pendientes |
|---------|------------------|-------------|-----------|------------|
| Revisor 1 | Menor | 8 | 8 | 0 |
| Revisor 2 | Mayor | 10 | 7 | 3 |

**Estado del texto:** los 16 cambios de redacción están aplicados y verificados.
**Estado global:** quedan tres frentes abiertos, detallados en la sección 4.

---

## 2. Resumen por comentario

### Revisor 1 (revisión menor)

| Ref. | Qué pedía | Estado |
|------|-----------|--------|
| R1.1 | Limitar la afirmación de "sin sobrecarga" al entorno de un solo nodo | Resuelto |
| R1.2 | Usar bien los términos estadísticos y aportar medidas de variabilidad | Resuelto |
| R1.3 | Aclarar que los 293 ms son latencia interna del mezclador, no total | Resuelto |
| R1.4 | Describir mejor el experimento de fallo inducido | Resuelto |
| R1.5 | Interpretar con cautela la comparación con OBS Studio | Resuelto |
| R1.6 | Moderar las afirmaciones sobre escalabilidad horizontal | Resuelto |
| R1.7 | Discutir autenticación, cifrado y control de acceso | Resuelto |
| R1.8 | Revisión de idioma | Resuelto |

### Revisor 2 (revisión mayor)

| Ref. | Qué pedía | Estado |
|------|-----------|--------|
| R2.1 | Métricas de integridad de salida (pérdida de fotogramas y fps) | Medido, falta incorporarlo al texto |
| R2.2 | Renombrar, indicar el commit de origen y añadir tabla comparativa | Parcial, ver sección 4 |
| R2.3 | Aclarar que la telemetría depende de la interfaz gráfica | Resuelto |
| R2.4 | Corregir la comparación con OBS Studio | Resuelto |
| R2.5 | Conectar el trabajo con el modo en que el público consume el vídeo | Resuelto |
| R2.6 | Explicar el comportamiento no monótono del tiempo de recuperación | Resuelto |
| R2.7 | Reconocer el riesgo de los subtítulos automáticos | Resuelto |
| R2.8 | Armonizar medias y medianas, y explicar el consumo de memoria | Resuelto |
| R2.9 | Identificador permanente, licencia, datos y consentimiento de figura | Parcial, ver sección 4 |
| R2.10 | Añadir la referencia sugerida | Resuelto |

---

## 3. Cambios aplicados al manuscrito

### 3.1 · Resumen (abstract) — línea 48

**Comentarios:** R1.1, R1.2, R1.3, R2.8
**Motivo:** el resumen afirmaba que no hay sobrecarga alguna, cuando solo se ha probado un ordenador.
Además usaba la palabra "media" mientras el cuerpo del artículo usa "mediana", y no aclaraba que la
latencia medida es interna del mezclador.

**Antes:**
> Results under a continuous four-source 1080p25 workload demonstrated that containerization and orchestration do not impose any noticeable processing overhead, maintaining an average host-level CPU utilization near 90\% and stable RAM consumption of around 13 GB on standard hardware. Average command-to-output latency was 293 ms.

**Después:**
> Results under a continuous four-source 1080p25 workload showed that, in a single-node deployment, containerization and orchestration impose no appreciable processing overhead, with a median host-level CPU utilization near 90\% and a stable RAM working set of around 13 GB on standard hardware. The median command-to-output latency within the mixer was 293 ms, an internal switching latency that does not include camera capture or wide-area transport.

---

### 3.2 · Introducción, comparación con el proyecto original — línea 63

**Comentario:** R2.2
**Motivo:** el texto atribuía al proyecto original carencias que no tiene. El revisor señaló que el
motor de composición y transiciones ya existía en la versión actual del proyecto de origen.

**Antes:**
> Although pioneering open-source solutions such as the original Voctomix 1.0 successfully introduced a client-server architecture for operation with a remote graphical interface, they critically lacked the robust synchronization, dynamic compositing, and advanced graphic overlay capabilities required by continuous professional workflows.

**Después:**
> Although pioneering open-source solutions such as Voctomix introduced a client-server architecture with a remote graphical interface and a configurable compositing and transition engine, they were conceived for event recording rather than continuous, cloud-orchestrated production: they lacked an automated production layer (audio-follows-video, stream blanking, dynamic lower-thirds with automatic deactivation), a decoupled machine-readable telemetry channel, and reproducible container-orchestration manifests. This work builds directly on that upstream engine and contributes precisely that missing layer, as detailed in Table 2.

---

### 3.3 · Introducción, cómo llega el vídeo al público — línea 65

**Comentario:** R2.5
**Motivo:** el artículo justifica el trabajo hablando de campus universitarios y educación a distancia,
pero no explicaba cómo recibe el público el resultado. El revisor pidió cerrar ese argumento.

**Antes:** (no existía)

**Después (añadido al final del párrafo):**
> Delivery is deliberately kept outside the mixing core: the programme output is handed to standard distribution paths, such as an SRT or RTMP egress to a campus streaming server or a public platform, so audiences watch through the clients they already use, with no dedicated hardware on the receiving side. The cost argument is therefore one of accessibility, bringing professional-grade live production within reach of institutions currently priced out of it.

---

### 3.4 · Tercera contribución — línea 74

**Comentario:** R2.1
**Motivo:** se afirmaba que los ficheros de despliegue "optimizan" el tráfico interno, pero esa mejora
nunca se midió. El propio artículo reconoce en otra sección que no se hizo esa comparación.

**Antes:**
> Standardized Deployment Topology: The design of deployment manifests using Docker Compose and Kubernetes to eliminate configuration overhead and optimize internal routing of uncompressed bandwidth within cloud clusters.

**Después:**
> Standardized Deployment Topology: The design of Docker Compose and Kubernetes manifests that eliminate manual configuration overhead and confine uncompressed internal traffic to a shared network namespace, so that raw video does not traverse a physical network interface between the ingest and mixing processes.

---

### 3.5 · Tabla nueva: qué aporta este trabajo frente al proyecto original — línea 117

**Comentario:** R2.2
**Motivo:** el revisor pidió expresamente una tabla que distinga lo que ya ofrecía el proyecto de
origen de lo que aporta este trabajo, para poder valorar la novedad real.

**Antes:** (no existía)

**Después:** se añade la Tabla 2, con diez filas que separan lo heredado de lo aportado (división
cliente-servidor, motor de composición y protocolo de control como heredados; telemetría, overlays,
despliegues Docker y Kubernetes y la evaluación empírica como aportaciones propias).

> **Nota:** esta tabla necesita una corrección, explicada en la sección 4.2.

---

### 3.6 · Tabla 1, licencia — línea 160

**Comentario:** R2.9
**Motivo:** el revisor pidió declarar la licencia con precisión. Al comprobar el fichero de licencia
del repositorio, se confirma que es MIT, sin ninguna parte GPL.

**Antes:** `Open-source | Yes (MIT/GPL) | Yes (GPL) | No | No`
**Después:** `Open-source | Yes (MIT) | Yes (GPL) | No | No`

---

### 3.7 · Tabla 1, comparación con OBS Studio — líneas 162, 165, 166, 170 y 172

**Comentario:** R2.4
**Motivo:** el revisor señaló que OBS Studio sí admite varios clientes simultáneos y sí emite eventos
de estado a través de su complemento, así que marcarlo como "No" era incorrecto. También pidió definir
qué significa la categoría "Parcial" y justificar la versión de OBS utilizada.

**Antes:**
> Multi-operator | Yes | No | No | No
> Advanced telemetry | Yes | No | No | No

**Después:**
> Multi-operator | Yes | Partial | No | No
> Advanced telemetry | Yes | Partial (WS events) | No | No

**Además se añade una nota al pie definiendo la categoría:**
> Partial indicates a capability achievable only through unofficial or community-maintained configurations, rather than through an integrated, vendor-supported deployment path.

**Y una frase explicativa tras la tabla:**
> OBS Studio's obs-websocket plugin supports concurrent clients and state events, but not a decoupled telemetry stream or native multi-operator mixing, hence Partial.

---

### 3.8 · Telemetría y dependencia de la interfaz gráfica — línea 250

**Comentario:** R2.3
**Motivo:** este es uno de los comentarios más finos del revisor. El artículo afirmaba que el sistema
es "totalmente observable" sin interfaz, pero la telemetría se obtiene leyendo la interfaz gráfica. Se
comprobó en el código y el revisor tiene razón. Se corrige reconociendo la limitación con claridad.

**Antes:**
> This machine-readable stream makes the headless pipeline fully observable: it records what was on air at any given moment, keeps operators working in sync, and provides a non-intrusive foundation for auditing, session logging, and the dashboards described as future work.

**Después:**
> This machine-readable stream records what was on air at any given moment, keeps operators working in sync, and provides a non-intrusive foundation for auditing, session logging, and the dashboards described as future work. In the current implementation the state exporter runs embedded inside voctogui (Figure 1), so a graphical client instance must be connected to voctocore for telemetry to be produced; a fully unattended, GUI-less deployment does not currently emit telemetry. A native voctocore-side exporter that removes this dependency on the graphical client is left as future work. Note that the CPU and RAM figures reported in Section 4 are sampled directly from the host /proc interfaces on the mixing machine, independently of this telemetry path.

> **Importante:** los resultados de consumo de CPU y memoria del artículo **no** proceden de esa
> telemetría, sino de las interfaces del sistema operativo. Por tanto, los datos publicados siguen
> siendo válidos. Se ha añadido esa aclaración expresamente.

---

### 3.9 · Definición de la latencia medida — línea 309

**Comentario:** R1.3
**Motivo:** el texto decía "medida de extremo a extremo", lo que puede entenderse como la latencia
total del sistema (cámara, red y pantalla del espectador). En realidad es la latencia interna del
mezclador.

**Antes:**
> Switching and Transition Latency: Latency was measured end-to-end in the mixed video output, detecting the frame in which the switch becomes visible in the programme signal, rather than at the control protocol layer.

**Después:**
> Switching and Transition Latency: Latency was measured on the mixed video output itself, detecting the frame in which the switch becomes visible in the programme signal, rather than at the control-protocol layer. This is an internal command-to-output latency of the mixer and does not include camera capture or wide-area network transport, so it is not an end-to-end REMI figure.

---

### 3.10 · Descripción del experimento de fallo — línea 311

**Comentario:** R1.4
**Motivo:** el revisor pidió detallar qué proceso se interrumpía, cómo se detectaba el fallo y cómo se
comprobaba que la emisión seguía en directo.

**Antes:**
> Failover Resilience: An active camera was abruptly terminated and the Mean Time To Repair (MTTR) was measured on the programme output, divided into a detection phase, the time until the blocked source is detected; and a recovery phase, the time until the live signal is restored. Each failure was injected 100 times per configuration.

**Después:**
> Failover Resilience: The FFmpeg ingest process of the active camera was terminated with a SIGKILL (kill -9), rotating across all four sources, to simulate an ungraceful dropout. The Mean Time To Repair (MTTR) was measured on the programme output as a detection phase, until the missing source is signalled at its input pad, followed by a recovery phase, until a live signal from the restarted source is restored. Output continuity during this window was maintained by the stream blanker. Each failure was injected 100 times per configuration.

---

### 3.11 · Consumo de CPU, variabilidad y anomalía de Kubernetes — línea 323

**Comentarios:** R1.2, R2.8 y R2.1
**Motivo:** dos cosas. Primera, el revisor pidió acompañar cada valor central con una medida de
variabilidad. Segunda, señaló que Kubernetes aparecía consumiendo *menos* procesador que la ejecución
nativa, algo que no es esperable al añadir una capa de orquestación. El texto anterior lo presentaba
como un resultado positivo.

**Antes:**
> With four simultaneously 1080p25 sources, the median CPU load reaches nearly 90\% in the local and Docker deployments, while Kubernetes deployments show slightly lower utilization. In all scenarios, the load approaches but does not exceed the capacity of the ten-core host. It is worth noting that the three deployments tiers remain very close to one another across all operating points, and the Kubernetes orchestration never imposes a CPU penalty greater than the native local baseline.

**Después:**
> With four simultaneous 1080p25 sources, the median CPU load reaches nearly 90\% in the local and Docker deployments (89.6\% [IQR 84.0--94.3\%] and 89.1\% [IQR 84.1--94.1\%], respectively), while Kubernetes deployments show slightly lower utilization (81.5\% [IQR 76.3--87.5\%]). In all scenarios, the load approaches but does not exceed the capacity of the ten-core host. The three deployment tiers remain very close to one another across all operating points. The Kubernetes median falls below the native baseline, which is not physically expected of an added orchestration layer; given that the interquartile ranges of the three tiers overlap and the host operates close to saturation at this point, this difference should be attributed to measurement variance rather than read as evidence that orchestration reduces computational load.

---

### 3.12 · Variabilidad de la latencia — línea 355

**Comentarios:** R1.2 y R2.8
**Motivo:** faltaban las medidas de dispersión. Al añadirlas se comprobó además que la afirmación de
comportamiento "prácticamente idéntico" entre los tres entornos no se sostenía, porque la ejecución
nativa está un 12 % por encima de las demás. Se sustituye por los datos reales.

**Antes:**
> At 1080p25, the median latency is approximately 300 ms with a low variance, demonstrating virtually identical behavior across the local, Docker, and Kubernetes deployments.

**Después:**
> At 1080p25, the median latency is close to 300 ms in all three environments, with tight dispersion in each: 293 ms (IQR 291--294 ms) in Docker, 293 ms (IQR 292--294 ms) in Kubernetes, and 330 ms (IQR 294--331 ms) in the local deployment.

---

### 3.13 · Tiempo de recuperación no monótono — línea 378

**Comentarios:** R1.4 y R2.6
**Motivo:** el revisor detectó algo que el artículo no explicaba: el tiempo de recuperación no crece
de forma ordenada con la resolución. Además pedía saber qué componente reinicia la cámara en cada
entorno. Se revisó el código: el fallo se detecta por un evento de fin de flujo, no por un temporizador,
y eso explica el comportamiento. También se corrigió el rango numérico tras recalcularlo con los datos
originales.

**Antes:**
> A clear structural trade-off can be observed between the different formats: higher resolutions are detected more quickly (going from approximately 790 ms at 1080p25 to tens of milliseconds at 4K in local and Docker environments), but require significantly longer recovery times (increasing from about 1000 ms to between 1500 and 1750 ms) due to the higher computational cost of filling larger frame buffers. For the 1080p25 baseline format, the total recovery time is approximately 1.8 s in both local and Docker deployments. The Kubernetes environment exhibits slower and more variable recovery times, a delay caused by the kubelet observation cycle before the Pod is restarted.

**Después:**
> A structural trade-off can be observed between the two phases: higher resolutions are detected far more quickly, going from approximately 790 ms at 1080p25 to tens of milliseconds at 4K in local and Docker environments, while recovery times are longest at the 4K profiles, reaching roughly 1500 to 1800 ms. For the 1080p25 baseline format, the total recovery time is approximately 1.8 s in both local and Docker deployments (1797 ms, IQR 1796--1797 ms, and 1794 ms, IQR 1757--1797 ms, respectively), while Kubernetes is both slower and more dispersed at this format (2078 ms, IQR 2037--2607 ms). The total MTTR is not monotonic in bitrate, which follows from the two-phase structure of the metric. Detection time decreases markedly as bitrate increases, since a source failure is signalled by an end-of-stream event on the GStreamer bus once the already-buffered data drains, rather than by a fixed wall-clock timeout, so higher-bitrate streams cross this threshold sooner. Recovery time does not follow the same trend: it stays comparable between 1080p25 and 1080p50, then rises substantially at the 4K profiles, where re-establishing the larger decoded buffer state is more costly. MTTR therefore falls at 1080p50, dominated by the drop in detection time, and rises again at 4K, dominated by the rise in recovery time. The component restarted differs per tier: Docker Compose restarts the container via its restart policy; Kubernetes restarts it through the kubelet's observation cycle, which also explains the greater variability seen in that environment; the native deployment has no orchestrator, so the equivalent restart (a supervisor relaunching the terminated ingest process, akin to a systemd Restart=always unit) was reproduced by the test harness for this benchmark rather than being a standing component of the deployment.

---

### 3.14 · Explicación del consumo de memoria — línea 414

**Comentario:** R2.8
**Motivo:** el revisor hizo un cálculo propio: un margen de latencia de unos 300 milisegundos equivale
a unos siete fotogramas y medio, lo cual no puede ocupar 13 GB de memoria. Pedía explicar esa
diferencia. Se responde con el cálculo hecho de forma explícita.

**Antes:** (no existía)

**Después (añadido tras la mención de los 13 GB):**
> The RAM footprint is not governed by the latency-critical buffer depth: at approximately 3.1 MB per uncompressed 1080p25 frame, even a generous few-frame buffer per source accounts for well under 1 GB in aggregate, two orders of magnitude below the observed 13 GB. The steady-state resident set is instead dominated by process- and pipeline-level overhead, including the per-source JPEG preview pipelines, the FFmpeg decode processes, and the baseline footprint of GStreamer, Python, and (in Docker) the container runtime. This working set is bounded rather than growing, as confirmed by the flat 24-hour memory profile.

---

### 3.15 · Limitación a un solo nodo — línea 414

**Comentarios:** R1.1 y R1.6
**Motivo:** solo se ha evaluado un ordenador, así que no se puede generalizar la conclusión ni hablar
de escalabilidad horizontal.

**Antes:**
> This finding is highly significant for the broadcasting industry, as it demonstrates that containerizing the mixing engine and integrating it into an orchestrator does not impose a noticeable processing overhead on the host.

**Después:**
> This finding is significant for the broadcasting industry, as it shows that, in this single-node deployment, containerizing the mixing engine and integrating it into an orchestrator does not impose a noticeable processing overhead on the host; multi-node scaling, where inter-node networking and scheduling come into play, is left for future validation.

---

### 3.16 · Coherencia con la limitación de la telemetría — línea 420

**Comentario:** R2.3
**Motivo:** tras corregir la sección de telemetría, quedaba en la discusión una frase que volvía a
presentar el sistema como "sin interfaz" y con telemetría a la vez, que es justo la contradicción que
el revisor señalaba.

**Antes:**
> By providing a workflow that is interface-less, natively containerized, and multi-operator, equipped with a machine-readable control API and asynchronous AMQP telemetry, ...

**Después:**
> By providing a workflow that is natively containerized and multi-operator, equipped with a machine-readable control API and asynchronous AMQP telemetry, ...

---

### 3.17 · Comparación con OBS Studio: retirada de la columna de procesador — líneas 426, 444 y 458

**Comentarios:** R1.5 y R2.4
**Motivo:** ambos revisores coinciden en que comparar el consumo de procesador es injusto, porque OBS
Studio compone con tarjeta gráfica y además comprime el vídeo, mientras que nuestro sistema compone
con procesador y no comprime. El revisor 2 ofrecía como solución válida retirar esa columna y
mantener solo la memoria, que es la comparación equitativa. Es lo que se ha hecho. También se ha
trasladado la justificación de la versión de OBS al lugar donde se describe la medición.

**Antes:** la tabla incluía cuatro columnas (procesador y memoria de cada sistema), con valores de
procesador de 89,6 % frente a 39,4 %.

**Después:** la tabla incluye únicamente las dos columnas de memoria. El texto explicativo pasa a ser:

> A direct CPU comparison between the two systems is not reported, because it would primarily reflect two architectural differences rather than a difference in implementation efficiency. First, OBS composites video on the GPU via OpenGL, whereas Voctomix's compositor executes entirely on the CPU by design... RAM usage is far less affected by these two factors and is therefore fairer to compare directly.

---

### 3.18 · Apartado de seguridad — línea 464

**Comentario:** R1.7
**Motivo:** el artículo no decía nada sobre seguridad, y el sistema expone servicios de control y
telemetría por red. El revisor pidió tratar autenticación, cifrado y control de acceso.

**Antes:** (no existía)

**Después:**
> The current implementation also assumes a trusted network: the TCP control channel, the telemetry HTTP endpoint, and the RabbitMQ broker carry no encryption or client authentication, so any host with network reachability could issue mixer commands or read state. Remote production therefore requires confining these services to a trusted segment, a VPN, or Kubernetes NetworkPolicies, and placing them behind a TLS reverse proxy with authenticated broker credentials. Native token-based authentication and TLS in the control protocol are left for future work.

---

### 3.19 · Conclusiones, definición de la latencia — línea 474

**Comentario:** R1.3
**Motivo:** misma aclaración que en la metodología, para que no quede ninguna lectura ambigua.

**Antes:**
> Responsiveness remained within professional tolerance limits, with a median latency between command and output of approximately 293 ms at 25 fps.

**Después:**
> Responsiveness remained within professional tolerance limits, with a median internal command-to-output latency of approximately 293 ms at 25 fps, a mixer-internal figure that excludes camera capture and network transport.

---

### 3.20 · Riesgo de los subtítulos automáticos — línea 488

**Comentarios:** R2.7 y R2.10
**Motivo:** el trabajo futuro proponía generar subtítulos automáticos sin supervisión humana. El
revisor advirtió que el riesgo real no es la velocidad sino que el sistema emita texto incorrecto con
apariencia de correcto, y propuso una redacción concreta y una referencia. Se ha aceptado su
sugerencia prácticamente literal.

**Antes:**
> AI-Based Transcription Overlays: The decoupled, event-driven architecture can be scaled by routing the isolated program audio to a separate automatic speech recognition engine. The resulting transcribed text could be fed back into the process as automated caption commands, enabling real-time captioning without manual intervention.

**Después:**
> AI-Based Transcription Overlays: The decoupled, event-driven architecture can be scaled by routing the isolated program audio to a separate automatic speech recognition engine, feeding the transcribed text back as automated caption commands. Because such captions would be inserted unattended, the operative risk is not recognition latency but fluent, confident and factually wrong text, the broadcast analogue of the plausible-but-incorrect outputs documented for probabilistic language models [ref]. Any such extension should therefore be paired with a confidence-gated insertion policy, so that the overlay module suppresses low-confidence segments rather than rendering them on air.

Se añade además la referencia propuesta por el revisor: Hamid, O. H. (2024), *Beyond Probabilities:
Unveiling the Delicate Dance of Large Language Models (LLMs) and AI-Hallucination*, IEEE CogSIMA.

---

### 3.21 · Disponibilidad de datos — línea 514

**Comentario:** R2.9
**Motivo:** el revisor observó que el código está en una cuenta personal sin identificador permanente,
y que los datos se ofrecían "bajo petición". Pidió depositar una versión etiquetada, declarar la
licencia y depositar los registros.

**Antes:**
> The source code and deployment manifests ... are publicly available in the project repository at [enlace]. The raw experimental logs used to compute the reported metrics are available from the corresponding author upon reasonable request.

**Después:**
> The source code and deployment manifests ... are publicly available in the project repository at [enlace], archived with a persistent identifier at Zenodo (DOI: [pendiente]) under the MIT license. The raw experimental logs used to compute the reported metrics are deposited in the same archive.

---

### 3.22 · Correcciones de idioma

**Comentario:** R1.8

| Antes | Después |
|-------|---------|
| compoud layout changes | compound layout changes |
| the three deployments tiers | the three deployment tiers |
| tight, highly and repeatable recovery distributions | tight and highly repeatable recovery distributions |
| With four simultaneously 1080p25 sources | With four simultaneous 1080p25 sources |

---

## 4. Qué queda pendiente

### 4.1 · Incorporar al texto la medición de integridad de salida (R2.1)

**Situación:** la medición ya está hecha. Se ejecutaron 36 pruebas cubriendo los tres entornos y los
cuatro formatos de vídeo. El resultado principal es que **no se pierde ningún fotograma en ninguna
combinación**, lo que responde directamente a la sospecha del revisor.

Ahora bien, la campaña incluyó una segunda comprobación que resultó decisiva: contar cuántos de esos
fotogramas son realmente distintos entre sí. Un mezclador sin datos suficientes puede repetir el
último fotograma y producir un recuento perfecto con la imagen congelada.

| Formato | Fotogramas distintos por segundo |
|---------|----------------------------------|
| 1080p25 | 25 de 25 |
| 1080p50 | 1,8 de 50 |
| 2160p25 | 1,2 de 25 |
| 2160p50 | 0,6 a 0,8 de 50 |

Los experimentos de aislamiento posteriores muestran que en 1080p50 y 2160p25 la limitación estaba en
la **simulación de las cámaras** (cuatro decodificaciones de vídeo 4K simultáneas en la misma máquina),
no en el mezclador: alimentando el sistema con fotogramas ya preparados, esos dos formatos funcionan
con fidelidad completa. Solo en 2160p50 el límite es real y corresponde a la capacidad del ordenador.

**Implicación:** conviene revisar cómo se presentan los resultados de los formatos superiores a
1080p25. Está pendiente una consulta al equipo de laboratorio para confirmar el alcance exacto y
valorar si conviene repetir esas medidas con la alimentación de datos más ligera.

**Aspecto favorable:** este hallazgo aporta una explicación física a la anomalía que había señalado el
revisor 2, según la cual Kubernetes parecía consumir menos procesador que la ejecución nativa. Cuando
el sistema repite fotogramas también deja de trabajar, y por eso el consumo baja.

### 4.2 · Ajustar la tabla comparativa y el origen del proyecto (R2.2)

Se ha determinado con precisión el punto de partida del código: rama `voctomix2`, revisión `558489d`,
de diciembre de 2018. El manuscrito debe indicarlo, que es exactamente lo que pedía el revisor.

Al comparar con esa base real, dos filas de la tabla comparativa atribuyen a este trabajo elementos
que ya existían:

| Elemento | Situación real |
|----------|----------------|
| Módulo de corte de emisión | Pertenece al proyecto original. Lo aportado es el control desde la interfaz del operador y su acoplamiento con el audio. |
| Sincronización automática de audio con el vídeo | El módulo de audio no se ha modificado. Lo aportado es el acoplamiento del audio al estado de corte de emisión. |

Se recomienda corregirlo antes de reenviar el manuscrito. El revisor 2 ya ha demostrado que consulta
el proyecto de origen, y una tabla presentada como gesto de transparencia debe ser exacta. Las demás
aportaciones (overlays, telemetría, despliegues Docker y Kubernetes, modificaciones del compositor y
la evaluación empírica) están correctamente atribuidas.

**Decisión pendiente:** el revisor pide además **renombrar** el sistema, porque el proyecto original
mantiene una rama que ya se llama `voctomix2`. Es la única petición literal de un revisor que de
momento no se está atendiendo. Conviene decidirlo en esta reunión, porque afecta al título, al
repositorio y al identificador permanente, y debe resolverse antes de generar este último.

### 4.3 · Gestiones de reproducibilidad (R2.9)

| Tarea | Estado |
|-------|--------|
| Publicar una versión etiquetada y obtener identificador permanente en Zenodo | Pendiente |
| Depositar los registros experimentales | Preparados, pendientes de subir |
| Sustituir fuentes divulgativas por fuentes académicas donde sostienen afirmaciones técnicas | Pendiente |
| Regenerar la Figura 3 sin personas identificables | Herramientas preparadas |

### 4.4 · Cierre

| Tarea | Estado |
|-------|--------|
| Revisión final de erratas y coherencia numérica | Pendiente, a realizar al final |
| Carta de respuesta a los revisores, punto por punto | Pendiente |

---

## 5. Verificaciones realizadas

Sobre la versión actual del manuscrito se han comprobado de forma automática:

- Los 16 cambios de redacción, mediante 30 comprobaciones de texto: todas correctas.
- La bibliografía: ninguna cita sin su entrada correspondiente.
- Las referencias cruzadas: ninguna referencia a figuras, tablas o secciones sin destino.
- La estructura del documento: llaves equilibradas y todos los entornos correctamente cerrados
  (6 tablas, 12 figuras).

Además, todas las afirmaciones técnicas nuevas se han verificado contra el código del proyecto y
contra los datos experimentales originales, y no únicamente contra la redacción previa del artículo.

---

## 6. La prueba de integridad de salida, explicada

### 6.1 · Por qué el revisor la pide

El artículo dice que el sistema funciona con el procesador cerca del 90 %, y presenta esa cifra como
señal de que la contenerización no penaliza el rendimiento. El revisor 2 objeta lo siguiente:

> *"sin recuentos de fotogramas descartados o tasa de fotogramas sostenida en la salida, una lectura
> de procesador más baja no puede distinguirse de una tubería que está descartando fotogramas en
> silencio."*

El argumento es sólido. Un consumo de procesador bajo puede significar dos cosas opuestas: que el
sistema es eficiente, o que el sistema no está haciendo el trabajo. Ambas producen la misma lectura.
Para distinguirlas hay que mirar **lo que sale por el otro extremo**, no solo lo que consume.

### 6.2 · Cómo se ha hecho la prueba

Se conecta un analizador a la salida del mezclador, se graba una ventana de 60 segundos y se cuentan
los fotogramas que realmente llegan. Se compara con los que deberían llegar: a 25 fotogramas por
segundo durante 60 segundos, deberían ser 1500.

Se repitió para las doce combinaciones posibles, tres entornos (nativo, Docker y Kubernetes) por
cuatro formatos de vídeo, con tres repeticiones cada una: 36 mediciones.

Dos decisiones técnicas relevantes:

- **La salida se mide en el puerto del mezclador, no en el de emisión final.** El de emisión pasa por
  el módulo de corte y aparece en negro salvo que esté explícitamente en directo, así que habría dado
  una medición sin sentido.
- **No se guarda el vídeo en disco.** A 4K son 622 MB por segundo, y un disco que no siguiera el ritmo
  frenaría al analizador. El mezclador descarta a los clientes lentos, así que la propia medición
  habría provocado la pérdida de fotogramas que pretendía detectar. Se cuentan al vuelo.

### 6.3 · El resultado, y por qué hizo falta una segunda comprobación

**Primera comprobación (cadencia):** no se pierde ni un fotograma. Las 36 mediciones dan exactamente
el número esperado, en todos los entornos y todos los formatos.

Ese resultado, por sí solo, habría permitido una afirmación muy favorable. Pero hay una trampa: **un
mezclador que no recibe datos suficientes no se para, sino que repite el último fotograma**. El
recuento sale perfecto mientras la imagen está congelada. Es decir, la primera comprobación puede dar
un aprobado a un sistema que en realidad ha dejado de funcionar.

**Segunda comprobación (contenido):** se cuenta cuántos de esos fotogramas son realmente distintos
entre sí.

| Formato | Fotogramas distintos por segundo |
|---------|----------------------------------|
| 1080p25 | 25 de 25, imagen fluida |
| 1080p50 | 1,8 de 50 |
| 2160p25 | 1,2 de 25 |
| 2160p50 | 0,6 a 0,8 de 50 |

Solo el formato base entrega vídeo realmente fluido. En los demás, la salida está repetida entre un
95 % y un 98 % del tiempo.

Este resultado se confirmó por un segundo método independiente, comparando las huellas digitales de
cada fotograma una a una: de 250 fotogramas, solo 4 imágenes distintas y 246 repeticiones idénticas.
Las dos técnicas coinciden exactamente.

### 6.4 · Dónde está realmente el límite

La pregunta siguiente es si el culpable es el mezclador o el banco de pruebas. Para separarlo se
repitió la medición alimentando el sistema con fotogramas ya preparados en memoria, de modo que
generar la señal de entrada costara prácticamente nada.

| Formato | Con las cámaras simuladas | Con entrada de coste casi nulo |
|---------|---------------------------|--------------------------------|
| 1080p50 | 1,8 de 50 | **50 de 50, fluido** |
| 2160p25 | 1,2 de 25 | **25 de 25, fluido** |
| 2160p50 | 0,8 de 50 | 1,3 de 50, sigue congelado |

La conclusión es importante y matiza mucho el hallazgo: en 1080p50 y 2160p25 **el cuello de botella
era la simulación de las cámaras**, no el mezclador. Cada cámara simulada decodifica un vídeo 4K, así
que cuatro cámaras suponen cuatro decodificaciones 4K simultáneas en la misma máquina que ejecuta el
mezclador. El mezclador sí puede con esos formatos. Solo en 2160p50 el límite es real y pertenece al
ordenador.

### 6.5 · Por qué conviene repetir la prueba

Se ha solicitado al equipo de laboratorio una segunda ejecución completa e independiente. El motivo no
es desconfianza, sino método: un resultado de cero pérdidas en 36 mediciones consecutivas es lo
bastante limpio como para que convenga confirmar que se reproduce antes de escribirlo en un artículo
sometido a revisión. Si la segunda tanda coincide, la afirmación queda respaldada por dos campañas
independientes.

Se han solicitado además algunas aclaraciones sobre las condiciones exactas de la primera tanda, entre
ellas una diferencia de consumo de procesador entre repeticiones que conviene entender antes de
publicar cualquier cifra.

### 6.6 · Qué aporta todo esto al artículo

1. Responde exactamente a lo que pedía el revisor, y la respuesta es favorable: no se descarta ningún
   fotograma en ningún entorno.
2. Obliga a matizar cómo se presentan los formatos superiores al básico, lo cual es incómodo pero es
   la lectura honesta de los datos.
3. Aporta una explicación física a otra anomalía que el mismo revisor había detectado: cuando el
   sistema repite fotogramas también deja de trabajar, y por eso el consumo de procesador bajaba en
   lugar de subir.

---

## Anexo · Comentarios de los revisores, texto original y correspondencia

A continuación se recoge el texto literal de cada comentario, seguido de una explicación breve en
español y de la sección de este informe donde se atiende.

---

### Revisor 1

> The manuscript presents a practical cloud-native architecture for real-time remote video production.
> The evaluation of resource consumption, switching latency, and failure recovery is useful. The
> following minor issues should be addressed before publication.

*Valoración de partida favorable: considera el trabajo útil y pide únicamente correcciones menores
antes de publicar.*

---

**R1.1**
> The statement that containerization and orchestration introduce no noticeable overhead should be
> limited to the evaluated single-node environment. The current experiments do not verify this
> conclusion in a distributed multi-node cluster.

*Solo se ha probado un ordenador, así que no se puede afirmar de forma general que no haya sobrecarga.
Hay que acotar la afirmación a ese escenario.*
**Atendido en:** 3.1 (resumen) y 3.15 (discusión).

---

**R1.2**
> The statistical terminology should be made consistent. The Abstract reports "average" CPU usage and
> latency, whereas the Results and Discussion mainly report median values. Please use the correct
> statistical terms consistently and provide appropriate variability measures.

*El resumen hablaba de "media" y el cuerpo del artículo de "mediana". Hay que unificarlo y, además,
acompañar cada valor con una medida de cuánto varía.*
**Atendido en:** 3.1, 3.11, 3.12 y 3.13.

---

**R1.3**
> Please clarify throughout the manuscript that the reported 293 ms latency represents
> command-to-output latency within the mixer rather than complete end-to-end REMI latency.

*Los 293 ms son el tiempo interno del mezclador, no la latencia total del sistema. Hay que dejarlo
claro en todo el artículo para que nadie lo confunda.*
**Atendido en:** 3.1, 3.9 y 3.19.

---

**R1.4**
> The failure-injection procedure should be described more clearly. Please specify which process or
> container was terminated, how the failure was detected, which component was restarted, and how
> output continuity was determined.

*Falta detalle del experimento de caída de cámara: qué se interrumpe exactamente, cómo se detecta,
qué lo reinicia y cómo se comprueba que la emisión no se corta.*
**Atendido en:** 3.10 y 3.13.

---

**R1.5**
> The comparison with OBS Studio should be interpreted carefully because the two systems use different
> processing pipelines, including CPU versus GPU compositing and raw output versus H.264 encoding.
> Please emphasize that Table 4 provides a practical reference rather than a strictly equivalent
> efficiency comparison.

*Comparar consumo con OBS Studio es engañoso porque los dos sistemas trabajan de forma distinta. Hay
que presentar la tabla como una referencia orientativa, no como una comparación de eficiencia.*
**Atendido en:** 3.17.

---

**R1.6**
> Claims concerning horizontal scalability should be moderated because only a single-node Kubernetes
> deployment was evaluated. Multi-node scalability remains an important direction for future
> validation.

*No se puede hablar de escalabilidad habiendo probado un solo nodo. Debe quedar como trabajo futuro.*
**Atendido en:** 3.1 y 3.15.

---

**R1.7**
> Since the control and telemetry layers expose TCP, HTTP, and AMQP services, the authors should
> briefly discuss authentication, encryption, and access-control requirements for practical remote
> deployment.

*El sistema abre servicios de control y telemetría por red y el artículo no dice nada de seguridad.
Hay que tratar autenticación, cifrado y control de acceso.*
**Atendido en:** 3.18.

---

**R1.8**
> A minor language check is recommended. For example, "compoud layout changes," "three deployments
> tiers," and "tight, highly and repeatable recovery distributions" should be corrected.

*Erratas de idioma. El "por ejemplo" indica que puede haber más, así que conviene una relectura
completa antes de reenviar.*
**Atendido en:** 3.22, y revisión final pendiente en 4.4.

---

### Revisor 2

> This work presents Voctomix 2.0 [...] It is evaluated on a single ten-core workstation across three
> deployment tiers and four video profiles [...] Publication of the source code and manifests is also
> welcome, and the topic is of clear relevance to small broadcasters and academic institutions.
> However, several issues should be addressed before the manuscript can be recommended for publication.

*Reconoce el valor del trabajo y la relevancia del tema, y valora que se publique el código, pero pide
resolver varios puntos antes de recomendar su publicación.*

---

**R2.1**
> The headline overhead claim is stronger than the measurements support [...] all values are whole-host
> /proc samples taken at roughly 90% of a ten-core CPU, where utilisation saturates as a metric and
> cannot discriminate between tiers. Second, Kubernetes is reported as consuming less CPU than the
> native baseline, which is not physically expected and suggests noise exceeding the effect size.
> Third, no output-integrity metric appears anywhere: without dropped-frame counts or sustained output
> frame rate at the programme sink, a lower CPU reading cannot be distinguished from a pipeline that is
> silently dropping frames. Please add per-tier frame-drop and output-fps figures, report dispersion,
> and soften the claim accordingly. Relatedly, contribution bullet 3 claims the manifests "optimize
> internal routing of uncompressed bandwidth", while Section 3.4 states no bridged control condition
> was measured.

*Es el comentario más exigente. Plantea tres cosas: que medir al 90 % de procesador no permite
distinguir entre entornos; que Kubernetes aparezca consumiendo menos que la ejecución nativa no es
físicamente esperable; y que no hay ninguna medida de lo que sale por la salida, de modo que un
consumo bajo podría esconder un sistema que descarta fotogramas. Además señala que se afirma una
optimización que nunca se midió.*
**Atendido en:** 3.1 (afirmación suavizada), 3.4 (tercera contribución), 3.11 (variabilidad y anomalía
de Kubernetes) y 6 (medición de integridad, pendiente de incorporar al texto según 4.1).

---

**R2.2**
> The delta with respect to upstream Voctomix is not established, and the version naming is likely to
> cause confusion: C3VOC itself maintains a branch named voctomix2, which already provides a generic
> composite/transition engine [...] Naming the present fork "Voctomix 2.0" collides with that
> designation, and the claims in Section 2.3 and Table 1 that Voctomix "critically lacked … dynamic
> compositing" appear to be assessed against Voctomix 1.x rather than the current upstream state.
> Please rename the artefact, state the upstream commit or branch forked from, and add a short table
> mapping each claimed extension to what upstream already provides.

*Dice que no queda claro qué aporta este trabajo frente al proyecto original, que el nombre choca con
una rama que ya existe con ese nombre, y que se atribuyen carencias al original que en realidad no
tiene. Pide tres cosas: renombrar, indicar el punto exacto del que se parte, y una tabla que separe lo
heredado de lo aportado.*
**Atendido parcialmente en:** 3.2 y 3.5. Pendiente en 4.2, incluida la decisión sobre el nombre.

---

**R2.3**
> The telemetry subsystem is derived from the GUI, which contradicts the headless-observability claim
> [...] the state exporter polls the voctogui widget tree, and Figure 1 shows telemetry fed over HTTP
> from the operator GUI, yet line 267 asserts this "makes the headless pipeline fully observable". As
> described, telemetry is unavailable precisely in the unattended server-side deployment the paper
> argues for [...] Please clarify whether an exporter can run against voctocore directly; if not,
> state the limitation plainly and revise the claim.

*Detecta una contradicción real: el artículo presume de que el sistema puede funcionar sin interfaz
gráfica, pero la telemetría se obtiene precisamente leyendo esa interfaz. Pide aclararlo o reconocer
la limitación.*
**Atendido en:** 3.8 y 3.16.

---

**R2.4**
> The comparison against alternatives is not yet fair [...] In Table 1, obs-websocket supports
> concurrent clients and emits state events, so "Multi-operator: No" and "Advanced telemetry: No" for
> OBS Studio require correction or justification, and the criterion for "Partial" containerisation is
> undefined. In Table 4, the comparison is acknowledged to be confounded twice over (GPU versus CPU
> compositing; OBS performing a full x264 encode while Voctomix passes raw frames) [...] Either
> equalise the workload [...] or drop the CPU column and keep only the RAM comparison, which you
> rightly identify as the fairer one. Benchmarking against OBS Studio 27.2.3 also needs justification.

*Señala que la comparación con OBS Studio es injusta en las dos tablas. En la cualitativa, porque OBS
sí admite varios clientes y sí emite eventos de estado. En la numérica, porque los dos sistemas hacen
trabajos distintos. Ofrece explícitamente la salida de retirar la columna de procesador y quedarse
con la de memoria.*
**Atendido en:** 3.7 y 3.17.

---

**R2.5**
> The stated application domain is asserted but never connected to evidence about the delivery end:
> the introduction motivates the work by reference to distributed university campuses and
> distance-learning production networks, and the conclusion repeats this framing, yet nothing in the
> paper engages with how such audiences consume the produced material. Since the cost argument is
> ultimately an accessibility argument, a short grounding passage would strengthen the motivation.

*El artículo se justifica hablando de campus universitarios y educación a distancia, pero nunca
explica cómo llega el vídeo al público. Como el argumento de coste es en realidad de accesibilidad,
pide un párrafo breve que lo cierre.*
**Atendido en:** 3.3.

---

**R2.6**
> The resilience results are internally puzzling and the recovery mechanism is under-specified: Figure
> 10 reports detection falling from ~790 ms at 1080p25 to tens of milliseconds at 4K, while Figure 12
> shows total MTTR at 1080p50 lower than at 1080p25. MTTR is therefore non-monotonic in bitrate, which
> the frame-buffer explanation does not account for; if detection is triggered by a fixed byte or
> buffer threshold rather than a wall-clock timeout, stating so would resolve this. Please also
> specify, per tier, what actually restarts the failed source — the kubelet is named for Kubernetes,
> but the equivalent mechanism in the native and Docker scenarios is never described.

*Ha detectado que los tiempos de recuperación no siguen un patrón lógico al subir la resolución, y que
la explicación dada no lo justifica. Sugiere él mismo la explicación probable. Además pide decir qué
componente reinicia la cámara en cada uno de los tres entornos.*
**Atendido en:** 3.10 y 3.13.

---

**R2.7**
> AI-based transcription overlays: this bullet proposes routing programme audio to an ASR engine and
> feeding the result back as caption commands, composited into the live feed with no operator in the
> loop. A one-line acknowledgement of the failure mode would improve the section. [Sugiere el texto y
> la referencia R1: Hamid, O. H. (2024), IEEE CogSIMA.]

*Advierte de que generar subtítulos automáticos sin supervisión puede emitir en directo texto
incorrecto con apariencia de fiable. Propone él mismo la redacción y la referencia a citar.*
**Atendido en:** 3.20.

---

**R2.8**
> Inconsistent statistics: the abstract reports an "average" host CPU near 90% and an "average" latency
> of 293 ms, whereas Sections 4.1–4.2 report medians. Please harmonise and report dispersion alongside
> every central value, and explain the ~13 GB RAM figure for four 1080p25 sources, which is large
> relative to a ~300 ms (≈7.5 frame) latency budget.

*Coincide con el revisor 1 en lo de media y mediana, insiste en dar la dispersión de todos los valores,
y añade algo propio: hace el cálculo de que 300 milisegundos son unos siete fotogramas y medio, lo que
no explica 13 GB de memoria, y pide justificar esa diferencia.*
**Atendido en:** 3.1, 3.11, 3.12, 3.13 y 3.14.

---

**R2.9**
> Reproducibility and references: the code sits on a personal GitHub account with no archival
> identifier—please deposit a tagged release (e.g. Zenodo), state the licence explicitly (Table 1
> asserts MIT/GPL), and deposit the raw logs rather than offering them on request. The reference list
> leans heavily on vendor pages and trade press; please substitute peer-reviewed sources where the
> claim is technical. Permission for the third-party content and identifiable individuals in Figure 3
> should also be confirmed.

*Cuatro peticiones: un identificador permanente para el código, declarar bien la licencia, publicar
los datos en vez de ofrecerlos bajo petición, sustituir fuentes divulgativas por académicas, y
confirmar el consentimiento de las personas que aparecen en la Figura 3.*
**Atendido parcialmente en:** 3.6 (licencia) y 3.21 (texto de disponibilidad). Pendiente en 4.3.

---

**R2.10**
> References: the authors are to update the References Section after including the suggested reference
> [R1], and citing it appropriately at the indicated point.

*Recordatorio de añadir a la bibliografía la referencia que propone en el punto anterior.*
**Atendido en:** 3.20.
