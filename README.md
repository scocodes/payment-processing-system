# Payment Processing System

This educational project is being developed under the mentorship of a software
engineer at ePay Worldwide, who assigns engineering tasks to help me learn
software engineering through practical implementation and review. It is an
independent learning project and is not an ePay Worldwide product.

The current implementation is a Python and FastAPI REST API for processing basic
account transactions. It uses SQLite for persistent storage and supports account
creation and retrieval, deposits, withdrawals with insufficient-funds checks,
atomic transfers, and transaction history. Transfers create linked transaction
records with a shared reference ID.

The project also supports user registration, password hashing, login with
time-limited JWT Bearer tokens, token validation, and retrieval of the currently
authenticated user. Automated API tests run against isolated temporary SQLite
databases and cover successful operations, validation errors, authentication
failures, and transaction boundary cases.

This is a learning project rather than a production payment service. Account
routes require authentication and enforce ownership: users can access and
modify their own accounts, and transfers can credit another user's account
only when the sender account belongs to the authenticated user.

## Requirements

- Python 3.11 or newer

## Setup

Create and activate a virtual environment, then install the project and its
development dependencies:

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
