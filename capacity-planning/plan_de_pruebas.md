# 🧪 Plan de Análisis de Capacidad

## 1. Objetivo General

Evaluar la **capacidad máxima** que puede soportar la aplicación en sus dos componentes críticos:
1. **Capa Web (API HTTP):** endpoint de subida de videos `/api/videos/upload`
2. **Capa Worker:** procesamiento asíncrono de videos con FFmpeg

El propósito es identificar límites de **concurrencia, rendimiento y estabilidad**, establecer una línea base de desempeño y proponer acciones de mejora basadas en evidencia.

---

## 2. Objetivos Específicos

| Nº | Objetivo | Métrica asociada |
|----|-----------|------------------|
| 1 | Determinar el número máximo de usuarios concurrentes soportados en upload sin degradación | p95 ≤ 1s, error rate ≤ 5% |
| 2 | Medir la capacidad de procesamiento de los workers (videos/minuto) | Throughput y tiempo medio de servicio |
| 3 | Identificar cuellos de botella en CPU, memoria, red o almacenamiento | Métricas del host y contenedores |
| 4 | Evaluar la estabilidad bajo carga sostenida y picos repentinos | Desviación estándar de latencia y uso de recursos |
| 5 | Validar el tiempo de aceptación de archivos de diferentes tamaños | Tiempo de respuesta para 5 MB, 50 MB, 100 MB |
| 6 | Documentar resultados y recomendaciones de escalabilidad | Informe final con evidencias y gráficos |

---

## 3. Descripción General

Este plan de pruebas evalúa dos componentes críticos de la arquitectura:

### 3.1 Capa Web (API HTTP)
- **Endpoint bajo prueba:** `POST /api/videos/upload`
- **Función:** Recepción de archivos multipart/form-data, validación, almacenamiento temporal y encolado de tarea
- **Tecnología:** FastAPI (Python), almacenamiento S3/local, mensajería Kafka
- **Métricas clave:** Tiempo de aceptación, RPS, concurrencia máxima, error rate

### 3.2 Capa Worker
- **Función:** Procesamiento asíncrono de videos con FFmpeg (branding, trim, concatenación)
- **Tecnología:** Python, Kafka Consumer, FFmpeg, S3
- **Métricas clave:** Videos procesados/minuto, tiempo medio de procesamiento, throughput

Las pruebas se ejecutarán en **entorno local** con **Docker Compose**, garantizando un aislamiento controlado y replicable del sistema.

---

## 4. Tipos de Pruebas

| Tipo | Objetivo | Descripción |
|------|----------|-------------|
| **Capacidad** | Determinar máximo de usuarios concurrentes y RPS sostenido | Incremento progresivo de carga hasta detectar degradación |
| **Carga** | Evaluar comportamiento con niveles crecientes de solicitudes | Rampas ascendentes con plateaus de estabilización |
| **Estrés** | Analizar respuesta ante sobrecarga extrema | Incremento súbito hasta saturación y observar recuperación |
| **Picos (Spike)** | Evaluar recuperación tras picos repentinos | Carga instantánea 10x–20x durante 20–30s |
| **Sostenida (Soak)** | Validar estabilidad a largo plazo | 1–2 horas a carga media para detectar fugas |
| **Escalabilidad Worker** | Validar impacto de aumentar paralelismo | Comparar throughput con 1/2/4 workers |

---

## 5. Criterios de Aceptación

### 5.1 Capa Web (Upload)
- ✅ **p95 de latencia ≤ 1 segundo** para archivos de hasta 100 MB
- ✅ **Error rate ≤ 5%** (excluyendo errores esperados como 400/413)
- ✅ **Sin resets ni timeouts anómalos**
- ✅ **CPU del contenedor `storeapi` ≤ 85%** sostenido
- ✅ **Tiempo de aceptación:**
  - 5 MB: ≤ 500 ms
  - 50 MB: ≤ 1.5 s
  - 100 MB: ≤ 2 s
