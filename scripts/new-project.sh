#!/usr/bin/env bash
# Create a new project in the langchain uv workspace.
#   ./scripts/new-project.sh <name> [extra-deps...]
#   ./scripts/new-project.sh rag-demo langchain-chroma --env
# --env also writes .env / .env.example and adds python-dotenv.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# A stale VIRTUAL_ENV from a deleted venv silently redirects uv and activation.
unset VIRTUAL_ENV _OLD_VIRTUAL_PATH

die() { printf '\033[31merror:\033[0m %s\n' "$1" >&2; exit 1; }
step() { printf '\033[36m==>\033[0m %s\n' "$1"; }

[ $# -ge 1 ] || die "usage: $0 <name> [extra-deps...] [--env]"

NAME=""
WANT_ENV=0
DEPS=()
for arg in "$@"; do
  case "$arg" in
    --env) WANT_ENV=1 ;;
    -*)    die "unknown flag: $arg" ;;
    *)     if [ -z "$NAME" ]; then NAME="$arg"; else DEPS+=("$arg"); fi ;;
  esac
done

[ -n "$NAME" ] || die "project name required"
[[ "$NAME" =~ ^[a-z0-9][a-z0-9-]*$ ]] || die "name must be lowercase letters, digits and hyphens: '$NAME'"
[ ! -e "$ROOT/$NAME" ] || die "$NAME already exists"
command -v uv >/dev/null || die "uv not found on PATH"
[ -x "$ROOT/.venv/bin/python" ] || die "workspace venv missing — run 'uv sync --all-packages' in $ROOT first"

cd "$ROOT"

step "scaffolding $NAME"
# --vcs none: a nested .git inside the existing repo would shadow it.
uv init --vcs none "$NAME" >/dev/null

step "adding dependencies"
( cd "$NAME" && uv add langchain "${DEPS[@]+"${DEPS[@]}"}" $( [ "$WANT_ENV" = 1 ] && echo python-dotenv ) >/dev/null )

if [ "$WANT_ENV" = 1 ]; then
  step "writing .env.example"
  printf '# Fill in and copy to .env\nGOOGLE_API_KEY=\n' > "$NAME/.env.example"
  cp "$NAME/.env.example" "$NAME/.env"
fi

step "registering $NAME with pyright"
"$ROOT/.venv/bin/python" - "$NAME" <<'PY'
import json, pathlib, sys
name = sys.argv[1]
cfg = pathlib.Path("pyrightconfig.json")
data = json.loads(cfg.read_text()) if cfg.exists() else {}
inc = data.setdefault("include", [])
if name not in inc:
    inc.append(name)
    inc.sort()
cfg.write_text(json.dumps(data, indent=2) + "\n")
PY

step "syncing workspace venv"
uv sync --all-packages >/dev/null

cat <<EOF

$(printf '\033[32mdone\033[0m') — $NAME is ready.

  cd $NAME
  uv run main.py

Reload your editor window so pyright picks up the new project.
EOF
