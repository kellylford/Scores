# GitHub Branch Protection & Release Branch Management Guide

## 🎯 Overview

This guide covers how to protect and "lock" branches in GitHub, with specific focus on preserving release branches and preventing unwanted changes to completed releases.

## 🔒 Branch Protection Concepts

### What is Branch Protection?
GitHub's **Branch Protection Rules** allow you to control how changes are made to specific branches. While not technically "locking," these rules can effectively prevent modifications to important branches.

### Common Use Cases
- **Protect main/master branch** - Require pull requests and reviews
- **Lock release branches** - Prevent changes to completed releases  
- **Enforce quality gates** - Require CI/CD checks before merging
- **Maintain history** - Preserve important development milestones

---

## 🛠️ Branch Protection Methods

### Method 1: GitHub Web Interface (Recommended)

#### **Step-by-Step Setup:**

1. **Navigate to Repository Settings**
   - Go to your repository on GitHub
   - Click the **Settings** tab
   - Select **Branches** from the left sidebar

2. **Create Protection Rule**
   - Click **Add rule** or **Add classic branch protection rule**
   - Enter branch name pattern (see patterns below)

3. **Configure Protection Options**
   - Choose from available protection settings
   - Apply to administrators if desired
   - Save the rule

#### **Branch Name Patterns:**
```bash
# Specific branch
main

# All release branches
*release

# Version-specific releases  
v*.*.*

# Multiple patterns (separate rules needed)
release/*
hotfix/*
```

#### **Protection Options:**
- ✅ **Restrict pushes to matching branches** - Prevents direct pushes
- ✅ **Require a pull request before merging** - Forces PR workflow
- ✅ **Require status checks to pass** - CI/CD must succeed
- ✅ **Require branches to be up to date** - Must sync with base branch
- ✅ **Require review from code owners** - Designated reviewers needed
- ✅ **Dismiss stale reviews** - New commits invalidate approvals
- ✅ **Restrict who can push** - Only specific users/teams
- ✅ **Include administrators** - Rules apply to repo owners too

### Method 2: GitHub CLI

#### **Installation:**
```bash
# Install GitHub CLI
# Windows (via winget)
winget install GitHub.cli

# Or download from: https://cli.github.com/
```

#### **Branch Protection Commands:**
```bash
# Lock a specific release branch
gh api repos/OWNER/REPO/branches/BRANCH/protection \
  --method PUT \
  --field restrictions='{"users":[],"teams":[],"apps":[]}' \
  --field enforce_admins=true

# Example for our Scores repository
gh api repos/kellylford/Scores/branches/0.5release/protection \
  --method PUT \
  --field restrictions='{"users":[],"teams":[],"apps":[]}' \
  --field enforce_admins=true

# Remove protection (unlock branch)
gh api repos/kellylford/Scores/branches/0.5release/protection \
  --method DELETE
```

#### **Check Protection Status:**
```bash
# View current protection rules
gh api repos/kellylford/Scores/branches/0.5release/protection

# List all protected branches
gh api repos/kellylford/Scores/branches --jq '.[] | select(.protected==true) | .name'
```

### Method 3: GitHub REST API

#### **Create Protection Rule:**
```bash
curl -X PUT \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/kellylford/Scores/branches/0.5release/protection \
  -d '{
    "required_status_checks": null,
    "enforce_admins": true,
    "required_pull_request_reviews": null,
    "restrictions": {
      "users": [],
      "teams": [],
      "apps": []
    }
  }'
```

---

## 🎯 Specific Scenarios

### Scenario 1: Lock Completed Release Branches

**Goal:** Prevent any changes to `0.5release` and `0.51release` branches.

**Solution:**
```bash
# Pattern-based rule (covers both branches)
Branch pattern: *release
Protection: Restrict pushes + Include administrators
```

**Benefits:**
- ✅ Both current and future release branches protected
- ✅ Branches preserved as historical snapshots
- ✅ Tags remain intact and accessible
- ✅ Can't accidentally modify completed releases

### Scenario 2: Protect Main Branch (Solo Developer)

**Goal:** Enforce discipline for a solo developer using PR workflow.

**Recommended Settings:**
```bash
Branch: main
✅ Require a pull request before merging
✅ Require branches to be up to date  
❌ Require review (solo developer)
✅ Include administrators (applies to you)
```

