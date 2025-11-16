#!/bin/bash

# wait_for_worker.sh - Wait for all worker containers to finish processing tasks
# Usage: ./wait_for_worker.sh [timeout_seconds] [worker_pattern]

WORKER_PATTERN=${2:-"worker"}
TIMEOUT=${1:-3600}  # Default 1 hour timeout
CHECK_INTERVAL=5   # Check every 5 seconds
IDLE_THRESHOLD=30  # Consider idle after 30 seconds without new tasks (increased for large batches)

# Find all worker containers
WORKER_CONTAINERS=$(docker ps --format "{{.Names}}" | grep -E "${WORKER_PATTERN}" | tr '\n' ' ')

if [ -z "$WORKER_CONTAINERS" ]; then
    echo "❌ No worker containers found matching pattern: $WORKER_PATTERN"
    exit 1
fi

echo "⏳ Waiting for worker containers to finish processing tasks..."
echo "   Worker containers: $WORKER_CONTAINERS"
echo "   Timeout: ${TIMEOUT}s | Check interval: ${CHECK_INTERVAL}s"

elapsed=0
last_task_count=0
idle_time=0

while [ $elapsed -lt $TIMEOUT ]; do
    # Count tasks being processed or in queue across ALL worker containers
    total_activity=0
    
    for container in $WORKER_CONTAINERS; do
        # Count recent activity in this container
        container_activity=$(docker logs --since ${CHECK_INTERVAL}s "$container" 2>&1 | grep -E "Processing video|TOTAL TASK TIME|Received task" | wc -l | tr -d ' ')
        total_activity=$((total_activity + container_activity))
    done
    
    if [ "$total_activity" -gt 0 ]; then
        # At least one worker is still active
        idle_time=0
        echo "   [${elapsed}s] Workers active: $total_activity events across all workers in last ${CHECK_INTERVAL}s"
    else
        # No recent activity across any worker
        idle_time=$((idle_time + CHECK_INTERVAL))
        echo "   [${elapsed}s] All workers idle for ${idle_time}s..."
        
        # If idle for more than threshold, consider done
        if [ $idle_time -ge $IDLE_THRESHOLD ]; then
            echo "✅ All workers have been idle for ${idle_time}s - all tasks completed!"
            exit 0
        fi
    fi
    
    sleep $CHECK_INTERVAL
    elapsed=$((elapsed + CHECK_INTERVAL))
done

echo "⚠️  Timeout reached after ${TIMEOUT}s - proceeding anyway"
exit 0
