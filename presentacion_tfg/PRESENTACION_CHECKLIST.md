# Checklist de formato y requisitos — Defensa TFG Voctomix 2.0

> Fuente de verdad de **cómo tiene que ser** la presentación. Revisar antes de cerrar cualquier cambio.
> Lo automatizable se comprueba con `python3 verificar.py`.

## 🎨 Estilo visual (obligatorio, mantener SIEMPRE)
- **Paleta:** azul oscuro `#08447C` (títulos, acentos), azul brillante `#2899F9` (barras/acentos secundarios), gris cuerpo `#464747`, gris subtítulo/pie `#8A8C8E`, blanco `#FFFFFF`.
- **Bloque de título de cada diapo de contenido:** título `#08447C` ~25 pt (0.6, 0.92) + barra de acento `#2899F9` (0.62, 1.55, 1.1×0.04) + subtítulo `#8A8C8E` ~13 pt (0.6, 1.6).
- **Pie:** "Defensa TFG · ETSIT-UPM" gris 9 pt (esquina inferior izquierda).
- **Tarjetas:** rectángulo redondeado con **barra de acento a la izquierda** (0.13–0.18 de ancho), cabecera en negrita `#08447C` ~13,5 pt, cuerpo `#464747` ~11 pt. Fondo blanco o `#F5F7FA`.
- **Divisores de sección:** fondo de plantilla (antena/satélite) + panel azul + título centrado 44 pt en MAYÚSCULAS.
- **Coherencia:** cualquier diapo nueva se **duplica de una existente** para heredar cabecera/pie/fondo, y se reutiliza el estilo de tarjeta.

## ✍️ Redacción
- **Prohibido el guion ortográfico (—)** como inciso: usar coma, dos puntos o punto y coma.
- Frases cortas, directas, registro técnico. Sin primera persona del singular.
- Números con **coma decimal** (1,8 pp) en español.
- Nombres de módulos/comandos consistentes (LIVE/PAUSE/NOSTREAM, voctocore, voctogui, RabbitMQ, AMQP).

## ✅ Checks obligatorios tras cada cambio
- [ ] Compilar/exportar a PDF y **revisar visualmente** las diapos tocadas (LibreOffice → PDF → PNG).
- [ ] `python3 verificar.py` sin errores (duplicados, placeholders, nº de diapos).
- [ ] Sin partes `slideXX.xml` duplicadas (residuo de borrar diapos mal).
- [ ] Sin `(insertar foto)` / `(insertar vídeo)` en el **cuerpo principal** (diapos 1–29). En CONTENIDO ADICIONAL se toleran temporalmente.
- [ ] Texto que no se salga de su caja ni pise otros elementos.
- [ ] Índices/toc coherentes con las secciones reales.
- [ ] Hacer **backup** en `backups/` antes de tocar el pptx (ya se hace en cada script).

## 🔗 Coherencia presentación ↔ memoria TFG
- Datos numéricos deben coincidir con la memoria (cap. 5): CPU 33,5→38,8 % (Docker), K8s ~50 % (Minikube), RAM ~10 %, energía 25–32 W (<20 % TDP), conmutación 1,5 ms, transición 2,8 ms (Docker)/79,8 ms (K8s), resiliencia ~520 ms/570 ms.
- Estructura del índice = secciones reales (Introducción, Arquitectura, Implementación, Escenarios, Resultados, Conclusiones).
- Líneas futuras = las 5 de la memoria (cámaras físicas, H.265, 4K, GUI dinámica, más métricas).
- Objetivos OE-1…OE-6 reflejados en Conclusiones.

## 💾 Reproducción del vídeo (diapo 14)
- Arranca **al hacer clic** (no autoplay), **sin bucle**, se para al final. Barra de control visible al pasar el ratón (PowerPoint).
- Llevar el `demo_voctomix.mp4` **suelto en USB** además del embebido.

## ❤️ Cosas que le gustan a Martín (respetar)
- Estética limpia, formal, alineada, "digna de presentación".
- Visual > texto: tarjetas, iconos, figuras que se entiendan de un vistazo.
- Explicaciones directas, sin rodeos.
- Imágenes **sencillas y visuales**, no recargadas.
