import argparse
import datetime
from zoneinfo import ZoneInfo

import services
from exceptions import KnowledgeBaseError
from models import KnowledgeItem

parser = argparse.ArgumentParser(
    prog="kb",
    description="Personal knowledge base"
)

subparsers = parser.add_subparsers(
    dest="command",
    required=True,
)

add_parser = subparsers.add_parser(
    "add",
    help="Add a knowledge item",
)

add_parser.add_argument(
    "--title",
    required=True,
    help="Title of the knowledge item",
)

add_parser.add_argument(
    "--content",
    required=True,
    help="Content of the knowledge item",
)

add_parser.add_argument(
    "--tags",
    nargs="+",
    required=True,
    help="Tags for the knowledge item",
)

add_parser.add_argument(
    "--category",
    required=True,
    help="Category of the knowledge item",
)

add_parser.add_argument(
    "--source",
    required=True,
    help="Source of the knowledge item",
)

view_parser = subparsers.add_parser(
    "view",
    help="View a knowledge item"
)

view_parser.add_argument(
    "item_id",
    help="unique id of the knowledge item",
)

list_parser = subparsers.add_parser(
    "list",
    help="List knowledge items",
)

delete_parser = subparsers.add_parser(
    "delete",
    help="delete a knowledge item"
)

delete_parser.add_argument(
    "item_id",
    help="unique id of the knowledge item",
)

edit_parser = subparsers.add_parser(
    "edit",
    help="edit a knowledge item"
)

edit_parser.add_argument(
    "item_id",
    help="unique id of the knowledge item",
)

edit_parser.add_argument(
    "--title",
    help="Title of the knowledge item",
)

edit_parser.add_argument(
    "--content",
    help="Content of the knowledge item",
)

edit_parser.add_argument(
    "--tags",
    nargs="+",
    help="Tags for the knowledge item",
)

edit_parser.add_argument(
    "--category",
    help="Category of the knowledge item",
)

edit_parser.add_argument(
    "--source",
    help="Source of the knowledge item",
)

search_parser = subparsers.add_parser(
    "search",
    help="search knowledge item"
)

search_parser.add_argument(
    "query",
    help="Text to search for"
)

search_parser.add_argument(
    "--field",
    help="the field to search in",
    choices=[
        "title",
        "category",
        "content",
        "tags",
        "source",
        "created_at",
        "updated_at",
    ],
)

stats_parser = subparsers.add_parser(
    "stats",
    help="gives stats of all knowledge items",
)

export_parser = subparsers.add_parser(
    "export",
    help="export already existing knowledge data"
)

import_parser = subparsers.add_parser(
    "import",
    help="import already existing knowledge data"
)

export_parser.add_argument(
    "file_path",
    help="path to the file where the data is exported"
)

import_parser.add_argument(
    "file_path",
    help="the path of the file where the data to be imported is stored"
)

def add_command(args):
    today = datetime.datetime.now(tz=ZoneInfo("Asia/Kolkata")).date()

    knowledge = KnowledgeItem(
        title=args.title,
        category=args.category,
        content=args.content,
        tags=args.tags,
        source=args.source,
        created_at=today,
        updated_at=today,
)
    
    services.add_item(knowledge)
    
    print(f"Knowledge item '{knowledge.title}' successfully added.")
    print(f"ID: {knowledge.item_id}")


def view_command(args):
    knowledge = services.get_item(args.item_id)

    print(f"Title: {knowledge.title}")
    print(f"Content: {knowledge.content}")
    print(f"Tags: {knowledge.tags}")
    print(f"Category: {knowledge.category}")
    print(f"Source: {knowledge.source}")
    print(f"Created: {knowledge.created_at}")
    print(f"Updated: {knowledge.updated_at}")
    print(f"ID: {knowledge.item_id}")


def list_command(args):
    knowledge_item_list = services.list_items()
    if not knowledge_item_list:
        print("You currently do not have any knowledge items.")
    else:
        print("Knowledge items:\n")

        for knowledge in knowledge_item_list:
            print(f"* Title: {knowledge.title}")
            print(f"  Tags: {', '.join(knowledge.tags)}")
            print(f"  Category: {knowledge.category}")
            print(f"  ID: {knowledge.item_id}\n\n")


def delete_command(args):
    deleted_item = services.delete_item(args.item_id)
    print(f"Knowledge item '{deleted_item.title}' deleted successfully.")


def edit_command(args):
    updated_item = services.update_item(
        args.item_id,
        title=args.title,
        content=args.content,
        tags=args.tags,
        category=args.category,
        source=args.source,
    )

    print(f"Knowledge item '{updated_item.title}' updated successfully.")


def search_command(args):
    matches = services.search_items(
        args.query,
        field=args.field
    )

    if not matches:
        print("No matching knowledge items found.")
        return

    for item_id in matches:
        item = services.get_item(item_id)
        print(f"Title: {item.title}")
        print(f"ID: {item.item_id}")
        print()


def stats_command(args):
    total_items, categories, tags, sources = services.get_stats()
    print("Knowledge Base Statistics\n")
    print(f"Total items: {total_items}\n")
    print("Categories:")
    for key, value in categories.items():
        print(f"  {key}: {value}")
    print(" ")
    print("Most used tags:")
    for key, value in tags.most_common(3):
        print(f"  {key}: {value}")
    print(" ")
    print("Sources:")
    for key, value in sources.items():
        print(f"  {key}: {value}")


def export_command(args):
    services.export_items(args.file_path)
    print(f"your data has been exported to {args.file_path}")


def import_command(args):
    services.import_items(args.file_path)
    print(f"your data has been imported to {args.file_path}")


add_parser.set_defaults(func=add_command)
view_parser.set_defaults(func=view_command)
list_parser.set_defaults(func=list_command)
delete_parser.set_defaults(func=delete_command)
edit_parser.set_defaults(func=edit_command)
search_parser.set_defaults(func=search_command)
stats_parser.set_defaults(func=stats_command)
export_parser.set_defaults(func=export_command)
import_parser.set_defaults(func=import_command)


def main():
    args = parser.parse_args()
    try:
        args.func(args)
    except KnowledgeBaseError as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()