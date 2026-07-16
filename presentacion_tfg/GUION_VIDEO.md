# Guion del vídeo demo — Voctomix 2.0 (opción A: tres vistas en directo, ~4:15)

Vídeo pregrabado que se reproduce en la diapositiva 13. **Tú narras en directo encima.**
Estilo: directo y sencillo, frases cortas.

> **Opción A (elegida):** las **tres vistas** están en pantalla desde el segundo 0, igual que
> en la diapositiva: **GUI grande a la izquierda**, **señal de programa (:15000) arriba-derecha**
> y **terminal de telemetría abajo-derecha**. La telemetría corre de fondo todo el vídeo, así que
> cada botón que pulsas se ve reflejado en la salida de programa **y** en el JSON. Duración ~4:15.

---

## 1. Preparación (antes de grabar)

**Montaje en pantalla (fijo todo el vídeo):**

```
┌──────────────────────────┬─────────────────────┐
│                          │  PROGRAMA :15000     │  ← ffplay, lo que ve el público
│                          │  (arriba-derecha)    │
│      voctogui (GUI)      ├─────────────────────┤
│      grande, izquierda   │  TERMINAL telemetría │  ← tail -f gui_state.json
│                          │  (abajo-derecha)     │     (JSON scrolleando)
└──────────────────────────┴─────────────────────┘
```

**Arranque (Docker):**
```bash
cd /home/sonda/Documentos/voctomix
sudo docker compose up -d                                          # 11 contenedores
ffplay -hide_banner -window_title "PROGRAM" tcp://127.0.0.1:15000  # ventana del espectador
tail -f registros/gui_state.json                                  # terminal abajo-dcha, letra grande
cd voctogui && python3 voctogui.py                                # la GUI
# RabbitMQ solo 5 s al final:  http://localhost:15672  (voctomix / voctomix123)
```

**Grabación:** OBS a 1080p, **sin micro**, cámaras con **audio distinto por fuente**, graba
**por fases** y en edición **acelera x1.5** el tecleo (fase 4) y los tiempos muertos.

**Modelo A/B:** el bus **A** es la fuente principal (programa); el bus **B** es la segunda fuente
que usan los modos compuestos (el recuadro del PIP, la derecha del Side-by-Side…).

---

## 2. Segundo a segundo (todos los botones)

> Cada fila: **Tiempo · Botón (tecla) · qué dices.** La telemetría (abajo-dcha) está visible
> siempre: señálala cuando cambies de fuente para que se vea el evento en el JSON.

### Fase 0 — Entorno · 0:00–0:15
| Tiempo | Acción | Qué dices |
|---|---|---|
| 0:00–0:08 | Muestras las 3 vistas | "Esto es Voctomix 2.0. A la izquierda mi mesa de control; arriba-derecha lo que ve el espectador; abajo-derecha la telemetría en vivo." |
| 0:08–0:15 | Señalas: arriba 6 fuentes, centro buses A/B, abajo la barra | "Arriba las seis fuentes, en medio los dos buses, abajo los controles." |

### Fase 1 — Fuentes · 0:15–0:55  *(A = programa, B = 2ª fuente)*
| Tiempo | Botón (tecla) | Qué dices |
|---|---|---|
| 0:15–0:22 | **CAM1** en A (F1) | "El bus A es el programa. Pongo la cámara 1." |
| 0:22–0:34 | **CAM2 → CAM3 → CAM4** en A (F2–F4) | "Tengo cuatro cámaras, cambio entre ellas. Mira el JSON abajo: cada cambio se registra." |
| 0:34–0:42 | **BREAK** en A (F5) | "BREAK es la pausa, con su propia música." |
| 0:42–0:48 | **INTRO** en A (F6) | "INTRO es la careta de entrada, en bucle." |
| 0:48–0:55 | **CAM2** en bus B (tecla 2) | "Y en el bus B dejo la cámara 2, para combinarla con la 1." |

### Fase 2 — Composición · 0:55–1:40
| Tiempo | Botón (tecla) | Qué dices |
|---|---|---|
| 0:55–1:03 | **FULL SCREEN** (F5) | "Pantalla completa: solo una fuente." |
| 1:03–1:14 | **PIP** (F7) | "Picture-in-picture: la cámara 2 en un recuadro sobre la 1." |
| 1:14–1:24 | **SIDE BY SIDE** (F6) | "Lado a lado, las dos a la vez." |
| 1:24–1:33 | **LECTURE** (F8) | "Modo conferencia: ponente y contenido. El típico de una charla." |
| 1:33–1:40 | **MIRROR** (F9) | "Con MIRROR invierto quién va grande y quién pequeño." |

