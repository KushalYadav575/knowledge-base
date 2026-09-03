import json
from datetime import date

import pytest

import storage
from exceptions import DataCorruptionError, StorageError
from models import KnowledgeItem


@pytest.fixture
def sample_items():
    return [
        KnowledgeItem(
            title="Python Basics",
            content="Introduction to Python",
            tags=["python", "beginner"],
            category="Programming",
            source="Book",
            created_at=date(2026, 1, 1),
            updated_at=date(2026, 1, 1),
            item_id="item-101",
        ),
        KnowledgeItem(
            title="SQL Basics",
            content="Introduction to SQL",
            tags=["sql", "database"],
            category="Data",
            source="Course",
            created_at=date(2026, 1, 2),
            updated_at=date(2026, 1, 2),
            item_id="item-102",
        ),
    ]


def test_save_and_load_knowledge_roundtrip(tmp_path, sample_items):
    file_path = tmp_path / "knowledge.json"

    storage.save_knowledge(
        sample_items,
        filename=str(file_path),
    )

    loaded_items = storage.load_knowledge(
        filename=str(file_path),
    )

    assert loaded_items == sample_items


def test_save_creates_valid_json(tmp_path, sample_items):
    file_path = tmp_path / "knowledge.json"

    storage.save_knowledge(
        sample_items,
        filename=str(file_path),
    )

    with open(file_path, encoding="utf-8") as file:
        data = json.load(file)

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["title"] == "Python Basics"
    assert data[1]["title"] == "SQL Basics"


def test_save_empty_knowledge(tmp_path):
    file_path = tmp_path / "knowledge.json"

    storage.save_knowledge(
        [],
        filename=str(file_path),
    )

    loaded_items = storage.load_knowledge(
        filename=str(file_path),
    )

    assert loaded_items == []


def test_load_missing_file(tmp_path):
    file_path = tmp_path / "does_not_exist.json"

    with pytest.raises(StorageError):
        storage.load_knowledge(filename=str(file_path))


def test_load_corrupted_json(tmp_path):
    file_path = tmp_path / "knowledge.json"

    file_path.write_text(
        "{this is not valid json}",
        encoding="utf-8",
    )

    with pytest.raises(DataCorruptionError):
        storage.load_knowledge(
            filename=str(file_path),
        )


def test_load_malformed_item(tmp_path):
    file_path = tmp_path / "knowledge.json"

    file_path.write_text(
        '[{"missing_keys": true}]',
        encoding="utf-8",
    )

    with pytest.raises(KeyError):
        storage.load_knowledge(
            filename=str(file_path),
        )


def test_dates_are_restored_as_date_objects(tmp_path, sample_items):
    file_path = tmp_path / "knowledge.json"

    storage.save_knowledge(
        sample_items,
        filename=str(file_path),
    )

    loaded_items = storage.load_knowledge(
        filename=str(file_path),
    )

    assert isinstance(loaded_items[0].created_at, date)
    assert isinstance(loaded_items[0].updated_at, date)