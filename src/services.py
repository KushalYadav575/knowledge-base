from datetime import date

from exceptions import ItemNotFoundError
from models import KnowledgeItem
from storage import load_knowledge, save_knowledge
from validators import validate_all


def add_item(knowledge_item: KnowledgeItem) -> None:

    validate_all(knowledge_item)
    knowledge = load_knowledge()
    knowledge.append(knowledge_item)
    save_knowledge(knowledge)


def get_item(item_id: str) -> KnowledgeItem:

    knowledge = load_knowledge()
    for item in knowledge:
        if item.item_id == item_id:
            return item
    raise ItemNotFoundError("could not find an item with that id")


def delete_item(item_id: str) -> KnowledgeItem:
    knowledge = load_knowledge()
    for item in knowledge:
        if item.item_id == item_id:
            knowledge = [k for k in knowledge if k.item_id != item_id]

            save_knowledge(knowledge)
            return item

    raise ItemNotFoundError("could not find an item with that id")


def update_item(
    item_id: str,
    title: str | None = None,
    content: str | None = None,
    tags: list[str] | None = None,
    category: str | None = None,
    source: str | None = None,
) -> KnowledgeItem:
    
    knowledge = load_knowledge()
    for item in knowledge:
        if item.item_id == item_id:
            if title is not None:
                item.title = title
            if content is not None:
                item.content = content
            if tags is not None:
                item.tags = tags
            if category is not None:
                item.category = category
            if source is not None:
                item.source = source
            validate_all(item)
            item.updated_at = date.today()
            save_knowledge(knowledge)
            return item

    raise ItemNotFoundError("could not find an item with that id")\


def list_items() -> list[KnowledgeItem]:
    return load_knowledge()


def search_items(
    query: str,
    field: str | None = None
) -> set[str]:
    result = set()
    Knowledge = load_knowledge()
    for item in Knowledge:
        if field is not None:
            attribute_value = getattr(item, field)
            if isinstance(attribute_value, str):
                for item2 in attribute_value.split():
                    if query.lower() in item2.lower():
                        result.add(item.item_id)
            elif isinstance(attribute_value, list):
                for item2 in attribute_value:
                    for item3 in item2.split():
                        if query.lower() in item3.lower():
                            result.add(item.item_id)
            else:
                if str(attribute_value) == query:
                    result.add(item.item_id)
        else:
            for attribute_value in vars(item).values():
                if attribute_value:
                    if isinstance(attribute_value, str):
                        for item2 in attribute_value.split():
                            if query.lower() in item2.lower():
                                result.add(item.item_id)
                    elif isinstance(attribute_value, list):
                        for item2 in attribute_value:
                            for item3 in item2.split():
                                if query.lower() in item3.lower():
                                    result.add(item.item_id)
                    else:
                        if str(attribute_value) == query:
                            result.add(item.item_id)
    return result