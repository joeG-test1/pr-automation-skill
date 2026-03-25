# pr-streamline Skill Documentation

Documentation for the `pr-streamline` Claude Code skill -- a project-level custom skill that automates GitHub PR description generation from git commits and diffs.

## Table of Contents

- [Overview](#overview)
- [Prerequisites and Dependencies](#prerequisites-and-dependencies)
- [Installation and File Structure](#installation-and-file-structure)
- [How to Use](#how-to-use)
- [How It Works](#how-it-works)
- [Output Format](#output-format)
- [Risk Assessment Logic](#risk-assessment-logic)
- [Security Considerations](#security-considerations)
- [Configuration](#configuration)
- [Limitations and Known Behaviors](#limitations-and-known-behaviors)
- [Troubleshooting](#troubleshooting)

---

## Overview

The `pr-streamline` skill is a **project-level Claude Code custom skill** that analyzes git history and diffs to automatically generate structured PR descriptions. It is not an official Anthropic-bundled skill -- it is a custom skill following the [Agent Skills open standard](https://agentskills.io) that Claude Code supports.

The skill has two layers:

1. **Claude Code skill integration** (`SKILL.md`) -- Registers the skill with Claude Code via YAML frontmatter so it can be invoked automatically or via slash command.
2. **Python script** (`scripts/generate-pr-description.py`) -- A standalone Python script that runs git commands and produces the formatted PR description.

### What it automates

- Extracting and synthesizing commit messages into a purpose statement
- Formatting commit subjects into release notes
- Counting and categorizing changed files
- Suggesting a risk level (Low / Medium / High) with reasoning
- Producing a `git diff --stat` summary
- Outputting a complete markdown PR description ready for `gh pr create --body`

### What it leaves to you

- Functional testing status
- Performance testing status
- Comments to reviewers

---

## Prerequisites and Dependencies

| Dependency | Required? | Notes |
|---|---|---|
| **Python 3** | Yes | Uses only the standard library (`subprocess`, `argparse`, `pathlib`, `sys`). No `pip install` needed. |
| **Git** | Yes | Must be available in `PATH`. The script shells out to `git log`, `git diff`, and `git branch`. |
| **Claude Code** | Yes | Required to invoke the skill via `/pr-streamline` or trigger phrases. Not needed if running the Python script directly. |
| **GitHub CLI (`gh`)** | No (optional) | Only needed if you want to create the PR directly from the command line using `gh pr create`. The script itself only generates the description text. |

### System Requirements

- Any OS with Python 3 and Git installed (tested on Windows with Python 3.14.3)
- The repository must be a git repository with at least one branch to compare against
- The base branch (default: `trunk`) must exist in the repository

---

## Installation and File Structure

The skill lives inside the `.claude/skills/` directory at the project root:

```
.claude/skills/pr-streamline/
├── SKILL.md                              # Skill definition (YAML frontmatter + docs)
├── scripts/
│   └── generate-pr-description.py        # Main Python script
├── references/
│   └── pr-template-guide.md              # Comprehensive guide with examples
└── assets/                               # Reserved for future use
```

No installation steps are required beyond having the files in this directory structure. Claude Code discovers project-level skills automatically from `.claude/skills/`.

---

## How to Use

### Method 1: Via Claude Code slash command

In a Claude Code session, type:

```
/pr-streamline
```

Claude will invoke the skill and generate the PR description for your current branch.

### Method 2: Via trigger phrases

The skill registers three trigger phrases in its YAML frontmatter. Saying any of these in a Claude Code session will automatically invoke the skill:

- `"create a PR"`
- `"generate PR description"`
- `"help with PR writing"`

### Method 3: Run the Python script directly

You can run the script without Claude Code:

```bash
# Default: compare current branch against 'trunk'
python .claude/skills/pr-streamline/scripts/generate-pr-description.py --base trunk

# Specify both branches explicitly
python .claude/skills/pr-streamline/scripts/generate-pr-description.py --base main --target feature/my-feature

# Override working directory
python .claude/skills/pr-streamline/scripts/generate-pr-description.py --base trunk --cwd /path/to/repo
```

**CLI arguments:**

| Argument | Default | Description |
|---|---|---|
| `--base` | `trunk` | The base branch to compare against |
| `--target` | Current branch (auto-detected) | The feature branch |
| `--cwd` | Current directory | Working directory override |

### Method 4: Pipe into GitHub CLI

Create a draft PR with the auto-generated description:

```bash
gh pr create --title "Your PR Title" \
  --body "$(python .claude/skills/pr-streamline/scripts/generate-pr-description.py --base trunk)" \
  --draft
```

Or save to a file first for editing:

```bash
python .claude/skills/pr-streamline/scripts/generate-pr-description.py --base trunk > /tmp/pr-desc.txt
# Edit /tmp/pr-desc.txt to fill in testing and reviewer sections
gh pr create --title "Your PR Title" --body "$(cat /tmp/pr-desc.txt)"
```

### Recommended Workflow

1. Make commits on your feature branch with clear, descriptive commit messages
2. Run the generator to create a draft PR description
3. Review the auto-generated sections (Purpose, Release Notes, Risk) for accuracy
4. Fill in the user-facing sections (Functional Testing, Performance Testing, Comments to Reviewers)
5. Create the PR with the completed description

---

## How It Works

The Python script (`generate-pr-description.py`) executes a pipeline of git commands and text processing:

### Step 1: Gather git data

The script runs four git commands via `subprocess.run()`:

| Command | Purpose |
|---|---|
| `git log <base>..<target> --pretty=format:%B` | Full commit bodies for purpose synthesis |
| `git log <base>..<target> --pretty=format:%s` | One-line commit subjects for release notes |
| `git diff <base>..<target> --name-status` | Changed files with Add/Modify/Delete status |
| `git diff <base>..<target> --stat` | Diff statistics summary |

### Step 2: Generate Purpose section

- Takes the most recent commit message as the primary purpose
- Includes up to 2 additional commit messages as "Additional changes"
- Appends a summary of how many files were modified
- Filters out `Co-Authored-By` lines

### Step 3: Generate Release Notes

- Formats each commit subject as a bullet point
- Capitalizes the first letter of each entry
- Strips trailing periods for consistency
- Filters out merge commits

### Step 4: Assess Risk Level

- Categorizes all changed files (see [Risk Assessment Logic](#risk-assessment-logic))
- Applies a rule-based decision tree to suggest Low, Medium, or High
- Generates human-readable reasoning

### Step 5: Assemble output

- Combines all sections into a single markdown document
- Includes placeholder text for user-fillable sections
- Appends the `git diff --stat` output as a Summary of Changes

---

## Output Format

The generated PR description contains six sections:

```markdown
## Purpose of this PR
[Auto-generated from commit messages and diff analysis]

## Release Notes
[Auto-generated bullet points from commit subjects]

## Functional Testing Status
[Placeholder -- user fills in]

## Performance Testing Status
[Placeholder -- user fills in]

## Overall Product Risk
**Suggested: Low/Medium/High**
Reasoning: [Auto-generated reasoning]

## Comments to Reviewers
[Placeholder -- user fills in]

---
### Summary of Changes
[git diff --stat output]
```

### Auto-generated vs. user-fillable

| Section | Auto-generated? | Source |
|---|---|---|
| Purpose | Yes | Commit messages + file count |
| Release Notes | Yes | Commit subjects as bullet points |
| Functional Testing Status | No | User fills in |
| Performance Testing Status | No | User fills in |
| Overall Product Risk | Yes | File count + path heuristics |
| Comments to Reviewers | No | User fills in |

---

## Risk Assessment Logic

The `analyze_risk_level()` function categorizes files and applies rules to suggest a risk level.

### File categorization

| Category | Matching criteria |
|---|---|
| Test files | Paths ending in `.test.py`, `.test.js`, `_test.py`, `test_`, `tests/` |
| Doc files | Extensions `.md`, `.rst`, `.txt` |
| Config files | Extensions `.json`, `.yaml`, `.yml`, `.toml`, `.cfg`, `.conf` |
| Core files | Paths containing `core/`, `engine/`, `main/`, `kernel/` |
| Other | Everything else |

### Decision rules (evaluated in order)

| Condition | Risk Level | Reasoning |
|---|---|---|
| <= 3 files AND no core files AND has test files | **Low** | Primarily tests |
| <= 5 files AND no core files | **Low** | Isolated modules |
| Has core files AND > 10 files | **High** | Widespread core impact |
| Has core files (any count) | **Medium** | Focused core changes |
| > 8 files (any type) | **Medium** | Moderate scope |
| Everything else | **Medium** | Standard feature development |

The suggested risk level is always labeled as "Suggested" -- you should review it and override if your judgment differs.

---

## Security Considerations

### Command injection via `shell=True`

The script uses `subprocess.run()` with `shell=True` to execute git commands. The `--base` and `--target` arguments are interpolated directly into shell command strings (e.g., `f"git log {base_branch}..{target_branch}"`).

**Risk:** If an attacker can control the values of `--base` or `--target` (for example, a branch named with shell metacharacters like `` `rm -rf /` `` or `$(malicious-command)`), arbitrary commands could be executed.

**When this matters:**
- In CI/CD pipelines where branch names come from external PR authors or untrusted input
- In automation scripts that pass user-controlled strings as arguments

**When this is low risk:**
- Local developer usage where you control the branch names
- Interactive Claude Code sessions where you manually invoke the skill

**Mitigation options:**
- Switch `shell=True` to `shell=False` and pass commands as a list instead of a string
- Sanitize/validate `--base` and `--target` arguments against a regex like `^[a-zA-Z0-9/_.-]+$`
- Use `shlex.quote()` on interpolated values

### Read-only git operations

The script only runs read-only git commands (`git log`, `git diff`, `git branch`). It never modifies the repository, pushes, or writes files. The output is printed to stdout.

### No network access

The script makes no HTTP requests, API calls, or network connections. All data comes from the local git repository.

### No secrets handling

The script does not read environment variables, credentials files, API keys, or tokens.

### Claude Code permissions

The project's `settings.local.json` grants `Bash(python:*)` permission, which allows Claude Code to run any `python` command without prompting. This means:

- Claude can execute the PR generation script automatically
- Claude can also execute **any other** Python command without a permission prompt
- If you want tighter controls, scope the permission to the specific script path

The `SKILL.md` does **not** define `allowed-tools` in its frontmatter, so it does not grant additional tool permissions beyond what the settings file provides.

### Summary of security posture

| Aspect | Status |
|---|---|
| Shell injection surface | Present (`shell=True` with user-controlled args) |
| Write operations | None (read-only) |
| Network access | None |
| Secrets access | None |
| Scope | Project-level only (not global) |
| Local interactive use | Low risk |
| CI/CD with untrusted input | Requires input sanitization |

---

## Configuration

### Claude Code settings

The skill requires permission to run Python via Bash. This is configured in `.claude/settings.local.json`, which is **gitignored** and must be created locally by each user.

Create `.claude/settings.local.json` with the following content:

```json
{
  "permissions": {
    "allow": [
      "Bash(python:*)",
      "Bash(dir:*)"
    ]
  }
}
```

| Permission | Purpose |
|---|---|
| `Bash(python:*)` | Allows Claude to run the `generate-pr-description.py` script (and any other Python commands) without prompting |
| `Bash(dir:*)` | Allows Claude to run `dir` commands for file listing without prompting |

Without this file, Claude Code will prompt for approval each time it runs the script. You can also approve permissions interactively on a per-invocation basis if you prefer not to create this file.

### Skill registration

The skill is registered via YAML frontmatter in `SKILL.md`:

```yaml
---
name: pr-streamline
description: Streamlines GitHub PR creation by automatically generating PR descriptions from git commits and diffs
triggers:
  - "create a PR"
  - "generate PR description"
  - "help with PR writing"
---
```

- **name**: The slash command name (`/pr-streamline`)
- **description**: Shown in skill listings
- **triggers**: Phrases that cause Claude to auto-invoke the skill

### Changing the default base branch

The script defaults to `trunk` as the base branch. To change this default, edit line 219 of `scripts/generate-pr-description.py`:

```python
parser.add_argument(
    "--base",
    default="trunk",  # Change this to "main" or your default branch
    help="Base branch to compare against (default: trunk)"
)
```

---

## Limitations and Known Behaviors

- **Default base branch is `trunk`**: If your repository uses `main` or `master`, you must pass `--base main` explicitly or modify the script default.
- **Purpose section uses first commit**: The "primary purpose" is taken from the most recent commit message. If your most recent commit is a minor fix, the purpose may not reflect the overall goal of the PR.
- **Release notes include all commits**: Every non-merge commit becomes a bullet point. Internal/WIP commits will appear in the release notes and should be edited out.
- **Risk assessment is heuristic**: The file-count and path-based rules are a rough approximation. A 2-line change to a critical file could be high risk but scored as Low. Always review and override the suggestion.
- **No semantic analysis**: The script does not read file contents or understand the nature of code changes. It only counts files and matches path patterns.
- **Bare `except` clause**: Line 241 uses a bare `except:` when auto-detecting the current branch, which catches all exceptions including `KeyboardInterrupt` and `SystemExit`.
- **Test file detection is limited**: The heuristic checks for common test file patterns but may miss project-specific test conventions (e.g., `spec/` directories, `*_spec.rb` files).

---

## Troubleshooting

### "Error running git command"

- Ensure you are inside a git repository
- Ensure the base branch exists (`git branch -a` to list branches)
- Ensure there are commits between the base and target branches

### "No commits found between branches"

- The target branch has no commits ahead of the base branch
- Check that you are on the correct branch (`git branch`)
- Verify the branch comparison: `git log trunk..HEAD --oneline`

### Script not found

- Ensure the script is at `.claude/skills/pr-streamline/scripts/generate-pr-description.py` relative to the project root
- Check that Python 3 is installed and in `PATH`

### Skill not appearing in Claude Code

- Ensure the `SKILL.md` file exists at `.claude/skills/pr-streamline/SKILL.md`
- Ensure the YAML frontmatter is valid (check for syntax errors)
- Restart Claude Code to pick up new skills

### Permission denied in Claude Code

- Add `"Bash(python:*)"` to your `.claude/settings.local.json` permissions allow list
- Or approve the permission prompt when Claude asks

---

## References

- `SKILL.md` -- Skill definition and usage documentation
- `references/pr-template-guide.md` -- Comprehensive guide with examples for each PR section
- [Agent Skills open standard](https://agentskills.io) -- The standard that Claude Code skills follow
