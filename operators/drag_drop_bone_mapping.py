import bpy
from bpy.types import Operator

class UNIVERSALGTA_OT_StartBoneDrag(Operator):
    bl_idname = "universalgta.start_bone_drag"
    bl_label = "Iniciar Drag & Drop de hueso"
    bl_description = "Arrastra un hueso fuente sobre uno destino para crear un mapeo"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Aquí se podría activar un modo de arrastre visual
        self.report({'INFO'}, "Arrastra un hueso fuente sobre uno destino para mapear")
        return {'FINISHED'}

class UNIVERSALGTA_OT_DropBoneMapping(Operator):
    bl_idname = "universalgta.drop_bone_mapping"
    bl_label = "Soltar mapeo de hueso"
    bl_description = "Crea un mapeo al soltar un hueso fuente sobre uno destino"
    bl_options = {'REGISTER', 'UNDO'}

    source_bone: bpy.props.StringProperty()
    target_bone: bpy.props.StringProperty()

    def execute(self, context):
        settings = context.scene.universal_gta_settings
        # Crear o actualizar mapeo
        found = False
        for m in settings.bone_mappings:
            if m.source_bone == self.source_bone:
                m.target_bone = self.target_bone
                m.enabled = True
                found = True
                break
        if not found:
            item = settings.bone_mappings.add()
            item.source_bone = self.source_bone
            item.target_bone = self.target_bone
            item.enabled = True
            item.detection_method = "Manual"
            item.confidence = 1.0
        self.report({'INFO'}, f"Mapeado: {self.source_bone} → {self.target_bone}")
        return {'FINISHED'}
