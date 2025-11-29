# Pruebas de carga capa web

## Escenario 1 - Sanidad (Smoke):

Para este escenario inicial de sanidad, configuramos JMeter con 5 hilos (usuarios concurrentes), un periodo de ramp-up de 5 segundos y una duración total de 60 segundos. Esta configuración nos permite validar que todo el sistema responde correctamente y que la telemetría está funcionando antes de proceder con pruebas más intensivas.

La configuración de la petición incluye el endpoint de login con parámetros URL encoded para username y password, realizando una petición POST al DNS público del Application Load Balancer (ALB) que distribuye el tráfico entre las instancias EC2 del grupo de Auto Scaling donde se encuentra desplegada la aplicación.

<img width="1519" height="856" alt="java_GLTQw7kwge" src="https://github.com/user-attachments/assets/5bdb580a-83ad-4bff-a666-e49b65cb069e" />

Configuración de la petición:

<img width="1519" height="856" alt="java_9TiwWWu65a" src="https://github.com/user-attachments/assets/de358d32-885f-40ff-b6bf-f92720e53929" />

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

<img width="1519" height="856" alt="java_QME7Z4XvN6" src="https://github.com/user-attachments/assets/824edb86-e7e6-4408-b4b1-3f1b6a5a920d" />

<img width="1519" height="856" alt="java_luNTl2Op3k" src="https://github.com/user-attachments/assets/4adc34c1-761a-4aef-9088-f6c5af82edb2" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 1,617 ms
- **95% de las respuestas:** ≤ 1,711 ms  
- **99% de las respuestas:** ≤ 2,468 ms

<img width="1519" height="856" alt="java_Lf3vsRDZGB" src="https://github.com/user-attachments/assets/151da9c8-743e-47fb-b153-d54f044e0aaa" />

**Análisis de Tiempo de Respuesta:**
El gráfico de tiempo de respuesta muestra un comportamiento bastante estable, con un pequeño pico que supera los 1,700 milisegundos, pero la mayoría de las respuestas se mantienen por debajo de este umbral. Esto indica que el sistema maneja bien la carga básica de 5 usuarios concurrentes.

<img width="1519" height="856" alt="java_kEMqX6ccL5" src="https://github.com/user-attachments/assets/9ab25a2d-69f1-4e7e-8e6a-e66166997485" />

**Monitoreo de Recursos del Sistema:**
El monitoreo se realizó a través de Amazon CloudWatch, el servicio nativo de observabilidad de AWS. En esta ocasión, en lugar de usar el script local calculate-stats dentro del contenedor, se aprovecharon las métricas agregadas de las instancias EC2 pertenecientes al grupo de Auto Scaling donde se encuentra desplegada la capa web.

Los resultados muestran un uso máximo de CPU del 35 %, lo cual representa un comportamiento saludable y evidencia que el sistema tiene amplio margen de capacidad disponible bajo la carga básica de cinco usuarios concurrentes.

<img alt="image" src="https://github.com/user-attachments/assets/f399daa3-6904-4ee4-8758-ccb32c6f63a2" />

---

## Escenario 1 - Escalamiento rápido (Ramp) X = 100:

Para este escenario de escalamiento rápido, aumentamos significativamente la carga para determinar el punto donde el sistema comienza a mostrar signos de degradación. Configuramos JMeter para escalar desde 0 hasta 100 usuarios concurrentes en 3 minutos, manteniendo esta carga durante 5 minutos adicionales.

### Resultados del Test con 100 Usuarios Concurrentes:

**Summary Report:**
- **1,787 samples** procesados
- **Tiempo promedio de respuesta:** 22,657 ms
- **Tiempo mínimo:** 426 ms
- **Tiempo máximo:** 33,340 ms
- **0% de errores** - todas las peticiones fueron exitosas
- **Throughput:** se mantiene estable
- **Mediana:** 27,824 ms

