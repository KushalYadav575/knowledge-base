from datetime import date

import pytest

import services
from exceptions import ItemNotFoundError, ValidationError
from models import KnowledgeItem


@pytest.fixture(autouse=True)
def mock_storage(monkeypatch, tmp_path):
    test_file = tmp_path / "service_knowledge.json"

    monkeypatch.setattr(
        "services.load_knowledge",
        lambda filename=str(test_file): services.storage.load_knowledge(filename),
    )
    monkeypatch.setattr(
        "services.save_knowledge",
        lambda knowledge, filename=str(test_file): services.storage.save_knowledge(
            knowledge, filename
        ),
    )

    services.storage.save_knowledge([], filename=str(test_file))
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


def test_add_and_get_item(sample_items):
    services.add_item(sample_items[0])
    fetched = services.get_item("item-101")
    assert fetched.title == "Python Basics"


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
    base_kwargs = {
        "title": "Title",
        "content": "Content",
        "tags": ["tag"],
        "category": "Cat",
        "source": "Src",
        "created_at": date.today(),
        "updated_at": date.today(),
    }
    base_kwargs.update(invalid_override)
    item = KnowledgeItem(**base_kwargs)

    with pytest.raises(ValidationError):
        services.add_item(item)

    assert len(services.list_items()) == 0


@pytest.mark.parametrize("operation", ["get", "delete"])
def test_item_not_found_operations(operation):
    target_func = getattr(services, f"{operation}_item")
    with pytest.raises(ItemNotFoundError):
        target_func("non-existent-id")


@pytest.mark.parametrize(
    "update_kwargs, expected_attr, expected_val",
    [
        ({"title": "New Title"}, "title", "New Title"),
        ({"content": "New Content"}, "content", "New Content"),
        ({"tags": ["new", "tags"]}, "tags", ["new", "tags"]),
        ({"category": "New Cat"}, "category", "New Cat"),
        ({"source": "New Src"}, "source", "New Src"),
    ],
)
def test_update_item_individual_fields(
    sample_items, update_kwargs, expected_attr, expected_val
):
    services.add_item(sample_items[0])
    updated = services.update_item("item-101", **update_kwargs)

    assert getattr(updated, expected_attr) == expected_val
    assert updated.updated_at == date.today()


@pytest.mark.parametrize(
    "invalid_update",
    [
        {"title": "   "},
        {"content": ""},
        {"tags": []},
        {"category": None},
    ],
)
def test_update_item_validation_failures(sample_items, invalid_update):
    services.add_item(sample_items[0])

    with pytest.raises(ValidationError):
        services.update_item("item-101", **invalid_update)

    item = services.get_item("item-101")
    assert item.title == "Python Basics"


@pytest.mark.parametrize(
    "query, search_field, expected_ids",
    [
        # Global search: matches 2 items containing 'python' in title/content/tags
        ("python", None, {"item-101", "item-102"}),
        # Global search: matches all 3 items containing 'guide'/'design'/'syntax' via 'coding' tag or content
        ("coding", None, {"item-101", "item-102"}),
        # Global search: single match
        ("database", None, {"item-103"}),
        # Global search: case insensitivity test across multiple matches
        ("SOFTWARE", None, {"item-101", "item-102"}),
        # Global search: no match
        ("rust", None, set()),
        
        # Specific field search (category): matches 2 items
        ("Software", "category", {"item-101", "item-102"}),
        # Specific field search (tags): matches 2 items
        ("python", "tags", {"item-101", "item-102"}),
        # Specific field search (title): matches 2 items
        ("Python", "title", {"item-101", "item-102"}),
        # Specific field search: present in category but searching title -> empty set
        ("Development", "title", set()),
        
        # Exact non-string attribute comparison
        ("2026-01-01", "created_at", {"item-101"}),
        ("2026-01-02", "created_at", {"item-102"}),
    ],
)
def test_search_items_multiple_matches(
    sample_items, query, search_field, expected_ids
):
    for item in sample_items:
        services.add_item(item)

    results = services.search_items(query, field=search_field)

    assert isinstance(results, set)
    assert results == expected_ids