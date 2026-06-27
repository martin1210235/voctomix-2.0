# PAPER_PATTERNS — patrones de papers similares (cómo presentan las cosas)

Base de conocimiento viva. Cada vez que analizamos un paper parecido, anotamos
aquí qué hacen bien y qué deberíamos imitar. Objetivo: acercar nuestro paper a
la "versión que no rechazan". Iniciado 2026-06-27.

## Paper gemelo nº1 — DeepStream + SRS containerizado (MDPI Electronics)

Fuente: https://pmc.ncbi.nlm.nih.gov/articles/PMC11723310/ — casi mismo perfil
(GStreamer + Docker Compose, métricas CPU/RAM/latencia/FPS, edge).

**Estructura de secciones (IMRaD MDPI):**
1. Introduction
2. Background Review and Related Study (¡10 subsecciones!)
3. **Materials and Methods** (nombre canónico MDPI; nosotros usamos
   "System Architecture" + "Deployment Scenarios")
4. Experimental Results
5. Discussion (8 subsecciones temáticas con NOMBRE)
6. Conclusions

**Lo que hacen y deberíamos imitar:**
- **17 figuras y 5 tablas.** Densidad visual alta: gráficas comparativas
  CPU/RAM lado a lado, capturas de despliegue real, diagramas de arquitectura.
- **Tabla de versiones de software** (Docker 19.03.6, CUDA 10.2…) → patrón de
  reproducibilidad. ⇒ ACCIÓN: añadir tabla de entorno/versiones a nuestro paper
  (ya tenemos los datos: i9-10900X, Docker 29.1.3, Minikube v1.38.1…).
- **Tabla de especificaciones de dispositivo** separada de la de software.
- **Discussion con subsecciones temáticas nombradas**: Energy-Constrained,
  System Security, Real-World Applications, Future Directions. ⇒ Nosotros ya
  tenemos Interpretation/Comparison/Limitations/Future; considerar elevar
  "Security" (plano de control sin cifrar) a subsección propia.
- **Abstract ~175 palabras**: problema → enfoque → 5 hallazgos con métricas.
  ⇒ ACCIÓN: revisar longitud de nuestro abstract (puede estar largo).
- **Validación con capturas de despliegue real** (tráfico, vigilancia).
  ⇒ Nosotros ya lo tenemos con CyberNEMO. ✅ (fortaleza)
- **Transparencia de limitaciones** explícita (degradación >3 dispositivos).
  ⇒ Nosotros ya las tenemos. ✅

## Checklist de imitación (lo que aплicamos a NUESTRO paper)

- [ ] Añadir **tabla de entorno de pruebas / versiones de software** (repro).
- [ ] Revisar longitud del abstract (objetivo ~175-200 palabras).
- [ ] Valorar subsección "Security" en Discussion.
- [ ] Mantener alta densidad de tablas-resumen en Results (ya reforzado con
      CPU/RAM, ancho banda, latencia, resiliencia).
- [ ] Considerar 1-2 figuras comparativas más (Docker vs K8s lado a lado).

## Qué es lo más importante en estos papers (resumen transversal)

1. **Reproducibilidad** = versiones exactas + datos crudos + repo público. Es el
   criterio nº1 de aceptación en papers de sistemas.
2. **Resultados que explican el "por qué"**, no solo el número (causalidad).
3. **Comparación justa** contra alternativas (tabla comparativa). ✅ ya la tenemos.
4. **Validación en producción real** (no solo laboratorio). ✅ CyberNEMO.
5. **Densidad**: tablas-resumen y figuras antes que prosa larga.

## Paper nº2 — Middleware monolítico → microservicios (MDPI Electronics 15(1) 221, 2025)

Fuente: https://www.mdpi.com/2079-9292/15/1/221 — microservicios + evaluación de
rendimiento en Electronics, muy reciente (perfil de "sistema + medidas").

**Lo que hacen y nos sirve:**
- Foco explícito en **performance, scalability y availability** como los tres
  ejes de evaluación. ⇒ Nosotros cubrimos performance y (con resiliencia)
  availability; podríamos nombrar explícitamente esos ejes en Results/Discussion.
