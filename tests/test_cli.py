import argparse
from collections import Counter

import pytest

import cli
import services
from exceptions import ItemNotFoundError
from models import KnowledgeItem


class TestArgumentParsing:
    def test_add_requires_all_flags(self):
        args = cli.parser.parse_args([
            "add",
            "--title", "T",
            "--content", "C",
            "--tags", "a", "b",
            "--category", "Cat",
            "--source", "Src",
        ])
        assert args.title == "T"
        assert args.tags == ["a", "b"]
        assert args.func == cli.add_command

    @pytest.mark.parametrize(
        "missing_flag",
        ["--title", "--content", "--tags", "--category", "--source"],
    )
    def test_add_fails_without_each_required_flag(self, missing_flag):
        full_args = [
            "add",
            "--title", "T",
            "--content", "C",
            "--tags", "a",
            "--category", "Cat",
            "--source", "Src",
        ]
        idx = full_args.index(missing_flag)
        args_without_flag = full_args[:idx] + full_args[idx + 2:]

        with pytest.raises(SystemExit):
            cli.parser.parse_args(args_without_flag)

    def test_view_requires_item_id(self):
        with pytest.raises(SystemExit):
            cli.parser.parse_args(["view"])

    def test_view_parses_item_id(self):
        args = cli.parser.parse_args(["view", "abc-123"])
        assert args.item_id == "abc-123"

    def test_list_needs_no_extra_args(self):
        args = cli.parser.parse_args(["list"])
        assert args.func == cli.list_command

    def test_stats_needs_no_extra_args(self):
        args = cli.parser.parse_args(["stats"])
        assert args.func == cli.stats_command

    def test_search_rejects_invalid_field_choice(self):
        with pytest.raises(SystemExit):
            cli.parser.parse_args(["search", "python", "--field", "not-a-real-field"])

    def test_search_accepts_valid_field_choice(self):
        args = cli.parser.parse_args(["search", "python", "--field", "title"])
        assert args.query == "python"
        assert args.field == "title"

    def test_search_field_is_optional(self):
        args = cli.parser.parse_args(["search", "python"])
        assert args.field is None

    def test_no_command_at_all_is_rejected(self):
        with pytest.raises(SystemExit):
            cli.parser.parse_args([])

    def test_export_requires_file_path(self):
        with pytest.raises(SystemExit):
            cli.parser.parse_args(["export"])

    def test_export_parses_file_path(self):
        args = cli.parser.parse_args(["export", "backup.json"])
        assert args.file_path == "backup.json"

    def test_import_requires_file_path(self):
        with pytest.raises(SystemExit):
            cli.parser.parse_args(["import"])

    def test_import_parses_file_path(self):
        args = cli.parser.parse_args(["import", "backup.json"])
        assert args.file_path == "backup.json"
        assert args.func == cli.import_command


@pytest.fixture
def item(make_item):
    return make_item(title="Binary Search")


class TestAddCommand:
    def test_prints_title_and_id(self, monkeypatch, capsys):
        monkeypatch.setattr(services, "add_item", lambda knowledge: None)
        args = argparse.Namespace(
            title="Binary Search",
            content="A search algorithm",
            tags=["algorithms"],
            category="CS",
            source="textbook",
        )

        cli.add_command(args)

        out = capsys.readouterr().out
        assert "Binary Search" in out
        assert "ID:" in out

    def test_calls_services_add_item_once(self, monkeypatch, capsys):
        calls = []
        monkeypatch.setattr(services, "add_item", lambda knowledge: calls.append(knowledge))
        args = argparse.Namespace(
            title="T", content="C", tags=["x"], category="Cat", source="Src",
        )

        cli.add_command(args)

        assert len(calls) == 1
        assert isinstance(calls[0], KnowledgeItem)
        assert calls[0].title == "T"


class TestViewCommand:
    def test_prints_all_fields(self, monkeypatch, capsys, item):
        monkeypatch.setattr(services, "get_item", lambda item_id: item)
        args = argparse.Namespace(item_id=item.item_id)

        cli.view_command(args)

        out = capsys.readouterr().out
        assert item.title in out
        assert item.content in out
        assert item.item_id in out


class TestListCommand:
    def test_empty_list_prints_friendly_message(self, monkeypatch, capsys):
        monkeypatch.setattr(services, "list_items", lambda: [])

        cli.list_command(argparse.Namespace())

        out = capsys.readouterr().out
        assert "do not have any knowledge items" in out

    def test_nonempty_list_prints_each_title(self, monkeypatch, capsys, sample_items):
        monkeypatch.setattr(services, "list_items", lambda: sample_items)

        cli.list_command(argparse.Namespace())

        out = capsys.readouterr().out
        for expected_item in sample_items:
            assert expected_item.title in out


