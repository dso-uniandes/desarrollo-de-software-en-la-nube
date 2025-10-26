## Plan B — Rendimiento de la capa Worker (videos/min)

### Objetivo
Medir videos/min procesados por el/los worker(s) a distintos niveles de paralelismo y tamaños de archivo, identificando puntos de saturación y cuellos de botella.

### Alcance y setup
- **Bypass web**: inyección directa a Kafka `video_tasks` con `capacity-planning/worker_load_producer.py`.
- **Seeding**: generación/registro de videos de prueba (50 MB, 100 MB) con `capacity-planning/seed_videos.py`.
- **Monitoreo**: `monitor_resources.sh` y `monitor_worker.sh` activados via Makefile; lag Kafka opcional con `check_kafka_lag.sh`.
- **Resultados**: CSV/JSON/PNG en `capacity-planning/postman/results/`.

### Matriz de pruebas
- **Tamaños**: 50 MB, 100 MB
- **Paralelismo**: 1, 2, 4 workers (procesos)
- Para cada combinación ejecutar:
  - **Saturación**: gran volumen (crece backlog) para ubicar saturación y cuellos.
  - **Sostenida**: ritmo estable (lag ≈ 0) para validar estabilidad.

### Procedimiento resumido
1) Iniciar servicios: `make -C ./capacity-planning/ up`
2) Sembrar videos: `make -C ./capacity-planning/ worker-seed`
3) Escalar workers: `docker compose -f ./docker-compose.yml up -d --scale worker=<1|2|4>`
4) Ejecutar prueba (por combinación):
   - Saturación: `make -C ./capacity-planning/ worker-saturate`
   - Sostenida: `make -C ./capacity-planning/ worker-sustained` y opcional `worker-lag`
5) Ver estadísticas y gráficas: `make -C ./capacity-planning/ view-stats` y `open-graphs`

### Tabla de resultados (llenar con los datos obtenidos)

| Tamaño | Workers | Prueba | Videos/min (avg) | S (avg s/video) | p95 (s) | Error rate | CPU worker avg | Lag medio |
|--------|---------|--------|------------------:|-----------------:|--------:|-----------:|---------------:|---------:|
| 50 MB  | 1       | Sostenida  |                  |                  |         |            |                |          |
| 50 MB  | 1       | Saturación |                  |                  |         |            |                |          |
| 50 MB  | 2       | Sostenida  |                  |                  |         |            |                |          |
| 50 MB  | 2       | Saturación |                  |                  |         |            |                |          |
| 50 MB  | 4       | Sostenida  |                  |                  |         |            |                |          |
| 50 MB  | 4       | Saturación |                  |                  |         |            |                |          |
| 100 MB | 1       | Sostenida  |                  |                  |         |            |                |          |
| 100 MB | 1       | Saturación |                  |                  |         |            |                |          |
| 100 MB | 2       | Sostenida  |                  |                  |         |            |                |          |
| 100 MB | 2       | Saturación |                  |                  |         |            |                |          |
| 100 MB | 4       | Sostenida  |                  |                  |         |            |                |          |
| 100 MB | 4       | Saturación |                  |                  |         |            |                |          |

Notas para llenar la tabla:
- **Videos/min (avg)**: `60 / total_time.avg` del CSV `worker_timing_*.csv` (muestra `calculate_stats.py`).
- **S (avg s/video)** y **p95**: métricas de `total_time` en el resumen de consola/CSV.
- **CPU worker avg**: `container_stats_*.csv` (métrica cpu_percent del contenedor `worker`).
- **Lag medio**: promedio de `lag` en `consumer_lag_*.csv` (si se ejecutó `worker-lag`).

### Evidencias
- `capacity-planning/postman/results/worker_timing_<ts>.csv` — descomposición por tarea (DB, S3, FFmpeg, DB update).
- `capacity-planning/postman/results/container_stats_<ts>.csv` — CPU/Mem/Net/Disk por contenedor.
- `capacity-planning/postman/results/consumer_lag_<ts>.csv` — lag del consumer group (opcional).
- Gráficas generadas por `generate_graphs.py`.

### Hallazgos y cuellos de botella (completar)
- 50 MB @ 1 worker: …
- 50 MB @ 4 workers: …
- 100 MB @ 1/2/4 workers: …
- Principales cuellos (CPU FFmpeg / IO disco / red / lectura S3 local): …

### Conclusiones
- Capacidad nominal por configuración (videos/min): …
- Estabilidad de cola en sostenidas (lag ≈ 0 sí/no): …
- Punto(s) de saturación observados y síntomas: …

### Recomendaciones
- **Escalamiento horizontal**: ajustar número de workers según objetivo X videos/min.
- **Optimización FFmpeg**: presets, menor bitrate/resolución si la calidad lo permite.
- **IO/almacenamiento**: disco temporal más rápido o aumentar paralelismo de lectura/escritura.
- **Broker**: particionar tópico si se requiere paralelismo mayor (balanceo por particiones).


