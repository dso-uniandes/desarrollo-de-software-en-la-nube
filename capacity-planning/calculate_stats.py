#!/usr/bin/env python3

"""
Calculate statistics and averages from monitoring CSV files
Processes both container stats and worker timing data
"""

import sys
import csv
import statistics
import json
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
    """Parse worker timing CSV and calculate averages, including error statistics"""
    
    metrics = {
        'total_time': [],
        'db_fetch': [],
        's3_download': [],
        'ffmpeg': [],
        'db_update': []
    }
    
    task_count = 0
    success_count = 0
    error_count = 0
    error_messages = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            task_count += 1
            
            # Check task status
            status = row.get('status', 'unknown')
            if status == 'success':
                success_count += 1
            elif status == 'error':
                error_count += 1
                error_msg = row.get('error_msg', 'Unknown error')
                error_messages.append({
                    'task_id': row.get('task_id', 'unknown'),
                    'video_id': row.get('video_id', 'N/A'),
                    'time': row.get('total_time_s', '0'),
                    'error': error_msg
                })
            
            try:
                metrics['total_time'].append(float(row['total_time_s']))
            except (ValueError, KeyError):
                pass
            
            try:
                if row['db_fetch_s']:  # Only append if not empty
                    metrics['db_fetch'].append(float(row['db_fetch_s']))
            except (ValueError, KeyError):
                pass
            
            try:
                if row['s3_download_s']:
                    metrics['s3_download'].append(float(row['s3_download_s']))
            except (ValueError, KeyError):
                pass
            
            try:
                if row['ffmpeg_s']:
                    metrics['ffmpeg'].append(float(row['ffmpeg_s']))
            except (ValueError, KeyError):
                pass
            
            try:
                if row['db_update_s']:
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
    results['success_count'] = success_count
    results['error_count'] = error_count
    results['error_rate'] = (error_count / task_count * 100) if task_count > 0 else 0
    results['error_messages'] = error_messages
    
    return results

def parse_newman_json(json_file):
    """Parse Newman JSON report and extract API metrics"""
    
    if not json_file.exists():
        return None
    
    metrics = {
        'test_name': json_file.stem,
        'total_requests': 0,
        'failed_requests': 0,
        'success_rate': 0.0,
        'avg_response_time': 0.0,
        'min_response_time': 0.0,
        'max_response_time': 0.0,
        'p95_response_time': 0.0,
        'total_test_duration': 0.0
    }
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract run statistics
        run = data.get('run', {})
        stats = run.get('stats', {})
        timings = run.get('timings', {})
        
        # Get request counts
        requests_stats = stats.get('requests', {})
        metrics['total_requests'] = requests_stats.get('total', 0)
        metrics['failed_requests'] = requests_stats.get('failed', 0)
        
        # Calculate success rate
        if metrics['total_requests'] > 0:
            metrics['success_rate'] = ((metrics['total_requests'] - metrics['failed_requests']) / 
                                       metrics['total_requests'] * 100)
        
        # Extract response times from executions
        response_times = []
        executions = run.get('executions', [])
        
        for execution in executions:
            response = execution.get('response', {})
            response_time = response.get('responseTime')
            if response_time is not None:
                response_times.append(response_time)
        
        # Calculate response time statistics
        if response_times:
            metrics['avg_response_time'] = statistics.mean(response_times)
            metrics['min_response_time'] = min(response_times)
            metrics['max_response_time'] = max(response_times)
            
            # Calculate P95
            sorted_times = sorted(response_times)
            p95_index = int(len(sorted_times) * 0.95)
            metrics['p95_response_time'] = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
        
        # Extract total duration (difference between completed and started timestamps in milliseconds)
        started = timings.get('started', 0)
        completed = timings.get('completed', 0)
        duration_ms = completed - started
        metrics['total_test_duration'] = duration_ms / 1000.0  # Convert to seconds
        
        return metrics
    except Exception as e:
        print(f"⚠️  Error parsing Newman JSON report: {e}")
        return None

def generate_summary_csv(container_stats, worker_stats, newman_stats, output_file):
    """Generate a summary CSV with all statistics"""
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write Newman API metrics first if available
        if newman_stats:
            writer.writerow(['=== API/NEWMAN METRICS ==='])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Test Name', newman_stats['test_name']])
            writer.writerow(['Total Requests', newman_stats['total_requests']])
            writer.writerow(['Failed Requests', newman_stats['failed_requests']])
            writer.writerow(['Success Rate', f"{newman_stats['success_rate']:.2f}%"])
            writer.writerow(['Avg Response Time (ms)', f"{newman_stats['avg_response_time']:.2f}"])
            writer.writerow(['Min Response Time (ms)', f"{newman_stats['min_response_time']:.2f}"])
            writer.writerow(['Max Response Time (ms)', f"{newman_stats['max_response_time']:.2f}"])
            writer.writerow(['P95 Response Time (ms)', f"{newman_stats['p95_response_time']:.2f}"])
            writer.writerow(['Test Duration (s)', f"{newman_stats['total_test_duration']:.2f}"])
            if newman_stats['total_test_duration'] > 0 and newman_stats['total_requests'] > 0:
                rps = newman_stats['total_requests'] / newman_stats['total_test_duration']
                writer.writerow(['Throughput (req/s)', f"{rps:.2f}"])
            writer.writerow([])
            writer.writerow([])
        
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
        
        # Write summary metrics first
        if 'total_tasks' in worker_stats:
            total_tasks = worker_stats.get('total_tasks', 0)
            success_count = worker_stats.get('success_count', 0)
            error_count = worker_stats.get('error_count', 0)
            error_rate = worker_stats.get('error_rate', 0)
            
            writer.writerow(['Total Tasks', total_tasks])
            writer.writerow(['Successful Tasks', success_count, f'{100 - error_rate:.2f}%'])
            writer.writerow(['Failed Tasks', error_count, f'{error_rate:.2f}%'])
            writer.writerow([])
        
        writer.writerow(['Metric', 'Min (s)', 'Max (s)', 'Avg (s)', 'Median (s)', 'P95 (s)', 'StdDev', 'Samples'])
        
        for metric_name, stats in worker_stats.items():
            # Skip non-timing metrics
            if metric_name in ['total_tasks', 'success_count', 'error_count', 'error_rate', 'error_messages']:
                continue
            
            if isinstance(stats, dict) and 'min' in stats:
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
        
        # Write error details if any
        error_messages = worker_stats.get('error_messages', [])
        if error_messages:
            writer.writerow([])
            writer.writerow(['=== ERROR DETAILS ==='])
            writer.writerow(['Task ID', 'Video ID', 'Time (s)', 'Error Message'])
            for err in error_messages:
                writer.writerow([
                    err['task_id'],
                    err['video_id'],
                    err['time'],
                    err['error']
                ])

