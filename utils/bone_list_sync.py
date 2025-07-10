import bpy

def sync_bone_collections(context):
    """
    Sincroniza las colecciones source_bones_collection y target_bones_collection
    con los huesos actuales de los armatures seleccionados.
    """
    settings = context.scene.universal_gta_settings
    # Limpiar colecciones
    settings.source_bones_collection.clear()
    settings.target_bones_collection.clear()
    # Poblar source
    if settings.source_armature and settings.source_armature.type == 'ARMATURE':
        for bone in settings.source_armature.data.bones:
            item = settings.source_bones_collection.add()
            item.source_bone = bone.name
            item.target_bone = ""
            item.enabled = True
            item.detection_method = "Manual"
            item.confidence = 1.0
    # Poblar target
    if settings.target_armature and settings.target_armature.type == 'ARMATURE':
        for bone in settings.target_armature.data.bones:
            item = settings.target_bones_collection.add()
            item.source_bone = ""
            item.target_bone = bone.name
            item.enabled = True
            item.detection_method = "Manual"
            item.confidence = 1.0
