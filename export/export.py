import bpy
import time
import os
from . import export_utils
from ..helpers import sge_utils
from .. import sge_statics


def register():
    register_attribs()

    for t in classRefs:
        bpy.utils.register_class(t)

def unregister():
    unregister_attribs()

    for t in reversed(classRefs):
        bpy.utils.unregister_class(t)

def register_attribs():
    setattr(bpy.types.Scene,
            sge_statics.SGE_EXPORT_FILTER,
            bpy.props.EnumProperty(
                name ="Export filter",
                description ="",
                override = {'LIBRARY_OVERRIDABLE'},
                default = sge_statics.SGE_EXPORT_FILTER_NOFILTER,
                items = [
                    (sge_statics.SGE_EXPORT_FILTER_NOFILTER, "No filter",
                        "Export with the parent if the parents is \"Export recursive\""),
                    (sge_statics.SGE_EXPORT_FILTER_SELECTED_ONLY, "Selected only",
                        "Exports only selected objects and their children")
                ]
            ))
    
    setattr(bpy.types.Scene,
            sge_statics.SGE_EXPORT_FORMAT_ENUM,
            bpy.props.EnumProperty(
                name='Export format',
                description='Choose the export format',
                default=sge_statics.SGE_EXPORT_FORMAT_GLB,
                items= [
                    (sge_statics.SGE_EXPORT_FORMAT_GLB, 'GLB',
                     'Export as compressed GLTF'),
                    (sge_statics.SGE_EXPORT_FORMAT_GLTF, 'GLTF',
                     'Export uncompressed GLTF')
                ]
            ))

    setattr(bpy.types.Scene,
            sge_statics.SGE_EXPORT_SETTINGS_EXPANDED,
            bpy.props.BoolProperty())
    
    setattr(bpy.types.Scene,
            sge_statics.SGE_EXPORT_FILTERPROPERTIES_EXPANDED,
            bpy.props.BoolProperty())
    
    setattr(bpy.types.Scene,
        sge_statics.SGE_EXPORT_PROCESS_EXPANDED,
        bpy.props.BoolProperty())
    
    setattr(bpy.types.Scene,
            sge_statics.SGE_EXPORT_GLOBAL_EXPORT_DIR_PATH,
            bpy.props.StringProperty(
                name='Object export file path',
                description='Choose a directory to export objects to.',
                maxlen=512,
                default=os.path.join('//', 'Export'),
                subtype='DIR_PATH'
            ))

def unregister_attribs():
    sceneProps = [
        sge_statics.SGE_EXPORT_SETTINGS_EXPANDED,
        sge_statics.SGE_EXPORT_FILTERPROPERTIES_EXPANDED,
        sge_statics.SGE_EXPORT_FILTER,
        sge_statics.SGE_EXPORT_PROCESS_EXPANDED,
        sge_statics.SGE_EXPORT_GLOBAL_EXPORT_DIR_PATH,
        sge_statics.SGE_EXPORT_FORMAT_ENUM
    ]
    for sceneProp in sceneProps:
        if hasattr(bpy.types.Scene, sceneProp):
            delattr(bpy.types.Scene, sceneProp)

