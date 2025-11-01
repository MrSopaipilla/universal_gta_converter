"""
Operadores de validación de mapeos
"""

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty


class UNIVERSALGTA_OT_validate_mappings_fixed(Operator):
    """Validar mapeos de huesos - Version corregida"""
    bl_idname = "universalgta.validate_mappings_fixed"
    bl_label = "Validate Mappings (Fixed)"
    bl_description = "Validación robusta de mapeos de huesos"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature or not settings.target_armature:
            self.report({'ERROR'}, "Selecciona ambos armatures")
            return {'CANCELLED'}
        
        try:
            # Obtener huesos con método robusto
            source_bones = self.get_armature_bones_robust(settings.source_armature)
            target_bones = self.get_armature_bones_robust(settings.target_armature)
            
            if not source_bones:
                self.report({'ERROR'}, "No se pudieron obtener huesos del source armature")
                return {'CANCELLED'}
            
            if not target_bones:
                self.report({'ERROR'}, "No se pudieron obtener huesos del target armature")
                return {'CANCELLED'}
            
            # Validar mapeos
            valid_count = 0
            invalid_count = 0
            
            for mapping in settings.bone_mappings:
                if mapping.enabled:
                    source_exists = self.bone_exists_flexible(mapping.source_bone, source_bones)
                    target_exists = self.bone_exists_flexible(mapping.target_bone, target_bones)
                    
                    if source_exists and target_exists:
                        valid_count += 1
                    else:
                        invalid_count += 1
                        mapping.enabled = False  # Deshabilitar inválidos
            
            message = f"Validación: {valid_count} válidos, {invalid_count} deshabilitados"
            self.report({'INFO'}, message)
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en validación: {e}")
            return {'CANCELLED'}
    
    def get_armature_bones_robust(self, armature_obj):
        """Obtener huesos de armature con múltiples métodos"""
        if not armature_obj or armature_obj.type != 'ARMATURE':
            return []
        
        try:
            # Método 1: pose.bones
            if armature_obj.pose and armature_obj.pose.bones:
                return [b.name for b in armature_obj.pose.bones]
        except:
            pass
        
        try:
            # Método 2: data.bones
            if armature_obj.data and armature_obj.data.bones:
                return [b.name for b in armature_obj.data.bones]
        except:
            pass
        
        return []
    
    def bone_exists_flexible(self, bone_name, bone_list):
        """Verificación flexible de existencia de hueso"""
        if not bone_name or not bone_list:
            return False
        
        # Coincidencia exacta
        if bone_name in bone_list:
            return True
        
        # Coincidencia con espacios normalizados
        bone_clean = bone_name.strip()
        for bone in bone_list:
            if bone.strip() == bone_clean:
                return True
        
        # Coincidencia case-insensitive
        bone_lower = bone_name.lower()
        for bone in bone_list:
            if bone.lower() == bone_lower:
                return True
        
        return False


class UNIVERSALGTA_OT_fix_mappings_automatically(Operator):
    """Auto-corregir mapeos de huesos automáticamente"""
    bl_idname = "universalgta.fix_mappings_automatically"
    bl_label = "Fix Mappings Automatically"
    bl_description = "Corrige automáticamente mapeos de huesos usando normalización"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No hay target armature")
            return {'CANCELLED'}
        
        try:
            # Intentar usar el normalizador si está disponible
            fixes_applied = 0
            
            try:
                from ..gta_sa_normalizer import GTASANormalizer
                
                for mapping in settings.bone_mappings:
                    if mapping.target_bone:
                        normalized = GTASANormalizer.normalize_bone_name(mapping.target_bone)
                        if normalized and normalized != mapping.target_bone:
                            mapping.target_bone = normalized
                            fixes_applied += 1
                
                message = f"Auto-fix: {fixes_applied} mapeos corregidos"
                
            except ImportError:
                # Fallback: auto-fix básico sin normalizer
                target_bones = [b.name for b in settings.target_armature.pose.bones]
                
                for mapping in settings.bone_mappings:
                    if mapping.target_bone and mapping.target_bone not in target_bones:
                        # Buscar coincidencia similar
                        for target_bone in target_bones:
                            if target_bone.strip().lower() == mapping.target_bone.strip().lower():
                                mapping.target_bone = target_bone
                                fixes_applied += 1
                                break
                
                message = f"Auto-fix básico: {fixes_applied} mapeos corregidos"
            
            self.report({'INFO'}, message)
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en auto-fix: {e}")
            return {'CANCELLED'}


