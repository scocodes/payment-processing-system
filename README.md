# ePay

This project is being developed as part of a software engineering mentorship
with ePay Worldwide.

ePay is a FastAPI transaction-processing project with SQLite-backed accounts,
deposits, withdrawals, transfers, and transaction history. It also supports user
registration and JWT login. This is a learning project, not a production payment
service: account and transaction routes do not yet enforce authentication or
account ownership.

## Learning workflow

Whenever a new function or feature is added, use this validation process before
considering it complete:

1. Before implementation, describe the intended request or data flow.
2. Identify the expected successful behaviour and relevant boundary or failure
   cases.
3. Propose tests for those behaviours before generating the implementation.
4. Review the completed code and explain the purpose of each new part.
5. Predict the test results, then run both the focused tests and the full suite.
6. Explain the implementation back in plain language and answer a short quiz or
   make a small related change to demonstrate understanding.

The goal is not to memorise library syntax. It is to be able to specify the
behaviour, understand the design choices, identify risks, and verify that the
generated implementation is correct.

## Requirements

- Python 3.11 or newer

## Setup

Create and activate a virtual environment, then install ePay and its development
dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

Set a signing secret before using login, then start the API:

```bash
export SECRET_KEY="$(openssl rand -hex 32)"
uvicorn app.main:app --reload
```

The API documentation is available at `http://127.0.0.1:8000/docs`. SQLite data
is stored in `accounts.db` by default; set `DATABASE_PATH` to use another file.

## Tests

Run the test suite with:

```bash
pytest
```
