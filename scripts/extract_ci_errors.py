#!/usr/bin/env python3
"""Extract actual error messages from CI logs."""
import json
import sys
import urllib.request
import re

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
    
    print(f"Run #{run_number} - {run.get('conclusion', 'N/A')}")
    print(f"URL: {run.get('html_url')}\n")
    
    # Get job
    jobs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs"
    with urllib.request.urlopen(jobs_url) as response:
        jobs_data = json.load(response)
    
    if not jobs_data.get('jobs'):
        print("No jobs found")
        return 1
    
    job = jobs_data['jobs'][0]
    job_url = job.get('html_url')
    
    print(f"Job URL: {job_url}")
    print(f"\nTo see the actual error output:")
    print(f"1. Visit: {job_url}")
    print(f"2. Click on the 'Run tests' step")
    print(f"3. Look for lines starting with 'FAILED' or 'ERROR'")
    print(f"\nThe verbose output (-v) should show which specific tests are failing.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

