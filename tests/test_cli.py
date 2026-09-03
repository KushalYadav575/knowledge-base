import sys
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

import cli
from exceptions import (
    DataCorruptionError,
    ItemNotFoundError,
    StorageError,
    ValidationError,
)
from models import KnowledgeItem


@pytest.fixture
def sample_item():
    return KnowledgeItem(
        title="Python Testing",
        content="Learn how to break CLI apps with pytest",
        tags=["python", "testing"],
        category="Software",
        source="Documentation",
        created_at=date(2026, 1, 1),
        updated_at=date(2026, 1, 1),
        item_id="test-uuid-1234",
    )


@pytest.fixture
def run_cli(monkeypatch, capsys):
    def _run(args: list[str]):
        monkeypatch.setattr(sys, "argv", ["kb"] + args)
        cli.main()
        return capsys.readouterr()

    return _run


@pytest.mark.parametrize(
    "invalid_args",
    [
        [],
        ["add", "--title", "Only Title"],
        ["search", "python", "--field", "non_existent_field"],
    ],
)
def test_cli_argparse_errors(run_cli, invalid_args):
    with pytest.raises(SystemExit) as exc_info:
        run_cli(invalid_args)
    assert exc_info.value.code != 0


@pytest.mark.parametrize(
    "args, patch_target, side_effect, expected_error",
    [
        (
            ["add", "--title", "   ", "--content", "Valid content", "--tags", "test", "--category", "General", "--source", "Web"],
            "services.add_item",
            ValidationError("Title cannot be empty"),
            "Error: Title cannot be empty",
        ),
        (
            ["add", "--title", "Title", "--content", "Content", "--tags", "", "--category", "Cat", "--source", "Src"],
            "services.add_item",
            ValidationError("Tags cannot contain empty strings"),
            "Error: Tags cannot contain empty strings",
        ),
        (
            ["view", "non-existent-id"],
            "services.get_item",
            ItemNotFoundError("could not find an item with that id"),
            "Error: could not find an item with that id",
        ),
        (
            ["delete", "non-existent-id"],
            "services.delete_item",
            ItemNotFoundError("could not find an item with that id"),
            "Error: could not find an item with that id",
        ),
        (
            ["edit", "non-existent-id", "--title", "New Title"],
            "services.update_item",
            ItemNotFoundError("could not find an item with that id"),
            "Error: could not find an item with that id",
        ),
        (
            ["list"],
            "services.list_items",
            StorageError("No file found"),
            "Error: No file found",
        ),
        (
            ["search", "any_query"],
            "services.search_items",
            DataCorruptionError("Failed to parse data"),
            "Error: Failed to parse data",
        ),
    ],
)
def test_cli_handles_exceptions(run_cli, args, patch_target, side_effect, expected_error):
    with patch(patch_target, side_effect=side_effect):
        out = run_cli(args)
        assert expected_error in out.out


@pytest.mark.parametrize(
    "items_return, expected_outputs",
    [
        (
            [],
            ["You currently do not have any knowledge items."],
        ),
        (
            "USE_SAMPLE",
            ["Knowledge items:", "* Title: Python Testing", "Tags: python, testing", "Category: Software", "ID: test-uuid-1234"],
        ),
    ],
)
def test_list_command(run_cli, sample_item, items_return, expected_outputs):
    mock_data = [sample_item] if items_return == "USE_SAMPLE" else items_return
    with patch("services.list_items", return_value=mock_data):
        out = run_cli(["list"])
        for expected in expected_outputs:
            assert expected in out.out


@pytest.mark.parametrize(
    "args, search_return, expected_output, expected_field",
    [
        (["search", "Python"], {"test-uuid-1234"}, "Title: Python Testing", None),
        (["search", "nonexistentquery"], set(), "No matching knowledge items found.", None),
        (["search", "Software", "--field", "category"], {"test-uuid-1234"}, "Title: Python Testing", "category"),
    ],
)
def test_search_command(run_cli, sample_item, args, search_return, expected_output, expected_field):
    with patch("services.search_items", return_value=search_return) as mock_search, \
        patch("services.get_item", return_value=sample_item):
        out = run_cli(args)
        if expected_field:
            mock_search.assert_called_once_with(args[1], field=expected_field)
        assert expected_output in out.out


