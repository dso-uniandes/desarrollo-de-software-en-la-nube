#!/bin/bash

# Enhanced Container Resource Monitor with CSV Output
# Captures CPU, Memory, Network, and Disk I/O metrics

RESULTS_DIR=${1:-"postman/results"}
TIMESTAMP=${2:-$(date +%Y%m%d_%H%M%S)}
OUTPUT_FILE="${RESULTS_DIR}/container_stats_${TIMESTAMP}.csv"

# Create results directory if it doesn't exist
mkdir -p "$RESULTS_DIR"

# Write CSV header
echo "timestamp,container_name,cpu_percent,memory_usage_mb,memory_percent,network_rx_mb,network_tx_mb,block_read_mb,block_write_mb" > "$OUTPUT_FILE"

echo "📊 Starting container resource monitoring..."
echo "📁 Output: $OUTPUT_FILE"

# Trap SIGTERM and SIGINT to exit gracefully
trap 'echo "📊 Container monitoring stopped"; exit 0' SIGTERM SIGINT

# Monitoring loop
while true; do
    CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
    
    # Get docker stats in parseable format
    docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}}" | while IFS=',' read -r name cpu mem mempct netio blockio; do
        # Clean CPU percentage (remove %)
        cpu_clean=$(echo "$cpu" | sed 's/%//')
        
        # Parse memory (e.g., "123.4MiB / 1.5GiB" -> extract MB)
        mem_mb=$(echo "$mem" | awk '{
            val=$1; unit=$2;
            if (unit ~ /GiB/) { val = val * 1024 }
            else if (unit ~ /KiB/) { val = val / 1024 }
            printf "%.2f", val
        }')
        
        # Clean memory percentage
        mempct_clean=$(echo "$mempct" | sed 's/%//')
        
        # Parse network IO (e.g., "1.23MB / 456kB" -> extract MB for RX and TX)
        net_rx=$(echo "$netio" | awk -F' / ' '{
            val=$1; 
            gsub(/[^0-9.]/, "", val);
            print val
        }')
        net_tx=$(echo "$netio" | awk -F' / ' '{
            val=$2; 
            gsub(/[^0-9.]/, "", val);
            print val
        }')
        
        # Convert network to MB if needed
        if echo "$netio" | grep -q "kB"; then
            net_rx=$(echo "$net_rx" | awk '{printf "%.4f", $1/1024}')
        fi
        if echo "$netio" | grep -q "GB"; then
            net_rx=$(echo "$net_rx" | awk '{printf "%.2f", $1*1024}')
        fi
        
        # Parse block IO (e.g., "1.23MB / 456kB" -> extract MB for Read and Write)
        block_read=$(echo "$blockio" | awk -F' / ' '{
            val=$1; 
            gsub(/[^0-9.]/, "", val);
            print val
        }')
        block_write=$(echo "$blockio" | awk -F' / ' '{
            val=$2; 
            gsub(/[^0-9.]/, "", val);
            print val
        }')
        
        # Convert block IO to MB if needed
        if echo "$blockio" | grep -q "kB"; then
            block_read=$(echo "$block_read" | awk '{printf "%.4f", $1/1024}')
            block_write=$(echo "$block_write" | awk '{printf "%.4f", $1/1024}')
        fi
        if echo "$blockio" | grep -q "GB"; then
            block_read=$(echo "$block_read" | awk '{printf "%.2f", $1*1024}')
            block_write=$(echo "$block_write" | awk '{printf "%.2f", $1*1024}')
        fi
        
        # Write to CSV
        echo "$CURRENT_TIME,$name,$cpu_clean,$mem_mb,$mempct_clean,$net_rx,$net_tx,$block_read,$block_write" >> "$OUTPUT_FILE"
    done
    
    sleep 1
done
