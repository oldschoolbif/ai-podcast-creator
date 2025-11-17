#!/usr/bin/env python3
"""Fetch CI error messages from GitHub Actions."""
import json
import sys
import urllib.request
import urllib.parse

def fetch_workflow_runs(repo, branch, per_page=5):
    """Fetch workflow runs for a branch."""
    url = f"https://api.github.com/repos/{repo}/actions/runs?branch={branch}&per_page={per_page}"
    try:
        with urllib.request.urlopen(url) as response:
            return json.load(response)
    except Exception as e:
        print(f"Error fetching runs: {e}", file=sys.stderr)
        return None

def fetch_job_steps(repo, run_id):
    """Fetch job steps for a workflow run."""
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.load(response)
            jobs = data.get('jobs', [])
            if jobs:
                return jobs[0].get('steps', [])
            return []
    except Exception as e:
        print(f"Error fetching job steps: {e}", file=sys.stderr)
        return []

def main():
    repo = "oldschoolbif/ai-podcast-creator"
    branch = "qa/avatar-generator-tests"
    
    print(f"Fetching workflow runs for {repo} branch {branch}...")
    runs_data = fetch_workflow_runs(repo, branch)
    
    if not runs_data:
        print("Failed to fetch workflow runs")
        return 1
    
    runs = runs_data.get('workflow_runs', [])
    # Filter for "Deterministic Test Suite" workflow specifically
    deterministic_runs = [r for r in runs if 'Deterministic' in r.get('name', '')]
    failed_runs = [r for r in deterministic_runs if r.get('conclusion') == 'failure']
    
    # If no deterministic failures, show any failures
    if not failed_runs:
        failed_runs = [r for r in runs if r.get('conclusion') == 'failure']
    
    if not failed_runs:
        print("No failed runs found")
        return 0
    
    latest_failed = failed_runs[0]
    run_id = latest_failed['id']
    run_number = latest_failed['run_number']
    workflow_name = latest_failed['name']
    
    print(f"\nLatest failed run: #{run_number} ({workflow_name})")
    print(f"Run ID: {run_id}")
    print(f"URL: {latest_failed.get('html_url', 'N/A')}")
    
    steps = fetch_job_steps(repo, run_id)
    failed_steps = [s for s in steps if s.get('conclusion') == 'failure']
    
    if failed_steps:
        print(f"\nFailed steps ({len(failed_steps)}):")
        for step in failed_steps:
            print(f"  Step {step['number']}: {step['name']}")
            print(f"    Status: {step.get('status')}")
            print(f"    Conclusion: {step.get('conclusion')}")
    else:
        print("\nNo failed steps found in API response")
        print("(Note: Step logs require authentication to access)")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

