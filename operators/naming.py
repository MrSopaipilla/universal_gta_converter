"""
Operadores para sistema de nombres personalizados
"""

import bpy
import re
from bpy.types import Operator


class UNIVERSALGTA_OT_apply_custom_names(Operator):
    """Aplicar nombres personalizados al skin y autor"""
    bl_idname = "universalgta.apply_custom_names"
    bl_label = "Apply Custom Names"
    bl_description = "Aplica los nombres personalizados al skin y autor"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Validar nombres antes de aplicar
        if not self.validate_names(settings):
            return {'CANCELLED'}
        
        # Aplicar nombre del skin
        success_skin = self.apply_skin_name(settings)
        
        # Aplicar nombre del autor
        success_author = self.apply_author_name(settings)
        
        if success_skin and success_author:
            self.report({'INFO'}, f"Nombres aplicados: Skin='{settings.skin_name}', Autor='{settings.author_nickname}'")
        elif success_skin:
            self.report({'WARNING'}, f"Solo se aplicó el nombre del skin: '{settings.skin_name}'")
        elif success_author:
            self.report({'WARNING'}, f"Solo se aplicó el nombre del autor: '{settings.author_nickname}'")
        else:
            self.report({'ERROR'}, "No se pudieron aplicar los nombres")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def validate_names(self, settings):
        """Valida que los nombres sean válidos"""
        # Validar skin_name
        if not settings.skin_name or not re.match(r'^[a-zA-Z0-9_-]+$', settings.skin_name):
            self.report({'ERROR'}, "Nombre del skin inválido. Solo se permiten letras, números, _ y -")
            return False
        
        # Validar author_nickname
        if not settings.author_nickname or not re.match(r'^[a-zA-Z0-9_-]+$', settings.author_nickname):
            self.report({'ERROR'}, "Nickname del autor inválido. Solo se permiten letras, números, _ y -")
            return False
        
        return True
    
    def apply_skin_name(self, settings):
        """Aplica el nombre personalizado al skin (mesh principal)"""
        try:
            # Buscar el mesh principal
            target_mesh = None
            possible_names = ["Mesh", "MySkin"]
            
            for obj_name in possible_names:
                if obj_name in bpy.data.objects:
                    obj = bpy.data.objects[obj_name]
                    if obj.type == 'MESH':
                        target_mesh = obj
                        break
            
            if not target_mesh:
                # Buscar cualquier mesh principal
                for obj in bpy.data.objects:
                    if obj.type == 'MESH' and obj.parent and obj.parent.type == 'ARMATURE':
                        target_mesh = obj
                        break
            
            if target_mesh:
                # Cambiar nombre del objeto
                old_name = target_mesh.name
                target_mesh.name = settings.skin_name
                
                # Cambiar nombre de los datos del mesh
                if target_mesh.data:
                    target_mesh.data.name = settings.skin_name
                
                print(f"[NAMING] Mesh renombrado: {old_name} -> {settings.skin_name}")
                return True
            else:
                print("[NAMING] No se encontró mesh principal para renombrar")
                return False
                
        except Exception as e:
            print(f"[NAMING] Error aplicando nombre del skin: {e}")
            return False
    
    def apply_author_name(self, settings):
        """Aplica el nombre del autor al armature y hueso root"""
        try:
            success_count = 0
            
            # Aplicar al target armature
            if settings.target_armature:
                old_armature_name = settings.target_armature.name
                settings.target_armature.name = settings.author_nickname
                # También renombrar los datos del armature
                settings.target_armature.data.name = settings.author_nickname
                print(f"[NAMING] Armature renombrado: {old_armature_name} -> {settings.target_armature.name}")
                success_count += 1
                
                # Aplicar al hueso Root
                if settings.target_armature.type == 'ARMATURE':
                    # Buscar hueso Root
                    root_bone = None
                    for bone in settings.target_armature.data.bones:
                        if bone.name.lower() in ['root', 'base', 'origin']:
                            root_bone = bone
                            break
                    
                    # Si no se encuentra, usar el primer hueso
                    if not root_bone and len(settings.target_armature.data.bones) > 0:
                        root_bone = settings.target_armature.data.bones[0]
                    
                    if root_bone:
                        # Cambiar a modo edición para renombrar hueso
                        bpy.context.view_layer.objects.active = settings.target_armature
                        bpy.ops.object.mode_set(mode='EDIT')
                        
                        edit_bone = settings.target_armature.data.edit_bones.get(root_bone.name)
                        if edit_bone:
                            old_bone_name = edit_bone.name
                            # Solo usar el nombre del autor sin sufijo
                            edit_bone.name = settings.author_nickname
                            print(f"[NAMING] Hueso root renombrado: {old_bone_name} -> {edit_bone.name}")
                            success_count += 1
                        
                        bpy.ops.object.mode_set(mode='OBJECT')
            
            return success_count > 0
            
        except Exception as e:
            print(f"[NAMING] Error aplicando nombre del autor: {e}")
            return False


