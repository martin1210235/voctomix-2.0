# DOC_PATTERNS — patrones de documentación de repos top

Base de conocimiento viva sobre cómo documentan los proyectos open-source de
referencia. Objetivo: que la documentación de Voctomix 2.0 sea "top top".
Iniciado 2026-06-27.

## Marco de organización: Diátaxis (el estándar que siguen los grandes)

Fuente: https://diataxis.fr/ — usado por Django, NumPy, Gatsby, Cloudflare…
Divide TODA la documentación en cuatro tipos según la necesidad del usuario:

| Tipo | Orientado a | Responde a | En Voctomix |
|---|---|---|---|
| **Tutorial** | aprender | "llévame de la mano la 1ª vez" | Quick Start del README + DEPLOYMENT por escenario |
| **How-to guide** | resolver tarea | "cómo hago X" | "cómo añadir una cámara", "cómo grabar el programa" |
| **Reference** | consultar dato | "cuál es el comando/puerto exacto" | CONTROL_PROTOCOL.md, CONFIGURATION.md, tabla de puertos |
| **Explanation** | entender | "por qué está diseñado así" | ARCHITECTURE.md, TELEMETRY.md |

Regla de oro: **no mezclar tipos en el mismo documento**. Un usuario que busca un
comando (reference) no quiere un tutorial, y viceversa. Nuestra `docs/` ya
separa reference (protocolo, config) de explanation (arquitectura, telemetría).

## README como escaparate (FastAPI, 80k+ estrellas)

Fuente: github.com/fastapi/fastapi — README considerado ejemplar.

Patrones a imitar:
1. **Logo + tagline centrados** arriba del todo.
2. **Badges inmediatamente** (build, cobertura, versión, licencia) = señales de
   confianza/mantenimiento. ⇒ ACCIÓN: añadir badges a nuestro README.
3. **Enlaces a docs y código** justo bajo los badges.
4. **Lista de features con cabecera en negrita** + descripción corta, cada una
   apuntando a un público distinto.
5. **Ejemplos de código progresivos**: del más simple al más complejo, paso a
   paso (curva de aprendizaje). ⇒ Nuestro equivalente: comandos del protocolo
   de control de menos a más.
6. **Mostrar, no contar**: capturas (Swagger UI). ⇒ Nosotros: captura de
   voctogui + gif de un corte de cámara.
7. **Prueba social**: quién lo usa (Netflix, Uber…). ⇒ Nuestro equivalente:
   "usado en el proyecto europeo CyberNEMO en la UPM".

## README de dominio (OBS Studio, broadcast)

Fuente: github.com/obsproject/obs-studio — mismo dominio (vídeo en directo).

Patrones:
1. **Badges de cabecera** (build, traducción, Discord/comunidad).
2. **"What is OBS Studio?"** = frase de propósito directa.
3. **"Quick Links"** = hub de navegación (docs, foros, wiki). ⇒ ACCIÓN: añadir
   sección Quick Links a nuestro README.
4. **Building/instalación enlaza a wiki** en vez de meterlo todo en el README
   (mantiene el README corto). ⇒ Patrón: README corto + `docs/` profundo.
5. **Contributing exhaustivo**: financiación, código + guía de estilo,
   traducciones, código de conducta, soporte comunitario.
6. **Licencia explícita** con fichero COPYING.

## Plantilla canónica de README (readmine + best practices)

Fuentes: github.com/mhucka/readmine, freecodecamp, dev.to.

Orden recomendado de secciones:
1. Título + descripción (las 2 primeras líneas responden: ¿qué es? ¿por qué me
   importa?)
2. Badges
3. Tabla de contenidos (si es largo)
4. **Highlights/Features** (lo más importante arriba; lista con viñetas)
5. Installation (prerequisitos + pasos copy-paste, subsecciones por SO)
6. Quick start (ejemplo mínimo funcional)
7. Usage (básico y avanzado; enlazar a docs para lo complejo)
8. Known issues / limitations
9. Getting help / support
10. Contributing
11. License
12. Acknowledgments / Citation (badge DOI para citar académicamente)

## Checklist de mejoras para NUESTRO repo

- [x] Árbol `docs/` separado por tipo (reference vs explanation). Hecho.
- [ ] Añadir **badges** al README (licencia, lenguaje, estado).
- [ ] Añadir **Quick Links** (docs, issues, licencia) al README.
- [ ] Corregir "tres escenarios" → **cuatro** en el README.
- [ ] Añadir `CONTRIBUTING.md`, `CHANGELOG.md`, `.env.example` en la raíz.
- [ ] Completar `docs/`: DEPLOYMENT, CONFIGURATION, TROUBLESHOOTING.
- [ ] Añadir un **gif/captura** (mostrar, no contar) — pendiente de material.
- [ ] Prueba social: destacar CyberNEMO/UPM en el README.
- [ ] (Futuro) badge DOI (Zenodo) para que el repo sea citable desde el paper.

## Cómo esto ayuda al PAPER

- El `dataavailability` del paper exige un repo público y creíble: estos
  patrones (badges, docs/, CONTRIBUTING, licencia) son justo lo que un revisor
  mira al verificar "código disponible".
- Un badge DOI de Zenodo permite **citar el propio software** en el paper.
