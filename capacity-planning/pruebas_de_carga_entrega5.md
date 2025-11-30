# Pruebas de carga capa web

## Escenario 1 - Sanidad (Smoke):

Para este escenario inicial de sanidad, configuramos JMeter con 5 hilos (usuarios concurrentes), un periodo de ramp-up de 5 segundos y una duración total de 60 segundos. Esta configuración nos permite validar que todo el sistema responde correctamente y que la telemetría está funcionando antes de proceder con pruebas más intensivas.

La configuración de la petición incluye el endpoint de login con parámetros URL encoded para username y password, realizando una petición POST al DNS público del Application Load Balancer (ALB) que distribuye el tráfico entre las instancias EC2 del grupo de Auto Scaling donde se encuentra desplegada la aplicación.

<img alt="java_F1daE78feS" src="https://github.com/user-attachments/assets/7a2bd856-f0e2-4ac0-b752-a26876ba49d8" />

Configuración de la petición:

<img alt="java_HrkLbhf6KN" src="https://github.com/user-attachments/assets/7d94f89f-739c-4f80-a8be-6cbd37ef6e56" />

---

### Resultados del Test de Sanidad:

Los resultados muestran que todas las peticiones fueron exitosas, lo cual es un excelente indicador de que el sistema está funcionando correctamente bajo carga básica.

**Summary Report:**
- **208 samples** procesados exitosamente
- **Tiempo promedio de respuesta:** 1,413 ms
- **Tiempo mínimo:** 433 ms
- **Tiempo máximo:** 4,380 ms
- **0% de errores** - todas las peticiones fueron exitosas
- **Throughput:** 3.4 requests/segundo

<img alt="java_82Yube57PO" src="https://github.com/user-attachments/assets/e09f52c4-b092-4af0-9029-6314cc7daea9" />

<img alt="java_ucSYkoJoJs" src="https://github.com/user-attachments/assets/af47183e-243b-475d-897f-401133fa2100" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 1,617 ms
- **95% de las respuestas:** ≤ 1,711 ms  
- **99% de las respuestas:** ≤ 2,468 ms

<img alt="java_lhOjiiQml4" src="https://github.com/user-attachments/assets/bcde8fe3-3a61-4004-a3e5-93f81af53e82" />

**Análisis de Tiempo de Respuesta:**
El gráfico de tiempo de respuesta muestra un comportamiento bastante estable, con un pequeño pico que supera los 1,700 milisegundos, pero la mayoría de las respuestas se mantienen por debajo de este umbral. Esto indica que el sistema maneja bien la carga básica de 5 usuarios concurrentes.

<img alt="java_wNYcK1Tmix" src="https://github.com/user-attachments/assets/2254d754-ba61-4d76-8ad3-19ef91857c05" />

**Monitoreo de Recursos del Sistema:**
El monitoreo se realizó a través de Amazon CloudWatch, el servicio nativo de observabilidad de AWS. En esta ocasión, en lugar de usar el script local calculate-stats dentro del contenedor, se aprovecharon las métricas agregadas de las instancias EC2 pertenecientes al grupo de Auto Scaling donde se encuentra desplegada la capa web.

Los resultados muestran un uso máximo de CPU del 35 %, lo cual representa un comportamiento saludable y evidencia que el sistema tiene amplio margen de capacidad disponible bajo la carga básica de cinco usuarios concurrentes.

<img alt="image" src="https://github.com/user-attachments/assets/f399daa3-6904-4ee4-8758-ccb32c6f63a2" />

---

## Escenario 1 - Escalamiento rápido (Ramp) X = 100:

Para este escenario de escalamiento rápido, aumentamos significativamente la carga para determinar el punto donde el sistema comienza a mostrar signos de degradación. Configuramos JMeter para escalar desde 0 hasta 100 usuarios concurrentes en 3 minutos, manteniendo esta carga durante 5 minutos adicionales.

### Resultados del Test con 100 Usuarios Concurrentes:

<img alt="java_YRlmVYzzXV" src="https://github.com/user-attachments/assets/edfa4837-5a16-4929-8058-c1af9b4db3dd" />

**Summary Report:**
- **1,787 samples** procesados
- **Tiempo promedio de respuesta:** 22,657 ms
- **Tiempo mínimo:** 426 ms
- **Tiempo máximo:** 33,340 ms
- **0% de errores** - todas las peticiones fueron exitosas
- **Throughput:** se mantiene estable
- **Mediana:** 27,824 ms