- ✅ **Validación de errores controlados:**
  - 400 para tipos de archivo inválidos
  - 413 para archivos que exceden límite configurado

### 5.2 Capa Worker
- ✅ **La cola no debe crecer indefinidamente** durante prueba sostenida
- ✅ **Throughput estable** según configuración de paralelismo
- ✅ **CPU del contenedor `worker` ≤ 85%** sostenido
- ✅ **Sin fallos de procesamiento** por timeout o recursos
- ✅ **Tiempo de procesamiento predecible** según tamaño de archivo

---

## 6. Datos de Prueba

### 6.1 Para Capa Web
- **Usuarios simulados:** 5, 50, 100, 200, 300, 400
- **Duración por escenario:** 1–10 minutos
- **Tamaños de archivo:** 5 MB, 50 MB, 100 MB
- **Formato de archivos:** MP4 (válidos) y archivos inválidos para pruebas de error
- **Credenciales:** Usuario de prueba pre-creado (test@example.com / pass123)

### 6.2 Para Capa Worker
- **Mensajes en cola:** 10 a 500 por ejecución
- **Tamaños de video:** 50 MB, 100 MB
- **Configuraciones de paralelismo:** 1, 2, 4 workers
- **Operaciones FFmpeg:** Intro (2.5s) + Video (max 30s) + Outro (2.5s)

---

## 7. Iteraciones y Repetibilidad

- Cada escenario se repetirá **mínimo 5 veces** para validar consistencia
- Se calcularán: **promedio, desviación estándar y percentiles** (p50, p90, p95, p99)
- Se identificarán y justificarán **valores atípicos**
- Se mantendrá un **baseline** por iteración del desarrollo para comparación

---

## 8. Configuración del Sistema

### 8.1 Arquitectura

```mermaid
graph TD
  A[Newman/Postman<br/>Generador de carga] --> B[Nginx<br/>Reverse Proxy]
  B --> C[StoreAPI<br/>FastAPI]
  C --> D[(PostgreSQL<br/>Base de datos)]
  C --> E[(Redis<br/>Caché opcional)]
  C --> F[S3/Local<br/>Almacenamiento]
  C --> G[Kafka<br/>Message Broker]
  G --> H[Worker<br/>FFmpeg Processor]
  H --> F
  H --> D
  
  I[Monitor<br/>Docker Stats] -.-> C
  I -.-> H
  I -.-> G
  
  style C fill:#4A90E2
  style H fill:#E27B4A
  style A fill:#50C878
```

### 8.2 Servicios Docker Compose

| Servicio | Imagen/Tecnología | Propósito |
|----------|-------------------|-----------|
| `nginx` | nginx:latest | Proxy reverso y balanceo de carga |
| `storeapi` | FastAPI (Python 3.11) | API REST para manejo de videos |
| `worker` | Python 3.11 + FFmpeg | Procesamiento asíncrono de videos |
| `anb-database` | PostgreSQL 15 | Persistencia de metadatos |
| `anb-redis` | Redis 7 | Caché (opcional) |
| `kafka` | Apache Kafka | Cola de mensajes para tareas |

### 8.3 Host Local (Requisitos Mínimos)

- **CPU:** 8 núcleos (mínimo 4 dedicados a Docker)
- **RAM:** 16 GB (mínimo 8 GB disponibles)
- **Disco:** 50 GB libres (para videos y logs)
- **Sistema operativo:** macOS / Linux
- **Docker:** Docker Desktop 4.x o Docker Engine 20.x

---

## 9. Herramientas de Prueba