def test_add_command_success(run_cli):
    with patch("services.add_item") as mock_add:
        out = run_cli([
            "add",
            "--title", "Python Testing",
            "--content", "Learn how to break CLI apps with pytest",
            "--tags", "python", "testing",
            "--category", "Software",
            "--source", "Documentation",
        ])
        assert mock_add.called
        assert "Knowledge item 'Python Testing' successfully added." in out.out
        assert "ID:" in out.out


def test_view_command_success(run_cli, sample_item):
    with patch("services.get_item", return_value=sample_item):
        out = run_cli(["view", "test-uuid-1234"])
        assert "Title: Python Testing" in out.out
        assert "Content: Learn how to break CLI apps with pytest" in out.out
        assert "Tags: ['python', 'testing']" in out.out
        assert "Category: Software" in out.out
        assert "Source: Documentation" in out.out
        assert "ID: test-uuid-1234" in out.out


def test_delete_command_success(run_cli, sample_item):
    with patch("services.delete_item", return_value=sample_item) as mock_delete:
        out = run_cli(["delete", "test-uuid-1234"])
        mock_delete.assert_called_once_with("test-uuid-1234")
        assert "Knowledge item 'Python Testing' deleted successfully." in out.out


def test_edit_command_partial_update(run_cli, sample_item):
    updated_item = KnowledgeItem(
        title="Updated Title",
        content=sample_item.content,
        tags=sample_item.tags,
        category=sample_item.category,
        source=sample_item.source,
        created_at=sample_item.created_at,
        updated_at=date.today(),
        item_id=sample_item.item_id,
    )
    with patch("services.update_item", return_value=updated_item) as mock_update:
        out = run_cli(["edit", "test-uuid-1234", "--title", "Updated Title"])
        mock_update.assert_called_once_with(
            "test-uuid-1234",
            title="Updated Title",
            content=None,
            tags=None,
            category=None,
            source=None,
        )
        assert "Knowledge item 'Updated Title' updated successfully." in out.out


def test_stats_command_populated(run_cli):
    categories = {"Software": 2, "Books": 1}
    tags = MagicMock()
    tags.most_common.return_value = [("python", 2), ("testing", 1)]
    sources = {"Documentation": 3}

    with patch("services.get_stats", return_value=(3, categories, tags, sources)):
        out = run_cli(["stats"])
        assert "Knowledge Base Statistics" in out.out
        assert "Total items: 3" in out.out
        assert "Software: 2" in out.out
        assert "python: 2" in out.out
        assert "Documentation: 3" in out.out


def test_edit_command_no_arguments_passed(run_cli, sample_item):
    with patch("services.update_item", return_value=sample_item) as mock_update:
        out = run_cli(["edit", "test-uuid-1234"])
        mock_update.assert_called_once_with(
            "test-uuid-1234",
            title=None,
            content=None,
            tags=None,
            category=None,
            source=None,
        )
        assert "Knowledge item 'Python Testing' updated successfully." in out.out


def test_search_returns_id_that_disappears_before_fetch(run_cli):
    with patch("services.search_items", return_value={"stale-id"}), \
         patch("services.get_item", side_effect=ItemNotFoundError("could not find an item with that id")):
        out = run_cli(["search", "query"])
        assert "Error: could not find an item with that id" in out.out


def test_add_command_accepts_multiword_arguments(run_cli):
    with patch("services.add_item") as mock_add:
        out = run_cli([
            "add",
            "--title", "Design Patterns in Python",
            "--content", "Comprehensive guide to OOP patterns",
            "--tags", "design patterns", "software architecture",
            "--category", "Software Engineering",
            "--source", "O'Reilly Book",
        ])
        assert mock_add.called
        added_item = mock_add.call_args[0][0]
        assert added_item.title == "Design Patterns in Python"
        assert added_item.tags == ["design patterns", "software architecture"]
        assert added_item.category == "Software Engineering"
        assert added_item.source == "O'Reilly Book"
        assert "Knowledge item 'Design Patterns in Python' successfully added." in out.out