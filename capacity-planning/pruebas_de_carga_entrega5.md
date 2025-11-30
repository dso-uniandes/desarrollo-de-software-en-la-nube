# Pruebas de carga capa web

## Escenario 1 - Sanidad (Smoke):

Para este escenario inicial de sanidad, configuramos JMeter con 5 hilos (usuarios concurrentes), un periodo de ramp-up de 5 segundos y una duración total de 60 segundos. Esta configuración nos permite validar que todo el sistema responde correctamente y que la telemetría está funcionando antes de proceder con pruebas más intensivas.

En este escenario inicial validamos el funcionamiento básico del endpoint ahora expuesto por API Gateway que invoca nuestra Lambda Web.

<img alt="java_F1daE78feS" src="https://github.com/user-attachments/assets/7a2bd856-f0e2-4ac0-b752-a26876ba49d8" />

Aquí se aprecia la configuración de la petición. Ahora usamos HTTPS (puerto 443) porque ya no dependemos de un ALB escuchando en puerto 80, sino de un endpoint seguro administrado por API Gateway.

<img alt="java_HrkLbhf6KN" src="https://github.com/user-attachments/assets/7d94f89f-739c-4f80-a8be-6cbd37ef6e56" />

---

### Resultados del Test de Sanidad:

Los resultados muestran que todas las peticiones fueron exitosas, lo cual es un excelente indicador de que el sistema está funcionando correctamente bajo carga básica.

**Summary Report:**
- **222 samples** procesados exitosamente
- **Tiempo promedio de respuesta:** 1,320 ms
- **Tiempo mínimo:** 1,206 ms
- **Tiempo máximo:** 3,875 ms
- **0% de errores** - todas las peticiones fueron exitosas
- **Throughput:** 3.6 requests/segundo

<img alt="java_82Yube57PO" src="https://github.com/user-attachments/assets/e09f52c4-b092-4af0-9029-6314cc7daea9" />

<img alt="java_ucSYkoJoJs" src="https://github.com/user-attachments/assets/af47183e-243b-475d-897f-401133fa2100" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 1,332 ms
- **95% de las respuestas:** ≤ 1,356 ms  
- **99% de las respuestas:** ≤ 3,749 ms

<img alt="java_lhOjiiQml4" src="https://github.com/user-attachments/assets/bcde8fe3-3a61-4004-a3e5-93f81af53e82" />

**Análisis de Tiempo de Respuesta:**
El gráfico evidencia que la primera petición tarda ~2100 ms mientras que las siguientes rondan los ~1200 ms, consistente con el arranque inicial de Lambda.

<img alt="java_wNYcK1Tmix" src="https://github.com/user-attachments/assets/2254d754-ba61-4d76-8ad3-19ef91857c05" />

**Monitoreo de Recursos del Sistema:**
En CloudWatch se registraron 157 invocaciones, todas exitosas.

<img alt="image" src="https://github.com/user-attachments/assets/f399daa3-6904-4ee4-8758-ccb32c6f63a2" />

---

## Escenario 1 - Escalamiento rápido (Ramp) X = 100:

Comenzamos el ramp-up hacia 100 usuarios concurrentes. Aquí es donde se evidenciaron los fallos.

### Resultados del Test con 100 Usuarios Concurrentes:

<img alt="java_YRlmVYzzXV" src="https://github.com/user-attachments/assets/edfa4837-5a16-4929-8058-c1af9b4db3dd" />

**Summary Report:**
- **68,667 samples** procesados
- **99.94% de errores** 

<img alt="java_rIlqStSM9R" src="https://github.com/user-attachments/assets/c5a9f33f-8826-4805-bc02-60c6b748618f" />

**Análisis de Percentiles:**

Los percentiles (p90≈721 ms, p99≈978 ms) no reflejan la gravedad porque la mayoría fueron fallos.

<img alt="java_MhuykOY2p1" src="https://github.com/user-attachments/assets/b7de3550-209e-43af-8069-6fe4f5e2f306" />

**Análisis de Tiempo de Respuesta:**
<img alt="java_vSceHSQpGY" src="https://github.com/user-attachments/assets/ba84b8ea-7af8-4fc6-9d4a-ce99dded4d51" />