| Herramienta | Uso | Versión | Comando de instalación |
|-------------|-----|---------|------------------------|
| **Newman** | Ejecución automatizada de colecciones Postman | 5.6.3+ | `npm install -g newman` |
| **Postman** | Diseño de colecciones y verificación manual | Última | Descargar de postman.com |
| **Docker Stats** | Monitoreo de recursos de contenedores | Built-in | - |
| **monitor.sh** | Script personalizado para captura de métricas | Custom | Incluido en el proyecto |
| **Python 3.11** | Inyección de mensajes en Kafka (worker tests) | 3.11+ | - |
| **jq** | Procesamiento de logs JSON | Última | `brew install jq` |

---

## 10. Métricas

### 10.1 Métricas de Aplicación

| Categoría | Métrica | Descripción | Unidad |
|-----------|---------|-------------|--------|
| **Latencia** | p50, p90, p95, p99 | Percentiles de tiempo de respuesta | ms |
| **Throughput** | RPS (Requests Per Second) | Solicitudes procesadas por segundo | req/s |
| **Errores** | Error Rate | Porcentaje de respuestas 4xx/5xx | % |
| **Disponibilidad** | Uptime | Tiempo sin errores 5xx | % |
| **Capacidad** | Max VUs | Usuarios concurrentes máximos sin degradación | usuarios |

### 10.2 Métricas de Worker

| Métrica | Descripción | Unidad |
|---------|-------------|--------|
| **Videos procesados/min** | Throughput del worker | videos/min |
| **Tiempo medio de procesamiento** | Tiempo promedio por video | segundos |
| **Tiempo por fase** | DB Fetch, S3 Download, FFmpeg, DB Update | segundos |
| **Cola pendiente** | Mensajes en espera en Kafka | mensajes |
| **Error rate** | Fallos de procesamiento | % |

### 10.3 Métricas de Infraestructura

| Recurso | Métricas | Herramienta |
|---------|----------|-------------|
| **CPU** | Utilización %, carga promedio | docker stats, monitor.sh |
| **Memoria** | Uso MB, porcentaje, swap | docker stats |
| **Red** | Ancho de banda (NetIO) | docker stats |
| **Disco** | IO (BlockIO), espacio usado | docker stats, df -h |
| **Base de datos** | Conexiones activas, latencia de consultas | Logs de PostgreSQL |

---

## 11. Escenarios de Prueba

### 11.1 Escenario 1: Capacidad de la Capa Web (Upload)

**Objetivo:** Determinar el máximo de usuarios concurrentes y RPS que soporta `POST /api/videos/upload` cumpliendo SLOs.

**Estrategia:**
1. **Smoke Test:** 5 VUs durante 1 minuto (validación básica)
2. **Ramp Test:** Incremento gradual 0 → X VUs en 3 minutos, mantener 5 minutos
3. **Capacity Test:** Encontrar X máximo donde p95 ≤ 1s y error rate ≤ 5%
4. **Sustained Test:** 5 minutos al 80% de X para validar estabilidad

**Configuración Newman:**
```bash
# Smoke test (5 usuarios, 60 iteraciones total)
newman run postman/collection.json \
  -e postman/environment.json \
  --iteration-count 60 \
  --delay-request 1000 \
  -r cli,html \
  --reporter-html-export postman/report_smoke.html

# Ramp test (incremento gradual simulado con múltiples ejecuciones)
for users in 50 100 150 200 250 300; do
  echo "Testing with $users users..."
  newman run postman/collection.json \
    -e postman/environment.json \
    --iteration-count $users \
    --delay-request 200 \
    -r cli,html \
    --reporter-html-export postman/report_${users}users.html
  sleep 30  # pausa entre escalones
done
```

**Criterios de éxito:**
- ✅ p95 ≤ 1s
- ✅ Error rate ≤ 5% (excluyendo 400/413 esperados)
- ✅ CPU API ≤ 85%
- ✅ Sin resets/timeouts anómalos

**Salidas esperadas:**
- Curva: Usuarios concurrentes vs. p95 latencia
- Gráfico: RPS vs. Error rate
- Identificación de capacidad máxima
- Reporte HTML de Newman con estadísticas detalladas