<img alt="java_rIlqStSM9R" src="https://github.com/user-attachments/assets/c5a9f33f-8826-4805-bc02-60c6b748618f" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 28,583 ms
- **95% de las respuestas:** ≤ 29,801 ms
- **99% de las respuestas:** ≤ 30,439 ms

<img alt="java_MhuykOY2p1" src="https://github.com/user-attachments/assets/b7de3550-209e-43af-8069-6fe4f5e2f306" />

**Análisis de Tiempo de Respuesta:**
El gráfico muestra que los tiempos de respuesta aumentan significativamente a aproximadamente 30,000 milisegundos (30 segundos), lo cual indica que el sistema está comenzando a experimentar estrés bajo esta carga. Aunque no hay errores, la degradación en el rendimiento es evidente.

<img alt="java_vSceHSQpGY" src="https://github.com/user-attachments/assets/ba84b8ea-7af8-4fc6-9d4a-ce99dded4d51" />

**Monitoreo de Recursos del Sistema:**
El análisis de recursos, monitoreado a través de Amazon CloudWatch, muestra un uso máximo de CPU del 49.8 % en la instancia que ejecuta la capa web. Este valor es particularmente interesante, ya que el umbral de autoescalado se configuró precisamente en el 50 % de utilización, por lo que el sistema no alcanzó a disparar la creación de una nueva instancia.

El gráfico de métricas confirma que el CPU se mantuvo estable justo por debajo del umbral durante toda la ejecución, sin superar el 50 %. Este comportamiento sugiere que la capacidad actual del sistema fue suficiente para manejar la carga del escenario sin requerir escalado adicional, demostrando una distribución eficiente del tráfico a través del ALB.

Además, el uso de memoria y red se mantuvo dentro de rangos normales, sin signos de saturación. En conjunto, las métricas reflejan que la infraestructura está correctamente dimensionada para este nivel de demanda, aunque cualquier incremento leve en la carga habría activado el mecanismo de Auto Scaling, añadiendo una nueva instancia para mantener el rendimiento estable.

<img alt="image" src="https://github.com/user-attachments/assets/4b19cd6a-74d4-4f93-9d39-66669dff0963" />

---

## Escenario 1 - Sostenida corta (300 * 0.8 = 240):

Para el escenario de sostenida corta, utilizamos el 80% de la carga máxima que no presentó errores (300 usuarios) de la Entrega 2 (recordemos que en esta entrega no hubo errores), es decir, 240 usuarios concurrentes. Este test nos permite confirmar la estabilidad del sistema bajo una carga sostenida.

### Resultados del Test de Sostenida Corta con 240 Usuarios:

**Summary Report:**
- **2,780 samples** procesados
- **Tiempo promedio de respuesta:** 26,519 ms (vs 59,747 ms Entrega 2)
- **Tiempo mínimo:** 405 ms
- **Tiempo máximo:** 36,291 ms
- **0% de errores** - todas las peticiones fueron exitosas
- **Throughput:** 8.3 requests/segundo (vs 3.8 requests/segundo Entrega 2)
- **Mediana:** 34,116 ms

<img alt="java_tE0NZXX8tf" src="https://github.com/user-attachments/assets/6d5991ef-0e90-436b-b40b-8a6a108fea8f" />

**Monitoreo de Recursos del Sistema:**
En este escenario también se monitoreó la instancia desde CloudWatch y se observó un comportamiento similar al de los escenarios anteriores: la CPU no llega a los valores críticos que veíamos cuando todo el tráfico se atendía desde una sola instancia o desde un solo contenedor. La política de autoescalado con umbral bajo (35%) permitió que la infraestructura estuviera lista para escalar.

<img alt="image" src="https://github.com/user-attachments/assets/5968d78b-186b-4d60-a5e6-fa89ce7178ee" />

---

## Conclusiones del Escenario 1 - Capacidad de la Capa Web:

### Capacidad Máxima Identificada:
Basándonos en los resultados de las pruebas, podemos concluir que:

- **Capacidad máxima sin errores:** 300 usuarios concurrentes
- **Punto de degradación:** Entre 300 y 500 usuarios concurrentes

