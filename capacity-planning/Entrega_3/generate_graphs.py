#!/usr/bin/env python3

"""
Generate graphs from monitoring CSV files and test results
"""

import sys
import csv
import json
import statistics
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from collections import defaultdict

def plot_container_resources(csv_file, output_dir):
    """Plot container resource usage over time"""
    
    # Read CSV data
    containers = defaultdict(lambda: {
        'timestamps': [],
        'cpu': [],
        'memory_mb': [],
        'memory_pct': []
    })
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            container = row['container_name']
            try:
                timestamp = datetime.fromisoformat(row['timestamp'])
                containers[container]['timestamps'].append(timestamp)
                containers[container]['cpu'].append(float(row['cpu_percent']))
                containers[container]['memory_mb'].append(float(row['memory_usage_mb']))
                containers[container]['memory_pct'].append(float(row['memory_percent']))
            except (ValueError, KeyError):
                pass
    
    if not containers:
        print("⚠️  No container data to plot")
        return []
    
    output_files = []
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle('Container Resource Usage Over Time', fontsize=16, fontweight='bold')
    
    # Plot CPU usage
    for container, data in containers.items():
        if data['cpu']:
            ax1.plot(data['timestamps'], data['cpu'], label=container, marker='o', markersize=2, linewidth=1.5)
    
    ax1.set_xlabel('Time')
    ax1.set_ylabel('CPU Usage (%)')
    ax1.set_title('CPU Usage by Container')
    ax1.legend(loc='best', fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Plot Memory usage
    for container, data in containers.items():
        if data['memory_mb']:
            ax2.plot(data['timestamps'], data['memory_mb'], label=container, marker='o', markersize=2, linewidth=1.5)
    
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Memory Usage (MB)')
    ax2.set_title('Memory Usage by Container')
    ax2.legend(loc='best', fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    output_file = output_dir / 'container_resources.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  📈 Generated: {output_file}")
    output_files.append(output_file)
    
    return output_files

def plot_worker_timing_breakdown(csv_file, output_dir):
    """Plot worker timing breakdown"""
    
    # Read worker timing data
    timing_data = {
        'db_fetch': [],
        's3_download': [],
        'ffmpeg': [],
        'db_update': []
    }
    
    total_times = []
    task_numbers = []
    task_num = 0
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('status') == 'success':
                task_num += 1
                task_numbers.append(task_num)
                
                try:
                    total_times.append(float(row['total_time_s']))
                    timing_data['db_fetch'].append(float(row.get('db_fetch_s', 0)))
                    timing_data['s3_download'].append(float(row.get('s3_download_s', 0)))
                    timing_data['ffmpeg'].append(float(row.get('ffmpeg_s', 0)))
                    timing_data['db_update'].append(float(row.get('db_update_s', 0)))
                except (ValueError, KeyError):
                    pass
    
    if not task_numbers:
        print("⚠️  No worker timing data to plot")
        return []
    
    output_files = []
    
    # Create stacked area chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle('Worker Task Processing Breakdown', fontsize=16, fontweight='bold')
    
    # Stacked area chart
    ax1.fill_between(task_numbers, 0, timing_data['db_fetch'], label='DB Fetch', alpha=0.7)
    ax1.fill_between(task_numbers, timing_data['db_fetch'], 
                     [a+b for a,b in zip(timing_data['db_fetch'], timing_data['s3_download'])],
                     label='S3 Download', alpha=0.7)
    ax1.fill_between(task_numbers, 
                     [a+b for a,b in zip(timing_data['db_fetch'], timing_data['s3_download'])],
                     [a+b+c for a,b,c in zip(timing_data['db_fetch'], timing_data['s3_download'], timing_data['ffmpeg'])],
                     label='FFmpeg Processing', alpha=0.7)
    ax1.fill_between(task_numbers, 
                     [a+b+c for a,b,c in zip(timing_data['db_fetch'], timing_data['s3_download'], timing_data['ffmpeg'])],
                     total_times,
                     label='DB Update', alpha=0.7)
    
    ax1.set_xlabel('Task Number')
    ax1.set_ylabel('Time (seconds)')
    ax1.set_title('Stacked Task Processing Time')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Total time line chart
    ax2.plot(task_numbers, total_times, label='Total Time', marker='o', markersize=3, linewidth=1.5, color='darkblue')
    ax2.set_xlabel('Task Number')
    ax2.set_ylabel('Time (seconds)')
    ax2.set_title('Total Task Processing Time')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # Add average line
    if total_times:
        avg_time = sum(total_times) / len(total_times)
        ax2.axhline(y=avg_time, color='r', linestyle='--', label=f'Average: {avg_time:.2f}s')
        ax2.legend(loc='best')
    
    plt.tight_layout()
    
    output_file = output_dir / 'worker_timing.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  📈 Generated: {output_file}")
    output_files.append(output_file)
    
    # Create enhanced breakdown chart with bar graph
    if timing_data['db_fetch']:
        # Create figure with two subplots side by side
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        fig.suptitle('Worker Task Processing Time Breakdown', fontsize=16, fontweight='bold')
        
        # Calculate average breakdown
        avg_breakdown = {
            'DB Fetch': sum(timing_data['db_fetch']) / len(timing_data['db_fetch']),
            'S3 Download': sum(timing_data['s3_download']) / len(timing_data['s3_download']),
            'FFmpeg Processing': sum(timing_data['ffmpeg']) / len(timing_data['ffmpeg']),
            'DB Update': sum(timing_data['db_update']) / len(timing_data['db_update'])
        }
        
        # Calculate total and percentages
        total_avg_time = sum(avg_breakdown.values())
        percentages = {k: (v / total_avg_time * 100) for k, v in avg_breakdown.items()}
        
        # Left subplot: Horizontal Bar Chart
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
        bars = ax1.barh(list(avg_breakdown.keys()), list(avg_breakdown.values()), color=colors, alpha=0.8)
        
        ax1.set_xlabel('Time (seconds)', fontsize=11, fontweight='bold')
        ax1.set_title('Average Time per Stage', fontsize=12, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for i, (bar, (k, v)) in enumerate(zip(bars, avg_breakdown.items())):
            width = bar.get_width()
            ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{v:.2f}s ({percentages[k]:.1f}%)',
                    ha='left', va='center', fontweight='bold', fontsize=10)
        
        # Right subplot: Pie Chart
        explode = (0.05, 0.05, 0.15, 0.05)  # Explode FFmpeg slice more
        
        wedges, texts, autotexts = ax2.pie(avg_breakdown.values(), 
                                           labels=avg_breakdown.keys(),
                                           autopct='%1.1f%%',
                                           startangle=45,
                                           colors=colors,
                                           explode=explode,
                                           shadow=True)
        
        # Enhance text
        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        ax2.set_title('Percentage Distribution', fontsize=12, fontweight='bold')
        
        # Add summary text below
        summary_text = f'Total Average Time: {total_avg_time:.2f}s | Tasks: {len(task_numbers)}'
        fig.text(0.5, 0.02, summary_text, ha='center', fontsize=11, 
                fontweight='bold', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout(rect=[0, 0.05, 1, 0.96])
        
        output_file = output_dir / 'worker_breakdown_pie.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  📈 Generated: {output_file}")
        output_files.append(output_file)
    
    return output_files

def plot_newman_metrics(json_file, output_dir):
    """Plot Newman API metrics from JSON report"""
    
    if not json_file.exists():
        print("⚠️  Newman JSON report not found")
        return []
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract metrics
        run = data.get('run', {})
        stats = run.get('stats', {})
        timings = run.get('timings', {})
        executions = run.get('executions', [])
        
        # Get response times
        response_times = []
        failed_requests = 0
        successful_requests = 0
        
        for execution in executions:
            response = execution.get('response', {})
            response_time = response.get('responseTime')
            
            # Check if request failed
            assertions = execution.get('assertions', [])
            has_failure = any(a.get('error') for a in assertions)
            
            if response_time is not None:
                response_times.append(response_time)
                if has_failure:
                    failed_requests += 1
                else:
                    successful_requests += 1
        
        if not response_times:
            print("⚠️  No response time data found in Newman report")
            return []
        
        output_files = []
        
        # Create comprehensive dashboard with 4 subplots
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle(f'Newman API Test Results - {json_file.stem}', fontsize=16, fontweight='bold')
        
        # 1. Response Time Distribution (histogram)
        ax1 = plt.subplot(2, 2, 1)
        ax1.hist(response_times, bins=30, color='#3498db', alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Response Time (ms)', fontweight='bold')
        ax1.set_ylabel('Frequency', fontweight='bold')
        ax1.set_title('Response Time Distribution', fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Add statistics lines
        avg_time = statistics.mean(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        ax1.axvline(avg_time, color='red', linestyle='--', linewidth=2, label=f'Avg: {avg_time:.1f}ms')
        ax1.axvline(p95_time, color='orange', linestyle='--', linewidth=2, label=f'P95: {p95_time:.1f}ms')
        ax1.legend()
        
        # 2. Response Time Over Requests (line chart)
        ax2 = plt.subplot(2, 2, 2)
        request_numbers = list(range(1, len(response_times) + 1))
        ax2.plot(request_numbers, response_times, color='#2ecc71', linewidth=1.5, alpha=0.7)
        ax2.scatter(request_numbers, response_times, color='#27ae60', s=20, alpha=0.6)
        ax2.set_xlabel('Request Number', fontweight='bold')
        ax2.set_ylabel('Response Time (ms)', fontweight='bold')
        ax2.set_title('Response Time Trend', fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        # Add average line
        ax2.axhline(avg_time, color='red', linestyle='--', linewidth=2, alpha=0.7, label=f'Average: {avg_time:.1f}ms')
        ax2.legend()
        
        # 3. Success vs Failed Requests (pie chart)
        ax3 = plt.subplot(2, 2, 3)
        total_requests = successful_requests + failed_requests
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        sizes = [successful_requests, failed_requests]
        colors = ['#2ecc71', '#e74c3c']
        labels = [f'Successful\n{successful_requests}', f'Failed\n{failed_requests}']
        explode = (0.05, 0.05)
        
        wedges, texts, autotexts = ax3.pie(sizes, explode=explode, labels=labels, colors=colors,
                                           autopct='%1.1f%%', startangle=90, shadow=True)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)
        
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        
        ax3.set_title(f'Request Success Rate: {success_rate:.1f}%', fontweight='bold')
        
        # 4. Response Time Statistics (bar chart)
        ax4 = plt.subplot(2, 2, 4)
        
        stats_data = {
            'Min': min(response_times),
            'Avg': avg_time,
            'Median': statistics.median(response_times),
            'P95': p95_time,
            'Max': max(response_times)
        }
        
        bars = ax4.bar(stats_data.keys(), stats_data.values(), 
                       color=['#3498db', '#2ecc71', '#f39c12', '#e67e22', '#e74c3c'],
                       alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax4.set_ylabel('Response Time (ms)', fontweight='bold')
        ax4.set_title('Response Time Statistics', fontweight='bold')
        ax4.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bar, (k, v) in zip(bars, stats_data.items()):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{v:.1f}ms',
                    ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # Add summary info at bottom
        started = timings.get('started', 0)
        completed = timings.get('completed', 0)
        duration_ms = completed - started
        duration_s = duration_ms / 1000.0
        throughput = len(response_times) / duration_s if duration_s > 0 else 0
        
        summary_text = (f'Total Requests: {len(response_times)} | '
                       f'Duration: {duration_s:.1f}s | '
                       f'Throughput: {throughput:.2f} req/s | '
                       f'Success Rate: {success_rate:.1f}%')
        
        fig.text(0.5, 0.02, summary_text, ha='center', fontsize=11, 
                fontweight='bold', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout(rect=(0, 0.05, 1, 0.96))
        
        output_file = output_dir / 'newman_api_metrics.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  📈 Generated: {output_file}")
        output_files.append(output_file)
        
        return output_files
        
    except Exception as e:
        print(f"⚠️  Error generating Newman graphs: {e}")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_graphs.py <test_name>")
        print("Example: python generate_graphs.py 20251019_143025")
        sys.exit(1)
    
    test_name = sys.argv[1]
    results_dir = Path("postman/results")
    
    container_csv = results_dir / f"container_stats_{test_name}.csv"
    worker_csv = results_dir / f"worker_timing_{test_name}.csv"
    
    print(f"\n📊 Generating graphs for test: {test_name}")
    print("=" * 60)
    
    all_output_files = []
    
    # Generate container resource graphs
    if container_csv.exists():
        print(f"\n📈 Generating container resource graphs...")
        files = plot_container_resources(container_csv, results_dir)
        all_output_files.extend(files)
    else:
        print(f"⚠️  Container stats file not found: {container_csv}")
    
    # Generate worker timing graphs
    if worker_csv.exists():
        print(f"\n📈 Generating worker timing graphs...")
        files = plot_worker_timing_breakdown(worker_csv, results_dir)
        all_output_files.extend(files)
    else:
        print(f"⚠️  Worker timing file not found: {worker_csv}")
    
    # Generate Newman API metrics graphs
    # Look for any Newman JSON report with this timestamp
    newman_json_files = list(results_dir.glob(f"report_*{test_name}.json"))
    if newman_json_files:
        print(f"\n📈 Generating Newman API metrics graphs...")
        files = plot_newman_metrics(newman_json_files[0], results_dir)
        all_output_files.extend(files)
    else:
        print(f"⚠️  No Newman JSON report found for timestamp: {test_name}")
    
    if all_output_files:
        print("\n" + "=" * 60)
        print(f"✅ Generated {len(all_output_files)} graph(s)")
        print("=" * 60 + "\n")
    else:
        print("\n❌ No graphs generated")
        sys.exit(1)

if __name__ == "__main__":
    main()
