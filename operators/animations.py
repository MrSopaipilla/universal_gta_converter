"""Operadores para animaciones predefinidas."""

import bpy  # type: ignore
import os
from bpy.types import Operator  # type: ignore


class UNIVERSALGTA_OT_load_animation(Operator):
    """Cargar animación predefinida desde archivo .blend"""
    bl_idname = "universalgta.load_animation"
    bl_label = "Load Animation"
    bl_description = "Carga una animación predefinida desde archivo .blend en el armature target"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No hay armature target definido")
            return {'CANCELLED'}
        
        if settings.predefined_animation == 'NONE':
            self.report({'WARNING'}, "Selecciona una animación primero")
            return {'CANCELLED'}
        
        try:
            # Limpiar animaciones existentes primero
            self.clear_animations(settings.target_armature)
            
            # Cargar la animación desde archivo .blend
            success = self.load_animation_from_blend(
                settings.target_armature, 
                settings.predefined_animation
            )
            
            if success:
                self.report({'INFO'}, f"Animación '{settings.predefined_animation}' cargada exitosamente")
            else:
                self.report({'ERROR'}, f"Error cargando animación '{settings.predefined_animation}'")
                return {'CANCELLED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def get_animation_blend_path(self, animation_name):
        """Obtiene la ruta del archivo .blend de la animación"""
        # Obtener la ruta del addon
        addon_dir = os.path.dirname(os.path.dirname(__file__))
        animations_dir = os.path.join(addon_dir, "animations")
        
        # Mapeo de nombres de animación a archivos
        animation_files = {
            'IDLE': 'gta_idle.blend',
            'WALK': 'gta_walk.blend', 
            'RUNNING': 'gta_running.blend',
            'JUMP': 'gta_jump.blend',
            'CHAT': 'gta_chat.blend',
            'FACIAL': 'gta_facial.blend'
        }
        
        if animation_name not in animation_files:
            return None
        
        blend_path = os.path.join(animations_dir, animation_files[animation_name])
        
        if not os.path.exists(blend_path):
            print(f"[ANIMATION] Archivo no encontrado: {blend_path}")
            return None
        
        return blend_path
    
    def load_animation_from_blend(self, target_armature, animation_name):
        """Carga animación desde archivo .blend específico"""
        try:
            blend_path = self.get_animation_blend_path(animation_name)
            
            if not blend_path:
                print(f"[ANIMATION] No se pudo encontrar archivo para animación: {animation_name}")
                # Crear animación por defecto si no existe el archivo
                return self.create_fallback_animation(target_armature, animation_name)
            
            # Limpiar animaciones existentes
            self.clear_animations(target_armature)
            
            print(f"[ANIMATION] Cargando animación desde: {blend_path}")
            
            # Importar action desde el archivo .blend
            with bpy.data.libraries.load(blend_path) as (data_from, data_to):
                # Buscar actions en el archivo
                available_actions = data_from.actions
                print(f"[ANIMATION] Actions disponibles en {blend_path}: {available_actions}")
                
                if available_actions:
                    # Tomar la primera action o buscar una específica
                    target_action_name = None
                    
                    # Buscar action que coincida con el nombre de la animación
                    for action_name in available_actions:
                        if animation_name.lower() in action_name.lower():
                            target_action_name = action_name
                            break
                    
                    # Si no se encuentra, tomar la primera
                    if not target_action_name:
                        target_action_name = available_actions[0]
                    
                    # Importar la action
                    data_to.actions = [target_action_name]
                    print(f"[ANIMATION] Importando action: {target_action_name}")
                else:
                    print(f"[ANIMATION] No se encontraron actions en {blend_path}")
                    return False
            
            # Aplicar la action importada al armature
            if data_to.actions:
                imported_action = data_to.actions[0]
                
                # Renombrar la action para evitar conflictos
                new_action_name = f"{target_armature.name}_{animation_name}"
                imported_action.name = new_action_name
                
                # Asignar al armature
                if not target_armature.animation_data:
                    target_armature.animation_data_create()
                
                target_armature.animation_data.action = imported_action
                
                # Configurar frame range basado en la animación
                if imported_action.frame_range:
                    start_frame, end_frame = imported_action.frame_range
                    bpy.context.scene.frame_start = int(start_frame)
                    bpy.context.scene.frame_end = int(end_frame)
                
                print(f"[ANIMATION] Action '{new_action_name}' aplicada a {target_armature.name}")
                return True
            
            return False
            
        except Exception as e:
            print(f"[ANIMATION] Error cargando desde .blend: {e}")
            return False
    
    def create_fallback_animation(self, armature, animation_type):
        """Crea una animación básica si no existe el archivo .blend"""
        try:
            print(f"[ANIMATION] Creando animación fallback para: {animation_type}")
            
            # Crear nueva action
            action_name = f"{armature.name}_{animation_type}_fallback"
            action = bpy.data.actions.new(name=action_name)
            
            # Asignar action al armature
            if not armature.animation_data:
                armature.animation_data_create()
            armature.animation_data.action = action
            
            # Configurar frame range
            bpy.context.scene.frame_start = 1
            bpy.context.scene.frame_end = 60
            
            # Crear animación básica según el tipo
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            
            if animation_type == 'IDLE':
                self.create_basic_idle(armature)
            elif animation_type == 'WALK':
                self.create_basic_walk(armature)
            # Agregar más tipos según sea necesario
            
            bpy.ops.object.mode_set(mode='OBJECT')
            return True
            
        except Exception as e:
            print(f"[ANIMATION] Error creando animación fallback: {e}")
            return False
    
    def create_basic_idle(self, armature):
        """Crea animación básica de idle"""
        # Respiración suave en el spine
        if 'Spine' in armature.pose.bones:
            spine = armature.pose.bones['Spine']
            
            bpy.context.scene.frame_set(1)
            spine.scale = (1.0, 1.0, 1.0)
            spine.keyframe_insert(data_path="scale")
            
            bpy.context.scene.frame_set(30)
            spine.scale = (1.01, 1.01, 1.01)
            spine.keyframe_insert(data_path="scale")
            
            bpy.context.scene.frame_set(60)
            spine.scale = (1.0, 1.0, 1.0)
            spine.keyframe_insert(data_path="scale")
    
    def create_basic_walk(self, armature):
        """Crea animación básica de caminata"""
        # Movimiento simple de piernas
        leg_bones = ['L Thigh', 'R Thigh']
        
        for i, bone_name in enumerate(leg_bones):
            if bone_name in armature.pose.bones:
                bone = armature.pose.bones[bone_name]
                
                # Alternancia simple
                for frame in [1, 20, 40, 60]:
                    bpy.context.scene.frame_set(frame)
                    if (frame // 20 + i) % 2 == 0:
                        bone.rotation_euler.x = 0.2
                    else:
                        bone.rotation_euler.x = -0.2
                    bone.keyframe_insert(data_path="rotation_euler")
    
    def clear_animations(self, armature):
        """Limpia todas las animaciones del armature"""
        if armature.animation_data:
            armature.animation_data.action = None
        
        # Limpiar actions relacionadas con este armature
        for action in list(bpy.data.actions):
            if armature.name in action.name:
                bpy.data.actions.remove(action)


class UNIVERSALGTA_OT_clear_animations(Operator):
    """Limpiar todas las animaciones"""
    bl_idname = "universalgta.clear_animations"
    bl_label = "Clear Animations"
    bl_description = "Limpia todas las animaciones del armature target"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No hay armature target definido")
            return {'CANCELLED'}
        
        try:
            armature = settings.target_armature
            
            # Limpiar animation data
            if armature.animation_data:
                armature.animation_data.action = None
            
            # Resetear pose a rest pose
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.transforms_clear()
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Limpiar actions relacionadas
            actions_removed = 0
            for action in list(bpy.data.actions):
                if armature.name in action.name:
                    bpy.data.actions.remove(action)
                    actions_removed += 1
            
            self.report({'INFO'}, f"Animaciones limpiadas. {actions_removed} actions eliminadas")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error limpiando animaciones: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_refresh_animations_on_spacing_change(Operator):
    """Recargar animaciones cuando cambie el espaciado"""
    bl_idname = "universalgta.refresh_animations_on_spacing_change"
    bl_label = "Refresh Animations"
    bl_description = "Recarga las animaciones después de cambiar el espaciado"
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            return {'CANCELLED'}
        
        # Si hay una animación cargada, recargarla
        current_animation = settings.predefined_animation
        if current_animation != 'NONE':
            # Limpiar y recargar
            bpy.ops.universalgta.clear_animations()
            bpy.ops.universalgta.load_animation()
            print(f"[ANIMATION] Animación {current_animation} recargada después de cambio de espaciado")
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_apply_facial_expressiveness(Operator):
    """Aplicar expresividad facial"""
    bl_idname = "universalgta.apply_facial_expressiveness"
    bl_label = "Apply Facial Expressiveness"
    bl_description = "Aplica expresividad facial modificando el roll de huesos faciales"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No hay armature target definido")
            return {'CANCELLED'}
        
        try:
            armature = settings.target_armature
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Huesos faciales a modificar
            facial_bones = {
                'R Brow': settings.eyebrow_intensity,
                'L Brow': settings.eyebrow_intensity, 
                'Jaw': settings.jaw_expression
            }
            
            modified_bones = 0
            
            for bone_name, intensity in facial_bones.items():
                if bone_name in armature.data.edit_bones:
                    edit_bone = armature.data.edit_bones[bone_name]
                    
                    # Modificar el roll del hueso para expresividad
                    original_roll = edit_bone.roll
                    edit_bone.roll = original_roll + (intensity * 0.5)  # Ajuste suave
                    
                    modified_bones += 1
                    print(f"[FACIAL] {bone_name} roll modificado: {original_roll:.3f} -> {edit_bone.roll:.3f}")
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            if modified_bones > 0:
                self.report({'INFO'}, f"Expresividad facial aplicada a {modified_bones} huesos")
            else:
                self.report({'WARNING'}, "No se encontraron huesos faciales para modificar")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error aplicando expresividad facial: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_create_animation_files(Operator):
    """Crear archivos de animación de ejemplo"""
    bl_idname = "universalgta.create_animation_files"
    bl_label = "Create Animation Files"
    bl_description = "Crea archivos .blend de ejemplo para las animaciones"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        # Obtener directorio del addon
        addon_dir = os.path.dirname(os.path.dirname(__file__))
        animations_dir = os.path.join(addon_dir, "animations")
        
        # Crear directorio si no existe
        if not os.path.exists(animations_dir):
            os.makedirs(animations_dir)
        
        # Lista de archivos a crear
        animation_files = [
            'gta_idle.blend',
            'gta_walk.blend', 
            'gta_running.blend',
            'gta_jump.blend',
            'gta_chat.blend',
            'gta_facial.blend'
        ]
        
        created_files = []
        
        for filename in animation_files:
            filepath = os.path.join(animations_dir, filename)
            if not os.path.exists(filepath):
                # Crear archivo .blend básico
                bpy.ops.wm.save_as_mainfile(filepath=filepath)
                created_files.append(filename)
        
        if created_files:
            self.report({'INFO'}, f"Creados {len(created_files)} archivos de animación en: {animations_dir}")
        else:
            self.report({'INFO'}, f"Archivos de animación ya existen en: {animations_dir}")
        
        return {'FINISHED'}


classes = [
    UNIVERSALGTA_OT_load_animation,
    UNIVERSALGTA_OT_clear_animations,
    UNIVERSALGTA_OT_refresh_animations_on_spacing_change,
    UNIVERSALGTA_OT_apply_facial_expressiveness,
    UNIVERSALGTA_OT_create_animation_files,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)