#!/usr/bin/env python3
"""Get detailed CI error information."""
import json
import sys
import urllib.request

def main():
    repo = "oldschoolbif/ai-podcast-creator"
    branch = "qa/avatar-generator-tests"
    
    # Get latest runs
    url = f"https://api.github.com/repos/{repo}/actions/runs?branch={branch}&per_page=3"
    with urllib.request.urlopen(url) as response:
        data = json.load(response)
    
    runs = [r for r in data['workflow_runs'] if 'Deterministic' in r.get('name', '')]
    
    if not runs:
        print("No Deterministic Test Suite runs found")
        return 1
    
    latest = runs[0]
    run_id = latest['id']
    
    print(f"Latest run: #{latest['run_number']}")
    print(f"Status: {latest.get('status')}")
    print(f"Conclusion: {latest.get('conclusion', 'N/A')}")
    print(f"URL: {latest.get('html_url')}\n")
    
    # Get job details
    jobs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs"
    with urllib.request.urlopen(jobs_url) as response:
        jobs_data = json.load(response)
    
    if not jobs_data.get('jobs'):
        print("No jobs found")
        return 1
    
    job = jobs_data['jobs'][0]
    steps = job.get('steps', [])
    
    # Find the pytest step
    pytest_step = next((s for s in steps if 'pytest' in s.get('name', '').lower()), None)
    
    if pytest_step:
        print(f"Pytest step: {pytest_step.get('name')}")
        print(f"Status: {pytest_step.get('status')}")
        print(f"Conclusion: {pytest_step.get('conclusion', 'N/A')}")
        
        if pytest_step.get('conclusion') == 'failure':
            print("\n❌ Pytest step failed!")
            print("Check the workflow logs for detailed error messages.")
    
    failed_steps = [s for s in steps if s.get('conclusion') == 'failure']
    if failed_steps:
        print(f"\nFailed steps ({len(failed_steps)}):")
        for step in failed_steps:
            print(f"  - {step.get('name')} (step {step.get('number')})")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

