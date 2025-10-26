SHELL := /bin/bash

# Detect docker compose command (v2 plugin or legacy binary)
# Falls back to "docker-compose" if "docker compose" plugin is not available
DOCKER_COMPOSE := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || (command -v docker-compose >/dev/null 2>&1 && echo "docker-compose" || echo "docker compose"))

HOST ?= http://localhost
EMAIL ?= test@example.com
PASSWORD ?= pass123
DOCKER_COMPOSE_FILE := ../docker-compose.yml
RESULTS_DIR := postman/results
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)

.PHONY: up down ps newman newman-with-monitor monitor-start monitor-stop \
        test-smoke test-capacity test-ramp test-sustained test-stress test-spike \
        test-all run-all-tests clean-results help view-stats calculate-stats \
        monitor-interactive show-results open-latest-report kill-monitors install-deps \
        worker-seed worker-saturate worker-sustained worker-lag

# =============================================================================
# Setup
# =============================================================================

install-deps:
	@echo "📦 Installing capacity planning dependencies..."
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "⚠️  Warning: No virtual environment detected!"; \
		echo "   Consider activating a venv first:"; \
		echo "   source ../.venv/bin/activate"; \
		echo ""; \
		read -p "Continue anyway? (y/n) " -n 1 -r; \
		echo; \
		if [[ ! $$REPLY =~ ^[Yy]$$ ]]; then \
			exit 1; \
		fi \
	fi
	pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully!"

# =============================================================================
# Infrastructure Management
# =============================================================================

up:
	@echo "🚀 Starting all services..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo "✅ Services are up!"

down:
	@echo "🛑 Stopping all services..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down -v
	@echo "✅ Services stopped!"

ps:
	@echo "📊 Container Status:"
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps

# =============================================================================
# Monitoring
# =============================================================================

monitor-start:
	@echo "📊 Starting enhanced monitoring (containers + worker)..."
	@mkdir -p $(RESULTS_DIR)
	@chmod +x monitor_resources.sh monitor_worker.sh 2>/dev/null || true
	@TS=$$(date +%Y%m%d_%H%M%S); \
	 echo $$TS > .current_test_ts; \
	 nohup bash monitor_resources.sh $(RESULTS_DIR) $$TS > /dev/null 2>&1 & echo $$! > .monitor_resources.pid; \
	 nohup bash monitor_worker.sh $(RESULTS_DIR) $$TS > /dev/null 2>&1 & echo $$! > .monitor_worker.pid; \
	 echo "✅ Container monitor started (PID=$$(cat .monitor_resources.pid))"; \
	 echo "✅ Worker monitor started (PID=$$(cat .monitor_worker.pid))"; \
	 echo "📁 Results: $(RESULTS_DIR)/container_stats_$$TS.csv"; \
	 echo "📁 Results: $(RESULTS_DIR)/worker_timing_$$TS.csv"

monitor-stop:
	@echo "🛑 Stopping monitors and calculating statistics..."
	@# Wait for worker to finish processing tasks (10 minutes timeout for large batches)
	@chmod +x wait_for_worker.sh 2>/dev/null || true
	@./wait_for_worker.sh 3600 || true
	@echo ""
	@# Stop monitoring processes
	@if [ -f .monitor_resources.pid ]; then \
		echo "Stopping container monitor (PID=$$(cat .monitor_resources.pid))..."; \
		kill -TERM $$(cat .monitor_resources.pid) 2>/dev/null || true; \
		rm .monitor_resources.pid; \
	fi
	@if [ -f .monitor_worker.pid ]; then \
		echo "Stopping worker monitor (PID=$$(cat .monitor_worker.pid))..."; \
		kill -TERM $$(cat .monitor_worker.pid) 2>/dev/null || true; \
		rm .monitor_worker.pid; \
	fi
	@echo "Killing any orphaned monitor processes..."
	@pkill -f "monitor_resources.sh" 2>/dev/null || true
	@pkill -f "monitor_worker.sh" 2>/dev/null || true
	@sleep 2
	@TS=$$(cat .current_test_ts 2>/dev/null || echo ""); \
	 if [ -n "$$TS" ] && [ -f "$(RESULTS_DIR)/container_stats_$$TS.csv" ] && [ -f "calculate_stats.py" ]; then \
		echo "📊 Calculating statistics for $$TS ..."; \
		python3 calculate_stats.py $$TS || echo "⚠️  Stats calculation skipped"; \
		echo "📊 Generating graphs for $$TS ..."; \
		python3 generate_graphs.py $$TS || echo "⚠️  Graph generation skipped"; \
	 else \
		echo "⚠️  Missing timestamp or container stats; skipping stats/graphs"; \
	 fi; \
	 rm -f .current_test_ts 2>/dev/null || true
	@echo "✅ Monitoring stopped"

