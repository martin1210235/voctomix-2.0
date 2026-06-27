# DATA_CONSISTENCY — paper ↔ TFG ↔ datos crudos

Fuente única de verdad para cada cifra del paper. Antes de enviar el paper,
TODA cifra de `main.tex` debe coincidir con la columna "TFG (medido)" o
justificarse explícitamente. Generado 2026-06-27.

> ✅ **ALINEADO (2026-06-27).** Todas las cifras cuantitativas de `main.tex` se
> han ajustado a los datos medidos del TFG (cap5) y verificado con compilación
> (19 págs, 0 citas sin resolver). Esta tabla queda como registro de auditoría;
> la columna "Acción" refleja lo ya aplicado. Pendiente solo: confirmar conteo
> de validación funcional y hardware en la tabla de escenarios.

## 0. Decisión de fondo pendiente (BLOQUEANTE)

El TFG midió rendimiento en **2 entornos** (Docker Compose y Kubernetes/Minikube),
no en 4. El paper presenta una tabla de **4 escenarios** (Single-PC, Two-PC,
Docker, K8s) con cifras de CPU/RAM que no existen en el TFG para Single-PC ni
Two-PC. Opciones:
- **(Recomendada)** Reescribir Results del paper para reportar solo Docker vs
  Kubernetes con los números reales del TFG, y describir Single-PC/Two-PC como
  escenarios de despliegue (cualitativos), no como puntos de medida.
- O bien medir realmente Single-PC y Two-PC (no hay datos; supondría nueva
  campaña experimental).

## 1. Tabla de consistencia

| Métrica | PAPER (main.tex actual) | TFG (medido, cap5) | Fuente cruda | Acción |
|---|---|---|---|---|
| Formato interno vídeo | UYVY 4:2:2, 16-bit (L.410-411) | **I420** | `voctocore/default-config.ini:2` | **Corregir paper a I420** |
| Ancho banda / fuente | 829 Mbps | **622 Mbps** | I420 = 1.5 B/px ⇒ 1920·1080·1.5·25 | **Corregir** |
| Ancho banda 4 fuentes | 3.32 Gbps | **2.49 Gbps** | cap5/5_3:152-154 | **Corregir** |
| Entornos medidos | 4 (Single,Two,Docker,K8s) | **2 (Docker, K8s)** | cap5/5_3 | **Reestructurar** |
| CPU @4 cám Docker | 44 % | **38.8 %** | cap5/5_3:31,43 | **Corregir** |
| CPU @4 cám K8s | 47 % | **51.2 %** | cap5/5_3:35 | **Corregir** |
| CPU Single-PC / Two-PC | 38 % / 40 % | (no medido) | — | **Eliminar o medir** |
| RAM @4 cám Docker | 12 % | **10.1 %** | cap5/5_3:78 | **Corregir** |
| RAM @4 cám K8s | 13 % | **13.4 %** | cap5/5_3:82 | Ajustar |
| Latencia conmutación (mediana) | 22 ms | **1.5 ms Docker / 1.8 ms K8s** | cap5/5_3:213 | **Corregir (gran divergencia)** |
| Latencia conmutación (n) | n=20 | **n=30** | cap5/5_3:178 | **Corregir** |
| Latencia conmutación (cota) | <40 ms; sobre WiFi 5 GHz | **<5 ms; cableado, sin codificación** | cap5/5_3:212 | **Corregir (no fue WiFi)** |
| Umbral de referencia | "100–150 ms percepción humana" | **45 ms, ITU-R BT.1359-1** | cap5/5_3:214-215 | **Sustituir por la cita ITU-R real** |
| Latencia transición composición | (ausente) | Docker 2.8 ms / K8s 79.8 ms (n=32) | cap5/5_3:262-264 | **Añadir (resultado fuerte)** |
| Energía (RAPL) | (ausente) | Docker 25–32 W / K8s 25–27 W neto | cap5/5_3:130-141 | Considerar añadir |
| Estabilidad 31 min | (ausente) | sin fuga; CPU 49–58 % Docker / 54–60 % K8s; RAM plana | cap5/5_5:81-96 | Considerar añadir |
| Resiliencia cam1 (recuperación) | (ausente) | Docker 520 ms (n=10) / K8s 570 ms (n=10, +10 %) | cap5/5_5:171-176 | **Añadir (diferencial)** |
| Validación funcional | "9 categorías × 4 escenarios = 36" | revisar contra cap5/5_2 | cap5/5_2 | Verificar conteo |
| Hardware de prueba | i7-8750H, 16 GB | verificar contra cap5/5_1 | cap5/5_1 | Verificar |

## 2. Citas

| Tema | Paper | Estado |
|---|---|---|
| Telefónica / REMI | `tsa_laliga_srt_2025` (Appear/LaLiga, Madrid) | ✅ Corregido 2026-06-27 (antes `tsa_remi_2022` Bernabéu, no verificable) |
| Umbral audio/vídeo | usar `itur_bt1359_1998` como en TFG | ⛔ Pendiente: el paper aún no cita ITU-R BT.1359-1 |

## 3. Notas

- El umbral correcto es **45 ms (ITU-R BT.1359-1)**, no "una trama de 40 ms" ni
  "100–150 ms de percepción humana". Unifica el discurso del paper con el TFG.
- `dataavailability` apunta a `github.com/martin1210235/voctomix-2.0`: verificar
  que el repositorio existe y es público antes del envío.

---

## Ficheros relacionados (mapa)

- Hub / estado → [PAPER_STATUS.md](PAPER_STATUS.md)
- Reglas de revisión → [PAPER_REVIEW_CHECKLIST.md](PAPER_REVIEW_CHECKLIST.md)
- Guardián que vigila estas cifras → [check_paper.sh](check_paper.sh) (guard §3)
