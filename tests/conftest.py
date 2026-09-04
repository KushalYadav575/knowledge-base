import sys
from datetime import date, timedelta
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import pytest

from models import KnowledgeItem


@pytest.fixture
def today() -> date:
    """A fixed 'today' so tests aren't sensitive to when they run."""
    return date(2026, 1, 15)


@pytest.fixture
def make_item(today):
    """
    Factory fixture: call make_item() for a valid default KnowledgeItem,
    or make_item(title="Custom title") to override just what you need.

    Using a factory (a function) instead of a single fixed object means
    each test can build its own item without copy-pasting the same
    5-argument constructor call everywhere.
    """

    def _make_item(**overrides) -> KnowledgeItem:
        defaults = dict(
            title="Binary Search",
            content="A divide-and-conquer search algorithm on sorted data.",
            tags=["algorithms", "search"],
            category="Computer Science",
            source="CLRS textbook",
            created_at=today,
            updated_at=today,
        )
        defaults.update(overrides)
        return KnowledgeItem(**defaults)

    return _make_item


@pytest.fixture
def sample_item(make_item) -> KnowledgeItem:
    """A single ready-to-use valid KnowledgeItem."""
    return make_item()


@pytest.fixture
def sample_items(make_item, today):
    """A small list of varied items, handy for list/search/stats tests."""
    return [
        make_item(
            title="Binary Search",
            tags=["algorithms", "search"],
            category="Computer Science",
        ),
        make_item(
            title="Photosynthesis",
            content="How plants convert light into chemical energy.",
            tags=["biology", "plants"],
            category="Science",
            source="Campbell Biology",
        ),
        make_item(
            title="The French Revolution",
            content="A period of political upheaval in France, 1789-1799.",
            tags=["history", "europe"],
            category="History",
            source="Wikipedia",
            created_at=today - timedelta(days=1),
            updated_at=today,
        ),
    ]