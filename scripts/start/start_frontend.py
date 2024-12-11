# [AI]: This file implements a script to start the Next.js frontend server.
# It provides functionality to run the development server, open a browser, and handle server lifecycle.
# Key features:
# - Starts the Next.js development server
# - Opens the application in a web browser (preferably Microsoft Edge)
# - Handles server shutdown gracefully
# - Supports command-line arguments for browser selection
# - Implements logging and colorized console output

import sys
from pathlib import Path
import logging
import subprocess
import os
import time
from threading import Thread
import argparse
import webbrowser
from colorama import Fore, Style, init
import requests
import json

# [AI]: Add the project root to the Python path to allow imports from other project modules
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# [AI]: Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# [AI]: Configure logging for the script
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# [AI]: Define helper functions for colorized console output
def print_info(message):
    print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}Warning: {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}Error: {message}{Style.RESET_ALL}")

# [AI]: Function to load settings from a TOML file (Note: 'tomli' import is missing)
def load_settings(project_root: Path) -> dict:
    settings_path = project_root / "backend" / "config" / "settings.lcl.toml"
    try:
        with open(settings_path, "rb") as f:
            return tomli.load(f)
    except FileNotFoundError:
        logger.error(f"Settings file not found: {settings_path}")
        sys.exit(1)
    except tomli.TOMLDecodeError:
        logger.error(f"Error decoding TOML file: {settings_path}")
        sys.exit(1)

# [AI]: Function to find the project root directory
def find_project_root(start_path: Path) -> Path:
    current_path = start_path.resolve()
    while current_path != current_path.parent:
        if (current_path / 'README.md').exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError("Could not find project root. Make sure you're in the correct directory with README.md.")

# [AI]: Find project root and add it to the Python path
script_path = Path(__file__).resolve()
try:
    project_root = find_project_root(script_path)
except FileNotFoundError as e:
    logger.error(str(e))
    sys.exit(1)

sys.path.insert(0, str(project_root))

# [AI]: Function to run the Next.js development server
def run_server():
    npm_command = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_dir = project_root / "frontend"
    
    try:
        print_info("Starting Next.js development server...")
        subprocess.run([npm_command, "run", "dev"], check=True, cwd=frontend_dir)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Next.js server: {e}")
    except FileNotFoundError:
        logger.error("npm not found. Make sure Node.js and npm are installed and in your PATH.")
    except KeyboardInterrupt:
        print_info("Server shutting down...")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        print_info("Server shutdown complete.")

# [AI]: Function to open Microsoft Edge browser
def open_edge():
    url = 'http://localhost:3000'
    edge_commands = [
        'start microsoft-edge:' + url,  # Windows
        'open -a "Microsoft Edge" ' + url,  # macOS
        'microsoft-edge ' + url  # Linux
    ]
    
    for cmd in edge_commands:
        try:
            subprocess.Popen(cmd, shell=True)
            return True
        except:
            continue
    return False

# [AI]: Function to open a web browser, with preference for Microsoft Edge
def open_browser(browser_name=None):
    url = 'http://localhost:3000'
    
    if not browser_name:
        # Try to use Microsoft Edge first
        if open_edge():
            return
        
        # If Edge fails, try using webbrowser's built-in support
        edge_names = ['edge', 'msedge', 'microsoft-edge']
        for name in edge_names:
            try:
                browser = webbrowser.get(name)
                browser.open(url)
                return
            except webbrowser.Error:
                continue
    
    # If Edge not found or a specific browser was requested
    if browser_name:
        try:
            browser = webbrowser.get(browser_name)
            browser.open(url)
            return
        except webbrowser.Error:
            print(f"Couldn't find browser: {browser_name}. Falling back to default.")
    
    # If all else fails, use the default browser
    webbrowser.open(url)

# [AI]: Function to wait for the server to be ready
def wait_for_server(timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            requests.get('http://localhost:3000', timeout=1)
            return True
        except requests.RequestException:
            time.sleep(0.5)
    return False

# [AI]: Main function to orchestrate the server startup process
def main():
    parser = argparse.ArgumentParser(description="Start the Next.js frontend server")
    parser.add_argument('--browser', help="Specify the browser to open (e.g., 'chrome', 'firefox'). Defaults to Microsoft Edge if available.")
    args = parser.parse_args()

    print()  # Add one line space after the command line

    print_info("Starting Next.js server on http://localhost:3000")
    
    # [AI]: Start the server in a separate thread
    server_thread = Thread(target=run_server)
    server_thread.start()

    # [AI]: Wait for the server to be ready before opening the browser
    if wait_for_server():
        # Open the browser
        Thread(target=open_browser, args=(args.browser,)).start()
        print_info("App opened in browser")
    else:
        print_warning("Server didn't start in time. Please open the browser manually.")
    
    print()

    # [AI]: Keep the main thread alive and handle graceful shutdown
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_info("Server stopping...")
    finally:
        server_thread.join()

if __name__ == "__main__":
    main()