class SGE_PT_ExportPanel(bpy.types.Panel):
    bl_label = "Export"
    bl_idname = "SGE_PT_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = sge_statics.SGE_ADDON_CATEGORY

    def draw(self, context):
        scene = context.scene
        obj = context.object
        layout = self.layout

        self.ui_filter_section(context)
        self.ui_export_process_section(context)
        
    def ui_filter_section(self, context):
        scene = context.scene
        layout = self.layout
        
        sge_utils.LayoutSection(layout, sge_statics.SGE_EXPORT_FILTERPROPERTIES_EXPANDED, 'Export filter')
        if not getattr(scene, sge_statics.SGE_EXPORT_FILTERPROPERTIES_EXPANDED):
            return
        
        filter_row = layout.row()
        filter_row.prop(scene, sge_statics.SGE_EXPORT_FILTER)

    def ui_export_process_section(self, context):
        scene = context.scene
        layout = self.layout
        sge_utils.LayoutSection(layout, sge_statics.SGE_EXPORT_PROCESS_EXPANDED, 'Export process')
        if not getattr(scene, sge_statics.SGE_EXPORT_PROCESS_EXPANDED):
            return

        # export info button
        ObjectNum = len(GetRecursiveObjectsForExport())
        ObjectInfo = layout.row().box().split(factor=0.75)
        ObjectFeedback = str(ObjectNum) + ' Object(s) will be exported.'
        ObjectInfo.label(text=ObjectFeedback, icon='INFO')
        ObjectInfo.operator(sge_statics.SGE_ID_SHOW_OBJECTS_TO_EXPORT)

        # global export path
        exportPath = layout.row()
        exportPath.prop(scene, sge_statics.SGE_EXPORT_GLOBAL_EXPORT_DIR_PATH)

        # export format
        if getattr(scene, sge_statics.SGE_EXPORT_FORMAT_ENUM) == sge_statics.SGE_EXPORT_FORMAT_GLTF:
            layout.label(text='GLB is recommended, but GLTF can be useful for debugging', icon='INFO')
        layout.row().prop(scene, sge_statics.SGE_EXPORT_FORMAT_ENUM)

        # export button
        exportButton = layout.row()
        exportButton.scale_y = 2.0
        exportButton.operator(sge_statics.SGE_ID_EXPORT_BUTTON, icon='EXPORT')

        # open export folder button
        openExportFolder = layout.row()
        openExportFolder.operator(sge_statics.SGE_ID_OPEN_EXPORT_FOLDER, icon='FILE_FOLDER')

    class SGE_OT_ShowObjectsToExport(bpy.types.Operator):
        bl_label = "Show object(s)"
        bl_idname = sge_statics.SGE_ID_SHOW_OBJECTS_TO_EXPORT
        bl_description = "Click to show objects that are to be exported."

        def execute(self, context):
            objects = GetRecursiveObjectsForExport()
            popup_title = "Objects list"
            if len(objects) > 0:
                popup_title = str(len(objects))+' asset(s) will be exported.'
            else:
                popup_title = 'No exportable objects were found.'

            def draw(self, context):
                col = self.layout.column()
                for obj in objects:
                    row = col.row()
                    if obj is None:
                        row.label(text="- ("")")
                        continue
                    else:
                        row.label(text="- " + obj.name)
                        
            bpy.context.window_manager.popup_menu(
                draw,
                title=popup_title,
                icon='PACKAGE')
            return {'FINISHED'}
        
    class SGE_OT_ExportButton(bpy.types.Operator):
        bl_label = 'Export to Godot'
        bl_idname = sge_statics.SGE_ID_EXPORT_BUTTON
        bl_description = 'Export objects in the scene'
        

        def execute(self, context):

            parentExportObjects = GetRecursiveObjectsForExport()

            def canExport(exportObjects : list[bpy.types.Object]):
                if len(exportObjects) < 1:
                    self.report(
                        {'WARNING'},
                        'No assets found for export'
                    )
                    return False
                
                if export_utils.HasRelativeExportPaths(exportObjects, context):
                    self.report(
                        {'ERROR'},
                        'Save the .blend file before using relative export paths!'
                    )
                    return False
                
                for child in exportObjects:
                    if not child.visible_get(view_layer=context.view_layer):
                        return False

                return True
            
            if not canExport(parentExportObjects):
                return {'FINISHED'}
            
            scene = context.scene
            counter = CounterTimer()

            numExported = self.perform_export(context)

            self.report(
                {'INFO'},
                "Export of " +
                str(numExported) +
                " object(s), finished in " +
                str(round(counter.GetTime(), 2)) +
                "seconds. Look in console for more info.")

            return {'FINISHED'}
        
        def perform_export(self, context: bpy.types.Context):
            obj_list = GetRecursiveObjectsForExport()
            exportDirPath = getattr(context.scene, sge_statics.SGE_EXPORT_GLOBAL_EXPORT_DIR_PATH)

            original_user_selection = bpy.context.selected_objects
            original_active_user_selection = bpy.context.view_layer.objects.active
            original_visibility_map = {} # {obj: (hide_viewport, hide_set)}

            numExported = 0
            for export_obj in obj_list:
                print('Starting export of Mesh ' + export_obj.name)
                absDirPath = bpy.path.abspath(exportDirPath)
                fullPath = os.path.join(absDirPath, export_obj.name)

                bpy.ops.object.select_all(action='DESELECT')

                for child in export_utils.GetExportChildren(export_obj):
                    # can't select objects if they are hidden aparently so we save their original visiblity and restore it after
                    original_visibility_map[child] = child.hide_viewport, child.hide_get()
                    child.hide_viewport = False
                    child.hide_set(False)
                    child.select_set(True)

                # set selection and visibility of roots
                original_visibility_map[export_obj] = export_obj.hide_viewport, export_obj.hide_get()
                export_obj.hide_viewport = False
                export_obj.hide_set(False)
                export_obj.select_set(True)

                # export
                export_utils.export_mesh_with_children(fullPath)

                # restore original visibility
                for obj, (hide_viewport, hide_set) in original_visibility_map.items():
                    obj.hide_viewport = hide_viewport
                    obj.hide_set(hide_set)

                numExported += 1

            # restore original selection
            bpy.ops.object.select_all(action='DESELECT')
            for obj in original_user_selection:
                obj.select_set(True)

            # restore active object LAST
            bpy.context.view_layer.objects.active = original_active_user_selection

            return numExported
        
    class SGE_OT_OpenExportFolder(bpy.types.Operator):
        bl_label = 'Open export folder'
        bl_idname = sge_statics.SGE_ID_OPEN_EXPORT_FOLDER
        bl_description = 'Open the export folder in explorer'

        def execute(self, context):
            globalExportPath = getattr(context.scene, sge_statics.SGE_EXPORT_GLOBAL_EXPORT_DIR_PATH)
            os.startfile(globalExportPath)
            return {'FINISHED'}
            