monitor-interactive:
	@echo "🔍 Launching interactive monitor..."
	@chmod +x monitor.sh 2>/dev/null || true
	@./monitor.sh

# =============================================================================
# Basic Newman Execution
# =============================================================================

newman-basic:
	@echo "🧪 Running basic Newman test..."
	@mkdir -p $(RESULTS_DIR)
	newman run postman/collection.json \
		-e postman/environment.json \
		-r cli,html,json \
		--reporter-html-export $(RESULTS_DIR)/report_$(TIMESTAMP).html \
		--reporter-json-export $(RESULTS_DIR)/report_$(TIMESTAMP).json

newman-with-monitor:
	@echo "🧪 Running Newman with monitoring..."
	@$(MAKE) monitor-start
	@newman run postman/collection.json \
		-e postman/environment.json \
		-r cli,html,json \
		--reporter-html-export $(RESULTS_DIR)/report_basic_$(TIMESTAMP).html \
		--reporter-json-export $(RESULTS_DIR)/report_basic_$(TIMESTAMP).json || true
	@$(MAKE) monitor-stop

# =============================================================================
# Test Scenarios - Capacity Planning
# =============================================================================

test-smoke:
	@echo "🔥 Running SMOKE TEST (5 users, 1 min)..."
	@$(MAKE) monitor-start
	@newman run postman/collection.json \
		-e postman/environment.json \
		-n 5 \
		--delay-request 50 \
		-r cli,html,json \
		--reporter-html-export $(RESULTS_DIR)/report_smoke_$(TIMESTAMP).html \
		--reporter-json-export $(RESULTS_DIR)/report_smoke_$(TIMESTAMP).json || true
	@$(MAKE) monitor-stop
	@echo "✅ Smoke test completed! Report: $(RESULTS_DIR)/report_smoke_$(TIMESTAMP).html"

test-capacity:
	@echo "📈 Running CAPACITY TEST (incremental load)..."
	@echo "Testing with different user loads: 50, 100, 150, 200, 250, 300"
	@mkdir -p $(RESULTS_DIR)
	@for users in 250 300; do \
		echo ""; \
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
		echo "🔄 Testing with $$users concurrent users..."; \
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
		$(MAKE) monitor-start; \
		newman run postman/collection.json \
			-e postman/environment.json \
			-n $$users \
			--delay-request 20 \
			-r cli,html,json \
			--reporter-html-export $(RESULTS_DIR)/report_capacity_$${users}users_$(TIMESTAMP).html \
			--reporter-json-export $(RESULTS_DIR)/report_capacity_$${users}users_$(TIMESTAMP).json || true; \
		$(MAKE) monitor-stop; \
		echo "✅ Test with $$users users completed"; \
		echo "⏳ Cooling down for 30 seconds..."; \
		sleep 30; \
	done
	@echo "✅ Capacity test suite completed!"

test-ramp:
	@echo "📊 Running RAMP TEST (gradual increase)..."
	@echo "Simulating ramp: 50 → 100 → 200 → 300 users"
	@mkdir -p $(RESULTS_DIR)
	@for users in 50 100 200 300; do \
		echo ""; \
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
		echo "📈 Ramp step: $$users users (sustained 2 min)"; \
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
		$(MAKE) monitor-start; \
		newman run postman/collection.json \
			-e postman/environment.json \
			-n $$users \
			--delay-request 1 \
			-r cli,html,json \
			--reporter-html-export $(RESULTS_DIR)/report_ramp_$${users}users_$(TIMESTAMP).html \
			--reporter-json-export $(RESULTS_DIR)/report_ramp_$${users}users_$(TIMESTAMP).json || true; \
		$(MAKE) monitor-stop; \
		echo "✅ Ramp step $$users completed"; \
		sleep 20; \
	done
	@echo "✅ Ramp test completed!"

test-sustained:
	@echo "⏱️  Running SUSTAINED TEST (200 users, 5 min)..."
	@$(MAKE) monitor-start
	@newman run postman/collection.json \
		-e postman/environment.json \
		-n 200 \
		--delay-request 1 \
		-r cli,html,json \
		--reporter-html-export $(RESULTS_DIR)/report_sustained_$(TIMESTAMP).html \
		--reporter-json-export $(RESULTS_DIR)/report_sustained_$(TIMESTAMP).json || true
	@$(MAKE) monitor-stop
	@echo "✅ Sustained test completed!"

