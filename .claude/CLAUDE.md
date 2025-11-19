# Project-Specific Claude Instructions for LEH (Legal Evidence Hub)

## 🔴 CRITICAL: Role-Based Git Permissions

**Your Role in This Project**: **L (AI / Data)**

### L Role Responsibilities
- AI Worker implementation
- Parser development (STT/OCR)
- RAG/Embedding pipeline
- Data processing logic

---

## ⛔ ABSOLUTE RESTRICTIONS

### 1. Main Branch Access - STRICTLY FORBIDDEN

**YOU MUST NEVER:**
- ❌ `git push origin main` - **ABSOLUTELY PROHIBITED**
- ❌ `git commit` directly on main branch
- ❌ `git checkout main` for making changes
- ❌ Direct merge to main branch

**REASON:**
- L role has **NO PERMISSION** to push to main
- Main branch is **production-ready only**
- Main changes require **P (PM/Frontend) approval** via PR

### 2. Allowed Git Operations

**YOU CAN SAFELY:**
- ✅ `git push origin dev` - Free to push to dev branch
- ✅ `git checkout dev` - Work on dev branch
- ✅ `git checkout -b feat/ai-xxx` - Create feature branches
- ✅ `git merge feat/xxx` into dev - Merge features to dev
- ✅ Create PR (dev → main) - **But cannot approve/merge it yourself**

---

## 🌱 Branch Strategy (For L Role)

```text
main  ←  [PR ONLY, P approves]  ←  dev  ←  feat/*
                                    ↑
                                 YOU WORK HERE
```

### 🚨 CRITICAL: Safe Workflow to Prevent Code Conflicts

**LESSON LEARNED (2025-11-19):**
> Never create a feature branch without `git pull origin dev` first!
> Old local dev state can restore previously deleted files and cause conflicts.

---

## ⚠️ Phase 0: Pre-Work Safety Checklist (MANDATORY)

**Execute EVERY TIME before starting new work:**

```bash
# Step 1: Verify current location
git branch
# ✅ Confirm you're on 'dev'
# ❌ If on 'main', STOP and switch to dev

# Step 2: Check for uncommitted changes
git status
# ✅ "nothing to commit, working tree clean"
# ❌ If dirty, commit or stash first

# Step 3: ⚠️ MOST CRITICAL - Always fetch and pull!
git fetch origin
git pull origin dev
# 🔴 NEVER SKIP THIS STEP!
# Even if it says "Already up to date", run it!

# Step 4: Verify you have latest commits
git log --oneline -5
# Check H and P teammates' recent work

# Step 5: NOW create feature branch
git checkout -b feat/your-feature-name

# Step 6: Double-check you're on correct branch
git branch
# ✅ * feat/your-feature-name
```

**Why This Matters:**
- Teammates (H, P) push to dev while you work
- Without `git pull`, your local dev is outdated
- Creating branch from old dev = old deleted code comes back
- Merge conflicts and restored deleted files = BAD! ❌

---

### Daily Workflow for L

1. **Always start from dev with Phase 0 checklist**
   ```bash
   git checkout dev
   git fetch origin        # Check remote state
   git pull origin dev     # ⚠️ NEVER SKIP!
   ```

2. **Work on dev or feature branch**
   ```bash
   # Option 1: Direct on dev
   git checkout dev
   # ... make changes ...
   git add .
   git commit -m "feat: implement xxx"
   git push origin dev

   # Option 2: Feature branch
   git checkout -b feat/ai-parser-v2
   # ... make changes ...
   git checkout dev
   git merge feat/ai-parser-v2
   git push origin dev
   ```

3. **When ready for production**
   - Create PR: dev → main
   - Assign to **P** for review
   - **Wait for P's approval** - DO NOT merge yourself

---

## 🚨 Pre-Commit Safety Check

**Before EVERY git push, verify:**

```bash
# Check current branch
git branch

# Output should show:
# * dev          ✅ SAFE to push
# * feat/xxx     ✅ SAFE to push
# * main         ⛔ DANGER! Do NOT push!
```

**If you see `* main` highlighted:**
1. ⛔ STOP IMMEDIATELY
2. Switch back to dev: `git checkout dev`
3. Never commit/push on main

---

## 📁 Your Working Directories

**Primary work areas for L role:**
- `ai_worker/` - AI Worker Lambda/service code
- `leh-ai-pipeline/` - Previous AI pipeline reference
- `docs/specs/AI_PIPELINE_DESIGN.md` - AI architecture
- `tests/ai_worker/` - AI Worker tests

**Avoid direct changes to:**
- `backend/` - H's responsibility (Backend/Infra)
- `frontend/` - P's responsibility (React dashboard)

---

## 🔄 Collaboration Rules

### With H (Backend)
- Coordinate on API contracts
- H manages: FastAPI, RDS, S3 integration
- L manages: AI Worker, parsers, RAG

