# Repository Guidelines

## Project Structure & Module Organization
- `src/tau2/` holds the benchmark runtime (domains, orchestrator, CLI). Group new modules by domain and update `registry.py` when registering tools or policies.
- `src/experiments/` documents reproducible study setups; put notebooks and configs here.
- `tests/` mirrors package folders; create new suites alongside the code they cover.
- Generated outputs land in `data/tau2/…`; keep large artifacts out of git and prefer gitignore updates.
- CLI helpers and one-off utilities live in `scripts/`; reuse them before adding new entrypoints to `Makefile`.

## Build, Test, and Development Commands
- `pip install -e .` installs the package and exposes the `tau2` CLI.
- `make test` runs the full pytest suite under `tests/`.
- `make lint` and `make format` run Ruff in check and format modes.
- `make env-cli` launches `python -m tau2.environment.utils.interface_agent` for manual environment probing.
- `tau2 check-data` validates that `TAU2_DATA_DIR` points to a populated data directory before simulations.

## Coding Style & Naming Conventions
- Python code follows Ruff and Black defaults (88-char lines, double quotes where Black applies).
- Import only what you use; unused imports fail `ruff check`.
- Use snake_case for modules, functions, and variables; PascalCase for classes; keep public CLI commands in `cli.py`.
- Prefer type hints on public APIs and add docstrings describing agent behavior or side effects.

## Testing Guidelines
- Write pytest tests that mirror runtime modules (`tests/test_run.py`, `tests/test_orchestrator.py`, etc.) and name new files `test_<feature>.py`.
- Leverage shared fixtures in `tests/conftest.py` for domain setup.
- Cover success and failure trajectories; add regression tests for reported bugs.
- Run `pytest path/to/test_file.py -k case` locally to iterate quickly; ensure `make test` passes before submitting.

## Commit & Pull Request Guidelines
- Follow existing Conventional-Commits-style prefixes (`feature:`, `fix:`, `chore:`, `submission:`) with concise summaries.
- Squash or rebase before opening a PR and reference related issues or leaderboard submissions.
- PRs should include: goal-oriented description, testing notes (`make test`, lint results), and links to relevant simulation logs or figures when UI changes are involved.
- Attach screenshots or terminal snippets when touching `web/` assets or CLI UX.

## Security & Configuration Tips
- Store provider credentials in `.env` (based on `.env.example`) and never commit secrets.
- Set `TAU2_DATA_DIR` for non-editable installs and run `tau2 check-data` after changing datasets.
- When sharing logs, scrub user-identifying data from `data/tau2/simulations/` before publishing.
