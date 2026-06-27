# PAPER_REVIEW_CHECKLIST — qué revisar SIEMPRE en el paper

Adaptación, para el **paper científico en inglés** (MDPI), del checklist de
revisión de la memoria TFG. Aplicar esta lista completa cada vez que se revisa o
se edita `main.tex`. Pensado para ejecutarse (en parte) de forma automática: ver
[check_paper.sh](check_paper.sh).

> ⚠️ Diferencias clave respecto al checklist del TFG (idioma inglés):
> - **Punto decimal**, no coma (`1.5 ms`, no `1,5 ms`).
> - **Em-dash (—) permitido** en inglés (la prohibición de guiones es solo del TFG).
> - Números: estilo MDPI (cifras para magnitudes con unidad; texto para <10 en prosa general).
> - Unidades con espacio fino LaTeX: `5~ms`, `25~fps`, `48~kHz`.

## 0. Automatizable (lo verifica `check_paper.sh`)

- [ ] Todo `\cite{}` tiene entrada en `references.bib`.
- [ ] Compila sin `undefined reference/citation` nuevas.
- [ ] No quedan notas sueltas / TODO / texto en español dentro del cuerpo
      (`CAMBIAR`, `TODO`, `PENDIENTE`, `XXX`).
- [ ] No reaparecen cifras antiguas ya descartadas (guardia de regresión):
      `829`, `3.32`, `22~ms`, `i7-8750`, `UYVY`, `WiFi`. Ver [DATA_CONSISTENCY.md](DATA_CONSISTENCY.md).

## 1. Veracidad técnica y consistencia con el TFG ⚠️ PRIORITARIO

- [ ] Cada cifra de `main.tex` coincide con [DATA_CONSISTENCY.md](DATA_CONSISTENCY.md)
      (que mapea paper ↔ cap5 del TFG ↔ dato crudo). **Antes de aceptar cualquier
      número nuevo, registrarlo allí.**
- [ ] Descripciones de comportamiento del sistema contrastadas con el código real
      (`voctocore/lib/*`, `default-config.ini`, `docker-compose.yml`, `k8s/`).
- [ ] Conteos (servicios, puertos, fuentes, escenarios) verificados contra los
      ficheros reales, no asumidos.
- [ ] Diagrama de arquitectura: cada puerto/flecha/servicio correcto frente al
      código (un puerto mal es un error factual, no estético).

## 2. Verificación numérica de figuras pgfplots (OBLIGATORIO)

- [ ] Para cada `\addplot coordinates {...}`: la suma de frecuencias coincide con
      el N declarado en el texto (p.ej. histograma de latencia debe sumar 30).
- [ ] En `ybar interval`, la última coordenada es solo el borde derecho, no suma.
- [ ] Si el texto dice "X % de los casos", la proporción es exacta según el plot.

## 3. Bibliografía

- [ ] Toda afirmación técnica no trivial, dato o estándar tiene `\cite{}`.
- [ ] Afirmaciones de mercado/contexto en la Introducción respaldadas por informe
      o paper (no sin cita).
- [ ] Fuentes de autoridad (IEEE/ACM, RFC, SMPTE/ITU); reemplazar fuentes
      informales. Candidatos en [RELATED_WORK_NOTES.md](RELATED_WORK_NOTES.md).
- [ ] Antes de añadir una entrada a `references.bib`: `grep` para no duplicar.

## 4. Referencias LaTeX

- [ ] Todo `\ref{}` tiene su `\label{}`; toda tabla/figura referenciada existe.
- [ ] Cada figura/tabla referenciada explícitamente en el texto ANTES de aparecer.
- [ ] Recompilar 2× tras cambios de labels y confirmar 0 undefined nuevas.

## 5. Acrónimos y terminología

- [ ] Cada acrónimo definido en su primera aparición ("Audio Follows Video (AFV)").
- [ ] Tras la definición, usar siempre la forma corta; lista de abreviaturas del
      final coherente con lo usado (ni de más ni de menos).
- [ ] Mismo término para el mismo concepto en todas las secciones.

## 6. Tiempos verbales (inglés)

- [ ] **Presente** para describir el sistema ("voctocore hosts…", "the compositor
      updates…").
- [ ] **Pasado** para experimentos y resultados ("was measured", "the median was").
- [ ] No mezclar ambos en el mismo párrafo descriptivo.

## 7. Estructura MDPI y altura del contenido

- [ ] Estructura IMRaD coherente (Intro → Background → Architecture/Methods →
      Results → Discussion → Conclusions). Ver patrones en [PAPER_PATTERNS.md](PAPER_PATTERNS.md).
- [ ] Abstract ~175–220 palabras: problema → enfoque → contribuciones con métricas.
      Verifica que no promete ni omite nada del cuerpo.
- [ ] Conclusiones: cada cifra es verificable en Results; **no overclaim** (si el
      cuerpo dice "<5 ms", las conclusiones no pueden decir "<3 ms").
- [ ] Densidad: tablas-resumen y figuras antes que prosa larga; sin relleno
      ("it is important to note that…").

## 8. Tablas y figuras

- [ ] Cada tabla/figura aporta algo que el texto solo no transmite; si no, eliminar.
- [ ] Caption autónomo (se entiende sin el párrafo).
- [ ] Ejes con etiqueta y unidades; datos coherentes con el texto.
- [ ] Flotadores `[H]` para pequeñas/medianas; `[htbp]` para grandes.

## 9. Reproducibilidad (criterio nº1 anti-rechazo)

- [ ] Tabla de entorno/versiones presente y completa (tab:testenv).
- [ ] `dataavailability` apunta a un repo público real y accesible.
- [ ] Datos suficientes para reproducir cada medida (carga, nº repeticiones, métrica).

## 10. Compilación y sync

- [ ] `latexmk -pdf -shell-escape` → 0 errores propios (el del logo MDPI es del
      entorno, no nuestro).
- [ ] Tras commit en `paper/`: `git push` al remote de Overleaf del paper
      (NO el push de la memoria TFG).

---

## Motivos frecuentes de rechazo (vigilar activamente)

De la investigación sobre desk-reject (40–50 % se rechazan antes de revisión):

1. **Scope mismatch** → confirmar revista y citar papers de ese número.
2. **Reproducibilidad insuficiente** → §9.
3. **"Proof of concept" sin terminar** → mantener resiliencia + CyberNEMO + estabilidad.
4. **Baselines débiles** → tabla comparativa y Docker vs K8s.
5. **Inconsistencias de datos** → §1 + check_paper.sh.

---

## Ficheros relacionados (mapa)

- Cifras canónicas → [DATA_CONSISTENCY.md](DATA_CONSISTENCY.md)
- Patrones de papers analizados → [PAPER_PATTERNS.md](PAPER_PATTERNS.md)
- Estado y bloqueos → [PAPER_STATUS.md](PAPER_STATUS.md)
- Candidatos a cita → [RELATED_WORK_NOTES.md](RELATED_WORK_NOTES.md)
- Guardián automático → [check_paper.sh](check_paper.sh)
