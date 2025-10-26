#!/bin/bash

# check_kafka_lag.sh - Sample Kafka consumer group lag over time and save to CSV
# Usage: ./check_kafka_lag.sh [results_dir] [timestamp] [group_id] [duration_seconds] [interval_seconds]
# Defaults: results_dir=postman/results, timestamp=now, group_id=video_tasks_group, duration=60, interval=5

RESULTS_DIR=${1:-"postman/results"}
TIMESTAMP=${2:-$(date +%Y%m%d_%H%M%S)}
GROUP_ID=${3:-"video_tasks_group"}
DURATION=${4:-60}
INTERVAL=${5:-5}

OUTPUT_FILE="${RESULTS_DIR}/consumer_lag_${TIMESTAMP}.csv"

mkdir -p "$RESULTS_DIR"
echo "timestamp,topic,partition,current_offset,log_end_offset,lag" > "$OUTPUT_FILE"

echo "🔎 Sampling Kafka lag for group='${GROUP_ID}' for ${DURATION}s (every ${INTERVAL}s)"

elapsed=0
while [ $elapsed -lt $DURATION ]; do
  now=$(date "+%Y-%m-%d %H:%M:%S")
  # Describe group from inside the kafka container for consistent tooling availability
  desc=$(docker exec kafka bash -lc "kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group ${GROUP_ID}" 2>/dev/null)

  # Parse lines that look like: TOPIC PARTITION CURRENT-OFFSET LOG-END-OFFSET LAG ...
  # We skip headers and empty lines.
  echo "$desc" | awk -v ts="$now" '(
      $1 != "TOPIC" && NF >= 6 && $1 ~ /.+/ && $2 ~ /[0-9]+/ && $3 ~ /[0-9-]+/ && $4 ~ /[0-9-]+/ && $5 ~ /[0-9-]+/
    ) { printf("%s,%s,%s,%s,%s,%s\n", ts, $1, $2, $3, $4, $5) }' >> "$OUTPUT_FILE"

  sleep $INTERVAL
  elapsed=$((elapsed + INTERVAL))
done

echo "✅ Lag sampling complete: $OUTPUT_FILE"


