#!/bin/sh
# Local launcher: use existing tools without installing anything globally.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
BUNDLED_RUNTIME="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies"
if ! command -v node >/dev/null 2>&1; then
  if [ -x "$BUNDLED_RUNTIME/node/bin/node" ]; then
    PATH="$BUNDLED_RUNTIME/node/bin:$PATH"
    export PATH
  else
    printf '%s\n' 'Node.js was not found. Install Node.js 20.19+ or 22.12+ and pnpm, then run this launcher again.' >&2
    exit 1
  fi
fi
if command -v pnpm >/dev/null 2>&1; then
  PACKAGE_RUNNER="$(command -v pnpm)"
elif [ -x "$BUNDLED_RUNTIME/bin/fallback/pnpm" ]; then
  PACKAGE_RUNNER="$BUNDLED_RUNTIME/bin/fallback/pnpm"
else
  printf '%s\n' 'pnpm was not found. Install pnpm, then run this launcher again.' >&2
  exit 1
fi
if [ ! -d node_modules ]; then
  "$PACKAGE_RUNNER" install
fi
COCONUTS_PACKAGE_RUNNER="$PACKAGE_RUNNER"
export COCONUTS_PACKAGE_RUNNER
exec "$PACKAGE_RUNNER" run dev:all
