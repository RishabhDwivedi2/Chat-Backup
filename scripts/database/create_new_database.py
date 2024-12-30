# [AI]: This file implements a database and user setup script for a PostgreSQL database.
# It provides functionality to create a new database, create a new user, and grant privileges.
# Key features:
# - Interactive prompts for database name, username, and passwords
# - Automatic creation of database and user if they don't exist
# - Granting of privileges to the new user on the new database
# - Configuration file updates with new database details
# - Colored console output for better readability
# - Error handling and logging

import sys
from pathlib import Path

# [AI]: Add the project root to the system path to allow imports from the backend
PROJECT_ROOT = Path(__file__).parents[2]
sys.path.append(str(PROJECT_ROOT))

from backend.app.config.constants import settings

import asyncio
import asyncpg
import logging
import toml
from colorama import Fore, Style, init
from typing import Dict, Tuple
import getpass

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

def prompt_message(message: str) -> str:
    return format_message(message, PROMPT_COLOR)

def success_message_with_white_text(header: str, message: str) -> str:
    return f"{SUCCESS_COLOR}{header}{Style.RESET_ALL} {message}"

# [AI]: Set up logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MAX_PASSWORD_ATTEMPTS = 3

def get_input_with_default(prompt: str, default: str) -> str:
    user_input = input(prompt_message(f"{prompt} (default: {default}): ")).strip()
    if not user_input:
        print(info_message(f"Using default: {default}"))
        return default
    print(info_message(f"Using: {user_input}"))
    return user_input

def get_password_input(prompt: str) -> str:
    password = getpass.getpass(prompt_message(f"{prompt}: ")).strip()
    print(info_message(f"Password entered: {password}"))
    return password

async def get_db_config() -> Tuple[Dict[str, str], str]:
    host = get_input_with_default("Enter database host", settings.get('DATABASE.HOST', 'localhost'))
    port = get_input_with_default("Enter database port", str(settings.get('DATABASE.PORT', 5432)))
    admin_user = get_input_with_default("Enter admin username", settings.get('DATABASE.ADMIN_USER', 'postgres'))
    admin_password = settings.get('DATABASE.ADMIN_PASSWORD')
    if not admin_password:
        admin_password = get_password_input("Enter the admin password to grant privileges")
    else:
        print(info_message(f"Using admin password from settings: {admin_password}"))

    db_config = {
        'host': host,
        'port': int(port),
        'user': admin_user,
        'password': admin_password,
    }
    return db_config, admin_password

async def test_connection(config: Dict[str, str]) -> bool:
    try:
        conn = await asyncpg.connect(**config)
        await conn.close()
        return True
    except asyncpg.PostgresError as e:
        print(error_message(f"Connection test failed: {e}"))
        return False

async def get_postgres_version(conn):
    version = await conn.fetchval("SHOW server_version")
    return version

async def create_database_and_user(pool, NAME: str, new_user: str, new_password: str, admin_password: str):
    try:
        async with pool.acquire() as conn:
            # Check PostgreSQL version
            pg_version = await get_postgres_version(conn)
            print(info_message(f"PostgreSQL version: {pg_version}"))

            # Check if database exists
            exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", NAME)
            if not exists:
                await conn.execute(f'CREATE DATABASE "{NAME}"')
                print(success_message(f"Database '{NAME}' created successfully."))
            else:
                print(warning_message("Warning:", f"Database '{NAME}' already exists."))

            # Check if user exists
            exists = await conn.fetchval("SELECT 1 FROM pg_roles WHERE rolname = $1", new_user)
            if not exists:
                await conn.execute(f"CREATE USER \"{new_user}\" WITH PASSWORD '{new_password}'")
                print(success_message(f"User '{new_user}' created successfully."))
            else:
                await conn.execute(f"ALTER USER \"{new_user}\" WITH PASSWORD '{new_password}'")
                print(warning_message("Warning:", f"User '{new_user}' already exists. Password updated."))

            # Grant initial privileges
            await conn.execute(f'GRANT ALL PRIVILEGES ON DATABASE "{NAME}" TO "{new_user}"')
            await conn.execute(f'ALTER USER "{new_user}" WITH LOGIN')

        # Connect to the new database to set schema-level permissions
        db_config = {
            'host': settings.get('DATABASE.HOST', 'localhost'),
            'port': settings.get('DATABASE.PORT', 5432),
            'user': settings.get('DATABASE.ADMIN_USER', 'postgres'),
            'password': admin_password,
            'database': NAME
        }
        print(info_message(f"Connecting to new database '{NAME}' as admin to set schema permissions..."))
        
        if not await test_connection(db_config):
            raise asyncpg.PostgresError("Failed to connect to the new database as admin.")

        async with asyncpg.create_pool(**db_config) as new_pool:
            async with new_pool.acquire() as new_conn:
                # Grant comprehensive schema privileges
                schema_privileges_sql = [
                    f'GRANT ALL PRIVILEGES ON DATABASE "{NAME}" TO "{new_user}"',
                    f'GRANT ALL PRIVILEGES ON SCHEMA public TO "{new_user}"',
                    f'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "{new_user}"',
                    f'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "{new_user}"',
                    f'GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO "{new_user}"',
                    f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "{new_user}"',
                    f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "{new_user}"',
                    f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO "{new_user}"',
                    f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO "{new_user}"',
                    f'ALTER USER "{new_user}" WITH CREATEDB',
                ]
                for sql in schema_privileges_sql:
                    await new_conn.execute(sql)
        print(success_message_with_white_text("Granted:", f"Comprehensive privileges to '{new_user}' on database '{NAME}'."))

    except asyncpg.PostgresError as error:
        print(error_message(f"PostgreSQL Error: {error}"))
        logger.error(f"PostgreSQL Error in create_database_and_user: {error}")
        raise
    except Exception as error:
        print(error_message(f"Unexpected Error: {error}"))
        logger.error(f"Unexpected error in create_database_and_user: {error}", exc_info=True)
        raise

