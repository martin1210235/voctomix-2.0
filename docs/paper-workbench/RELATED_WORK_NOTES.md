# RELATED_WORK_NOTES — lecturas para Background y bibliografía

Notas de calibración del paper (venue fit) y candidatos a cita. Generado
2026-06-27. Cada entrada confirmada se traslada a `references.bib`.

## Encaje de revista (venue fit)

- **MDPI Electronics SÍ publica trabajos de este perfil.** Existe un paper muy
  cercano: *"The Construction of a Stream Service Application with DeepStream
  and Simple Realtime Server Using Containerization for Edge Computing"*
  (Electronics, PMC11723310). Usa **GStreamer + Docker/Docker Compose** sobre
  NVIDIA Jetson Xavier NX y compara latencias de RTMP/WebRTC/HLS y consumo de
  CPU. Confirma que nuestro enfoque (pipeline GStreamer containerizado, métricas
  de CPU/latencia) encaja en el scope y el formato de la revista.
  → Modelo a imitar en densidad de métricas y estructura de Results.
  → Candidato a cita directa en Background (workflows containerizados).

## Candidatos a cita (verificar antes de añadir)

| Tema | Fuente | Uso en paper | URL |
|---|---|---|---|
| GStreamer containerizado + métricas (MDPI Electronics) | DeepStream/SRS edge paper | Background §containers; comparación de overhead | https://pmc.ncbi.nlm.nih.gov/articles/PMC11723310/ |
| Evolución hacia latencia sub-segundo en live media | survey arXiv 2310.03256 | Intro/Background (contexto latencia) | https://arxiv.org/pdf/2310.03256 |
| Multi-channel live streaming baja latencia | arXiv 2410.16284 | Background pipelines | https://arxiv.org/pdf/2410.16284 |
| Sistema remoto panorámico baja latencia | arXiv 2401.03398 | Background (producción remota) | https://arxiv.org/pdf/2401.03398 |
| SRT open source baja latencia (white paper) | Haivision | refuerza `sharabayko2024_srt` | https://www.haivision.com/white-papers/srt-open-source/ |
| 2025 Broadcast Transformation Report (43% remote prio.) | Haivision | dato de motivación en Intro (ya citado `haivision_broadcast_report_2025`) | — |

## Observaciones de calibración

- La mayoría de "resultados" del sector están en white papers comerciales, no en
  papers académicos: refuerza el valor de contribución académica del nuestro
  (medidas reproducibles, código abierto).
- Prioridad de refuerzo bibliográfico del paper (bib hoy ~11 KB): añadir 1-2
  papers académicos revisados por pares (el de Electronics y un arXiv de
  latencia) para subir densidad y credibilidad del Background.
- Pendiente: revisar 2-3 papers recientes del propio número de Electronics para
  fijar longitud objetivo y densidad de citas por sección.

---

## Ficheros relacionados (mapa)

- Patrones de presentación de esos papers → [PAPER_PATTERNS.md](PAPER_PATTERNS.md)
- Hub / estado → [PAPER_STATUS.md](PAPER_STATUS.md)
- Reglas de revisión (incl. respaldo bibliográfico) → [PAPER_REVIEW_CHECKLIST.md](PAPER_REVIEW_CHECKLIST.md)
