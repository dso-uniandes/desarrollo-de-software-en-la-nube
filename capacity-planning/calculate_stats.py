#!/usr/bin/env python3

"""
Calculate statistics and averages from monitoring CSV files
Processes both container stats and worker timing data
"""

import sys
import csv
import statistics
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def parse_container_stats(csv_file):
    """Parse container stats CSV and calculate averages per container"""
    
    container_metrics = defaultdict(lambda: {
        'cpu': [],
        'memory_mb': [],
        'memory_pct': [],
        'net_rx': [],
        'net_tx': [],
        'block_read': [],
        'block_write': []
    })
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            container = row['container_name']
            
            # Collect metrics (handle empty or invalid values)
            try:
                container_metrics[container]['cpu'].append(float(row['cpu_percent']))
            except (ValueError, KeyError):
                pass
            
            try:
                container_metrics[container]['memory_mb'].append(float(row['memory_usage_mb']))
            except (ValueError, KeyError):
                pass
            
            try:
                container_metrics[container]['memory_pct'].append(float(row['memory_percent']))
            except (ValueError, KeyError):
                pass
            
            try:
                container_metrics[container]['net_rx'].append(float(row['network_rx_mb']))
            except (ValueError, KeyError):
                pass
            
            try:
                container_metrics[container]['net_tx'].append(float(row['network_tx_mb']))
            except (ValueError, KeyError):
                pass
            
            try:
                container_metrics[container]['block_read'].append(float(row['block_read_mb']))
            except (ValueError, KeyError):
                pass
            
            try:
                container_metrics[container]['block_write'].append(float(row['block_write_mb']))
            except (ValueError, KeyError):
                pass
    
    # Calculate statistics
    results = {}
    for container, metrics in container_metrics.items():
        results[container] = {}
        
        for metric_name, values in metrics.items():
            if values:
                results[container][metric_name] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': statistics.mean(values),
                    'median': statistics.median(values),
                    'stdev': statistics.stdev(values) if len(values) > 1 else 0,
                    'samples': len(values)
                }
    
    return results

def parse_worker_timing(csv_file):
    """Parse worker timing CSV and calculate averages"""
    
    metrics = {
        'total_time': [],
        'db_fetch': [],
        's3_download': [],
        'ffmpeg': [],
        'db_update': []
    }
    
    task_count = 0
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            task_count += 1
            
            try:
                metrics['total_time'].append(float(row['total_time_s']))
            except (ValueError, KeyError):
                pass
            
            try:
                metrics['db_fetch'].append(float(row['db_fetch_s']))
            except (ValueError, KeyError):
                pass
            
            try:
                metrics['s3_download'].append(float(row['s3_download_s']))
            except (ValueError, KeyError):
                pass
            
            try:
                metrics['ffmpeg'].append(float(row['ffmpeg_s']))
            except (ValueError, KeyError):
                pass
            
            try:
                metrics['db_update'].append(float(row['db_update_s']))
            except (ValueError, KeyError):
                pass
    
    # Calculate statistics
    results = {}
    for metric_name, values in metrics.items():
        if values:
            results[metric_name] = {
                'min': min(values),
                'max': max(values),
                'avg': statistics.mean(values),
                'median': statistics.median(values),
                'stdev': statistics.stdev(values) if len(values) > 1 else 0,
                'p95': sorted(values)[int(len(values) * 0.95)] if len(values) > 20 else max(values),
                'samples': len(values)
            }
    
    results['total_tasks'] = task_count
    
    return results

def generate_summary_csv(container_stats, worker_stats, output_file):
    """Generate a summary CSV with all statistics"""
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write container stats
        writer.writerow(['=== CONTAINER RESOURCE STATISTICS ==='])
        writer.writerow(['Container', 'Metric', 'Min', 'Max', 'Avg', 'Median', 'StdDev', 'Samples'])
        
        for container, metrics in container_stats.items():
            for metric_name, stats in metrics.items():
                writer.writerow([
                    container,
                    metric_name,
                    f"{stats['min']:.2f}",
                    f"{stats['max']:.2f}",
                    f"{stats['avg']:.2f}",
                    f"{stats['median']:.2f}",
                    f"{stats['stdev']:.2f}",
                    stats['samples']
                ])
            writer.writerow([])  # Empty row between containers
        
        writer.writerow([])
        writer.writerow(['=== WORKER TIMING STATISTICS ==='])
        writer.writerow(['Metric', 'Min (s)', 'Max (s)', 'Avg (s)', 'Median (s)', 'P95 (s)', 'StdDev', 'Samples'])
        
        if 'total_tasks' in worker_stats:
            total_tasks = worker_stats.pop('total_tasks')
            
            for metric_name, stats in worker_stats.items():
                writer.writerow([
                    metric_name,
                    f"{stats['min']:.2f}",
                    f"{stats['max']:.2f}",
                    f"{stats['avg']:.2f}",
                    f"{stats['median']:.2f}",
                    f"{stats['p95']:.2f}",
                    f"{stats['stdev']:.2f}",
                    stats['samples']
                ])
            
            writer.writerow([])
            writer.writerow(['Total Tasks Processed', total_tasks])