---

### 11.2 Escenario 2: Rendimiento de la Capa Worker

**Objetivo:** Medir videos/min procesados a distintos tamaños y niveles de paralelismo.

**Estrategia:**
1. **Bypass de la capa web:** Inyectar mensajes directamente en Kafka topic `video_tasks`
2. **Variables experimentales:**
   - Tamaños: 50 MB, 100 MB
   - Paralelismo: 1, 2, 4 workers
3. **Medición:** Saturación (aumentar tareas) y sostenida (mantener backlog fijo)

**Inyección de mensajes (Python script):**
```python
# worker_load_test.py
from confluent_kafka import Producer
import json
import time

producer = Producer({'bootstrap.servers': 'localhost:9092'})

# Inyectar 100 tareas
for i in range(100):
    message = {
        'task_id': f'test-task-{i}',
        'video_id': 1,  # ID de video existente en DB
    }
    producer.produce('video_tasks', json.dumps(message))
    if i % 10 == 0:
        print(f'Enqueued {i} tasks...')
        time.sleep(1)  # control de ritmo

producer.flush()
print('All tasks enqueued!')
```

**Ejecución:**
```bash
# Con 1 worker (default)
docker-compose up -d worker

# Con 2 workers
docker-compose up -d --scale worker=2

# Con 4 workers
docker-compose up -d --scale worker=4

# Inyectar carga
python worker_load_test.py

# Monitorear procesamiento
docker logs -f worker | grep "TOTAL TASK TIME"
```

**Métricas a calcular:**
- Videos procesados/minuto = (Total videos / Tiempo total en min)
- Tiempo medio de servicio = Promedio de "TOTAL TASK TIME"
- Descomposición: DB Fetch, S3 Download, FFmpeg, DB Update
- Pendiente de la cola = Mensajes encolados - Mensajes procesados

**Criterios de éxito:**
- ✅ Capacidad nominal estable (throughput constante)
- ✅ Cola no crece indefinidamente (pendiente ≈ 0 en sostenidas)
- ✅ CPU worker ≤ 85%
- ✅ Sin errores de procesamiento

**Salidas esperadas:**
- Tabla: Capacidad por configuración (1/2/4 workers) y tamaño (50/100 MB)
- Gráfico: Throughput vs. Paralelismo
- Identificación de cuellos de botella (CPU, IO, S3, DB)

---

## 12. Ejecución de Pruebas

### 📦 Requisitos

```bash
# 1. Activar el entorno virtual
source ../.venv/bin/activate

# 2. Instalar dependencias (matplotlib para gráficas)
cd capacity-planning
pip install -r requirements.txt
```

### 🧪 Tipos de Tests Disponibles

Todos los comandos se ejecutan desde la raíz del proyecto:

```bash
# Smoke Test - Validación rápida (5 usuarios)
make -C ./capacity-planning/ test-smoke

# Capacity Test - Encontrar límite (50→300 usuarios)
make -C ./capacity-planning/ test-capacity

# Ramp Test - Rampa gradual
make -C ./capacity-planning/ test-ramp

# Sustained Test - Carga sostenida (10 min)
make -C ./capacity-planning/ test-sustained

# Stress Test - Sobrecarga hasta fallo
make -C ./capacity-planning/ test-stress

# Spike Test - Picos repentinos
make -C ./capacity-planning/ test-spike
```

**Nota**: Cada test automáticamente:
- Inicia monitores de recursos
- Ejecuta Newman con la carga configurada
- Espera a que el worker termine de procesar
- Genera estadísticas y gráficas
- Guarda reportes en `postman/results/`

### 📊 Generar Estadísticas y Gráficas

Si necesitas regenerar estadísticas/gráficas de un test ya ejecutado:

```bash
# Opción 1: Interactivo (te pide el timestamp)
make -C ./capacity-planning/ calculate-stats

# Opción 2: Directo con timestamp
cd capacity-planning
source ../.venv/bin/activate
python3 calculate_stats.py 20251019_170416
python3 generate_graphs.py 20251019_170416
```

### 📈 Ver Resultados

```bash
# Ver estadísticas en consola
make -C ./capacity-planning/ view-stats

# Abrir gráficas generadas
make -C ./capacity-planning/ open-graphs

# Ver reportes HTML de Newman
make -C ./capacity-planning/ open-latest-report
```

### 📁 Archivos Generados

Ubicación: `capacity-planning/postman/results/`

**Reportes de Newman:**
- `report_[test]_[timestamp].html` - Reporte visual con métricas HTTP
- `report_[test]_[timestamp].json` - Datos estructurados (usado por scripts)

**Datos de monitoreo (CSV):**
- `container_stats_[timestamp].csv` - CPU, memoria, red, disco por contenedor
- `worker_timing_[timestamp].csv` - Tiempos de procesamiento por tarea
- `summary_[timestamp].csv` - Resumen consolidado (API + containers + worker)

**Gráficas (PNG):**
- `container_resources.png` - Recursos por contenedor (series de tiempo)
- `worker_timing.png` - Tiempos de procesamiento (área apilada)
- `worker_breakdown_pie.png` - Desglose de tiempos (barra + pie chart)
- `newman_api_metrics.png` - Dashboard de API (4 paneles: histograma, tendencia, success rate, estadísticas)

---

## 13. Interpretación de Resultados

### Criterios de Éxito

- **p95 ≤ 1s** = Sistema cumple SLO ✅
- **Error rate ≤ 5%** = Disponibilidad aceptable ✅
- **CPU < 85%** = Margen para picos de tráfico ✅
- **Worker queue estable** = Throughput suficiente ✅

### Resultados

- **Smoke Test - Validación rápida (5 usuarios)**
  
  ```bash
  make -C ./capacity-planning/ test-smoke
  ```

  **Métricas de API:**
  
  ![Newman API Metrics](./resultados/Escenario1/newman_api_metrics.png)

  **Recursos de Contenedores:**
  
  ![Container Resources](./resultados/Escenario1/container_resources.png)

  **Tiempos de Worker:**
  
  ![Worker Timing](./resultados/Escenario1/worker_timing.png)

  **Desglose de Procesamiento:**
  
  ![Worker Breakdown](./resultados/Escenario1/worker_breakdown_pie.png)

