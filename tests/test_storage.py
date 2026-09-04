import json

import pytest

from exceptions import DataCorruptionError, StorageError
from storage import load_knowledge, save_knowledge


class TestSaveAndLoadRoundTrip:
    def test_saving_then_loading_returns_equivalent_items(self, tmp_path, sample_items):
        file_path = tmp_path / "knowledge.json"

        save_knowledge(sample_items, filename=file_path)
        loaded = load_knowledge(filename=file_path)

        assert len(loaded) == len(sample_items)
        assert [item.item_id for item in loaded] == [item.item_id for item in sample_items]
        assert [item.title for item in loaded] == [item.title for item in sample_items]

    def test_saving_empty_list_then_loading_returns_empty_list(self, tmp_path):
        file_path = tmp_path / "knowledge.json"

        save_knowledge([], filename=file_path)
        loaded = load_knowledge(filename=file_path)

        assert loaded == []

    def test_save_creates_a_file_on_disk(self, tmp_path, sample_item):
        file_path = tmp_path / "knowledge.json"
        assert not file_path.exists()

        save_knowledge([sample_item], filename=file_path)

        assert file_path.exists()

    def test_saved_file_is_valid_json(self, tmp_path, sample_items):
        file_path = tmp_path / "knowledge.json"
        save_knowledge(sample_items, filename=file_path)

        raw = json.loads(file_path.read_text(encoding="utf-8"))
        assert isinstance(raw, list)
        assert len(raw) == len(sample_items)


class TestLoadErrors:
    def test_missing_file_raises_storage_error(self, tmp_path):
        missing_path = tmp_path / "does_not_exist.json"
        with pytest.raises(StorageError):
            load_knowledge(filename=missing_path)

    def test_corrupted_json_raises_data_corruption_error(self, tmp_path):
        bad_file = tmp_path / "corrupted.json"
        bad_file.write_text("{not valid json!!", encoding="utf-8")

        with pytest.raises(DataCorruptionError):
            load_knowledge(filename=bad_file)

    def test_data_corruption_error_is_also_a_storage_error(self, tmp_path):
        bad_file = tmp_path / "corrupted.json"
        bad_file.write_text("not json at all", encoding="utf-8")

        with pytest.raises(StorageError):
            load_knowledge(filename=bad_file)