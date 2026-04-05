import bpy
from .. import sge_statics
from . import godot_helpers
from bpy_extras.io_utils import ImportHelper

def register():
    for t in classRefs:
        try:
            bpy.utils.register_class(t)
        except ValueError:
            bpy.utils.unregister_class(t)
            bpy.utils.register_class(t)
    register_attribs()

    # try loading the godot project after blender has loaded
    bpy.app.handlers.load_post.append(load_post_godot)

def load_post_godot(dummy):
    scene = bpy.context.scene
    # we can use this variable to check if the godot project has been loaded before
    if godot_helpers.GODOT_PROJECT_NAME:
        return
        
    # load the godot project on registration if the path is set
    if hasattr(scene, sge_statics.SGE_GODOT_PROJECT_PATH):
        projectPath = getattr(scene, sge_statics.SGE_GODOT_PROJECT_PATH)
        if projectPath and godot_helpers.isGodotProject(projectPath):
            godot_helpers.load_godot_project(projectPath)


def unregister():
    for t in reversed(classRefs):
        bpy.utils.unregister_class(t)
    unregister_attribs()

def register_attribs():
    setattr(bpy.types.Scene,
            sge_statics.SGE_GODOT_PROJECT_PATH,
            bpy.props.StringProperty(
                name='Godot project file path',
                description='The path to your godot project file. Usually called project.godot',
                maxlen=512,
                default='',
                subtype='FILE_PATH'
            ))
    
def unregister_attribs():
    delattr(bpy.types.Scene, sge_statics.SGE_GODOT_PROJECT_PATH)


class SGE_PT_GodotPanel(bpy.types.Panel):
    bl_label = "Godot"
    bl_idname = "SGE_PT_godot"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = sge_statics.SGE_ADDON_CATEGORY

    triedLoading = False

    def draw(self, context):
        scene = context.scene
        obj = context.object
        layout = self.layout

        # try loading the godot project ONCE here
        if not self.triedLoading:
            load_post_godot(None)
            self.triedLoading = True

        ObjectFeedback = 'Godot project: ' + godot_helpers.GODOT_PROJECT_NAME
        
        box = layout.row().box()
        split_main = box.split(factor=0.75, align=True)
        split_main.label(text=ObjectFeedback, icon='INFO')
        split_right = split_main.split(factor=0.8, align=True)
        split_right.operator(
            sge_statics.SGE_ID_SELECT_GODOT_PATH,
            icon='FILE_FOLDER',
            text="Select"
        )
        split_right.operator(
            sge_statics.SGE_ID_REFRESH_GODOT_PROJECT,
            icon='FILE_REFRESH',
            text=""
        )


    class SGE_OT_SelectGodotProject(bpy.types.Operator, ImportHelper):
        bl_idname = sge_statics.SGE_ID_SELECT_GODOT_PATH
        bl_label = "Select Godot Project"
        bl_description = 'Set the path to your godot project file'

        filename_ext = ".godot"

        filter_glob: bpy.props.StringProperty(# type: ignore
            default="*.godot",
            options={'HIDDEN'}
        )

        filepath: bpy.props.StringProperty(subtype="FILE_PATH") #type: ignore

        def execute(self, context):
            if not godot_helpers.isGodotProject(self.filepath):
                self.report(
                    {'ERROR'},
                    'Not a valid path to a godot project'
                )
                return {'FINISHED'}
            
            if godot_helpers.load_godot_project(self.filepath):
                setattr(context.scene, sge_statics.SGE_GODOT_PROJECT_PATH, self.filepath)                
            else:
                self.report({'ERROR'}, "Failed to load Godot project")

            return {'FINISHED'}
        
    class SGE_OT_RefreshGodotProject(bpy.types.Operator):
        bl_idname = sge_statics.SGE_ID_REFRESH_GODOT_PROJECT
        bl_label = ''
        bl_description = 'Refresh the godot project'

        def execute(self, context):
            path = godot_helpers.GODOT_PROJECT_PATH
            if path != '' and godot_helpers.isGodotProject(path):
                godot_helpers.load_godot_project(path)
                return {'FINISHED'}
            
            self.report(
                {'ERROR'},
                'No valid godot project path is set'
            )
            return {'FINISHED'}



classRefs = [
    SGE_PT_GodotPanel,
    SGE_PT_GodotPanel.SGE_OT_SelectGodotProject,
    SGE_PT_GodotPanel.SGE_OT_RefreshGodotProject,
]