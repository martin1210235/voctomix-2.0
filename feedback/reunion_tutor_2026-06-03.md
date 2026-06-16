# Feedback reunión con Álvaro — 2026-06-03

Checklist completo de cambios a realizar en la memoria del TFG y el paper,
ordenados para ir prompt a prompt. Marcar cada uno como completado al terminar.

---

## PAPER CIENTÍFICO

- [x] **PROMPT 1 — Añadir coautores al paper**
  > "Añade al paper a Alberto [apellidos] y a David [apellidos] como coautores con su afiliación y email. Te daré los datos exactos."

---

## PORTADA Y DATOS GENERALES

- [x] **PROMPT 2 — Fecha de la memoria**
  > "En la portada y donde aparezca la fecha '2 de febrero de 2026' o similar, cámbiala por 'Junio 2026'."

- [x] **PROMPT 3 — Tutor, ponente y departamento**
  > "En la portada: el tutor es Álvaro Llorente, el ponente es David [apellidos, te lo diré], el departamento es el de David (te lo confirmaré). Quita todas las interrogaciones que haya en esa sección y deja en blanco lo que no se pueda rellenar todavía."

---

## LISTA DE ACRÓNIMOS

- [x] **PROMPT 4 — FPS en mayúsculas**
  > "En la lista de acrónimos, el término FPS aparece en minúsculas. Ponlo en mayúsculas correctamente."

---

## CAPÍTULO 1 — OBJETIVOS

- [x] **PROMPT 5 — Reescribir los objetivos**
  > "Reescribe la sección de objetivos para que el objetivo principal y central sea: diseño e implementación de una arquitectura de código abierto para la producción remota de vídeo en tiempo real. El resto de funcionalidades (overlay, telemetría, stream blanker, Docker, etc.) deben presentarse como objetivos secundarios que cuelgan de ese objetivo principal, no como el foco central."

---

## CAPÍTULO 2 — ESTADO DEL ARTE

- [ ] **PROMPT 6 — Añadir JPEG XS y VC-3 en contribución**
  > "En el apartado 2.2.1 (o donde estén los formatos de contribución de vídeo), añade JPEG XS y VC-3 con una descripción breve de cada uno y por qué son relevantes."

- [ ] **PROMPT 7 — Reorganizar codecs de contribución y distribución**
  > "Reorganiza la sección 2.2 y 2.3 para que cada codec/protocolo aparezca en un único apartado (contribución O distribución, no en ambos). Agrupa todo bajo epígrafes claros tipo 'Codecs de contribución' y 'Codecs de distribución', evitando que parezca una lista de la compra. El SRT, que ahora aparece en los dos sitios, debe quedar solo en uno. Álvaro sugiere esta estructura de agrupación por tipo."

- [ ] **PROMPT 8 — Añadir UDP, TCP y HTTP en el estado del arte**
  > "En el estado del arte (cap. 2), añade un apartado o párrafo que explique UDP, TCP y HTTP como protocolos de transporte utilizados en el proyecto, ya que son los que realmente se usan y deben estar comentados."

- [ ] **PROMPT 9 — Profundizar en RAW video y H.264**
  > "En el estado del arte, amplía la explicación de RAW video y H.264, ya que son los dos formatos que se usan en el proyecto. Deben tener más peso que el resto."

- [ ] **PROMPT 10 — Añadir MOV en distribución**
  > "En el apartado de codecs/formatos de distribución, añade el formato MOV con una descripción breve."

- [ ] **PROMPT 11 — Nuevo apartado: casos de uso reales de producción remota**
  > "Al final del capítulo 2, añade un nuevo apartado (el último del capítulo) titulado algo como 'Experiencias reales de producción remota' o 'Casos de uso reales'. Incluye varios ejemplos reales y contrastados de producciones que han utilizado este modelo (p.ej. Juegos Olímpicos Tokyo 2020, UEFA Champions League, eventos CCC, etc.)."

---

## CAPÍTULO 3 — ARQUITECTURA DEL SISTEMA

- [ ] **PROMPT 12 — Figura diagrama de puertos (3.1) con draw.io**
  > "La figura principal del capítulo 3 con el diagrama de puertos y flechas del sistema hay que rehacerla. Genera el XML de draw.io equivalente a la figura actual para que yo la pueda abrir, editar y exportar desde draw.io. Que quede limpia, con los puertos correctos y que encaje bien en el margen."

- [ ] **PROMPT 13 — Resto de figuras del cap. 3 con draw.io**
  > "Revisa todas las figuras del capítulo 3 que estén generadas con código LaTeX/TikZ y genera su equivalente en XML de draw.io para que las pueda rehacer manualmente."

