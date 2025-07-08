# operators/pose.py - Versión mejorada
import bpy
from bpy.types import Operator
from .. import external_pose_caller


class UNIVERSALGTA_OT_apply_custom_pose(Operator):
    """Aplicar pose personalizada usando el script externo"""
    bl_idname = "universalgta.apply_custom_pose"
    bl_label = "Apply Custom Pose"
    bl_description = "Aplica pose personalizada usando el script externo"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        try:
            # Usar el aplicador de poses externo
            applier = external_pose_caller.ExternalPoseApplier()
            success = applier.execute_full_pose_application(
                source_armature=settings.source_armature,
                target_armature=settings.target_armature
            )
            
            if success:
                self.report({'INFO'}, "Pose personalizada aplicada con éxito")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Error al aplicar pose personalizada")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}


class UNIVERSALGTA_OT_apply_manual_pose(Operator):
    """Aplicar pose manual al armature y sus hijos"""
    bl_idname = "universalgta.apply_manual_pose"
    bl_label = "Apply Manual Pose"
    bl_description = "Aplica la pose actual del armature activo a sus mallas hijas"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        armature = context.active_object
        
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No hay armature válido seleccionado")
            return {'CANCELLED'}
        
        try:
            success = external_pose_caller.apply_manual_pose_to_children_and_reassign(armature)
            
            if success:
                self.report({'INFO'}, "Pose manual aplicada con éxito")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Error al aplicar pose manual")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}


class UNIVERSALGTA_OT_reset_pose(Operator):
    """Resetear pose del armature"""
    bl_idname = "universalgta.reset_pose"
    bl_label = "Reset Pose"
    bl_description = "Resetea la pose del armature seleccionado"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        armature = context.active_object
        
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No hay armature válido seleccionado")
            return {'CANCELLED'}
        
        try:
            applier = external_pose_caller.ExternalPoseApplier()
            success = applier.reset_armature_pose(armature)
            
            if success:
                self.report({'INFO'}, "Pose reseteada con éxito")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Error al resetear pose")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error al resetear pose: {str(e)}")
            return {'CANCELLED'}


class UNIVERSALGTA_OT_copy_pose(Operator):
    """Copiar pose de un armature a otro"""
    bl_idname = "universalgta.copy_pose"
    bl_label = "Copy Pose"
    bl_description = "Copia la pose del armature fuente al armature destino"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        source_armature = settings.source_armature
        target_armature = settings.target_armature
        
        # Validación
        if not self._validate_armatures(source_armature, target_armature):
            return {'CANCELLED'}
        
        try:
            applier = external_pose_caller.ExternalPoseApplier()
            success = applier.copy_pose_between_armatures(source_armature, target_armature)
            
            if success:
                self.report({'INFO'}, "Pose copiada con éxito")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Error al copiar pose")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}
    
    def _validate_armatures(self, source, target):
        """Valida que los armatures sean válidos"""
        if not source or not target:
            self.report({'ERROR'}, "Necesitas definir tanto el armature fuente como el destino")
            return False
        
        if source.type != 'ARMATURE' or target.type != 'ARMATURE':
            self.report({'ERROR'}, "Ambos objetos deben ser armatures")
            return False
        
        return True


class UNIVERSALGTA_OT_bake_pose(Operator):
    """Hornear pose en el armature"""
    bl_idname = "universalgta.bake_pose"
    bl_label = "Bake Pose"
    bl_description = "Hornea la pose actual del armature en su rest pose"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        armature = context.active_object
        
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No hay armature válido seleccionado")
            return {'CANCELLED'}
        
        try:
            # Activar armature y entrar en modo pose
            context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            
            # Aplicar pose como rest pose
            bpy.ops.pose.armature_apply()
            
            # Volver a modo objeto
            bpy.ops.object.mode_set(mode='OBJECT')
            
            self.report({'INFO'}, "Pose horneada con éxito")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error al hornear pose: {str(e)}")
            self._safe_mode_set('OBJECT')
            return {'CANCELLED'}
    
    def _safe_mode_set(self, mode):
        """Cambia de modo de forma segura"""
        try:
            bpy.ops.object.mode_set(mode=mode)
        except:
            pass


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_apply_custom_pose,
    UNIVERSALGTA_OT_apply_manual_pose,
    UNIVERSALGTA_OT_reset_pose,
    UNIVERSALGTA_OT_copy_pose,
    UNIVERSALGTA_OT_bake_pose,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)