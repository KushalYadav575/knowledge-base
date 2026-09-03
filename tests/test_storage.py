import json
from datetime import date

import pytest

from exceptions import DataCorruptionError, StorageError
from models import KnowledgeItem
from storage import load_knowledge, save_knowledge


@pytest.fixture
def sample_items():
    return [
        KnowledgeItem(
            title="Item 1",
            # content="Content 1",
            tags=["t1"],
            category="Cat1",
            source="Src1",
            created_at=date(2026, 1, 1),
            updated_at=date(2026, 1, 2),
            item_id="id-1",
        ),
        KnowledgeItem(
            title="Item 2",
            content="Content 2",
            tags=["t2"],
            category="Cat2",
            source="Src2",
            created_at=date(2026, 1, 3),
            updated_at=date(2026, 1, 4),
            item_id="id-2",
        ),
    ]


def test_save_and_load_knowledge_roundtrip(tmp_path, sample_items):
    filepath = tmp_path / "test_knowledge.json"
    save_knowledge(sample_items, filename=str(filepath))

    loaded = load_knowledge(filename=str(filepath))
    assert len(loaded) == 2
    assert loaded[0].title == "Item 1"
    assert loaded[1].item_id == "id-2"


@pytest.mark.parametrize(
    "corrupt_content, expected_exception, match_msg",
    [
        ("{ invalid json syntax", DataCorruptionError, "failed to parse data"),
        ("not json at all", DataCorruptionError, "failed to parse data"),
        ('{"key": "unclosed string}', DataCorruptionError, "failed to parse data"),
        ("[{'missing_keys': True}]", KeyError, None),  # Malformed item structure
    ],
)
def test_load_knowledge_corrupt_files(
    tmp_path, corrupt_content, expected_exception, match_msg
):
    filepath = tmp_path / "corrupt_data.json"
    filepath.write_text(corrupt_content, encoding="utf-8")

    if match_msg:
        with pytest.raises(expected_exception, match=match_msg):
            load_knowledge(filename=str(filepath))
    else:
        with pytest.raises(expected_exception):
            load_knowledge(filename=str(filepath))


def test_load_knowledge_file_not_found(tmp_path):
    non_existent = tmp_path / "does_not_exist.json"
    with pytest.raises(StorageError, match="no file found"):
        load_knowledge(filename=str(non_existent))