import bpy
from bpy.types import Operator
from bpy.props import IntProperty

class UNIVERSALGTA_OT_add_custom_entry(Operator):
    """Agregar entrada personalizada de mapeo"""
    bl_idname = "universalgta.add_custom_entry"
    bl_label = "Add Custom Entry"
    bl_description = "Add a new bone mapping entry"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Agregar nueva entrada
        new_mapping = settings.bone_mappings.add()
        new_mapping.enabled = True
        new_mapping.detection_method = "Manual"
        new_mapping.confidence = 0.0
        new_mapping.source_bone = ""
        new_mapping.target_bone = ""
        
        # Establecer como activo
        settings.bone_mappings_index = len(settings.bone_mappings) - 1
        
        self.report({'INFO'}, "Nueva entrada de mapeo agregada")
        return {'FINISHED'}


class UNIVERSALGTA_OT_remove_mapping_entry(Operator):
    """Eliminar entrada de mapeo"""
    bl_idname = "universalgta.remove_mapping_entry"
    bl_label = "Remove Mapping Entry"
    bl_description = "Remove this bone mapping entry"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: IntProperty(
        name="Index",
        description="Index of the mapping to remove",
        default=0
    )
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if 0 <= self.index < len(settings.bone_mappings):
            settings.bone_mappings.remove(self.index)
            
            # Ajustar índice activo
            if settings.bone_mappings_index >= len(settings.bone_mappings):
                settings.bone_mappings_index = max(0, len(settings.bone_mappings) - 1)
            
            self.report({'INFO'}, "Entrada de mapeo eliminada")
        else:
            self.report({'ERROR'}, "Índice de mapeo inválido")
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_clear_mappings(Operator):
    """Limpiar todos los mapeos"""
    bl_idname = "universalgta.clear_mappings"
    bl_label = "Clear All Mappings"
    bl_description = "Clear all bone mappings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        settings.bone_mappings.clear()
        settings.bone_mappings_index = 0
        
        self.report({'INFO'}, "Todos los mapeos eliminados")
        return {'FINISHED'}


class UNIVERSALGTA_OT_move_mapping_up(Operator):
    """Mover mapeo hacia arriba"""
    bl_idname = "universalgta.move_mapping_up"
    bl_label = "Move Up"
    bl_description = "Move mapping up in the list"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        
        if index > 0:
            settings.bone_mappings.move(index, index - 1)
            settings.bone_mappings_index = index - 1
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_move_mapping_down(Operator):
    """Mover mapeo hacia abajo"""
    bl_idname = "universalgta.move_mapping_down"
    bl_label = "Move Down"
    bl_description = "Move mapping down in the list"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        
        if index < len(settings.bone_mappings) - 1:
            settings.bone_mappings.move(index, index + 1)
            settings.bone_mappings_index = index + 1
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_add_target_bones(Operator):
    """Agregar todos los huesos del target automáticamente"""
    bl_idname = "universalgta.add_target_bones"
    bl_label = "Add Target Bones"
    bl_description = "Add all bones from target armature as empty mappings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No target armature selected")
            return {'CANCELLED'}
        
        # Limpiar mapeos existentes
        settings.bone_mappings.clear()
        
        # Agregar todos los huesos del target
        for bone in settings.target_armature.data.bones:
            mapping = settings.bone_mappings.add()
            mapping.target_bone = bone.name
            mapping.source_bone = ""
            mapping.enabled = False
            mapping.detection_method = "Manual"
            mapping.confidence = 0.0
        
        settings.bone_mappings_index = 0
        
        self.report({'INFO'}, f"Agregados {len(settings.bone_mappings)} huesos del target")
        return {'FINISHED'}


class UNIVERSALGTA_OT_auto_detect_mappings(Operator):
    """Detectar automáticamente mapeos basados en nombres"""
    bl_idname = "universalgta.auto_detect_mappings"
    bl_label = "Auto Detect Mappings"
    bl_description = "Automatically detect bone mappings based on bone names"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature or not settings.target_armature:
            self.report({'ERROR'}, "Both source and target armatures are required")
            return {'CANCELLED'}
        
        # Llamar al detector automático existente
        bpy.ops.universalgta.auto_detect_bones()
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_validate_mappings(Operator):
    """Validar mapeos actuales"""
    bl_idname = "universalgta.validate_mappings"
    bl_label = "Validate Mappings"
    bl_description = "Validate current bone mappings"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature or not settings.target_armature:
            self.report({'ERROR'}, "Both armatures are required for validation")
            return {'CANCELLED'}
        
        src_bones = [b.name for b in settings.source_armature.data.bones]
        tgt_bones = [b.name for b in settings.target_armature.data.bones]
        
        issues = []
        valid_mappings = 0
        
        for i, mapping in enumerate(settings.bone_mappings):
            if mapping.enabled:
                if not mapping.source_bone or not mapping.target_bone:
                    issues.append(f"Mapping {i+1}: Empty source or target bone")
                elif mapping.source_bone not in src_bones:
                    issues.append(f"Mapping {i+1}: Source bone '{mapping.source_bone}' not found")
                elif mapping.target_bone not in tgt_bones:
                    issues.append(f"Mapping {i+1}: Target bone '{mapping.target_bone}' not found")
                else:
                    valid_mappings += 1
        
        if issues:
            issue_text = "\n".join(issues[:5])  # Mostrar solo los primeros 5
            if len(issues) > 5:
                issue_text += f"\n... and {len(issues) - 5} more issues"
            self.report({'WARNING'}, f"Validation issues found:\n{issue_text}")
        else:
            self.report({'INFO'}, f"All mappings valid! {valid_mappings} mappings ready for conversion")
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_load_mapping(Operator):
    """Cargar mapeo desde archivo"""
    bl_idname = "universalgta.load_mapping"
    bl_label = "Load Mapping"
    bl_description = "Load bone mapping from file"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Implementar carga desde archivo
        self.report({'INFO'}, "Load mapping functionality - coming soon")
        return {'FINISHED'}


