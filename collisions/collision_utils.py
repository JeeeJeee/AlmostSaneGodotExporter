import bpy
import bmesh
from .. import sge_statics

def CreateCollisionMaterial():
    
    collisionMat = bpy.data.materials.get("GodotCollision")
    if collisionMat is None:
        collisionMat = bpy.data.materials.new(name="GodotCollision")

    collisionMat.diffuse_color = (0, 0.6, 0, 0.11)
    collisionMat.use_nodes = False

    return collisionMat

def CreateCollision(collisionType: str):

    def DeselectAllWithoutActive():
        for obj in bpy.context.selected_objects:
            if obj != bpy.context.active_object:
                obj.select_set(False)

    ownerObj = bpy.context.active_object
    objList = bpy.context.selected_objects
    if ownerObj is None:
        return []

    collisionObjs = []

    for obj in objList:
        DeselectAllWithoutActive()
        obj.select_set(True)
        if obj == ownerObj:
            continue
        
        if obj.type == 'MESH':
            ConvertToConvexHull(obj)
            obj.modifiers.clear()
            obj.data
            obj.data.materials.clear()
            obj.active_material_index = 0
            obj.data.materials.append(CreateCollisionMaterial())

            obj.show_wire = True
            obj.show_transparent = True
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            setattr(obj, sge_statics.SGE_COLLISION_IS_COLLIDER, True)
            setattr(obj, sge_statics.SGE_OBJECT_EXPORT_ENUM, sge_statics.SGE_OBJECT_EXPORT_AUTO)

            # this is important because just registering an enum property doesn't really create the object ID
            if not sge_statics.SGE_COLLISION_LAYER_ENUM in obj.keys():
                obj[sge_statics.SGE_COLLISION_LAYER_ENUM] = 1
            if not sge_statics.SGE_COLLISION_MASK_ENUM in obj.keys():
                obj[sge_statics.SGE_COLLISION_MASK_ENUM] = 1

            if collisionType == 'Box':
                obj[sge_statics.SGE_COLLISION_IS_BOX_COLLIDER] = True
                obj[sge_statics.SGE_COLLISION_IS_CONVEX_COLLIDER] = False
                # setattr(obj, sge_statics.SGE_COLLISION_IS_BOX_COLLIDER, True)
                # setattr(obj, sge_statics.SGE_COLLISION_IS_CONVEX_COLLIDER, False)
            elif collisionType == 'Convex':
                obj[sge_statics.SGE_COLLISION_IS_BOX_COLLIDER] = False
                obj[sge_statics.SGE_COLLISION_IS_CONVEX_COLLIDER] = True
                # setattr(obj, sge_statics.SGE_COLLISION_IS_BOX_COLLIDER, False)
                # setattr(obj, sge_statics.SGE_COLLISION_IS_CONVEX_COLLIDER, True)
            
            collisionObjs.append(obj)

        # Set the collision hidden for renders
        obj.hide_render = True

    DeselectAllWithoutActive()
    for obj in objList:
        obj.select_set(True)  # Resets previous selected object
    return collisionObjs

def ConvertToConvexHull(obj : bpy.types.Object):
    # Convert obj to Convex Hull
    mesh = obj.data
    if not mesh.is_editmode:
        bm = bmesh.new()
        bm.from_mesh(mesh)  # Mesh to Bmesh
        convex_hull = bmesh.ops.convex_hull(
            bm, input=bm.verts,
            use_existing_faces=True
        )
        bm.to_mesh(mesh)  # BMesh to Mesh


def hasCollisionObject(objs) -> bpy.types.Object:
    for obj in objs:
        if getattr(obj, sge_statics.SGE_COLLISION_IS_COLLIDER):
            return obj
    return None

def isCollisionObject(obj) -> bool:
    return getattr(obj, sge_statics.SGE_COLLISION_IS_COLLIDER)