#!/usr/bin/env bash
# PreToolUse hook (Bash): blocks destructive or gate-bypassing commands.
# Exit 2 = block; stderr is shown to the agent so it can adjust.
set -euo pipefail
cmd=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))')

block() { echo "BLOCKED by guard-bash: $1. Ask the human for explicit confirmation instead." >&2; exit 2; }

# Destructive filesystem / history operations
grep -Eq '(^|[;&|[:space:]])rm[[:space:]]+(-[a-zA-Z]*[rR][a-zA-Z]*[fF]|-[a-zA-Z]*[fF][a-zA-Z]*[rR]|--recursive|-r)' <<<"$cmd" && block "recursive delete"
grep -Eq 'git[[:space:]]+push.*(--force|-f([[:space:]]|$)|--force-with-lease|\+[A-Za-z])' <<<"$cmd" && block "force push"
grep -Eq 'git[[:space:]]+push[^;&|]*[[:space:]:](main|master)([[:space:]]|$)' <<<"$cmd" && block "direct push to main (open a PR instead)"
grep -Eq 'git[[:space:]]+(reset[[:space:]]+--hard|clean[[:space:]]+-[a-zA-Z]*f|checkout[[:space:]]+--[[:space:]]+\.|branch[[:space:]]+-D|worktree[[:space:]]+remove[[:space:]]+--force|filter-branch|rebase)' <<<"$cmd" && block "history/worktree-destroying git command"
grep -Eq 'git[[:space:]]+(commit|push|merge)[^;&|]*--no-verify' <<<"$cmd" && block "skipping verification hooks"
grep -Eiq '(drop[[:space:]]+(table|database)|truncate[[:space:]]+table)' <<<"$cmd" && block "destructive SQL"
grep -Eq '(gh|hub)[[:space:]]+pr[[:space:]]+merge' <<<"$cmd" && block "merging PRs is reserved for the human"

# Secret leakage: printing the environment or known secret files
grep -Eq '(^|[;&|[:space:]])(env|printenv|set)([[:space:]]*($|[;&|>]))' <<<"$cmd" && block "dumping environment variables"
grep -Eq '(cat|less|head|tail|echo)[^;&|]*(\.env|id_rsa|\.npmrc|\$[A-Z_]*(TOKEN|KEY|SECRET))' <<<"$cmd" && block "reading/printing secrets"
exit 0
