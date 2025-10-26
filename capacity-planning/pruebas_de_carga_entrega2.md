## Escenario 1 - Sanidad (Smoke):

Para este escenario inicial de sanidad, configuramos JMeter con 5 hilos (usuarios concurrentes), un periodo de ramp-up de 5 segundos y una duración total de 60 segundos. Esta configuración nos permite validar que todo el sistema responde correctamente y que la telemetría está funcionando antes de proceder con pruebas más intensivas.

La configuración de la petición incluye el endpoint de login con parámetros URL encoded para username y password, haciendo una petición POST a la IP pública de la EC2 donde está desplegado nuestro proyecto FastAPI.

<img width="1519" height="856" alt="java_GLTQw7kwge" src="https://github.com/user-attachments/assets/5bdb580a-83ad-4bff-a666-e49b65cb069e" />

Configuración de la petición:

<img width="1519" height="856" alt="java_TE3ziuAjav" src="https://github.com/user-attachments/assets/531da995-64b9-4b56-9687-71351d85add3" />

### Resultados del Test de Sanidad:

Los resultados muestran que todas las peticiones fueron exitosas, lo cual es un excelente indicador de que el sistema está funcionando correctamente bajo carga básica.

**Summary Report:**
- **206 samples** procesados exitosamente
- **Tiempo promedio de respuesta:** 1,431 ms
- **Tiempo mínimo:** 471 ms
- **Tiempo máximo:** 3,255 ms
- **0% de errores** - todas las peticiones fueron exitosas
- **Throughput:** 3.4 requests/segundo

<img width="1519" height="856" alt="java_0WpDjov8j2" src="https://github.com/user-attachments/assets/a07d8133-4dda-468f-ac19-894ed22fa159" />

<img width="1519" height="856" alt="java_5JfaZ5r1M8" src="https://github.com/user-attachments/assets/496397c9-1ce6-4001-9cb2-19bc680547a9" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 1,805 ms
- **95% de las respuestas:** ≤ 1,910 ms  
- **99% de las respuestas:** ≤ 2,549 ms

<img width="1519" height="856" alt="java_ErSibnIBm4" src="https://github.com/user-attachments/assets/4772e192-21bb-4c70-9dc4-ec4e69321ff2" />

**Análisis de Tiempo de Respuesta:**
El gráfico de tiempo de respuesta muestra un comportamiento bastante estable, con un pequeño pico que supera los 1,600 milisegundos, pero la mayoría de las respuestas se mantienen por debajo de este umbral. Esto indica que el sistema maneja bien la carga básica de 5 usuarios concurrentes.

<img width="1519" height="856" alt="java_rOpBp4TdaX" src="https://github.com/user-attachments/assets/b84f74d7-9766-4619-9f1c-872515e23a18" />

<img width="1519" height="856" alt="java_XCSEdQx20G" src="https://github.com/user-attachments/assets/c4f3d6ff-efef-406c-b2fd-abc2f86fe3bf" />

**Monitoreo de Recursos del Sistema:**
Utilizando calculate-stats en la EC2, generamos métricas de uso de recursos durante la prueba. Los resultados muestran un uso de CPU del 40% en el contenedor storeapi, lo cual es un nivel saludable y indica que el sistema tiene capacidad adicional para manejar más carga.

<img width="1920" height="1726" alt="image" src="https://github.com/user-attachments/assets/ae472958-d251-49f7-975b-91d50c363e94" />

Luego descargamos la imagen generada con secure copy:

```bash
scp -i "ANB.pem" ubuntu@{{ip}}:/home/ubuntu/anb/capacity-planning/postman/results/container_resources.png ./container_resources.png
```

El gráfico de recursos del contenedor muestra que el uso de CPU se mantiene estable alrededor del 100% durante la mayor parte de la prueba, con caídas solo al inicio y final de la ejecución. Esto confirma que el sistema está operando dentro de sus límites normales bajo esta carga básica.

<img width="4170" height="2955" alt="container_resources" src="https://github.com/user-attachments/assets/31f3c92d-6b42-4e65-8c28-31a0e16f7016" />

## Escenario 1 - Escalamiento rápido (Ramp) X = 100:

