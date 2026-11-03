# Team learnings (the orchestrator appends 1–3 lines after each task)

- 2026-11-03 · Setup · 4 games (Breitseite, Mörser, Platinum Space, bouldercrash) load three.js r128 from cdnjs/jsdelivr at runtime. In sandboxes without CDN access, they FAIL as `preexisting`; this is not a regression. Long-term option: vendor three.js locally (needs human approval, since it changes game files).
- 2026-11-03 · Setup · ES modules ignore global Node modules. tests/smoke.mjs therefore loads Playwright via createRequire.
