# Knowledge Base CLI

A local command-line app for storing, searching, importing, and exporting personal knowledge notes.

This project started as a way to practice building a real Python application beyond small scripts. It uses a layered structure with models, validation, storage, services, a command-line interface, custom exceptions, tests, linting, and packaging.

## What It Does

Knowledge Base CLI lets you save short knowledge items from the terminal.

Each item has:

- a title
- content
- tags
- a category
- a source
- created and updated dates
- a unique item ID

The app stores everything locally in a JSON file.

## Features

- Add new knowledge items
- View an item by ID
- List all saved items
- Edit existing items
- Delete items
- Search across all fields or a specific field
- View basic statistics
- Export data to JSON or CSV
- Import data from JSON or CSV
- Validation for knowledge item data
- Custom error handling
- Pytest test suite
- Ruff linting
- Installable command-line entry point with `kb`

## Project Structure

```text
knowledge-base/
├── data/
│   └── knowledge.json
├── src/
│   └── knowledge_base_cli/
│       ├── __init__.py
│       ├── cli.py
│       ├── exceptions.py
│       ├── models.py
│       ├── services.py
│       ├── storage.py
│       └── validators.py
├── tests/
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Installation

Clone the project:

```powershell
git clone https://github.com/KushalYadav575/knowledge-base.git
cd knowledge-base
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the project in editable mode:

```powershell
pip install -e .
```

After installation, the `kb` command should be available:

```powershell
kb --help
```

## Usage

### Add an Item

```powershell
kb add --title "Binary Search" --content "A search algorithm for sorted data." --tags algorithms search python --category "Computer Science" --source "CLRS"
```

### List Items

```powershell
kb list
```

### View an Item

```powershell
kb view <item_id>
```

### Edit an Item

```powershell
kb edit <item_id> --title "Updated Title"
```

You can also edit other fields:

```powershell
kb edit <item_id> --content "Updated content" --tags python cli testing --category "Programming" --source "Personal notes"
```

### Delete an Item

```powershell
kb delete <item_id>
```

### Search

Search across all fields:

```powershell
kb search python
```

Search inside a specific field:

```powershell
kb search python --field tags
```

Supported search fields:

```text
title
content
tags
category
source
created_at
updated_at
```

### View Statistics

```powershell
kb stats
```

This shows:

- total number of items
- category counts
- most used tags
- source counts

### Export Data

Export to JSON:

```powershell
kb export backup.json
```

Export to CSV:

```powershell
kb export backup.csv
```

### Import Data

Import from JSON:

```powershell
kb import backup.json
```

Import from CSV:

```powershell
kb import backup.csv
```

If imported items have the same ID as existing items, the app gives the imported item a new ID so the existing item is not overwritten.

## Development

Run the tests:

```powershell
pytest
```

Run Ruff:

```powershell
ruff check .
```

The project is currently expected to pass both:

```text
pytest
ruff check .
```

## Main Concepts Practiced

This project was built to practice core Python application skills:

- dataclasses
- type hints
- file handling
- JSON storage
- CSV import/export
- command-line interfaces with `argparse`
- validation
- custom exceptions
- service-layer design
- automated testing with `pytest`
- linting with Ruff
- Python packaging with `pyproject.toml`

## Notes

This app stores data locally. It does not use a database or cloud storage.

If the data file does not exist yet, the app treats that as an empty knowledge base.

The project is installable from source, but it is not published to PyPI.

That means users should install it from the project folder with:

```powershell
pip install -e .
```

not:

```powershell
pip install knowledge-base-cli
```

## License

This project is licensed under the terms in the `LICENSE` file.