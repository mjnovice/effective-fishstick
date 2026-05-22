# Aurelian Conversation Category Workspace

## Start Here

```bash
python3 run.py
```

Open `http://localhost:8000`.

If port `8000` is busy:

```bash
AURELIAN_PORT=8010 python3 run.py
```

## Where Things Live

- `workspace/` — the code you'll edit or read (`app.py`, `database.py`,
  `category_catalog.py`, `seed.py`, plus frontend in `workspace/static/`).
- `framework/` — HTTP plumbing and the static HTML shell. Do not edit.

## Only If Needed

- If startup is flaky, tell the interviewer and keep moving.
- Reset the local database with `python3 framework/reset_db.py`.
- Category IDs and field metadata live in
  [workspace/category_catalog.py](workspace/category_catalog.py).