### Fase 3 — Cómo se aplica la mezcla · 1:40–2:05
| Tiempo | Botón (tecla) | Qué dices |
|---|---|---|
| 1:40–1:50 | **TRANS** (Espacio) | "Aplico el cambio con transición suave, 750 milisegundos. Fíjate en la ventana de programa." |
| 1:50–1:58 | **CUT** (Enter) | "O con corte directo, instantáneo." |
| 1:58–2:05 | **RETAKE** (Retroceso) | "Y RETAKE reaplica lo anterior si me equivoco." |

### Fase 4 — Overlays y rótulos · 2:05–2:50
| Tiempo | Botón | Qué dices |
|---|---|---|
| 2:05–2:14 | **LOGO 1** | "Activo el logo. Aparece con un fundido, no de golpe." |
| 2:14–2:21 | **LOGO 2** | "Puedo tener un segundo logo, independiente." |
| 2:21–2:34 | Escribo en **DYNAMIC TEXT 1** + **INSERT 1** | "Escribo un rótulo, el nombre del ponente, y lo inserto abajo." |
| 2:34–2:44 | Escribo en **DYNAMIC TEXT 2** + **INSERT 2** | "Y una segunda línea, el cargo. Son dos capas de texto independientes." |
| 2:44–2:50 | **CUT** a otra fuente | "Al cortar, los rótulos se apagan solos. No me tengo que acordar." |

### Fase 5 — Stream Blanker · 2:50–3:30  *(mira la ventana de programa)*
| Tiempo | Botón | Qué dices |
|---|---|---|
| 2:50–3:00 | **LIVE** | "En LIVE, el público ve exactamente lo que mezclo." |
| 3:00–3:13 | **PAUSE** (sigues tocando A/B por detrás) | "Pulso PAUSE: el público ve la pantalla de pausa, y yo sigo preparando por detrás sin que se note." |
| 3:13–3:22 | **NOSTREAM** | "NOSTREAM corta la señal del todo, para los bloques entre secciones." |
| 3:22–3:30 | **LIVE** | "Y vuelvo a directo, limpio." |

### Fase 6 — Audio Follows Video · 3:30–3:50
| Tiempo | Acción | Qué dices |
|---|---|---|
| 3:30–3:50 | **CUT** CAM1 → CAM2 (audios distintos); señalas el vúmetro | "Cambio de cámara y el audio cruza solo a la fuente activa. No he tocado ni un fader." |

### Fase 7 — Telemetría y RabbitMQ · 3:50–4:05
| Tiempo | Acción | Qué dices |
|---|---|---|
| 3:50–3:58 | Señalas el terminal (ya visible) y das 2 cortes; se ve el JSON | "Todo lo que hago se publica como evento, en JSON: CHANGE, STATE…" |
| 3:58–4:05 | Traes RabbitMQ (:15672) 5 s al frente | "Y viaja por RabbitMQ. Se puede monitorizar y auditar la producción desde fuera, en tiempo real." |

### Fase 8 — Cierre · 4:05–4:15
| Tiempo | Acción | Qué dices |
|---|---|---|
| 4:05–4:15 | Vuelves a la salida de programa en LIVE | "Todo esto con software libre, en un portátil. Sin hardware caro y sin depender de nadie. Esto es Voctomix 2.0." |

---

## 3. Chuleta de botones (qué es cada uno)
- **Fuentes A / B:** CAM1-4 (cámaras), BREAK (pausa con música), INTRO (careta en bucle). A = programa, B = segunda fuente.
- **FULL SCREEN / SIDE BY SIDE / PIP / LECTURE:** los 4 modos de composición.
- **MIRROR:** invierte A y B en el modo compuesto.
- **RETAKE / CUT / TRANS:** reaplicar / cortar instantáneo / transición animada (750 ms).
- **LOGO 1 / LOGO 2:** dos logos PNG independientes, con fundido.
- **DYNAMIC TEXT 1 / 2 (+ INSERT):** dos capas de rótulo inferior, con auto-off al cortar.
- **LIVE / PAUSE / NOSTREAM:** los tres estados de la salida al público.

## 4. Post-producción y checklist
- Une las fases 0→8; **acelera x1.5** el tecleo y los tiempos muertos.
- Comprueba que se lee el terminal (JSON) todo el vídeo; si no, re-grábalo con más zoom / letra más grande.
- Si te pasas de ~4:15, recorta primero: nombrar cam3/cam4 sin pulsar (fase 1) y el RETAKE (fase 3).
- Inserta el `mp4` en la diapositiva 13 (Insertar > Vídeo > Este dispositivo; "Iniciar: al hacer clic").
- **Lleva el `mp4` suelto** en el portátil, además del embebido.
- **Ensaya cronometrando**: con comentarios, 4 min pasan rápido.
