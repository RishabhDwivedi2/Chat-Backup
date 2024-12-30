# [AI]: This file implements database connection functionality for the project.
# It provides functionality to test and establish connections to a PostgreSQL database.
# Key features:
# - Asynchronous database connection using asyncpg
# - Colored console output for better readability
# - Error handling and logging
# - Configuration loading from settings

import sys
from pathlib import Path

# [AI]: Add the project root to the Python path to allow imports from the backend
PROJECT_ROOT = Path(__file__).parents[2]
sys.path.append(str(PROJECT_ROOT))

from backend.app.config.constants import settings

import asyncio
import asyncpg
import logging
from colorama import Fore, Style, init
from typing import Dict, Any

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

def file_path_message(message: str) -> str:
    return format_message(message, INFO_COLOR)

# [AI]: Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# [AI]: Retrieve database connection parameters from settings
async def get_connection_params() -> Dict[str, Any]:
    return {
        'database': settings.get('DATABASE.NAME'),
        'user': settings.get('DATABASE.USER_NAME'),
        'password': settings.get('DATABASE.USER_PASSWORD'),
        'host': settings.get('DATABASE.HOST', 'localhost'),
        'port': settings.get('DATABASE.PORT', 5432)
    }

# [AI]: Main function to test the database connection
async def test_database_connection():
    try:
        connection_params = await get_connection_params()
        
        # [AI]: Log connection parameters (excluding password for security)
        safe_params = {k: v for k, v in connection_params.items() if k != 'password'}
        print(info_message("\nAttempting to connect with parameters:"))
        for key, value in safe_params.items():
            print(info_message(f"  {key}: {value}"))
        print()  # Add an extra line for spacing

        # [AI]: Check if all required parameters are present
        required_params = ['database', 'user', 'password', 'host', 'port']
        missing_params = [param for param in required_params if not connection_params.get(param)]
        
        if missing_params:
            raise AttributeError(f"Missing required database parameters: {', '.join(missing_params)}")

        # [AI]: Establish a connection to the database
        print(info_message("Connecting to the database..."))
        conn = await asyncpg.connect(**connection_params)
        
        print(info_message(f"Successfully connected to the database '{connection_params['database']}' as user '{connection_params['user']}'."))
        
        # [AI]: Execute a simple test query to verify the connection
        await conn.fetchval("SELECT 1")
        
        # [AI]: Close the database connection
        await conn.close()
        
        print(info_message("Successfully disconnected from the database."))
        print()  # Add an extra line for spacing
        print(success_message("Database connection test completed successfully."))
        print()  # Add an extra line for spacing after completion message

    except AttributeError as e:
        # [AI]: Handle configuration errors (e.g., missing parameters)
        print(error_message(f"Configuration error: {str(e)}"))
    except asyncpg.PostgresError as e:
        # [AI]: Handle database-specific errors
        print(error_message(f"Database connection error: {str(e)}"))
    except Exception as e:
        # [AI]: Handle any unexpected errors and log the stack trace
        print(error_message(f"Unexpected error: {str(e)}"))
        logger.exception("Stack trace:")

# [AI]: Main entry point for the script
async def main():
    print()  # Add a space before the starting message
    print(success_message("Starting database connection test..."))
    await test_database_connection()

if __name__ == "__main__":
    # [AI]: Remove debug logging for asyncio to reduce noise
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    asyncio.run(main())