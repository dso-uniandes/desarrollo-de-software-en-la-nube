# Plan de Pruebas

## Objetivo(s)

- Validar el desempeño, estabilidad y escalabilidad del API bajo diferentes perfiles de carga, garantizando tiempos de respuesta objetivo y baja tasa de errores.
- Asegurar que las rutas con operaciones intensivas (ranking con agregaciones y caché, votos con invalidación de caché, subida y streaming de video) cumplen con criterios de aceptación medibles.

## Objetivo (refinado para esta entrega)

- Ejecutar escenarios de prueba para medir la capacidad máxima de componentes clave y reportarla en el documento de análisis de capacidad, con escenarios de acceso, carga, estrés y utilización.
- Enfoque práctico en `POST /api/videos/upload` para la capa Web y definición de Plan B para la capa Worker.

## Objetivos específicos

- Medir p50/p90/p95/p99 de latencia, RPS sostenido, error rate (< 1%), y throughput por endpoint.
- Verificar eficacia del caché en `GET /api/ranking` (ratio de aciertos y latencia) y coherencia tras operaciones de voto.
- Determinar el máximo de concurrencia estable por endpoint antes de degradación (capacidad) y el comportamiento ante picos (estrés/spikes).
- Evaluar impacto en infraestructura: CPU, memoria, IO, red y base de datos (conexiones, latencia de consultas, bloqueos), así como en el worker de procesamiento de video.

## Descripción general

El sistema es un API FastAPI con endpoints de autenticación, gestión de videos (subida/listado/detalle/borrado/streaming), votos y ranking. Utiliza base de datos SQL (SQLAlchemy async), almacenamiento S3/local, mensajería (Kafka) para procesamiento asíncrono de video y caché opcional (Redis) para ranking. Se someterán las rutas a cargas simuladas con rampas, plateaus y picos para observar latencia, throughput y estabilidad.

## Tipos de pruebas

- Pruebas de capacidad: determinar concurrentes máximos manteniendo p95 objetivo y error rate < 1%.
- Pruebas de carga: rampas ascendentes/descendentes y plateaus por endpoint crítico.
- Pruebas de estrés: sobrepasar límites previstos hasta degradación y evaluar recuperación.
- Pruebas de picos: incrementos instantáneos 10x–20x en 10–30 s para ranking y votos.
- Pruebas de concurrencia específica: colisiones de voto, invalidación de caché y consistencia del ranking.
- Pruebas de resistencia (soak): 1–2 h a carga media para detectar fugas y degradación temporal.
- Pruebas de escalabilidad: comparar 1 vs N réplicas de API y del worker de video.

## Criterios de aceptación

- `GET /api/ranking`: p95 ≤ 200 ms hasta 300 concurrentes, error rate < 1%, cache hit ≥ 80% (con TTL configurado), coherencia ≤ 2 s tras votos.
- `POST /api/videos/vote` y `DELETE /api/videos/{id}/vote`: p95 ≤ 150 ms hasta 300 concurrentes; sin duplicados (constraint única); invalidación de caché efectiva.
- `GET /api/videos` y `GET /api/videos/{id}`: p95 ≤ 200 ms hasta 300 concurrentes; 404/403/500 controlados.
- `POST /api/auth/login`: p95 ≤ 150 ms hasta 200 concurrentes; tokens válidos devueltos; errores 400 para credenciales inválidas.
- `POST /api/videos/upload`: tiempo de aceptación (respuesta) ≤ 2 s con archivos de 5/50/100 MB; 400 para tipo/tamaño inválido.
- `GET /api/videos/stream/{file_path}`: TTFB ≤ 200 ms, bitrate estable; 20–50 streams concurrentes sin cortes.

## Datos de prueba

- Usuarios sintéticos (1k–10k) con ciudades variadas y tokens válidos precalculados para carga.
- Videos de prueba: 5 MB, 50 MB, 100 MB; rutas válidas para `stream` y rutas inexistentes (para 404).
- Votos masivos sobre un conjunto de `video_id` con mezcla equilibrada like/dislike.
- Semillas de DB para tener videos en `status="processed"` durante pruebas de votos/ranking.
- Nota: anonimizar datos si se usan datos reales.

