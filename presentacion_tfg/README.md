# Presentación TFG — Voctomix 2.0

Defensa del Trabajo Fin de Grado (ETSIT-UPM). Presentación en Beamer con tema
`metropolis` e identidad corporativa UPM/ETSIT.

## Estructura

- `presentacion.tex` — fichero principal de la presentación.
- `figuras/` — diagramas, gráficas y logos (reutilizar los de la memoria/paper).

## Compilación

Recomendado (tipografía Fira del tema metropolis):

```bash
latexmk -xelatex presentacion.tex
```

Alternativa (sin Fira, pero compila igual):

```bash
pdflatex presentacion.tex
```

## Pendiente

- Descargar la plantilla oficial ETSIT (`https://www.upm.es/gsfs/SFS17721`),
  extraer el **logo ETSIT** a `figuras/logo_etsit.png` y el **hex azul oficial**.
- Sustituir el color `UPMblue` aproximado por el hex corporativo exacto.
- Insertar el diagrama de arquitectura y las gráficas de resultados (cap5).
- Iterar el diseño con las presentaciones de referencia.

## Entregable PowerPoint (formato oficial ETSIT)

- `presentacion_voctomix_etsit.pptx` — deck en la **plantilla oficial ETSIT**
  (`SFS17721.pptx`): master, layouts, colores (azul `08447C`, cian `2899F9`) y
  tipografía Arial oficiales.
- `build_pptx.py` — genera el `.pptx` con `python-pptx` sobre la plantilla
  oficial. Reejecutar tras cualquier cambio de contenido.
- 15 diapositivas para una defensa de ~12-13 min, con
  **contenido adicional** para preguntas. La diapositiva de **vídeo demostrativo**
  vertebra la parte de implementación.

## Requisitos del acto de defensa (ETSIT-UPM)

- Exposición oral: **15 min**. Turno de preguntas: **5 min**.
- Se presenta en pantalla de sala; llevar portátil propio con salida HDMI.
- Tribunal de 3 miembros. Acto público.
- Plantilla oficial de diapositivas: `SFS17721.pptx`.