async def grant_additional_privileges(pool, NAME: str, new_user: str):
    try:
        async with pool.acquire() as conn:
            additional_privileges_sql = [
                f'GRANT ALL PRIVILEGES ON DATABASE "{NAME}" TO "{new_user}"',
                f'GRANT ALL PRIVILEGES ON SCHEMA public TO "{new_user}"',
                f'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "{new_user}"',
                f'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "{new_user}"',
                f'GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO "{new_user}"',
                f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "{new_user}"',
                f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "{new_user}"',
                f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO "{new_user}"',
                f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO "{new_user}"',
            ]
            for sql in additional_privileges_sql:
                await conn.execute(sql)
        print(success_message_with_white_text("Granted:", f"Additional schema privileges to '{new_user}' on database '{NAME}'."))
    except asyncpg.PostgresError as error:
        print(error_message(f"Failed to grant additional privileges: {error}"))
        raise

def update_config(updates: Dict[str, str]):
    # [AI]: Update configuration files with new database details
    try:
        settings_path = PROJECT_ROOT / 'backend' / 'config' / 'settings.lcl.toml'
        secrets_path = PROJECT_ROOT / 'backend' / 'config' / '.secrets.lcl.toml'

        # [AI]: Load existing configurations
        with open(settings_path, 'r') as f:
            settings_config = toml.load(f)
        with open(secrets_path, 'r') as f:
            secrets_config = toml.load(f)

        # [AI]: Update configurations with new values
        for key, value in updates.items():
            if key in ['DATABASE.ADMIN_PASSWORD', 'DATABASE.USER_PASSWORD']:
                secrets_config['DATABASE'][key.split('.')[-1]] = value
            else:
                settings_config['DATABASE'][key.split('.')[-1]] = value

        # [AI]: Write updated configurations back to files
        with open(settings_path, 'w') as f:
            toml.dump(settings_config, f)
        with open(secrets_path, 'w') as f:
            toml.dump(secrets_config, f)

        # [AI]: Update runtime settings
        for key, value in updates.items():
            settings.set(key, value)

        print(success_message_with_white_text("Updated:", "Configuration successfully."))
    except Exception as e:
        print(error_message(f"Error updating configuration: {e}"))

async def main():
    print(success_message("\nStarting database and user setup..."))

    # Generate suggested database name and username based on project settings
    project_name = settings.PROJECT.NAME.lower()
    env = settings.ENV.APP_ENV.lower()
    suggested_name = f"{project_name}_{env}_db"
    suggested_user = f"{project_name}_{env}_user"

    # Prompt user for database name, username, and password
    NAME = get_input_with_default("Enter the new database name", suggested_name)
    new_user = get_input_with_default("Enter the new username", suggested_user)
    new_password = get_password_input("Enter the password for the new user")

    try:
        # Get database configuration and test connection
        db_config, admin_password = await get_db_config()
        print(info_message("\nTesting connection to PostgreSQL server..."))
        
        connection_attempts = 0
        while connection_attempts < MAX_PASSWORD_ATTEMPTS:
            if await test_connection(db_config):
                break
            connection_attempts += 1
            if connection_attempts < MAX_PASSWORD_ATTEMPTS:
                print(error_message(f"Connection attempt {connection_attempts} failed. Retrying..."))
                db_config['password'] = get_password_input(f"Re-enter admin password")
            else:
                raise Exception("Failed to connect to PostgreSQL server after multiple attempts. Please check your admin credentials.")

        print(info_message("Connection successful. Proceeding with database and user setup..."))
        
        async with asyncpg.create_pool(**db_config) as pool:
            await create_database_and_user(pool, NAME, new_user, new_password, admin_password)
            await grant_additional_privileges(pool, NAME, new_user)
        
        # Update configuration files with new database details
        update_config({
            'DATABASE.HOST': db_config['host'],
            'DATABASE.PORT': db_config['port'],
            'DATABASE.ADMIN_USER': db_config['user'],
            'DATABASE.ADMIN_PASSWORD': admin_password,
            'DATABASE.NAME': NAME,
            'DATABASE.USER_NAME': new_user,
            'DATABASE.USER_PASSWORD': new_password
        })
        
        print(success_message_with_white_text("Success:", f"Database '{NAME}' and user '{new_user}' setup completed successfully.\n"))
    except Exception as error:
        print(error_message(f"Error: {error}\n"))
        logger.error(f"Error in main function: {error}", exc_info=True)
        print(error_message("Setup failed. Please check the error messages above and try again."))
    else:
        print(info_message("All operations completed successfully."))
    finally:
        print(info_message("Script execution finished."))

if __name__ == "__main__":
    # [AI]: Remove debug logging for asyncio
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    # [AI]: Set event loop policy for Windows compatibility
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())