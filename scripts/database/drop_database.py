# [AI]: This file implements a database and user management system for PostgreSQL.
# It provides functionality to list, drop databases, and manage users.
# Key features:
# - Interactive command-line interface
# - Database listing and dropping
# - User listing and management
# - Colored output for better readability
# - Error handling and logging

import sys
from pathlib import Path
import asyncio
import asyncpg
import logging
from typing import List, Tuple
from datetime import datetime
from colorama import Fore, Style, init

# [AI]: Add the project root to the system path to allow imports from the backend
PROJECT_ROOT = Path(__file__).parents[2]
sys.path.append(str(PROJECT_ROOT))

from backend.app.config import settings

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

# [AI]: Set up logging for the application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# [AI]: Retrieve database configuration from settings
async def get_db_config() -> dict:
    admin_password = settings.get('DATABASE.ADMIN_PASSWORD')
    if not admin_password:
        print(error_message("Admin password not found in settings."))
        print(warning_message("Warning:", f"Please update the admin password in the settings for the '{settings.get('ENV.APP_ENV', 'lcl')}' environment and run this script again."))
        sys.exit(1)
    
    return {
        'host': settings.get('DATABASE.HOST', 'localhost'),
        'port': settings.get('DATABASE.PORT', 5432),
        'user': settings.get('DATABASE.ADMIN_USER', 'postgres'),
        'password': admin_password,
    }

# [AI]: Query the database to list all non-template databases
async def list_databases(conn) -> List[tuple]:
    query = """
    SELECT d.datname, pg_size_pretty(pg_database_size(d.datname)) as size
    FROM pg_database d
    WHERE datistemplate = false
    ORDER BY d.datname;
    """
    return await conn.fetch(query)

# [AI]: Query the database to list all users (roles that can login)
async def list_users(conn) -> List[tuple]:
    query = """
    SELECT r.rolname
    FROM pg_roles r
    WHERE r.rolcanlogin = true AND r.rolname != 'postgres'
    ORDER BY r.rolname;
    """
    return await conn.fetch(query)

# [AI]: Drop a user and revoke their privileges
async def drop_user(conn, username: str):
    try:
        quoted_username = f'"{username}"'
        new_owner = 'postgres'  # Change as needed

        # Reassign all owned objects to the new owner
        await conn.execute(f"REASSIGN OWNED BY {quoted_username} TO {new_owner};")
        logger.info(f"Reassigned all owned objects from user '{username}' to '{new_owner}'.")

        # Drop all privileges and owned objects by the user
        await conn.execute(f"DROP OWNED BY {quoted_username};")
        logger.info(f"Dropped all privileges and owned objects of user '{username}'.")

        # Drop the user role
        await conn.execute(f"DROP USER IF EXISTS {quoted_username};")
        print(success_message(f"User '{username}' has been successfully dropped."))

        return True
    except Exception as error:
        print(error_message(f"Error while dropping user {username}: {error}"))
        logger.error(f"Failed to drop user '{username}': {error}")
        return False

# [AI]: Get all databases owned by a specific user
async def get_user_databases(conn, username: str) -> List[str]:
    return [row['datname'] for row in await conn.fetch("""
        SELECT datname FROM pg_database
        WHERE datdba = (SELECT oid FROM pg_roles WHERE rolname = $1);
    """, username)]

# [AI]: Drop a specific database
async def drop_database(conn, dbname: str):
    try:
        quoted_dbname = f'"{dbname}"'
        await conn.execute(f"DROP DATABASE IF EXISTS {quoted_dbname}")
        print(success_message(f"Database '{dbname}' has been successfully dropped."))
        return True
    except Exception as error:
        print(error_message(f"Error while dropping database {dbname}: {error}"))
        return False

# [AI]: Print the list of available databases
async def print_available_databases(databases: List[tuple]):
    print(info_message("\nAvailable databases:"))
    for i, db in enumerate(databases, 1):
        print(info_message(f"{i}. {db['datname']} (Size: {db['size']})"))

# [AI]: Print the list of existing users
async def print_available_users(users: List[tuple]):
    print(info_message("\nExisting users:"))
    for i, user in enumerate(users, 1):
        print(info_message(f"{i}. {user['rolname']}"))

# [AI]: Main function to handle the interactive CLI
async def main():
    print()  # Add a space before the starting message
    print(success_message("Starting database and user management..."))
    
    try:
        db_config = await get_db_config()
    except SystemExit:
        return  # Exit the script if admin password is not available

    async with asyncpg.create_pool(**db_config) as pool:
        async with pool.acquire() as conn:
            while True:
                databases = await list_databases(conn)
                users = await list_users(conn)
                
                await print_available_databases(databases)
                await print_available_users(users)

                choice = input(prompt_message("\nEnter 'd' to drop databases, 'u' to manage users, or 'q' to quit: "))

                if choice.lower() == 'q':
                    print(info_message("Exiting database and user management process.\n"))
                    break
                elif choice.lower() == 'd':
                    await handle_database_drop(conn, databases)
                elif choice.lower() == 'u':
                    await handle_user_management(conn, users)
                else:
                    print(warning_message("Warning:", "Invalid choice. Please enter 'd', 'u', or 'q'."))

# [AI]: Handle the database dropping process
async def handle_database_drop(conn, databases: List[tuple]):
    while True:
        await print_available_databases(databases)
        choice = input(prompt_message("\nEnter the numbers of the databases to drop (comma-separated) or 'q' to quit: "))

        if choice.lower() == 'q':
            print(info_message("Exiting database drop process."))
            break

        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            to_drop = [databases[i]['datname'] for i in indices if 0 <= i < len(databases)]
            
            if not to_drop:
                print(warning_message("Warning:", "No valid databases selected. Please try again."))
                continue

            confirm = input(prompt_message(f"Are you sure you want to drop these databases: {', '.join(to_drop)}? (y/n): "))
            if confirm.lower() == 'y':
                dropped = [db for db in to_drop if await drop_database(conn, db)]
                
                if dropped:
                    print(success_message("\nDatabases successfully dropped:"))
                    for db in dropped:
                        print(success_message_with_white_text("-", db))
                
                databases = await list_databases(conn)
        except ValueError:
            print(error_message("Invalid input. Please enter comma-separated numbers or 'q'."))

# [AI]: Handle the user management process
async def handle_user_management(conn, users: List[tuple]):
    user_choice = input(prompt_message("Enter the numbers of the users to check/drop (comma-separated): "))
    try:
        indices = [int(x.strip()) - 1 for x in user_choice.split(',')]
        to_check = [users[i]['rolname'] for i in indices if 0 <= i < len(users)]
        
        if not to_check:
            print(warning_message("Warning:", "No valid users selected. Please try again."))
            return

        for user in to_check:
            user_dbs = await get_user_databases(conn, user)
            if user_dbs:
                print(info_message(f"User '{user}' is associated with databases: {', '.join(user_dbs)}"))
            else:
                confirm = input(prompt_message(f"User '{user}' is not associated with any databases. Drop this user? (y/n): "))
                if confirm.lower() == 'y':
                    await drop_user(conn, user)
    except ValueError:
        print(error_message("Invalid input. Please enter comma-separated numbers."))

if __name__ == "__main__":
    # [AI]: Remove debug logging and set the event loop policy for Windows
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())