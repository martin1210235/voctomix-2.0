> Sincronizado con GUION_Presentacion_Voctomix.docx (2026-07-10).

# Guion de defensa — Voctomix 2.0 (~15 min)

> Guion diapositiva por diapositiva. Cabeceras compactas «N)» para leer de un vistazo mientras se presenta.

## Bloque 1

### 1) Portada

> Buenos días. Soy Martín Herranz y presento mi Trabajo Fin de Grado: «Desarrollo y optimización de un sistema modular de código abierto para la producción remota de vídeo en tiempo real», desarrollado en el marco de la Cátedra RTVE en la ETSIT. La idea es convertir un mezclador de vídeo en una plataforma completa y validada para realizar en directo de forma remota.

### 2) Índice

> El índice está dividido en seis bloques: primero la introducción; después la arquitectura, la implementación, a continuación los escenarios de despliegue y los resultados medidos; y finalmente las conclusiones.

### 3) INTRODUCCIÓN

> Empecemos por el contexto: cómo se produce vídeo en directo.

### 4) Producción tradicional

> La producción en directo ha dependido siempre de infraestructura física muy cara: un mezclador hardware dedicado, tipo ATEM o Ross, cableado SDI, y todo el equipo desplazado al evento. Por ejemplo, retransmitir un partido de LaLiga en España moviliza decenas de cámaras, unidades móviles y personal. Un modelo sólido, pero inaccesible para universidades o eventos medianos.

### 5) Producción remota (REMI)

> Para resolverlo surge la producción remota, el modelo REMI: la realización se centraliza y en el evento solo queda la captura. Herramientas software como OBS o vMix abren este modelo, pero siguen atadas al escritorio: no están pensados para operar en servidor, ni en multioperador, ni en contenedores.

### 6) Evolución de la producción

> Así, la producción evoluciona en tres etapas: de lo tradicional, caro y presencial, a lo remoto, y de ahí a un modelo virtualizado: un mezclador libre, que puede ejecutarse en un servidor, multioperador y en contenedores. Ese último paso es donde se sitúa mi trabajo.

### 7) Objetivos

> En concreto, seis objetivos: funcionalidades profesionales, un servicio de telemetría, contenerizar con Docker, desplegar en Kubernetes, validarlo en varios escenarios y probarlo en un entorno real. Todo ello en línea con los ODS 9, 4 y 10.

### 8) Cadena de producción

> Antes de entrar en el sistema, situémoslo en la cadena. La señal va de las cámaras (la contribución, por SDI o IP), pasa por el mezclador de vídeo, se codifica y se distribuye al espectador por RTMP o HLS. Mi trabajo se centra en ese mezclador.

### 9) Casos de uso

> Y esto no es teoría: la producción remota ya se usa a gran escala, en los Juegos de Tokio, en LaLiga con SRT, o en proyectos europeos como NEMO y CyberNEMO, con la UPM. Precisamente en CyberNEMO ya se había trabajado con una versión previa de este mezclador, el Voctomix original. Y este Trabajo Fin de Grado es su continuación directa: la versión 2.0, más completa, que es la que voy a presentar.

### 10) ARQUITECTURA

> Vista la introducción, pasamos a cómo está construido el sistema.

### 11) Dos módulos: voctocore + voctogui

> Voctomix 2.0 se divide en dos módulos. Por un lado, voctocore, el núcleo: recibe las fuentes, mezcla el vídeo, gestiona el audio y genera la señal de programa. Por otro, voctogui, la interfaz gráfica del realizador. Ambos se comunican por TCP, lo que separa el control del procesamiento. Y esa separación es la clave: permite controlar la interfaz de forma remota mientras el motor se ejecuta en un servidor, sin necesidad de pantalla.

### 12) Arquitectura del sistema

