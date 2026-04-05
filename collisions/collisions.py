import bpy
from .. import sge_statics
from ..helpers import sge_utils
from . import collision_utils
from ..godot import godot_helpers

_collisionToggleLastValue = False

def register():
    for ref in classRefs:
        try:
            bpy.utils.register_class(ref)
        except ValueError:
            bpy.utils.unregister_class(ref)
            bpy.utils.register_class(ref)
    register_attribs()

def unregister():
    for ref in classRefs:
        bpy.utils.unregister_class(ref)
    unregister_attribs()

def get_col_layer_enum(obj : bpy.types.Object):
    return obj.get(sge_statics.SGE_COLLISION_LAYER_ENUM, 1)

def set_col_layer_enum(obj : bpy.types.Object, value):
    obj[sge_statics.SGE_COLLISION_LAYER_ENUM] = value

def register_attribs():
    setattr(bpy.types.Object,
            sge_statics.SGE_COLLISION_IS_COLLIDER,
            bpy.props.BoolProperty())

    setattr(bpy.types.Scene,
            sge_statics.SGE_COLLISION_LAYERS_EXPANDED,
            bpy.props.BoolProperty())
    
    setattr(bpy.types.Scene,
            sge_statics.SGE_COLLISION_MASKS_EXPANDED,
            bpy.props.BoolProperty())
    
    setattr(bpy.types.Scene,
            sge_statics.SGE_COLLISION_CREATE_EXPANDED,
            bpy.props.BoolProperty())
    
    setattr(bpy.types.Object,
            sge_statics.SGE_COLLISION_LAYER_ENUM,
            bpy.props.EnumProperty(
                name="Collision Layers",
                description="Godot 3D physics layers",
                items=godot_helpers.get_godot_col_layer_items,
                options={'ENUM_FLAG'},
                default=1,
                get=get_col_layer_enum,
                set=set_col_layer_enum
            ))
    
    setattr(bpy.types.Object,
            sge_statics.SGE_COLLISION_MASK_ENUM,
            bpy.props.EnumProperty(
                name="Collision Masks",
                description="Godot 3D physics masks",
                items=godot_helpers.get_godot_col_layer_items,
                options={'ENUM_FLAG'},
                default=1
            ))
    
def unregister_attribs():
    delattr(bpy.types.Scene, sge_statics.SGE_COLLISION_LAYERS_EXPANDED)
    delattr(bpy.types.Scene, sge_statics.SGE_COLLISION_MASKS_EXPANDED)
    delattr(bpy.types.Scene, sge_statics.SGE_COLLISION_CREATE_EXPANDED)
    delattr(bpy.types.Object, sge_statics.SGE_COLLISION_IS_COLLIDER)
    delattr(bpy.types.Object, sge_statics.SGE_COLLISION_LAYER_ENUM)
    delattr(bpy.types.Object, sge_statics.SGE_COLLISION_MASK_ENUM)

