from datetime import date

from exceptions import ValidationError
from models import KnowledgeItem


def validate_title(title: str) -> None:
    if not isinstance(title, str):
        raise ValidationError("Title must be a string")
    if not title.strip():
        raise ValidationError("Title cannot be empty")


def validate_content(content: str) -> None:
    if not isinstance(content, str):
        raise ValidationError("Content must be a string")
    if not content.strip():
        raise ValidationError("Content cannot be empty")


def validate_tags(tags: list[str]) -> None:
    if not tags:
        raise ValidationError("Tags cannot be empty")
    for item in tags:
        if not isinstance(item, str):
            raise ValidationError("Tags must contain only strings")
        if not item.strip():
            raise ValidationError("Tags cannot contain empty strings")


def validate_category(category: str) -> None:
    if not isinstance(category, str):
        raise ValidationError("Category must be a string")
    if not category.strip():
        raise ValidationError("Category cannot be empty")


def validate_source(source: str) -> None:
    if not isinstance(source, str):
        raise ValidationError("Source must be a string")
    if not source.strip():
        raise ValidationError("Source cannot be empty")


def validate_created_at(created_at: date) -> None:
    if not isinstance(created_at, date):
        raise ValidationError("created_at must be a date object")


def validate_updated_at(updated_at: date) -> None:
    if not isinstance(updated_at, date):
        raise ValidationError("updated_at must be a date object")


def validate_all(knowledge_item: KnowledgeItem) -> None:
    validate_title(knowledge_item.title)
    validate_content(knowledge_item.content)
    validate_tags(knowledge_item.tags)
    validate_category(knowledge_item.category)
    validate_source(knowledge_item.source)
    validate_created_at(knowledge_item.created_at)
    validate_updated_at(knowledge_item.updated_at)