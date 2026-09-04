import csv
import datetime
import json
import uuid
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

from .exceptions import ImportExportError, ItemNotFoundError
from .models import KnowledgeItem
from .storage import load_knowledge, save_knowledge
from .validators import validate_all


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
            item.updated_at = datetime.datetime.now(tz=ZoneInfo("Asia/Kolkata")).date()
            save_knowledge(knowledge)
            return item

    raise ItemNotFoundError("could not find an item with that id")


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
    total_items = len(knowledge)
    categories = Counter(item.category for item in knowledge)
    tags = Counter(item2 for item in knowledge for item2 in item.tags)
    sources = Counter(item.source for item in knowledge)
    return total_items, categories, tags, sources


def export_items(file_path):
    path = Path(file_path)
    knowledge = load_knowledge()

    if path.suffix.lower() == ".json":
        list_knowledge = [item.to_dict() for item in knowledge]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(list_knowledge, f)

    elif path.suffix.lower() == ".csv":
        fieldnames = [
            "item_id",
            "title",
            "content",
            "tags",
            "category",
            "source",
            "created_at",
            "updated_at",
        ]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()

            for item in knowledge:
                writer.writerow({
                    "item_id": item.item_id,
                    "title": item.title,
                    "content": item.content,
                    "tags": ", ".join(item.tags),
                    "category": item.category,
                    "source": item.source,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                })
    else:
        raise ImportExportError("File type must be .csv or .json")


def import_items(file_path):
    path = Path(file_path)

    if path.suffix.lower() == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        list_knowledge = [
            KnowledgeItem.from_dict(dictionary)
            for dictionary in data
        ]

    elif path.suffix.lower() == ".csv":
        list_knowledge = []

        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                row["tags"] = row["tags"].split(", ") if row["tags"] else []

                list_knowledge.append(
                    KnowledgeItem.from_dict(row)
                )

    else:
        raise ImportExportError("File type must be .csv or .json")

    knowledge = load_knowledge()

    for item in list_knowledge:
        for item2 in knowledge:
            if item.item_id == item2.item_id:
                item.item_id = str(uuid.uuid4())
                break

    knowledge.extend(list_knowledge)
    save_knowledge(knowledge)