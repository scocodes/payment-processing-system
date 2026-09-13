import os
import sqlite3
from pathlib import Path
from uuid import uuid4

DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "accounts.db"))

class AccountNotFoundError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


class SameAccountError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            balance INTEGER NOT NULL CHECK (balance >= 0),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount INTEGER NOT NULL CHECK (amount > 0),
            reference_id TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
        """
    )
    return connection


def initialize_database() -> None:
    with _connect():
        pass


def create_user(email: str, password_hash: str) -> dict:
    try:
        with _connect() as connection:
            cursor = connection.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash),
            )
            row = connection.execute(
                "SELECT id, email, created_at FROM users WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
    except sqlite3.IntegrityError as error:
        raise UserAlreadyExistsError from error
    return dict(row)


def get_user_by_email(email: str) -> dict | None:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT id, email, password_hash, created_at
            FROM users
            WHERE email = ? COLLATE NOCASE
            """,
            (email,),
        ).fetchone()
    return dict(row) if row is not None else None


def get_user(user_id: int) -> dict | None:
    with _connect() as connection:
        row = connection.execute(
            "SELECT id, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row is not None else None


def create_account(user_id: int, balance: int) -> dict:
    with _connect() as connection:
        cursor = connection.execute(
            "INSERT INTO accounts (user_id, balance) VALUES (?, ?)",
            (user_id, balance),
        )
        row = connection.execute(
            "SELECT id, user_id, balance FROM accounts WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return dict(row)


def get_account(account_id: int) -> dict | None:
    with _connect() as connection:
        row = connection.execute(
            "SELECT id, user_id, balance FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
    return dict(row) if row is not None else None


def get_accounts() -> list[dict]:
    with _connect() as connection:
        rows = connection.execute(
            "SELECT id, user_id, balance FROM accounts ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]


def get_transactions(account_id: int | None = None) -> list[dict]:
    with _connect() as connection:
        if account_id is None:
            rows = connection.execute(
                """
                SELECT id, account_id, type, amount, reference_id, created_at
                FROM transactions
                ORDER BY id
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, account_id, type, amount, reference_id, created_at
                FROM transactions
                WHERE account_id = ?
                ORDER BY id
                """,
                (account_id,),
            ).fetchall()
    return [dict(row) for row in rows]


def deposit(account_id: int, amount: int) -> dict:
    with _connect() as connection:
        cursor = connection.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (amount, account_id),
        )
        if cursor.rowcount == 0:
            raise AccountNotFoundError
        connection.execute(
            """
            INSERT INTO transactions (account_id, type, amount)
            VALUES (?, 'deposit', ?)
            """,
            (account_id, amount),
        )
        row = connection.execute(
            "SELECT id, user_id, balance FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
    return dict(row)


def withdraw(account_id: int, amount: int) -> dict:
    with _connect() as connection:
        account = connection.execute(
            "SELECT id, user_id, balance FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
        if account is None:
            raise AccountNotFoundError
        if amount > account["balance"]:
            raise InsufficientFundsError

        connection.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (amount, account_id),
        )
        connection.execute(
            """
            INSERT INTO transactions (account_id, type, amount)
            VALUES (?, 'withdrawal', ?)
            """,
            (account_id, amount),
        )
        updated_account = connection.execute(
            "SELECT id, user_id, balance FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
    return dict(updated_account)


def transfer(sender_id: int, recipient_id: int, amount: int) -> dict:
    if sender_id == recipient_id:
        raise SameAccountError

    reference_id = str(uuid4())
    connection = _connect()
    try:
        connection.execute("BEGIN IMMEDIATE")
        sender = connection.execute(
            "SELECT id, user_id, balance FROM accounts WHERE id = ?",
            (sender_id,),
        ).fetchone()
        recipient = connection.execute(
            "SELECT id, user_id, balance FROM accounts WHERE id = ?",
            (recipient_id,),
        ).fetchone()

        if sender is None or recipient is None:
            raise AccountNotFoundError
        if amount > sender["balance"]:
            raise InsufficientFundsError

        connection.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (amount, sender_id),
        )
        connection.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (amount, recipient_id),
        )
        connection.execute(
            """
            INSERT INTO transactions (account_id, type, amount, reference_id)
            VALUES (?, 'transfer_out', ?, ?)
            """,
            (sender_id, amount, reference_id),
        )
        connection.execute(
            """
            INSERT INTO transactions (account_id, type, amount, reference_id)
            VALUES (?, 'transfer_in', ?, ?)
            """,
            (recipient_id, amount, reference_id),
        )
        updated_sender = connection.execute(
            "SELECT id, user_id, balance FROM accounts WHERE id = ?",
            (sender_id,),
        ).fetchone()
        updated_recipient = connection.execute(
            "SELECT id, user_id, balance FROM accounts WHERE id = ?",
            (recipient_id,),
        ).fetchone()
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return {"sender": dict(updated_sender), "recipient": dict(updated_recipient)}
