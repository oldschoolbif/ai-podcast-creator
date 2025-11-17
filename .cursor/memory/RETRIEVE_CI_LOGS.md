# Memory: Retrieve CI Logs Directly

## Important Workflow Rule

**When checking CI errors, ALWAYS retrieve the logs directly from GitHub Actions instead of asking the user to copy/paste them.**

### How to Retrieve GitHub Actions Logs

1. **Get workflow run ID:**
   ```bash
   curl -s "https://api.github.com/repos/OWNER/REPO/actions/runs?branch=BRANCH&per_page=1"
   ```

2. **Get job details:**
   ```bash
   curl -s "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID/jobs"
   ```

3. **Access logs:**
   - Use the `html_url` from the job to access the GitHub page
   - Or try to parse HTML content directly
   - Check for error patterns in the HTML/JSON responses

4. **Parse errors:**
   - Look for "FAILED", "ERROR", "exit code" patterns
   - Check step conclusions for "failure"
   - Extract error messages from step outputs

### Why This Matters

- **User efficiency:** Users shouldn't have to manually copy/paste logs
- **Faster debugging:** Direct access means immediate error identification
- **Better workflow:** AI should be proactive in gathering information

### When to Use

- **Always** when user reports CI errors
- **Always** when checking PR status
- **Always** when verifying fixes worked

### Tools Available

- `curl` for API access
- `web_search` for finding GitHub pages
- HTML parsing for extracting error messages
- GitHub API endpoints for workflow/job data

---

**Remember:** Don't ask users to retrieve logs - do it yourself!

