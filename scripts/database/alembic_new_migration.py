# [AI]: This file implements an Alembic migration management script.
# It provides functionality to check database status, generate and apply migrations.
# Key features:
# - Import all models dynamically
# - Check database migration status
# - Generate schema differences
# - Create new migrations
# - Apply migrations
# - User-friendly CLI interface with colored output

import sys
from pathlib import Path
import importlib
from sqlalchemy import create_engine, MetaData
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.autogenerate import compare_metadata
from colorama import Fore, Style, init
import io
import contextlib
import logging

# [AI]: Add project root and backend directory to Python path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.models.base import Base

# [AI]: Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# [AI]: Define color constants for consistent message formatting
INFO_COLOR = Fore.WHITE
SUCCESS_COLOR = Fore.GREEN
WARNING_COLOR = Fore.YELLOW
ERROR_COLOR = Fore.RED
HEADER_COLOR = Fore.MAGENTA

# [AI]: Helper functions for formatted console output
def format_message(message: str, color: str) -> str:
    return f"{color}{message}{Style.RESET_ALL}"

def info(message: str) -> None:
    print(format_message(f"ℹ️ {message}", INFO_COLOR))

def success(message: str) -> None:
    print(format_message(f"✅ {message}", SUCCESS_COLOR))

def warning(message: str) -> None:
    print(format_message(f"⚠️ {message}", WARNING_COLOR))

def error(message: str) -> None:
    print(format_message(f"❌ {message}", ERROR_COLOR))

def header(message: str) -> None:
    print()  # Add a line before the header
    print(f"{HEADER_COLOR}{message}")
    print(f"{HEADER_COLOR}{'-' * len(message)}{Style.RESET_ALL}")

def get_user_input(prompt: str) -> str:
    return input(format_message(prompt, WARNING_COLOR)).strip()

# [AI]: Configure Alembic with project-specific settings
def get_alembic_config():
    alembic_cfg = Config(BACKEND_DIR / "alembic.ini")
    alembic_cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE.URL)
    return alembic_cfg

# [AI]: Dynamically import all model files to ensure they're registered with SQLAlchemy
def import_all_models():
    models_path = BACKEND_DIR / "app" / "models"
    for model_file in models_path.glob("*.py"):
        if model_file.stem not in {"__init__", "base"}:
            module_name = f"app.models.{model_file.stem}"
            importlib.import_module(module_name)
            info(f"Imported {module_name}")
    success("Models imported successfully.")

# [AI]: Check if the database schema is up-to-date with the latest migration
def check_database_status(alembic_cfg):
    header("Checking database status")
    script = ScriptDirectory.from_config(alembic_cfg)
    engine = create_engine(settings.DATABASE.URL)
    
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_rev = context.get_current_revision()
    
    head_rev = script.get_current_head()
    
    if current_rev != head_rev:
        warning(f"Database is not up to date. Current: {current_rev}, Latest: {head_rev}")
        return False
    else:
        success("Database is up to date")
        return True

# [AI]: Generate and display differences between current database schema and models
def get_schema_diff(alembic_cfg):
    header("Generating schema diff")
    engine = create_engine(settings.DATABASE.URL)
    with engine.connect() as connection:
        with capture_output():  # Capture and discard the output
            context = MigrationContext.configure(connection)
            metadata = MetaData()
            metadata.reflect(engine)
            diff = compare_metadata(context, Base.metadata)
    
    if diff:
        info("Schema differences found:")
        for change in diff:
            if change[0] == 'add_table':
                info(f"  Add table: {change[1].name}")
            elif change[0] == 'remove_table':
                info(f"  Remove table: {change[1].name}")
            elif change[0] == 'add_column':
                info(f"  Add column: {change[2]}.{change[3]}")
            elif change[0] == 'remove_column':
                info(f"  Remove column: {change[2]}.{change[3]}")
            elif change[0] in ('modify_type', 'modify_nullable', 'modify_default'):
                info(f"  Modify column: {change[2]}.{change[3]} ({change[0]})")
            else:
                info(f"  Other change: {change}")
    else:
        warning("No schema differences found")

# [AI]: Generate a new Alembic migration based on detected schema changes
def generate_migration(alembic_cfg):
    header("Generating new migration")
    try:
        with capture_output() as (out, err):
            revision = command.revision(alembic_cfg, autogenerate=True, message="Auto migration")
        print(filter_alembic_output(out))
        print(filter_alembic_output(err), end='')
        if revision:
            success(f"New migration created: {revision.revision}")
            return revision
        else:
            warning("No new migration was created")
            return None
    except Exception as e:
        error(f"Failed to generate migration: {str(e)}")
        return None

# [AI]: Apply pending migrations to the database
def apply_migration(alembic_cfg):
    header("Applying migration")
    try:
        with capture_output() as (out, err):
            command.upgrade(alembic_cfg, "head")
        print(filter_alembic_output(out), end='')
        print(filter_alembic_output(err), end='')
        success("Migration applied successfully")
    except Exception as e:
        error(f"Failed to apply migration: {str(e)}")

# [AI]: Context manager to capture and return stdout and stderr
@contextlib.contextmanager
def capture_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

# [AI]: Filter Alembic output to remove unnecessary information
def filter_alembic_output(output):
    return '\n'.join(line for line in output.getvalue().splitlines() 
                     if not line.startswith("INFO") 
                     and "serial" not in line.lower() 
                     and "omitting" not in line.lower())

# [AI]: Main function to orchestrate the migration process
def main():
    # Set Alembic logging level to ERROR to reduce noise
    logging.getLogger('alembic').setLevel(logging.ERROR)

    header("Alembic Migration Process")
    import_all_models()
    alembic_cfg = get_alembic_config()

    is_up_to_date = check_database_status(alembic_cfg)
    get_schema_diff(alembic_cfg)

    # [AI]: Present options to the user
    print("Options:")
    print("1. Generate a new migration")
    print("2. Apply existing migrations")
    print("3. Exit")

    choice = get_user_input("\nEnter your choice (1/2/3): ")

    if choice == '1':
        if not is_up_to_date:
            warning("Database is not up to date. Updating to the latest migration before generating a new one.")
            apply_migration(alembic_cfg)
        
        new_revision = generate_migration(alembic_cfg)
        if new_revision:
            apply_choice = get_user_input("Do you want to apply this new migration? (y/n): ")
            if apply_choice.lower() == 'y':
                apply_migration(alembic_cfg)
            else:
                info("New migration created but not applied")
    elif choice == '2':
        apply_migration(alembic_cfg)
    elif choice == '3':
        info("Exiting without any changes")
    else:
        error("Invalid choice. Exiting.")
    
    print()  # Add a line break after the last print message

if __name__ == "__main__":
    main()