class UNIVERSALGTA_OT_ignore_naming_warnings(Operator):
    """Ignorar advertencias de nombres y continuar"""
    bl_idname = "universalgta.ignore_naming_warnings"
    bl_label = "Ignore Naming Warnings"
    bl_description = "Ignora advertencias de nombres y permite continuar"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Marcar como ignorado (podríamos agregar una propiedad para esto)
        if hasattr(settings, 'ignore_naming_warnings'):
            settings.ignore_naming_warnings = True
        
        self.report({'INFO'}, "Advertencias de nombres ignoradas")
        return {'FINISHED'}


class UNIVERSALGTA_OT_validate_mappings_and_disable_invalid(Operator):
    """Validar mapeos y deshabilitar los inválidos - OPERADOR FALTANTE"""
    bl_idname = "universalgta.validate_mappings_and_disable_invalid"
    bl_label = "Validate & Disable Invalid"
    bl_description = "Valida mapeos y deshabilita automáticamente los inválidos"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature or not settings.target_armature:
            self.report({'ERROR'}, "Selecciona ambos armatures")
            return {'CANCELLED'}
        
        try:
            print(f"[VALIDATE] Iniciando validación de {len(settings.bone_mappings)} mapeos...")
            
            # Obtener listas de huesos
            source_bones = [b.name for b in settings.source_armature.pose.bones]
            target_bones = [b.name for b in settings.target_armature.pose.bones]
            
            valid_count = 0
            disabled_count = 0
            
            for i, mapping in enumerate(settings.bone_mappings):
                if not mapping.enabled:
                    continue
                
                # Verificar source bone
                source_valid = self.bone_exists_flexible(mapping.source_bone, source_bones)
                
                # Verificar target bone
                target_valid = self.bone_exists_flexible(mapping.target_bone, target_bones)
                
                if source_valid and target_valid:
                    valid_count += 1
                    print(f"[VALIDATE] ✅ Mapeo #{i+1}: {mapping.source_bone} -> {mapping.target_bone}")
                else:
                    mapping.enabled = False
                    disabled_count += 1
                    issues = []
                    if not source_valid:
                        issues.append("source no existe")
                    if not target_valid:
                        issues.append("target no existe")
                    print(f"[VALIDATE] ❌ Mapeo #{i+1} deshabilitado: {' y '.join(issues)}")
            
            message = f"Validación completada: {valid_count} válidos, {disabled_count} deshabilitados"
            self.report({'INFO'}, message)
            
            return {'FINISHED'}
            
        except Exception as e:
            print(f"[VALIDATE] Error: {e}")
            self.report({'ERROR'}, f"Error en validación: {e}")
            return {'CANCELLED'}
    
    def bone_exists_flexible(self, bone_name, bone_list):
        """Verificación flexible de existencia de hueso"""
        if not bone_name or not bone_list:
            return False
        
        # Coincidencia exacta
        if bone_name in bone_list:
            return True
        
        # Coincidencia con espacios normalizados
        bone_clean = bone_name.strip()
        for bone in bone_list:
            if bone.strip() == bone_clean:
                return True
        
        # Coincidencia case-insensitive
        bone_lower = bone_name.lower()
        for bone in bone_list:
            if bone.lower() == bone_lower:
                return True
        
        return False


# CLASES PARA REGISTRAR - TODAS LAS NECESARIAS
classes = [
    UNIVERSALGTA_OT_validate_mappings_fixed,
    UNIVERSALGTA_OT_fix_mappings_automatically,
    UNIVERSALGTA_OT_ignore_naming_warnings,
    UNIVERSALGTA_OT_validate_mappings_and_disable_invalid,
]


def register():
    """Registrar operadores de validación"""
    for cls in classes:
        bpy.utils.register_class(cls)
    print("[VALIDATION] Operadores de validación registrados correctamente")


def unregister():
    """Desregistrar operadores de validación"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("[VALIDATION] Operadores de validación desregistrados")
