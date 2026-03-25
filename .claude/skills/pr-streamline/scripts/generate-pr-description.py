#!/usr/bin/env python3
"""Generate PR descriptions by analyzing git commits and diffs."""

import subprocess
import sys
import argparse
from pathlib import Path

def run_git_command(cmd, cwd=None):
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def get_commit_messages(base_branch, target_branch, cwd=None):
    """Get all commit messages between branches."""
    cmd = f"git log {base_branch}..{target_branch} --pretty=format:%B"
    output = run_git_command(cmd, cwd)
    return output if output else ""

def get_commits_list(base_branch, target_branch, cwd=None):
    """Get list of commits with one-line summaries."""
    cmd = f"git log {base_branch}..{target_branch} --pretty=format:%s"
    output = run_git_command(cmd, cwd)
    commits = [line for line in output.split('\n') if line.strip()]
    return commits

def get_changed_files(base_branch, target_branch, cwd=None):
    """Get list of changed files and their stats."""
    cmd = f"git diff {base_branch}..{target_branch} --name-status"
    output = run_git_command(cmd, cwd)

    files = []
    for line in output.split('\n'):
        if line.strip():
            parts = line.split()
            status = parts[0]
            filepath = parts[1] if len(parts) > 1 else ""
            files.append((status, filepath))
    return files

def get_diff_stats(base_branch, target_branch, cwd=None):
    """Get diff statistics."""
    cmd = f"git diff {base_branch}..{target_branch} --stat"
    output = run_git_command(cmd, cwd)
    return output

def analyze_risk_level(changed_files):
    """Analyze and suggest risk level based on changed files."""
    if not changed_files:
        return "Low", "No changes detected."

    total_files = len(changed_files)

    # Categorize files
    core_files = []
    test_files = []
    doc_files = []
    config_files = []
    other_files = []

    for status, filepath in changed_files:
        if filepath.endswith(('.test.py', '.test.js', '_test.py', 'test_', 'tests/')):
            test_files.append(filepath)
        elif filepath.endswith(('.md', '.rst', '.txt')):
            doc_files.append(filepath)
        elif filepath.endswith(('.json', '.yaml', '.yml', '.toml', '.cfg', '.conf')):
            config_files.append(filepath)
        elif any(x in filepath for x in ['core/', 'engine/', 'main/', 'kernel/']):
            core_files.append(filepath)
        else:
            other_files.append(filepath)

    # Determine risk level
    if total_files <= 3 and not core_files and test_files:
        level = "Low"
        reasoning = f"Only {total_files} files modified, primarily tests. Low risk changes."
    elif total_files <= 5 and not core_files:
        level = "Low"
        reasoning = f"{total_files} files modified in isolated modules. Well-contained changes."
    elif core_files and total_files > 10:
        level = "High"
        reasoning = f"{total_files} files modified including {len(core_files)} core system files. Widespread impact."
    elif core_files:
        level = "Medium"
        reasoning = f"{total_files} files modified including {len(core_files)} core system files. Focused core changes."
    elif total_files > 8:
        level = "Medium"
        reasoning = f"{total_files} files modified across multiple modules. Moderate scope."
    else:
        level = "Medium"
        reasoning = f"{total_files} files modified. Standard feature development."

    return level, reasoning

def generate_purpose(commit_messages, changed_files):
    """Generate Purpose section from commits and diffs."""
    # Collect meaningful commit messages (first few, not co-authored lines)
    commits = []
    for line in commit_messages.split('\n'):
        if line.strip() and not line.startswith('Co-Authored'):
            commits.append(line.strip())

    file_count = len(changed_files)

    # Build a more robust purpose section
    if commits:
        # Use the most recent (first) commit as primary purpose
        primary_purpose = commits[0]

        # Add context from other commits if available
        additional_context = ""
        if len(commits) > 1:
            other_commits = commits[1:3]  # Include up to 2 more commits
            if other_commits:
                additional_context = "\n\nAdditional changes:\n"
                for commit in other_commits:
                    additional_context += f"- {commit}\n"

        purpose = f"This PR {primary_purpose.lower()}{additional_context}\n\nModifies {file_count} files to enhance code modularity, maintainability, and architecture."
    else:
        purpose = f"This PR modifies {file_count} files to improve platform architecture and functionality."

    return purpose

def generate_release_notes(commits):
    """Generate Release Notes from commit messages."""
    notes = []
    for commit in commits:
        # Clean up commit message
        msg = commit.strip()
        if msg and not msg.startswith('Merge'):
            # Convert to user-friendly format
            if msg.endswith('.'):
                msg = msg[:-1]
            notes.append(f"- {msg.capitalize()}")

    if not notes:
        return "[Add release notes for end users]"

    return '\n'.join(notes)

def generate_pr_description(base_branch, target_branch, cwd=None):
    """Generate complete PR description."""
    try:
        # Validate branches exist
        branches = run_git_command("git branch -a", cwd)

        # Get analysis data
        commits = get_commits_list(base_branch, target_branch, cwd)
        commit_messages = get_commit_messages(base_branch, target_branch, cwd)
        changed_files = get_changed_files(base_branch, target_branch, cwd)
        diff_stats = get_diff_stats(base_branch, target_branch, cwd)

        if not commits:
            print("Error: No commits found between branches. Ensure you're on the correct branch.", file=sys.stderr)
            sys.exit(1)

        # Generate sections
        purpose = generate_purpose(commit_messages, changed_files)
        release_notes = generate_release_notes(commits)
        risk_level, risk_reasoning = analyze_risk_level(changed_files)

        # Build PR description
        description = f"""## Purpose of this PR

{purpose}

## Release Notes

{release_notes}

## Functional Testing Status

[Add your testing status here - describe what was tested and results]

## Performance Testing Status

[Add your testing status here - describe any performance implications and testing done]

## Overall Product Risk

**Suggested: {risk_level}**

Reasoning: {risk_reasoning}

## Comments to Reviewers

[Add comments to help reviewers understand the changes and what to focus on]

---

### Summary of Changes
{diff_stats}
"""

        return description

    except Exception as e:
        print(f"Error generating PR description: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate PR descriptions from git commits and diffs"
    )
    parser.add_argument(
        "--base",
        default="trunk",
        help="Base branch to compare against (default: trunk)"
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Target branch (default: current branch)"
    )
    parser.add_argument(
        "--cwd",
        default=None,
        help="Working directory (default: current directory)"
    )

    args = parser.parse_args()

    # Get current branch if target not specified
    if args.target is None:
        try:
            args.target = run_git_command("git rev-parse --abbrev-ref HEAD", args.cwd)
        except:
            print("Error: Could not determine current branch. Please specify --target", file=sys.stderr)
            sys.exit(1)

    # Generate and output description
    description = generate_pr_description(args.base, args.target, args.cwd)
    print(description)

if __name__ == "__main__":
    main()
