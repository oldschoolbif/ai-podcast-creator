#!/usr/bin/env python3
"""Get the actual CI error messages by parsing HTML."""
import json
import re
import sys
import urllib.request
from html import unescape

def extract_errors_from_html(html_content):
    """Extract error messages from GitHub Actions HTML."""
    errors = []
    
    # Look for common error patterns in HTML
    patterns = [
        r'FAILED\s+[^\n<]+',
        r'ERROR\s+[^\n<]+',
        r'AssertionError[^\n<]+',
        r'ImportError[^\n<]+',
        r'ModuleNotFoundError[^\n<]+',
        r'SyntaxError[^\n<]+',
        r'FAILED\s+\d+\s+[^\n<]+',
        r'=\s+\d+\s+failed[^\n<]+',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        errors.extend(matches)
    
    return errors[:50]  # Limit to first 50

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
    run_url = run.get('html_url')
    
    print(f"Run #{run_number}")
    print(f"Status: {run.get('status')}")
    print(f"Conclusion: {run.get('conclusion', 'N/A')}")
    print(f"URL: {run_url}\n")
    
    # Try to get HTML content
    try:
        with urllib.request.urlopen(run_url) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        errors = extract_errors_from_html(html)
        if errors:
            print("Found potential errors in HTML:")
            for i, error in enumerate(errors[:20], 1):
                print(f"{i}. {error[:200]}")
        else:
            print("Could not extract errors from HTML.")
            print("Please check the workflow logs manually at:")
            print(f"  {run_url}")
    except Exception as e:
        print(f"Could not fetch HTML: {e}")
        print(f"Please check logs manually: {run_url}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

