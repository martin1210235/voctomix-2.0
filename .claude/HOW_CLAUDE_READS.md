# HOW_CLAUDE_READS.md — Cómo Claude Accede a la Información del Proyecto

Explicación de cómo Claude Code automáticamente accede, lee y actualiza los ficheros de documentación del proyecto.

---

## 🔄 Sistema de Archivos (Hay Dos Niveles)

### Nivel 1: Archivos en la Raíz del Proyecto (Visibles para ti)

Estos archivos están en `/home/sonda/Documentos/voctomix/` y **tú puedes verlos, editarlos y compartirlos**:

- **CLAUDE.md** — Reglas de proyecto (comandos, arquitectura, normas de código)
- **MEMORY.md** — Contexto persistente (puertos, estructura TFG, módulos clave)
- **users.md** — Tu perfil como usuario (preferencias de trabajo, habilidades técnicas)
- **GLOSSARY.md** — Glosario técnico (AFV, compositor, stream-blanker, etc.)
- **TROUBLESHOOTING.md** — Problemas conocidos y soluciones
- **HOW_CLAUDE_READS.md** — Este fichero (documentación del sistema)

**Acceso:** Claude lee estos archivos automáticamente al inicio de cada sesión, extrayendo información crítica para entender el proyecto y cómo trabajar contigo.

---

### Nivel 2: Archivos en el Sistema de Memoria Persistente (Uso Interno de Claude)

Estos archivos están en `/home/sonda/.claude/projects/-home-sonda-Documentos-voctomix/memory/` y **son gestionados automáticamente por Claude**:

- **MEMORY.md** (índice) — Punteros a los archivos de memoria
- **user_profile.md** — Tu perfil (se sincroniza con users.md del proyecto)
- **project_tfg.md** — Contexto del TFG (se sincroniza con MEMORY.md del proyecto)

**Acceso:** Claude accede a estos automáticamente. Los consulta para recordar contexto de sesiones anteriores.

---

## 📖 Flujo de Lectura Automática

### Al iniciar una sesión de Claude Code:

1. **Claude busca CLAUDE.md** en la raíz del proyecto
2. **Lee la sección "Reference Files"** → identifica qué archivos .md debe consultar
3. **Carga MEMORY.md, users.md, GLOSSARY.md, TROUBLESHOOTING.md** en su contexto
4. **También consulta el sistema de memoria persistente** (user_profile.md, project_tfg.md)
5. **Combina toda esta información** para entender:
   - El proyecto (Voctomix 2.0, arquitectura, puertos)
   - Tus preferencias (cómo trabajar contigo, autonomía, idiomas)
   - Problemas conocidos (soluciones rápidas)
   - Terminología consistente (AFV, compositor, etc.)

### Resultado: 
Claude entra cada sesión sabiendo:
- ✅ Cómo ejecutar, testear y deployar el proyecto
- ✅ Tu rol, nivel técnico y preferencias de trabajo
- ✅ Qué hacer si algo falla (troubleshooting)
- ✅ Cómo hablar sobre el proyecto (glosario consistente)

---

## ✏️ Cuándo y Cómo Claude Actualiza los Archivos

### MEMORY.md — Actualización automática por Claude

**Cuándo:** Cuando descubre información nueva sobre el proyecto que no estaba documentada.

**Ejemplos:**
- Descubre un nuevo puerto que no está en la tabla
- Identifica un módulo clave no documentado
- Tutor aprueba un cambio en la estructura del TFG
- Cambia la versión de GStreamer y las instrucciones

**Cómo:** Claude edita directamente `MEMORY.md` sin pedir permiso (es documentación, no código).

**Ejemplo:**
```markdown
# Antes (MEMORY.md)
| Puerto | Servicio |
|--------|---------|
| 9999 | Control TCP |

# Después (Claude actualiza automáticamente)
| Puerto | Servicio |
|--------|---------|
| 9999 | Control TCP |
| 9998 | UDP GStreamer clock |  ← Nuevo descubrimiento
```

---

### users.md — Actualización automática por Claude

**Cuándo:** Cuando descubre una nueva preferencia tuya o cambios en cómo trabajas juntos.

**Ejemplos:**
- Observa que prefieres respuestas más largas y detalladas
- Notas que tienes dificultad con un tema específico (necesita explicación más lenta)
- Tu nivel técnico crece o cambia de foco
- Cambias de idioma de preferencia para ciertos contextos

**Cómo:** Claude edita directamente `users.md` sin pedir permiso.

**Ejemplo:**
```markdown
# Antes (users.md)
| Kubernetes | Working knowledge |

# Después (Claude observa y actualiza)
| Kubernetes | Proficient |  ← Tras resolver varios problemas K8s
```

---

### GLOSSARY.md — Actualización automática por Claude

**Cuándo:** Cuando descubre términos nuevos que necesitan definición o encuentra inconsistencias terminológicas.

**Ejemplos:**
- Introduces un nuevo módulo (p.ej., "rotulación_dinamica_v2")
- Descubre que un término causa confusión
- Se añade una nueva característica con su propio vocabulario

