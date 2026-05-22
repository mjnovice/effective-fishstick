from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict
from uuid import uuid4

from workspace.seed import CONVERSATIONS, SEEDED_CONVERSATION_CATEGORIES


REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "app.db"


class ConversationSummary(TypedDict):
    id: str
    caller_name: str
    summary: str


class Conversation(ConversationSummary):
    transcript: str


class ConversationCategoryRow(TypedDict):
    id: str
    conversation_id: str
    category_id: str
    review_status: str
    field_values: dict[str, Any]
    created_at: str
    updated_at: str


def connect_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def utc_timestamp() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def initialize_database(include_conversation_categories: bool, seed_saved_categories: bool) -> None:
    with connect_db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                caller_name TEXT NOT NULL,
                summary TEXT NOT NULL,
                transcript TEXT NOT NULL
            )
            """
        )

        if include_conversation_categories:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_categories (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL UNIQUE,
                    category_id TEXT NOT NULL,
                    review_status TEXT NOT NULL,
                    field_values_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
                """
            )

        conversation_count = connection.execute(
            "SELECT COUNT(*) FROM conversations"
        ).fetchone()[0]
        if conversation_count == 0:
            connection.executemany(
                """
                INSERT INTO conversations (id, caller_name, summary, transcript)
                VALUES (:id, :caller_name, :summary, :transcript)
                """,
                CONVERSATIONS,
            )

        if include_conversation_categories and seed_saved_categories:
            category_count = connection.execute(
                "SELECT COUNT(*) FROM conversation_categories"
            ).fetchone()[0]
            if category_count == 0:
                connection.executemany(
                    """
                    INSERT INTO conversation_categories (
                        id,
                        conversation_id,
                        category_id,
                        review_status,
                        field_values_json,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        :id,
                        :conversation_id,
                        :category_id,
                        :review_status,
                        :field_values_json,
                        :created_at,
                        :updated_at
                    )
                    """,
                    [
                        {
                            **record,
                            "field_values_json": json.dumps(record["field_values"]),
                        }
                        for record in SEEDED_CONVERSATION_CATEGORIES
                    ],
                )


def list_conversations() -> list[ConversationSummary]:
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT id, caller_name, summary
            FROM conversations
            ORDER BY id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_conversation(conversation_id: str) -> Conversation | None:
    with connect_db() as connection:
        row = connection.execute(
            """
            SELECT id, caller_name, summary, transcript
            FROM conversations
            WHERE id = ?
            """,
            (conversation_id,),
        ).fetchone()
    return dict(row) if row is not None else None


def get_conversation_category(conversation_id: str) -> ConversationCategoryRow | None:
    with connect_db() as connection:
        row = connection.execute(
            """
            SELECT id, conversation_id, category_id, review_status, field_values_json, created_at, updated_at
            FROM conversation_categories
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        ).fetchone()

    if row is None:
        return None

    record = dict(row)
    record["field_values"] = json.loads(record.pop("field_values_json"))
    return record


def create_conversation_category(
    conversation_id: str,
    category_id: str,
    review_status: str,
    field_values: dict[str, Any],
) -> ConversationCategoryRow:
    record_id = f"conversation-category-{uuid4().hex[:8]}"
    created_at = utc_timestamp()
    with connect_db() as connection:
        connection.execute(
            """
            INSERT INTO conversation_categories (
                id,
                conversation_id,
                category_id,
                review_status,
                field_values_json,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                conversation_id,
                category_id,
                review_status,
                json.dumps(field_values),
                created_at,
                created_at,
            ),
        )
    result = get_conversation_category(conversation_id)
    assert result is not None
    return result
