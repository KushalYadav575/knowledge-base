import uuid
from datetime import date

import pytest

from models import KnowledgeItem


@pytest.mark.parametrize(
    "item_id_input",
    [
        None,  # Triggers default UUID factory
        "custom-uuid-1234",
    ],
)
def test_knowledge_item_instantiation(item_id_input):
    kwargs = {
        "title": "Title",
        "content": "Content",
        "tags": ["tag"],
        "category": "Cat",
        "source": "Src",
        "created_at": date(2026, 1, 1),
        "updated_at": date(2026, 1, 1),
    }
    if item_id_input:
        kwargs["item_id"] = item_id_input

    item = KnowledgeItem(**kwargs)

    if item_id_input:
        assert item.item_id == "custom-uuid-1234"
    else:
        # Validate that default factory produced a valid UUID v4
        uuid_obj = uuid.UUID(item.item_id, version=4)
        assert str(uuid_obj) == item.item_id


def test_str_representation():
    item = KnowledgeItem(
        title="Python Testing",
        content="Content",
        tags=["python", "testing"],
        category="Cat",
        source="Src",
        created_at=date(2026, 1, 15),
        updated_at=date(2026, 1, 20),
        item_id="custom-uuid-1234",
    )
    expected_str = (
        "Python Testing with id = custom-uuid-1234 "
        "having tags ['python', 'testing'] created at 2026-01-15"
    )
    assert str(item) == expected_str


def test_to_dict():
    item = KnowledgeItem(
        title="Python Testing",
        content="Testing with Pytest is simple.",
        tags=["python", "testing"],
        category="Software",
        source="Documentation",
        created_at=date(2026, 1, 15),
        updated_at=date(2026, 1, 20),
        item_id="custom-uuid-1234",
    )
    assert item.to_dict() == {
        "title": "Python Testing",
        "content": "Testing with Pytest is simple.",
        "tags": ["python", "testing"],
        "category": "Software",
        "source": "Documentation",
        "created_at": "2026-01-15",
        "updated_at": "2026-01-20",
        "item_id": "custom-uuid-1234",
    }


@pytest.mark.parametrize(
    "raw_dict, expected_title, expected_created, expected_updated, expected_id",
    [
        (
            {
                "title": "Restored Item",
                "content": "Details",
                "tags": ["db"],
                "category": "Data",
                "source": "Disk",
                "created_at": "2026-02-01",
                "updated_at": "2026-02-02",
                "item_id": "restored-id-99",
            },
            "Restored Item",
            date(2026, 2, 1),
            date(2026, 2, 2),
            "restored-id-99",
        ),
    ],
)
def test_from_dict_valid(
    raw_dict, expected_title, expected_created, expected_updated, expected_id
):
    item = KnowledgeItem.from_dict(raw_dict)
    assert item.title == expected_title
    assert item.created_at == expected_created
    assert item.updated_at == expected_updated
    assert item.item_id == expected_id


@pytest.mark.parametrize(
    "invalid_dict, expected_exception",
    [
        # Missing required keys
        ({"title": "Missing attributes", "content": "Incomplete dict"}, KeyError),
        # Invalid date format
        (
            {
                "title": "Bad Date",
                "content": "Text",
                "tags": ["test"],
                "category": "Cat",
                "source": "Src",
                "created_at": "15-01-2026",  # Not ISO format
                "updated_at": "2026-01-20",
                "item_id": "123",
            },
            ValueError,
        ),
        # Invalid date type
        (
            {
                "title": "Bad Date Type",
                "content": "Text",
                "tags": ["test"],
                "category": "Cat",
                "source": "Src",
                "created_at": 12345678,
                "updated_at": "2026-01-20",
                "item_id": "123",
            },
            TypeError,
        ),
    ],
)
def test_from_dict_failures(invalid_dict, expected_exception):
    with pytest.raises(expected_exception):
        KnowledgeItem.from_dict(invalid_dict)