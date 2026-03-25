---
name: pr-streamline
description: Streamlines GitHub PR creation by automatically generating PR descriptions from git commits and diffs
triggers:
  - "create a PR"
  - "generate PR description"
  - "help with PR writing"
---

# PR Streamline Skill

Automates GitHub PR description generation to save time and ensure consistent, high-quality PRs.

## What It Does

The pr-streamline skill analyzes your git commits and code changes to automatically generate the first draft of a PR description. It:

1. **Analyzes commits** - Extracts commit messages from your branch
2. **Examines code changes** - Counts files modified and categorizes them
3. **Generates sections** - Creates Purpose, Release Notes, and Risk Assessment
4. **Produces output** - Generates a formatted PR description ready for GitHub

## When to Use It

Use this skill when you're ready to create a GitHub PR and want to:
- Quickly generate a PR description from your commits
- Get a suggested risk level for your changes
- Ensure consistent PR structure across your team
- Save time on mechanical PR writing tasks

## Problem It Solves

Creating high-quality PR descriptions requires:
- Reviewing all your commits to summarize changes
- Assessing the scope and risk of modifications
- Writing release notes from commit messages
- Formatting everything correctly for GitHub

This skill automates the analysis and generation, letting you focus on the creative parts (explaining decisions, guiding reviewers, describing implications).

## Usage

### Basic Usage

Generate a PR description for the current branch:

```bash
python .claude/skills/pr-streamline/scripts/generate-pr-description.py --base trunk
```

### With Custom Branches

```bash
python .claude/skills/pr-streamline/scripts/generate-pr-description.py --base main --target feature/my-feature
```

### Integrate with GitHub CLI

Create a draft PR with auto-generated description:

```bash
gh pr create --title "Your PR Title" \
  --body "$(python .claude/skills/pr-streamline/scripts/generate-pr-description.py --base trunk)" \
  --draft
```

## Output

The skill generates a PR description with six sections:

1. **Purpose** - What problem does this PR solve?
2. **Release Notes** - What should end users know?
3. **Functional Testing Status** - How was this tested?
4. **Performance Testing Status** - Any performance implications?
5. **Overall Product Risk** - Risk assessment (Low/Medium/High)
6. **Comments to Reviewers** - Guidance for code review

## Auto-Generated vs. User-Fillable

### Auto-Generated Sections
- **Purpose** - Synthesized from commits and diff analysis
- **Release Notes** - Formatted from commit messages
- **Overall Product Risk** - Assessed from file count and type analysis

### User-Fillable Sections (Free-Form)
- **Functional Testing Status** - You describe what was tested
- **Performance Testing Status** - You describe performance implications
- **Comments to Reviewers** - You provide review guidance

## Risk Level Suggestions

The skill suggests risk levels: **Low / Medium / High**

- **Low**: Minor changes (≤5 files), tests only, documentation, isolated bug fixes
- **Medium**: Feature changes in isolated modules (5-10 files), localized fixes, moderate scope
- **High**: Core system changes, widespread refactoring (10+ files), affecting multiple modules

Each suggestion includes reasoning you can evaluate and override if needed.

## Files Included

- `scripts/generate-pr-description.py` - Main script for generating descriptions
- `references/pr-template-guide.md` - Comprehensive guide to PR sections with examples
- `SKILL.md` - This file

## Workflow

1. **Make commits** on your feature branch with clear commit messages
2. **Run the generator** to create draft PR description
3. **Review** the auto-generated sections for accuracy
4. **Fill in** the user-facing sections (Testing, Reviewers)
5. **Create PR** with the generated description using GitHub CLI

## Tips for Best Results

- **Write clear commit messages** - They become your Purpose and Release Notes
- **Organize commits logically** - Good commit history produces better narratives
- **Keep PRs focused** - Fewer files = clearer scope and lower risk assessments
- **Fill in testing sections** - These are critical for reviewer confidence
- **Add reviewer guidance** - Specific focus areas help reviewers review effectively

## Example Workflow

```bash
# On your feature branch after making commits
cd my-project

# Generate the PR description
python .claude/skills/pr-streamline/scripts/generate-pr-description.py --base trunk > /tmp/pr-desc.txt

# Review and edit /tmp/pr-desc.txt to fill in testing and reviewer sections

# Create the PR
gh pr create --title "Add platform abstraction layer" --body "$(cat /tmp/pr-desc.txt)"
```

## References

See `references/pr-template-guide.md` for:
- Detailed explanation of each PR section
- Examples of Low/Medium/High risk PRs
- Best practices for release notes
- Tips for reviewer guidance

## Requirements

- Python 3 (for running the generator script)
- Git (for analyzing commits and diffs)
- GitHub CLI optional (for creating PRs directly)

---

Generated with pr-streamline skill