- **Capacity Test - Encontrar límite (50→300 usuarios)**
  
  ```bash
  make -C ./capacity-planning/ test-capacity
  ```

  **50 Usuarios:**
  
  | API Metrics | Container Resources |
  |-------------|---------------------|
  | ![API 50](./resultados/Escenario2/newman_api_metrics_50_users.png) | ![Resources 50](./resultados/Escenario2/container_resources_50_users.png) |
  
  | Worker Timing | Worker Breakdown |
  |---------------|------------------|
  | ![Timing 50](./resultados/Escenario2/worker_timing_50_users.png) | ![Breakdown 50](./resultados/Escenario2/worker_breakdown_pie_50_users.png) |

  **100 Usuarios:**
  
  | API Metrics | Container Resources |
  |-------------|---------------------|
  | ![API 100](./resultados/Escenario2/newman_api_metrics_100_users.png) | ![Resources 100](./resultados/Escenario2/container_resources_100_users.png) |
  
  | Worker Timing | Worker Breakdown |
  |---------------|------------------|
  | ![Timing 100](./resultados/Escenario2/worker_timing_100_users.png) | ![Breakdown 100](./resultados/Escenario2/worker_breakdown_pie_100_users.png) |

  **150 Usuarios:**
  
  | API Metrics | Container Resources |
  |-------------|---------------------|
  | ![API 150](./resultados/Escenario2/newman_api_metrics_150_users.png) | ![Resources 150](./resultados/Escenario2/container_resources_150_users.png) |
  
  | Worker Timing | Worker Breakdown |
  |---------------|------------------|
  | ![Timing 150](./resultados/Escenario2/worker_timing_150_users.png) | ![Breakdown 150](./resultados/Escenario2/worker_breakdown_pie_150_users.png) |

  **200 Usuarios:**
  
  | API Metrics | Container Resources |
  |-------------|---------------------|
  | ![API 200](./resultados/Escenario2/newman_api_metrics_200_users.png) | ![Resources 200](./resultados/Escenario2/container_resources_200_users.png) |
  
  | Worker Timing | Worker Breakdown |
  |---------------|------------------|
  | ![Timing 200](./resultados/Escenario2/worker_timing_200_users.png) | ![Breakdown 200](./resultados/Escenario2/worker_breakdown_pie_200_users.png) |

  **250 Usuarios:**
  
  | API Metrics | Container Resources |
  |-------------|---------------------|
  | ![API 250](./resultados/Escenario2/newman_api_metrics_250_users.png) | ![Resources 250](./resultados/Escenario2/container_resources_250_users.png) |
  
  > **Nota:** A partir de 250 usuarios, las métricas del worker no se incluyen ya que el tiempo de procesamiento se vuelve excesivamente largo, haciendo impráctico esperar a que termine el procesamiento de todos los videos encolados. El foco de estas pruebas de alta carga está en la capacidad de la API para aceptar solicitudes, no en el throughput del worker que ya no cumple con la metrica esperada.

  **300 Usuarios:**
  
  | API Metrics | Container Resources |
  |-------------|---------------------|
  | ![API 300](./resultados/Escenario2/newman_api_metrics_300_users.png) | ![Resources 300](./resultados/Escenario2/container_resources_300_users.png) |
  
  > **Nota:** Las gráficas del worker no están disponibles para cargas de 250+ usuarios debido a los tiempos de procesamiento prolongados.

- **Ramp Test - Rampa gradual**
  
  ```bash
  make -C ./capacity-planning/ test-ramp
  ```

  **50 Usuarios:**
  
  | API Metrics | Container Resources |
  |-------------|---------------------|
  | ![API 50](./resultados/Esceneario3/newman_api_metrics_50_users.png) | ![Resources 50](./resultados/Esceneario3/container_resources_50_users.png) |

  **100 Usuarios:**
  
  | API Metrics | Container Resources |
  |-------------|---------------------|
  | ![API 100](./resultados/Esceneario3/newman_api_metrics_100_users.png) | ![Resources 100](./resultados/Esceneario3/container_resources_100_users.png) |

  **200 Usuarios:**
  
  | API Metrics | Container Resources |
  |-------------|---------------------|
  | ![API 200](./resultados/Esceneario3/newman_api_metrics_200_users.png) | ![Resources 200](./resultados/Esceneario3/container_resources_200_users.png) |

  **300 Usuarios:**
  
  | API Metrics | Container Resources |
  |-------------|---------------------|
  | ![API 300](./resultados/Esceneario3/newman_api_metrics_300_users.png) | ![Resources 300](./resultados/Esceneario3/container_resources_300_users.png) |

  > **Nota:** En el Ramp Test solo se muestran métricas de API y recursos de contenedores, ya que el enfoque está en evaluar la capacidad de aceptación de solicitudes bajo carga gradual incremental.


- **Stress Test - Sobrecarga hasta fallo**
  
  ```bash
  make -C ./capacity-planning/ test-stress
  ```

  **Métricas de API:**
  
  ![Newman API Metrics](./resultados/Escenario4/newman_api_metrics.png)

  **Recursos de Contenedores:**
  
  ![Container Resources](./resultados/Escenario4/container_resources.png)

  > **Nota:** El Stress Test evalúa el comportamiento del sistema bajo sobrecarga extrema, buscando identificar el punto de ruptura y la capacidad de recuperación. Solo se muestran métricas de API y recursos de contenedores.