test-stress:
	@echo "💥 Running STRESS TEST (1000 users, pushing limits)..."
	@$(MAKE) monitor-start
	@newman run postman/collection.json \
		-e postman/environment.json \
		-n 1000 \
		--delay-request 1 \
		-r cli,html,json \
		--reporter-html-export $(RESULTS_DIR)/report_stress_$(TIMESTAMP).html \
		--reporter-json-export $(RESULTS_DIR)/report_stress_$(TIMESTAMP).json || true
	@$(MAKE) monitor-stop
	@echo "✅ Stress test completed!"

test-spike:
	@echo "⚡ Running SPIKE TEST (sudden burst: 20 → 400 → 20)..."
	@mkdir -p $(RESULTS_DIR)
	@echo "Phase 1: Baseline (20 users)"
	@$(MAKE) monitor-start
	@newman run postman/collection.json \
		-e postman/environment.json \
		-n 20 \
		--delay-request 0 \
		-r cli,html,json \
		--reporter-html-export $(RESULTS_DIR)/report_spike_baseline_$(TIMESTAMP).html \
		--reporter-json-export $(RESULTS_DIR)/report_spike_baseline_$(TIMESTAMP).json || true
	@$(MAKE) monitor-stop
	@echo "Phase 2: SPIKE (400 users)"
	@$(MAKE) monitor-start
	@newman run postman/collection.json \
		-e postman/environment.json \
		-n 400 \
		--delay-request 5 \
		-r cli,html,json \
		--reporter-html-export $(RESULTS_DIR)/report_spike_burst_$(TIMESTAMP).html \
		--reporter-json-export $(RESULTS_DIR)/report_spike_burst_$(TIMESTAMP).json || true
	@$(MAKE) monitor-stop
	@echo "Phase 3: Recovery (20 users)"
	@$(MAKE) monitor-start
	@newman run postman/collection.json \
		-e postman/environment.json \
		-n 20 \
		--delay-request 20 \
		-r cli,html,json \
		--reporter-html-export $(RESULTS_DIR)/report_spike_recovery_$(TIMESTAMP).html \
		--reporter-json-export $(RESULTS_DIR)/report_spike_recovery_$(TIMESTAMP).json || true
	@$(MAKE) monitor-stop
	@echo "✅ Spike test completed!"

# =============================================================================
# Comprehensive Test Execution
# =============================================================================

test-all: clean-results
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  🚀 COMPREHENSIVE CAPACITY TEST SUITE                     ║"
	@echo "║  Following the capacity planning document                 ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📋 Test sequence:"
	@echo "  1. Smoke Test (validation)"
	@echo "  2. Capacity Test (find limits)"
	@echo "  3. Ramp Test (gradual increase)"
	@echo "  4. Sustained Test (stability)"
	@echo "  5. Stress Test (breaking point)"
	@echo "  6. Spike Test (burst recovery)"
	@echo ""
	@read -p "⚠️  This will take ~45-60 minutes. Continue? [y/N] " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		echo "❌ Test suite cancelled"; \
		exit 1; \
	fi
	@echo ""
	@echo "Starting test suite at $$(date)..."
	@$(MAKE) test-smoke
	@$(MAKE) test-capacity
	@$(MAKE) test-ramp
	@$(MAKE) test-sustained
	@$(MAKE) test-stress
	@$(MAKE) test-spike
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  ✅ ALL TESTS COMPLETED!                                   ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📊 Results available in: $(RESULTS_DIR)/"
	@echo "🔍 To analyze results, open HTML reports in your browser"
	@echo ""
	@$(MAKE) show-results

run-all-tests: up test-all
	@echo "✅ Complete test cycle finished!"
	@echo "⚠️  Remember to run 'make down' when finished to stop services"

# =============================================================================
# Results Management
# =============================================================================