<img width="1519" height="856" alt="java_zh5W8gvrAN" src="https://github.com/user-attachments/assets/79cd7fbc-bf88-4943-8b21-6661333e3fe5" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 28,583 ms
- **95% de las respuestas:** ≤ 29,801 ms
- **99% de las respuestas:** ≤ 30,439 ms

<img width="1519" height="856" alt="java_ibsQTXP2QU" src="https://github.com/user-attachments/assets/00780ba4-fd30-4c4a-99da-c13ada9535f5" />

**Análisis de Tiempo de Respuesta:**
El gráfico muestra que los tiempos de respuesta aumentan significativamente a aproximadamente 30,000 milisegundos (30 segundos), lo cual indica que el sistema está comenzando a experimentar estrés bajo esta carga. Aunque no hay errores, la degradación en el rendimiento es evidente.

<img width="1519" height="856" alt="java_JPoXx9Ma2Q" src="https://github.com/user-attachments/assets/c4a01b21-d788-452a-a3e2-8d85f8611d6a" />

**Monitoreo de Recursos del Sistema:**
El análisis de recursos, monitoreado a través de Amazon CloudWatch, muestra un uso máximo de CPU del 49.8 % en la instancia que ejecuta la capa web. Este valor es particularmente interesante, ya que el umbral de autoescalado se configuró precisamente en el 50 % de utilización, por lo que el sistema no alcanzó a disparar la creación de una nueva instancia.

El gráfico de métricas confirma que el CPU se mantuvo estable justo por debajo del umbral durante toda la ejecución, sin superar el 50 %. Este comportamiento sugiere que la capacidad actual del sistema fue suficiente para manejar la carga del escenario sin requerir escalado adicional, demostrando una distribución eficiente del tráfico a través del ALB.

Además, el uso de memoria y red se mantuvo dentro de rangos normales, sin signos de saturación. En conjunto, las métricas reflejan que la infraestructura está correctamente dimensionada para este nivel de demanda, aunque cualquier incremento leve en la carga habría activado el mecanismo de Auto Scaling, añadiendo una nueva instancia para mantener el rendimiento estable.

<img width="1920" height="912" alt="image" src="https://github.com/user-attachments/assets/af658afe-6f01-41bc-ad3c-e77d3cfcbb0c" />

---

## Escenario 1 - Escalamiento rápido (Ramp) X = 300:

Continuamos con el escalamiento, aumentando la carga a 300 usuarios concurrentes para identificar más claramente los límites del sistema.

### Resultados del Test con 300 Usuarios Concurrentes:

**Summary Report:**
- **4,535 samples** procesados
- **Tiempo promedio de respuesta:** 27,031 (vs 68,657 ms Entrega 2)
- **Tiempo mínimo:** 408 ms
- **Tiempo máximo:** 51,539 ms (vs 93,516 ms Entrega 2)
- **0% de errores** - todas las peticiones fueron exitosas
- **Throughput:** 8.6 requests/segundo (vs 3.3 requests/segundo Entrega 2)
- **Mediana:** 22,901 ms (vs 87,646 ms Entrega 2)

<img width="1497" height="857" alt="image" src="https://github.com/user-attachments/assets/8d8763b3-c7f2-4c47-9d7c-2ab9fa3d63c9" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 48,357 (vs 90,761 ms Entrega 2)
- **95% de las respuestas:** ≤ 49,197 (vs 92,577 ms Entrega 2)
- **99% de las respuestas:** ≤ 50,952 ms (vs 93,230 ms Entrega 2)

<img width="1497" height="857" alt="image" src="https://github.com/user-attachments/assets/72e46faa-ec49-4275-999a-59475b81b6cf" />

**Análisis de Tiempo de Respuesta:**
El gráfico de tiempo de respuesta muestra que efectivamente los tiempos suben a aproximadamente 42,000 milisegundos (42 segundos) después de los 3 minutos de rampa. Esta degradación significativa indica que el sistema está operando muy cerca de sus límites máximos.

