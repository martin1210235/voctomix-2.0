# PAPER_STATUS — panel de control del paper científico

Estado vivo del paper MDPI Electronics (`paper/main.tex`). Actualizar al cerrar
cada tarea. Última actualización: 2026-06-27.

## Estado global

Borrador estructural **completo** (IMRaD + boilerplate MDPI, ~1280 líneas). La
redacción está hecha; lo que falta es **cerrar consistencia de datos, citas y
figuras**. No es "escribir de cero", es "auditar y pulir".

## Bloqueos prioritarios (orden de impacto)

1. ⛔ **Publicar el código en ambas URLs antes del envío** — el `dataavailability`
   cita `gitlab.com/GATV/nemo/voctomix` y `github.com/martin1210235/voctomix-2.0`.
   Verificado 2026-06-27: **ninguna de las dos resuelve todavía** (GATV solo tiene
   `voctomix1`; el GitHub no existe). Un revisor comprueba estas URLs. Hay que
   publicar voctomix2 en GATV GitLab y crear/espejar el repo GitHub, y confirmar
   que ambas URLs cargan, antes de enviar.
2. ⛔ **ORCID de los 4 autores** — decisión del usuario (2026-06-27): dejar los
   placeholders `000X` y el TODO en `main.tex` L.28-32; rellenar antes del envío.
3. ⚠️ **Refuerzo bibliográfico** — `references.bib` aún algo fino; añadir 1-2
   papers académicos (ver RELATED_WORK_NOTES.md).
4. ⚠️ **Decisión de revista** — confirmar Electronics vs Future Internet.

## Hecho

- ✅ Cita Bernabéu no verificable (`tsa_remi_2022`) sustituida por
  `tsa_laliga_srt_2025` (Appear/LaLiga), alineada con el TFG. (2026-06-27)
- ✅ Eliminada nota suelta "CAMBIAR IMAGEN A UNA DE RABBITMQ" del cuerpo. (2026-06-27)
- ✅ **TODAS las cifras alineadas con el TFG** (I420/622 Mbps/2.49 Gbps; CPU
  38.8/51.2 %; latencia 1.5/1.8 ms vs 45 ms ITU-R; hardware i9-10900X/128 GB;
  energía RAPL). Cita `itur_bt1359_1998` añadida. (2026-06-27)
- ✅ Añadida subsección "Long-Term Stability and Resilience" (31 min sin fuga;
  recuperación cam1 520/570 ms). (2026-06-27)
- ✅ Compila: 19 págs, 0 citas sin resolver. Push a Overleaf hecho. (2026-06-27)

## Pendientes de datos externos

- ORCID de los 4 autores (`main.tex` L.28-32, placeholders `000X`).
- URL repositorio público definitiva (`dataavailability`, L.1236) y verificar
  que existe y es accesible.
- Confirmar journal destino (Electronics vs Future Internet) y ajustar scope.

## Figuras

| Figura | Fuente | Estado |
|---|---|---|
| Arquitectura | TikZ inline | ✅ |
| voctogui_screenshot | `figures/` | ✅ |
| rabbitmq_queues | `figures/` | ✅ (decidida; nota eliminada) |
| cybernemo_operator / output | `figures/` | ✅ |
| CPU/RAM barras | TikZ inline | ⚠️ números a corregir (DATA_CONSISTENCY) |
| Histograma latencia | TikZ inline | ⚠️ números a corregir |

## Tareas de redacción/refuerzo

- [ ] Reforzar `references.bib` (solo ~11 KB): SRT, SMPTE 2110, K8s real-time
      media, Docker overhead benchmarking. Ver [RELATED_WORK_NOTES.md](RELATED_WORK_NOTES.md).
- [x] Subsección de Resiliencia (520/570 ms) añadida a Results.
- [x] Subsección "Security Considerations" añadida a Discussion.
- [x] Tabla de entorno/versiones (tab:testenv) añadida.
- [ ] Verificar longitud/densidad frente a 2-3 papers recientes de la revista.

## Mapa de ficheros y automatización

Este fichero es el **hub**. Los ficheros de apoyo se enlazan entre sí para que,
al actualizar el paper, cada uno lleve al siguiente sin tener que recordarlo:

| Fichero | Rol |
|---|---|
| **PAPER_STATUS.md** (este) | Panel de control: estado, bloqueos, datos pendientes |
| [DATA_CONSISTENCY.md](DATA_CONSISTENCY.md) | Cifras canónicas paper↔TFG↔dato crudo |
| [PAPER_REVIEW_CHECKLIST.md](PAPER_REVIEW_CHECKLIST.md) | Reglas de revisión (adaptadas del checklist TFG) |
| [PAPER_PATTERNS.md](PAPER_PATTERNS.md) | Patrones de papers analizados (cómo presentan) |
| [RELATED_WORK_NOTES.md](RELATED_WORK_NOTES.md) | Candidatos a cita / encaje de revista |
| [check_paper.sh](check_paper.sh) | **Guardián automático** (parte automatizable del checklist) |

### Automatización (se ejecuta sola al actualizar el paper)

`check_paper.sh` está instalado como **git pre-commit hook** del repo del paper:
cada `git commit` dentro de `paper/` ejecuta automáticamente las comprobaciones
(citas definidas, 0 referencias rotas, sin notas sueltas/marcadores de conflicto,
sin cifras ya descartadas) y **bloquea el commit** si algo falla. El script vive
en el repo principal (`docs/paper-workbench/`); reinstalar tras clonar, desde la
raíz del proyecto:
`ln -sf "$(pwd)/docs/paper-workbench/check_paper.sh" paper/.git/hooks/pre-commit`.

Flujo completo al editar el paper:
1. Editar `main.tex` siguiendo [PAPER_REVIEW_CHECKLIST.md](PAPER_REVIEW_CHECKLIST.md).
2. Registrar cualquier cifra nueva en [DATA_CONSISTENCY.md](DATA_CONSISTENCY.md).
3. `git commit` → el hook corre `check_paper.sh` y valida solo.
4. `git push` al remote de Overleaf del paper (NO el push de la memoria TFG).
