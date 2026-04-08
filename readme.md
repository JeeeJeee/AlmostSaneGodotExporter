Almost Sane Godot Exporter
---
I have found Godots 3D workflow to be extremely painful to work with, so I've spent some time making this addon.  
This addon requires its [godot importer counterpart](https://github.com/JeeeJeee/AlmostSaneGodotImporter) to get any real use out of it. *Though exporting itself still works*  
The project is a slimmed down version of [blender-for-unrealengine](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/) modified specifically for Godot.

### Features
*This addon is focused on meshes. No effort was made to support animations/actions etc.*
- Exporting multiple separate .glb files from a single .blend file
- Adding convex and box collision shapes in blender
- Setting collision layers and masks directly inside blender *(no need to do any scene inheritance in godot)*
- Convenience functions for scene export (*moving/rotating objects to zero*)
