from datetime import date

import pytest

import services
import storage
from exceptions import ItemNotFoundError, ValidationError
from models import KnowledgeItem


@pytest.fixture(autouse=True)
def mock_storage(monkeypatch, tmp_path):
    test_file = tmp_path / "service_knowledge.json"

    monkeypatch.setattr(
        services,
        "load_knowledge",
        lambda filename=str(test_file): storage.load_knowledge(filename),
    )

    monkeypatch.setattr(
        services,
        "save_knowledge",
        lambda knowledge, filename=str(test_file): storage.save_knowledge(
            knowledge, filename
        ),
    )

    storage.save_knowledge([], filename=str(test_file))

    return test_file


@pytest.fixture
def sample_items():
    return [
        KnowledgeItem(
            title="Python Basics",
            content="Introductory guide to Python programming syntax",
            tags=["python", "beginner", "coding"],
            category="Software Development",
            source="Book",
            created_at=date(2026, 1, 1),
            updated_at=date(2026, 1, 1),
            item_id="item-101",
        ),
        KnowledgeItem(
            title="Advanced Python",
            content="Deep dive into Python async, GIL, and metaprogramming",
            tags=["python", "advanced", "coding"],
            category="Software Development",
            source="Course",
            created_at=date(2026, 1, 2),
            updated_at=date(2026, 1, 2),
            item_id="item-102",
        ),
        KnowledgeItem(
            title="Database Design",
            content="Relational database schema design and SQL optimization",
            tags=["sql", "database"],
            category="Data Engineering",
            source="Article",
            created_at=date(2026, 1, 3),
            updated_at=date(2026, 1, 3),
            item_id="item-103",
        ),
    ]


def test_add_item(sample_items):
    services.add_item(sample_items[0])

    items = services.list_items()

    assert len(items) == 1
    assert items[0] == sample_items[0]


def test_get_item(sample_items):
    services.add_item(sample_items[0])

    item = services.get_item("item-101")

    assert item == sample_items[0]


def test_get_item_not_found():
    with pytest.raises(ItemNotFoundError):
        services.get_item("does-not-exist")


def test_delete_item(sample_items):
    services.add_item(sample_items[0])
    services.add_item(sample_items[1])

    deleted = services.delete_item("item-101")

    assert deleted == sample_items[0]
    assert len(services.list_items()) == 1
    assert services.get_item("item-102") == sample_items[1]


def test_delete_item_not_found():
    with pytest.raises(ItemNotFoundError):
        services.delete_item("does-not-exist")


@pytest.mark.parametrize(
    "invalid_override",
    [
        {"title": ""},
        {"content": "   "},
        {"tags": []},
        {"category": 123},
        {"source": None},
    ],
)
def test_add_item_validation_failures(invalid_override):
    data = {
        "title": "Title",
        "content": "Content",
        "tags": ["tag"],
        "category": "Category",
        "source": "Source",
        "created_at": date.today(),
        "updated_at": date.today(),
    }

    data.update(invalid_override)

    item = KnowledgeItem(**data)

    with pytest.raises(ValidationError):
        services.add_item(item)

    assert services.list_items() == []


@pytest.mark.parametrize(
    "update_kwargs, expected_attr, expected_value",
    [
        ({"title": "New Title"}, "title", "New Title"),
        ({"content": "New Content"}, "content", "New Content"),
        ({"tags": ["new", "tags"]}, "tags", ["new", "tags"]),
        ({"category": "New Category"}, "category", "New Category"),
        ({"source": "New Source"}, "source", "New Source"),
    ],
)
def test_update_item(
    sample_items,
    update_kwargs,
    expected_attr,
    expected_value,
):
    services.add_item(sample_items[0])

    updated = services.update_item(
        "item-101",
        **update_kwargs,
    )

    assert getattr(updated, expected_attr) == expected_value
    assert updated.updated_at == date.today()


def test_update_multiple_fields(sample_items):
    services.add_item(sample_items[0])

    updated = services.update_item(
        "item-101",
        title="Updated Title",
        content="Updated Content",
        tags=["updated", "tags"],
        category="Updated Category",
        source="Updated Source",
    )

    assert updated.title == "Updated Title"
    assert updated.content == "Updated Content"
    assert updated.tags == ["updated", "tags"]
    assert updated.category == "Updated Category"
    assert updated.source == "Updated Source"


@pytest.mark.parametrize(
    "invalid_update",
    [
        {"title": ""},
        {"content": "   "},
        {"tags": []},
        {"category": ""},
        {"source": ""},
    ],
)
def test_update_item_validation_failures(sample_items, invalid_update):
    services.add_item(sample_items[0])

    with pytest.raises(ValidationError):
        services.update_item("item-101", **invalid_update)

    item = services.get_item("item-101")

    assert item.title == "Python Basics"


def test_update_item_not_found():
    with pytest.raises(ItemNotFoundError):
        services.update_item(
            "does-not-exist",
            title="New Title",
        )


def test_list_items(sample_items):
    services.add_item(sample_items[0])
    services.add_item(sample_items[1])

    items = services.list_items()

    assert items == sample_items[:2]


@pytest.mark.parametrize(
    "query, field, expected_ids",
    [
        ("python", None, {"item-101", "item-102"}),
        ("coding", None, {"item-101", "item-102"}),
        ("database", None, {"item-103"}),
        ("SOFTWARE", None, {"item-101", "item-102"}),
        ("rust", None, set()),
        ("Software", "category", {"item-101", "item-102"}),
        ("python", "tags", {"item-101", "item-102"}),
        ("Python", "title", {"item-101", "item-102"}),
        ("Development", "title", set()),
        ("2026-01-01", "created_at", {"item-101"}),
        ("2026-01-02", "created_at", {"item-102"}),
    ],
)
def test_search_items(
    sample_items,
    query,
    field,
    expected_ids,
):
    for item in sample_items:
        services.add_item(item)

    results = services.search_items(query, field=field)

    assert isinstance(results, set)
    assert results == expected_ids