# Estructura de la presentación — Defensa TFG Voctomix 2.0

> Estado a 2026-07-09. Fuente: `presentacion_voctomix_etsit.pptx`.
> Objetivo: versión final para defensa; cambios puntuales solo.

## Cuerpo principal (51 diapos totales; 1–29 principal)

| # | Diapositiva | Estado | Notas |
|---|---|---|---|
| 1 | Portada | ✅ | Título oficial, tutores y Cátedra RTVE. |
| 2 | Índice | ✅ | 6 bloques: Introducción, Arquitectura, Implementación, Escenarios, Resultados, Conclusiones. |
| 3 | **INTRODUCCIÓN** | ✅ | Divisor. |
| 4 | Producción audiovisual tradicional | ✅ | Modelo SDI/hardware/in situ. |
| 5 | Producción audiovisual remota (REMI) | ✅ | Realización centralizada y límites de software de escritorio. |
| 6 | Evolución de la producción audiovisual | ✅ | Tradicional → REMI → virtualizada. |
| 7 | Objetivos | ✅ | OE-1…OE-6 + ODS. |
| 8 | Cadena de producción | ✅ | Contribución, mezcla, codificación y distribución. |
| 9 | Casos de uso reales | ✅ | C3VOC, Tokio 2020, LaLiga, NEMO/CyberNEMO. |
| 10 | **ARQUITECTURA** | ✅ | Divisor. |
| 11 | Dos módulos: voctocore + voctogui | ✅ | Separación núcleo/interfaz. |
| 12 | Arquitectura del sistema | ✅ | Diagrama global + puertos críticos. |
| 13 | **IMPLEMENTACIÓN** | ✅ | Divisor. |
| 14 | Módulos clave | ✅ | Compositor, blanker, overlays, AFV, telemetría. |
| 15 | Demostración en vídeo | ✅ | Vídeo integrado; llevar `demo_voctomix.mp4` suelto. |
| 16 | **ESCENARIOS DE DESPLIEGUE** | ✅ | Divisor. |
| 17 | Escenario 1: Un PC | ✅ | Desarrollo y validación básica. |
| 18 | Escenario 2: Dos PCs | ✅ | Producción remota en LAN. |
| 19 | Escenario 3: Docker Compose | ✅ | 11 contenedores con un comando. |
| 20 | Escenario 4: Kubernetes | ✅ | Orquestación con Minikube. |
| 21 | **RESULTADOS** | ✅ | Divisor. |
| 22 | Consumo de recursos | ✅ | CPU, RAM y energía. |
| 23 | Latencia | ✅ | Conmutación y transición de modo. |
| 24 | Fiabilidad | ✅ | Estabilidad y resiliencia. |
| 25 | **CONCLUSIONES** | ✅ | Divisor. |
| 26 | Conclusiones | ✅ | Checklist OE-1…OE-6. |
| 27 | Líneas futuras | ✅ | Cámaras físicas, H.265, 4K, GUI dinámica, más métricas. |
| 28 | Impacto y méritos | ✅ | CyberNEMO, artículo, GitHub. |
| 29 | GRACIAS POR SU ATENCIÓN | ✅ | Cierre. |

## Contenido adicional (30–51, solo para preguntas)

30 divisor · 31 índice adicional · 32 mapa de puertos · 33 INTRO/BREAK ·
34 modos de composición · 35 Stream Blanker · 36 overlays y rótulos ·
37 Audio Follows Video · 38 telemetría · 39 RabbitMQ · 40 estado inicial ·
41 ficheros incorporados · 42 herramientas de medición · 43 CPU · 44 RAM ·
45 energía · 46 latencia de conmutación · 47 latencia de transición ·
48 resiliencia · 49 estabilidad · 50 comparativa de mezcladores ·
51 presupuesto económico.

## Notas de cierre

- La diapositiva 41 muestra un árbol reducido con puntos suspensivos; el árbol
  completo antes/después está en el Anexo C de la memoria.
- Se eliminaron las diapositivas redundantes de contenido adicional para dejar
  solo material útil ante preguntas del tribunal.
- OE-6 se mantiene como en la memoria, pero la defensa oral debe matizar:
  "validado sobre la infraestructura real de CyberNEMO con fuentes controladas;
  la captura física es la primera línea futura".

## Tiempo objetivo

15 min + 5 min de preguntas. El guion actual estima aproximadamente 15:30; en el
ensayo conviene recortar 30–45 s en índice, escenarios o cierre.