## Iteraciones

- Repetir cada escenario 5–10 veces; registrar media, desviación y percentiles; identificar y justificar atípicos. Mantener un baseline por iteración del desarrollo.

## Configuración del sistema

- Arquitectura:
  - FastAPI (`storeapi.main`) con routers de `auth`, `videos`, `votes`, `ranking`.
  - DB SQL asíncrona (`storeapi.database`) via `DATABASE_URL`.
  - Almacenamiento S3/local (`utils.s3.s3_local`).
  - Caché Redis opcional (`REDIS_URL`), usado en `GET /api/ranking` con TTL `RANKING_CACHE_TTL` e invalidación al votar.
  - Mensajería Kafka para procesamiento de video (topic `video_tasks`).
  - Nginx como proxy (si aplica en despliegue docker-compose).
- Infraestructura (llenar según entorno de pruebas): CPU, Memoria, Disco, Red, versión SO, versión Python, versiones Nginx/Kafka/Redis/DB.
- Sistemas externos: S3/local, Kafka, Redis.
- Variables relevantes: `DATABASE_URL`, `REDIS_URL`, `AWS_*`, `KAFKA_BOOTSTRAP_SERVERS`, `APP_HOST`, `UPLOADED_FOLDER`, `PROCESSED_FOLDER`.
- Ambiente: ejecutar pruebas en el mismo segmento de red del servidor para evitar sesgos por latencia.

## Infraestructura requerida (recomendación)

- Ejecutar las pruebas desde equipo/entorno local o instancia independiente (evitar cuentas educativas/Academy para pruebas intensivas).
- Crear la instancia de cómputo del generador de carga según requisitos del plan (CPU, RAM, red) para no ser cuello de botella.

## Herramientas para la prueba

- Generación de carga:
  - Postman/Newman para `upload` multipart y escenarios parametrizados.
- Monitoreo:
  - Sistema: `glances`, `htop`, `iostat`, `nload`.
  - Base de datos: métricas de conexiones y latencia (según motor).
  - Aplicación: logs estructurados; considerar habilitar `CorrelationIdMiddleware` para trazabilidad.
- Reportería: exportación CSV/JSON y gráficos de p95/RPS/CPU.

## Métricas

- Aplicación: p50/p90/p95/p99, RPS, error rate, tamaño de respuesta, latencia de caché.
- Infra: CPU, memoria, disco, red, file descriptors, GC (si aplica), uso de disco en `stream`.
- DB: conexiones activas, latencia de consultas, locks, cache hit del motor.
- Caché: hit/miss ratio, latencia `cache_get`/`cache_set`, tamaño de claves `ranking:*`.
- Cola/worker: tiempo desde encolado a `status=processed`, errores de procesamiento.

## Perfiles de carga

- Rampas ascendentes: iniciar en 100 concurrentes e incrementar de 50 en 50 (100, 150, 200, 250, 300, ...).
- Rampas descendentes: simétricas para observar recuperación.
- Plateaus: mantener 3–5 minutos por escalón para estabilizar mediciones.
- Spikes: 10x–20x durante 20–30 s sobre `ranking` y `votes`.
- Mezcla de tráfico de referencia:
  - 50% `GET /api/ranking`
  - 20% `GET /api/videos`
  - 10% `POST /api/videos/vote`
  - 10% `GET /api/videos/{id}`
  - 10% `POST /api/auth/login`
- Think time: 0.2–1.5 s aleatorio según escenario.

## Ejecución

1. Preparación:
   - Desplegar API, DB, Redis (opcional), Kafka y worker.
   - Sembrar usuarios y videos `processed`; generar tokens.
   - Verificar conectividad y healthchecks.
2. Monitoreo:
   - Iniciar herramientas de host/DB/app antes de la carga.
