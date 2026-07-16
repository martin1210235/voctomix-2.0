# Grabar el vídeo demo con OBS (opción A: tres vistas en un PC)

Todo se graba en **este** PC. El core de Voctomix corre aquí, así que la GUI, la
señal de programa (`:15000`) y la telemetría salen todas de esta máquina. No hace
falta el PC de Arya.

OBS captura cada **ventana por separado** (no una región de pantalla), así que
**da igual dónde tengas las ventanas** en el escritorio: las colocas dentro de OBS.
Solo no las minimices durante la grabación.

---

## 0. Instalar OBS

```bash
sudo apt install obs-studio
```

## 1. Abrir las tres ventanas

```bash
cd /home/sonda/Documentos/voctomix
./presentacion_tfg/obs/launch_demo_recording.sh
```

El script levanta el stack Docker, espera a que `:15000` responda y abre:

- **voctogui** (tu mesa de control),
- **PROGRAM** (ffplay, lo que ve el público),
- **TELEMETRY** (terminal con `docker compose logs -f telemetry`, eventos JSON).

> Modo nativo (sin Docker): `MODE=native ./presentacion_tfg/obs/launch_demo_recording.sh`
> (usa `tail -f registros/gui_state.json` para los logs).

## 2. Ajustes base de OBS (una sola vez)

- **Ajustes > Vídeo:** Resolución base y de salida `1920x1080`; FPS `30`.
- **Ajustes > Salida > Grabación:** Formato `mkv` (más seguro ante cortes) y luego
  *Archivo > Remux* a `mp4`; o directamente `mp4` si lo prefieres simple.
  Codificador `x264`, calidad alta.
- **Audio:** sin micrófono (narras en directo). Deja el **Audio del escritorio**
  a volumen bajo para que se oiga el cruce de audio en la fase 6 (Audio Follows
  Video); puedes silenciarlo si prefieres solo tu voz.

## 3. Montar la escena (3 fuentes de ventana)

En **Fuentes**, botón `+` → **Captura de ventana** (en X11 es *XComposite*; en
Wayland, *PipeWire*). Crea tres, una por ventana:

| Fuente (nombre) | Ventana a elegir |
|---|---|
| GUI | la de voctogui |
| PROGRAM | PROGRAM (ffplay) |
| TELEMETRY | TELEMETRY (terminal) |

Coloca cada una con **Editar transformación** (`Ctrl+E`), con lienzo `1920x1080`:

| Fuente | Pos X | Pos Y | Tipo de caja | Tamaño de caja | Alineación |
|---|---|---|---|---|---|
| GUI | 0 | 0 | Ajustar al interior | 1216 x 1080 | Arriba-izquierda |
| PROGRAM | 1216 | 0 | Ajustar al interior | 704 x 540 | Arriba-izquierda |
| TELEMETRY | 1216 | 540 | Ajustar al interior | 704 x 540 | Arriba-izquierda |

Queda así (encaja perfecto: 1216+704 = 1920, 540+540 = 1080):

```
┌──────────────────────────┬─────────────────────┐
│                          │  PROGRAM :15000     │
│      GUI (voctogui)      ├─────────────────────┤
│                          │  TELEMETRY (logs)   │
└──────────────────────────┴─────────────────────┘
```

### (Opcional) Etiquetas quemadas en el vídeo

Para que el vídeo se explique solo, igual que la diapo, añade 3 fuentes de **Texto**:

| Texto | Pos X | Pos Y |
|---|---|---|
| GUI · voctogui | 24 | 24 |
| Señal de programa · :15000 | 1240 | 16 |
| Logs de telemetría | 1240 | 556 |

## 4. Grabar

Pulsa **Iniciar grabación** y sigue `GUION_VIDEO.md` (segundo a segundo, ~4:15).
Graba por fases si lo prefieres; en edición acelera x1.5 el tecleo y los tiempos
muertos. El `.mp4` que sale **ya está compuesto** con el layout de la diapo: no hay
que montar nada, solo recortar.

## 5. Insertarlo en la presentación

Como OBS ya compone las tres vistas en un solo vídeo, la **diapositiva 13** necesita
**un único hueco de vídeo** (no tres). Inserta el `mp4` con
*Insertar > Vídeo > Este dispositivo*, "Iniciar: al hacer clic", y lleva el `mp4`
suelto en el portátil además del embebido.

---

## Notas / problemas

- **Wayland:** *XComposite* no funciona; usa la fuente **PipeWire** y elige cada
  ventana en el portal. El resto es idéntico.
- **La ventana capturada sale en negro:** en algunos drivers OBS no captura ventanas
  ocultas; muévela a un hueco visible del escritorio (o a otro monitor) y no la minimices.
- **Los logs van muy rápidos/lentos:** puedes tener a mano RabbitMQ
  (`http://localhost:15672`, voctomix / voctomix123) para el plano de "cada acción es
  un evento" en la fase 7.
