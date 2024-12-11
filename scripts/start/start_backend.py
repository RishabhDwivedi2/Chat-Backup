# [AI]: This file implements the backend server startup script for the project.
# It provides functionality to start the FastAPI server, open a browser, and handle command-line arguments.
# Key features:
# - Configures Python path and imports necessary modules
# - Sets up logging and colored console output
# - Implements browser opening functionality with fallback options
# - Parses command-line arguments for browser selection
# - Starts the FastAPI server using uvicorn

import sys
from pathlib import Path
import logging
import uvicorn
import webbrowser
import time
from threading import Thread
import argparse
import subprocess
from colorama import Fore, Style, init

# [AI]: Add project root and backend directory to Python path for proper imports
project_root = Path(__file__).resolve().parents[2]
backend_dir = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

from app.config import settings

# [AI]: Initialize colorama for cross-platform colored console output
init(autoreset=True)

# [AI]: Helper functions for colored console output
def print_colored(message, color):
    print(f"{color}{message}{Style.RESET_ALL}")

def print_info(message):
    print_colored(message, Fore.CYAN)

def print_warning(message):
    print_colored(f"⚠️  {message}", Fore.YELLOW)

# [AI]: Configure logging to display warnings and errors
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# [AI]: Reduce watchfiles logging output in debug mode to minimize console clutter
if settings.ENV.DEBUG:
    logging.getLogger("watchfiles").setLevel(logging.ERROR)

# [AI]: Function to open the application in a browser
def open_browser(url, browser_name=None):
    time.sleep(2)  # [AI]: Short delay to ensure server is ready
    if browser_name:
        try:
            browser = webbrowser.get(browser_name)
            browser.open(url)
            return
        except webbrowser.Error:
            logger.warning(f"Failed to open specified browser: {browser_name}")
    
    # [AI]: Attempt to open Microsoft Edge as a fallback
    if open_edge(url):
        return
    
    # [AI]: Use default system browser if Edge is not available
    webbrowser.open(url)

# [AI]: Function to attempt opening Microsoft Edge browser
def open_edge(url):
    edge_commands = [
        f'start microsoft-edge:{url}',
        f'open -a "Microsoft Edge" {url}',
        f'microsoft-edge {url}'
    ]
    
    for cmd in edge_commands:
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            continue
    return False

# [AI]: Main function to start the backend server
def main():
    # [AI]: Parse command-line arguments for browser selection
    parser = argparse.ArgumentParser(description="Start the FastAPI backend server")
    parser.add_argument('--browser', help="Specify the browser to open")
    args = parser.parse_args()

    print()  # [AI]: Add one line space after the command line for better readability
    print_info(f"Starting {settings.PROJECT.NAME} backend server ({settings.ENV.APP_ENV})")
    
    # [AI]: Warn about potential need for database migrations
    if settings.DATABASE.AUTO_MIGRATE:
        print_warning("Run alembic_new_migration.py and update_database_schema.py if you made model changes.")

    # [AI]: Construct server URL and start browser in a separate thread
    url = f'http://{settings.SERVER.HOST}:{settings.SERVER.PORT}'
    print_info(f"Starting server on {url}")
    Thread(target=open_browser, args=(url, args.browser)).start()
    print_info("App opened in browser")
    print()

    print_warning("Logging set to display only warnings and errors on the terminal.")
    print()

    # [AI]: Start the FastAPI server using uvicorn
    uvicorn.run(
        app="app.main:app",
        host=settings.SERVER.HOST,
        port=settings.SERVER.PORT,
        log_level="warning",
        reload=settings.ENV.DEBUG,
    )

if __name__ == "__main__":
    main()