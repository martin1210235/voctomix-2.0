# Actualización de resultados experimentales

**Fecha de ejecución:** 16 de julio de 2026
**Equipo de pruebas:** Intel Core i9-10900X (10 núcleos / 20 hilos, 3,70 GHz, TDP 165 W), 128 GB DDR4, Ubuntu 22.04.5 LTS (kernel 6.8.0-124)
**Software:** Docker Engine 29.1.3, Docker Compose 2.37.1, Minikube v1.38.1, kubectl v1.36.0, GStreamer 1.20, Python 3.10.14

## 1. Objetivo

El objetivo de esta sesión era repetir, en el equipo de referencia (i9-10900X, 128 GB), las mediciones de consumo de recursos y de recuperación ante fallos ya descritas en el capítulo de resultados, para comprobar que las cifras que se están usando en la memoria y en el paper corresponden efectivamente a dicho equipo.

## 2. Procedimiento

Se lanzaron dos scripts sobre el equipo de referencia: `experiments/run_rapl_repeat.sh`, que recoge muestras de CPU y RAM en reposo y bajo carga tanto en Docker Compose como en Kubernetes, y `tools/measure_resilience.py --n 10`, que mide el tiempo que tarda `voctocore` en recuperarse tras la terminación forzosa del contenedor de la cámara principal en Docker Compose.

## 3. Resultados

### 3.1 Consumo de CPU y RAM en reposo

Se tomaron veintiuna muestras con `voctocore` en ejecución pero sin ninguna fuente de vídeo activa.

| Métrica | Mínimo | Mediana | Media | Desviación típica | P95 |
|---|---|---|---|---|---|
| CPU (%) | 0,80 | 3,60 | 6,87 | 7,59 | 16,40 |
| RAM (%) | 5,80 | 6,60 | 9,76 | 4,74 | 16,60 |

Conviene aclarar que estas cifras son de reposo y no sustituyen a las medidas bajo carga activa (cuatro cámaras simultáneas) que ya aparecen en el capítulo de resultados; esa prueba concreta no se llegó a repetir en esta sesión.

### 3.2 Recuperación ante fallos en Docker Compose

Se completaron diez ciclos de terminación forzosa y recuperación del contenedor de la cámara principal.

| Métrica | Mínimo | Mediana | Media | Desviación típica | P95 |
|---|---|---|---|---|---|
| Tiempo de recuperación (ms) | 517 | 527 | 525,7 | 5,0 | 532,1 |

Las diez iteraciones se completaron sin fallos ni reintentos.

## 4. Conclusiones

El tiempo de recuperación en Docker Compose (mediana de 527 ms) es coherente con el orden de magnitud que ya se venía manejando en la memoria, así que confirma la resiliencia del despliegue en este equipo concreto. El consumo de CPU y RAM en reposo también resulta bajo y estable, sin picos anómalos entre muestras.

## 5. Mediciones pendientes

Quedan por hacer varias mediciones que no dio tiempo a completar en esta sesión. Se han organizado por prioridad, pensando en qué necesita el paper primero.

**Consumo de CPU y RAM bajo carga activa.** Es la más urgente, porque las cifras que hoy aparecen en el capítulo de resultados (con las cuatro cámaras funcionando a la vez, en Docker y en Kubernetes) todavía no se han vuelto a comprobar en este equipo. Para repetirla hace falta ejecutar `experiments/run_rapl_repeat.sh` completando las cuatro sesiones de carga, de N=1 a N=4, en los dos entornos y sin interrupciones, y luego analizar los ficheros resultantes con `experiments/analyze_cameras.py`. Sería buena idea aprovechar y registrar también, en paralelo, el consumo de CPU del propio proceso de `voctocore` por separado, por ejemplo con `pidstat`, para poder distinguir su huella real de la del resto de procesos del sistema.

**Recuperación ante fallos en Kubernetes.** El ciclo de `tools/measure_resilience_k8s.py --n 10 --wait 720` no se llegó a terminar en Kubernetes. Hay que tener en cuenta que dura unas dos horas, porque entre cada una de las diez iteraciones hace falta esperar doce minutos para que Kubernetes reinicie su contador interno de reinicios; conviene reservar ese tiempo sin interrupciones antes de lanzarlo.

**Consumo energético real.** Los contadores RAPL no se pudieron leer porque el fichero `/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj` solo es accesible con permisos de superusuario. Habría que repetir la sesión con `sudo`, o dando esos permisos al proceso de medición, para tener lecturas de potencia reales en vez de la estimación indirecta que se usó como respaldo.

**Latencia de conmutación entre fuentes.** Tampoco se ha comprobado en este equipo. Se mide con `experiments/measure_latency.py`, que envía treinta comandos `set_video_a` por el canal de control TCP y cronometra hasta que llega la confirmación `video_status`; habría que correrlo tanto en Docker como en Kubernetes.

**Latencia de las transiciones de composición.** De forma parecida, `tools/measure_composite_latency.py` envía comandos `transition` (pantalla completa, side-by-side, picture-in-picture, lower-third) y mide el tiempo hasta la confirmación `composite`. Igual que el punto anterior, falta repetirla en los dos entornos de despliegue.

**Estabilidad a largo plazo.** La prueba original duraba solo 31 minutos, y ese tiempo es demasiado corto para sacar conclusiones firmes sobre fugas de memoria: una fuga lenta, de unas pocas decenas de kilobytes por minuto, no se distinguiría del ruido normal de medición en media hora, pero sí se acumularía lo suficiente como para verse con claridad a lo largo de 24 horas. Además, 24 horas se corresponde con un caso de uso realista (una jornada completa de retransmisión) y es la duración que se suele usar en este tipo de pruebas de estabilidad prolongada. Si el calendario lo permite, alargarla hasta 48 horas dejaría la conclusión todavía más asentada. El procedimiento sería mantener el sistema en marcha de forma continua bajo carga activa, capturando la telemetría de estado sin interrupción, y analizar después la sesión con `tools/analyze_stability.py`.

**Contador de fotogramas perdidos.** Esta es la única medición que no se puede hacer solo con un script; requiere tocar código. Ahora mismo no hay forma de comprobar de manera directa que no se pierden fotogramas durante la mezcla, así que habría que instrumentar `voctocore/lib/videomix.py` para contar los fotogramas de entrada y de salida de cada fuente, y calcular la tasa de pérdida como la diferencia relativa entre ambos contadores durante una sesión con carga activa. Es la medición más completa de las que quedan pendientes, pero también la que más tiempo llevaría implementar.