class UNIVERSALGTA_OT_reset_names(Operator):
    """Resetear nombres a valores por defecto"""
    bl_idname = "universalgta.reset_names"
    bl_label = "Reset Names"
    bl_description = "Resetea los nombres a valores por defecto"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Resetear nombres en configuración
        settings.skin_name = "MySkin"
        settings.author_nickname = "Author"
        settings.name_validation_message = "✅ Nombres reseteados"
        
        self.report({'INFO'}, "Nombres reseteados a valores por defecto")
        return {'FINISHED'}


class UNIVERSALGTA_OT_validate_names(Operator):
    """Validar nombres manualmente"""
    bl_idname = "universalgta.validate_names"
    bl_label = "Validate Names"
    bl_description = "Valida que los nombres cumplan con los requisitos"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        issues = []
        
        # Validar skin_name
        if not settings.skin_name:
            issues.append("Nombre del skin está vacío")
        elif not re.match(r'^[a-zA-Z0-9_-]+$', settings.skin_name):
            issues.append("Nombre del skin contiene caracteres inválidos")
        elif len(settings.skin_name) > 32:
            issues.append("Nombre del skin es demasiado largo (máximo 32 caracteres)")
        
        # Validar author_nickname
        if not settings.author_nickname:
            issues.append("Nickname del autor está vacío")
        elif not re.match(r'^[a-zA-Z0-9_-]+$', settings.author_nickname):
            issues.append("Nickname del autor contiene caracteres inválidos")
        elif len(settings.author_nickname) > 32:
            issues.append("Nickname del autor es demasiado largo (máximo 32 caracteres)")
        
        # Mostrar resultados
        if issues:
            settings.name_validation_message = "❌ " + "; ".join(issues)
            self.report({'ERROR'}, f"Validación falló: {'; '.join(issues)}")
        else:
            settings.name_validation_message = "✅ Todos los nombres son válidos"
            self.report({'INFO'}, "Todos los nombres son válidos")
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_auto_generate_names(Operator):
    """Generar nombres automáticamente"""
    bl_idname = "universalgta.auto_generate_names"
    bl_label = "Auto Generate Names"
    bl_description = "Genera nombres automáticamente basados en el contenido actual"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Generar nombre del skin basado en el mesh actual
        skin_name = "MySkin"
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and len(obj.data.vertices) > 100:  # Mesh principal probablemente
                base_name = obj.name
                # Limpiar nombre para que sea válido
                clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', base_name)
                if clean_name and clean_name != "Mesh":
                    skin_name = clean_name[:32]  # Limitar longitud
                break
        
        # Generar nickname del autor basado en el usuario del sistema
        import os
        author_name = "Author"
        try:
            system_user = os.getenv('USERNAME') or os.getenv('USER') or "User"
            clean_author = re.sub(r'[^a-zA-Z0-9_-]', '_', system_user)
            if clean_author:
                author_name = clean_author[:32]
        except:
            pass
        
        # Aplicar nombres generados
        settings.skin_name = skin_name
        settings.author_nickname = author_name
        settings.name_validation_message = "✅ Nombres generados automáticamente"
        
        self.report({'INFO'}, f"Nombres generados: Skin='{skin_name}', Autor='{author_name}'")
        return {'FINISHED'}


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_apply_custom_names,
    UNIVERSALGTA_OT_reset_names,
    UNIVERSALGTA_OT_validate_names,
    UNIVERSALGTA_OT_auto_generate_names,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)