Para este escenario de escalamiento rápido, aumentamos significativamente la carga para determinar el punto donde el sistema comienza a mostrar signos de degradación. Configuramos JMeter para escalar desde 0 hasta 100 usuarios concurrentes en 3 minutos, manteniendo esta carga durante 5 minutos adicionales.

### Resultados del Test con 100 Usuarios Concurrentes:

**Summary Report:**
- **1,708 samples** procesados
- **Tiempo promedio de respuesta:** 23,713 ms (aproximadamente 24 segundos)
- **Tiempo mínimo:** 450 ms
- **Tiempo máximo:** 37,108 ms
- **0% de errores** - todas las peticiones fueron exitosas
- **Throughput:** se mantiene estable
- **Mediana:** 28,606 ms

<img width="1467" height="801" alt="java_TOYLZpBFWs" src="https://github.com/user-attachments/assets/06d49d2c-028d-402f-9480-cfaaae7c9221" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 31,058 ms
- **95% de las respuestas:** ≤ 31,558 ms
- **99% de las respuestas:** ≤ 32,004 ms

<img width="1467" height="801" alt="java_1YL9a5qtSc" src="https://github.com/user-attachments/assets/5ef849cf-24b1-4dee-920f-5ba0d2d6c929" />

**Análisis de Tiempo de Respuesta:**
El gráfico muestra que los tiempos de respuesta aumentan significativamente a aproximadamente 30,000 milisegundos (30 segundos), lo cual indica que el sistema está comenzando a experimentar estrés bajo esta carga. Aunque no hay errores, la degradación en el rendimiento es evidente.

<img width="1467" height="801" alt="java_CMYt9fWng5" src="https://github.com/user-attachments/assets/5d060f5b-fecb-4709-a340-61347725fe8b" />

<img width="1467" height="801" alt="java_T1g88d5sYG" src="https://github.com/user-attachments/assets/c67dad2d-f371-4dd0-bb7f-4af67e33e7ff" />

**Monitoreo de Recursos del Sistema:**
El análisis de recursos muestra un uso promedio de CPU del 94.82% en el contenedor storeapi, lo cual indica que el sistema está operando cerca de su capacidad máxima. El gráfico de recursos del contenedor confirma que el CPU se mantiene constantemente al 100%, con picos ocasionales que lo llevan hasta el 140% o 120%. El uso de memoria se mantiene estable en aproximadamente 70MB.

<img width="1920" height="1704" alt="image" src="https://github.com/user-attachments/assets/a9b82748-d342-495c-a728-3e6e2b56a0c2" />

Descargamos la imagen generada con secure copy:

```bash
scp -i "ANB.pem" ubuntu@{{ip}}:/home/ubuntu/anb/capacity-planning/postman/results/container_resources.png ./container_resources.png
```

<img width="4170" height="2955" alt="container_resources" src="https://github.com/user-attachments/assets/48ee57d7-02b2-45e2-b8d0-e231e0ade0fe" />

## Escenario 1 - Escalamiento rápido (Ramp) X = 300:

Continuamos con el escalamiento, aumentando la carga a 300 usuarios concurrentes para identificar más claramente los límites del sistema.

### Resultados del Test con 300 Usuarios Concurrentes:

**Summary Report:**
- **1,901 samples** procesados
- **Tiempo promedio de respuesta:** 68,657 ms (aproximadamente 69 segundos)
- **Tiempo mínimo:** 535 ms
- **Tiempo máximo:** 93,516 ms
- **0% de errores** - todas las peticiones fueron exitosas
- **Throughput:** 3.3 requests/segundo
- **Mediana:** 87,646 ms

<img width="1467" height="801" alt="java_8XfTceekM3" src="https://github.com/user-attachments/assets/e1c88317-c01b-4df6-89ae-77fd2d57fd2f" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 90,761 ms
- **95% de las respuestas:** ≤ 92,577 ms
- **99% de las respuestas:** ≤ 93,230 ms

<img width="1467" height="801" alt="java_Yt914qjvWT" src="https://github.com/user-attachments/assets/37257a2f-ce58-4dfd-bb00-235ddf5c93bf" />

**Análisis de Tiempo de Respuesta:**
El gráfico de tiempo de respuesta muestra que efectivamente los tiempos suben a aproximadamente 90,000 milisegundos (90 segundos) después de los 3 minutos de rampa. Esta degradación significativa indica que el sistema está operando muy cerca de sus límites máximos.

