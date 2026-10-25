# langchain

A [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) of small LangChain
projects. One shared virtualenv at the root, one lockfile, one project per folder.

```
langchain/
├── .venv/                   # shared virtualenv — do NOT create per-project venvs
├── pyproject.toml           # workspace root: members + dev tools
├── uv.lock                  # single lockfile for every member
├── pyrightconfig.json       # type checking, resolves against the shared .venv
├── scripts/new-project.sh   # scaffolds a new member
├── hello-world/             # Gemini via langchain-google-genai
├── hello-world-with-ollma/  # local model via langchain-ollama
└── langsmith-tracing/       # LangSmith tracing example
```

## Requirements

- [uv](https://docs.astral.sh/uv/) (`brew install uv`)
- Python 3.13 (uv installs it if missing)
- [Ollama](https://ollama.com) for the local-model projects: `ollama serve`, then
  `ollama pull llama3.1:8b`

## Running a project

```bash
cd hello-world-with-ollma
uv run main.py
```

`uv run` resolves the shared workspace venv on its own, so there is nothing to activate.
If you prefer an activated shell:

```bash
source .venv/bin/activate   # from the repo root, not from a project folder
```

## Adding a new project

Use the script — it handles workspace registration, dependencies, and type-checker config
in one step:

```bash
cd ~/Desktop/langchain
./scripts/new-project.sh <name> [extra-deps...] [--env]
```

Examples:

```bash
./scripts/new-project.sh rag-demo                                  # langchain only
./scripts/new-project.sh chat-ollama langchain-ollama               # plus extra deps
./scripts/new-project.sh gemini-demo langchain-google-genai --env   # plus .env + python-dotenv
```

Names must be lowercase letters, digits and hyphens. The script then:

1. scaffolds the folder with `uv init --vcs none` (no nested git repo),
2. installs `langchain` plus any deps you listed into the shared `.venv`,
3. writes `.env` and `.env.example` and adds `python-dotenv` when given `--env`,
4. appends the project to `include` in `pyrightconfig.json`,
5. runs `uv sync --all-packages`.

Then:

```bash
cd <name>
uv run main.py
```

Reload your editor window afterwards so the type checker picks up the new folder.

### Doing it by hand

```bash
cd ~/Desktop/langchain
uv init --vcs none <name>        # auto-appends to [tool.uv.workspace] members
cd <name> && uv add langchain
```

Then add `<name>` to `include` in `pyrightconfig.json` yourself.

### Adding dependencies later

```bash
cd <name> && uv add <package>        # records in that project, installs into shared .venv
uv add --dev ruff                    # shared dev tooling, from the root
```

## Two things to avoid

- **Do not run `uv venv` or `python -m venv` inside a project.** The root `.venv` covers every
  member. Per-project venvs were removed because `activate` bakes in an absolute path at
  creation time, so a copied or moved folder silently falls back to the system Python.
- **Do not copy an existing project folder to start a new one.** That is how duplicate project
  names and stale venv paths appear. Use `uv init` or the script.

## Secrets

Each project keeps its own `.env`, ignored by git; `.env.example` is the tracked template.
Fill in real values locally:

```bash
cp .env.example .env
```

Note that `langsmith` compares `LANGSMITH_TRACING` to the exact string `true`, so
`LANGSMITH_TRACING=True` silently disables tracing.
