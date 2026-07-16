
## 2026-07-07 — sesión sync
- **Detectado (tú, diapo 1):** línea de tutores actualizada → añadido Álvaro Llorente Gómez como cotutor; "Tutor" → "Tutores".
- **Aplicado (yo):** eliminado "Voctomix 2.0" del pie en 37 diapositivas → ahora "Defensa TFG · ETSIT-UPM". Backup en backups/…_prefooter_*.pptx
- **Aplicado (yo):** creada diapositiva "Motivación" (nueva diapo 8, tras Objetivos) con estilo de la diapo 24: título + subtítulo + 3 tarjetas (Coste prohibitivo / Software libre limitado / Producción remota en auge) + frase destacada. Backup en backups/…_premotivacion_*.pptx
- **Aplicado (yo):** portada — corregido título (estaba corrupto: "optimizaci´on", "cÓdigo", 44pt, partido). Ahora título oficial completo, limpio, centrado, 28pt, Montserrat blanco. Backup en …_pretitulo_*.pptx
- **Aplicado (yo):** diapo "Contexto" (RTVE) como nueva diapo 3, con logo Cátedra RTVE + texto beca→motivación; línea discreta "Beca de la Cátedra RTVE — ETSIT-UPM" en la portada. (Corregido bug de layout: había 4 layouts 'Blank Slide' de distintos másters; usado el limpio.)
- **Detectado (tú):** borrada diapo Contexto RTVE; Motivación movida antes de Objetivos.
- **Aplicado (yo):** 3 diapos nuevas tras el divisor INTRODUCCIÓN → (4) Producción tradicional [Fig 2.1 + cajas SDI/ATEM/La Liga], (5) REMI [Fig 2.2 + cajas realización centralizada/coste/OBS-vMix], (6) Tabla comparativa Tradicional vs REMI. Beca Cátedra RTVE incluida en las NOTAS de cada diapo. Backup …_preintro_*.pptx
- **Aplicado (yo):** Arquitectura → gráfica movida a la derecha y agrandada + tabla de puertos (13 filas) a la izquierda. Borradas El problema / Contexto y motivación / Estado del arte. Rescatado: línea "Democratizar + ODS 9,4,10" a la diapo Motivación; contexto Voctomix v1.3 (del Río) a las notas de la tabla comparativa. Backup …_prearq_*.pptx
- **Aplicado (yo):** ODS movido de Motivación → Objetivos (línea de propósito centrada bajo los 6 OE). Nueva diapo "¿Dónde encaja Voctomix 2.0?" (Fig 2.3 cadena completa) como puente al inicio de la sección técnica, tras el divisor "Cómo está construido". Backup …_precadena_*.pptx
- **Aplicado (yo):** revisada "Cadena de procesamiento" vs "¿Dónde encaja?": complementarias (interna vs externa), se mantienen ambas. Eliminada del pie la línea redundante de codificación/distribución (H.264/RTMP/HLS), ya cubierta por "¿Dónde encaja?".
- **Detectado (tú):** (1) divisor INTRODUCCIÓN sin sub-índice; (2) divisor "Cómo está construido" → "Arquitectura"; (3) divisor "Lo que he desarrollado" → "Implementación"; (4) borrada "Cadena de procesamiento". Cambios aceptados como nueva base; NO deshacer.
- **Detectado (tú):** borrada "Contribuciones"; retocado divisor "Resultados y validación".
- **Aplicado (yo):** diapo "Demostración en vídeo" rehecha con 3 placeholders → GUI grande (izq), Señal de programa :15000 (arriba-dcha), Logs de telemetría (abajo-dcha), los dos pequeños. Etiquetados con ▶ "insertar vídeo". Backup …_prevideos_*.pptx
- **Aplicado (yo):** nueva diapo "Telemetría en RabbitMQ" (captura paper/figures/rabbitmq_queues.png) tras el vídeo. Pie corregido: la captura muestra colas vcompressor/vproduction/vqprobe (entorno CyberNEMO), NO CHANGE/STATE; pie reescrito fiel a la imagen. Backup …_prerabbit_*.pptx
- **Detectado (tú):** borradas "Despliegue" (resumen escenarios) y "Telemetría en RabbitMQ" (¿intencionado?).
- **Aplicado (yo):** movidas "Resultados: RAM" y "Resultados: energía" del anexo a la sección principal, tras CPU. Orden: CPU→RAM→Energía→conmutación→resiliencia. Transición y estabilidad siguen en el anexo. Backup …_preresultados_*.pptx
- **Aplicado (yo):** re-añadida diapo "Telemetría en RabbitMQ" tras el vídeo (la habías borrado sin querer).
- **Aplicado (yo):** (1) reordenado cierre → Conclusiones antes de Impacto y méritos, luego Líneas futuras; (2) "Impacto y méritos" rehecha: 3 columnas (Producción real / Paper científico / Código abierto) con texto, URL del repo y placeholder de foto etiquetado en cada una; (3) "Resultados: consumo de recursos" rediseñada: sin cajas, gráficas más grandes + viñetas horizontales. INCIDENCIA corregida: un find por subcadena machacó el índice; restaurado backup precierre y rehecho con buscador por título exacto. Backup …_precierre_*.pptx
- **PENDIENTE avisar:** (a) 2 diapos "GRACIAS POR SU ATENCIÓN" duplicadas (28,29); (b) índice desactualizado respecto a las secciones nuevas (INTRODUCCIÓN/ARQUITECTURA/IMPLEMENTACIÓN/ESCENARIOS/RESULTADOS/CONCLUSIONES).

## 2026-07-09 — cierre contenido adicional
- **Aplicado (yo):** recortado contenido adicional a lo esencial: deck final de
  **51 diapositivas** (1–29 principal, 30–51 apoyo). Eliminadas las diapos
  redundantes de implementación/respaldo: composición resumen, overlays resumen,
  blanker resumen, AFV+telemetría resumen, contenerización, Kubernetes, por qué
  PC→Kubernetes, estado del arte de tecnologías y distribución.
- **Aplicado (yo):** intercambiadas las diapositivas de latencia de transición y
  resiliencia en el contenido adicional.
- **Aplicado (yo):** rehacida "Ficheros incorporados" como árbol reducido y
  legible; el árbol completo antes/después queda referenciado al Anexo C.
- **Aplicado (yo):** actualizados `PRESENTACION_ESTRUCTURA.md`,
  `PRESENTACION_BRIEF.md`, `PRESENTACION_PREGUNTAS_TRIBUNAL.md` y regenerado
  `GUION_Presentacion_Voctomix.docx`.
