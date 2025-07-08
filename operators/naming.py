# operators/naming.py - Versión mejorada
"""
Operadores para sistema de nombres personalizados
"""

import bpy
import re
import os
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
        if not self._validate_names(settings):
            return {'CANCELLED'}
        
        # Aplicar nombres
        results = {
            'skin': self._apply_skin_name(settings),
            'author': self._apply_author_name(settings)
        }
        
        # Reportar resultados
        if results['skin'] and results['author']:
            self.report({'INFO'}, 
                       f"Nombres aplicados: Skin='{settings.skin_name}', "
                       f"Autor='{settings.author_nickname}'")
        elif results['skin']:
            self.report({'WARNING'}, 
                       f"Solo se aplicó el nombre del skin: '{settings.skin_name}'")
        elif results['author']:
            self.report({'WARNING'}, 
                       f"Solo se aplicó el nombre del autor: '{settings.author_nickname}'")
        else:
            self.report({'ERROR'}, "No se pudieron aplicar los nombres")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def _validate_names(self, settings):
        """Valida que los nombres sean válidos"""
        pattern = r'^[a-zA-Z0-9_-]+$'
        errors = []
        
        # Validar skin_name
        if not settings.skin_name:
            errors.append("Nombre del skin está vacío")
        elif not re.match(pattern, settings.skin_name):
            errors.append("Nombre del skin contiene caracteres inválidos")
        
        # Validar author_nickname
        if not settings.author_nickname:
            errors.append("Nickname del autor está vacío")
        elif not re.match(pattern, settings.author_nickname):
            errors.append("Nickname del autor contiene caracteres inválidos")
        
        if errors:
            self.report({'ERROR'}, ". ".join(errors))
            return False
        
        return True
    
    def _apply_skin_name(self, settings):
        """Aplica el nombre personalizado al skin (mesh principal)"""
        try:
            # Buscar el mesh principal
            target_mesh = self._find_main_mesh()
            
            if not target_mesh:
                print("[NAMING] No se encontró mesh principal para renombrar")
                return False
            
            # Cambiar nombre
            old_name = target_mesh.name
            target_mesh.name = settings.skin_name
            
            # Cambiar nombre de los datos del mesh
            if target_mesh.data:
                target_mesh.data.name = settings.skin_name
            
            print(f"[NAMING] Mesh renombrado: {old_name} -> {settings.skin_name}")
            return True
                
        except Exception as e:
            print(f"[NAMING] Error aplicando nombre del skin: {e}")
            return False
    
    def _find_main_mesh(self):
        """Encuentra el mesh principal del modelo"""
        # Buscar por nombres comunes
        common_names = ["Mesh", "MySkin"]
        for name in common_names:
            if name in bpy.data.objects:
                obj = bpy.data.objects[name]
                if obj.type == 'MESH':
                    return obj
        
        # Buscar mesh con armature parent
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.parent and obj.parent.type == 'ARMATURE':
                return obj
        
        # Buscar cualquier mesh grande
        largest_mesh = None
        largest_vertex_count = 0
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                vertex_count = len(obj.data.vertices)
                if vertex_count > largest_vertex_count:
                    largest_vertex_count = vertex_count
                    largest_mesh = obj
        
        return largest_mesh
    
    def _apply_author_name(self, settings):
        """Aplica el nombre del autor al armature y hueso root"""
        try:
            if not settings.target_armature:
                print("[NAMING] No hay target armature definido")
                return False
            
            success_count = 0
            
            # Aplicar al armature
            old_armature_name = settings.target_armature.name
            settings.target_armature.name = f"{settings.author_nickname}_Armature"
            print(f"[NAMING] Armature renombrado: {old_armature_name} -> {settings.target_armature.name}")
            success_count += 1
            
            # Aplicar al hueso Root
            if self._rename_root_bone(settings):
                success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            print(f"[NAMING] Error aplicando nombre del autor: {e}")
            return False
    
    def _rename_root_bone(self, settings):
        """Renombra el hueso root con el nombre del autor"""
        if settings.target_armature.type != 'ARMATURE':
            return False
        
        # Buscar hueso Root
        root_bone = None
        root_keywords = ['root', 'base', 'origin', 'pelvis']
        
        for bone in settings.target_armature.data.bones:
            if any(keyword in bone.name.lower() for keyword in root_keywords):
                root_bone = bone
                break
        
        # Si no se encuentra, usar el primer hueso
        if not root_bone and len(settings.target_armature.data.bones) > 0:
            root_bone = settings.target_armature.data.bones[0]
        
        if not root_bone:
            return False
        
        # Cambiar a modo edición para renombrar
        bpy.context.view_layer.objects.active = settings.target_armature
        bpy.ops.object.mode_set(mode='EDIT')
        
        try:
            edit_bone = settings.target_armature.data.edit_bones.get(root_bone.name)
            if edit_bone:
                old_bone_name = edit_bone.name
                edit_bone.name = f"{settings.author_nickname}_Root"
                print(f"[NAMING] Hueso root renombrado: {old_bone_name} -> {edit_bone.name}")
                success = True
            else:
                success = False
        finally:
            bpy.ops.object.mode_set(mode='OBJECT')
        
        return success


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
        
        validation_result = self._validate_all_names(settings)
        
        # Actualizar mensaje de validación
        settings.name_validation_message = validation_result['message']
        
        # Mostrar resultado
        if validation_result['valid']:
            self.report({'INFO'}, "Todos los nombres son válidos")
        else:
            self.report({'ERROR'}, f"Validación falló: {validation_result['details']}")
        
        return {'FINISHED'}
    
    def _validate_all_names(self, settings):
        """Valida todos los nombres y devuelve resultado detallado"""
        issues = []
        pattern = r'^[a-zA-Z0-9_-]+$'
        
        # Validar skin_name
        if not settings.skin_name:
            issues.append("Nombre del skin está vacío")
        elif not re.match(pattern, settings.skin_name):
            issues.append("Nombre del skin contiene caracteres inválidos")
        elif len(settings.skin_name) > 32:
            issues.append("Nombre del skin es demasiado largo (máximo 32 caracteres)")
        
        # Validar author_nickname
        if not settings.author_nickname:
            issues.append("Nickname del autor está vacío")
        elif not re.match(pattern, settings.author_nickname):
            issues.append("Nickname del autor contiene caracteres inválidos")
        elif len(settings.author_nickname) > 32:
            issues.append("Nickname del autor es demasiado largo (máximo 32 caracteres)")
        
        # Preparar resultado
        if issues:
            return {
                'valid': False,
                'message': "❌ " + "; ".join(issues),
                'details': "; ".join(issues)
            }
        else:
            return {
                'valid': True,
                'message': "✅ Todos los nombres son válidos",
                'details': ""
            }


