# Project instructions

- The brief is in `README.md` and the data dictionary in `data/README.md`.
- Stack: Python 3.12, FastAPI, SQLite, pytest.
- Structure: `app/` contains the API and UI, `data/` contains the synthetic source files, `tests/` holds the workflow and endpoint checks, and the generated SQLite file lives at the repo root.
- API conventions: endpoints are REST-style under `/api`, request and action payloads use JSON, success responses return `{ "success": true, "permit": {...} }`, and refusal responses return HTTP 400 with `{ "ok": false, "error": { "code": "CHECK_ID", "message": "..." } }`.
- Code conventions: use snake_case for Python functions and variables, keep the workflow checks in a single service layer, and make every rule return a check ID and a human-readable explanation.
- Tests: run `python -m pytest -q` from the repo root.
