#!/usr/bin/env python3
"""Get the latest CI run details."""
import json
import sys
import urllib.request

def main():
    repo = "oldschoolbif/ai-podcast-creator"
    branch = "qa/avatar-generator-tests"
    
    # Get latest runs
    url = f"https://api.github.com/repos/{repo}/actions/runs?branch={branch}&per_page=5"
    with urllib.request.urlopen(url) as response:
        data = json.load(response)
    
    runs = [r for r in data['workflow_runs'] if 'Deterministic' in r.get('name', '')]
    
    if not runs:
        print("No Deterministic Test Suite runs found")
        return 1
    
    latest = runs[0]
    run_id = latest['id']
    run_number = latest['run_number']
    
    print(f"Latest run: #{run_number}")
    print(f"Status: {latest.get('status')}")
    print(f"Conclusion: {latest.get('conclusion', 'N/A')}")
    print(f"URL: {latest.get('html_url')}")
    
    # Get job details
    jobs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs"
    with urllib.request.urlopen(jobs_url) as response:
        jobs_data = json.load(response)
    
    if jobs_data.get('jobs'):
        job = jobs_data['jobs'][0]
        steps = job.get('steps', [])
        
        print(f"\nJob: {job.get('name')}")
        print(f"Status: {job.get('status')}")
        print(f"Conclusion: {job.get('conclusion', 'N/A')}")
        
        print("\nAll steps:")
        for step in steps:
            status = step.get('status', 'N/A')
            conclusion = step.get('conclusion', 'N/A')
            name = step.get('name', 'N/A')
            print(f"  Step {step.get('number', '?')}: {name} - {status} - {conclusion}")
        
        failed = [s for s in steps if s.get('conclusion') == 'failure']
        if failed:
            print(f"\nFailed steps ({len(failed)}):")
            for step in failed:
                print(f"  Step {step.get('number')}: {step.get('name')}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

