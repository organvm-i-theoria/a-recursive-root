# Git Workflow Visual Guide

**Quick visual reference for understanding your repository**

---

## Your Repository Right Now

```
┌─────────────────────────────────────────────────────────────────┐
│                        GITHUB (REMOTE)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Branch: main (origin/main)                                     │
│  └─ Initial commit only                                         │
│     Status: Not updated with any work ⚠️                        │
│                                                                 │
│  Branch: claude/foundation-architecture-setup-...               │
│  └─ Phase 2 Complete: AI Council System                        │
│     Location: workspace/projects/ai-council-system/             │
│     Files: 100+ files, ~20,000 lines                           │
│     Status: PRODUCTION READY ✅                                 │
│                                                                 │
│  Branch: claude/explain-git-workflow-...                        │
│  └─ Documentation and merged PRs                                │
│     Status: Current work location 📍                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
          │                    │                    │
          │ git push           │ git push           │ git push
          │                    │                    │
          ↓                    ↓                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR LOCAL MACHINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Working Directory: /home/user/a-recursive-root                 │
│                                                                 │
│  Branches (git branch -a):                                      │
│  ├─ main                                                        │
│  ├─ claude/foundation-architecture-setup-...                    │
│  └─ claude/explain-git-workflow-... ← YOU ARE HERE              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## How Branches Work: The Timeline

```
TIME ═══════════════════════════════════════════════════════>