**Monitoreo de Recursos del Sistema:**
En CloudWatch se observan 9380 invocaciones, todas fallidas, confirmando el problema estructural al trabajar con picos sobre Lambda.

<img alt="image" src="https://github.com/user-attachments/assets/4b19cd6a-74d4-4f93-9d39-66669dff0963" />

---

## Escenario 1 - Sostenida corta (300 * 0.8 = 240):
### Resultados del Test de Sostenida Corta con 240 Usuarios:

**Summary Report:**
<img alt="java_tE0NZXX8tf" src="https://github.com/user-attachments/assets/6d5991ef-0e90-436b-b40b-8a6a108fea8f" />

**Monitoreo de Recursos del Sistema:**
<img alt="image" src="https://github.com/user-attachments/assets/5968d78b-186b-4d60-a5e6-fa89ce7178ee" />

---

## Conclusiones del Escenario 1 - Capacidad de la Capa Web:

De nuestro análisis llegamos a estas conclusiones:

- El límite de concurrencia de la cuenta es 400, con un mínimo libre obligatorio de 40; solo podemos reservar 360.  
- La concurrencia reservada no mantiene instancias calientes; solo garantiza cupo.  
- Lambda escala por burst y luego progresivamente; no reacciona de inmediato.  
- API Gateway también tiene límites propios de burst, más bajos en cuentas educativas.  
- JMeter genera picos sincronizados que saturan el burst inicial.  
- La primera ola de tráfico cayó en cold starts y throttling.  

### Alternativas identificadas:

- Usar Provisioned Concurrency.  
- Precalentar la función antes de la prueba.  
- Optimizar el arranque de la Lambda.  

# Pruebas de carga capa worker

Recepción de mensajes en la cola.
<img width="1920" height="864" alt="SQS_recibido_5" src="https://github.com/user-attachments/assets/543c1cdc-808a-4a7f-87d1-7970771fe620" />

## Escenario 2 50Mb - 1 Worker - 5 Tasks

El script `send_message_to_broker.py` es el mismo de la entrega pasada, que toma videos previamente subidos a S3 y registrados en RDS. El script busca los videos por su ID en la base de datos (video ID 54 para 50MB) y genera mensajes con `task_id` únicos que enviamos directamente a la cola SQS. 

**Alarma CloudWatch:**

<img alt="image" src="https://github.com/user-attachments/assets/964650af-33c1-4d23-ab81-87b769d7ea92" />

**Métrica de procesamiento:**

Aquí se muestran los logs de Lambda procesando las tareas.

<img alt="chrome_F9RrgpGKCu" src="https://github.com/user-attachments/assets/69038f63-6e5a-44c8-84e1-81ec3786b3df" />

El tiempo total por video fue ~56 s, siendo FFmpeg (~55 s) el dominante.

## Escenario 2 100Mb - 1 Worker - 5 Tasks

Repetimos la misma metodología de inyección de carga, pero utilizando videos de 100MB (video ID 44 en la base de datos).

<img alt="chrome_Ml9oJlY3Ua" src="https://github.com/user-attachments/assets/320cf8a8-ac7a-4823-ace1-d53d5fd34e9a" />

Este gráfico confirma que todas las tareas usaron una sola Lambda debido al mismo groupId; enviando múltiples groupIds podríamos escalar horizontalmente.

<img alt="chrome_8onkKUbKQp" src="https://github.com/user-attachments/assets/c47ef014-3a8e-4ef4-806c-9c9a0e6a4724" />

Para videos de 100MB, FFmpeg tardó ~102 s.

**Autoescalado:**

<img alt="chrome_hcwiGtb5pF" src="https://github.com/user-attachments/assets/9ee8cd4e-2b2f-4fc5-acf8-6f9b54f2ec9d" />


## Conclusiones del Escenario 2 - Capacidad de la Capa Worker

En la capa worker el comportamiento fue estable y predecible. La carga depende principalmente de FFmpeg, y el throughput solo varía según el tamaño del archivo. A diferencia de la capa web, aquí no hay usuarios concurrentes sino tareas intensivas, lo cual hace que el sistema responda de forma más controlada.
