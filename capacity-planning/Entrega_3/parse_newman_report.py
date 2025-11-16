#!/usr/bin/env python3

"""
Parse Newman JSON reports and extract API metrics
"""

import sys
import json
import csv
import statistics
from pathlib import Path

def parse_newman_json(json_file):
    """Parse Newman JSON report and extract metrics"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metrics = {
        'test_name': Path(json_file).stem,
        'total_requests': 0,
        'failed_requests': 0,
        'success_rate': 0.0,
        'avg_response_time': 0.0,
        'min_response_time': 0.0,
        'max_response_time': 0.0,
        'p95_response_time': 0.0,
        'total_test_duration': 0.0
    }
    
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
    
    # Extract total duration (in milliseconds, convert to seconds)
    metrics['total_test_duration'] = timings.get('completed', 0) / 1000.0
    
    return metrics

def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_newman_report.py <report.json> [output.csv]")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(json_file).exists():
        print(f"Error: File not found: {json_file}")
        sys.exit(1)
    
    metrics = parse_newman_json(json_file)
    
    # Print to console
    print(f"\n📊 Newman Report Metrics: {metrics['test_name']}")
    print("=" * 60)
    print(f"Total Requests:     {metrics['total_requests']}")
    print(f"Failed Requests:    {metrics['failed_requests']}")
    print(f"Success Rate:       {metrics['success_rate']:.2f}%")
    print(f"  Avg Response Time:  {metrics['avg_response_time']:.2f} ms")
    print(f"  Min Response Time:  {metrics['min_response_time']:.2f} ms")
    print(f"  Max Response Time:  {metrics['max_response_time']:.2f} ms")
    print(f"  P95 Response Time:  {metrics['p95_response_time']:.2f} ms")
    print(f"  Test Duration:      {metrics['total_test_duration']:.2f} s")
    print("=" * 60)
    
    # Write to CSV if specified
    if output_csv:
        with open(output_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=metrics.keys())
            writer.writeheader()
            writer.writerow(metrics)
        print(f"\n✅ Metrics saved to: {output_csv}")
    
    return metrics

if __name__ == "__main__":
    main()