> Este es el diagrama completo con los puertos. A la izquierda, las fuentes de entrada llegan por los puertos 10000 a 10005, junto con las del stream blanker. Todo pasa por el voctocore, que mezcla audio y vídeo, aplica overlays y rotulación, y genera la salida. Por un lado: la mezcla en bruto en el puerto 11000, para la monitorización por parte del realizador, y la señal de programa en el 15000, que es la que llega al espectador. Y en paralelo, voctogui controla el núcleo por TCP, mientras la telemetría se publica hacia RabbitMQ mediante AMQP.

### 13) IMPLEMENTACIÓN

> Vista la arquitectura, pasamos a lo que he implementado.

### 14) Módulos clave

**Cinco módulos principales:**

- Los modos de composición, para cambiar el diseño de pantalla.

- El stream blanker, que controla si la emisión está en directo, en pausa o cortada.

- Los overlays y rótulos sobre el vídeo.

- Audio Follows Video, que automatiza el audio según la cámara activa.

- La telemetría, que publica el estado en tiempo real.

> Ahora lo veréis todo funcionando.

### 15) Demostración en vídeo

**Presentación:**

> A la izquierda, la mesa del realizador, con las cuatro cámaras arriba y el panel de control abajo. Arriba a la derecha, lo que ve el espectador. Y abajo a la derecha, la telemetría en vivo. Reproduzco.

**Narración sobre el vídeo:**

> En primer lugar, se puede observar cómo el realizador puede cambiar entre cámaras mediante el corte clásico, o cut. Por ejemplo, podemos pasar de la cámara 1 a la cámara 2, después a la cámara 3 o incluso a la cámara 4, manteniendo el modo de pantalla completa.

> En la parte inferior derecha se muestra la telemetría, que se va actualizando en tiempo real. Por un lado, aparecen eventos de tipo change, que se generan cada vez que se produce un cambio en la realización. Por otro lado, aparecen eventos de tipo state, que se actualizan periódicamente cada cinco segundos para informar del estado general del sistema.

> También se han incorporado los botones de break e intro. El botón de break lanza un vídeo en bucle, pensado para pausas o descansos en retransmisiones largas. El botón de intro reproduce un vídeo pregrabado desde el momento en que lo pulsa el realizador, con un pequeño retardo de un segundo, y está pensado para presentaciones o introducciones de programa.

> A la derecha se encuentran los modos de composición. Además del modo full screen, se incluye side by side, que muestra dos fuentes una al lado de la otra; picture in picture, con una fuente principal y otra en pequeño; y lecture, pensado para conferencias o presentaciones. También se ha añadido la función mirror, que permite invertir el orden de las cámaras y facilita el trabajo del realizador.

> En cuanto al estado de emisión, el modo live indica que el espectador final está viendo la retransmisión en directo. En cambio, con no stream o con el botón de pausa, el espectador ve un vídeo pregrabado en bucle con música de fondo.

> Además del botón de corte clásico, se ha incorporado el botón retake, que permite volver al estado anterior si el realizador se equivoca, y un botón de transición suave entre cámaras.

> En la sección de overlays, se han añadido dos logotipos, situados en la parte superior e inferior derecha, y un rótulo superpuesto sobre la señal emitida. Además, se han incorporado dos textos dinámicos, que permiten al realizador escribir mensajes personalizados durante la retransmisión.

> También se incluye la opción auto off, que, cuando está activada, desactiva automáticamente los overlays y los textos dinámicos al cambiar de cámara. Esto permite una realización más ágil y evita que elementos gráficos permanezcan en pantalla por error.

> Por último, el botón update permite actualizar dinámicamente los overlays disponibles sin necesidad de cortar la retransmisión. Y, en la parte izquierda, aparecen los vúmetros de cada cámara, que permiten ajustar el nivel de audio de cada señal de previsualización. Además, el sistema conserva el último nivel de audio seleccionado, de forma que los cambios realizados por el realizador se mantienen durante la sesión.

### 16) ESCENARIOS DE DESPLIEGUE

