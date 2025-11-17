# How to Enable Auto-Merge in GitHub

**Repository:** https://github.com/oldschoolbif/ai-podcast-creator

---

## 📍 Step-by-Step Instructions

### **Step 1: Navigate to Repository Settings**
1. Go to your repository: https://github.com/oldschoolbif/ai-podcast-creator
2. Click on the **"Settings"** tab (top right of the repository page)
   - It's in the horizontal menu bar at the top
   - You need to be a repository owner/admin to see this tab

### **Step 2: Go to Pull Requests Section**
1. In the left sidebar, scroll down to **"Pull Requests"**
2. Click on **"Pull Requests"** (under "Code and automation" section)

### **Step 3: Enable Auto-Merge**
1. Look for the section: **"Pull request merges"**
2. Find the checkbox: **"Allow auto-merge"**
3. ✅ **Check the box** to enable it
4. Click **"Save"** or **"Save changes"** button at the bottom

---

## 🎯 Visual Guide

```
GitHub Repository Page
├── Code
├── Issues
├── Pull requests
├── Actions
├── Projects
├── Wiki
├── Security
├── Insights
└── Settings  ← Click here
    │
    └── Left Sidebar:
        ├── General  ← Click here
        │   └── Scroll down to:
        │       └── "Pull Requests" section
        │           └── "Pull request merges"
        │               └── ☑ Allow auto-merge  ← Check this box
        │                   └── Save changes
```

---

## 🔍 Alternative Path (If Different UI)

If you don't see "Pull Requests" in the left sidebar under General:

1. Go to **Settings** → **General**
2. Scroll down to find **"Pull Requests"** section
3. Look for **"Allow auto-merge"** checkbox
4. Enable it and save

---

## ✅ After Enabling

Once auto-merge is enabled:

1. **Verify it's enabled:**
   - The checkbox should be checked
   - You should see a green checkmark or confirmation

2. **Run the batch merge script:**
   ```powershell
   cd D:\dev\AI_Podcast_Creator
   .\scripts\batch_merge_dependabot.ps1 -Group all
   ```

3. **PRs will now auto-merge when CI passes!**

---

## 🚨 If You Don't See Settings Tab

If you don't see the **Settings** tab:
- You may not have admin/owner permissions
- Ask the repository owner to enable it
- Or use the monitor script instead (no permissions needed)

---

## 📝 Quick Link

**Direct link to settings:**
https://github.com/oldschoolbif/ai-podcast-creator/settings

Then navigate to: **General** → Scroll to **"Pull Requests"** section

---

**Once enabled, come back and we'll run the batch merge script!** 🚀

