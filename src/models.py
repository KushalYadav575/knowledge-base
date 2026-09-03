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

    def __str__(self):
        return f"{self.title} with id = {self.item_id} having tags {self.tags} created at {self.created_at}"