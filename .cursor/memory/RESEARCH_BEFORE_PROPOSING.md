# Research Before Proposing Changes

## Critical Principle
**ALWAYS research and verify before proposing solutions or making claims about functionality.**

## What Happened
- Proposed auto-enable-merge workflow without checking if GITHUB_TOKEN has required permissions
- Claimed it would "automatically enable auto-merge" without verification
- Workflow failed due to permission limitations that could have been discovered with research

## Lesson Learned
1. **Verify permissions first** - Check if GITHUB_TOKEN or required tokens have necessary permissions
2. **Test assumptions** - Don't assume workflows will work without checking GitHub documentation
3. **Research limitations** - GitHub Actions has security limitations that prevent certain operations
4. **Be honest about unknowns** - If unsure, research first, then propose

## GitHub Actions Limitations to Remember
- GITHUB_TOKEN has limited permissions for security
- Cannot enable auto-merge via workflow (requires user action or GitHub App)
- Cannot bypass branch protection rules
- Cannot perform certain administrative actions

## Best Practice
Before proposing any automation or workflow:
1. Check GitHub documentation for permissions/limitations
2. Verify if GITHUB_TOKEN can perform the action
3. Test in a small PR first if possible
4. Be clear about limitations and workarounds

## Auto-Merge Reality
- **Cannot be automated** with standard GITHUB_TOKEN
- **Must be enabled manually** using: `gh pr merge <PR> --auto --squash`
- **Or use GitHub App** with proper permissions (complex setup)

