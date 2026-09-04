from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date


@dataclass
class KnowledgeItem:

    title: str
    content: str
    tags: list[str]
    category: str
    source: str
    created_at: date
    updated_at: date
    item_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        return f"{self.title} with id = {self.item_id} having tags {self.tags} created at {self.created_at}"


    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "category": self.category,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "item_id": self.item_id,
        }


    @classmethod
    def from_dict(cls, data: dict[str, object]) -> KnowledgeItem:
        return cls(
            data["title"],
            data["content"],
            data["tags"],
            data["category"],
            data["source"],
            date.fromisoformat(data["created_at"]),
            date.fromisoformat(data["updated_at"]),
            data["item_id"],
        )