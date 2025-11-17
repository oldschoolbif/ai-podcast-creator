#!/usr/bin/env python3
"""Fetch logs from the most recent failed CI run."""
import json
import sys
import urllib.request
import urllib.parse

def main():
    repo = "oldschoolbif/ai-podcast-creator"
    branch = "qa/avatar-generator-tests"
    
    # Get failed runs
    url = f"https://api.github.com/repos/{repo}/actions/runs?branch={branch}&per_page=5&status=completed"
    with urllib.request.urlopen(url) as response:
        data = json.load(response)
    
    failed_runs = [r for r in data.get('workflow_runs', []) if r.get('conclusion') == 'failure']
    
    if not failed_runs:
        print("No failed runs found")
        return 1
    
    run = failed_runs[0]
    run_id = run['id']
    run_number = run['run_number']
    
    print(f"Fetching logs for failed run #{run_number} (ID: {run_id})")
    print(f"URL: {run.get('html_url')}")
    
    # Get job details
    jobs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs"
    with urllib.request.urlopen(jobs_url) as response:
        jobs_data = json.load(response)
    
    if not jobs_data.get('jobs'):
        print("No jobs found")
        return 1
    
    job = jobs_data['jobs'][0]
    job_id = job['id']
    
    print(f"\nJob: {job.get('name')}")
    print(f"Job URL: {job.get('html_url')}")
    
    # Try to get log URL
    # Note: GitHub API doesn't provide direct log download, but we can construct the URL
    log_url = f"https://github.com/{repo}/actions/runs/{run_id}/job/{job_id}"
    print(f"\nLog URL: {log_url}")
    print("\nTo get actual logs, use GitHub CLI:")
    print(f"  gh run view {run_id} --log")
    print("\nOr visit the URL above in a browser.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