<img width="1467" height="801" alt="java_QbncFsrJQo" src="https://github.com/user-attachments/assets/7f5ba010-41d9-4529-9ec7-880b0b37c13b" />

<img width="1467" height="801" alt="java_0bwM9nL3gJ" src="https://github.com/user-attachments/assets/00859e86-703a-47bf-b8d3-3003c0e4dc2a" />

**Monitoreo de Recursos del Sistema:**
El análisis de recursos muestra un uso promedio de CPU del 100.71% en el contenedor storeapi, lo cual indica que el sistema está operando al límite de su capacidad. El gráfico de recursos del contenedor muestra el mismo comportamiento que el escenario anterior, con el CPU manteniéndose al 100% y picos ocasionales que llegan hasta el 160%.

<img width="1920" height="1704" alt="image" src="https://github.com/user-attachments/assets/cbeb5e60-b284-4a0c-8799-7eb52d4ed8c6" />

Descargamos la imagen generada con secure copy:

```bash
scp -i "ANB.pem" ubuntu@{{ip}}:/home/ubuntu/anb/capacity-planning/postman/results/container_resources.png ./container_resources.png
```

<img width="4170" height="2955" alt="container_resources" src="https://github.com/user-attachments/assets/9c36a0a9-1dfe-4bba-a9f3-832d85bcddb9" />

## Escenario 1 - Escalamiento rápido (Ramp) X = 500:

En este escenario crítico, aumentamos la carga a 500 usuarios concurrentes para identificar el punto de fallo del sistema.

### Resultados del Test con 500 Usuarios Concurrentes:

**Summary Report:**
- **2,157 samples** procesados
- **Tiempo promedio de respuesta:** 107,183 ms (aproximadamente 107 segundos)
- **Tiempo mínimo:** 254 ms
- **Tiempo máximo:** 344,100 ms
- **1.25% de errores** - aquí comenzamos a ver fallos en el sistema
- **Throughput:** se mantiene en 3.4 requests/segundo
- **Mediana:** 139,466 ms

<img width="1467" height="801" alt="java_SeVT6L9y5S" src="https://github.com/user-attachments/assets/fc7f0d46-5ae7-4786-a252-f2244c65366e" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 146,951 ms
- **95% de las respuestas:** ≤ 147,586 ms
- **99% de las respuestas:** ≤ 147,863 ms

<img width="1467" height="801" alt="java_xvUmw0GM0T" src="https://github.com/user-attachments/assets/d168cbe3-fbe5-44ae-ad81-e21dabd35a65" />

**Análisis de Tiempo de Respuesta:**
El gráfico muestra tiempos de respuesta promedio de aproximadamente 140,000 milisegundos (140 segundos). Es interesante observar un pico descendente después de los 2 minutos y medio (después de la rampa de 3 minutos), lo cual probablemente se debe a la degradación de los servicios que comienzan a fallar y por tanto responden más rápido con errores.

<img width="1467" height="801" alt="java_sEj6Om40Nr" src="https://github.com/user-attachments/assets/07cade6e-ddf0-47b1-9966-19c18896f793" />

<img width="1754" height="801" alt="java_boAxAlMMBP" src="https://github.com/user-attachments/assets/0faf9013-5d34-419f-b883-3b5cf3b9dc53" />

**Monitoreo de Recursos del Sistema:**
El análisis de recursos muestra un uso promedio de CPU del 99.76% en el contenedor storeapi. Es curioso notar que aunque este escenario presenta degradación con errores, el uso de CPU es ligeramente menor que en el escenario de 300 usuarios (que no tuvo errores pero sí alcanzó el 160% en algunos picos). El gráfico de recursos del contenedor muestra el mismo comportamiento, con picos que llegan hasta el 140%.

<img width="903" height="216" alt="image" src="https://github.com/user-attachments/assets/28edeb81-f280-4ed0-b5b3-913ef76f2142" />

Descargamos la imagen generada con secure copy:

```bash
scp -i "ANB.pem" ubuntu@{{ip}}:/home/ubuntu/anb/capacity-planning/postman/results/container_resources.png ./container_resources.png
```

<img width="4170" height="2955" alt="container_resources" src="https://github.com/user-attachments/assets/656dd095-32cb-4180-9077-f6a126e1b7f2" />

