#!/bin/bash
# --reset clears tutorial files in place without stopping Jupyter.
set -euo pipefail
DEMO_ROOT="$HOME/forth-demo"
JUPYTER=/tmp/crete-lightcone-venv/bin/jupyter
export PATH="/tmp/crete-lightcone-adapters/node_modules/.bin:$PATH"
if [[ ! -x "$JUPYTER" ]]; then
  echo "Missing demo runtime: $JUPYTER" >&2
  exit 1
fi
if [[ "${1:-}" != "" && "${1:-}" != "--reset" ]]; then
  echo "Usage: $0 [--reset]" >&2
  exit 1
fi
if [[ "${1:-}" == "--reset" ]]; then
  if [[ -L "$DEMO_ROOT" ]]; then
    echo "Refusing to reset a symlink: $DEMO_ROOT" >&2
    exit 1
  fi
  mkdir -p "$DEMO_ROOT"
  # Keep the root directory itself: running terminals may have it as their cwd.
  # Include dotfiles and read-only git-annex directories, but never follow symlinks.
  python3 - "$DEMO_ROOT" <<'PYRESET'
import os
from pathlib import Path
import shutil
import stat
import sys

root = Path(sys.argv[1])
for entry in root.iterdir():
    if entry.is_symlink() or not entry.is_dir():
        entry.unlink()
        continue
    for parent, dirs, files in os.walk(entry, followlinks=False):
        path = Path(parent)
        path.chmod(path.stat().st_mode | stat.S_IWUSR | stat.S_IXUSR)
    shutil.rmtree(entry)
print("Tutorial files cleared. Jupyter is still running. Start a new agent chat.")
PYRESET
  exit 0
fi
if lsof -tiTCP:8889 -sTCP:LISTEN >/dev/null; then
  "$JUPYTER" server stop 8889
fi
mkdir -p "$DEMO_ROOT"
cd "$DEMO_ROOT"
exec "$JUPYTER" lab --no-browser --ServerApp.ip=127.0.0.1 \
  --ServerApp.port=8889 --ServerApp.port_retries=0 \
  --ServerApp.root_dir="$DEMO_ROOT"
