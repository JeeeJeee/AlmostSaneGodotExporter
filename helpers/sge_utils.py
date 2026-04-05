import bpy

def LayoutSection(layout, PropName, PropLabel, shouldEmboss = False):
    scene = bpy.context.scene

    if not hasattr(scene, PropName):
        raise AttributeError(f"Scene has no property '{PropName}'")

    expanded = getattr(scene, PropName)
    
    tria_icon = "TRIA_DOWN" if expanded else "TRIA_RIGHT"
    layout.row().prop(scene, PropName, icon=tria_icon, icon_only=True, text=PropLabel, emboss=shouldEmboss)
    return expanded

def ActiveModeIs(targetMode):
    # Return True is active mode ==
    obj = bpy.context.active_object
    if obj is not None:
        if obj.mode == targetMode:
            return True
    return False