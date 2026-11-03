#!/usr/bin/env bash
# PreToolUse hook (Edit|Write|MultiEdit|NotebookEdit): protects files no agent may change on its own.
# Exit 2 = block. The human edits these files, or approves the change explicitly in chat.
set -euo pipefail
path=$(python3 -c 'import json,sys; d=json.load(sys.stdin).get("tool_input",{}); print(d.get("file_path") or d.get("notebook_path") or "")')
root=$(git -C "$(dirname "$path")" rev-parse --show-toplevel 2>/dev/null || pwd)
rel=${path#"$root"/}

block() { echo "BLOCKED by guard-paths: $rel — $1. Ask the human for approval." >&2; exit 2; }

case "$rel" in
  .github/workflows/*) block "CI/deploy pipeline is human-owned" ;;
  .claude/settings.json|.claude/hooks/*) block "agents may not weaken their own guardrails" ;;
  .env*|*.pem|*.key) block "secret material" ;;
esac
# Existing games are content, not platform code: only a task with GAME_EDIT_ALLOWED=1 may touch them.
if [[ "$rel" =~ \.html?$ && "$rel" != "index.html" && -f "$path" && "${GAME_EDIT_ALLOWED:-0}" != "1" ]]; then
  block "existing game file (platform tasks must not modify games)"
fi
exit 0