Sin embargo, a diferencia de la Entrega 2, en esta ocasión se contó con el Application Load Balancer (ALB) y con una configuración de autoescalado más agresiva, lo que permitió que el tráfico se distribuyera mejor entre las instancias y que los tiempos de respuesta se redujeran de manera importante (de 68 s a ~27 s en promedio). También se ajustaron parámetros del ALB como el health check y el connection idle timeout, de forma que las nuevas instancias comenzaran a recibir tráfico solo cuando estuvieran en estado healthy, evitando tiempos muertos durante el escalado.

<img width="1497" height="857" alt="image" src="https://github.com/user-attachments/assets/dd279e42-aa56-4ec6-814f-3505befb11ca" />

**Monitoreo de Recursos del Sistema:**

<img width="1918" height="887" alt="image" src="https://github.com/user-attachments/assets/4f7e59ee-0028-4087-bd94-8f46263087b9" />

A partir de este comportamiento se decidió **bajar los umbrales de la política de autoescalado** y trabajar con un máximo de **35% de CPU** y un mínimo de **10%**, ya que en nuestro contexto de prueba las cargas eran conocidas y era preferible anticipar el escalado antes de que la instancia se saturara.

---

## Escenario 1 - Escalamiento rápido (Ramp) X = 500:

En este escenario crítico, aumentamos la carga a 500 usuarios concurrentes.

### Resultados del Test con 500 Usuarios Concurrentes:

**Summary Report:**
- **4,687 samples** procesados
- **Tiempo promedio de respuesta:** 45,326 ms (vs 107,183 ms Entrega 2)
- **Tiempo mínimo:** 430 ms
- **Tiempo máximo:** 78,324 ms (vs 344,100 ms Entrega 2)
- **0.00% de errores** - En este escenario, en la entrega anterior ya se presentaban errores.
- **Throughput:** 8.5 requests/segundo (vs 3.4 Entrega 2)
- **Mediana:** 59,638 ms (vs 139,466 ms Entrega 2)

<img width="1497" height="857" alt="image" src="https://github.com/user-attachments/assets/2aebf1ce-62e1-4405-a968-3f2d3aac5eea" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 74,428 ms (vs 146,951 ms Entrega 2)
- **95% de las respuestas:** ≤ 74,973 ms (vs 147,586 ms Entrega 2)
- **99% de las respuestas:** ≤ 76,754 ms (vs 147,863 ms Entrega 2)

<img width="1497" height="857" alt="image" src="https://github.com/user-attachments/assets/fde28c55-e9fa-4887-a118-1a01a28c1e76" />

**Análisis de Tiempo de Respuesta:**
El gráfico muestra tiempos de respuesta promedio de aproximadamente 72,000 milisegundos (72 segundos). Aunque siguen siendo tiempos elevados, es evidente la mejora frente a la entrega anterior, en la que ya empezábamos a ver errores y tiempos máximos por encima de los 300,000 ms.

Esta mejora no solo se debe al ALB, sino también a que se creó una métrica personalizada en CloudWatch para monitorear más de cerca el comportamiento de la carga y no depender únicamente de la política por defecto de AWS, la cual espera 3 minutos para escalar y 15 minutos para desescalar. En nuestros escenarios de laboratorio, esperar 3 minutos implicaba que cuando la instancia nueva llegaba, la anterior ya estaba muy cercana a la saturación. Con la métrica personalizada y umbrales más bajos, logramos que el escalado fuera más oportuno y que el balanceador pudiera redirigir tráfico a una instancia nueva apenas estuviera healthy.

<img width="1497" height="857" alt="image" src="https://github.com/user-attachments/assets/aae13d8d-9038-410a-b26b-d5b57f570ba9" />

**Monitoreo de Recursos del Sistema:**
Las métricas de CloudWatch para este escenario muestran que, incluso con 500 usuarios, la CPU de la instancia no supera el 50%. Esto es un comportamiento muy distinto al de la Entrega 2, donde el contenedor `storeapi` se mantenía al 100% e incluso llegaba a picos de 120% o 140%. La diferencia ahora es que la carga está siendo distribuida por el ALB y que la instancia no está procesando todo el tráfico de forma directa.

