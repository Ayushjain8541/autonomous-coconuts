# Checks and evidence

From repository root:

- `python3 -m unittest discover -s tests -v`: real ephemeral HTTP fixture, asset allowlist, threshold/missing/invalid rules and unavailable prediction adapter.
- `python3 scripts/check.py`: same suite, fixture JSON parsing and JS syntax when Node is installed.
- `node --check web/app.js`: browser JS syntax, requires Node.
- `./.beryl/agent/scripts/agent-doctor.sh`: lock-aware Beryl readiness.
- `./.beryl/scripts/check.sh`: standard deterministic gate including real configured project checks.

Browser check: start `python3 backend/server.py --port 8000`, load the page and click Load Demo; confirm synthetic response labeling and three returned encounters. Use an available browser tool; API tests alone are not browser evidence. Recheck failure feedback when changing the interaction. No formatter, package typecheck, ML evaluation or hosted deployment check exists yet; do not claim those ran.

Owners choose working/test methods consistent with the user's freedom instruction. Never weaken checks to pass. Intentional test edits regenerate `tests/.manifest.sha256` with `./.beryl/scripts/update-test-manifest.sh` and commit both. When replacing a runtime, update its real commands, Beryl test adapter and CI together. Hooks are installed but not enabled automatically. Tests may run in CI/manual checks without changing local hook settings.