### Análisis de SLOs:
- **p95 de endpoints:** En el escenario de 300 usuarios, el p95 fue de 49,197 ms, lo que aún excede el SLO establecido de ≤ 1 segundo, pero representa una mejora significativa respecto a la entrega anterior (92,577 ms). La optimización en la distribución de carga mediante el Application Load Balancer (ALB) y la configuración de autoescalado más reactiva permitió reducir los tiempos de respuesta en más de un 45 %, manteniendo la estabilidad bajo carga elevada.

- **Errores:** El sistema mantuvo 0 % de errores incluso en el escenario de 500 usuarios concurrentes, lo que demuestra que la arquitectura actual logra sostener una carga mucho mayor sin degradar la disponibilidad.

- **Bottleneck identificado** En esta entrega, el cuello de botella ya no se encuentra en la CPU de una única instancia, sino en la latencia de respuesta agregada del balanceador y en los tiempos de activación del autoescalado, factores que dependen de la configuración del ALB y de la política de escalamiento. La CPU de las instancias se mantuvo por debajo del 50 %, indicando una capacidad ociosa saludable y margen para admitir más tráfico si se ajustan los umbrales de escalado.

### Recomendaciones:
1. **Escalado horizontal:** Implementar múltiples instancias del API para distribuir la carga (ya se evidenció en esta entrega que mejora los tiempos).
2. **Optimización de CPU:** Revisar y optimizar el código para reducir el uso de CPU en escenarios de carga alta.
3. **Monitoreo proactivo:** Establecer alertas cuando el CPU supere el 35% (de acuerdo con la política nueva) para escalar automáticamente.
4. **Capacidad recomendada:** Para producción (con esta configuración), no exceder 240–300 usuarios concurrentes a menos que se tenga garantizado el escalado automático y la instancia nueva alcance estado healthy a tiempo.

### Consideraciones adicionales de esta entrega:
- El ALB tiene varias configuraciones que afectan directamente la prueba de carga (health check interval, timeout, unhealthy threshold, connection idle timeout). Ajustarlas permitió que las nuevas instancias empezaran a recibir tráfico sin causar errores 5xx durante el escalamiento.
- La métrica personalizada en CloudWatch fue necesaria porque la política por defecto de AWS (3 minutos para escalar) era demasiado lenta para nuestro escenario de pruebas con JMeter, donde la carga sube en cuestión de segundos.
- Aunque la carga fue alta, la CPU de las instancias no superó el 50%, por lo que se decidió trabajar con umbrales más bajos (35% máx., 10% mín.) para evitar que el autoscaling se quedara esperando a que la instancia estuviera ya saturada.

# Pruebas de carga capa worker

Recepción de 5 mensajes
<img width="1920" height="864" alt="SQS_recibido_5" src="https://github.com/user-attachments/assets/543c1cdc-808a-4a7f-87d1-7970771fe620" />

## Escenario 2 50Mb - 1 Worker - 5 Tasks

Actualizamos el script `send_message_to_broker.py` para que tome videos previamente subidos a S3 y registrados en RDS. El script busca los videos por su ID en la base de datos (video ID 54 para 50MB) y genera mensajes con `task_id` únicos que enviamos directamente a la cola SQS. 

**Alarma CloudWatch:**

Configuramos la política de autoescalado del worker para usar la métrica `ApproximateNumberOfVisibleMessages` de SQS, con un umbral de 5 mensajes visibles para activar el escalado. Sin embargo, durante la prueba observamos que la alarma no se activó y el sistema se mantuvo en 1 instancia durante todo el procesamiento.

Esto ocurre porque cuando inyectamos 5 mensajes en la cola, el worker inmediatamente toma uno para procesarlo, dejando 4 mensajes visibles. Como el umbral está en 5, la condición nunca se cumple. El worker procesa los mensajes lo suficientemente rápido como para mantener la cola por debajo del umbral.

<img alt="image" src="https://github.com/user-attachments/assets/964650af-33c1-4d23-ab81-87b769d7ea92" />

**Métrica de procesamiento:**

La métrica `FFmpegProcessingTime` registró un promedio de **47 segundos** por video. Este tiempo incluye todas las operaciones de FFmpeg: creación del intro con logo, recorte y codificación del video principal, generación del outro, y concatenación final de todos los segmentos. Este comportamiento es consistente con entregas anteriores, donde FFmpeg se identifica como la fase más costosa del pipeline.