class CounterTimer():
    def __init__(self):
        self.start = time.perf_counter()

    def ResetTime(self):
        self.start = time.perf_counter()

    def GetTime(self):
        return time.perf_counter()-self.start
    


# Returns a list or collection (what ever the fuck python uses) of objects marked for recursive export
def GetRecursiveObjectsForExport() -> list[bpy.types.Object]: 
    scene = bpy.context.scene
    export_filter = getattr(scene, sge_statics.SGE_EXPORT_FILTER)

    objects_to_export = []
    if export_filter == sge_statics.SGE_EXPORT_FILTER_NOFILTER:
        objects_to_export = FilterObjectsByExportType(scene.objects, sge_statics.SGE_OBJECT_EXPORT_RECURSIVE)
        return objects_to_export
    
    if export_filter == sge_statics.SGE_EXPORT_FILTER_SELECTED_ONLY:
        objects_to_export = FilterObjectsByExportType(
            bpy.context.selected_objects, sge_statics.SGE_OBJECT_EXPORT_RECURSIVE)
        return objects_to_export


def FilterObjectsByExportType(objs, exportType):
    targetObj = []
    for obj in objs:
        prop = getattr(obj, sge_statics.SGE_OBJECT_EXPORT_ENUM)
        if prop == exportType:
            targetObj.append(obj)
    return targetObj

classRefs = [
    SGE_PT_ExportPanel,
    SGE_PT_ExportPanel.SGE_OT_ShowObjectsToExport,
    SGE_PT_ExportPanel.SGE_OT_ExportButton,
    SGE_PT_ExportPanel.SGE_OT_OpenExportFolder
]