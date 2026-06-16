# Feedback reunión con tutores — 2026-06-15

Checklist completo de cambios a realizar en la memoria del TFG, ordenados por sección.
Marcar cada uno como completado al terminar.

---

## CAPÍTULO 1 — INTRODUCCIÓN

- [x] **Mencionar la cátedra de RTVE en la introducción**
  > En el cuarto párrafo de la introducción, donde se menciona CyberNEMO, añadir que el proyecto está enmarcado en la cátedra de Radiotelevisión Española (RTVE) de la UPM.

---

## CAPÍTULO 2 — ESTADO DEL ARTE

- [ ] **2.1 — Ampliar con estudios académicos sobre producción audiovisual remota**
  > Buscar y añadir más referencias académicas (Google Scholar, IEEE) sobre producción audiovisual remota. El apartado está demasiado escaso de citas de peso.

- [ ] **2.1.2 — Extender un ~20% e integrar Docker/Kubernetes**
  > El apartado 2.1.2 debe ser más extenso. Integrar una mención a Docker y Kubernetes como infraestructura que ha facilitado la adopción de sistemas de producción remota. Mencionar también Matroska como contenedor de vídeo RAW en este contexto (moverlo desde donde esté ahora).

- [ ] **2.2 (Protocolos de transporte) — Integrar en 2.3/2.4, no como sección independiente**
  > La sección de protocolos de transporte no debe ser un apartado autónomo. Integrar su contenido dentro de las secciones de contribución (2.3) y distribución (2.4) según corresponda. Además, los títulos de las subsecciones no deben usar siglas: escribir "User Datagram Protocol", "Transmission Control Protocol", "Hypertext Transfer Protocol" en lugar de UDP, TCP, HTTP.

- [ ] **2.3.2 — Renombrar a "Contenedores multimedia de contribución" y revisar contenido**
  > Renombrar el apartado de formatos de contribución a "Contenedores multimedia [de contribución]". Quitar Matroska de aquí (no es un formato de contribución profesional) y añadir en su lugar los formatos profesionales MXF y XF (usados en cámaras de broadcast).

- [ ] **2.3.3 — Añadir códecs de audio profesionales**
  > Añadir Dolby Atmos y AC-4 como códecs de audio relevantes en el contexto de contribución profesional.

- [ ] **2.4.2 — Renombrar a "Contenedores multimedia de distribución"**
  > Renombrar el apartado de formatos de distribución a "Contenedores multimedia de distribución" para mantener coherencia con el cambio en 2.3.2.

- [ ] **2.4.3 — Añadir H.266/VVC y AC-4 y actualizar tabla comparativa**
  > Añadir H.266/VVC como sucesor de H.265 en la sección de códecs de vídeo de distribución. Añadir AC-4 como códec de audio tras AAC. Actualizar la tabla comparativa de códecs para reflejar estas incorporaciones.

- [ ] **2.5 — Añadir "Proyecto 5G Media" (Telefónica) como caso de uso**
  > Incluir el proyecto 5G Media de Telefónica como nuevo caso de uso REMI. Añadir también una subsección específica para los proyectos europeos de la UPM: 5G Media, NEMO y CyberNEMO.

---

## CAPÍTULO 3 — DISEÑO E IMPLEMENTACIÓN

- [ ] **3.4 — Ocultar subsecciones del índice (solo 2 niveles de profundidad en TOC)**
  > Las subsecciones de 3.4 (3.4.1, 3.4.2...) no deben aparecer en el índice general. Limitar la profundidad del TOC a dos niveles en este capítulo, o usar `\subsubsection*` para las subsecciones internas.

- [ ] **3.9.2 — Ajustar terminología de los tipos de eventos**
  > Cambiar "por latido" por "periódico" o "por intervalos de tiempo". Revisar también el título del tipo CHANGE para que sea más formal (evitar "por evento" si suena coloquial).

---

## CAPÍTULO 4 — DESPLIEGUE DEL SISTEMA

- [ ] **Introducción del capítulo — Justificar la relevancia de Docker/Kubernetes**
  > En el segundo párrafo de la introducción del capítulo, añadir que el despliegue en Kubernetes fue un objetivo prioritario del proyecto porque los proyectos CyberNEMO y NEMO de la UPM utilizan Kubernetes como infraestructura de producción.

---

