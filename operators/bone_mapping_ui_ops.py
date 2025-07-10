import bpy
from bpy.types import Operator
from ..utils.bone_list_sync import sync_bone_collections

class UNIVERSALGTA_OT_SyncBoneLists(Operator):
    bl_idname = "universalgta.sync_bone_lists"
    bl_label = "Sincronizar listas de huesos"
    bl_description = "Actualiza las listas de huesos fuente y destino según los armatures seleccionados"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sync_bone_collections(context)
        self.report({'INFO'}, "Listas de huesos sincronizadas")
        return {'FINISHED'}

class UNIVERSALGTA_OT_SelectSourceBone(Operator):
    bl_idname = "universalgta.select_source_bone"
    bl_label = "Seleccionar hueso fuente en 3D"
    bl_description = "Selecciona el hueso fuente activo en el 3D View"
    from_list: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        settings = context.scene.universal_gta_settings
        idx = settings.source_bones_index
        if settings.source_armature and 0 <= idx < len(settings.source_bones_collection):
            bone_name = settings.source_bones_collection[idx].source_bone
            bpy.ops.object.mode_set(mode='POSE')
            context.view_layer.objects.active = settings.source_armature
            for pb in settings.source_armature.pose.bones:
                pb.bone.select = False
            if bone_name in settings.source_armature.pose.bones:
                pb = settings.source_armature.pose.bones[bone_name]
                pb.bone.select = True
                settings.source_armature.data.bones.active = pb.bone
        return {'FINISHED'}

class UNIVERSALGTA_OT_SelectTargetBone(Operator):
    bl_idname = "universalgta.select_target_bone"
    bl_label = "Seleccionar hueso destino en 3D"
    bl_description = "Selecciona el hueso destino activo en el 3D View"
    from_list: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        settings = context.scene.universal_gta_settings
        idx = settings.target_bones_index
        if settings.target_armature and 0 <= idx < len(settings.target_bones_collection):
            bone_name = settings.target_bones_collection[idx].target_bone
            bpy.ops.object.mode_set(mode='POSE')
            context.view_layer.objects.active = settings.target_armature
            for pb in settings.target_armature.pose.bones:
                pb.bone.select = False
            if bone_name in settings.target_armature.pose.bones:
                pb = settings.target_armature.pose.bones[bone_name]
                pb.bone.select = True
                settings.target_armature.data.bones.active = pb.bone
        return {'FINISHED'}
