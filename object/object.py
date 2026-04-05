import bpy
from .. import sge_statics
from ..helpers import sge_utils

def register():
    # Not sure why only this class sometimes tries to double register
    try:
        bpy.utils.register_class(SGE_PT_ObjectPanel)
    except ValueError:
        bpy.utils.unregister_class(SGE_PT_ObjectPanel)
        bpy.utils.register_class(SGE_PT_ObjectPanel)

    register_attribs()
    return

def unregister():
    bpy.utils.unregister_class(SGE_PT_ObjectPanel)
    unregister_attribs()
    return

def register_attribs():
    setattr(bpy.types.Scene,
            sge_statics.SGE_OBJECT_PROPERTIES_EXPANDED,
            bpy.props.BoolProperty())

    setattr(bpy.types.Object,
            sge_statics.SGE_OBJECT_EXPORT_ENUM,
            bpy.props.EnumProperty(
            name="Export type",
            description="Export procedure",
            override={'LIBRARY_OVERRIDABLE'},
            items=[
                (sge_statics.SGE_OBJECT_EXPORT_AUTO, "Auto",
                    "Export with the parent if the parents is \"Export recursive\"",
                    "BOIDS", 1),
                (sge_statics.SGE_OBJECT_EXPORT_RECURSIVE, "Export recursive",
                    "Export self object and all children",
                    "KEYINGSET", 2),
                (sge_statics.SGE_OBJECT_EXPORT_NOEXPORT, "Not exported",
                    "Will never export",
                    "CANCEL", 3)
            ],
            default=sge_statics.SGE_OBJECT_EXPORT_AUTO)
    )

    setattr(
        bpy.types.Object,
        sge_statics.SGE_EXPORT_PEROBJECT_EXPORT_PATH,
        bpy.props.StringProperty(
            name="Custom export path",
            description=(
                'The path you want this specific object to be exported to.'
            ),
            default='',
            subtype='DIR_PATH'
        )
    )

    setattr(
        bpy.types.Object,
        sge_statics.SGE_OBJECT_MOVE_TO_ZERO,
        bpy.props.BoolProperty(
            name='Move to zero',
            description='Move object to zero on export',
            default=True
        )
    )

    setattr(
        bpy.types.Object,
        sge_statics.SGE_OBJECT_ROTATE_TO_ZERO,
        bpy.props.BoolProperty(
            name='Rotate to zero',
            description='Rotate object to zero on export',
            default=False
        )
    )

    
def unregister_attribs():
    delattr(bpy.types.Scene, sge_statics.SGE_OBJECT_PROPERTIES_EXPANDED)
    delattr(bpy.types.Object, sge_statics.SGE_OBJECT_EXPORT_ENUM)
    delattr(bpy.types.Object, sge_statics.SGE_EXPORT_PEROBJECT_EXPORT_PATH)
    delattr(bpy.types.Object, sge_statics.SGE_OBJECT_MOVE_TO_ZERO)
    delattr(bpy.types.Object, sge_statics.SGE_OBJECT_ROTATE_TO_ZERO)

class SGE_PT_ObjectPanel(bpy.types.Panel):
    bl_label = 'Object'
    bl_idname = 'SGE_PT_object'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'    
    bl_category = sge_statics.SGE_ADDON_CATEGORY

    def draw(self, context):
        scene = context.scene
        obj = context.object
        layout = self.layout

        # Object UI
        sge_utils.LayoutSection(layout, sge_statics.SGE_OBJECT_PROPERTIES_EXPANDED, "Object Properties", shouldEmboss=False)
        if getattr(scene, sge_statics.SGE_OBJECT_PROPERTIES_EXPANDED):
            if obj is None or obj not in context.selected_objects:
                layout.row().label(text='No selected object.')
            else:
                AssetType = layout.row()
                AssetType.prop(obj, 'name', text="", icon='OBJECT_DATA')

                ExportType = layout.column()
                ExportType.prop(obj, sge_statics.SGE_OBJECT_EXPORT_ENUM)

                value = getattr(obj, sge_statics.SGE_OBJECT_EXPORT_ENUM)
                if value == sge_statics.SGE_OBJECT_EXPORT_RECURSIVE:
                    CustomExport = layout.column()
                    CustomExport.prop(obj, sge_statics.SGE_EXPORT_PEROBJECT_EXPORT_PATH)
                    layout.row().prop(obj, sge_statics.SGE_OBJECT_MOVE_TO_ZERO)
                    layout.row().prop(obj, sge_statics.SGE_OBJECT_ROTATE_TO_ZERO)