<img width="1920" height="912" alt="image" src="https://github.com/user-attachments/assets/571fed7e-ef0a-4dfe-8c4a-89ad06601764" />

Para evitar que el autoscaling estuviera encendiendo y apagando instancias constantemente cuando la carga bajaba, se dejó un rango operativo entre 10% y 35% de CPU, que se adapta mejor al patrón de carga usado en las pruebas.

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

<img width="1497" height="857" alt="image" src="https://github.com/user-attachments/assets/162b44d0-0304-4b09-a2cf-1366d2eea39a" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 35,494 ms (vs 71,299 ms Entrega 2)
- **95% de las respuestas:** ≤ 35,711 ms (vs 72,284 ms Entrega 2)
- **99% de las respuestas:** ≤ 36,077 ms (vs 72,911 ms Entrega 2)

<img width="1497" height="857" alt="image" src="https://github.com/user-attachments/assets/132a6b10-24b9-4583-9842-a8bef9dd843d" />

**Análisis de Tiempo de Respuesta:**
El gráfico muestra tiempos de respuesta promedio de aproximadamente 35,000 milisegundos (35 segundos), pero con un comportamiento estable. El sistema mantiene la estabilidad sin errores bajo esta carga sostenida.

<img width="1497" height="857" alt="image" src="https://github.com/user-attachments/assets/e90e07e2-078a-4769-aa7c-a43d7fdb4e12" />

**Monitoreo de Recursos del Sistema:**
En este escenario también se monitoreó la instancia desde CloudWatch y se observó un comportamiento similar al de los escenarios anteriores: la CPU no llega a los valores críticos que veíamos cuando todo el tráfico se atendía desde una sola instancia o desde un solo contenedor. La política de autoescalado con umbral bajo (35%) permitió que la infraestructura estuviera lista para escalar.

<img width="1920" height="912" alt="image" src="https://github.com/user-attachments/assets/0e002e04-821f-48cf-83d1-0c5bf4fe0af7" />

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

<img width="1918" height="861" alt="Alarma" src="https://github.com/user-attachments/assets/0ab351ab-7ef4-4ae4-8cb4-121c72e42ceb" />

**Métrica de procesamiento:**

La métrica `FFmpegProcessingTime` registró un promedio de **47 segundos** por video. Este tiempo incluye todas las operaciones de FFmpeg: creación del intro con logo, recorte y codificación del video principal, generación del outro, y concatenación final de todos los segmentos. Este comportamiento es consistente con entregas anteriores, donde FFmpeg se identifica como la fase más costosa del pipeline.

Comparado con las otras fases, el tiempo de FFmpeg domina completamente el tiempo total. Las operaciones de descarga desde S3, consulta a la base de datos y actualización de registros consumen tiempos mínimos (menos de 1 segundo cada una), confirmando que el cuello de botella principal está en la codificación y procesamiento de video, no en I/O o acceso a datos. Los 47 segundos de `FFmpegProcessingTime` representan aproximadamente el 98% del tiempo total de procesamiento.

<img width="1920" height="863" alt="CloudWatch" src="https://github.com/user-attachments/assets/79286980-a380-47d6-8132-c190491868d1" />

**Uso de recursos de la instancia worker:**

El monitoreo de CloudWatch muestra un uso de CPU del **28.8%** durante el procesamiento de videos de 50MB. Aunque moderado, refleja que el procesamiento de video es intensivo en CPU, pero la instancia aún tiene capacidad disponible. El hecho de que la CPU no alcance niveles críticos (por encima del 85%) indica que, para este tamaño de archivo y nivel de paralelismo, la instancia tiene margen para manejar más carga.

<img width="1918" height="865" alt="CPU" src="https://github.com/user-attachments/assets/53665af0-b526-4507-b618-16fd28b1fa3b" />

**Autoescalado:**