class SGE_PT_CollisionsPanel(bpy.types.Panel):
    bl_label = 'Collisions'
    bl_idname = 'SGE_PT_collisions'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = sge_statics.SGE_ADDON_CATEGORY

    def draw(self, context : bpy.types.Context):
        layout = self.layout

        layout.row().operator(sge_statics.SGE_ID_TOGGLE_COLLISION_VISIBILITY, icon='HIDE_OFF')

        self.drawCollisionCreateSection(context)
        self.drawCollisionLayersSection(context)
        self.drawCollisionMaskSection(context)
    
    def canDrawCollisionButtons(self) -> bool:
        return len(bpy.context.selected_objects) >= 2
    
    def drawCollisionCreateSection(self, context : bpy.types.Context):
        sge_utils.LayoutSection(self.layout, sge_statics.SGE_COLLISION_CREATE_EXPANDED, 'Create')
        if not getattr(context.scene, sge_statics.SGE_COLLISION_CREATE_EXPANDED):
            return
        
        if not sge_utils.ActiveModeIs("OBJECT"):
            self.layout.label(text="Switch to Object Mode.", icon='INFO')
        elif not self.canDrawCollisionButtons():
            self.layout.label(text="Select your collider Object(s).", icon='INFO')
            
        convertButtons = self.layout.row()
        convertStaticCollisionButtons = convertButtons.column()
        convertStaticCollisionButtons.enabled = self.canDrawCollisionButtons()    
        convertStaticCollisionButtons.operator(sge_statics.SGE_ID_COLLISIONS_CONVERT_TO_BOX, icon='CUBE')
        convertStaticCollisionButtons.operator(sge_statics.SGE_ID_COLLISIONS_CONVERT_TO_CONVEX, icon='MESH_ICOSPHERE')

    def drawGodotCollisionLayers(self, colObject, enumType):
            col = self.layout.column()
            row = col.row()

            split = row.split(factor=0.5)

            col1 = split.column()
            col2 = split.column()

            for i in range(1, 31):
                identifier = f"LAYER_{i}"
                target_col = col1 if i <= 16 else col2
                target_col.prop_enum(colObject, enumType, identifier)
                

    def drawCollisionLayersSection(self, context : bpy.types.Context):
        sge_utils.LayoutSection(self.layout, sge_statics.SGE_COLLISION_LAYERS_EXPANDED, 'Collision Layer')
        if not getattr(context.scene, sge_statics.SGE_COLLISION_LAYERS_EXPANDED):
            return
        
        colObject = collision_utils.hasCollisionObject(context.selected_objects)
        if colObject is None:
            self.layout.row().label(text='Select a collision object', icon='INFO')
        else:
            self.drawGodotCollisionLayers(colObject, sge_statics.SGE_COLLISION_LAYER_ENUM)


    def drawCollisionMaskSection(self, context : bpy.types.Context):
        sge_utils.LayoutSection(self.layout, sge_statics.SGE_COLLISION_MASKS_EXPANDED, 'Collision Mask')
        if not getattr(context.scene, sge_statics.SGE_COLLISION_MASKS_EXPANDED):
            return
        
        colObject = collision_utils.hasCollisionObject(context.selected_objects)
        if colObject is None:
            self.layout.row().label(text='Select a collision object', icon='INFO')
        else:
            self.drawGodotCollisionLayers(colObject, sge_statics.SGE_COLLISION_MASK_ENUM)


    
    class SGE_OT_CreateBoxCollisionButton(bpy.types.Operator):
        bl_label = 'Convert to Box collision'
        bl_idname = sge_statics.SGE_ID_COLLISIONS_CONVERT_TO_BOX
        bl_description = (
            'Convert selected meshes to box collisions'
        )

        def execute(self, context):
            ConvertedObjs = collision_utils.CreateCollision("Box")
            if len(ConvertedObjs) > 0:
                self.report(
                    {'INFO'},
                    str(len(ConvertedObjs)) +
                    " object(s) of the selection have been" +
                    " converted to Box collisions.")
            else:
                self.report(
                    {'WARNING'},
                    "Please select two objects." +
                    " (Active object is the owner of the collision)")
            return {'FINISHED'}
        
    class SGE_OT_CreateConvexCollisionButon(bpy.types.Operator):
        bl_label ='Convert to Convex collision'
        bl_idname = sge_statics.SGE_ID_COLLISIONS_CONVERT_TO_CONVEX
        bl_description = (
            'Convert selected meshes to convex collisions'
        )

        def execute(self, context):
            ConvertedObjs = collision_utils.CreateCollision("Convex")
            if len(ConvertedObjs) > 0:
                self.report(
                    {'INFO'},
                    str(len(ConvertedObjs)) +
                    " object(s) of the selection have been" +
                    " converted to Convex collisions.")
            else:
                self.report(
                    {'WARNING'},
                    "Please select two objects." +
                    " (Active object is the owner of the collision)")
            return {'FINISHED'}

    class SGE_OT_ToggleCollisionVisibility(bpy.types.Operator):
        bl_label ='Toggle collision visibility'
        bl_idname = sge_statics.SGE_ID_TOGGLE_COLLISION_VISIBILITY
        bl_description = (
            'Toggles the visibility of all collision meshes'
        )

        _collisionToggleLastValue = False

        def execute(self, context):
            global _collisionToggleLastValue
            col_objects: list[bpy.types.Object] = []
            for obj in context.scene.objects:
                if collision_utils.isCollisionObject(obj):
                    col_objects.append(obj)
            
            for col in col_objects:
                col.hide_viewport = _collisionToggleLastValue

            _collisionToggleLastValue = not _collisionToggleLastValue

            return {'FINISHED'}

classRefs = [
    SGE_PT_CollisionsPanel,
    SGE_PT_CollisionsPanel.SGE_OT_CreateBoxCollisionButton,
    SGE_PT_CollisionsPanel.SGE_OT_ToggleCollisionVisibility,
    SGE_PT_CollisionsPanel.SGE_OT_CreateConvexCollisionButon,
]