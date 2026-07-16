# Revision post-cambios del paper - 2026-07-08

Estado despues de aplicar correcciones en `paper/main.tex`.

## Veredicto actualizado

El paper ya esta mucho mas cerca de envio. No veo bloqueantes tecnicos de LaTeX,
citas o coherencia interna que impidan generar el PDF. Aun asi, antes de enviarlo
manana hay cuatro confirmaciones humanas que no se deben saltar.

Nota actual: 8.4/10.

Nota si se confirman los cuatro pendientes humanos: 8.7/10.

## Checks ejecutados

- `latexmk -pdf -shell-escape -interaction=nonstopmode main.tex`: OK.
- `bash ../docs/paper-workbench/check_paper.sh` desde `paper/`: OK.
- `python3 ../docs/paper-workbench/audit_paper.py` desde `paper/`: OK.

Metricas finales del auditor:

- Abstract: 182 palabras.
- Bibliografia: 36 entradas.
- Citas indefinidas: 0.
- Referencias indefinidas: 0.
- Overfull hbox: 0.
- Figuras: 7.
- Tablas: 8.
- Placeholders ORCID `0000-0000`: 0.
- Claims sensibles antiguos eliminados: `six composite modes`, `CHANGE and STATE queues`.

## Cambios aplicados

1. Abstract reducido y hecho mas ajustado a MDPI.
   - Pasa de 239 a 182 palabras.
   - Mantiene metricas clave: 38.8% CPU, 10.1% RAM, <5 ms, 520 ms recovery.

2. Eliminados placeholders ORCID comentados.
   - Ya no aparece `0000-0000`.

3. Corregida la descripcion de previews y puertos de `voctogui`.
   - Fuentes preview: 14000-14005.
   - Mix preview: 12000.
   - Programme output: 15000.

4. Corregido el claim de modos compuestos.
   - Ahora dice cuatro modos primarios de operador + variantes internas/mirror.
   - La tabla funcional ya no dice "6 modes".

5. Corregida la descripcion/caption de RabbitMQ.
   - `CHANGE` y `STATE` se describen como tipos de evento.
   - La figura se describe como colas consumidoras CyberNEMO.

6. Anadida tabla de metodologia de medicion.
   - CPU/RAM: `analyze_cameras.py`.
   - RAPL: `rapl_scraper.py`.
   - Latencia: `measure_latency.py`.
   - Transiciones: `composite_latency_*.json`.
   - Resiliencia: `measure_resilience.py`.

7. Anadida tabla de resumen de latencia.
   - Source switch Docker/K8s.
   - Composite transition Docker/K8s.
   - Incluye n, mediana, p95 y maximo.

8. Documentado el outlier de RAPL Kubernetes.
   - La tabla marca el rango K8s con nota.
   - Explica la exclusion del sample de 36.1 W por artefacto de baseline.

9. Corregida Data Availability.
   - Ya no afirma que los raw logs sean publicos si no esta garantizado.
   - Codigo y scripts publicos; logs brutos bajo peticion razonable.

10. Mejorado back matter.
   - Author contributions incluye a A.d.R.P. y D.J.B. en review/editing y supervision.
   - Conflict of interest incluye el rol/no rol de los financiadores.

11. Preparada carta de presentacion.
   - Archivo: `paper/cover_letter.md`.
   - Incluye declaraciones obligatorias de originalidad y aprobacion de autores.

12. Maquetacion corregida.
   - Diagrama TikZ escalado al ancho de texto.
   - Tablas reducidas con `\small`.
   - Overfull hbox final: 0.

## Pendientes humanos antes de enviar

1. Consentimiento/copyright de figuras CyberNEMO.
   - `paper/figures/cybernemo_operator.png` muestra personas identificables.
   - Confirmar permiso escrito o sustituir/anonymizar la figura.

2. Author Contributions.
   - He incluido a Alberto y David en Writing-review/editing y Supervision para
     evitar incumplimiento formal, pero hay que confirmar que refleja sus roles reales.

3. APC funding.
   - El funding declara CyberNEMO, pero no dice quien paga el APC.
   - Confirmar con el tutor si hay que anadir: "The APC was funded by ...".

4. ORCID reales.
   - No hay placeholders, pero si algun autor tiene ORCID conviene anadirlo.

## Valoracion estricta final

Lo mejor:

- El paper ya tiene una contribucion clara, medible y reproducible.
- La narrativa esta mejor alineada con el proyecto real y con el codigo.
- Las afirmaciones tecnicas delicadas ahora estan mejor respaldadas por tablas.
- La compilacion esta limpia para referencias/citas y sin overfulls.

Lo todavia mejorable:

- Ocho tablas es algo denso. No lo veo bloqueante para MDPI, pero visualmente es
  mas "engineering report" que paper compacto.
- La bibliografia tiene buen numero, pero algunas referencias son webs/producto.
  Si hubiera mas tiempo, anadiria 3-5 referencias academicas extra.
- La captura CyberNEMO sigue siendo el mayor riesgo no tecnico.
- Seria mejor publicar raw logs en Zenodo/GitHub y no "available on request".

## Fuentes externas usadas como criterio

- MDPI Electronics Instructions for Authors:
  https://www.mdpi.com/journal/electronics/instructions
- MDPI Electronics Aims & Scope:
  https://www.mdpi.com/journal/electronics/about
- MDPI Author Layout Style:
  https://www.mdpi.com/authors/layout
- MDPI Reference List and Citations:
  https://www.mdpi.com/authors/references
- OBS official site:
  https://obsproject.com/
- OBS Remote Control Guide:
  https://obsproject.com/kb/remote-control-guide
- vMix official purchase/comparison:
  https://www.vmix.com/purchase/
- Blackmagic ATEM Mini official product page:
  https://www.blackmagicdesign.com/products/atemmini