Como mencionamos en el análisis de la alarma, el sistema se mantuvo en 1 instancia durante todo el procesamiento. La cola nunca alcanzó el umbral de 5 mensajes visibles configurado en la política de autoescalado, por lo que no hubo escalamiento.

<img width="1918" height="861" alt="Instancias" src="https://github.com/user-attachments/assets/aa25d5eb-8938-49cb-bb13-01d858ce5fd9" />

## Escenario 2 100Mb - 1 Worker - 5 Tasks

Repetimos la misma metodología de inyección de carga, pero utilizando videos de 100MB (video ID 44 en la base de datos). El objetivo era evaluar cómo el aumento en el tamaño del archivo impacta el tiempo de procesamiento y el consumo de recursos, manteniendo la misma configuración de 1 worker y 5 tareas.

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

## Escenario 2 50Mb - 3 Worker - 16 Tasks

Para este escenario inyectamos 16 tareas de procesamiento de videos de 50MB directamente en la cola SQS, manteniendo la misma metodología del escenario anterior pero con una carga mayor para evaluar el comportamiento del autoescalado.

**Alarma CloudWatch:**

La métrica `ApproximateNumberOfVisibleMessages` de SQS mostró un pico de **14 mensajes visibles** en la cola, superando significativamente el umbral de 5 mensajes configurado en la política de autoescalado. Este comportamiento es diferente al escenario con 1 worker y 5 tareas, donde el worker podía mantener el ritmo y la cola nunca alcanzaba el umbral. Con 16 tareas, la carga es suficiente para que los mensajes se acumulen en la cola antes de ser procesados, activando así la alarma de escalado.

<img width="1918" height="861" alt="Alarma" src="https://github.com/user-attachments/assets/85ea22c8-2da4-4661-89f9-6d270aa2c5f7" />

**Autoescalado:**

En la pestaña de Activity del Auto Scaling Group se puede observar cómo se activó el Policy Up de la alarma, lo que conllevó al escalado automático de las instancias worker. El sistema escaló desde 1 instancia hasta 3 instancias para manejar la carga de 16 tareas. Este comportamiento demuestra que la política de autoescalado funciona correctamente cuando la cola supera el umbral configurado, permitiendo que el sistema se adapte dinámicamente a la demanda.

<img width="1918" height="482" alt="AutoScaling" src="https://github.com/user-attachments/assets/573944a5-1279-4902-867e-ad9dbee96838" />

**Instancias:**

La imagen confirma que efectivamente se crearon y están activas las 3 instancias worker en el grupo de Auto Scaling. El escalado horizontal funcionó como se esperaba, distribuyendo la carga de procesamiento entre las múltiples instancias para mejorar el throughput del sistema.

<img width="1918" height="862" alt="Instancias" src="https://github.com/user-attachments/assets/4eb13663-f443-46ca-8767-44fa6b7b8950" />

**Uso de recursos de la instancia worker:**

El monitoreo de CloudWatch muestra un uso de CPU del **29.4%** en una de las instancias del autoescalado durante el procesamiento de videos de 50MB. Este valor es similar al observado en el escenario con 1 worker (28.8%), lo que indica que cada instancia está procesando una porción de la carga total de manera eficiente. El hecho de que el CPU se mantenga en un rango moderado incluso con múltiples instancias procesando en paralelo sugiere que el escalado horizontal está funcionando correctamente, distribuyendo la carga sin saturar ninguna instancia individual.

<img width="1918" height="865" alt="CPU" src="https://github.com/user-attachments/assets/7cdba982-204b-4544-8b7d-2d7553ab2dc6" />
**Análisis de tiempos desde logs de la instancia:**

Como CloudWatch no mostró logs detallados durante el autoescalado, analizamos los logs de la instancia worker para obtener los tiempos reales de procesamiento. Los logs muestran los siguientes tiempos totales por tarea:

