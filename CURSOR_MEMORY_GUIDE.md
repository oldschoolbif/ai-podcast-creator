# 🧠 Cursor Memory Files - Complete Guide

**Location:** `.cursor/memory/` directory

---

## 📁 Current Memory Files

### **1. TEST_INFRASTRUCTURE_WORKFLOW.md**
**Purpose:** Critical lessons about test stability and mutation testing workflow

**Key Points:**
- Always validate test suite stability locally before expensive operations
- Fix ALL infrastructure issues in batches, not one-by-one
- Mutation testing requires stable, deterministic test suite
- Distinguish between test infrastructure (fixtures, markers) and test logic

**Action:** When asked to run mutation testing, FIRST run `pytest` locally to validate stability

---

### **2. GPU_QUARANTINE.md**
**Purpose:** GPU test marking conventions

**Key Points:**
- Tests marked `@pytest.mark.gpu` are skipped by default
- Use `PY_ENABLE_GPU_TESTS=1` to enable GPU tests
- Mutmut excludes GPU tests by default for determinism
- Use `scripts/test_env_example.*` to set environment variables

**Action:** Always mark device-dependent tests with `@pytest.mark.gpu`

---

### **3. HARDWARE_ACCELERATION.md**
**Purpose:** Resource usage profiles

**Key Points:**
- Cursor may use 80-90% of CPU cores and GPU resources
- Controlled by `PY_PARALLEL`, `PY_GPU_MAX_LOAD`, `PY_MEMORY_LIMIT_FRACTION`
- Safe fallback at 50% if thermal/resource alerts occur

**Action:** Default to parallel test execution and GPU acceleration unless disabled

---

## 🔍 How to View Memory Files

### **Method 1: List All Memory Files**
```powershell
# List all memory files
Get-ChildItem .cursor\memory\*.md

# View a specific memory file
Get-Content .cursor\memory\TEST_INFRASTRUCTURE_WORKFLOW.md
```

### **Method 2: In Cursor**
1. Open `.cursor/memory/` folder
2. Browse the `.md` files
3. Each file contains important context and decisions

### **Method 3: Reference in Conversations**
```markdown
"Check .cursor/memory/TEST_INFRASTRUCTURE_WORKFLOW.md for our testing approach"
```

---

## 📝 How Memory Files Work

### **What They Are:**
- Markdown files stored in `.cursor/memory/` directory
- Automatically referenced by Cursor AI
- Contain important decisions, workflows, and conventions
- Help maintain context across sessions

### **What They Contain:**
- **Title:** Brief summary
- **Summary:** What was decided/learned
- **Action:** What to do next time

### **When They're Used:**
- Cursor automatically references them when relevant
- You can explicitly mention them in conversations
- They help maintain consistency across sessions

---

## 🎯 Current Memory Files Summary

| File | Purpose | Key Decision |
|------|---------|--------------|
| `TEST_INFRASTRUCTURE_WORKFLOW.md` | Test stability | Validate locally before expensive operations |
| `GPU_QUARANTINE.md` | GPU tests | Mark GPU tests, skip by default |
| `HARDWARE_ACCELERATION.md` | Resource usage | Use parallel execution by default |

---

## 💡 How to Add New Memory Files

### **Option 1: Let Cursor Create Them**
When Cursor learns something important, it may automatically create memory files.

### **Option 2: Create Manually**
Create a new `.md` file in `.cursor/memory/` with this format:

```markdown
Title: [Brief Title]

Summary: [What was decided/learned]

Action: [What to do next time]
```

### **Option 3: Ask Cursor**
```markdown
"Remember this decision: [decision]. Create a memory file for it."
```

---

## 🔄 How to Update Memory Files

### **Edit Directly:**
1. Open `.cursor/memory/[FILE].md`
2. Edit the content
3. Save the file

### **Ask Cursor:**
```markdown
"Update .cursor/memory/TEST_INFRASTRUCTURE_WORKFLOW.md with [new information]"
```

---

## 📚 Best Practices

### **What to Store:**
- ✅ Important decisions and rationale
- ✅ Workflow conventions
- ✅ Configuration patterns
- ✅ Lessons learned
- ✅ Recurring issues and solutions

### **What NOT to Store:**
- ❌ Temporary information
- ❌ Session-specific details
- ❌ Code snippets (use code files instead)
- ❌ Personal preferences (unless project-wide)

---

## 🔍 Finding Memory Files

### **Quick Commands:**
```powershell
# List all memory files
ls .cursor\memory\

# View all memory file titles
Get-ChildItem .cursor\memory\*.md | ForEach-Object { 
    Write-Host "`n=== $($_.Name) ===" -ForegroundColor Cyan
    Get-Content $_.FullName | Select-Object -First 5
}

# Search memory files for keyword
Select-String -Path .cursor\memory\*.md -Pattern "test" -CaseSensitive:$false
```

---

## 🎯 Using Memory Files

### **In Conversations:**
```markdown
"Check .cursor/memory/TEST_INFRASTRUCTURE_WORKFLOW.md for our testing approach"
```

### **To Restore Context:**
```markdown
"Read all memory files in .cursor/memory/ to understand project conventions"
```

### **To Update:**
```markdown
"Update .cursor/memory/[FILE].md with [new information]"
```

---

## 📋 Current Memory Files List

1. **TEST_INFRASTRUCTURE_WORKFLOW.md**
   - Test stability and mutation testing workflow
   - Batch fixes, validate locally first

2. **GPU_QUARANTINE.md**
   - GPU test marking conventions
   - Skip by default, enable with env var

3. **HARDWARE_ACCELERATION.md**
   - Resource usage profiles
   - Parallel execution defaults

---

## 🔗 Related Files

- **Session Summaries:** `SESSION_*.md` files in root
- **Status Files:** `*_STATUS_*.md` files
- **Context Files:** `WHERE_YOU_LEFT_OFF.md`, `CURRENT_CONTEXT_SUMMARY.md`

---

## ✅ Summary

**Memory Files Location:** `.cursor/memory/`

**Current Files:**
- `TEST_INFRASTRUCTURE_WORKFLOW.md`
- `GPU_QUARANTINE.md`
- `HARDWARE_ACCELERATION.md`

**How to View:**
```powershell
Get-ChildItem .cursor\memory\*.md
```

**How to Use:**
- Reference them in conversations
- Cursor automatically uses them when relevant
- Update them as decisions change

---

*Memory files help maintain context and consistency across Cursor sessions!*