3. Pruebas por endpoint (ver escenarios):
   - Ejecutar rampas/plateaus/spikes; capturar resultados y logs.
4. Cierre:
   - Consolidar métricas, calcular percentiles, comparar con criterios de aceptación.
   - Registrar hallazgos y acciones de mejora.

## Escenarios por endpoint

- Autenticación
  - `POST /api/auth/login`: válidos vs inválidos (400), medir p95 y error rate; prueba de 200 concurrentes.
  - `POST /api/auth/signup`: tasa moderada para validar constraints de email único.
- Videos
  - `POST /api/videos/upload`: multipart 5/50/100 MB; medir tiempo de aceptación; validar 400 por tipo/tamaño.
  - `GET /api/videos`: 100–300 concurrentes con tokens válidos.
  - `GET /api/videos/{id}`: 100–300 concurrentes; validar 403 cuando no es del usuario; 404 inexistente.
  - `DELETE /api/videos/{id}`: validar reglas de negocio (no borrar `processed`).
  - `GET /api/videos/stream/{file_path}`: 20–50 concurrentes; medir TTFB y estabilidad; validar 404.
- Votos
  - `POST /api/videos/vote`: ráfagas de votos, conflictos por (user_id, video_id), p95 ≤ 150 ms; invalidación de caché.
  - `DELETE /api/videos/{id}/vote`: retiro de voto y coherencia.
  - `GET /api/videos/{id}/votes`: lectura bajo carga moderada.
  - `GET /api/videos/public/all`: lectura de todos los videos `processed` con votos.
- Ranking
  - `GET /api/ranking`: con/sin `city`, paginación `offset/limit`; verificar primera llamada cache miss y siguientes hits; coherencia tras votos.

## Ejemplos de ejecución

Nota: reemplace `HOST` y `TOKEN` según su entorno. Ejecute desde el mismo segmento de red del servidor.

### Postman/Newman (upload)

- Colección: `postman/collection.json` (incluye `POST /api/auth/login` y `POST /api/videos/upload`).
- Entorno: `postman/environment.json` (HOST, EMAIL, PASSWORD, TOKEN).
- Variables previas: ejecutar login y guardar `access_token` como `{{TOKEN}}`.
- Upload (1 MB por defecto; parametrizable a 10/50/100 MB):
  - Iteraciones y concurrencia con Newman (CLI + reporters):
  ```
  newman run postman/collection.json \
    -e postman/environment.json \
    --iteration-count 1000 \
    --folder "upload" \
    --reporters cli,html \
    --reporter-html-export postman/report.html
  ```

Nota: Para concurrencia, ejecute múltiples instancias de Newman en paralelo (p. ej., 5 procesos × 200 iteraciones) en la misma máquina de carga, o use herramientas como `newman-reporter-htmlextra` y un orquestador de procesos.

## Automatización y ejecución

- Makefile (objetivos principales):
  - `up`, `login`, `seed`, `monitor-start`/`monitor-stop`
  - `ab-ranking`, `ab-vote`, `ab-login`
  - `ab-parse`, `cpu-parse`, `report`
  - `newman` (ejecución de colección Postman y reporter HTML)

- Spike tests:
  - (N/A) Eliminado uso de AB; todo se ejecuta vía Newman.

- Escalabilidad (2 réplicas):
  - Eliminar `container_name` del servicio `storeapi` y escalar:
  ```
  docker-compose up -d --scale storeapi=2
  ```
  - Probar con y sin `-k` (keep-alive). Sin `-k` puede requerir ajustar buffering/timeouts en Nginx.

- Upload (Postman/Newman):
  - Colección `postman/collection.json` (folder Upload) y entorno `postman/environment.json`.
  - Ejecutar: `newman run postman/collection.json -e postman/environment.json -r cli,html --reporter-html-export postman/report.html`

