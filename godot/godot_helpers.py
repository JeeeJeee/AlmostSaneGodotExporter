import bpy
import re
import os
from .. import sge_statics


GODOT_PROJECT_NAME = ""
GODOT_3D_LAYERS = {}
GODOT_PROJECT_PATH = ""

def load_godot_project(filepath):
    global GODOT_PROJECT_NAME
    global GODOT_3D_LAYERS
    global GODOT_PROJECT_PATH
    global GODOT_CACHED_COLLISION_LAYER_ENUM_ITEMS

    GODOT_PROJECT_NAME = ""
    GODOT_3D_LAYERS = {}
    GODOT_PROJECT_PATH = filepath

    in_layer_section = False

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()

                # skip empty + comments
                if not line or line.startswith(";"):
                    continue

                # detect section
                if line.startswith("[") and line.endswith("]"):
                    in_layer_section = (line == "[layer_names]")
                    continue

                # Project name
                # config/name="MyProject"
                match_name = re.match(r'config/name="(.+)"', line)
                if match_name:
                    GODOT_PROJECT_NAME = match_name.group(1)
                    continue

                # 3D physics layers
                if in_layer_section:
                    match_layer = re.match(r'3d_physics/layer_(\d+)="(.*)"', line)
                    if match_layer:
                        index = int(match_layer.group(1))
                        name = match_layer.group(2)
                        GODOT_3D_LAYERS[index] = name

        GODOT_CACHED_COLLISION_LAYER_ENUM_ITEMS = build_col_layers_enum(GODOT_3D_LAYERS)

        return True

    except Exception as e:
        print(f"[Godot Loader] Failed to load project: {e}")
        GODOT_PROJECT_NAME = ""
        GODOT_3D_LAYERS = {}
        return False


def build_col_layers_enum(col_layers_dict):
    items = []

    for i in range(1, 32):  # Godot supports 32 layers but blender only supports c int so 31
        name = col_layers_dict.get(i, f"Layer {i}")

        items.append((
            f"LAYER_{i}",      # identifier
            name,             # UI name
            f"Godot layer {i}",
            1 << (i - 1)      # bitmask value
        ))

    return items

def get_godot_col_layer_items(self, context):
    global GODOT_CACHED_COLLISION_LAYER_ENUM_ITEMS

    if GODOT_CACHED_COLLISION_LAYER_ENUM_ITEMS is None:
        return build_col_layers_enum({})

    return GODOT_CACHED_COLLISION_LAYER_ENUM_ITEMS


def isGodotProject(filepath):
    return os.path.isfile(filepath)

GODOT_CACHED_COLLISION_LAYER_ENUM_ITEMS = build_col_layers_enum({})