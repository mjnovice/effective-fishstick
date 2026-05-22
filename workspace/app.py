from __future__ import annotations

from http import HTTPStatus
from typing import Any, TypedDict

from workspace import category_catalog, database
from workspace.category_catalog import CategoryFieldDef, CategoryListing
from workspace.database import Conversation, ConversationCategoryRow, ConversationSummary


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class HealthResponse(TypedDict):
    status: str
    service: str


class EnrichedConversationCategory(TypedDict):
    id: str
    conversation_id: str
    category_id: str
    category_name: str | None
    review_status: str
    field_values: dict[str, Any]
    missing_required_fields: list[str]
    category_fields: list[CategoryFieldDef]


def health() -> HealthResponse:
    return {"status": "ok", "service": "aurelian-conversation-categories-starter"}


def list_categories() -> list[CategoryListing]:
    return category_catalog.list_categories()


def list_conversations() -> list[ConversationSummary]:
    return database.list_conversations()


def get_conversation_or_404(conversation_id: str) -> Conversation:
    conversation = database.get_conversation(conversation_id)
    if conversation is None:
        raise ApiError(HTTPStatus.NOT_FOUND, "Conversation not found")
    return conversation


def get_conversation_category(conversation_id: str) -> EnrichedConversationCategory:
    get_conversation_or_404(conversation_id)
    record = database.get_conversation_category(conversation_id)
    if record is None:
        raise ApiError(HTTPStatus.NOT_FOUND, "Conversation category not found")
    return record


def create_conversation_category(
    conversation_id: str,
    payload: dict[str, Any],
) -> ConversationCategoryRow:
    get_conversation_or_404(conversation_id)
    category_id = payload.get("category_id", "")
    field_values = payload.get("field_values", {})
    review_status = payload.get("review_status", "needs_review")
    created = database.create_conversation_category(
        conversation_id=conversation_id,
        category_id=category_id,
        review_status=review_status,
        field_values=field_values,
    )
    return created


ROUTES = [
    ("GET",  "/api/health",                                   health,                       200),
    ("GET",  "/api/categories",                               list_categories,              200),
    ("GET",  "/api/conversations",                            list_conversations,           200),
    ("GET",  "/api/conversations/{conversation_id}",          get_conversation_or_404,      200),
    ("GET",  "/api/conversations/{conversation_id}/category", get_conversation_category,    200),
    ("POST", "/api/conversations/{conversation_id}/category", create_conversation_category, 201),
]
