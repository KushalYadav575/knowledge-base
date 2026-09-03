import json

from exceptions import DataCorruptionError, StorageError
from models import KnowledgeItem


def save_knowledge(note: list[KnowledgeItem], filename: str="knowledge.json") -> None:
    note_data = [item.to_dict() for item in note]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(note_data, file)


def load_knowledge(filename: str="knowledge.json") -> list[KnowledgeItem]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            file_data = json.load(f)

        note: list[KnowledgeItem] = []
        for item in file_data:
            obj = KnowledgeItem.from_dict(item)
            note.append(obj)

        return note

    except FileNotFoundError:
        raise StorageError("no file found ")
    except json.JSONDecodeError:
        raise DataCorruptionError("failed to parse data")
    return []