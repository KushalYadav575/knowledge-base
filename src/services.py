from datetime import date

from exceptions import ItemNotFoundError
from models import KnowledgeItem
from storage import load_knowledge, save_knowledge
from validators import validate_all
from collections import Counter


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
    matches: set[str] = set()
    query = query.lower()
    for item in load_knowledge():
        attributes = [getattr(item, field)] if field else vars(item).values()

        for value in attributes:
            if isinstance(value, str):
                if query in value.lower():
                    matches.add(item.item_id)

            elif isinstance(value, list):
                for element in value:
                    if query in element.lower():
                        matches.add(item.item_id)

            elif query == str(value).lower():
                matches.add(item.item_id)

    return matches

def get_stats():
    knowledge = load_knowledge()
    total_items = sum(1 for item in knowledge)
    categories = Counter(item.category for item in knowledge)
    tags = Counter(item2 for item in knowledge for item2 in item.tags)
    sources = Counter(item.source for item in knowledge)
    return total_items, categories, tags, sources