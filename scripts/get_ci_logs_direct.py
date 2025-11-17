#!/usr/bin/env python3
"""Get CI logs directly from GitHub API."""
import json
import sys
import urllib.request
import base64
import gzip

def main():
    repo = "oldschoolbif/ai-podcast-creator"
    branch = "qa/avatar-generator-tests"
    
    # Get latest run
    url = f"https://api.github.com/repos/{repo}/actions/runs?branch={branch}&per_page=1"
    with urllib.request.urlopen(url) as response:
        data = json.load(response)
    
    if not data.get('workflow_runs'):
        print("No runs found")
        return 1
    
    run = data['workflow_runs'][0]
    run_id = run['id']
    run_number = run['run_number']
    conclusion = run.get('conclusion', 'N/A')
    
    print(f"Run #{run_number} - {conclusion}")
    print(f"URL: {run.get('html_url')}")
    
    # Get job
    jobs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs"
    with urllib.request.urlopen(jobs_url) as response:
        jobs_data = json.load(response)
    
    if not jobs_data.get('jobs'):
        print("No jobs found")
        return 1
    
    job = jobs_data['jobs'][0]
    job_id = job['id']
    job_name = job.get('name', 'unknown')
    
    print(f"\nJob: {job_name}")
    print(f"Job URL: {job.get('html_url')}")
    
    # Get logs - GitHub API requires authentication for logs, but we can try
    # For public repos, logs might be accessible via HTML
    log_url = f"https://github.com/{repo}/actions/runs/{run_id}/job/{job_id}"
    print(f"\nLog URL: {log_url}")
    
    # Try to get logs via API (may require auth token)
    # For now, print instructions
    print("\n" + "="*80)
    print("To get actual logs, use GitHub CLI:")
    print(f"  gh run view {run_id} --log > ci_logs.txt")
    print("\nOr visit the URL above and copy the error output.")
    print("="*80)
    
    # Check if there are failed steps
    if 'steps' in job:
        failed_steps = [s for s in job['steps'] if s.get('conclusion') == 'failure']
        if failed_steps:
            print(f"\nFailed steps ({len(failed_steps)}):")
            for step in failed_steps:
                print(f"  - {step.get('name', 'unknown')}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

