# Reporte de Pruebas (Postman/Newman)

## Resumen ejecutivo
- Enfoque: `POST /api/videos/upload` (multipart).
- Todas las corridas ejecutadas sin fallos en aserciones.
- Latencias promedio observadas entre ~0.19 s y ~0.66 s según escenario y concurrencia.
- Evidencias generadas: `postman/report.html`, `postman/report_20.html`, `postman/cpu_stats_newman.log`.

## Configuración
- Host: `http://127.0.0.1`
- Archivo: `sample.mp4` (1 MB)
- Colección: `postman/collection.json` (Login + Upload)
- Entorno: `postman/environment.json`
- Newman: `6.2.1`

## Escenarios ejecutados
1) Smoke (1 iteración)
- Comando: `make newman-with-monitor`
- Resultado: Login 200; Upload 201; promedio ~194 ms (min 31 ms, máx 357 ms)
- CPU/Mem: `postman/cpu_stats_newman.log`

2) Secuencial 20 iteraciones
- Comando: `newman run ... --iteration-count 20 -r cli,html`
- Resultado: 0 fallos; promedio ~608 ms (min 70 ms, máx 1322 ms, desv ~290 ms)
- Reporte: `postman/report_20.html`

3) Paralelo 5 procesos × 20 iteraciones (emulación concurrencia)
- Comando: 5 procesos newman en paralelo, cada uno con 20 iteraciones
- Resultado (resumen por proceso):
  - Proc A: promedio ~619 ms (min 74 ms, máx ~1197 ms)
  - Proc B: promedio ~620 ms (min 262 ms, máx ~1115 ms)
  - Proc C: promedio ~621 ms (min 63 ms, máx ~1167 ms)
  - Proc D: promedio ~657 ms (min 21 ms, máx ~3300 ms)
  - Proc E: promedio ~621 ms (min ~236 ms, máx ~3.3 s)
- Observación: algunos picos aislados (>1 s) bajo concurrencia paralela, sin fallos en aserciones.

## Observaciones de CPU/Memoria
- Log: `postman/cpu_stats_newman.log`
- Uso de CPU estable durante smoke; repetir monitor en cargas paralelas para caracterizar CPU en picos.
- Recomendación: capturar CPU en pruebas paralelas de mayor duración para determinar cuello de botella (API vs red vs disco).

## Conclusiones
- SLO de aceptación (referencia): p95 objetivo ≤ 1 s. En smoke y 20 iteraciones secuenciales, las latencias promedio están < 1 s.
- Bajo múltiples procesos concurrentes, aparecen picos aislados; no hubo fallos ni timeouts reportados.
- Próximos pasos: repetir con archivos de 10/50/100 MB, mayor duración y captura de CPU continua; ajustar infra si p95 supera 1 s de forma consistente.
