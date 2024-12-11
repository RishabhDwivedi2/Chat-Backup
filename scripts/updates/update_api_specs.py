# [AI]: This file implements an API documentation generator for FastAPI applications.
# It provides functionality to automatically generate Markdown documentation from OpenAPI specs.
# Key features:
# - Finds the project root directory
# - Imports the FastAPI app dynamically
# - Generates comprehensive API documentation in Markdown format
# - Supports colored console output for better readability
# - Handles errors and provides informative messages

import os
from pathlib import Path
import logging
import sys
import importlib.util
import json
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from colorama import Fore, Style, init

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

# [AI]: Set up logging for tracking script execution
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# [AI]: Function to find the project root directory
def find_project_root(start_path: Path) -> Path:
    current_path = start_path.resolve()
    while current_path != current_path.parent:
        if (current_path / '.git').exists() or (current_path / 'pyproject.toml').exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError("Could not find project root. Make sure you're in a git repository or have a pyproject.toml file.")

# [AI]: Function to dynamically import the FastAPI app
def import_app(file_path: Path) -> FastAPI:
    parent_dir = file_path.parent.parent.parent
    sys.path.append(str(parent_dir))
    spec = importlib.util.spec_from_file_location("main", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.app

# [AI]: Function to generate API documentation in Markdown format
def generate_api_docs(app: FastAPI) -> str:
    # [AI]: Get the OpenAPI schema from the FastAPI app
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # [AI]: Start building the Markdown documentation
    markdown_docs = f"# {app.title} API Documentation\n\n"
    markdown_docs += "This document provides detailed information about the API endpoints for the project.\n\n"

    # [AI]: Generate table of contents
    markdown_docs += "## Table of Contents\n"
    for path in openapi_schema["paths"]:
        endpoint_name = path.replace("/", "").capitalize()
        markdown_docs += f"- [{endpoint_name}](#{endpoint_name.lower()})\n"
    markdown_docs += "\n"

    # [AI]: Generate documentation for each endpoint
    for path, path_item in openapi_schema["paths"].items():
        endpoint_name = path.replace("/", "").capitalize()
        markdown_docs += f"## {endpoint_name}\n"
        markdown_docs += f"**Base URL:** `{path}`\n"

        for method, operation in path_item.items():
            markdown_docs += f"### {method.upper()}\n"
            markdown_docs += f"**Summary:** {operation.get('summary', 'N/A')}\n"
            markdown_docs += f"**Description:** {operation.get('description', 'N/A')}\n"

            # [AI]: Document parameters
            if "parameters" in operation:
                markdown_docs += "#### Parameters\n"
                markdown_docs += "| Name | Located In | Description | Required | Schema |\n"
                markdown_docs += "|------|------------|-------------|----------|--------|\n"
                for param in operation["parameters"]:
                    required = "Yes" if param.get('required', False) else "No"
                    schema = param.get('schema', {}).get('type', 'N/A')
                    markdown_docs += f"| {param['name']} | {param['in']} | {param.get('description', 'N/A')} | {required} | {schema} |\n"

            # [AI]: Document request body
            if "requestBody" in operation:
                markdown_docs += "#### Request Body\n"
                content = operation["requestBody"]["content"]
                for media_type, schema_info in content.items():
                    markdown_docs += f"**Content-Type:** `{media_type}`\n"
                    if "schema" in schema_info:
                        markdown_docs += "**Schema:**\n```json\n"
                        markdown_docs += json.dumps(schema_info["schema"], indent=2)
                        markdown_docs += "\n```\n"

            # [AI]: Document responses
            if "responses" in operation:
                markdown_docs += "#### Responses\n"
                markdown_docs += "| Status Code | Description | Schema |\n"
                markdown_docs += "|-------------|-------------|--------|\n"
                for status_code, response_info in operation["responses"].items():
                    schema = "N/A"
                    if "content" in response_info:
                        for media_type, media_info in response_info["content"].items():
                            if "schema" in media_info:
                                schema = json.dumps(media_info["schema"], indent=2)
                    markdown_docs += f"| {status_code} | {response_info.get('description', 'N/A')} | {schema} |\n"

            markdown_docs += "\n---\n"

    return markdown_docs

# [AI]: Main function to orchestrate the API documentation generation process
def main():
    print(info_message("\nStarting update_api_specs.py\n"))

    # [AI]: Find the project root directory
    script_path = Path(__file__).resolve()
    try:
        root_dir = find_project_root(script_path)
    except FileNotFoundError as e:
        print(error_message(str(e)))
        return

    # [AI]: Locate the main.py file in the backend directory
    main_py_path = root_dir / "backend" / "app" / "main.py"
    if not main_py_path.exists():
        print(error_message(f"Could not find main.py at {main_py_path}"))
        return

    # [AI]: Add the project root and backend directory to sys.path
    sys.path.append(str(root_dir))
    sys.path.append(str(root_dir / "backend"))

    # [AI]: Import the FastAPI app
    try:
        app = import_app(main_py_path)
        print()  # Add a line break
        print(info_message("Successfully imported FastAPI app"))
    except Exception as e:
        print(error_message(f"Error importing FastAPI app: {e}"))
        logger.exception("Error importing FastAPI app")
        return

    # [AI]: Generate API documentation
    print(info_message("Generating API documentation..."))
    api_docs = generate_api_docs(app)
    print(f"{SUCCESS_COLOR}Generated:{Style.RESET_ALL} API documentation generated successfully")

    # [AI]: Define the output file path
    output_path = root_dir / "workspace" / "files" / "api_specs.md"

    # [AI]: Ensure the output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # [AI]: Write the API documentation to the file at the specified path
    try:
        with output_path.open("w", encoding="utf-8") as f:
            f.write(api_docs)
        relative_path = output_path.relative_to(root_dir)
        print(f"{SUCCESS_COLOR}Updated:{Style.RESET_ALL} API documentation in {file_path_message(str(relative_path))}")
    except IOError as e:
        print(error_message(f"Error writing to file: {e}"))

    print(success_message("\nAPI specs update completed successfully."))
    print()  # Add a final line break

if __name__ == "__main__":
    main()
