#!/usr/bin/env python3
"""Get actual CI log output to see real errors."""
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
    
    print(f"\nJob: {job.get('name')}")
    print(f"Job URL: {job.get('html_url')}")
    print(f"\nTo see actual error output, check:")
    print(f"  {job.get('html_url')}")
    print(f"\nOr visit the run page and click on the failed step.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