def print_summary(container_stats, worker_stats, newman_stats=None):
    """Print summary to console"""
    
    # Print Newman/API metrics first if available
    if newman_stats:
        print("\n" + "="*80)
        print("🌐 API/NEWMAN METRICS")
        print("="*80)
        print(f"\n  Test: {newman_stats['test_name']}")
        print(f"  Total Requests:     {newman_stats['total_requests']}")
        print(f"  Failed Requests:    {newman_stats['failed_requests']}")
        print(f"  Success Rate:       {newman_stats['success_rate']:.2f}%")
        print(f"  Avg Response Time:  {newman_stats['avg_response_time']:.2f} ms")
        print(f"  Min Response Time:  {newman_stats['min_response_time']:.2f} ms")
        print(f"  Max Response Time:  {newman_stats['max_response_time']:.2f} ms")
        print(f"  P95 Response Time:  {newman_stats['p95_response_time']:.2f} ms")
        print(f"  Test Duration:      {newman_stats['total_test_duration']:.2f} s")
        if newman_stats['total_test_duration'] > 0 and newman_stats['total_requests'] > 0:
            rps = newman_stats['total_requests'] / newman_stats['total_test_duration']
            print(f"  Throughput:         {rps:.2f} req/s")
    
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
        success_count = worker_stats.get('success_count', 0)
        error_count = worker_stats.get('error_count', 0)
        error_rate = worker_stats.get('error_rate', 0)
        
        print(f"\n📦 Total Tasks Processed: {total_tasks}")
        print(f"   ✅ Successful: {success_count} ({100 - error_rate:.1f}%)")
        print(f"   ❌ Errors: {error_count} ({error_rate:.1f}%)")
        print("-" * 80)
        
        metrics_order = ['total_time', 'ffmpeg', 's3_download', 'db_fetch', 'db_update']
        
        for metric_name in metrics_order:
            if metric_name in worker_stats and isinstance(worker_stats[metric_name], dict):
                stats = worker_stats[metric_name]
                print(f"\n  {metric_name.replace('_', ' ').title()}:")
                print(f"    Avg:    {stats['avg']:6.2f}s")
                print(f"    Median: {stats['median']:6.2f}s")
                print(f"    Min:    {stats['min']:6.2f}s")
                print(f"    Max:    {stats['max']:6.2f}s")
                print(f"    P95:    {stats['p95']:6.2f}s")
                print(f"    StdDev: {stats['stdev']:6.2f}s")
        
        # Calculate throughput (only for successful tasks)
        if 'total_time' in worker_stats and success_count > 0:
            stats = worker_stats['total_time']
            if isinstance(stats, dict) and 'avg' in stats:
                avg_time = stats['avg']
                throughput = 60 / avg_time if avg_time > 0 else 0
                print(f"\n  📈 Estimated Throughput: {throughput:.2f} videos/minute")
        
        # Display error details if any
        error_messages = worker_stats.get('error_messages', [])
        if error_messages:
            print(f"\n  ⚠️  ERROR DETAILS ({len(error_messages)} errors):")
            print("  " + "-" * 76)
            for i, err in enumerate(error_messages[:10], 1):  # Show max 10 errors
                print(f"    {i}. Task {err['task_id'][:8]}... (video {err['video_id']}) after {err['time']}s")
                print(f"       Error: {err['error'][:70]}...")
            if len(error_messages) > 10:
                print(f"    ... and {len(error_messages) - 10} more errors")
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
    
    # Parse Newman JSON report
    newman_stats = None
    if len(sys.argv) == 2:
        # Look for any Newman JSON report with this timestamp
        newman_json_pattern = results_dir.glob(f"report_*{test_name}.json")
        newman_json_files = list(newman_json_pattern)
        
        if newman_json_files:
            # Use the first matching file
            newman_json = newman_json_files[0]
            print(f"🌐 Processing Newman report: {newman_json}")
            newman_stats = parse_newman_json(newman_json)
        else:
            print(f"⚠️  No Newman JSON report found for timestamp: {test_name}")
    
    # Generate output
    if container_stats or worker_stats or newman_stats:
        # Print to console
        print_summary(container_stats, worker_stats, newman_stats)
        
        # Generate CSV summary
        if len(sys.argv) == 2:
            output_csv = results_dir / f"summary_{test_name}.csv"
        else:
            output_csv = container_csv.parent / f"summary_{container_csv.stem}.csv"
        
        generate_summary_csv(container_stats, worker_stats, newman_stats, output_csv)
        print(f"✅ Summary saved to: {output_csv}")
    else:
        print("❌ No data to process")
        sys.exit(1)

if __name__ == "__main__":
    main()