def print_summary(container_stats, worker_stats):
    """Print summary to console"""
    
    print("\n" + "="*80)
    print("📊 CONTAINER RESOURCE STATISTICS")
    print("="*80)
    
    for container, metrics in container_stats.items():
        print(f"\n🐳 {container}")
        print("-" * 80)
        
        if 'cpu' in metrics:
            cpu = metrics['cpu']
            print(f"  CPU:        {cpu['avg']:6.2f}% avg  [{cpu['min']:6.2f}% - {cpu['max']:6.2f}%]  (σ={cpu['stdev']:.2f})")
        
        if 'memory_mb' in metrics:
            mem = metrics['memory_mb']
            print(f"  Memory:     {mem['avg']:6.2f} MB avg [{mem['min']:6.2f} - {mem['max']:6.2f} MB]  (σ={mem['stdev']:.2f})")
        
        if 'memory_pct' in metrics:
            memp = metrics['memory_pct']
            print(f"  Memory %:   {memp['avg']:6.2f}% avg  [{memp['min']:6.2f}% - {memp['max']:6.2f}%]")
        
        if 'net_rx' in metrics and 'net_tx' in metrics:
            rx = metrics['net_rx']
            tx = metrics['net_tx']
            print(f"  Network RX: {rx['max']:6.2f} MB total")
            print(f"  Network TX: {tx['max']:6.2f} MB total")
        
        if 'block_read' in metrics and 'block_write' in metrics:
            br = metrics['block_read']
            bw = metrics['block_write']
            print(f"  Disk Read:  {br['max']:6.2f} MB total")
            print(f"  Disk Write: {bw['max']:6.2f} MB total")
    
    print("\n" + "="*80)
    print("⏱️  WORKER TIMING STATISTICS")
    print("="*80)
    
    if worker_stats:
        total_tasks = worker_stats.get('total_tasks', 0)
        print(f"\n📦 Total Tasks Processed: {total_tasks}")
        print("-" * 80)
        
        metrics_order = ['total_time', 'ffmpeg', 's3_download', 'db_fetch', 'db_update']
        
        for metric_name in metrics_order:
            if metric_name in worker_stats:
                stats = worker_stats[metric_name]
                print(f"\n  {metric_name.replace('_', ' ').title()}:")
                print(f"    Avg:    {stats['avg']:6.2f}s")
                print(f"    Median: {stats['median']:6.2f}s")
                print(f"    Min:    {stats['min']:6.2f}s")
                print(f"    Max:    {stats['max']:6.2f}s")
                print(f"    P95:    {stats['p95']:6.2f}s")
                print(f"    StdDev: {stats['stdev']:6.2f}s")
        
        # Calculate throughput
        if 'total_time' in worker_stats and total_tasks > 0:
            avg_time = worker_stats['total_time']['avg']
            throughput = 60 / avg_time if avg_time > 0 else 0
            print(f"\n  📈 Estimated Throughput: {throughput:.2f} videos/minute")
    else:
        print("\n  ⚠️  No worker timing data found")
    
    print("\n" + "="*80 + "\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python calculate_stats.py <test_name>")
        print("Example: python calculate_stats.py 20251019_143025")
        print("\nOr provide specific CSV files:")
        print("  python calculate_stats.py <container_stats.csv> <worker_timing.csv>")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        # Assume it's a timestamp/test name
        test_name = sys.argv[1]
        results_dir = Path("postman/results")
        container_csv = results_dir / f"container_stats_{test_name}.csv"
        worker_csv = results_dir / f"worker_timing_{test_name}.csv"
    else:
        # Specific files provided
        container_csv = Path(sys.argv[1])
        worker_csv = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    # Parse container stats
    container_stats = {}
    if container_csv.exists():
        print(f"📊 Processing container stats: {container_csv}")
        container_stats = parse_container_stats(container_csv)
    else:
        print(f"⚠️  Container stats file not found: {container_csv}")
    
    # Parse worker timing
    worker_stats = {}
    if worker_csv and worker_csv.exists():
        print(f"⏱️  Processing worker timing: {worker_csv}")
        worker_stats = parse_worker_timing(worker_csv)
    else:
        if worker_csv:
            print(f"⚠️  Worker timing file not found: {worker_csv}")
    
    # Generate output
    if container_stats or worker_stats:
        # Print to console
        print_summary(container_stats, worker_stats)
        
        # Generate CSV summary
        if len(sys.argv) == 2:
            output_csv = results_dir / f"summary_{test_name}.csv"
        else:
            output_csv = container_csv.parent / f"summary_{container_csv.stem}.csv"
        
        generate_summary_csv(container_stats, worker_stats, output_csv)
        print(f"✅ Summary saved to: {output_csv}")
    else:
        print("❌ No data to process")
        sys.exit(1)

if __name__ == "__main__":
    main()
