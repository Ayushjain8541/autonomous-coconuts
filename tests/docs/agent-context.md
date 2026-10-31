# Shared baseline verification

`test_bootstrap.py` verifies real local HTTP routes, allowlisted assets, fixture semantics, classifier boundaries and the unavailable prediction adapter. Tests use an ephemeral local server and do not call providers or train a model. Run from root: `python3 -m unittest discover -s tests -v`.

Roles own tests for their behavior; P4 coordinates end-to-end additions. Do not weaken existing checks to pass. Intentional test changes update `tests/.manifest.sha256` using `./.beryl/scripts/update-test-manifest.sh` in the same commit. Configure actual replacement-runtime checks in .beryl/agent/affected-tests.conf when changing stacks.
