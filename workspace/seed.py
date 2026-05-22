from __future__ import annotations

from workspace.category_catalog import LOST_PET_CATEGORY_ID, NOISE_COMPLAINT_CATEGORY_ID


CONVERSATIONS = [
    {
        "id": "conv-100",
        "caller_name": "Kelly Nunez",
        "summary": "Caller reports a missing Labrador last seen near Maple Ave.",
        "transcript": (
            "Agent: Aurelian non-emergency line, this is Aria. How can I help?\n"
            "Caller: My dog Milo slipped his leash near Maple Ave and 12th about an hour ago.\n"
            "Agent: I'm sorry to hear that. Can you describe Milo?\n"
            "Caller: He's a brown Labrador, about sixty pounds, wearing a red collar with tags.\n"
            "Agent: Got it. Any chance he was heading toward a park or familiar spot?\n"
            "Caller: There's a dog park two blocks east — he might have gone that way.\n"
            "Agent: Thank you. I'll log this and dispatch will follow up shortly."
        ),
    },
    {
        "id": "conv-200",
        "caller_name": "Marcus Lee",
        "summary": "Caller wants an abandoned sedan removed from an alley.",
        "transcript": (
            "Agent: Aurelian non-emergency line, this is Aria. How can I help?\n"
            "Caller: There's a car sitting behind my building for two days now.\n"
            "Agent: Is it blocking traffic or access?\n"
            "Caller: It's blocking the alley entrance for deliveries.\n"
            "Agent: Can you give me the address and any details on the vehicle?\n"
            "Caller: 415 Cedar Street. It's a silver sedan, looks like the back tire is flat.\n"
            "Agent: Thank you. I'll forward this to parking enforcement."
        ),
    },
    {
        "id": "conv-300",
        "caller_name": "Priya Shah",
        "summary": "Caller reports overnight construction noise near downtown.",
        "transcript": (
            "Agent: Aurelian non-emergency line, this is Aria. How can I help?\n"
            "Caller: Construction is still going at almost midnight near my apartment.\n"
            "Agent: What address are you calling about?\n"
            "Caller: It's the project at 88 8th Street.\n"
            "Agent: How long has the noise been going on tonight?\n"
            "Caller: Since about eleven, and it happened last night too.\n"
            "Agent: Understood. I'll file a noise complaint for review."
        ),
    },
]


SEEDED_CONVERSATION_CATEGORIES = [
    {
        "id": "conversation-category-100",
        "conversation_id": "conv-100",
        "category_id": LOST_PET_CATEGORY_ID,
        "review_status": "needs_review",
        "field_values": {
            "collar_color": "red",
            "breed": "Labrador",
        },
        "created_at": "2026-03-28T09:18:00",
        "updated_at": "2026-03-28T09:18:00",
    },
    {
        "id": "conversation-category-300",
        "conversation_id": "conv-300",
        "category_id": NOISE_COMPLAINT_CATEGORY_ID,
        "review_status": "confirmed",
        "field_values": {
            "address": "88 8th St",
            "issue_description": "Construction noise after quiet hours",
            "observed_at": "11:30 PM",
        },
        "created_at": "2026-03-30T00:17:00",
        "updated_at": "2026-03-30T00:17:00",
    },
]