## Escenario 1 - Sostenida corta (300 * 0.8 = 240):

Para el escenario de sostenida corta, utilizamos el 80% de la carga máxima que no presentó errores (300 usuarios), es decir, 240 usuarios concurrentes. Este test nos permite confirmar la estabilidad del sistema bajo una carga sostenida.

### Resultados del Test de Sostenida Corta con 240 Usuarios:

**Summary Report:**
- **1,261 samples** procesados
- **Tiempo promedio de respuesta:** 59,747 ms (aproximadamente 60 segundos)
- **Tiempo mínimo:** 648 ms
- **Tiempo máximo:** 73,171 ms
- **0% de errores** - todas las peticiones fueron exitosas
- **Throughput:** 3.8 requests/segundo
- **Mediana:** 69,539 ms

<img width="1480" height="814" alt="java_quhkRDFM0y" src="https://github.com/user-attachments/assets/74ced228-becc-4f3e-896d-93298a615818" />

**Análisis de Percentiles:**
- **90% de las respuestas:** ≤ 71,299 ms
- **95% de las respuestas:** ≤ 72,284 ms
- **99% de las respuestas:** ≤ 72,911 ms

<img width="1480" height="814" alt="java_ZMvmCPWbfW" src="https://github.com/user-attachments/assets/2ea1fd22-6882-41c1-a25b-f137e453267e" />

**Análisis de Tiempo de Respuesta:**
El gráfico muestra tiempos de respuesta promedio de aproximadamente 72,000 milisegundos (72 segundos), pero con un comportamiento estable. Aunque el tiempo de respuesta promedio es considerablemente alto, el sistema mantiene la estabilidad sin errores bajo esta carga sostenida.

<img width="1226" height="814" alt="java_4ohOTcarIn" src="https://github.com/user-attachments/assets/857a06b3-847d-43bf-ab69-5031af3fdc7c" />

<img width="1226" height="814" alt="java_VWpGT4aaBJ" src="https://github.com/user-attachments/assets/d16b3857-b43e-475d-bafc-370fa3b9ea9f" />

**Monitoreo de Recursos del Sistema:**
El análisis de recursos muestra un uso promedio de CPU del 90% en el contenedor storeapi. El gráfico de recursos del contenedor muestra el mismo comportamiento observado en los escenarios anteriores: el CPU se mantiene al 100% con picos ocasionales que llegan hasta el 140%.

<img width="1536" height="1257" alt="image" src="https://github.com/user-attachments/assets/89452f9c-e917-4850-ad1e-3b7104af75ed" />

Descargamos la imagen generada con secure copy:

```bash
scp -i "ANB.pem" ubuntu@{{ip}}:/home/ubuntu/anb/capacity-planning/postman/results/container_resources.png ./container_resources.png
```

<img width="4170" height="2955" alt="container_resources" src="https://github.com/user-attachments/assets/1ca56b6c-6d84-4b00-b2ca-2f74fe4f6f27" />

## Conclusiones del Escenario 1 - Capacidad de la Capa Web:

### Capacidad Máxima Identificada:
Basándonos en los resultados de las pruebas, podemos concluir que:

- **Capacidad máxima sin errores:** 300 usuarios concurrentes
- **Punto de degradación:** Entre 300 y 500 usuarios concurrentes
- **Punto de fallo:** 500 usuarios concurrentes (1.25% de errores)

### Análisis de SLOs:
- **p95 de endpoints:** En el escenario de 300 usuarios, el p95 fue de 92,577 ms, lo cual excede significativamente el SLO de ≤ 1 segundo
- **Errores:** El sistema mantiene 0% de errores hasta 300 usuarios, pero comienza a fallar en 500 usuarios
- **Bottleneck identificado:** El CPU del contenedor storeapi es claramente el cuello de botella, operando constantemente al 100% con picos hasta el 160%

### Recomendaciones:
1. **Escalado horizontal:** Implementar múltiples instancias del API para distribuir la carga
2. **Optimización de CPU:** Revisar y optimizar el código para reducir el uso de CPU
3. **Monitoreo proactivo:** Establecer alertas cuando el CPU supere el 80% para escalar automáticamente
4. **Capacidad recomendada:** Para producción (con esta configuración), no exceder 240 usuarios concurrentes (80% de la capacidad máxima sin errores)












