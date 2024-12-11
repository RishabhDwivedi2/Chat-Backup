# [AI]: This file implements project name management for local development.
# It provides functionality to find the project root, get the project name, and update it in the local settings file.
# Key features:
# - Find project root directory
# - Get project name from directory structure
# - Update project name in local TOML configuration file
# - Error handling for missing files or configuration entries

import os
import toml
from pathlib import Path

# [AI]: This function recursively searches for the project root directory.
# It uses a marker file (default: README.md) to identify the root.
def find_project_root(current_path=os.getcwd(), marker_file="README.md"):
    while True:
        if os.path.exists(os.path.join(current_path, marker_file)):
            return current_path
        parent = os.path.dirname(current_path)
        if parent == current_path:
            # [AI]: Raise an error if the project root is not found
            raise FileNotFoundError(f"Project root not found. Marker file '{marker_file}' not detected in parent directories.")
        current_path = parent

# [AI]: This function retrieves the project name from the root directory name.
def get_project_name():
    project_root = Path(find_project_root())
    return project_root.name

# [AI]: This function updates the project name in the local settings file.
# It reads the TOML file, updates the project name if necessary, and writes it back.
def update_project_name():
    project_name = get_project_name()
    project_root = Path(find_project_root())
    config_file = project_root / "backend" / "config" / "settings.lcl.toml"

    # [AI]: Check if the config file exists
    if not config_file.exists():
        print(f"Error: {config_file} not found.")
        return

    # [AI]: Read the TOML file
    with open(config_file, "r") as file:
        config = toml.load(file)

    # [AI]: Update the project name if it's different from the current one
    if "PROJECT" in config and "NAME" in config["PROJECT"]:
        if config["PROJECT"]["NAME"] != project_name:
            config["PROJECT"]["NAME"] = project_name
            # [AI]: Write the updated config back to the file
            with open(config_file, "w") as file:
                toml.dump(config, file)
            print(f"Updated project name to '{project_name}' in {config_file}")
        else:
            print(f"Project name is already set to '{project_name}' in {config_file}")
    else:
        # [AI]: Handle the case where the expected configuration keys are missing
        print(f"Error: PROJECT.NAME not found in {config_file}")

# [AI]: Execute the update_project_name function when the script is run directly
if __name__ == "__main__":
    update_project_name()
