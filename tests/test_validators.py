from datetime import date, datetime
import pytest

from exceptions import ValidationError
from models import KnowledgeItem
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


@pytest.mark.parametrize(
    "validator_func",
    [validate_title, validate_content, validate_category, validate_source],
)
@pytest.mark.parametrize(
    "invalid_input, expected_msg",
    [
        (123, "must be a string"),
        (12.34, "must be a string"),
        (None, "must be a string"),
        ([], "must be a string"),
        ({}, "must be a string"),
        ("", "cannot be empty"),
        ("   ", "cannot be empty"),
        ("\n\t ", "cannot be empty"),
    ],
)
def test_string_validators_failures(validator_func, invalid_input, expected_msg):
    with pytest.raises(ValidationError, match=expected_msg):
        validator_func(invalid_input)


@pytest.mark.parametrize(
    "validator_func, valid_input",
    [
        (validate_title, "Valid Title"),
        (validate_content, "Valid Content text goes here"),
        (validate_category, "Technology"),
        (validate_source, "Official Documentation"),
    ],
)
def test_string_validators_success(validator_func, valid_input):
    validator_func(valid_input)  # Should not raise exception


@pytest.mark.parametrize(
    "invalid_tags, expected_msg",
    [
        ([], "Tags cannot be empty"),
        (None, "Tags cannot be empty"),
        (["valid", 123], "Tags must contain only strings"),
        (["valid", None], "Tags must contain only strings"),
        (["valid", 45.67], "Tags must contain only strings"),
        (["valid", ""], "Tags cannot contain empty strings"),
        (["valid", "   "], "Tags cannot contain empty strings"),
        (["\t\n"], "Tags cannot contain empty strings"),
    ],
)
def test_validate_tags_failures(invalid_tags, expected_msg):
    with pytest.raises(ValidationError, match=expected_msg):
        validate_tags(invalid_tags)


@pytest.mark.parametrize(
    "valid_tags",
    [
        ["python"],
        ["python", "pytest", "testing"],
        ["a", "b", "c"],
    ],
)
def test_validate_tags_success(valid_tags):
    validate_tags(valid_tags)


@pytest.mark.parametrize("validator_func", [validate_created_at, validate_updated_at])
@pytest.mark.parametrize(
    "invalid_date",
    [
        "2026-01-01",
        1672531199,
        None,
        [2026, 1, 1],
        {"year": 2026, "month": 1, "day": 1},
    ],
)
def test_date_validators_failures(validator_func, invalid_date):
    with pytest.raises(ValidationError, match="must be a date object"):
        validator_func(invalid_date)


@pytest.mark.parametrize("validator_func", [validate_created_at, validate_updated_at])
def test_date_validators_success(validator_func):
    validator_func(date.today())


def test_validate_all_success():
    item = KnowledgeItem(
        title="Valid Title",
        content="Valid Content",
        tags=["valid"],
        category="Cat",
        source="Src",
        created_at=date.today(),
        updated_at=date.today(),
    )
    validate_all(item)


@pytest.mark.parametrize(
    "field_override, expected_msg",
    [
        ({"title": ""}, "Title cannot be empty"),
        ({"content": "   "}, "Content cannot be empty"),
        ({"tags": []}, "Tags cannot be empty"),
        ({"category": 123}, "Category must be a string"),
        ({"source": None}, "Source must be a string"),
        ({"created_at": "2026-01-01"}, "created_at must be a date object"),
        ({"updated_at": "2026-01-01"}, "updated_at must be a date object"),
    ],
)
def test_validate_all_failure_cases(field_override, expected_msg):
    base_kwargs = {
        "title": "Valid Title",
        "content": "Valid Content",
        "tags": ["tag"],
        "category": "Cat",
        "source": "Src",
        "created_at": date.today(),
        "updated_at": date.today(),
    }
    base_kwargs.update(field_override)
    item = KnowledgeItem(**base_kwargs)

    with pytest.raises(ValidationError, match=expected_msg):
        validate_all(item)