**Cómo:** Claude edita GLOSSARY.md sin pedir permiso.

---

### TROUBLESHOOTING.md — Actualización automática por Claude

**Cuándo:** Cuando durante una sesión de trabajo:
- Encuentro un problema que antes no estaba documentado
- Resuelvo un bug recurrente con una solución clara
- Identifico un patrón de error que se repite

**Ejemplos:**
```bash
# Mientras trabajamos:
# Problema: "Error: 'videomixer' no encontrado"
# Solución: "Instalar gstreamer1.0-plugins-good"
# → Claude lo añade automáticamente a TROUBLESHOOTING.md
```

**Cómo:** Claude edita TROUBLESHOOTING.md sin pedir permiso, preservando todas las soluciones anteriores.

---

## 🔐 Privacidad y Control

### Qué CAN'T cambiar Claude:

- ❌ **CLAUDE.md** — Tus reglas de proyecto (cambios solo si tú lo autorizas)
- ❌ **Código fuente** (voctocore/, voctogui/, etc.) — Solo si lo pides
- ❌ **LaTeX/tesis** — Solo si lo solicitas explícitamente

### Qué SÍ puede cambiar Claude libremente:

- ✅ **MEMORY.md** — Información del proyecto
- ✅ **users.md** — Tu perfil observado
- ✅ **GLOSSARY.md** — Terminología
- ✅ **TROUBLESHOOTING.md** — Soluciones de problemas
- ✅ **HOW_CLAUDE_READS.md** — Este fichero (documentación del sistema)

**Principio:** Archivos de referencia/documentación → Claude puede editarlos libremente. Código + reglas → requieren autorización.

---

## 📝 Qué Esperar en Cada Sesión

### Primera sesión (ya hecha):
```
✅ CLAUDE.md creado con reglas del proyecto
✅ MEMORY.md creado con contexto completo
✅ users.md creado con tu perfil
✅ GLOSSARY.md creado con terminología
✅ TROUBLESHOOTING.md creado con soluciones
✅ Sistema de memoria persistente activado
```

### Sesiones posteriores:
```
1. Claude carga CLAUDE.md → extrae "Reference Files"
2. Lee todos los .md en paralelo
3. También carga la memoria persistente (/home/sonda/.claude/projects/...)
4. Entra con contexto completo: proyecto + tus preferencias + problemas conocidos
5. Durante la sesión:
   - Descubre algo nuevo → lo añade a MEMORY.md/GLOSSARY.md/TROUBLESHOOTING.md
   - Observa preferencia nueva → la añade a users.md
   - Resuelve un problema recurrente → lo documenta en TROUBLESHOOTING.md
6. Al terminar: todos los .md están actualizados para la próxima sesión
```

---

## 🎯 Ventajas de Este Sistema

| Ventaja | Cómo funciona |
|---------|---------------|
| **Continuidad sin perder contexto** | Cada sesión hereda todo lo aprendido anteriormente |
| **Documentación siempre actualizada** | Los cambios se registran automáticamente |
| **Soluciones rápidas a problemas recurrentes** | TROUBLESHOOTING.md evita repetir el mismo trabajo |
| **Terminología consistente** | GLOSSARY.md asegura que hablamos el mismo idioma |
| **Personalización del servicio** | users.md me enseña cómo trabajar mejor contigo |
| **Autonomía máxima** | Claude puede actualizar docs sin esperar aprobación |
| **Auditoría visible** | Todos los cambios están en ficheros de texto plano (puedes verlos en git) |

---

## ⚙️ Cómo Verificar que Todo Funciona

### Verificación manual:

```bash
# 1. Confirma que los archivos existen:
ls -la CLAUDE.md MEMORY.md users.md GLOSSARY.md TROUBLESHOOTING.md

# 2. Verifica la carpeta de memoria persistente:
ls -la ~/.claude/projects/-home-sonda-Documentos-voctomix/memory/

# 3. Monitorea cambios:
git status  # debería mostrar cambios en los .md
git log --oneline MEMORY.md  # histórico de actualizaciones

# 4. Test: provoca un error y comprueba que aparece en TROUBLESHOOTING.md
./voctocore/test.sh  # simula un problema
# → Claude debería documentarlo automáticamente
```

---

## 🔔 Si Algo No Funciona

**Claude no lee los archivos:** Verifica que CLAUDE.md existe y tiene la sección "Reference Files".

**MEMORY.md no se actualiza:** Posible que Claude esté siendo demasiado conservador. Puedes decirle: "Actualiza MEMORY.md con..." y lo hará inmediatamente.

**Información desincronizada:** Si la memoria persistente y los .md del proyecto divergen, di: "Sincroniza todos los .md con la memoria persistente".

---

## 📌 Resumen: Tú + Claude + Documentación Viva

- **Tú editas:** CLAUDE.md (reglas), código, tesis
- **Claude edita automáticamente:** MEMORY.md, users.md, GLOSSARY.md, TROUBLESHOOTING.md
- **Resultado:** Un proyecto donde la documentación es tan viva como el código, adaptándose con cada sesión
