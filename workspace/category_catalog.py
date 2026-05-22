from __future__ import annotations

from typing import Any, TypedDict


LOST_PET_CATEGORY_ID = "category-lost-pet"
TOW_REQUEST_CATEGORY_ID = "category-tow-request"
NOISE_COMPLAINT_CATEGORY_ID = "category-noise-complaint"


class CategoryFieldDef(TypedDict):
    key: str
    label: str
    required: bool


class CategoryDef(TypedDict):
    id: str
    name: str
    fields: list[CategoryFieldDef]


class CategoryListing(TypedDict):
    id: str
    name: str


CATEGORIES: dict[str, CategoryDef] = {
    LOST_PET_CATEGORY_ID: {
        "id": LOST_PET_CATEGORY_ID,
        "name": "Lost Pet",
        "fields": [
            {"key": "pet_name", "label": "Pet name", "required": True},
            {"key": "animal_type", "label": "Animal type", "required": True},
            {"key": "last_seen_location", "label": "Last seen location", "required": True},
            {"key": "collar_color", "label": "Collar color", "required": False},
        ],
    },
    TOW_REQUEST_CATEGORY_ID: {
        "id": TOW_REQUEST_CATEGORY_ID,
        "name": "Tow Request",
        "fields": [
            {"key": "vehicle_make", "label": "Vehicle make", "required": True},
            {"key": "vehicle_model", "label": "Vehicle model", "required": True},
            {"key": "location", "label": "Vehicle location", "required": True},
            {"key": "blocking_traffic", "label": "Blocking traffic", "required": True},
        ],
    },
    NOISE_COMPLAINT_CATEGORY_ID: {
        "id": NOISE_COMPLAINT_CATEGORY_ID,
        "name": "Noise Complaint",
        "fields": [
            {"key": "address", "label": "Address", "required": True},
            {"key": "issue_description", "label": "Issue description", "required": True},
            {"key": "observed_at", "label": "Observed at", "required": False},
        ],
    },
}


def get_category(category_id: str) -> CategoryDef | None:
    return CATEGORIES.get(category_id)


def category_name(category_id: str) -> str | None:
    category = get_category(category_id)
    if category is None:
        return None
    return category["name"]


def category_fields(category_id: str) -> list[CategoryFieldDef]:
    category = get_category(category_id)
    if category is None:
        return []
    return list(category["fields"])


def required_field_keys(category_id: str) -> list[str]:
    return [
        str(field["key"])
        for field in category_fields(category_id)
        if bool(field["required"])
    ]


def allowed_field_keys(category_id: str) -> list[str]:
    return [str(field["key"]) for field in category_fields(category_id)]


def field_has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def missing_required_fields(category_id: str, field_values: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for field in category_fields(category_id):
        if not field["required"]:
            continue
        if not field_has_value(field_values.get(str(field["key"]))):
            missing.append(str(field["key"]))
    return missing


def unknown_field_keys(category_id: str, field_values: dict[str, Any]) -> list[str]:
    allowed = set(allowed_field_keys(category_id))
    return sorted(key for key in field_values if key not in allowed)


def list_categories() -> list[CategoryListing]:
    return [
        {"id": cat["id"], "name": cat["name"]}
        for cat in CATEGORIES.values()
    ]
