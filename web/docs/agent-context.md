# P1: web context

Own this browser area, its dependency/configuration choices and UI checks. Read root AGENTS.md, the product brief, your P1 ticket and shared contracts. Other roles own the backend/model; coordinate shared changes with them. Your tools, framework and visual design are your choice.

## Current local map and interface

`index.html`, `app.js`, `styles.css` are a deliberately small replaceable connectivity shell. Load Demo requests `GET /api/demo` and displays labeled synthetic analysis; it is not the finished console. The backend serves these allowlisted assets on the same origin. P2 owns transport, P3 owns risk rules, and contracts/fixtures contains shared examples.

## Actual commands (from repo root)

- Run: `python3 backend/server.py --port 8000`; open `http://127.0.0.1:8000`.
- JS syntax: `node --check web/app.js` (Node optional for the Python server).
- Behavior/HTTP/rules: `python3 -m unittest discover -s tests -v`.
- Shared gate: `./.beryl/scripts/check.sh`.

Replace this shell with your preferred implementation while keeping the contract and honest fixture/status labels. If introducing a separate dev server, agree API proxy/origin behavior with P2 and update setup/check/CI instructions. Verify actual browser interaction and relevant keyboard/narrow-screen behavior; a Python HTTP test is not UI proof. Record your handoff at .beryl/agent/hackathon/handoffs/P1.md.
