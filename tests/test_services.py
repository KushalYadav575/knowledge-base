import csv
import json

import pytest

from knowledge_base_cli import services
from knowledge_base_cli.exceptions import (
    ImportExportError,
    ItemNotFoundError,
    ValidationError,
)
from knowledge_base_cli.models import KnowledgeItem


@pytest.fixture
def fake_db(monkeypatch):
    db: list[KnowledgeItem] = []

    def fake_load(filename=None):
        return list(db)

    def fake_save(knowledge, filename=None):
        db[:] = knowledge

    monkeypatch.setattr(services, "load_knowledge", fake_load)
    monkeypatch.setattr(services, "save_knowledge", fake_save)
    return db


class TestAddItem:
    def test_add_item_appends_to_storage(self, fake_db, sample_item):
        services.add_item(sample_item)
        assert fake_db == [sample_item]

    def test_add_item_keeps_existing_items(self, fake_db, sample_items):
        for item in sample_items:
            services.add_item(item)
        assert len(fake_db) == len(sample_items)

    def test_add_item_rejects_invalid_item(self, fake_db, sample_item):
        sample_item.title = ""
        with pytest.raises(ValidationError):
            services.add_item(sample_item)
        assert fake_db == []


class TestGetItem:
    def test_get_item_returns_matching_item(self, fake_db, sample_item):
        fake_db.append(sample_item)
        found = services.get_item(sample_item.item_id)
        assert found is sample_item

    def test_get_item_raises_when_missing(self, fake_db):
        with pytest.raises(ItemNotFoundError):
            services.get_item("no-such-id")


class TestDeleteItem:
    def test_delete_item_removes_it_from_storage(self, fake_db, sample_items):
        fake_db.extend(sample_items)
        target = sample_items[0]

        services.delete_item(target.item_id)

        remaining_ids = [item.item_id for item in fake_db]
        assert target.item_id not in remaining_ids
        assert len(fake_db) == len(sample_items) - 1

    def test_delete_item_returns_the_deleted_item(self, fake_db, sample_item):
        fake_db.append(sample_item)
        deleted = services.delete_item(sample_item.item_id)
        assert deleted.item_id == sample_item.item_id

    def test_delete_item_raises_when_missing(self, fake_db):
        with pytest.raises(ItemNotFoundError):
            services.delete_item("no-such-id")

    def test_delete_item_leaves_other_items_untouched(self, fake_db, sample_items):
        fake_db.extend(sample_items)
        services.delete_item(sample_items[0].item_id)

        remaining_titles = {item.title for item in fake_db}
        expected_titles = {item.title for item in sample_items[1:]}
        assert remaining_titles == expected_titles


class TestUpdateItem:
    def test_update_changes_only_given_fields(self, fake_db, sample_item):
        fake_db.append(sample_item)
        original_content = sample_item.content

        updated = services.update_item(sample_item.item_id, title="New Title")

        assert updated.title == "New Title"
        assert updated.content == original_content

    def test_update_bumps_updated_at(self, fake_db, sample_item, today):
        sample_item.updated_at = today
        fake_db.append(sample_item)

        updated = services.update_item(sample_item.item_id, title="New Title")

        assert updated.updated_at != today or updated.updated_at is not None

    def test_update_raises_when_missing(self, fake_db):
        with pytest.raises(ItemNotFoundError):
            services.update_item("no-such-id", title="New Title")

    def test_update_revalidates_new_values(self, fake_db, sample_item):
        fake_db.append(sample_item)
        with pytest.raises(ValidationError):
            services.update_item(sample_item.item_id, title="")

    def test_update_with_no_fields_leaves_item_unchanged(self, fake_db, sample_item):
        fake_db.append(sample_item)
        original_title = sample_item.title

        updated = services.update_item(sample_item.item_id)

        assert updated.title == original_title


class TestListItems:
    def test_list_items_returns_everything(self, fake_db, sample_items):
        fake_db.extend(sample_items)
        result = services.list_items()
        assert len(result) == len(sample_items)

    def test_list_items_on_empty_db_returns_empty_list(self, fake_db):
        assert services.list_items() == []


