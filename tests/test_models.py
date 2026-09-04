from datetime import date

from models import KnowledgeItem


class TestItemIdGeneration:
    def test_item_id_is_auto_generated_when_not_given(self, make_item):
        item = make_item()
        assert item.item_id

    def test_two_items_get_different_ids(self, make_item):
        item_a = make_item()
        item_b = make_item()
        assert item_a.item_id != item_b.item_id

    def test_explicit_item_id_is_respected(self, today):
        item = KnowledgeItem(
            title="Custom Id Item",
            content="content",
            tags=["tag"],
            category="cat",
            source="src",
            created_at=today,
            updated_at=today,
            item_id="my-custom-id",
        )
        assert item.item_id == "my-custom-id"


class TestToDict:
    def test_to_dict_has_all_expected_keys(self, sample_item):
        data = sample_item.to_dict()
        expected_keys = {
            "title", "content", "tags", "category", "source",
            "created_at", "updated_at", "item_id",
        }
        assert set(data.keys()) == expected_keys

    def test_to_dict_serializes_dates_as_iso_strings(self, sample_item):
        data = sample_item.to_dict()
        assert data["created_at"] == sample_item.created_at.isoformat()
        assert isinstance(data["created_at"], str)

    def test_to_dict_preserves_tag_list(self, sample_item):
        data = sample_item.to_dict()
        assert data["tags"] == sample_item.tags


class TestFromDict:
    def test_from_dict_reconstructs_equivalent_item(self, sample_item):
        data = sample_item.to_dict()
        rebuilt = KnowledgeItem.from_dict(data)

        assert rebuilt.title == sample_item.title
        assert rebuilt.content == sample_item.content
        assert rebuilt.tags == sample_item.tags
        assert rebuilt.category == sample_item.category
        assert rebuilt.source == sample_item.source
        assert rebuilt.item_id == sample_item.item_id

    def test_from_dict_parses_dates_back_into_date_objects(self, sample_item):
        data = sample_item.to_dict()
        rebuilt = KnowledgeItem.from_dict(data)

        assert isinstance(rebuilt.created_at, date)
        assert isinstance(rebuilt.updated_at, date)
        assert rebuilt.created_at == sample_item.created_at

    def test_round_trip_to_dict_then_from_dict_is_lossless(self, sample_item):
        rebuilt = KnowledgeItem.from_dict(sample_item.to_dict())
        assert rebuilt == sample_item


class TestStr:
    def test_str_contains_title_and_id(self, sample_item):
        text = str(sample_item)
        assert sample_item.title in text
        assert sample_item.item_id in text