### With P (Frontend/PM)
- P is your **PR approver**
- P manages GitHub operations
- Communicate before creating dev → main PR

---

## 🛡️ Safety Guidelines

### Git Safety (Updated 2025-11-19)

#### 🔴 Phase 0: Before Starting Work
1. **ALWAYS git pull origin dev first**: Prevents old code resurrection ⚠️
2. **Never skip git fetch**: Even if "Already up to date" ⚠️
3. **Check teammates' recent commits**: `git log --oneline -5` ✅

#### 🟡 During Work
1. **Use dev for experiments**: dev is your playground ✅
2. **Create feat/* for big changes**: Isolate complex work ✅
3. **Commit frequently**: Small, focused commits ✅

#### 🟢 Before Commit (Triple Check)
```bash
# Step 1: Review ALL changes
git diff
# Read every line - no surprises!

# Step 2: Stage files carefully
git add [specific-files]
# ❌ AVOID: git add .
# ✅ PREFER: git add ai_worker/handler.py src/parser.py

# Step 3: Review staged changes
git diff --staged
# Final check before commit

# Step 4: Commit with clear message
git commit -m "feat: [detailed description]"
```

#### 🔵 Before Push (Final Safety Check)
```bash
# Step 1: Verify current branch (MOST CRITICAL!)
git branch
# ✅ * dev or * feat/xxx
# ❌ * main → STOP IMMEDIATELY!

# Step 2: Check for remote updates
git fetch origin

# Step 3: Pull if needed
git pull origin dev

# Step 4: NOW safe to push
git push origin dev
```

#### ❌ Absolute Don'ts
1. **Never force push to main**: `git push -f origin main` ❌
2. **Never git add . blindly**: Review each file ❌
3. **Never skip git pull before feature branch**: Old code resurrection ❌
4. **Never push to main directly**: L role forbidden ❌

### Code Safety
1. **Test before pushing to dev**: Run local tests
2. **Use pytest for AI Worker**: `pytest ai_worker/tests/`
3. **Document breaking changes**: Inform team in commits
4. **Follow commit conventions**:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `refactor:` - Code restructure
   - `docs:` - Documentation
   - `chore:` - Build/config

---

## 🎯 Quick Reference Commands

### Safe Daily Workflow
```bash
# Morning routine
git checkout dev
git pull origin dev

# Work
# ... code changes ...

# Commit
git add .
git commit -m "feat: implement AI feature xxx"

# Safety check (CRITICAL!)
git branch  # Ensure you're on 'dev' or 'feat/*'

# Push (ONLY if on dev/feat/*)
git push origin dev
```

### Creating Features
```bash
# Start feature
git checkout dev
git pull origin dev
git checkout -b feat/ai-emotion-analysis

# Work on feature
# ... code changes ...

# Merge to dev
git checkout dev
git merge feat/ai-emotion-analysis
git push origin dev

# Clean up
git branch -d feat/ai-emotion-analysis
```

### Creating PR to Main (When Ready for Production)
```bash
# Ensure dev is up to date
git checkout dev
git pull origin dev

# Create PR on GitHub
# dev → main
# Assign: P (for review)
# DO NOT MERGE YOURSELF - Wait for P's approval
```

---

## ⚠️ Emergency Protocol

**If you accidentally pushed to main:**

1. **STOP all git operations**
2. Contact P (PM) immediately
3. P will handle revert/rollback
4. Never attempt force push to fix

**If you're unsure about a git operation:**

1. Check current branch: `git branch`
2. Check what will be pushed: `git log origin/dev..dev`
3. Ask team in chat before pushing
4. Better safe than sorry!

---

## 📝 Commit Message Templates

### Feature Implementation
```
feat: implement GPT-4o Vision emotion analysis

- Add emotion detection for image evidence
- Integrate with OpenAI Vision API
- Store emotion tags in DynamoDB
```

### Bug Fix
```
fix: correct timestamp parsing in STT pipeline

- Fix timezone handling for Whisper output
- Ensure consistent UTC timestamps
- Add test cases for edge cases
```

### Refactoring
```
refactor: unify parser interface across all types

- Create BaseParser abstract class
- Migrate text/image/audio parsers to new interface
- Remove duplicate code in parsing logic
```

---

## 🔍 Self-Check Before Any Git Push

**Ask yourself:**

1. ✅ Am I on `dev` or `feat/*` branch?
2. ✅ Have I tested the code locally?
3. ✅ Is my commit message descriptive?
4. ✅ Did I check `git branch` output?
5. ✅ Am I pushing to dev, not main?

**If ANY answer is NO or uncertain:**
- ⛔ STOP
- Fix the issue
- Re-verify checklist

---

**Remember**: As L role, you are a critical part of the AI pipeline, but main branch access is restricted for production stability. Work freely on dev, communicate with team, and let P handle main branch management.

**Last Updated**: 2025-11-19
**Your Role**: L (AI / Data)
**Branch Access**: dev ✅, feat/* ✅, main ❌
