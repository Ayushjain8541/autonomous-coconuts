# Checks and evidence

From repository root:

- `python3 -m unittest discover -s tests -v`: real ephemeral HTTP fixture, asset allowlist, threshold/missing/invalid rules and unavailable prediction adapter.
- `python3 scripts/check.py`: same suite, fixture JSON parsing and JS syntax when Node is installed.
- `node --check web/app.js`: browser JS syntax, requires Node.
- `./.beryl/agent/scripts/agent-doctor.sh`: lock-aware Beryl readiness.
- `./.beryl/scripts/check.sh`: standard deterministic gate including real configured project checks.
- `development/.venv/bin/python -m pytest -q development/tests`: ML/upload behavior,
  export compatibility, and benchmark arithmetic/alignment checks.
- `.venv/bin/python development/benchmark_predictions.py`: evaluation of frozen
  CSV predictions against local same-row reference risk, with distance-only and
  probability-only diagnostics; requires the local labelled CSVs.

Browser check: start `python3 backend/server.py --port 8000`, load the page and click Load Demo; confirm synthetic response labeling and three returned encounters. Use an available browser tool; API tests alone are not browser evidence. Recheck failure feedback when changing the interaction. The current frontend is checked with pnpm test and pnpm build (including TypeScript checking). CI installs the combined model/PDF dependencies and runs P3 tests too. No hosted deployment check is claimed. The CSV benchmark is a retrospective same-row label comparison, not validation of final-report forecasting or real collision outcomes.

Owners choose working/test methods consistent with the user's freedom instruction. Never weaken checks to pass. Intentional test edits regenerate `tests/.manifest.sha256` with `./.beryl/scripts/update-test-manifest.sh` and commit both. When replacing a runtime, update its real commands, Beryl test adapter and CI together. Hooks are installed but not enabled automatically. Tests may run in CI/manual checks without changing local hook settings.

The pinned Markdown source gate traverses ignored dependencies. Run the full Beryl gate from a clean source checkout before pnpm/pip installation (as CI does); use a clean worktree for that gate when the development checkout already has node_modules. Run native backend, ML and frontend checks in the fully installed environment as well. Do not edit vendor Markdown or weaken the managed check.
