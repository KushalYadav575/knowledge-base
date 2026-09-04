from datetime import date, datetime

import pytest

from exceptions import ValidationError
from validators import (
    validate_all,
    validate_category,
    validate_content,
    validate_created_at,
    validate_source,
    validate_tags,
    validate_title,
    validate_updated_at,
)


TEXT_FIELD_VALIDATORS = [
    validate_title,
    validate_content,
    validate_category,
    validate_source,
]

VALID_TEXT_VALUES = [
    "Binary Search",
    "a",
    "  padded but has real text  ",
]

INVALID_TEXT_VALUES = [
    "",
    "   ",
    None,
    123,
]


@pytest.mark.parametrize("validator", TEXT_FIELD_VALIDATORS)
@pytest.mark.parametrize("value", VALID_TEXT_VALUES)
def test_text_field_accepts_valid_values(validator, value):
    validator(value)


@pytest.mark.parametrize("validator", TEXT_FIELD_VALIDATORS)
@pytest.mark.parametrize("value", INVALID_TEXT_VALUES)
def test_text_field_rejects_invalid_values(validator, value):
    with pytest.raises(ValidationError):
        validator(value)


@pytest.mark.parametrize(
    "tags",
    [
        ["algorithms"],
        ["algorithms", "search"],
        ["  has real text  "],
    ],
)
def test_validate_tags_accepts_valid_lists(tags):
    validate_tags(tags)


@pytest.mark.parametrize(
    "tags",
    [
        [],
        [""],
        ["   "],
        ["ok", 123],
        None,
    ],
)
def test_validate_tags_rejects_invalid_lists(tags):
    with pytest.raises(ValidationError):
        validate_tags(tags)


@pytest.mark.parametrize("validator", [validate_created_at, validate_updated_at])
def test_date_field_accepts_a_date_object(validator):
    validator(date(2026, 1, 15))


@pytest.mark.parametrize("validator", [validate_created_at, validate_updated_at])
@pytest.mark.parametrize(
    "value",
    [
        "2026-01-15",
        None,
        12345,
    ],
)
def test_date_field_rejects_non_date_values(validator, value):
    with pytest.raises(ValidationError):
        validator(value)


def test_datetime_is_accepted_because_it_is_a_date_subclass():
    validate_created_at(datetime(2026, 1, 15, 9, 30))


class TestValidateAll:
    def test_valid_item_passes(self, sample_item):
        validate_all(sample_item)

    def test_invalid_title_is_caught(self, sample_item):
        sample_item.title = ""
        with pytest.raises(ValidationError):
            validate_all(sample_item)

    def test_invalid_tags_is_caught(self, sample_item):
        sample_item.tags = []
        with pytest.raises(ValidationError):
            validate_all(sample_item)

    def test_first_failing_field_wins(self, sample_item):
        sample_item.title = ""
        sample_item.content = ""
        with pytest.raises(ValidationError, match="Title"):
            validate_all(sample_item)