Comparado con las otras fases, el tiempo de FFmpeg domina completamente el tiempo total. Las operaciones de descarga desde S3, consulta a la base de datos y actualización de registros consumen tiempos mínimos (menos de 1 segundo cada una), confirmando que el cuello de botella principal está en la codificación y procesamiento de video, no en I/O o acceso a datos. Los 47 segundos de `FFmpegProcessingTime` representan aproximadamente el 98% del tiempo total de procesamiento.

<img alt="chrome_F9RrgpGKCu" src="https://github.com/user-attachments/assets/69038f63-6e5a-44c8-84e1-81ec3786b3df" />

**Uso de recursos de la instancia worker:**

El monitoreo de CloudWatch muestra un uso de CPU del **28.8%** durante el procesamiento de videos de 50MB. Aunque moderado, refleja que el procesamiento de video es intensivo en CPU, pero la instancia aún tiene capacidad disponible. El hecho de que la CPU no alcance niveles críticos (por encima del 85%) indica que, para este tamaño de archivo y nivel de paralelismo, la instancia tiene margen para manejar más carga.

<img width="1918" height="865" alt="CPU" src="https://github.com/user-attachments/assets/53665af0-b526-4507-b618-16fd28b1fa3b" />

## Escenario 2 100Mb - 1 Worker - 5 Tasks

Repetimos la misma metodología de inyección de carga, pero utilizando videos de 100MB (video ID 44 en la base de datos). El objetivo era evaluar cómo el aumento en el tamaño del archivo impacta el tiempo de procesamiento y el consumo de recursos, manteniendo la misma configuración de 1 worker y 5 tareas.

<img alt="chrome_Ml9oJlY3Ua" src="https://github.com/user-attachments/assets/320cf8a8-ac7a-4823-ace1-d53d5fd34e9a" />
<img alt="chrome_8onkKUbKQp" src="https://github.com/user-attachments/assets/c47ef014-3a8e-4ef4-806c-9c9a0e6a4724" />

**Alarma CloudWatch:**

Al igual que en el escenario de 50MB, la alarma de autoescalado no se activó y el sistema se mantuvo en 1 instancia durante todo el procesamiento. El mismo patrón se repite: el worker consume mensajes lo suficientemente rápido como para mantener la cola por debajo del umbral de 5 mensajes visibles, aunque en este caso el tiempo de procesamiento es más largo. Para cargas pequeñas (5 tareas), el worker puede mantener el ritmo independientemente del tamaño del archivo, pero el throughput se degrada significativamente con archivos más grandes.

<img width="1918" height="860" alt="Alarma" src="https://github.com/user-attachments/assets/8d324174-ea72-49b8-8e56-af2398b12b69" />

**Métrica de procesamiento:**

La métrica `FFmpegProcessingTime` para videos de 100MB registró un promedio de **102 segundos**, más del doble del tiempo observado para videos de 50MB (47 segundos). Esta relación no es exactamente lineal, ya que el tiempo de procesamiento no solo depende del tamaño del archivo, sino también de la complejidad de las operaciones de codificación, la duración del video original, y la cantidad de datos que FFmpeg debe procesar durante la transcodificación.

Al igual que en el escenario de 50MB, el tiempo de procesamiento con FFmpeg sigue siendo dominante sobre las demás fases. Las operaciones de descarga desde S3, consultas a la base de datos y actualizaciones continúan siendo despreciables en comparación, confirmando que el cuello de botella se mantiene en la capa de procesamiento de video, independientemente del tamaño del archivo.

<img width="1920" height="863" alt="CloudWatch" src="https://github.com/user-attachments/assets/b796203e-e213-4ac6-8ed4-d904185db60e" />

**Uso de recursos de la instancia worker:**

El uso de CPU aumentó a **33.8%** durante el procesamiento de videos de 100MB, un incremento del 5% respecto al escenario de 50MB. Este aumento es proporcional al mayor tiempo de procesamiento y al volumen de datos que deben ser procesados, pero aún se mantiene en un rango moderado que indica que la instancia tiene capacidad disponible. Sin embargo, el tiempo de procesamiento por video (102 segundos) es significativamente mayor, lo que impacta directamente el throughput del sistema: mientras que con videos de 50MB podemos procesar aproximadamente 1.3 videos por minuto, con videos de 100MB el throughput cae a aproximadamente 0.6 videos por minuto.

