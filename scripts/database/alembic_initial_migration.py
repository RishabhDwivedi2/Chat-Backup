# [AI]: This file implements an initial database migration using Alembic.
# It provides functionality to create and apply the first migration for the project's database schema.
# Key features:
# - Imports and sets up necessary models and configurations
# - Verifies database permissions
# - Creates and modifies the initial Alembic migration
# - Applies the migration to the database
# - Handles output formatting and logging

import sys
import io
from pathlib import Path
import importlib
import logging
import contextlib

from sqlalchemy import create_engine, inspect, text
from alembic import command
from alembic.config import Config
from colorama import Fore, Style, init
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext

# [AI]: Suppress SQLAlchemy warnings to reduce noise in the output
import warnings
from sqlalchemy import exc as sa_exc
warnings.filterwarnings('ignore', category=sa_exc.SAWarning)

# [AI]: Add the project root and backend directory to the Python path
# This ensures that imports from the app package work correctly
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.models.base import Base

# [AI]: Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# [AI]: Define color constants for different types of messages
INFO_COLOR = Fore.WHITE
SUCCESS_COLOR = Fore.GREEN
WARNING_COLOR = Fore.YELLOW
ERROR_COLOR = Fore.RED
HEADER_COLOR = Fore.MAGENTA

# [AI]: Helper functions for formatting and printing colored messages
def format_message(message: str, color: str) -> str:
    return f"{color}{message}{Style.RESET_ALL}"

def info(message: str) -> None:
    try:
        print(format_message(f"ℹ️ {message}", INFO_COLOR))
    except UnicodeEncodeError:
        print(format_message(f"i {message}", INFO_COLOR))

def success(message: str) -> None:
    try:
        print(format_message(f"✅ {message}", SUCCESS_COLOR))
    except UnicodeEncodeError:
        print(format_message(f"+ {message}", SUCCESS_COLOR))

def warning(message: str) -> None:
    try:
        print(format_message(f"⚠️ {message}", WARNING_COLOR))
    except UnicodeEncodeError:
        print(format_message(f"! {message}", WARNING_COLOR))

def error(message: str) -> None:
    try:
        print(format_message(f"❌ {message}", ERROR_COLOR))
    except UnicodeEncodeError:
        print(format_message(f"x {message}", ERROR_COLOR))

def header(message: str) -> None:
    print(f"\n{HEADER_COLOR}{message}")
    print("-" * len(message) + Style.RESET_ALL)

# [AI]: Context manager to suppress stdout temporarily
@contextlib.contextmanager
def suppress_stdout():
    save_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = save_stdout

# [AI]: Context manager to temporarily change Alembic's log level
@contextlib.contextmanager
def temporary_alembic_log_level(level):
    logger = logging.getLogger('alembic')
    original_level = logger.level
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(original_level)

# [AI]: Configure Alembic with project-specific settings
def get_alembic_config():
    alembic_cfg = Config(BACKEND_DIR / "alembic.ini")
    alembic_cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE.URL)
    
    # [AI]: Set up a custom logger for Alembic to minimize output
    logger = logging.getLogger('alembic')
    logger.setLevel(logging.ERROR)  # Only show ERROR and CRITICAL messages
    
    # Remove any existing handlers and add a NullHandler
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(logging.NullHandler())
    
    return alembic_cfg

# [AI]: Import all model files to ensure they're registered with SQLAlchemy
def import_all_models():
    models_path = BACKEND_DIR / "app" / "models"
    for model_file in models_path.glob("*.py"):
        if model_file.stem not in {"__init__", "base"}:
            importlib.import_module(f"app.models.{model_file.stem}")
    info("Models imported successfully.")

# [AI]: Verify that the database user has sufficient permissions
def verify_permissions(db_url):
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE alembic_test (id serial PRIMARY KEY)"))
            conn.execute(text("DROP TABLE alembic_test"))
        return True
    except Exception as e:
        error(f"Permission check failed: {e}")
        return False

# [AI]: Reset the Alembic version table to start fresh
def reset_alembic_version(db_url):
    engine = create_engine(db_url)
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))

# [AI]: Modify the generated migration script to handle custom enum types
def modify_migration_script():
    versions_dir = BACKEND_DIR / "alembic" / "versions"
    latest_script = max(versions_dir.glob("*.py"), key=lambda f: f.stat().st_mtime)
    
    with open(latest_script, "r") as file:
        content = file.read()
    
    modified_content = content.replace(
        "op.create_table('users',",
        "if not op.get_bind().dialect.has_type(op.get_bind(), 'gender_enum'):\n"
        "        op.execute(\"CREATE TYPE gender_enum AS ENUM ('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY')\")\n"
        "    op.create_table('users',"
    )
    
    with open(latest_script, "w") as file:
        file.write(modified_content)

# [AI]: Main function to create and apply the initial migration
def create_initial_migration(auto_confirm=False):
    print()  # Leave a line space before the warning
    warning("This is an initial migration. The database will be reset for a fresh start.")
    if not auto_confirm:
        user_input = input("Do you want to proceed? (yes/no): ").lower()
        if user_input != 'yes':
            info("Migration aborted.")
            return
    else:
        info("Auto-confirming migration...")

    if not verify_permissions(settings.DATABASE.URL):
        error("User does not have sufficient permissions. Please run create_new_database.py again.")
        sys.exit(1)

    header("Creating Initial Migration")

    info("Resetting Alembic version...")
    reset_alembic_version(settings.DATABASE.URL)

    info("Importing models...")
    import_all_models()

    alembic_cfg = get_alembic_config()

    try:
        info("Creating initial migration...")
        with capture_output() as (out, err):
            command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
        print(filter_alembic_output(out))
        print(filter_alembic_output(err), end='')  # Remove newline after this output

        info("Modifying migration script...")
        modify_migration_script()

        info("Applying migration...")
        with capture_output() as (out, err):
            command.upgrade(alembic_cfg, "head")
        print(filter_alembic_output(out), end='')  # Remove newline after this output
        print(filter_alembic_output(err), end='')  # Remove newline after this output

        success("Migration applied successfully.")
        print()  # Add a line space after the success message

    except Exception as e:
        error(f"Error in migration process: {str(e)}")
        sys.exit(1)

# [AI]: Context manager to capture stdout and stderr
@contextlib.contextmanager
def capture_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

# [AI]: Filter Alembic output to remove INFO messages
def filter_alembic_output(output):
    return '\n'.join(line for line in output.getvalue().splitlines() if not line.startswith("INFO"))

# [AI]: Main entry point of the script
if __name__ == "__main__":
    auto_confirm = len(sys.argv) > 1 and sys.argv[1] == '--yes'
    create_initial_migration(auto_confirm)