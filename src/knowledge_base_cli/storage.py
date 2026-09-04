import json
from pathlib import Path

from .exceptions import DataCorruptionError
from .models import KnowledgeItem

DEFAULT_FILE = (
    Path(__file__).resolve().parents[2] / "data" / "knowledge.json"
)


def save_knowledge(
    note: list[KnowledgeItem],
    filename: Path = DEFAULT_FILE,
) -> None:
    note_data = [item.to_dict() for item in note]

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(note_data, file)


def load_knowledge(
    filename: Path = DEFAULT_FILE,
) -> list[KnowledgeItem]:
    try:
        with open(filename, "r", encoding="utf-8") as file:
            file_data = json.load(file)

        note: list[KnowledgeItem] = []

        for item in file_data:
            obj = KnowledgeItem.from_dict(item)
            note.append(obj)

        return note

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        raise DataCorruptionError("Failed to parse data")