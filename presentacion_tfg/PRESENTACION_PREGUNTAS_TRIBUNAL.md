# Preparación turno de preguntas — Tribunal

> Dónde es MÁS probable que pregunten y qué llevar preparado. Diapo de respaldo en CONTENIDO ADICIONAL entre paréntesis.

## 🔥 Preguntas muy probables

### Arquitectura / diseño
- **¿Por qué cliente-servidor sobre TCP y RAW I420?** → separación núcleo/interfaz, control headless, calidad sin compresión intermedia (622 Mbit/s por fuente). Coste: ancho de banda interno alto (mencionar como limitación). (Diapo 11, 32 puertos)
- **¿Por qué no reusar OBS/vMix?** → no operan headless, ni multioperador, ni en contenedores; atados al escritorio. (Diapo 6)
- **¿Qué has añadido tú sobre el Voctomix original?** → OE-1…OE-6: composición+transiciones, rótulos con auto-off, stream blanker 3 estados, AFV, telemetría RabbitMQ, Docker (11 contenedores), Kubernetes. (Diapo 26)

### Resultados (lo más técnico → preparar bien)
- **¿Por qué Kubernetes consume ~50 % fijo de CPU?** → overhead del plano de control de **Minikube** (4 procesos en el mismo equipo), NO del mezclado; en un clúster real del proveedor no compartiría recursos. (Diapo 22, 43)
- **¿La latencia de transición 79,8 ms en K8s es un problema?** → es transición de MODO (no corte de cámara); el corte crítico es 1,5 ms. Aun así 79,8 ms es por Minikube. (Diapo 23, 47)
- **¿Cómo mides energía?** → sensor RAPL del procesador, descontando reposo. (Diapo 45)
- **¿Por qué solo 4 cámaras / sesiones de 5 min?** → alcance del TFG; margen para más (38,8 % CPU). Validación larga = 31 min sin fugas. (Diapos 43, 49)
- **¿Fuentes sintéticas (FFmpeg), no cámaras reales?** → sí; es la 1ª línea futura (validar con captura física). Reconocerlo con naturalidad. (Diapo 28)

### Despliegue
- **⭐ ¿Por qué esta evolución, de un PC hasta Kubernetes?** → **NEMO y CyberNEMO trabajan con un clúster de Kubernetes** para sus proyectos; por eso el **objetivo final era desplegar en Kubernetes**. Los cuatro escenarios muestran el camino de lo más simple (un PC) a lo orquestado (K8s), validando que el mismo sistema escala sin tocar el código. (Diapos 17–20; respuesta oral)
- **¿Diferencia real Docker vs K8s aquí?** → misma funcionalidad; K8s aporta orquestación/escalado sin tocar código. Medidos ambos. (Diapos 19–20)
- **¿Una sola imagen para 11 contenedores?** → sí, misma imagen, distinto proceso; voctogui nativo (necesita servidor gráfico). (Respuesta oral; detalle en memoria cap. 4)

### Estado del arte / contribución-distribución
- **¿Contribución y distribución?** → contribución SDI/SRT (ej. LaLiga), distribución RTMP→HLS/DASH. (Diapo 8)
- **Casos reales:** C3VOC (origen), Tokio 2020, LaLiga, 5G Media/UPM, CyberNEMO. (Diapo 9)

