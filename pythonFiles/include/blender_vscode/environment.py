import bpy
import sys
import addon_utils
from pathlib import Path
import platform
from itertools import chain

python_path = Path(sys.executable)
blender_path = Path(bpy.app.binary_path)
blender_directory = blender_path.parent

# Test for MacOS app bundles
if platform.system()=='Darwin':
    use_own_python = blender_directory.parent in python_path.parents
else:
    use_own_python = blender_directory in python_path.parents

version = bpy.app.version
scripts_folder = blender_path.parent / f"{version[0]}.{version[1]}" / "scripts"
user_addon_directory = Path(bpy.utils.user_resource('SCRIPTS', path="addons"))
if bpy.app.version >= (4, 2, 0):
    addon_directories = tuple(map(Path, chain(addon_utils.paths(), [
        ext.directory
        for ext in bpy.context.preferences.extensions.repos
        if not ext.use_remote_url
    ])))
else:
    addon_directories = tuple(map(Path, addon_utils.paths()))