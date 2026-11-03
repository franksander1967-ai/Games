# Game Center: rules for Claude Code and the agent team

## Project
Static GitHub Pages site (https://franksander1967-ai.github.io/Games/). Single-file HTML games plus `index.html` (Game Center).
`scripts/build_catalog.py` generates the cards between `<!-- GAMES:START/END -->`. A push to `main` deploys live immediately.
No bundler, no npm runtime dependencies. Python stdlib only. Playwright is used for tests only.

## Checks (all three must pass before any PR)
```
python3 -m py_compile scripts/*.py
python3 scripts/build_catalog.py --check
node tests/smoke.mjs          # report: test-results/report.json, screenshots: test-results/*.png
```

## Team (the main session is the Lead Orchestrator)
| Agent | File | Role | Writes code? |
|---|---|---|---|
| Lead Orchestrator | this session | plans, delegates, opens PRs, escalates | no (only `docs/agents/LEARNINGS.md`) |
| platform-builder | `.claude/agents/platform-builder.md` | implements one TASK_BRIEF in its own worktree | yes, on its branch only |
| auditor | `.claude/agents/auditor.md` | adversarial review of the diff | no |
| gatekeeper | `.claude/agents/gatekeeper.md` | re-runs all checks, PASS/FAIL | no |

## Orchestrator loop (for each task)
1. **Intake:** read the issue or request and write a TASK_BRIEF (schema below). If acceptance criteria are unclear, ask the human ONE question and do not guess.
2. **Baseline:** on `main`, run `node tests/smoke.mjs` and note the report path as `baseline_report`.
3. **Build:** start `platform-builder` with the brief (Agent tool, `isolation: "worktree"`). Branch: `agent/<task-id>-<slug>`. Independent tasks may run in parallel, each in its own worktree. Never give two agents the same file.
4. **Review:** start `auditor` with the brief and the branch. If the verdict is `request_changes`, send the findings back to the builder (via SendMessage to the same builder, so it keeps its context).
5. **Gate:** start `gatekeeper` with the branch and `baseline_report`. A FAIL goes back to the builder.
6. **Loop limit:** at most 2 review/gate rounds per task. After that: stop, collect all reports, and escalate to the human with a short summary (what works, what doesn't, the suggested decision).
7. **PR:** only after auditor `approve` and gate `PASS`. Push the branch (`git push -u origin <branch>`), open a PR against `main`, and use the PR body template from `docs/AGENT_TEAM.md`. Attach the REVIEW_REPORT and GATE_REPORT as summaries.
8. **Merge:** ONLY the human merges. The orchestrator never merges, never enables auto-merge, and never pushes to `main`.
9. **Learn:** after the merge or rejection, add 1–3 lines to `docs/agents/LEARNINGS.md` (date, task, lesson). Read this file at the start of every session.

### TASK_BRIEF schema
```json
{"type":"TASK_BRIEF","task_id":"T-001","title":"","branch":"agent/T-001-slug",
 "goal":"1–2 sentences","acceptance_criteria":["testable, observable"],
 "allowed_paths":["index.html","scripts/","tests/"],"forbidden_paths":["*.html games",".github/"],
 "human_approved_paths":[],"cdn_allowed":false,"notes":""}
```

## Hard rules (hooks enforce part of these, and they apply in any case)
- Never push to `main`, never force-push, never `rm -rf`, never `git reset --hard`/`rebase`/`clean -f` without explicit confirmation from the human in this chat.
- `.github/workflows/*`, `.claude/settings.json` and `.claude/hooks/*` belong to the human. Changes to them only as a PR proposal with a note "needs human approval".
- Existing games are not touched during platform tasks. A new game counts as a new file and is allowed when the brief requires it.
- No new external dependency (CDN, API, tracking) without human approval. No API keys in the repo.
- Never print, log or commit secrets or environment variables.
- A test that fails is never skipped, deleted or weakened in order to pass. Fix the cause or escalate.
