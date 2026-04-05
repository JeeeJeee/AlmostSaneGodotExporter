# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


# bl_info = {
#     'name': 'AlmostSaneGodotExporter',
#     'author': 'JeeeJeee',
#     'version': (0, 0, 1),
#     'blender': (3, 4, 0),
#     'location': 'View3D > UI > AlmostSaneGodotExporter',
#     'description': "Improves the mesh workflow when working with Godot",
#     'warning': '',
#     "wiki_url": "",
#     'tracker_url': '',
#     'support': 'COMMUNITY',
#     'category': 'Import-Export'}

_needs_reload = "bpy" in locals()

from .export import export
from .export import export_utils
from .object import object
from .collisions import collisions
from .godot import godot

# the order here is the order the UI is structured in
modules = [object, collisions, export, godot]

if _needs_reload:
    import importlib
    for m in modules:
        importlib.reload(m)

    importlib.reload(export_utils)
        

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()