- Mejoras presentadas como contribuciones concretas y nombradas (procesamiento
  asíncrono, autenticación de doble capa, caché). ⇒ Patrón: contribuciones con
  nombre propio y verificables (ya lo hacemos en la lista de Intro).
- **Comparación monolítico vs microservicios** = baseline claro. ⇒ Equivalente
  nuestro: Docker vs Kubernetes y la tabla comparativa vs OBS/vMix/ATEM.

## Patrón transversal de papers de "overhead de contenedores"

(de la literatura de evaluación de contenedores, p.ej. container performance on
IoT/cloud)

- **Baseline obligatorio**: nativo vs contenedor, o entorno A vs B, con la misma
  carga. ⇒ Nosotros: Docker vs K8s con idéntica carga de 4 fuentes. ✅
- **Tabla de entorno/versiones** para reproducibilidad. ✅ ya añadida (tab:testenv).
- **Varias repeticiones + mediana/percentiles**, no una sola medida. ✅ (n=30,
  10 iteraciones de resiliencia, 31 min de estabilidad).
- **Explicar la fuente del overhead** (no solo medirlo): plano de control,
  cgroups, namespaces. ✅ ya explicado (Minikube control plane).
- **Limitaciones de escalado** explícitas (host único, sin red física entre
  nodos). ✅ ya en Limitations.

> Corrección: el paper "gemelo" nº1 (PMC11723310) está en **MDPI Sensors**
> (ISSN 1424-8220), no en Electronics. El paper nº2 (microservicios bancarios,
> 2079-9292) sí es **Electronics**.

## Paper nº3 — Remote rendering QUIC vs WebRTC (arXiv 2505.22132, 2025)

Kubernetes + GStreamer + evaluación de streaming en tiempo real. Texto completo
accesible (HTML), lo que permite contar con precisión.

**Datos de calibración (muy útiles):**
- **~24 referencias**, 2 figuras + 3 tablas, **abstract ~140 palabras / 3 frases**.
- Estructura IMRaD con Related Work en subsecciones temáticas.
- **Resultados solo en tablas** (latencia, jitter, pérdida, CPU/GPU), por
  protocolo × red × bitrate. Confirma que tablas-por-configuración es aceptado;
  nosotros combinamos tablas + pgfplots (más rico).
- Reproducibilidad: VM 8 CPU / 32 GB / vGPU, Helm chart, bandas de red explícitas,
  NTP, tcpdump/PCAP. ⇒ Nuestro equivalente: telemetría STATE + tab:testenv. ✅

## Métricas objetivo para NUESTRO paper (de los 3 analizados)

| Elemento | Rango observado | Nuestro estado |
|---|---|---|
| Abstract | 140 (arXiv) – 175 (Sensors) palabras | **~250 → recortar a ≤200** |
| Referencias | 24 (arXiv) – 40+ (MDPI) | bib fina; subir a **~35-45** peer-reviewed |
| Figuras+tablas | 5 (arXiv) – 22 (Sensors) | ~10; aceptable, +1-2 opcional |
| Results | tablas por configuración | ✅ tablas + pgfplots |
| Discussion | subsecciones temáticas nombradas | ✅ Interpretation/Comparison/Security/Limitations/Future |

## Por analizar (cola de trabajo)

- [x] arXiv 2505.22132 (Kubernetes+GStreamer) — calibración longitud/citas.
- [ ] 1 paper más de Electronics (2079-9292) para nº de citas típico MDPI.
- [ ] Un paper IEEE de live media / SRT para calibrar Background.

---

## Ficheros relacionados (mapa)

- Reglas de revisión que aplican estos patrones → [PAPER_REVIEW_CHECKLIST.md](PAPER_REVIEW_CHECKLIST.md)
- Estado y bloqueos → [PAPER_STATUS.md](PAPER_STATUS.md)
- Cifras canónicas (paper↔TFG) → [DATA_CONSISTENCY.md](DATA_CONSISTENCY.md)
- Candidatos a cita → [RELATED_WORK_NOTES.md](RELATED_WORK_NOTES.md)