- **Sustained Con Postman 100 Parallel Users**
  

  **Prueba de Carga Sostenida (Postman):**
  
  ![Sustained Test Postman](./resultados/EscenarioExtra/image.png)

  > **Nota:** Esta prueba evalúa la estabilidad del sistema bajo carga sostenida de 100 usuarios concurrentes durante un período prolongado, utilizando Postman como herramienta de generación de carga.

### Conclusiones del Análisis de Capacidad

####  Desempeño Bajo Carga Ligera (Smoke Test)

El **Escenario 1 (Smoke Test)** demostró que tanto el API como el worker funcionan correctamente bajo carga ligera. Los resultados muestran:

- ✅ **API**: Tiempos de respuesta muy bajos y estables, con la mayoría de las peticiones completándose en menos de 500ms
- ✅ **Worker**: Procesamiento eficiente de videos con tiempos razonables y desglose predecible entre las diferentes fases (DB Fetch, S3 Download, FFmpeg, DB Update)
- ✅ **Recursos**: Uso moderado de CPU y memoria en todos los contenedores
- ✅ **Sin degradación**: No se observaron errores ni timeouts durante la prueba

Este escenario establece la **línea base de desempeño** del sistema y confirma que la arquitectura es sólida para cargas normales de operación.

#### Limitaciones del Worker en Cargas Altas

A partir del **Escenario 2 (Capacity Test)**, se identificó un cuello de botella crítico en la capa de procesamiento:

- ⚠️ **Con >50 videos encolados**: Los mensajes en la cola de Kafka permanecían en espera por tiempos significativamente mayores a los esperados
- ⚠️ **Con 200+ videos**: El tiempo de procesamiento completo superaba **30 minutos**, haciendo impráctico esperar la finalización del procesamiento
- ⚠️ **Decisión metodológica**: Para pruebas de capacidad con 250+ usuarios, se **excluyeron las métricas del worker** del análisis, enfocándose únicamente en la capacidad del API para aceptar solicitudes

**Implicaciones:**

- El throughput del worker (con configuración actual de 1 worker) es insuficiente para procesar la carga generada por ~100 usuarios concurrentes
- El procesamiento de video con FFmpeg es CPU-intensivo y secuencial, creando un backlog que crece más rápido de lo que puede ser procesado
- Se requiere **escalamiento horizontal** (más workers) para manejar picos de carga sostenidos

### 14.3 Limitaciones de la Herramienta de Pruebas (Newman)

La elección de **Newman** como herramienta de generación de carga presentó limitaciones significativas:

- ❌ **Sin concurrencia real**: Newman ejecuta iteraciones secuencialmente con delays configurados, pero no genera **usuarios verdaderamente paralelos** como lo hace JMeter
- ❌ **No se alcanzó el punto de ruptura del API**: En ninguna de las pruebas (50, 100, 150, 200, 250, 300 "usuarios") se logró saturar o tumbar el API
- ✅ **Validación con Postman**: La prueba del **EscenarioExtra** con Postman Collection Runner demostró que incluso con **100 usuarios concurrentes reales** y casi **6,000 peticiones**, el API mantuvo estabilidad sin errores críticos

**Conclusión clave**: El API tiene una **capacidad mucho mayor** de la que pudimos medir con Newman. Las pruebas actuales validan la estabilidad bajo carga secuencial incremental, pero no determinan el límite real de concurrencia del sistema.

**Posibles Mejoras para futuros tests:**

- Migrar a **Apache JMeter** o **k6** para pruebas de carga con concurrencia real
- Ejecutar pruebas con 500, 1000, 2000+ usuarios concurrentes simultáneos
- Configurar múltiples workers (2, 4, 8) para validar escalamiento horizontal
- Implementar monitoreo de métricas de Kafka (lag de consumidores, throughput de mensajes)

---