- Streaming:
  - Crear archivo visible para la app en `/app` (volumen montado) y probar concurrencia:
  ```
  dd if=/dev/zero of=videos/processed/test.mp4 bs=1024 count=2048
  for i in $(seq 1 10); do curl -s -o /dev/null -w "%{http_code}\n" \
    "http://HOST/api/videos/stream//app/videos/processed/test.mp4" & done; wait
  ```

## Escenario 1 — Capacidad de la capa Web (upload)

- Objetivo: determinar usuarios concurrentes (VUs) y RPS que soporta `POST /api/videos/upload` cumpliendo SLOs, sin límite de la capa asíncrona.
- Estrategia:
  - Desacoplar worker (sugerido): en pruebas de web, devolver 202/mocking cola para aceptación instantánea. Alternativa: medir solo tiempo de aceptación 201.
  - Simular archivos reales (1/10/50/100 MB) y ejecutar desde el mismo segmento de red.
- Escenarios:
  - Smoke: 5 VUs, 1 min.
  - Ramp: 0→X VUs en 3 min; hold 5 min. Repetir con X creciente hasta degradación.
  - Sostenida corta: 5 min al 80% de X (nivel sin degradación) para validar estabilidad.
- Criterios de éxito/fallo:
  - p95 ≤ 1 s; errores (4xx evitables/5xx) ≤ 5%; sin resets/timeouts anómalos.
  - Si se supera capacidad, registrar el primer KPI degradado (CPU API, ancho de banda, etc.).
- Herramientas: Postman (+Newman).
- Salidas: curva usuarios→latencia/errores; RPS a capacidad máxima; evidencias de bottlenecks.

## Plan B — Rendimiento de la capa Worker (videos/min)

- Objetivo: medir videos/min procesados a distintos tamaños y paralelismo.
- Estrategia:
  - Bypass web: inyectar mensajes en la cola (Kafka `video_tasks`) con payloads realistas (rutas/IDs).
- Diseño experimental:
  - Tamaños: 50 MB, 100 MB. Paralelismo: 1/2/4 procesos por nodo (o múltiples workers).
  - Por combinación: saturación (aumentar tareas) y sostenida (mantener backlog fijo).
- Métricas/calculos: videos/min; tiempo medio de servicio por video.
- Criterios de éxito/fallo: capacidad nominal estable; la cola no crece (pendiente ~0) durante sostenidas.
- Herramientas: productor Python/Go hacia Kafka; trazabilidad (enqueue→start→end); perfilado CPU/IO/red.
- Salidas: tabla capacidad por tamaño/configuración; puntos de saturación y cuellos de botella.

## Reportería

- Guardar resultados en CSV/JSON, calcular percentiles y RPS, graficar RPS vs p95 y error rate por escalón.
- Documentar configuraciones de cada corrida (infra, versiones, variables). Incluir capturas de monitoreo (CPU/Mem/IO/DB). Publicar documento y resultados en el repositorio (GitHub/GitLab).

## Medición de CPU y monitoreo

- Docker (captura a archivo durante la prueba):
```
while true; do \
  date "+%F %T"; \
  docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}}" \
    storeapi anb-nginx anb-database anb-redis kafka anb-worker; \
  sleep 1; \
done | tee cpu_stats.log
```

- Visual en vivo:
```
watch -n 1 'docker stats --no-stream storeapi anb-nginx anb-database anb-redis kafka anb-worker'
```

- macOS host (Glances):
```
brew install glances
glances
# o modo web
glances -w  # abrir http://localhost:61208
```

- Recomendaciones:
  - Iniciar captura 30 s antes y terminar 30 s después de cada prueba.
  - Correlacionar timestamps del monitor de CPU y logs de la app con la ejecución de Newman.
  - Observar especialmente `storeapi` (CPU app), `anb-database` (DB) y `anb-worker` (procesamiento).

## Trazabilidad y baseline

- Mantener una tabla/registro por iteración con: versión del API, commit, configuración, criterios y resultados clave (p95, RPS, error rate). Usar la primera corrida como baseline y comparar mejoras/regresiones.