> Este sistema lo he desplegado y validado en cuatro escenarios, de lo más simple a lo más orquestado.

### 17) Escenario 1: Un PC

> Empecé en un único PC: el escenario de desarrollo, donde además di forma al estilo y al aspecto visual de la interfaz gráfica. Es el más simple, y permite validar la funcionalidad básica sin depender de la red.

### 18) Escenario 2: Dos PCs

> El segundo separa servidor y operador: voctocore en un equipo y la interfaz en otro, por LAN. Aquí aparece ya la producción remota real: el realizador no está en la máquina que procesa la señal.

### 19) Escenario 3: Docker Compose

> El tercero es Docker Compose: el sistema pasa a once contenedores que arrancan con un solo comando. Las cámaras comparten la red del núcleo, así que se comunican por localhost sin sobrecarga. Aquí entra la telemetría a RabbitMQ. El objetivo es la reproducibilidad: el mismo sistema en cualquier máquina.

### 20) Escenario 4: Kubernetes

> Y el cuarto, Kubernetes, el objetivo final: CyberNEMO se prueba sobre un clúster de Kubernetes, así que lo natural era llevarlo ahí. El mismo sistema, ahora orquestado con manifiestos declarativos, escala sin tocar el código.

### 21) RESULTADOS

> Vistos los escenarios, paso a los resultados medidos.

### 22) Consumo de recursos

> Medí CPU, RAM y energía según el número de cámaras. Lo importante: en Docker con cuatro cámaras, el sistema usa un 38,8 % de CPU y un 10 % de RAM. Es decir, queda margen para más. En Kubernetes el consumo es mayor debido al overhead de Minikube, que ejecuta el plano de control en la misma máquina.

> Conclusión: consumo bajo y estable, con margen de sobra.

### 23) Latencia

> La latencia crítica en directo es el cambio de cámara: mediana de 1,5 milisegundos en Docker y 1,8 en Kubernetes. Muy por debajo del umbral perceptible por el ser humano, unos 45 milisegundos, así que el corte se percibe instantáneo.

> La transición de modo de composición sube algo en Kubernetes, otra vez por Minikube, pero no afecta al corte de cámara.

> En resumen: los cambios son imperceptibles en directo.

### 24) Fiabilidad

**Dos pruebas de fiabilidad:**

> La estabilidad: media hora funcionando sin crecimiento de CPU ni fugas de memoria, en Docker y en Kubernetes.

> Y la resiliencia: forcé la caída de una cámara y el sistema se recupera solo en torno a medio segundo, sin tocar nada. Conclusión: robusto en los escenarios validados.

### 25) CONCLUSIONES

> Y termino con las conclusiones.

### 26) Conclusiones

> Los seis objetivos se cumplen: funcionalidades profesionales, servicio de telemetría, contenerización con Docker, despliegue en Kubernetes, validación en múltiples escenarios y, por último, la validación en un entorno europeo real, CyberNEMO.

### 27) Líneas futuras

> De las limitaciones surgen las líneas futuras: validar con cámaras físicas reales, pasar a H.265 para reducir ancho de banda, subir a 4K, permitir reconfiguración dinámica desde la interfaz, y ampliar las métricas con pruebas más largas y redes más exigentes.

### 28) Impacto y méritos

> Y el trabajo no se queda en la memoria: se ha probado en CyberNEMO, se ha preparado un artículo científico, y todo el código está publicado como software libre en GitHub. Para mí, eso es lo importante: el proyecto tiene continuidad y utilidad más allá de la defensa.

### 29) Gracias

> Muchas gracias por su atención. Quedo a disposición del tribunal para responder a sus preguntas.


---
## Resumen de tiempos

> Apertura 1:00 · Introducción 2:45 · Arquitectura 1:45 · Implementación 5:00 (incluye el vídeo ~3:46) · Escenarios 1:45 · Resultados 2:05 · Cierre 1:45 → ≈ 15:30
