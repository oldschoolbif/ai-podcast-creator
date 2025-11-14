#!/usr/bin/env python3
"""Get detailed CI run information including step outputs."""
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
    
    # Find pytest and compare steps
    pytest1_step = next((s for s in steps if 'Pytest run 1' in s.get('name', '')), None)
    pytest2_step = next((s for s in steps if 'Pytest run 2' in s.get('name', '')), None)
    compare_step = next((s for s in steps if 'Compare' in s.get('name', '')), None)
    
    print("Key Steps:")
    if pytest1_step:
        print(f"  Pytest run 1: {pytest1_step.get('conclusion', 'N/A')} - {pytest1_step.get('status', 'N/A')}")
    if pytest2_step:
        print(f"  Pytest run 2: {pytest2_step.get('conclusion', 'N/A')} - {pytest2_step.get('status', 'N/A')}")
    if compare_step:
        print(f"  Compare: {compare_step.get('conclusion', 'N/A')} - {compare_step.get('status', 'N/A')}")
    
    # Check if compare step failed
    if compare_step and compare_step.get('conclusion') == 'failure':
        print("\n⚠️ Compare step failed!")
        print("This usually means:")
        print("  1. Exit codes weren't captured properly")
        print("  2. Exit codes differ between runs (non-deterministic)")
        print("  3. Pytest failed (exit code != 0)")
        print("\nCheck the workflow logs for detailed error messages.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

