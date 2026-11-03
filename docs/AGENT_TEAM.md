# Game Center agent team: blueprint

Status: setup v1 (2026-11-03) · Owner: franksander1967-ai · Merge authority: **human only**

## 1. Use case decision

| Option | ROI here | Risk | Review effort | Verdict |
|---|---|---|---|---|
| Full-stack feature delivery (platform) | high | medium | medium | **Start here** |
| Automated regression bug fixing | medium (there are hardly any tests yet) | low | low | phase 2 |
| Legacy refactoring of games | low (the games are finished content) | high | high | no |
| Security audit (ultrareview) | medium (small attack surface) | low | low | built in through the auditor |
| API integration pipelines | low (static site) | high (cost, secrets) | high | no |

**Recommendation:** platform features, and the first task is **real preview images for every game card**.
Reason: the smoke test produces a screenshot of every game anyway. One investment covers two of your bottlenecks:
*review time* (each PR comes with screenshots + PASS/FAIL, so you don't have to click through yourself) and
*idea → finished game* (a new game gets a card with a preview image automatically).

## 2. Team topology

```
                         ┌──────────────────────────────┐
   You (human) ────────▶│  LEAD ORCHESTRATOR            │◀── docs/agents/LEARNINGS.md
   Issue / request       │  main session · CLAUDE.md     │     (shared memory)
                         │  plans, delegates, escalates  │
                         └──┬──────────┬──────────┬─────┘
             TASK_BRIEF     │          │          │
          ┌─────────────────▼──┐   ┌───▼──────┐ ┌─▼─────────────┐
          │ PLATFORM-BUILDER   │   │ AUDITOR  │ │ GATEKEEPER    │
          │ worktree per task  │   │ read-only│ │ read-only     │
          │ agent/T-xxx-slug   │   │ adversar.│ │ runs checks   │
          └─────────┬──────────┘   └───▲──────┘ └──▲────────────┘
            CHANGE_REPORT              │ REVIEW_    │ GATE_REPORT
                    └──────────────────┘ REPORT ────┘
                                       │
                         max 2 rounds ─┤─ otherwise escalate to you
                                       ▼
                     PR ──▶ CI "PR checks" (smoke + catalog) ──▶ YOU merge ──▶ Pages deploy
```

Cross-agent communication: subagents never talk to each other directly. All handoffs go through the orchestrator as
JSON reports (schemas in the agent files). Feedback goes back to the *same* builder via SendMessage,
so its context is preserved. For parallel work across multiple cloud sessions: `create_session` + `send_message`,
one session per independent task (Day 5).

## 3. Workflow: issue to merge

1. **Intake:** a GitHub issue or chat request. The orchestrator writes a TASK_BRIEF with testable acceptance criteria.
2. **Baseline:** smoke run on `main` → `baseline_report` (known failures do not count as regressions).
3. **Build:** builder in its own git worktree (`isolation: worktree`) on `agent/T-xxx-slug`.
4. **Ultrareview:** the auditor checks the diff against 8 points (correctness, catalog contract, regression, XSS/CDN, deploy, performance, hallucination, scope).
5. **Gate:** the gatekeeper re-runs every check itself. PASS/FAIL, with no judgment calls.
6. **PR:** the orchestrator pushes the branch and opens a PR (template below). CI runs again on GitHub.
7. **Human gate:** you look at the screenshots in the CI artifact and the summary, then merge or comment.
8. **Deploy:** the existing `game-center.yml` publishes. The orchestrator writes a learning.

## 4. Tool stack and permissions

| Tool | Purpose | Who | Limit |
|---|---|---|---|
| Bash | checks, git, Playwright | all | guard-bash hook: no rm -rf, force push, push to main, reset/rebase, env dump, PR merge |
| Read/Grep/Glob | understand code | all | `.env*` denied |
| Edit/Write | code changes | builder only (+ orchestrator for LEARNINGS) | guard-paths hook: no workflows, hooks, settings, or existing games |
| Git worktrees | isolation | builder | one branch per task, never the same file in two tasks |
| GitHub MCP | issues, PRs, CI status | orchestrator | create PRs yes, merge **no** |
| Playwright (Chromium) | smoke, screenshots | builder, auditor, gatekeeper | test-only, not a runtime dependency |
| Memory | `CLAUDE.md` (rules), `docs/agents/LEARNINGS.md` (lessons) | orchestrator writes, all read | no secrets |
| Routines (cron) | weekly smoke against main + issue on regressions | orchestrator | Day 5, only after the pipeline is stable |

## 5. Branching and worktrees

```
main  ────────●──────────────●──────────────●───▶  (protected: PR + human merge)
               \            /  \            /
 agent/T-001-thumbnails ●──●    agent/T-002-tags ●──●
   (worktree .claude/worktrees/…)   (separate worktree, runs in parallel)
```
- Branch name: `agent/<task-id>-<slug>`. Commits follow Conventional Commits.
- Every PR must include the regenerated `index.html`. CI checks `--check`, so the bot commit in the deploy workflow becomes a no-op.
- **GitHub setting (human, Day 1):** Settings → Rules → Ruleset for `main`: require pull request, require status check "PR checks",
  bypass for *Repository admin* (so you can keep uploading games directly via the web).
  ⚠ The deploy workflow pushes the catalog as `github-actions[bot]` to `main`. With the ruleset, that push fails
  if a direct upload changed the catalog. Solution: switch the workflow to "generate the catalog only in `_site`, don't commit" (separate PR, your decision).

## 6. QA protocol

**Pre-flight (builder, before every report):** py_compile · catalog `--check` · full smoke run · `git status` clean.

**Auditor checklist:** see `.claude/agents/auditor.md` (8 points, findings only with file:line + evidence).

**Gate criteria (binary):**
- [ ] clean worktree, no protected paths in the diff
- [ ] py_compile + catalog check green
- [ ] smoke: no game PASS→FAIL compared to the baseline, index test green
- [ ] index.html ≤ 1 MB, preview images ≤ 60 KB each

**Automatic fallbacks:**
| Situation | Reaction |
|---|---|
| Same check fails 3× in a row in the builder | builder stops with `status: blocked` |
| 2 review/gate rounds without approve+PASS | orchestrator escalates to you with all reports and a suggested decision |
| Check can't run (network, tool missing) | gate = FAIL `infrastructure`, never PASS |
| Hook blocks a command | agent asks you; workarounds are forbidden |
| Smoke flake (timeout) | retry once at most, report both runs |

## 7. PR template (orchestrator)
```
## What & why
<2–4 sentences, link to issue>
## Acceptance criteria
- [x] …
## Verification
Auditor: approve (0 blocker, n minor) · Gate: PASS @ <sha> · Smoke: N/M (preexisting: …)
Screenshots: CI artifact "smoke-results"
## Risks / for the human to check
- …
```

## 8. 5-day rollout

| Day | Goal | Done when |
|---|---|---|
| **1** Foundation | merge this setup PR; set up the ruleset for `main`; check the proposals in `docs/agents/*.proposed` and adopt them yourself | hooks active, `node tests/smoke.mjs` runs locally |
| **2** CI | enable `pr-checks.yml` (proposal → `.github/workflows/`), deploy rsync excludes | a test PR shows green CI + screenshot artifact |
| **3** First real task | T-001 "preview images": the generator embeds screenshots as WebP/PNG thumbnails in the cards, falling back to the current letter tile | full loop issue → PR with no manual intervention by you before review |
| **4** Second task + tuning | T-002, e.g. genre tags/filters or "new" badge; adjust prompts using LEARNINGS | ≤ 1 escalation per task |
| **5** Scale | weekly routine: smoke on `main`, issue on regression; optionally 2 builders in parallel in separate sessions | routine runs, first parallel PRs without conflicts |

## START HERE FIRST
1. Review and merge the setup PR (agent files, hooks, smoke test, CLAUDE.md).
2. Copy `docs/agents/pr-checks.yml.proposed` yourself to `.github/workflows/pr-checks.yml` and apply the rsync patch.
3. Set up the ruleset for `main` (section 5).
4. In a new Claude Code session: *"Orchestrator: create T-001 preview images according to docs/AGENT_TEAM.md"*.
