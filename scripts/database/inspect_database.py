# [AI]: This file implements a database inspection tool for PostgreSQL databases.
# It provides functionality to examine database structure and metadata.
# Key features:
# - Inspect tables, columns, indexes, and foreign keys
# - Check all schemas in the database
# - Verify Alembic migration history
# - Check for custom enum types
# - Colorized output for better readability

import sys
from pathlib import Path

# [AI]: Add project root and backend directory to Python path for imports
PROJECT_ROOT = Path(__file__).parents[2]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "backend"))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError
from colorama import Fore, Style, init
from app.config import settings

# [AI]: Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# [AI]: Define color constants for various output types
INFO_COLOR = Fore.GREEN
SUCCESS_COLOR = Fore.GREEN
WARNING_COLOR = Fore.YELLOW
ERROR_COLOR = Fore.RED
HEADER_COLOR = Fore.MAGENTA + Style.BRIGHT
SUBHEADER_COLOR = Fore.BLUE + Style.BRIGHT
TABLE_COLOR = Fore.WHITE + Style.BRIGHT
COLUMN_COLOR = Fore.WHITE
VERSION_COLOR = Fore.WHITE
ENUM_COLOR = Fore.WHITE
BULLET_COLOR = Fore.WHITE

# [AI]: Helper functions for formatting and printing colored messages
def format_message(message: str, color: str) -> str:
    return f"{color}{message}{Style.RESET_ALL}"

def info(message: str) -> None:
    print(format_message(message, INFO_COLOR))

def success(message: str) -> None:
    print(format_message(message, SUCCESS_COLOR))

def warning(message: str) -> None:
    print(format_message(message, WARNING_COLOR))

def error(message: str) -> None:
    print(format_message(message, ERROR_COLOR))

def header(message: str, color=HEADER_COLOR) -> None:
    print("\n" + format_message(f"{message}", color))

def subheader(message: str) -> None:
    print(format_message(f"  {message}", SUBHEADER_COLOR))

# [AI]: Set up database connection using SQLAlchemy
engine = create_engine(settings.DATABASE.URL)
inspector = inspect(engine)

def inspect_database():
    """
    [AI]: Main function to perform database inspection.
    It checks tables, columns, indexes, foreign keys, schemas, Alembic history, and enum types.
    """
    header("Starting database inspection", SUCCESS_COLOR)
    try:
        table_names = inspector.get_table_names()
        if not table_names:
            warning("No tables found in the database.")
        else:
            header("Tables in the database")
            for table in table_names:
                print(format_message(f"  • {table}", BULLET_COLOR))
            print()
            for table_name in table_names:
                print(format_message(f"{table_name}", TABLE_COLOR))
                columns = inspector.get_columns(table_name)
                subheader("Columns:")
                for column in columns:
                    print(format_message(f"    • {column['name']} ({column['type']})", COLUMN_COLOR))
                indexes = inspector.get_indexes(table_name)
                if indexes:
                    subheader("Indexes:")
                    for index in indexes:
                        print(format_message(f"    • {index['name']}: {index['column_names']}", BULLET_COLOR))
                else:
                    warning("  No indexes found.")
                foreign_keys = inspector.get_foreign_keys(table_name)
                if foreign_keys:
                    subheader("Foreign Keys:")
                    for fk in foreign_keys:
                        print(format_message(f"    • {fk['name']}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}", BULLET_COLOR))
                else:
                    warning("  No foreign keys found.")
                print()
            check_all_schemas()
            check_alembic_history()
            check_enum_types()
        header("Database inspection completed", SUCCESS_COLOR)
    except SQLAlchemyError as e:
        error(f"An error occurred during database inspection: {str(e)}")
    print()  # Add a line break after the final print message

def check_all_schemas():
    """
    [AI]: Check and display all non-system schemas in the database.
    """
    header("Checking all schemas in the database")
    try:
        with engine.connect() as connection:
            # [AI]: Query to get all non-system schemas
            schemas = connection.execute(text("SELECT nspname FROM pg_namespace WHERE nspname !~ '^pg_' AND nspname != 'information_schema'"))
            for schema in schemas:
                schema_name = schema[0]
                subheader(f"Schema: {schema_name}")
                tables = inspector.get_table_names(schema=schema_name)
                if tables:
                    for table in tables:
                        print(format_message(f"    • {table}", BULLET_COLOR))
                else:
                    warning(f"    No tables in schema {schema_name}")
    except SQLAlchemyError as e:
        error(f"An error occurred while checking schemas: {str(e)}")

def check_alembic_history():
    """
    [AI]: Check and display Alembic migration history from the database.
    """
    header("Checking Alembic migration history")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            versions = result.fetchall()
            if versions:
                for row in versions:
                    print(format_message(f"  Version: {row.version_num}", VERSION_COLOR))
            else:
                warning("  No Alembic versions found in the database.")
    except SQLAlchemyError as e:
        error(f"An error occurred while checking Alembic history: {str(e)}")

def check_enum_types():
    """
    [AI]: Check for custom enum types in the database, specifically looking for 'gender_enum'.
    """
    header("Checking custom enum types")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT typname FROM pg_type WHERE typtype = 'e'"))
            enum_types = [row[0] for row in result]
            if 'gender_enum' in enum_types:
                print(format_message("  gender_enum type exists", ENUM_COLOR))
            else:
                warning("  gender_enum type does not exist")
    except SQLAlchemyError as e:
        error(f"An error occurred while checking enum types: {str(e)}")

if __name__ == "__main__":
    inspect_database()