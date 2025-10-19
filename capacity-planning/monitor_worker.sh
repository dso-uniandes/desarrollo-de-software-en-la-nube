#!/bin/bash

# Worker Logs Monitor - Extracts timing information and errors to CSV
# Captures: task_id, video_id, total_time, db_fetch_time, s3_download_time, ffmpeg_time, db_update_time, status, error_msg

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

# Variable to store the last video_id seen
last_video_id="N/A"

# Follow worker logs and extract timing information and errors
docker logs -f "$WORKER_CONTAINER" 2>&1 | while read -r line; do
    # Check for video_id in processing complete messages
    if echo "$line" | grep -q "video_id="; then
        vid=$(echo "$line" | sed -n 's/.*\[video_id=\([0-9]*\)\].*/\1/p')
        if [ -n "$vid" ]; then
            last_video_id="$vid"
        fi
    fi
    
    # Look for lines with "TOTAL TASK TIME" (successful completion)
    if echo "$line" | grep -q "TOTAL TASK TIME"; then
        CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
        
        # Extract task_id using sed (more portable than grep -P)
        task_id=$(echo "$line" | sed -n 's/.*\[task_id=\([a-f0-9-]*\)\].*/\1/p')
        [ -z "$task_id" ] && task_id="unknown"
        
        # Use the last video_id we saw
        video_id="$last_video_id"
        
        # Extract timing values using sed
        # Format: TOTAL TASK TIME: 10.03s (DB Fetch: 0.00s, S3 Download: 0.00s, FFmpeg: 10.03s, DB Update: 0.00s)
        total_time=$(echo "$line" | sed -n 's/.*TOTAL TASK TIME: \([0-9.]*\)s.*/\1/p')
        db_fetch=$(echo "$line" | sed -n 's/.*DB Fetch: \([0-9.]*\)s.*/\1/p')
        s3_download=$(echo "$line" | sed -n 's/.*S3 Download: \([0-9.]*\)s.*/\1/p')
        ffmpeg=$(echo "$line" | sed -n 's/.*FFmpeg: \([0-9.]*\)s.*/\1/p')
        db_update=$(echo "$line" | sed -n 's/.*DB Update: \([0-9.]*\)s.*/\1/p')
        
        # Only write if we have valid data
        if [ -n "$total_time" ]; then
            # Write to CSV with success status
            echo "$CURRENT_TIME,$task_id,$video_id,$total_time,$db_fetch,$s3_download,$ffmpeg,$db_update,success," >> "$OUTPUT_FILE"
            
            # Also print to console
            echo "✅ [$(date +%H:%M:%S)] Task $task_id (video $video_id) completed in ${total_time}s"
        fi
    fi
    
    # Look for error lines: [task_id=XXX] Error processing video after X.XXs: error message
    if echo "$line" | grep -q "Error processing video after"; then
        CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
        
        # Extract task_id
        task_id=$(echo "$line" | sed -n 's/.*\[task_id=\([a-f0-9-]*\)\].*/\1/p')
        [ -z "$task_id" ] && task_id="unknown"
        
        # Use the last video_id we saw
        video_id="$last_video_id"
        
        # Extract error time: "Error processing video after 12.34s:"
        error_time=$(echo "$line" | sed -n 's/.*Error processing video after \([0-9.]*\)s:.*/\1/p')
        [ -z "$error_time" ] && error_time="0"
        
        # Extract error message (everything after the colon)
        error_msg=$(echo "$line" | sed -n 's/.*Error processing video after [0-9.]*s: \(.*\)/\1/p')
        # Escape commas and quotes in error message
        error_msg=$(echo "$error_msg" | sed 's/,/;/g' | sed 's/"/'\''/g')
        [ -z "$error_msg" ] && error_msg="Unknown error"
        
        # Write to CSV with error status (no breakdown, just total time)
        echo "$CURRENT_TIME,$task_id,$video_id,$error_time,,,,error,\"$error_msg\"" >> "$OUTPUT_FILE"
        
        # Also print to console
        echo "❌ [$(date +%H:%M:%S)] Task $task_id (video $video_id) FAILED after ${error_time}s: $error_msg"
    fi
done