- **Tarea 1:** 48.78s (FFmpeg: 47.75s, S3 Download: 0.88s, DB Fetch: 0.03s, DB Update: 0.01s)
- **Tarea 2:** 50.32s (FFmpeg: 49.60s, S3 Download: 0.61s, DB Fetch: 0.00s, DB Update: 0.01s)
- **Tarea 3:** 48.68s (FFmpeg: 47.92s, S3 Download: 0.63s, DB Fetch: 0.00s, DB Update: 0.01s)
- **Tarea 4:** 48.78s (FFmpeg: 48.05s, S3 Download: 0.63s, DB Fetch: 0.01s, DB Update: 0.01s)

El tiempo promedio de procesamiento por video fue de **49.14 segundos**, con un rango entre 48.68s y 50.32s. El tiempo total para procesar los 5 videos (desde el inicio del primer procesamiento hasta el final del último) fue de aproximadamente **3 minutos y 19 segundos** (desde 20:53:30 hasta 20:56:49), lo que confirma que el worker procesa los videos de forma secuencial, uno tras otro, sin paralelismo dentro de la misma instancia.

## Escenario 2 100Mb - 3 Worker - 16 Tasks

Para este escenario inyectamos 16 tareas de procesamiento de videos de 100MB directamente en la cola SQS, manteniendo la misma metodología del escenario anterior pero con archivos más grandes para evaluar el impacto del tamaño en el comportamiento del autoescalado y el uso de recursos.

**Uso de recursos de la instancia worker:**

El monitoreo de CloudWatch muestra un uso de CPU del **35.2%** en una de las instancias del autoescalado durante el procesamiento de videos de 100MB. Este valor es ligeramente mayor que el observado en el escenario con 1 worker y videos de 100MB (33.8%), con un incremento de aproximadamente 1.4%. Esta diferencia mínima indica que cada instancia está procesando una porción similar de la carga total, confirmando que el escalado horizontal distribuye eficientemente el trabajo entre las múltiples instancias.

Comparado con el escenario de 3 workers y videos de 50MB (29.4% CPU), el incremento de 5.8% refleja el mayor tiempo de procesamiento requerido para archivos más grandes. El hecho de que el CPU se mantenga por debajo del 40% incluso con múltiples instancias procesando videos de 100MB en paralelo sugiere que el escalado horizontal sigue funcionando correctamente, distribuyendo la carga sin saturar ninguna instancia individual. Sin embargo, el tiempo de procesamiento por video (aproximadamente 106 segundos según los logs) es significativamente mayor que con videos de 50MB, lo que impacta directamente el throughput del sistema.

<img width="1918" height="861" alt="CPU" src="https://github.com/user-attachments/assets/30725cb5-74df-4b97-83cf-f8b770bf3c1e" />

**Análisis de tiempos desde logs de la instancia:**

Como CloudWatch no mostró logs detallados durante el autoescalado, analizamos los logs de la instancia worker para obtener los tiempos reales de procesamiento. Los logs muestran los siguientes tiempos totales por tarea:

- **Tarea 1:** 107.15s (FFmpeg: 105.42s, S3 Download: 1.34s, DB Fetch: 0.01s, DB Update: 0.01s)
- **Tarea 2:** 106.09s (FFmpeg: 104.46s, S3 Download: 1.24s, DB Fetch: 0.01s, DB Update: 0.01s)

El tiempo promedio de procesamiento por video fue de **106.62 segundos**, con un rango entre 106.09s y 107.15s. Este tiempo es más del doble del observado para videos de 50MB (49.14s), confirmando que el tamaño del archivo tiene un impacto directo y significativo en el tiempo de procesamiento. Al igual que en el escenario de 50MB, el tiempo de FFmpeg domina completamente el tiempo total, representando aproximadamente el 98% del tiempo de procesamiento (104-105 segundos), mientras que las operaciones de S3, base de datos y actualización continúan siendo despreciables en comparación.

<img width="1918" height="762" alt="Logs" src="https://github.com/user-attachments/assets/a55c7ec8-72e4-4a08-8903-106016576ea6" />

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
