#!/usr/bin/env bash
# Publish a fresh, extracted ReviewLens release to the intended *personal* GitHub account only.
# Intentionally refuses any non-Tangeroooo authentication, existing repo or remote, or parent git checkout.
set -euo pipefail

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "${script_dir}/.." && pwd)"
cd "$repo_dir"
# Force the public GitHub host even when enterprise GH_HOST is configured globally.
export GH_HOST=github.com

[[ -f skills/reviewlens/SKILL.md && -f .claude-plugin/plugin.json && -f README.md ]] || fail 'Not a ReviewLens distribution root.'
command -v gh >/dev/null 2>&1 || fail 'GitHub CLI (gh) is required. Install it and authenticate as Tangeroooo.'
command -v git >/dev/null 2>&1 || fail 'git is required.'

login="$(gh api --hostname github.com user --jq .login)" || fail 'No valid GitHub authentication. Run gh auth login -h github.com.'
[[ "$login" == 'Tangeroooo' ]] || fail "Refusing to publish: authenticated GitHub user is '$login', not 'Tangeroooo'."
user_id="$(gh api --hostname github.com user --jq .id)" || fail 'Cannot identify authenticated user.'
[[ "$user_id" =~ ^[0-9]+$ ]] || fail 'Invalid personal GitHub user ID.'

if gh repo view Tangeroooo/reviewlens --json name >/dev/null 2>&1; then
  fail 'Tangeroooo/reviewlens already exists. Refusing to overwrite or push into an existing repo.'
fi

if git_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  [[ "$git_root" == "$repo_dir" ]] || fail "This directory is inside another Git repository ($git_root). Refusing."
else
  git init -b main >/dev/null
fi

[[ -z "$(git remote)" ]] || fail 'Refusing to publish from a checkout that already has Git remotes.'
[[ -z "$(git rev-list --all 2>/dev/null || true)" ]] || fail 'Refusing to publish from a Git repository with existing history.'

python3 -m unittest discover -s tests -v

git add -A
# Use an account-specific GitHub no-reply address ONLY for this commit (no global or corporate identity).
GIT_AUTHOR_NAME='Tangeroooo' GIT_COMMITTER_NAME='Tangeroooo' \
GIT_AUTHOR_EMAIL="${user_id}+Tangeroooo@users.noreply.github.com" \
GIT_COMMITTER_EMAIL="${user_id}+Tangeroooo@users.noreply.github.com" \
git -c user.name='Tangeroooo' -c user.email="${user_id}+Tangeroooo@users.noreply.github.com" \
  -c commit.gpgsign=false commit -m 'Initial ReviewLens skill release' >/dev/null
expected_identity="Tangeroooo <${user_id}+Tangeroooo@users.noreply.github.com>"
actual_author="$(git log -1 --format='%an <%ae>')"
actual_committer="$(git log -1 --format='%cn <%ce>')"
[[ "$actual_author" == "$expected_identity" && "$actual_committer" == "$expected_identity" ]] || \
  fail 'Commit identity mismatch. Refusing to push.' 

printf 'Confirmed GitHub identity: %s\n' "$login"
printf 'Commit author: Tangeroooo <%s+Tangeroooo@users.noreply.github.com>\n' "$user_id"
printf 'Creating https://github.com/Tangeroooo/reviewlens (public)\n'
gh repo create Tangeroooo/reviewlens --public --source=. --remote=origin --push
printf 'Published: https://github.com/Tangeroooo/reviewlens\n'