show-results:
	@echo "📊 Test Results Summary:"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@if [ -d "$(RESULTS_DIR)" ]; then \
		echo ""; \
		echo "📄 HTML Reports:"; \
		ls -lh $(RESULTS_DIR)/*.html 2>/dev/null | awk '{print "  " $$9 " (" $$5 ")"}' || echo "  ⚠️  No HTML reports found"; \
		echo ""; \
		echo "📊 CSV Data Files:"; \
		ls -lh $(RESULTS_DIR)/*.csv 2>/dev/null | awk '{print "  " $$9 " (" $$5 ")"}' || echo "  ⚠️  No CSV files found"; \
		echo ""; \
		echo "� Graph Files:"; \
		ls -lh $(RESULTS_DIR)/*.png 2>/dev/null | awk '{print "  " $$9 " (" $$5 ")"}' || echo "  ⚠️  No graph files found"; \
		echo ""; \
		echo "�📋 Log Files:"; \
		ls -lh $(RESULTS_DIR)/*.log 2>/dev/null | awk '{print "  " $$9 " (" $$5 ")"}' || echo "  ⚠️  No log files found"; \
	else \
		echo "  ⚠️  Results directory not found"; \
	fi
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

clean-results:
	@echo "🧹 Cleaning old test results..."
	@echo "Stopping any running monitors..."
	@pkill -f "monitor_resources.sh" 2>/dev/null || true
	@pkill -f "monitor_worker.sh" 2>/dev/null || true
	@rm -f .monitor*.pid 2>/dev/null || true
	@echo "Removing result files..."
	@rm -rf $(RESULTS_DIR)/*.html $(RESULTS_DIR)/*.csv $(RESULTS_DIR)/*.log 2>/dev/null || true
	@echo "✅ Results cleaned!"

kill-monitors:
	@echo "🔪 Killing all monitoring processes..."
	@pkill -f "monitor_resources.sh" 2>/dev/null && echo "  ✓ Killed monitor_resources.sh" || echo "  ℹ️  No monitor_resources.sh running"
	@pkill -f "monitor_worker.sh" 2>/dev/null && echo "  ✓ Killed monitor_worker.sh" || echo "  ℹ️  No monitor_worker.sh running"
	@rm -f .monitor*.pid 2>/dev/null || true
	@echo "✅ All monitors stopped!"

open-latest-report:
	@echo "🔍 Opening latest test report..."
	@latest=$$(ls -t $(RESULTS_DIR)/report_*.html 2>/dev/null | head -1); \
	if [ -n "$$latest" ]; then \
		open "$$latest"; \
	else \
		echo "❌ No reports found"; \
	fi

open-graphs:
	@echo "📈 Opening latest test graphs..."
	@graphs=$$(ls -t $(RESULTS_DIR)/*.png 2>/dev/null | head -3); \
	if [ -n "$$graphs" ]; then \
		for graph in $$graphs; do \
			echo "  Opening $$graph"; \
			open "$$graph"; \
		done; \
	else \
		echo "❌ No graphs found"; \
	fi

view-stats:
	@echo "📊 Available test results:"
	@echo ""
	@if [ -d "$(RESULTS_DIR)" ]; then \
		ls -t $(RESULTS_DIR)/summary_*.csv 2>/dev/null | head -5 | while read file; do \
			timestamp=$$(basename "$$file" | sed 's/summary_//' | sed 's/.csv//'); \
			echo "  🔹 $$timestamp"; \
		done; \
		echo ""; \
		read -p "Enter timestamp to view (or press Enter for latest): " ts; \
		if [ -z "$$ts" ]; then \
			ts=$$(ls -t $(RESULTS_DIR)/summary_*.csv 2>/dev/null | head -1 | xargs basename | sed 's/summary_//' | sed 's/.csv//'); \
		fi; \
		if [ -n "$$ts" ]; then \
			echo ""; \
			if [ -f "$(RESULTS_DIR)/summary_$$ts.csv" ]; then \
				cat "$(RESULTS_DIR)/summary_$$ts.csv"; \
			else \
				echo "❌ Summary file not found: $(RESULTS_DIR)/summary_$$ts.csv"; \
			fi; \
		fi; \
	else \
		echo "  ⚠️  Results directory not found"; \
	fi

calculate-stats:
	@echo "📊 Calculate statistics for a specific test"
	@read -p "Enter timestamp (e.g., 20251019_143025): " ts; \
	if [ -n "$$ts" ]; then \
		python3 calculate_stats.py "$$ts"; \
		echo "📈 Generating graphs..."; \
		python3 generate_graphs.py "$$ts" || echo "⚠️  Graph generation skipped"; \
	else \
		echo "❌ Timestamp required"; \
	fi

# =============================================================================
# Help
# =============================================================================

help:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  📚 Capacity Planning Test Suite - Help                   ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "� Setup:"
	@echo "  make install-deps       - Install Python dependencies (matplotlib, etc.)"
	@echo ""
	@echo "�🔧 Infrastructure:"
	@echo "  make up                 - Start all services (API, Worker, DB, etc.)"
	@echo "  make down               - Stop and remove all services"
	@echo "  make ps                 - Show container status"
	@echo ""
	@echo "📊 Monitoring:"
	@echo "  make monitor-start      - Start background resource monitoring"
	@echo "  make monitor-stop       - Stop resource monitoring"
	@echo "  make monitor-interactive - Launch interactive monitor menu"
	@echo "  make kill-monitors      - Force kill all monitoring processes"
	@echo ""
	@echo "🧪 Individual Tests:"
	@echo "  make test-smoke         - Smoke test (5 users, quick validation)"
	@echo "  make test-capacity      - Capacity test (50→300 users)"
	@echo "  make test-ramp          - Ramp test (gradual load increase)"
	@echo "  make test-sustained     - Sustained test (200 users, 5 min)"
	@echo "  make test-stress        - Stress test (400 users, pushing limits)"
	@echo "  make test-spike         - Spike test (sudden burst pattern)"
	@echo ""
	@echo "🚀 Complete Test Suite:"
	@echo "  make test-all           - Run all tests sequentially (~45-60 min)"
	@echo "  make run-all-tests      - Start services + run all tests"
	@echo ""
	@echo "📁 Results:"
	@echo "  make show-results       - Display test results summary"
	@echo "  make view-stats         - View calculated statistics (interactive)"
	@echo "  make calculate-stats    - Calculate stats for specific test"
	@echo "  make clean-results      - Clean old test results"
	@echo "  make open-latest-report - Open most recent HTML report"
	@echo "  make open-graphs        - Open latest generated graphs"
	@echo ""
	@echo "💡 Quick Start:"
	@echo "  1. make up              - Start infrastructure"
	@echo "  2. make test-smoke      - Run quick validation"
	@echo "  3. make test-capacity   - Run capacity analysis"
	@echo "  4. make down            - Stop everything"
	@echo ""
	@echo "📖 All results saved to: $(RESULTS_DIR)/"
	@echo ""

# =============================================================================
# Worker Capacity Tests (Plan B)
# =============================================================================

worker-seed:
	@echo "🌱 Seeding test videos (50MB, 100MB)..."
	@mkdir -p $(RESULTS_DIR)
	@python3 seed_videos.py --user-id 1 --sizes 50,100 --count-per-size 1 --base-name captest > $(RESULTS_DIR)/seed_output_$(TIMESTAMP).json
	@echo "✅ Seed complete. Output: $(RESULTS_DIR)/seed_output_$(TIMESTAMP).json"

worker-saturate:
	@echo "🔥 Worker Saturation Test: enqueue many tasks quickly"
	@$(MAKE) monitor-start
	@seed_file=$$(ls -t $(RESULTS_DIR)/seed_output_*.json 2>/dev/null | head -1); \
	if [ -z "$$seed_file" ]; then \
		echo "❌ No seed output found. Run 'make -C ./capacity-planning/ worker-seed' first."; \
		exit 1; \
	fi; \
	jq -r '.video_ids | join(",")' "$$seed_file" | xargs -I{} sh -c \
	"python3 worker_load_producer.py --bootstrap localhost:9092 --video-ids {} --count 200 --rate 0" || true
	@$(MAKE) monitor-stop
	@echo "✅ Worker saturation test completed"

worker-sustained:
	@echo "⏱️  Worker Sustained Test: steady rate, check queue stability"
	@$(MAKE) monitor-start
	@seed_file=$$(ls -t $(RESULTS_DIR)/seed_output_*.json 2>/dev/null | head -1); \
	if [ -z "$$seed_file" ]; then \
		echo "❌ No seed output found. Run 'make -C ./capacity-planning/ worker-seed' first."; \
		exit 1; \
	fi; \
	jq -r '.video_ids | join(",")' "$$seed_file" | xargs -I{} sh -c \
	"python3 worker_load_producer.py --bootstrap localhost:9092 --video-ids {} --count 300 --rate 5" || true
	@$(MAKE) monitor-stop
	@echo "✅ Worker sustained test completed"

worker-lag:
	@echo "📉 Sampling Kafka consumer lag (group: video_tasks_group)"
	@chmod +x check_kafka_lag.sh 2>/dev/null || true
	@./check_kafka_lag.sh $(RESULTS_DIR) $(TIMESTAMP) video_tasks_group 120 5
	@echo "✅ Lag CSV saved to $(RESULTS_DIR)/consumer_lag_$(TIMESTAMP).csv"


