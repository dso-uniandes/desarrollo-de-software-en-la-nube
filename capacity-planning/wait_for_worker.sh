#!/bin/bash

# wait_for_worker.sh - Wait for worker to finish processing all tasks
# Usage: ./wait_for_worker.sh [timeout_seconds]

WORKER_CONTAINER="worker"
TIMEOUT=${1:-300}  # Default 5 minutes timeout
CHECK_INTERVAL=5   # Check every 5 seconds
IDLE_THRESHOLD=10  # Consider idle after 10 seconds without new tasks

echo "⏳ Waiting for worker to finish processing tasks..."
echo "   Timeout: ${TIMEOUT}s | Check interval: ${CHECK_INTERVAL}s"

elapsed=0
last_task_count=0
idle_time=0

while [ $elapsed -lt $TIMEOUT ]; do
    # Count tasks being processed or in queue (look for "Processing video" or "TOTAL TASK TIME" in recent logs)
    recent_activity=$(docker logs --since ${CHECK_INTERVAL}s "$WORKER_CONTAINER" 2>&1 | grep -E "Processing video|TOTAL TASK TIME|Received task" | wc -l | tr -d ' ')
    
    if [ "$recent_activity" -gt 0 ]; then
        # Worker is still active
        idle_time=0
        echo "   [${elapsed}s] Worker active: $recent_activity events in last ${CHECK_INTERVAL}s"
    else
        # No recent activity
        idle_time=$((idle_time + CHECK_INTERVAL))
        echo "   [${elapsed}s] Worker idle for ${idle_time}s..."
        
        # If idle for more than threshold, consider done
        if [ $idle_time -ge $IDLE_THRESHOLD ]; then
            echo "✅ Worker has been idle for ${idle_time}s - all tasks completed!"
            exit 0
        fi
    fi
    
    sleep $CHECK_INTERVAL
    elapsed=$((elapsed + CHECK_INTERVAL))
done

echo "⚠️  Timeout reached after ${TIMEOUT}s - proceeding anyway"
exit 0