START
  │
  │  2716f9a: Initial project structure
  │  [All branches start from here]
  │
  ├─────────────────────────────── MAIN BRANCH ────────────────────
  │                                (no new commits)
  │                                (still at initial state)
  │
  │
  ├─────────── COPILOT/STACK-DEEP-DIVE ────────────────────────────
  │                                                                │
  │  94ae672: Initial plan                                        │
  │  5cd32f1: Add software stack docs                             │
  │  f604ed2: Improve placeholder values                          │
  │  374bc41: Add user documentation                              │
  │                                                                │
  │  [PR #1 CREATED]                                              │
  │  "Please merge these 4 commits into                           │
  │   claude/explain-git-workflow branch"                         │
  │                                                                │
  │                                                                │
  ├─────────── EXPLAIN-GIT-WORKFLOW ────────────────────────┐     │
  │                                                          │     │
  │                                                          │     │
  │  78cdda2: Merge PR #2 (foundation architecture)         │     │
  │  d6d91ca: Merge PR #1 (stack deep dive) ←───────────────┘     │
  │                      [Merged from above]                      │
  │                                                                │
  │  [Current work location] 📍                                   │
  │                                                                │
  │                                                                │
  ├─────────── FOUNDATION-ARCHITECTURE ─────────────────────────┐ │
  │                                                              │ │
  │  ab6f15a: Phase 1 - tasks 1-3                               │ │
  │  b618e5a: Phase 1 Complete                                  │ │
  │  a3314ea: Working Prototype Complete                        │ │
  │  2b13f4b: Add project status document                       │ │
  │  f4fa626: Phase 2 Complete ✅                                │ │
  │                                                              │ │
  │  [All your AI Council System code lives here]               │ │
  │                                                              │ │
  │  [PR #2 CREATED]                                            │ │
  │  "Please merge these 5 commits into                         │ │
  │   claude/explain-git-workflow branch"  ─────────────────────┘ │
  │                                                                │
  └────────────────────────────────────────────────────────────────┘
```

---

## What a Pull Request Actually Does

### Before PR

```
BRANCH A (main)
  │
  │  commit 1
  │  commit 2
  │  [your stable code]
  │
  │

BRANCH B (feature)
  │
  │  commit 1 (from main)
  │  commit 2 (from main)
  │  commit 3 (YOUR NEW WORK)
  │  commit 4 (YOUR NEW WORK)
  │  commit 5 (YOUR NEW WORK)
  │
```

### Create PR: "Merge Branch B into Branch A"

```
On GitHub:
┌─────────────────────────────────────────┐
│  Pull Request #123                      │
│  From: feature → To: main               │
├─────────────────────────────────────────┤
│  Changes:                               │
│  + 500 lines added                      │
│  - 20 lines removed                     │
│  5 files changed                        │
│                                         │
│  Commits to be merged:                  │
│  • commit 3 (YOUR NEW WORK)            │
│  • commit 4 (YOUR NEW WORK)            │
│  • commit 5 (YOUR NEW WORK)            │
│                                         │
│  Status: ⏳ Awaiting review             │
│                                         │
│  [Merge Pull Request Button]           │
└─────────────────────────────────────────┘
```

### After Merge

```
BRANCH A (main)
  │
  │  commit 1
  │  commit 2
  │  commit 3 (from Branch B) ←┐
  │  commit 4 (from Branch B)  │ ALL YOUR WORK
  │  commit 5 (from Branch B)  │ IS NOW HERE
  │  commit M (merge commit) ←─┘
  │
  │  [now includes all your work]
  │

BRANCH B (feature)
  │
  │  commit 1
  │  commit 2
  │  commit 3 (YOUR NEW WORK)
  │  commit 4 (YOUR NEW WORK)
  │  commit 5 (YOUR NEW WORK)
  │
  │  [still exists, marked "merged" on GitHub]
  │
```

### Key Points

1. **Branch B still exists** after merge
2. **All commits are preserved** in both places
3. **Branch A gains new commits** from Branch B
4. **A "merge commit" is created** linking the histories
5. **Nothing is deleted** - both branches remain

---

## How Data Never Gets Lost

### Scenario: Accidentally Delete a Branch

```
BEFORE:
  main ─── A ─── B ─── C
                        │
  feature ─────────────── D ─── E ─── F
                                      ↑
                                  (branch pointer)

git branch -D feature  ← DELETE THE BRANCH

AFTER:
  main ─── A ─── B ─── C
                        │
  ???????????????????????? D ─── E ─── F
                                      ↑
                                 (commits still exist!
                                  just no label pointing to them)

RECOVER:
  git reflog              ← Find commit F's hash: abc1234
  git checkout abc1234    ← Go to that commit
  git checkout -b feature-recovered  ← Create new branch

RESULT:
  main ─── A ─── B ─── C
                        │
  feature-recovered ──── D ─── E ─── F
                                      ↑
                                  (recovered!)
```

### Scenario: Merge Conflict

```
BRANCH A (main)
  │
  file.txt: "Hello World"
  │

BRANCH B (feature)
  │
  file.txt: "Hello Universe"  ← Changed same line!
  │

git merge feature  ← TRY TO MERGE

RESULT:
  <<<<<<< HEAD
  Hello World        ← Version from main
  =======
  Hello Universe     ← Version from feature
  >>>>>>> feature

  Git says: "I found a conflict! YOU decide which to keep."

  ☑️  Git did NOT delete either version
  ☑️  Git shows you BOTH versions
  ☑️  You manually choose what to keep
```

---

## Your Current Repository Map

```
a-recursive-root/
│
├─ LOCATION: claude/explain-git-workflow-011CUSN6Nu1tuVpbLu9gZBhc
│  │
│  ├─ docs/
│  │  ├─ technical/
│  │  │  └─ software-stack-deep-dive_20251023.md  ← From PR #1
│  │  │
│  │  ├─ user/
│  │  │  └─ ai-handoff-user-summary_20251023.md   ← From PR #1
│  │  │
│  │  └─ [other docs...]
│  │
│  ├─ templates/
│  │  ├─ docker-compose.yml                        ← From PR #1
│  │  ├─ env.example                               ← From PR #1
│  │  └─ requirements.txt                          ← From PR #1
│  │
│  └─ README.md (updated)
│
│
├─ LOCATION: claude/foundation-architecture-setup-011CUQABXuEDbQArFpV8ouxf
│  │
│  ├─ workspace/
│  │  └─ projects/
│  │     └─ ai-council-system/                     ← Phase 2 code
│  │        │
│  │        ├─ core/
│  │        │  ├─ agents/        (7 modules)
│  │        │  ├─ council/       (2 modules)
│  │        │  ├─ events/        (7 modules)
│  │        │  └─ logging/       (2 modules)
│  │        │
│  │        ├─ swarm/            (9 modules)
│  │        ├─ streaming/        (TTS + Video)
│  │        ├─ web/
│  │        │  ├─ backend/       (FastAPI)
│  │        │  └─ frontend/      (Next.js React)
│  │        │
│  │        ├─ examples/         (3 demos)
│  │        ├─ STATUS.md         ← Phase 2 status
│  │        ├─ README.md
│  │        ├─ Dockerfile
│  │        ├─ docker-compose.yml
│  │        └─ requirements.txt
│  │
│  └─ [all other files...]
│
│
└─ LOCATION: main (not updated)
   │
   └─ Initial structure only
```

---

## Branch Switching Visualization

### What Happens When You Switch Branches

```
BEFORE:
  You are on: claude/explain-git-workflow
  Your files:
    docs/technical/software-stack-deep-dive_20251023.md ✅ EXISTS
    workspace/projects/ai-council-system/ ❌ DOES NOT EXIST

COMMAND:
  git checkout claude/foundation-architecture-setup-011CUQABXuEDbQArFpV8ouxf

AFTER:
  You are on: claude/foundation-architecture-setup
  Your files:
    docs/technical/software-stack-deep-dive_20251023.md ❌ DOES NOT EXIST
    workspace/projects/ai-council-system/ ✅ EXISTS

WHAT HAPPENED:
  ┌─────────────────────────────────────────┐
  │  Git replaced ALL files in your         │
  │  working directory with the files       │
  │  from the new branch.                   │
  │                                         │
  │  ✅ Old files are still safe in the     │
  │     old branch's history                │
  │                                         │
  │  ✅ New files appear instantly          │
  │                                         │
  │  ✅ No data was lost                    │
  └─────────────────────────────────────────┘
```

---

## The Pull Request Lifecycle

```
STEP 1: Create Branch
┌─────────────────┐
│   git checkout  │
│   -b feature/X  │
└────────┬────────┘
         ↓
┌─────────────────┐
│  You now have   │
│  your own       │
│  workspace      │
└────────┬────────┘


STEP 2: Make Changes
         ↓
┌─────────────────┐
│  Edit files     │
│  git add .      │
│  git commit     │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Changes saved  │
│  in commits     │
└────────┬────────┘


STEP 3: Push to GitHub
         ↓
┌─────────────────┐
│  git push       │
│  origin         │
│  feature/X      │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Branch now on  │
│  GitHub         │
└────────┬────────┘


STEP 4: Create Pull Request
         ↓
┌─────────────────────────────┐
│  On GitHub.com:             │
│  Click "New Pull Request"   │
│                             │
│  From: feature/X            │
│  To: main                   │
│                             │
│  Write description          │
│  Click "Create"             │
└────────┬────────────────────┘
         ↓
┌─────────────────┐
│  PR is now      │
│  OPEN           │
│  Status: ⏳     │
└────────┬────────┘


STEP 5: Review & Discussion
         ↓
┌─────────────────────────┐
│  Reviewers comment      │
│  You respond            │
│  You make changes       │
│  (git commit + push)    │
│                         │
│  PR updates             │
│  automatically          │
└────────┬────────────────┘
         ↓
┌─────────────────┐
│  Approved ✅    │
└────────┬────────┘


STEP 6: Merge
         ↓
┌─────────────────────────┐
│  Click "Merge PR"       │
│                         │
│  Options:               │
│  • Merge commit         │
│  • Squash and merge     │
│  • Rebase and merge     │
└────────┬────────────────┘
         ↓
┌──────────────────────────┐
│  PR Status: MERGED ✅    │
│                          │
│  All your commits are    │
│  now in target branch    │
│                          │
│  Your branch still       │
│  exists (until deleted)  │
└──────────────────────────┘


STEP 7: Clean Up (Optional)
         ↓
┌─────────────────┐
│  Delete branch  │
│  (on GitHub)    │
│                 │
│  Commits are    │
│  STILL in main  │
└─────────────────┘
```

---

## Common Commands Reference

```
┌──────────────────────────────────────────────────────────┐
│                    INFORMATION                           │
├──────────────────────────────────────────────────────────┤
│  git status          │ What changed?                     │
│  git branch -a       │ All branches                      │
│  git log --oneline   │ Commit history                    │
│  git diff            │ Show changes                      │
│  git remote -v       │ GitHub URLs                       │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                  MOVING AROUND                           │
├──────────────────────────────────────────────────────────┤
│  git checkout main        │ Switch to main               │
│  git checkout -b new      │ Create + switch              │
│  git checkout abc1234     │ Go to specific commit        │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                    SAVING WORK                           │
├──────────────────────────────────────────────────────────┤
│  git add .               │ Stage all changes             │
│  git add file.txt        │ Stage specific file           │
│  git commit -m "msg"     │ Save with message             │
│  git push origin branch  │ Upload to GitHub              │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                   COMBINING WORK                         │
├──────────────────────────────────────────────────────────┤
│  git merge other-branch  │ Merge into current            │
│  git pull origin main    │ Get updates from GitHub       │
│  git fetch origin        │ Download (don't merge yet)    │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                   EMERGENCY / UNDO                       │
├──────────────────────────────────────────────────────────┤
│  git reflog              │ See all your actions          │
│  git stash               │ Save changes temporarily      │
│  git stash pop           │ Restore saved changes         │
│  git reset --soft HEAD~1 │ Undo commit (keep changes)    │
│  git checkout -- file    │ Undo changes to file          │
└──────────────────────────────────────────────────────────┘
```

---

## Decision Tree: What Should I Do?

```
START
  │
  ├─ Do you want to add a new feature?
  │  │
  │  └─ YES → git checkout -b feature/name
  │           [work on feature]
  │           git push origin feature/name
  │           [create PR on GitHub]
  │
  ├─ Do you want to see what's on another branch?
  │  │
  │  └─ YES → git checkout other-branch
  │           [look around]
  │           git checkout - (to go back)
  │
  ├─ Do you want to combine two branches?
  │  │
  │  └─ YES → git checkout target-branch
  │           git merge source-branch
  │           git push origin target-branch
  │
  ├─ Did you mess something up?
  │  │
  │  └─ YES → git reflog
  │           [find the commit before you messed up]
  │           git reset --hard abc1234
  │
  ├─ Do you want to see what changed?
  │  │
  │  └─ YES → git diff branch1..branch2
  │           git log --oneline
  │
  └─ Are you confused?
     │
     └─ YES → git status
              git branch --show-current
              [ask for help!]
```

---

## Your Next Steps

### Option 1: Continue Phase 3 on Foundation Branch

```bash
# Switch to the branch with all your Phase 2 code
git checkout claude/foundation-architecture-setup-011CUQABXuEDbQArFpV8ouxf

# Create new branch for Phase 3
git checkout -b claude/phase-3-blockchain-[SESSION_ID]

# Start working on blockchain integration
```

### Option 2: Merge Everything into Main

```bash
# Switch to main
git checkout main

# Merge foundation work
git merge claude/foundation-architecture-setup-011CUQABXuEDbQArFpV8ouxf

# Push to GitHub
git push origin main

# Now main has everything
```

### Option 3: Merge Foundation into Current Branch

```bash
# You're already on claude/explain-git-workflow branch
git merge claude/foundation-architecture-setup-011CUQABXuEDbQArFpV8ouxf

# Now this branch has everything
# (docs + code)
```

---

## Visual Summary

```
YOUR REPOSITORY = TREE WITH BRANCHES

                    ╔═══════╗
                    ║ TRUNK ║  ← Main branch
                    ╚═══╤═══╝
                        │
        ┌───────────────┼───────────────┐
        │               │               │
     ╔══╧══╗         ╔══╧══╗         ╔══╧══╗
     ║  🌿  ║         ║  🌿  ║         ║  🌿  ║  ← Feature branches
     ╚═════╝         ╚═════╝         ╚═════╝
     Branch A        Branch B        Branch C

     • Each branch grows independently
     • Branches can merge back to trunk
     • Branches can merge to each other
     • Nothing is lost when merging
     • You can always create new branches
     • Old branches stay until deleted
```

---

**You now have a visual understanding of Git!** 🎉

Refer back to this guide whenever you're confused about:
- Where your code lives
- How branches relate
- What PRs actually do
- How merging works
- Why data isn't lost