**Workflow:**
1. Create feature branch for changes
2. Make commits on feature branch
3. Create PR to merge to main
4. Merge PR (automatic since no review required)

### Scenario 3: Team Development

**Goal:** Full protection for collaborative development.

**Recommended Settings:**
```bash
Branch: main
✅ Require a pull request before merging
✅ Require review from code owners
✅ Require status checks to pass
✅ Require branches to be up to date
✅ Dismiss stale reviews
✅ Include administrators
```

---

## 🗂️ Alternative: Branch Deletion

### When to Delete vs Protect

**Delete If:**
- ✅ You have tags marking the exact release state
- ✅ You want to keep repository clean
- ✅ You don't need branch-based references

**Protect If:**
- ✅ You want visible branch history
- ✅ You might need to reference branch commits
- ✅ You want to prevent accidental recreation

### Deletion Commands

```bash
# Delete local tracking branches
git branch -d -r origin/0.5release origin/0.51release

# Delete remote branches
git push origin --delete 0.5release
git push origin --delete 0.51release

# Verify deletion
git branch -a
```

**Note:** This only deletes branches, not tags. Your release tags (`v0.5.0-preview`, `v0.51.0-preview`) remain intact.

---

## 📋 Best Practices

### Release Branch Management

1. **Use Consistent Naming**
   ```bash
   # Good patterns
   release/v1.0.0
   1.0.0-release  
   v1.0-release
   
   # Our current pattern
   0.5release
   0.51release
   ```

2. **Protection Timing**
   - Protect immediately after release creation
   - Use pattern-based rules for automatic protection
   - Document protection rules in repository README

3. **Tag Strategy**
   ```bash
   # Create tags before protecting branches
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   
   # Then protect the branch
   ```

### Repository Rules

1. **Pattern-Based Protection**
   ```bash
   # Covers all release branches
   *release
   release/*
   v*.*.*
   hotfix/*
   ```

2. **Graduated Protection Levels**
   ```bash
   # Main branch: Full protection
   main: Require PR + Reviews + CI
   
   # Release branches: Lock completely  
   *release: Restrict all pushes
   
   # Feature branches: No protection
   feature/*: (no rules)
   ```

---

## 🚨 Important Considerations

### Access Control
- **Include Administrators**: Even repo owners follow rules
- **Emergency Access**: GitHub provides override mechanisms for emergencies
- **Team Permissions**: Rules interact with repository permissions

### CI/CD Integration
- **Status Checks**: Require builds/tests to pass
- **Required Contexts**: Specify which CI systems must succeed
- **Branch Updates**: Automatic updates vs manual merging

### Recovery Options
- **Rule Modification**: Protection rules can be updated anytime
- **Emergency Override**: GitHub admins can bypass in emergencies
- **Branch Recreation**: Deleted branches can be recreated from commits

---

## 🔧 Troubleshooting

### Common Issues

**"Can't push to protected branch"**
```bash
# Solution: Use pull request workflow
git checkout -b feature/my-changes
git push origin feature/my-changes
# Create PR on GitHub
```

**"Status checks required but not configured"**
```bash
# Solution: Either configure CI or disable status checks
# In branch protection: Uncheck "Require status checks"
```

**"Branch protection applies to administrators"**
```bash
# Solution: Either follow rules or temporarily disable
# Edit protection rule: Uncheck "Include administrators"
```

### Emergency Access

If you need to bypass protection temporarily:
1. **Disable Protection**: Remove or modify the rule
2. **Make Changes**: Push necessary fixes  
3. **Re-enable Protection**: Restore the original rule

---

## 📖 Reference Links

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [GitHub CLI Branch Commands](https://cli.github.com/manual/gh_api)
- [GitHub REST API - Branches](https://docs.github.com/en/rest/branches/branch-protection)
- [Repository Rulesets (newer feature)](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)

---

## 📝 For Scores Repository

### Current State
- **Release Branches**: `0.5release`, `0.51release` 
- **Release Tags**: `v0.5.0-preview`, `v0.51.0-preview`
- **Main Branch**: `main` (active development)

### Recommended Action
Create branch protection rule:
- **Pattern**: `*release`
- **Protection**: Restrict pushes + Include administrators
- **Result**: Both current and future release branches automatically protected

This preserves release history while preventing accidental modifications to completed releases.
