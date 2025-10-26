#!/bin/bash

# Worker Logs Monitor - Extracts timing information and errors to CSV
# Captures: task_id, video_id, total_time, db_fetch_time, s3_download_time, ffmpeg_time, db_update_time, status, error_msg
# Features:
# - Tracks task_id to video_id mapping to ensure correct association
# - Prevents duplicate task entries in analysis
# - Uses temporary file for persistent task tracking across pipeline
# - Only processes NEW logs from monitoring start time (avoids old tasks from previous runs)

RESULTS_DIR=${1:-"postman/results"}
TIMESTAMP=${2:-$(date +%Y%m%d_%H%M%S)}
OUTPUT_FILE="${RESULTS_DIR}/worker_timing_${TIMESTAMP}.csv"
WORKER_CONTAINER=${3:-"worker"}

# Create results directory if it doesn't exist
mkdir -p "$RESULTS_DIR"

# Write CSV header
echo "timestamp,task_id,video_id,total_time_s,db_fetch_s,s3_download_s,ffmpeg_s,db_update_s,status,error_msg" > "$OUTPUT_FILE"

echo "⏱️  Starting worker timing monitor..."
echo "📁 Output: $OUTPUT_FILE"

# Trap SIGTERM and SIGINT to exit gracefully
trap 'echo "⏱️  Worker monitoring stopped"; exit 0' SIGTERM SIGINT

# Associative array to track task information (task_id -> video_id)
# Note: This requires bash 4+, but we'll use a simpler approach for portability
declare -A task_video_map

# Get current timestamp to only process logs from this monitoring session
MONITOR_START_TIME=$(date "+%Y-%m-%d %H:%M:%S")
MONITOR_START_UNIX=$(date +%s)
echo "🕐 Monitor started at: $MONITOR_START_TIME"
echo "📝 Only processing logs from this point forward..."

# Follow NEW logs only (--since unix timestamp) to avoid processing old tasks
docker logs -f --since="$MONITOR_START_UNIX" "$WORKER_CONTAINER" 2>&1 | while read -r line; do
    # Debug: Show all lines being processed (comment out for production)
    # echo "DEBUG: $line"
    
    # Extract task_id and video_id when they appear together in logs
    if echo "$line" | grep -q "task_id=" && echo "$line" | grep -q "video_id="; then
        task_id=$(echo "$line" | sed -n 's/.*\[task_id=\([a-f0-9-]*\)\].*/\1/p')
        video_id=$(echo "$line" | sed -n 's/.*\[video_id=\([0-9]*\)\].*/\1/p')
        
        if [ -n "$task_id" ] && [ -n "$video_id" ]; then
            # Store the mapping in a temporary file for persistence across the pipeline
            echo "$task_id:$video_id" >> "/tmp/task_video_map_$$"
        fi
    fi
    
    # Look for lines with "TOTAL TASK TIME" (successful completion)
    if echo "$line" | grep -q "TOTAL TASK TIME"; then
        CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
        
        # Extract task_id using sed (more portable than grep -P)
        task_id=$(echo "$line" | sed -n 's/.*\[task_id=\([a-f0-9-]*\)\].*/\1/p')
        [ -z "$task_id" ] && task_id="unknown"
        
        # Get video_id for this specific task from our mapping
        video_id="N/A"
        if [ -f "/tmp/task_video_map_$$" ] && [ -n "$task_id" ] && [ "$task_id" != "unknown" ]; then
            video_id=$(grep "^$task_id:" "/tmp/task_video_map_$$" | cut -d':' -f2 | tail -1)
            [ -z "$video_id" ] && video_id="N/A"
        fi
        
        # Extract timing values using sed
        # Format: TOTAL TASK TIME: 10.03s (DB Fetch: 0.00s, S3 Download: 0.00s, FFmpeg: 10.03s, DB Update: 0.00s)
        total_time=$(echo "$line" | sed -n 's/.*TOTAL TASK TIME: \([0-9.]*\)s.*/\1/p')
        db_fetch=$(echo "$line" | sed -n 's/.*DB Fetch: \([0-9.]*\)s.*/\1/p')
        s3_download=$(echo "$line" | sed -n 's/.*S3 Download: \([0-9.]*\)s.*/\1/p')
        ffmpeg=$(echo "$line" | sed -n 's/.*FFmpeg: \([0-9.]*\)s.*/\1/p')
        db_update=$(echo "$line" | sed -n 's/.*DB Update: \([0-9.]*\)s.*/\1/p')
        
        # Only write if we have valid data and this task hasn't been recorded yet
        if [ -n "$total_time" ]; then
            # Check if this task has already been recorded in this monitoring session (prevent duplicates)
            if ! grep -q "^[^,]*,$task_id," "$OUTPUT_FILE" 2>/dev/null; then
                # Write to CSV with success status
                echo "$CURRENT_TIME,$task_id,$video_id,$total_time,$db_fetch,$s3_download,$ffmpeg,$db_update,success," >> "$OUTPUT_FILE"
                
                # Also print to console
                echo "✅ [$(date +%H:%M:%S)] Task $task_id (video $video_id) completed in ${total_time}s"
            else
                echo "⚠️  [$(date +%H:%M:%S)] Duplicate task $task_id ignored (already recorded in this session)"
            fi
        fi
    fi
    
    # Look for error lines: [task_id=XXX] Error processing video after X.XXs: error message
    if echo "$line" | grep -q "Error processing video after"; then
        CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
        
        # Extract task_id
        task_id=$(echo "$line" | sed -n 's/.*\[task_id=\([a-f0-9-]*\)\].*/\1/p')
        [ -z "$task_id" ] && task_id="unknown"
        
        # Get video_id for this specific task from our mapping
        video_id="N/A"
        if [ -f "/tmp/task_video_map_$$" ] && [ -n "$task_id" ] && [ "$task_id" != "unknown" ]; then
            video_id=$(grep "^$task_id:" "/tmp/task_video_map_$$" | cut -d':' -f2 | tail -1)
            [ -z "$video_id" ] && video_id="N/A"
        fi
        
        # Extract error time: "Error processing video after 12.34s:"
        error_time=$(echo "$line" | sed -n 's/.*Error processing video after \([0-9.]*\)s:.*/\1/p')
        [ -z "$error_time" ] && error_time="0"
        
        # Extract error message (everything after the colon)
        error_msg=$(echo "$line" | sed -n 's/.*Error processing video after [0-9.]*s: \(.*\)/\1/p')
        # Escape commas and quotes in error message
        error_msg=$(echo "$error_msg" | sed 's/,/;/g' | sed 's/"/'\''/g')
        [ -z "$error_msg" ] && error_msg="Unknown error"
        
        # Only write if this task hasn't been recorded yet in this monitoring session (prevent duplicates)
        if ! grep -q "^[^,]*,$task_id," "$OUTPUT_FILE" 2>/dev/null; then
            # Write to CSV with error status (no breakdown, just total time)
            echo "$CURRENT_TIME,$task_id,$video_id,$error_time,,,,error,\"$error_msg\"" >> "$OUTPUT_FILE"
            
            # Also print to console
            echo "❌ [$(date +%H:%M:%S)] Task $task_id (video $video_id) FAILED after ${error_time}s: $error_msg"
        else
            echo "⚠️  [$(date +%H:%M:%S)] Duplicate error for task $task_id ignored (already recorded in this session)"
        fi
    fi
done

# Cleanup temporary file when script exits
trap 'rm -f "/tmp/task_video_map_$$"; echo "⏱️  Worker monitoring stopped"; exit 0' SIGTERM SIGINT EXIT
