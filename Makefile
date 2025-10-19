SHELL := /bin/bash

HOST ?= http://localhost
EMAIL ?= test@example.com
PASSWORD ?= pass123

.PHONY: up down ps newman newman-with-monitor monitor-start monitor-stop

up:
	docker compose up -d

down:
	docker compose down -v

ps:
	docker compose ps

# Ejecutar colección de Postman con Newman (placeholder)
# Requiere tener newman instalado: npm install -g newman
# Variables y archivos se referenciarán desde postman/
newman:
	newman run postman/collection.json -e postman/environment.json -r cli,html --reporter-html-export postman/report.html

monitor-start:
	nohup sh -c 'while true; do date "+%F %T"; docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}}"; sleep 1; done' > postman/cpu_stats_newman.log 2>&1 & echo $$! > .monitor.pid; echo "Monitor iniciado PID=$$(cat .monitor.pid)"

monitor-stop:
	@if [ -f .monitor.pid ]; then kill $$(cat .monitor.pid) && rm .monitor.pid && echo "Monitor detenido"; else echo "No hay PID de monitor"; fi

newman-with-monitor:
	$(MAKE) monitor-start
	newman run postman/collection.json -e postman/environment.json -r cli,html --reporter-html-export postman/report.html
	$(MAKE) monitor-stop