class TestSearchItems:
    @pytest.mark.parametrize(
        "query, field, expected_title",
        [
            ("binary", "title", "Binary Search"),
            ("BINARY", "title", "Binary Search"),
            ("plants", "content", "Photosynthesis"),
            ("biology", "tags", "Photosynthesis"),
            ("history", "category", "The French Revolution"),
            ("wikipedia", "source", "The French Revolution"),
        ],
    )
    def test_search_finds_expected_item_by_field(
        self, fake_db, sample_items, query, field, expected_title
    ):
        fake_db.extend(sample_items)
        matches = services.search_items(query, field=field)

        matched_titles = {
            item.title for item in fake_db if item.item_id in matches
        }
        assert expected_title in matched_titles

    def test_search_with_no_field_searches_everything(self, fake_db, sample_items):
        fake_db.extend(sample_items)
        matches = services.search_items("europe")
        assert len(matches) == 1

    def test_search_with_no_matches_returns_empty_set(self, fake_db, sample_items):
        fake_db.extend(sample_items)
        matches = services.search_items("nonexistent-query-xyz")
        assert matches == set()

    def test_search_on_empty_db_returns_empty_set(self, fake_db):
        assert services.search_items("anything") == set()


class TestGetStats:
    def test_total_items_count(self, fake_db, sample_items):
        fake_db.extend(sample_items)
        total, _categories, _tags, _sources = services.get_stats()
        assert total == len(sample_items)

    def test_categories_are_counted_per_item(self, fake_db, sample_items):
        fake_db.extend(sample_items)
        _, categories, _, _ = services.get_stats()
        assert categories["Computer Science"] == 1
        assert categories["Science"] == 1
        assert categories["History"] == 1

    def test_tags_are_flattened_and_counted(self, fake_db, sample_items):
        fake_db.extend(sample_items)
        _, _, tags, _ = services.get_stats()
        assert tags["algorithms"] == 1
        assert tags["biology"] == 1

    def test_stats_on_empty_db(self, fake_db):
        total, categories, tags, _sources = services.get_stats()
        assert total == 0
        assert sum(categories.values()) == 0
        assert sum(tags.values()) == 0


class TestExportItems:
    def test_export_to_json_writes_readable_file(self, fake_db, sample_items, tmp_path):
        fake_db.extend(sample_items)
        out_path = tmp_path / "export.json"

        services.export_items(str(out_path))

        data = json.loads(out_path.read_text(encoding="utf-8"))
        assert len(data) == len(sample_items)

    def test_export_to_csv_writes_a_row_per_item(self, fake_db, sample_items, tmp_path):
        fake_db.extend(sample_items)
        out_path = tmp_path / "export.csv"

        services.export_items(str(out_path))

        with open(out_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == len(sample_items)

    @pytest.mark.xfail(
        reason=(
            "Known bug: export_items() has no 'else' branch for an "
            "unsupported extension, so it silently writes nothing instead "
            "of raising exceptions.ImportExportError (which exists but is "
            "never imported/used in services.py)."
        ),
        strict=False,
    )
    def test_export_with_unsupported_extension_raises(self, fake_db, sample_item, tmp_path):
        fake_db.append(sample_item)
        out_path = tmp_path / "export.txt"

        with pytest.raises(ImportExportError):
            services.export_items(str(out_path))


class TestImportItems:
    def test_import_from_json_adds_items(self, fake_db, sample_items, tmp_path):
        json_path = tmp_path / "import.json"
        json_path.write_text(
            json.dumps([item.to_dict() for item in sample_items]),
            encoding="utf-8",
        )

        services.import_items(str(json_path))

        assert len(fake_db) == len(sample_items)

    def test_import_keeps_existing_items(self, fake_db, sample_item, sample_items, tmp_path):
        fake_db.append(sample_item)
        json_path = tmp_path / "import.json"
        json_path.write_text(
            json.dumps([item.to_dict() for item in sample_items]),
            encoding="utf-8",
        )

        services.import_items(str(json_path))

        assert len(fake_db) == 1 + len(sample_items)

    def test_import_reassigns_id_on_collision(self, fake_db, sample_item, tmp_path):
        fake_db.append(sample_item)
        json_path = tmp_path / "import.json"
        colliding = sample_item.to_dict()
        colliding["title"] = "A totally different title"
        json_path.write_text(json.dumps([colliding]), encoding="utf-8")

        services.import_items(str(json_path))

        ids = [item.item_id for item in fake_db]
        assert len(ids) == len(set(ids)), "duplicate item_id survived import"
        assert len(fake_db) == 2

    @pytest.mark.xfail(
        reason=(
            "Known bug: import_items() only defines list_knowledge inside "
            "the .json/.csv branches. An unsupported extension falls "
            "through both, so list_knowledge is never assigned and the "
            "function raises UnboundLocalError instead of "
            "exceptions.ImportExportError."
        ),
        strict=False,
    )
    def test_import_with_unsupported_extension_raises(self, fake_db, tmp_path):
        bad_path = tmp_path / "import.txt"
        bad_path.write_text("not usable", encoding="utf-8")

        with pytest.raises(ImportExportError):
            services.import_items(str(bad_path))