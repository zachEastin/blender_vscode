import ast
import os
import re
def extract_bl_info(file_path):
    if not os.path.isfile(file_path):
        return None
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Parse the file content
    tree = ast.parse(file_content, filename=file_path)

    # Initialize bl_info variable
    bl_info = None

    # Traverse the AST to find the bl_info dictionary
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'bl_info':
                    # Convert the AST node to a Python object
                    bl_info = ast.literal_eval(node.value)
                    break

    return bl_info
def generate_toml(bl_info,dirname):
    # Extracting information from the bl_info dictionary
    name = bl_info.get("name", "")
    author = bl_info.get("author", "")
    description = bl_info.get("description", "")
    blender_version = bl_info.get("blender", (0, 0, 0))
    version = bl_info.get("version", (0, 0, 0))
    doc_url = bl_info.get("doc_url", "")
    category = bl_info.get("category", "")

    # Constructing the TOML content
    toml_content = f"""schema_version = "1.0.0"
id = "{dirname}"
version = "{'.'.join(map(str, version))}"
name = "{name}"
tagline = "{description}"
maintainer = "{author}"
type = "add-on"
website = "{doc_url if doc_url else 'NONE'}"
tags = ["{category}"]

blender_version_min = "{blender_version[0]}.{blender_version[1]}.{blender_version[2]}"


# License conforming to https://spdx.org/licenses/ (use "SPDX: prefix)
# https://docs.blender.org/manual/en/dev/advanced/extensions/licenses.html
license = [
  "SPDX:GPL-3.0-or-later",
]
copyright = [
    "2024 {author}",
]

[permissions]
network = "Checks if there is a new version available for download"
files = "Import/export of assets and updates"
"""

    return toml_content

def write_toml_to_file(toml_content, directory):
    file_path = os.path.join(directory, 'blender_manifest.toml')
    with open(file_path, 'w') as file:
        file.write(toml_content)
def update_version_from_init(directory):
    init_file = os.path.join(directory, '__init__.py')
    toml_file = os.path.join(directory, 'blender_manifest.toml')
    
    # Step 1: Read bl_info from __init__.py
    with open(init_file, 'r') as file:
        init_content = file.read()

    # Extract the bl_info dictionary
    bl_info_pattern = re.compile(r'bl_info\s*=\s*({.*?})', re.DOTALL)
    match = bl_info_pattern.search(init_content)
    if not match:
        print("bl_info dictionary not found in __init__.py")
        return
    
    bl_info_str = match.group(1)
    bl_info_dict = eval(bl_info_str)  # Be careful with eval, ensure the source is trusted

    # Get the version from bl_info
    if 'version' not in bl_info_dict:
        raise ValueError("version key not found in bl_info dictionary")
    
    version_tuple = bl_info_dict['version']
    version_str = '.'.join(map(str, version_tuple))

    # Step 2: Read and update the version in the toml file
    with open(toml_file, 'r') as file:
        toml_lines = file.readlines()

    version_pattern = re.compile(r'^\s*version\s*=\s*".*"\s*$')
    with open(toml_file, 'w') as file:
        for line in toml_lines:
            if version_pattern.match(line):
                file.write(f'version = "{version_str}"\n')
            else:
                file.write(line)

    print(f"Updated version to {version_str} in {toml_file}")
def ensure_toml(directory):
    file_path = os.path.join(directory, 'blender_manifest.toml')
    if os.path.exists(file_path):
        update_version_from_init(directory)
        return 
    bl_info=extract_bl_info(os.path.join(directory,"__init__.py"))
    if bl_info:
        toml_content = generate_toml(bl_info,os.path.basename(directory))
        write_toml_to_file(toml_content, directory)
        print("TOML file generated successfully.")
    else:
        print("bl_info not found in the specified file.")