class UNIVERSALGTA_OT_save_mapping(Operator):
    """Guardar mapeo a archivo"""
    bl_idname = "universalgta.save_mapping"
    bl_label = "Save Mapping"
    bl_description = "Save bone mapping to file"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Implementar guardado a archivo
        self.report({'INFO'}, "Save mapping functionality - coming soon")
        return {'FINISHED'}


class UNIVERSALGTA_OT_duplicate_mapping(Operator):
    """Duplicar mapeo seleccionado"""
    bl_idname = "universalgta.duplicate_mapping"
    bl_label = "Duplicate Mapping"
    bl_description = "Duplicate the selected bone mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        
        if 0 <= index < len(settings.bone_mappings):
            original = settings.bone_mappings[index]
            
            # Crear duplicado
            duplicate = settings.bone_mappings.add()
            duplicate.source_bone = original.source_bone
            duplicate.target_bone = original.target_bone + "_copy"
            duplicate.enabled = original.enabled
            duplicate.detection_method = "Manual"
            duplicate.confidence = original.confidence
            
            settings.bone_mappings_index = len(settings.bone_mappings) - 1
            
            self.report({'INFO'}, "Mapping duplicated")
        else:
            self.report({'ERROR'}, "No mapping selected")
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_invert_mapping(Operator):
    """Invertir mapeo seleccionado"""
    bl_idname = "universalgta.invert_mapping"
    bl_label = "Invert Mapping"
    bl_description = "Invert source and target bones in the mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        
        if 0 <= index < len(settings.bone_mappings):
            mapping = settings.bone_mappings[index]
            
            # Intercambiar source y target
            temp = mapping.source_bone
            mapping.source_bone = mapping.target_bone
            mapping.target_bone = temp
            
            self.report({'INFO'}, "Mapping inverted")
        else:
            self.report({'ERROR'}, "No mapping selected")
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_enable_all_mappings(Operator):
    """Habilitar todos los mapeos"""
    bl_idname = "universalgta.enable_all_mappings"
    bl_label = "Enable All"
    bl_description = "Enable all bone mappings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        for mapping in settings.bone_mappings:
            mapping.enabled = True
        
        self.report({'INFO'}, f"All {len(settings.bone_mappings)} mappings enabled")
        return {'FINISHED'}


class UNIVERSALGTA_OT_disable_all_mappings(Operator):
    """Deshabilitar todos los mapeos"""
    bl_idname = "universalgta.disable_all_mappings"
    bl_label = "Disable All"
    bl_description = "Disable all bone mappings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        for mapping in settings.bone_mappings:
            mapping.enabled = False
        
        self.report({'INFO'}, f"All {len(settings.bone_mappings)} mappings disabled")
        return {'FINISHED'}


class UNIVERSALGTA_OT_enable_high_confidence(Operator):
    """Habilitar solo mapeos de alta confianza"""
    bl_idname = "universalgta.enable_high_confidence"
    bl_label = "Enable High Confidence"
    bl_description = "Enable only high confidence mappings (>0.7)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        enabled_count = 0
        for mapping in settings.bone_mappings:
            if mapping.confidence > 0.7:
                mapping.enabled = True
                enabled_count += 1
            else:
                mapping.enabled = False
        
        self.report({'INFO'}, f"{enabled_count} high confidence mappings enabled")
        return {'FINISHED'}


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_add_custom_entry,
    UNIVERSALGTA_OT_remove_mapping_entry,
    UNIVERSALGTA_OT_clear_mappings,
    UNIVERSALGTA_OT_move_mapping_up,
    UNIVERSALGTA_OT_move_mapping_down,
    UNIVERSALGTA_OT_add_target_bones,
    UNIVERSALGTA_OT_auto_detect_mappings,
    UNIVERSALGTA_OT_validate_mappings,
    UNIVERSALGTA_OT_load_mapping,
    UNIVERSALGTA_OT_save_mapping,
    UNIVERSALGTA_OT_duplicate_mapping,
    UNIVERSALGTA_OT_invert_mapping,
    UNIVERSALGTA_OT_enable_all_mappings,
    UNIVERSALGTA_OT_disable_all_mappings,
    UNIVERSALGTA_OT_enable_high_confidence,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)