## CAPÍTULO 5 — PRUEBAS DE VALIDACIÓN

- [ ] **5.3 — Justificar mejor las diferencias de CPU/RAM/energía entre Docker y Kubernetes**
  > El texto actual no explica suficientemente por qué Kubernetes consume más recursos que Docker Compose. Añadir que el consumo extra se debe al plano de control de Minikube (API server, etcd, scheduler, controller-manager), que no existe en Docker Compose. En producción con un clúster externo este overhead desaparecería.

- [ ] **5.3 — Clarificar la descripción de la prueba de latencia**
  > Explicar con más detalle cómo se midió la latencia: qué se midió exactamente (tiempo entre comando de conmutación y primer fotograma del nuevo origen en el programa), cómo se obtuvo el valor (~1,5 ms), y por qué ese valor cumple el requisito de producción en directo.

- [ ] **5.3 — Investigar y usar el umbral de percepción humana para latencia**
  > El umbral de 40 ms usado actualmente puede tener base bibliográfica más sólida. Buscar referencias sobre percepción humana de retardo en vídeo en directo (en torno a 80 ms según algunos estudios). Considerar citar ese valor y comparar la latencia medida (~1,5–1,8 ms) con él.

- [ ] **5.3 — Añadir métricas específicas de Kubernetes**
  > Las métricas del escenario Kubernetes son escasas. Añadir datos sobre: tiempo de arranque del clúster, tiempo hasta que todos los pods están Ready, consumo del plano de control, y comparativa directa con Docker Compose para cada métrica.

---

## CAPÍTULO 6 — CONCLUSIONES Y LÍNEAS FUTURAS

- [ ] **6.2 — Verificar el punto 2 de líneas futuras y eliminar si es incorrecto**
  > Releer el punto 2 de las líneas futuras. Si no es preciso o no corresponde a una mejora real del sistema, eliminarlo.

- [ ] **6.2 — Añadir línea futura: actualización de códec H.264 → H.265**
  > Añadir una nueva línea futura (~4 líneas) sobre la migración del pipeline de vídeo de H.264 a H.265 (HEVC), con la reducción de ancho de banda que implicaría manteniendo la misma calidad.

- [ ] **6.2 — Añadir línea futura: escalado a resolución 4K**
  > Añadir una nueva línea futura (~4 líneas) sobre la ampliación de la resolución del sistema de 1080p a 4K (3840×2160), indicando los requisitos adicionales de CPU y ancho de banda.

- [ ] **6.2 — Añadir línea futura: interfaz gráfica más dinámica e intuitiva**
  > Añadir una nueva línea futura (~4 líneas) sobre la mejora de la GUI para permitir cambios de configuración en tiempo real sin reiniciar el sistema (añadir/quitar fuentes en caliente, reconfigurar composites dinámicamente).

- [ ] **6.2 — Añadir línea futura: análisis de métricas y monitorización en Kubernetes**
  > Añadir una nueva línea futura (~4 líneas) sobre la integración de herramientas de observabilidad nativas de Kubernetes (Prometheus, Grafana) para monitorización avanzada del sistema en producción.

---

## ANEXO B — PRESUPUESTO ECONÓMICO

- [ ] **Amortización: cambiar de 6 años a 5 años**
  > En el cálculo de amortización del equipo, actualizar el periodo de 6 años a 5 años.

- [ ] **Precio del equipo: verificar coste real del i9-10900X + 128 GB RAM**
  > Contrastar el precio indicado del equipo con el coste real de mercado de un sistema con Intel Core i9-10900X y 128 GB de RAM DDR4 (estimado entre 5.000 y 7.000 €). Actualizar el valor si hay discrepancia.

- [ ] **Eliminar la partida de material fungible (impresión y encuadernación)**
  > Quitar la línea de material fungible (impresión/encuadernación) del presupuesto, ya que no es un gasto imputable al proyecto.

- [ ] **Costes indirectos: cambiar del 15% al 25%**
  > Actualizar el porcentaje de costes indirectos del 15% al 25%.

- [ ] **Beneficio industrial: investigar el valor correcto y actualizar**
  > El porcentaje de beneficio industrial actual es incorrecto. Investigar el valor estándar para proyectos de ingeniería (en torno al 6% sobre el coste de ejecución material, no sobre el total). Corregir el cálculo y el valor indicado.