La comparación entre ambos escenarios revela que el tamaño del archivo tiene un impacto directo y significativo en el tiempo de procesamiento, pero no necesariamente en el uso de CPU de forma proporcional. Mientras que el tiempo de procesamiento se duplicó (de 47s a 102s), el uso de CPU solo aumentó en un 17% (de 28.8% a 33.8%). Esto indica que el procesamiento de video, aunque intensivo en CPU, también está limitado por otros factores como el ancho de banda de I/O del disco temporal, la velocidad de lectura/escritura durante la codificación, y posiblemente la memoria disponible para buffers de FFmpeg.

<img width="1918" height="860" alt="CPU" src="https://github.com/user-attachments/assets/a5b702e6-b0db-4f23-8db1-f2551a422ee2" />

**Autoescalado:**

No hubo escalamiento. Se procesó todo en 1 sola instancia worker, ya que la cola nunca alcanzó el umbral de 5 mensajes visibles configurado en la política de autoescalado.

<img alt="chrome_hcwiGtb5pF" src="https://github.com/user-attachments/assets/9ee8cd4e-2b2f-4fc5-acf8-6f9b54f2ec9d" />


## Conclusiones del Escenario 2 - Capacidad de la Capa Worker:

### Capacidad Máxima Identificada:

Basándonos en los resultados de las pruebas, podemos concluir que:

- **Capacidad con 1 worker:** 
  - Videos de 50MB: ~1.2 videos/minuto (tiempo promedio: 49.14s por video)
  - Videos de 100MB: ~0.6 videos/minuto (tiempo promedio: ~106s por video)
  
- **Capacidad con 3 workers (autoescalado):**
  - Videos de 50MB: ~1.2 videos/minuto El sistema escala correctamente cuando la cola supera 5 mensajes visibles, distribuyendo la carga entre múltiples instancias. (tiempo promedio: 48.68s - 50.32s por video)
  - Videos de 100MB: ~0.6 videos/minuto Comportamiento similar, pero con mayor tiempo de procesamiento por video. (tiempo promedio: 106.09s - 107.15s por video)

### Comportamiento del Autoescalado:

El autoescalado funciona correctamente cuando la carga supera la capacidad de una sola instancia. Con 16 tareas, la métrica `ApproximateNumberOfVisibleMessages` alcanzó 14 mensajes visibles, activando el Policy Up y escalando de 1 a 3 instancias. Sin embargo, con cargas pequeñas (5 tareas), el worker puede mantener el ritmo y la cola nunca alcanza el umbral de 5 mensajes, por lo que no se activa el escalado.

### Uso de Recursos:

El uso de CPU se mantiene en rangos moderados incluso con múltiples instancias:
- **1 worker, 50MB:** 28.8% CPU
- **1 worker, 100MB:** 33.8% CPU
- **3 workers, 50MB:** 29.4% CPU (en una instancia)
- **3 workers, 100MB:** 35.2% CPU (en una instancia)

Estos valores indican que las instancias tienen capacidad disponible y que el escalado horizontal distribuye eficientemente la carga sin saturar ninguna instancia individual.

### Cuello de Botella Identificado:

El análisis confirma que el cuello de botella principal está en el procesamiento con FFmpeg, que representa aproximadamente el 98% del tiempo total de procesamiento. Las operaciones de descarga desde S3, consultas a la base de datos y actualizaciones consumen tiempos mínimos (menos de 1.5 segundos en total), por lo que cualquier optimización debe enfocarse en la capa de procesamiento de video.

### Limitaciones y Consideraciones:

1. **Procesamiento secuencial:** Cada worker procesa videos de forma secuencial, uno tras otro, sin paralelismo dentro de la misma instancia.

2. **Impacto del tamaño de archivo:** El tamaño del archivo tiene un impacto directo y significativo en el tiempo de procesamiento, duplicando aproximadamente el tiempo cuando se duplica el tamaño.

3. **Throughput limitado:** Con la configuración actual, el throughput máximo es de aproximadamente 1.2 videos/minuto para archivos de 50MB y 0.6 videos/minuto para archivos de 100MB por instancia worker.

4. **Escalado horizontal efectivo:** El autoescalado funciona correctamente para distribuir la carga entre múltiples instancias, mejorando el throughput total del sistema cuando hay suficiente carga en la cola.