class UNIVERSALGTA_OT_auto_generate_names(Operator):
    """Generar nombres automáticamente"""
    bl_idname = "universalgta.auto_generate_names"
    bl_label = "Auto Generate Names"
    bl_description = "Genera nombres automáticamente basados en el contenido actual"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Generar nombres
        skin_name = self._generate_skin_name()
        author_name = self._generate_author_name()
        
        # Aplicar nombres generados
        settings.skin_name = skin_name
        settings.author_nickname = author_name
        settings.name_validation_message = "✅ Nombres generados automáticamente"
        
        self.report({'INFO'}, 
                   f"Nombres generados: Skin='{skin_name}', Autor='{author_name}'")
        return {'FINISHED'}
    
    def _generate_skin_name(self):
        """Genera un nombre para el skin basado en el contenido"""
        # Buscar mesh principal
        main_mesh = None
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and len(obj.data.vertices) > 100:
                main_mesh = obj
                break
        
        if main_mesh and main_mesh.name != "Mesh":
            # Limpiar nombre del mesh
            base_name = self._clean_name(main_mesh.name)
            if base_name:
                return base_name[:32]
        
        # Nombre por defecto basado en la fecha
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        return f"Skin_{date_str}"
    
    def _generate_author_name(self):
        """Genera un nombre de autor"""
        # Intentar obtener del sistema
        author_name = self._get_system_username()
        
        if author_name:
            return self._clean_name(author_name)[:32]
        
        # Nombre por defecto
        return "Author"
    
    def _get_system_username(self):
        """Obtiene el nombre de usuario del sistema"""
        try:
            # Intentar diferentes métodos
            username = os.getenv('USERNAME') or os.getenv('USER')
            if username:
                return username
            
            # Intentar desde el path del usuario
            import pathlib
            home = pathlib.Path.home()
            if home:
                return home.name
            
        except Exception:
            pass
        
        return None
    
    def _clean_name(self, name):
        """Limpia un nombre para que sea válido"""
        # Reemplazar caracteres inválidos con guiones bajos
        cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        # Eliminar guiones bajos múltiples
        cleaned = re.sub(r'_+', '_', cleaned)
        # Eliminar guiones bajos al principio y final
        cleaned = cleaned.strip('_-')
        return cleaned if cleaned else "Default"


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