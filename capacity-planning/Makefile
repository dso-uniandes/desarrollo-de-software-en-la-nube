SHELL := /bin/bash

HOST ?= http://localhost
EMAIL ?= test@example.com
PASSWORD ?= pass123
DOCKER_COMPOSE_FILE := ../docker-compose.yml
RESULTS_DIR := postman/results
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)

.PHONY: up down ps newman newman-with-monitor monitor-start monitor-stop \
        test-smoke test-capacity test-ramp test-sustained test-stress test-spike \
        test-all run-all-tests clean-results help view-stats calculate-stats \
        monitor-interactive show-results open-latest-report kill-monitors

# =============================================================================
# Infrastructure Management
# =============================================================================

up:
	@echo "🚀 Starting all services..."
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo "✅ Services are up!"

down:
	@echo "🛑 Stopping all services..."
	docker compose -f $(DOCKER_COMPOSE_FILE) down -v
	@echo "✅ Services stopped!"

ps:
	@echo "📊 Container Status:"
	docker compose -f $(DOCKER_COMPOSE_FILE) ps

# =============================================================================
# Monitoring
# =============================================================================

monitor-start:
	@echo "📊 Starting enhanced monitoring (containers + worker)..."
	@mkdir -p $(RESULTS_DIR)
	@chmod +x monitor_resources.sh monitor_worker.sh 2>/dev/null || true
	@nohup bash monitor_resources.sh $(RESULTS_DIR) $(TIMESTAMP) > /dev/null 2>&1 & echo $$! > .monitor_resources.pid
	@nohup bash monitor_worker.sh $(RESULTS_DIR) $(TIMESTAMP) > /dev/null 2>&1 & echo $$! > .monitor_worker.pid
	@echo "✅ Container monitor started (PID=$$(cat .monitor_resources.pid))"
	@echo "✅ Worker monitor started (PID=$$(cat .monitor_worker.pid))"
	@echo "📁 Results: $(RESULTS_DIR)/container_stats_$(TIMESTAMP).csv"
	@echo "📁 Results: $(RESULTS_DIR)/worker_timing_$(TIMESTAMP).csv"

monitor-stop:
	@echo "🛑 Stopping monitors and calculating statistics..."
	@# Wait for worker to finish processing tasks
	@chmod +x wait_for_worker.sh 2>/dev/null || true
	@./wait_for_worker.sh 180 || true
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
	@if [ -f "$(RESULTS_DIR)/container_stats_$(TIMESTAMP).csv" ] && [ -f "calculate_stats.py" ]; then \
		echo "📊 Calculating statistics..."; \
		python3 calculate_stats.py $(TIMESTAMP) || echo "⚠️  Stats calculation skipped"; \
	fi
	@echo "✅ Monitoring stopped"

monitor-interactive:
	@echo "🔍 Launching interactive monitor..."
	@chmod +x monitor.sh 2>/dev/null || true
	@./monitor.sh

# =============================================================================
# Basic Newman Execution
# =============================================================================

newman:
	@echo "🧪 Running Newman collection..."
	@mkdir -p $(RESULTS_DIR)
	newman run postman/collection.json \
		-e postman/environment.json \
		-r cli,html \
		--reporter-html-export $(RESULTS_DIR)/report_$(TIMESTAMP).html

newman-with-monitor:
	@echo "🧪 Running Newman with monitoring..."
	@$(MAKE) monitor-start
	@newman run postman/collection.json \
		-e postman/environment.json \
		-r cli,html \
		--reporter-html-export $(RESULTS_DIR)/report_basic_$(TIMESTAMP).html || true
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
		--delay-request 200 \
		-r cli,html \
		--reporter-html-export $(RESULTS_DIR)/report_smoke_$(TIMESTAMP).html || true
	@$(MAKE) monitor-stop
	@echo "✅ Smoke test completed! Report: $(RESULTS_DIR)/report_smoke_$(TIMESTAMP).html"

test-capacity:
	@echo "📈 Running CAPACITY TEST (incremental load)..."
	@echo "Testing with different user loads: 50, 100, 150, 200, 250, 300"
	@mkdir -p $(RESULTS_DIR)
	@for users in 50 100 150 200 250 300; do \
		echo ""; \
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
		echo "🔄 Testing with $$users concurrent users..."; \
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
		$(MAKE) monitor-start; \
		newman run postman/collection.json \
			-e postman/environment.json \
			-n $$users \
			--delay-request 100 \
			-r cli,html \
			--reporter-html-export $(RESULTS_DIR)/report_capacity_$${users}users_$(TIMESTAMP).html || true; \
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
			--delay-request 50 \
			-r cli,html \
			--reporter-html-export $(RESULTS_DIR)/report_ramp_$${users}users_$(TIMESTAMP).html || true; \
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
		--delay-request 150 \
		-r cli,html \
		--reporter-html-export $(RESULTS_DIR)/report_sustained_$(TIMESTAMP).html || true
	@$(MAKE) monitor-stop
	@echo "✅ Sustained test completed!"

test-stress:
	@echo "💥 Running STRESS TEST (400 users, pushing limits)..."
	@$(MAKE) monitor-start
	@newman run postman/collection.json \
		-e postman/environment.json \
		-n 400 \
		--delay-request 50 \
		-r cli,html \
		--reporter-html-export $(RESULTS_DIR)/report_stress_$(TIMESTAMP).html || true
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
		--delay-request 200 \
		-r cli,html \
		--reporter-html-export $(RESULTS_DIR)/report_spike_baseline_$(TIMESTAMP).html || true
	@$(MAKE) monitor-stop
	@echo "Phase 2: SPIKE (400 users)"
	@$(MAKE) monitor-start
	@newman run postman/collection.json \
		-e postman/environment.json \
		-n 400 \
		--delay-request 25 \
		-r cli,html \
		--reporter-html-export $(RESULTS_DIR)/report_spike_burst_$(TIMESTAMP).html || true
	@$(MAKE) monitor-stop
	@echo "Phase 3: Recovery (20 users)"
	@$(MAKE) monitor-start
	@newman run postman/collection.json \
		-e postman/environment.json \
		-n 20 \
		--delay-request 200 \
		-r cli,html \
		--reporter-html-export $(RESULTS_DIR)/report_spike_recovery_$(TIMESTAMP).html || true
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
		echo "📋 Log Files:"; \
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
	@echo "🔧 Infrastructure:"
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
	@echo ""
	@echo "💡 Quick Start:"
	@echo "  1. make up              - Start infrastructure"
	@echo "  2. make test-smoke      - Run quick validation"
	@echo "  3. make test-capacity   - Run capacity analysis"
	@echo "  4. make down            - Stop everything"
	@echo ""
	@echo "📖 All results saved to: $(RESULTS_DIR)/"
	@echo ""


