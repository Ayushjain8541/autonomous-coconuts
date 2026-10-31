#!/usr/bin/env python3
"""Portable baseline checks. Extend with real product checks as owners implement."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for path in (ROOT / "contracts/fixtures").glob("*.json"):
    json.loads(path.read_text())
subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=True)
node = shutil.which("node")
if node:
    subprocess.run([node, "--check", "web/app.js"], cwd=ROOT, check=True)
else:
    print("Node not installed: browser JS syntax check skipped; Python fixture checks completed.")
