#!/bin/bash
# Download CI logs to see actual errors
# This requires GitHub CLI (gh) to be installed and authenticated

REPO="oldschoolbif/ai-podcast-creator"
BRANCH="qa/avatar-generator-tests"

echo "Getting latest workflow run..."
RUN_ID=$(gh run list --repo "$REPO" --branch "$BRANCH" --workflow "Deterministic Test Suite" --limit 1 --json databaseId --jq '.[0].databaseId')

if [ -z "$RUN_ID" ]; then
    echo "No runs found"
    exit 1
fi

echo "Run ID: $RUN_ID"
echo "Downloading logs..."

gh run view "$RUN_ID" --repo "$REPO" --log > ci_logs.txt

echo "Logs saved to ci_logs.txt"
echo "Searching for errors..."

grep -i "FAILED\|ERROR\|failed\|error\|AssertionError\|ImportError" ci_logs.txt | head -50