class TestDeleteCommand:
    def test_prints_deleted_title(self, monkeypatch, capsys, item):
        monkeypatch.setattr(services, "delete_item", lambda item_id: item)
        args = argparse.Namespace(item_id=item.item_id)

        cli.delete_command(args)

        out = capsys.readouterr().out
        assert item.title in out
        assert "deleted" in out.lower()


class TestEditCommand:
    def test_prints_updated_title(self, monkeypatch, capsys, item):
        monkeypatch.setattr(
            services, "update_item",
            lambda item_id, title, content, tags, category, source: item,
        )
        args = argparse.Namespace(
            item_id=item.item_id, title="New Title",
            content=None, tags=None, category=None, source=None,
        )

        cli.edit_command(args)

        out = capsys.readouterr().out
        assert "updated" in out.lower()


class TestSearchCommand:
    def test_no_matches_prints_friendly_message(self, monkeypatch, capsys):
        monkeypatch.setattr(services, "search_items", lambda query, field: set())
        args = argparse.Namespace(query="nothing", field=None)

        cli.search_command(args)

        out = capsys.readouterr().out
        assert "No matching" in out

    def test_matches_print_each_title(self, monkeypatch, capsys, item):
        monkeypatch.setattr(services, "search_items", lambda query, field: {item.item_id})
        monkeypatch.setattr(services, "get_item", lambda item_id: item)
        args = argparse.Namespace(query="binary", field=None)

        cli.search_command(args)

        out = capsys.readouterr().out
        assert item.title in out


class TestStatsCommand:
    def test_prints_all_sections(self, monkeypatch, capsys):
        monkeypatch.setattr(
            services, "get_stats",
            lambda: (
                3,
                Counter({"CS": 2, "History": 1}),
                Counter({"algorithms": 2, "history": 1, "search": 1}),
                Counter({"textbook": 3}),
            ),
        )

        cli.stats_command(argparse.Namespace())

        out = capsys.readouterr().out
        assert "Total items: 3" in out
        assert "Categories:" in out
        assert "Most used tags:" in out
        assert "Sources:" in out

    def test_only_shows_top_3_tags(self, monkeypatch, capsys):
        monkeypatch.setattr(
            services, "get_stats",
            lambda: (
                1,
                Counter(),
                Counter({"a": 5, "b": 4, "c": 3, "d": 2, "e": 1}),
                Counter(),
            ),
        )

        cli.stats_command(argparse.Namespace())

        out = capsys.readouterr().out
        assert "a: 5" in out
        assert "d: 2" not in out
        assert "e: 1" not in out


class TestExportCommand:
    def test_prints_export_confirmation(self, monkeypatch, capsys):
        monkeypatch.setattr(services, "export_items", lambda file_path: None)
        args = argparse.Namespace(file_path="backup.json")

        cli.export_command(args)

        out = capsys.readouterr().out
        assert "backup.json" in out

    def test_calls_services_export_items_with_file_path(self, monkeypatch, capsys):
        calls = []
        monkeypatch.setattr(services, "export_items", lambda file_path: calls.append(file_path))
        args = argparse.Namespace(file_path="backup.json")

        cli.export_command(args)

        assert calls == ["backup.json"]


class TestImportCommand:
    def test_prints_import_confirmation(self, monkeypatch, capsys):
        monkeypatch.setattr(services, "import_items", lambda file_path: None)
        args = argparse.Namespace(file_path="backup.json")

        cli.import_command(args)

        out = capsys.readouterr().out
        assert "backup.json" in out

    def test_calls_services_import_items_with_file_path(self, monkeypatch, capsys):
        calls = []
        monkeypatch.setattr(services, "import_items", lambda file_path: calls.append(file_path))
        args = argparse.Namespace(file_path="backup.json")

        cli.import_command(args)

        assert calls == ["backup.json"]


class TestMain:
    def test_knowledge_base_error_is_caught_and_printed(self, monkeypatch, capsys):
        def raise_not_found(item_id):
            raise ItemNotFoundError("could not find an item with that id")

        monkeypatch.setattr(services, "get_item", raise_not_found)
        monkeypatch.setattr("sys.argv", ["kb", "view", "no-such-id"])

        cli.main()

        out = capsys.readouterr().out
        assert "Error:" in out
        assert "could not find an item with that id" in out

    def test_non_knowledge_base_errors_still_propagate(self, monkeypatch):
        def raise_type_error(item_id):
            raise TypeError("something unrelated went wrong")

        monkeypatch.setattr(services, "get_item", raise_type_error)
        monkeypatch.setattr("sys.argv", ["kb", "view", "no-such-id"])

        with pytest.raises(TypeError):
            cli.main()