---

## CAPÍTULO 4 (NUEVO) — DESPLIEGUE DEL SISTEMA

- [ ] **PROMPT 14 — Crear nuevo capítulo 4: Despliegue**
  > "Crea un nuevo capítulo 4 titulado 'Despliegue del sistema de producción remota de vídeo' (o título similar). Debe tener tres apartados:
  > - 4.1: Lanzamiento con scripts en PC local — cómo funcionan los scripts de arranque, qué hacen, cómo se lanza el sistema.
  > - 4.2: Despliegue con Docker — Dockerfile, docker-compose, cómo se ha containerizado el sistema.
  > - 4.3: Despliegue con Kubernetes — manifiestos, orquestación, cómo se despliega en el clúster.
  > El actual capítulo 4 pasa a ser el capítulo 5."

---

## CAPÍTULO 5 (antes cap. 4) — RESULTADOS Y VALIDACIÓN

- [ ] **PROMPT 15 — Experimentos por número de cámaras**
  > "En el capítulo de resultados, añade un experimento en el que se mide el impacto de ir añadiendo cámaras (1, 2, 3 y 4) sobre la CPU, la RAM y el consumo energético. Incluye una gráfica que muestre la tendencia (si es lineal, logarítmica, etc.) y comenta qué ocurre al añadir cada cámara adicional."

- [ ] **PROMPT 16 — Capturas de telemetría**
  > "En el capítulo de resultados, añade un apartado con capturas de pantalla reales de la telemetría en funcionamiento: una captura del evento STATE (estado periódico) y una del evento CHANGE (cambio inmediato al hacer una acción en la GUI). Explica brevemente qué muestra cada una."

- [ ] **PROMPT 17 — Checklist de funcionalidades por escenario**
  > "En el capítulo de resultados, añade una tabla o checklist con entre 5 y 10 funcionalidades o aspectos medibles del sistema, y comprueba/indica cuáles funcionan en cada uno de los escenarios de despliegue (PC local, Docker, Kubernetes, dos PCs). Formato tabla."

---

## CAPÍTULO 6 (antes cap. 5) — LÍNEAS FUTURAS

- [ ] **PROMPT 18 — Reescribir líneas futuras con los nuevos puntos**
  > "Reescribe el apartado de líneas futuras incluyendo estos puntos por orden:
  > 1. Uso de tarjetas SDI en vez de IP para inyección de cámaras (acercamiento al entorno profesional real).
  > 2. Escalabilidad: estudio del número máximo de cámaras soportadas en función del hardware, con ejemplo del equipo usado.
  > 3. Evolución de la señal: pruebas con 4K, 50 fps y HDR.
  > 4. Evolución de la codificación: migración de H.264 a H.265, comparativa de eficiencia.
  > 5. Explotación en CyberNEMO: integración real y continuidad del proyecto en el marco del proyecto europeo.
  > 6. Publicación en GitHub y paper científico como vías de difusión y continuidad investigadora.
  > 7. Mejora de la interfaz: drag & drop, recarga en caliente de assets sin reiniciar el sistema, mayor dinamismo e intuitividad.
  > Cada punto: un párrafo breve, máximo 7-8 líneas."

---

## ANEXOS

- [ ] **PROMPT 19 — Reescribir aspectos éticos, económicos y ambientales**
  > "Reescribe el apartado de aspectos éticos, económicos y ambientales del anexo con estos contenidos:
  > - Éticos: posible eliminación de puestos de trabajo en producción audiovisual presencial; implicaciones de ciberseguridad al exponer servicios por red.
  > - Económicos: reducción de hardware desplazado, menos personal en el lugar del evento, reducción de gastos de transporte y logística. Es la principal ventaja económica del proyecto.
  > - Ambiental (positivo): menos hardware, menos transporte, menos emisiones. Ambiental (negativo): mayor carga en servidores, más consumo de CPU y electricidad. Concluir que el balance es positivo."

- [ ] **PROMPT 20 — Actualizar presupuesto**
  > "Actualiza el apartado de presupuesto (Anexo B) con estos datos:
  > - PC 1: 1.500 € (precio fijo).
  > - PC 2 (PC Sonda del laboratorio): busca sus características y estima su precio de mercado actual.
  > - Amortización: 6 años (mantener si ya está).
  > - Precio por hora de ingeniero: súbelo a 25 €/hora.
  > - Número de horas: calcula una estimación realista basada en los créditos del TFG (12 créditos ECTS) asegurando que sea mayor que el mínimo estipulado. Justifica el número."

---
