import mathutils
import os
import bpy
from .. import sge_statics

def ApplyExportTransform(obj):

    newMatrix = obj.matrix_world @ mathutils.Matrix.Translation((0, 0, 0))
    saveScale = obj.scale * 1

    # Moves object to the center of the scene for export
    MoveToCenter = getattr(obj, sge_statics.SGE_OBJECT_MOVE_TO_ZERO)
    RotateToZero = getattr(obj, sge_statics.SGE_OBJECT_ROTATE_TO_ZERO)

    if MoveToCenter:
        mat_trans = mathutils.Matrix.Translation((0, 0, 0))
        mat_rot = newMatrix.to_quaternion().to_matrix()
        newMatrix = mat_trans @ mat_rot.to_4x4()

    obj.matrix_world = newMatrix
    # Turn object to the center of the scene for export
    if RotateToZero:
        mat_trans = mathutils.Matrix.Translation(newMatrix.to_translation())
        mat_rot = mathutils.Matrix.Rotation(0, 4, 'X')
        newMatrix = mat_trans @ mat_rot

    obj.matrix_world = newMatrix
    obj.scale = saveScale

def ApplyBoxCollider(collider_obj:bpy.types.Object):
    with bpy.context.temp_override(selected_objects=[collider_obj], active_object=collider_obj):
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    

def HasRelativeExportPaths(objects, context: bpy.types.Context):
    def is_relative(path: str):
        # Blender-relative OR normal relative path
        return path.startswith("//") or not os.path.isabs(path)

    globalExportPath = getattr(
        context.scene,
        sge_statics.SGE_EXPORT_GLOBAL_EXPORT_DIR_PATH,
        ""
    )

    if globalExportPath:
        print('globalExportPath= ' + globalExportPath)
        if is_relative(globalExportPath):
            return True

    for obj in objects:
        if not hasattr(obj, sge_statics.SGE_EXPORT_PEROBJECT_EXPORT_PATH):
            continue

        objectExportPath = getattr(
            obj,
            sge_statics.SGE_EXPORT_PEROBJECT_EXPORT_PATH,
            ""
        )

        if not objectExportPath:
            continue

        print('objectExportPath= ' + objectExportPath)

        if is_relative(objectExportPath):
            return True
    
    return False

def GetExportChildren(root_obj : bpy.types.Object) -> list[bpy.types.Object]:
    result = []

    def recurse(obj):
        export_attr = getattr(obj, sge_statics.SGE_OBJECT_EXPORT_ENUM)
        if export_attr == sge_statics.SGE_OBJECT_EXPORT_AUTO:
            result.append(obj)
        # don't export the children of objects that are marked to specifically not be exported
        elif export_attr == sge_statics.SGE_OBJECT_EXPORT_NOEXPORT:
            return

        for child in obj.children:
            recurse(child)

    recurse(root_obj)
    return result


class ExportContext:
    def __init__(self):
        self.original_selection = []
        self.duplicates = []
        self.name_map = {}  # {duplicate: original_name}
        self.original_names = {}  # {original_obj: original_name}
        self.duplicate_suffix = '_TEMPDUPLICATE'

    def duplicate_meshes(self):
        # Store original selection
        self.original_selection = list(bpy.context.selected_objects)

        # Store original names (by object, not string!)
        self.original_names = {obj: obj.name for obj in self.original_selection}

        # Duplicate
        bpy.ops.object.duplicate()
        self.duplicates = list(bpy.context.selected_objects)

        # Build lookup BEFORE renaming anything
        name_to_original = {obj.name: obj for obj in self.original_selection}

        # Track which originals we've already renamed
        renamed_originals = set()

        for dup in self.duplicates:
            # Handle Blender suffix like ".001"
            base_name = dup.name.rsplit(".", 1)[0]

            if base_name in name_to_original:
                orig = name_to_original[base_name]

                # Rename original ONLY ONCE
                if orig not in renamed_originals:
                    orig.name = self.original_names[orig] + self.duplicate_suffix
                    renamed_originals.add(orig)

                # Assign correct name to duplicate
                dup.name = self.original_names[orig]
                self.name_map[dup] = self.original_names[orig]

        # Make mesh data single-user
        for obj in self.duplicates:
            if obj.data:
                obj.data = obj.data.copy()

    def cleanup(self):
        # Delete duplicates (they should still be selected)
        bpy.ops.object.delete()

    def restore_names(self):
        # Restore original names safely
        for obj, original_name in self.original_names.items():
            obj.name = original_name


def prepare_meshes(objs: list[bpy.types.Object]):
    # Find roots (objects without parent OR parent not in selection)
    obj_set = set(objs)
    roots = [obj for obj in objs if obj.parent not in obj_set]
    colliders = [
        obj for obj in objs
        if obj.get(sge_statics.SGE_COLLISION_IS_BOX_COLLIDER, False)
    ] 

    # Apply export transform only to roots
    for obj in roots:
        ApplyExportTransform(obj)

    for col in colliders:
        ApplyBoxCollider(col)    


def export_mesh_with_children(filepath):
    ctx = ExportContext()

    ctx.duplicate_meshes()
    prepare_meshes(ctx.duplicates)

    # get export format
    format = getattr(bpy.context.scene, sge_statics.SGE_EXPORT_FORMAT_ENUM)
    exportFormatString = ''
    if format == sge_statics.SGE_EXPORT_FORMAT_GLB:
        exportFormatString = 'GLB'
    elif format == sge_statics.SGE_EXPORT_FORMAT_GLTF:
        exportFormatString = 'GLTF_SEPARATE'

    # Export glb file
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        check_existing=False,
        use_selection=True,
        export_apply=True,
        export_format=exportFormatString,
        export_animations=False,
        export_extras=True,
        export_image_format='NONE',
        export_materials='EXPORT',

    )

    ctx.cleanup()
    ctx.restore_names()