### CyberNEMO y seguridad
- **¿En qué consiste CyberNEMO?** → proyecto europeo de **ciberseguridad** para entornos IoT, Edge y Cloud. La **UPM lidera** el caso de uso de **producción multimedia colaborativa y segura** (UC1). Voctomix es el **motor de producción de vídeo** de esa cadena. (Diapo adicional 53 "¿En qué consiste CyberNEMO?")
- **¿Qué relación tiene con tu trabajo?** → es **prácticamente lo mismo que he construido**: la cadena de producción remota que CyberNEMO valida y protege desde el punto de vista de seguridad.
- **Objetivo de seguridad (clave para responder):** que **nadie acceda al sistema desde fuera** (Zero Trust Network Access, ZTNA) y que **no se pueda suplantar la identidad de las señales de vídeo** (integridad de contenido). En una frase: comprobar que la cadena es **segura de extremo a extremo**.
- **Componentes de seguridad de CyberNEMO:** ZTNA (acceso Zero Trust), ZT-FML (ML federado), IPDM-DSS (detección/prevención de intrusiones), CASB/PRESS/PPE (privacidad), SAAM. Mi trabajo **no implementa** esos componentes; aporta y valida la **cadena de producción** sobre la que actúan.
- **KPIs del piloto (por si preguntan cómo se mide):** precisión de detección de amenazas (>15 %), acceso no autorizado / integridad de contenido (<20 %, vía ZTNA), tiempo de detección/mitigación (<30 %), latencia con microsegmentación (<25 %).
- **Enlace con mi limitación de seguridad:** el puerto de control **9999 expuesto** es justo la superficie que ZTNA cubriría en CyberNEMO.

### Qué más se haría / líneas futuras
- **¿Qué habrías hecho con más tiempo?** / **¿línea futura principal?** → sobre todo **probarlo con cámaras físicas reales** (hasta ahora fuentes sintéticas con FFmpeg). Y el resto de líneas futuras: **H.265/HEVC** (mitad de ancho de banda), **4K**, **GUI dinámica** (añadir/quitar fuentes en caliente) y **más métricas** (pruebas más largas, redes más exigentes). (Diapo 27)

### Dificultades del proyecto
- **⭐ ¿Dónde estuvo la principal dificultad / complicación del proyecto?** → en dos frentes:
  1. **Colorimetría BT.709.** Los vídeos de cámaras convencionales o editados con software de consumo suelen venir en rango `pc` (full range); voctocore espera rango televisivo (`tv`) y espacio `bt709`. Sin conversión, **los colores se desviaban de forma perceptible en la mezcla** (aunque la conexión se establecía correctamente). Solución: filtros FFmpeg `scale=out_range=tv` y `colorspace=bt709`, que recalculan los píxeles en tiempo real sin degradación visible. (Memoria cap. 3.2)
  2. **Funcionalidades sofisticadas.** Implementar el **Audio Follows Video** (cruce automático del audio siguiendo a la cámara activa) y el **Stream Blanker** (conmutación de tres estados LIVE/PAUSE/NOSTREAM con conmutación de alpha) obligó a integrarse en el pipeline de GStreamer sin romper el núcleo existente. (Diapos adicionales 34–37)

### Impacto / coste
- **¿Coste real del proyecto?** → 14.429,25 € (Anexo B). Frente a hardware dedicado (miles a millones). Software 0 € en licencias. (Diapo 51, Anexo A/B)
- **Seguridad:** puerto de control 9999 expuesto → riesgo de acceso no autorizado a una emisión; quien despliega debe proteger la red. (Anexo A ético)
- **ODS:** 9 (industria/innovación), 4 (educación), 10 (reducción de desigualdades). (Diapo 7)

## 🧠 Debilidades a tener preparadas (por si las tocan)
- **Coherencia OE-6 / producción real:** OE-6 "Despliegue en producción real"
  sigue siendo la afirmación más fuerte de la defensa. No es un error, porque es
  el objetivo tal como está formulado en la memoria, pero conviene tener lista
  la respuesta: "validado sobre la infraestructura real de CyberNEMO con fuentes
  controladas; la captura física es la primera línea futura". Si se quisiera
  blindar aún más, la formulación alternativa sería "Validación en entorno real
  (CyberNEMO)".
- Sin cámaras físicas (solo FFmpeg).
- Ancho de banda interno RAW muy alto (622 Mbit/s/fuente) → futura 4K x4.
- Reconfiguración en caliente no soportada (reiniciar para cambiar nº fuentes) → línea futura GUI dinámica.
- K8s solo en Minikube local, no clúster cloud real.

## 📌 Por preparar (material)
- Repasar cifras de memoria cap. 5 de memoria (que salgan de carrerilla).
- Tener claro el flujo del vídeo demo por si piden explicar una función concreta.
- Saber justificar cada decisión de arquitectura (el "por qué").
