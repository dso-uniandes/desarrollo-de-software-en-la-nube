#!/bin/bash

# Container Monitoring Script
# This script shows CPU and memory usage for all containers

echo "======================================"
echo "  Container Resource Monitor"
echo "======================================"
echo ""

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    exit 1
fi

# Function to show stats
show_stats() {
    echo "📊 Real-time Container Stats (Press Ctrl+C to stop)"
    echo ""
    docker stats --format "table {{.Name}}\t{{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Function to show one-time snapshot
show_snapshot() {
    echo "📸 Current Container Stats Snapshot"
    echo ""
    docker stats --no-stream --format "table {{.Name}}\t{{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"
    echo ""
    echo "✅ Done!"
}

# Function to show worker logs with timing
show_worker_logs() {
    echo "⏱️  Worker Processing Times (last 50 lines)"
    echo ""
    docker logs worker --tail 50 2>&1 | grep -E "(TOTAL TASK TIME|video_id|Processing video|task_id)" || echo "No worker logs found"
    echo ""
}

# Function to show menu
show_menu() {
    echo ""
    echo "Options:"
    echo "  1) Show real-time stats (streaming)"
    echo "  2) Show snapshot (one-time)"
    echo "  3) Show worker processing times"
    echo "  4) Show all (snapshot + worker times)"
    echo "  5) Exit"
    echo ""
    read -p "Choose an option [1-5]: " option
    
    case $option in
        1)
            show_stats
            ;;
        2)
            show_snapshot
            show_menu
            ;;
        3)
            show_worker_logs
            show_menu
            ;;
        4)
            show_snapshot
            echo ""
            show_worker_logs
            show_menu
            ;;
        5)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option"
            show_menu
            ;;
    esac
}

# Parse command line arguments
if [ "$1" == "--stream" ] || [ "$1" == "-s" ]; then
    show_stats
elif [ "$1" == "--worker" ] || [ "$1" == "-w" ]; then
    show_worker_logs
elif [ "$1" == "--snapshot" ] || [ "$1" == "-n" ]; then
    show_snapshot
elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  -s, --stream      Show real-time streaming stats"
    echo "  -n, --snapshot    Show one-time snapshot"
    echo "  -w, --worker      Show worker processing times"
    echo "  -h, --help        Show this help message"
    echo ""
    echo "Without options, shows interactive menu"
else
    show_menu
fi
