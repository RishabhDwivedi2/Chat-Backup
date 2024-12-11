# [AI]: This file implements a database schema documentation generator.
# It provides functionality to scan Python files for SQLAlchemy models and generate a Markdown file with the database schema.
# Key features:
# - Automatic discovery of SQLAlchemy models in the project
# - Generation of a formatted Markdown file with table and column details
# - Colored console output for better readability
# - Error handling and logging

import sys
from pathlib import Path

# Add the project root and backend directory to the Python path
project_root = Path(__file__).resolve().parents[2]
backend_dir = project_root / 'backend'
sys.path.extend([str(project_root), str(backend_dir)])

import importlib
import inspect
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, ForeignKey
import logging
from colorama import Fore, Style, init
import traceback

# [AI]: Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# [AI]: Define color constants for consistent message formatting
INFO_COLOR = Fore.WHITE
SUCCESS_COLOR = Fore.GREEN
WARNING_COLOR = Fore.YELLOW
ERROR_COLOR = Fore.RED
PROMPT_COLOR = Fore.YELLOW

# [AI]: Helper functions for formatting colored messages
def format_message(message: str, color: str) -> str:
    """Format a message with the given color."""
    return f"{color}{message}{Style.RESET_ALL}"

def info_message(message: str) -> str:
    return format_message(message, INFO_COLOR)

def success_message(message: str) -> str:
    return format_message(message, SUCCESS_COLOR)

def warning_message(header: str, message: str) -> str:
    return f"{WARNING_COLOR}{header}{Style.RESET_ALL} {message}"

def error_message(message: str) -> str:
    return format_message(message, ERROR_COLOR)

def file_path_message(message: str) -> str:
    return format_message(message, INFO_COLOR)

# [AI]: Set up logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# [AI]: Function to check if a class is a SQLAlchemy model
def is_sqlalchemy_model(cls):
    return hasattr(cls, '__tablename__') and hasattr(cls, '__table__')

# [AI]: Main function to update the database schema documentation
def update_database_schema():
    print(info_message("\nStarting update_database_schema.py\n"))
    output_messages = []

    # Define paths for the models directory and output file
    models_dir = project_root / 'backend' / 'app' / 'models'
    output_file = project_root / 'workspace' / 'files' / 'database_schema.md'

    # Check if the models directory exists
    if not models_dir.exists():
        print(error_message(f"Models directory not found: {models_dir}"))
        output_messages.append(f"Models directory not found: {models_dir}")
        return False, output_messages

    models = {}  # Use a dictionary to prevent duplicate models

    print(info_message(f"Scanning directory: {models_dir}"))
    # Iterate through Python files in the models directory
    for file_path in models_dir.glob('*.py'):
        if file_path.name != '__init__.py':
            module_name = f"backend.app.models.{file_path.stem}"
            try:
                # Dynamically import the module and find SQLAlchemy models
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and is_sqlalchemy_model(obj):
                        if name not in models:
                            models[name] = obj
                            print(success_message(f"Found model: {name}"))
            except Exception as e:
                print(error_message(f"Error importing {file_path.name}:"))
                print(traceback.format_exc())
                output_messages.append(f"Error importing {file_path.name}:")
                output_messages.append(traceback.format_exc())

    if not models:
        error_msg = "No models found in any file"
        print(error_message(error_msg))
        output_messages.append(error_msg)
        return False, output_messages

    print(info_message("\nGenerating database schema documentation..."))
    output_messages.append("Generating database schema documentation...")

    # [AI]: Write the database schema documentation to the output file
    with open(output_file, 'w') as f:
        f.write("# Database Schema Documentation\n\n")
        f.write("This document provides detailed information about the database schema for the project.\n\n")
        f.write("## Table of Contents\n\n")

        # [AI]: Generate table of contents
        for model_name in models:
            f.write(f"- [{model_name}](#{model_name.lower()})\n")

        f.write("\n")

        # [AI]: Generate detailed information for each model
        for model_name, model in models.items():
            f.write(f"## {model_name}\n\n")
            f.write(f"Table name: `{model.__tablename__}`\n\n")
            f.write("| Column | Type | Constraints |\n")
            f.write("|--------|------|-------------|\n")

            # [AI]: Iterate through columns and document their properties
            for column in model.__table__.columns:
                constraints = []
                if column.primary_key:
                    constraints.append("PRIMARY KEY")
                if column.unique:
                    constraints.append("UNIQUE")
                if not column.nullable:
                    constraints.append("NOT NULL")
                if isinstance(column.type, ForeignKey):
                    constraints.append(f"FOREIGN KEY ({column.name}) REFERENCES {column.type.column.table.name}({column.type.column.name})")
                elif column.foreign_keys:
                    for fk in column.foreign_keys:
                        constraints.append(f"FOREIGN KEY ({fk.parent.name}) REFERENCES {fk.column.table.name}({fk.column.name})")
                
                f.write(f"| {column.name} | {column.type} | {', '.join(constraints)} |\n")

            f.write("\n")

    # [AI]: Print success message with the relative path of the output file
    relative_path = output_file.relative_to(project_root)
    print(f"{SUCCESS_COLOR}Updated:{Style.RESET_ALL} Database schema documentation in {file_path_message(str(relative_path))}")
    print(success_message("\nDatabase schema update completed successfully."))
    print()  # Add a final line break

    return True, output_messages

if __name__ == "__main__":
    success, messages = update_database_schema()
    if not success:
        sys.exit(1)

