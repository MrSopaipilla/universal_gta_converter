import bpy
from bpy.types import Operator
from .. import external_pose_caller



class UNIVERSALGTA_OT_apply_custom_pose(Operator):
    """Aplicar pose personalizada usando el script externo"""
    bl_idname = "universalgta.apply_custom_pose"
    bl_label = "Apply Custom Pose"
    bl_description = "Aplica pose personalizada usando el script externo"
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        try:
            # Importar el aplicador de poses externo
            from ..external_pose_caller import ExternalPoseApplier
            
            # Usar el aplicador de poses externo
            applier = ExternalPoseApplier()
            success = applier.execute_full_pose_application(
                source_armature=settings.source_armature,
                target_armature=settings.target_armature
            )
            
            if success:
                self.report({'INFO'}, "Pose personalizada aplicada con éxito")
            else:
                self.report({'ERROR'}, "Error al aplicar pose personalizada")
                
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            
        return {'FINISHED'}


class UNIVERSALGTA_OT_apply_manual_pose(Operator):
    """Aplicar pose manual al armature y sus hijos"""
    bl_idname = "universalgta.apply_manual_pose"
    bl_label = "Apply Manual Pose"
    bl_description = "Aplica la pose actual del armature activo a sus mallas hijas"
    
    def execute(self, context):
        armature = context.active_object
        
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No hay armature válido seleccionado")
            return {'CANCELLED'}
        
        try:
            success = self.apply_manual_pose_to_children_and_reassign(armature)
            
            if success:
                self.report({'INFO'}, "Pose manual aplicada con éxito")
            else:
                self.report({'ERROR'}, "Error al aplicar pose manual")
                
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            
        return {'FINISHED'}
    
    def apply_manual_pose_to_children_and_reassign(self, armature):
        """
        Aplica la pose actual del armature activo a sus mallas hijas,
        horneando la deformación y luego reasigna un nuevo modificador apuntando al armature padre.
        """
        print(f"[POSE_UTIL] Procesando armature: {armature.name}")

        children_meshes = [
            obj for obj in bpy.data.objects
            if obj.type == 'MESH' and obj.parent == armature
        ]

        if not children_meshes:
            print("[POSE_UTIL] No se encontraron mallas hijas del armature.")
            return False

        # Aplicar pose al armature
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.armature_apply()
        bpy.ops.object.mode_set(mode='OBJECT')

        # Aplicar modificadores en hijos y crear nuevos
        for mesh_obj in children_meshes:
            arm_mod = None
            for mod in mesh_obj.modifiers:
                if mod.type == 'ARMATURE' and mod.object == armature:
                    arm_mod = mod
                    break

            if not arm_mod:
                print(f"[POSE_UTIL] {mesh_obj.name} no tiene modificador válido, se salta.")
                continue

            # Aplicar el modificador (hornear pose)
            bpy.context.view_layer.objects.active = mesh_obj
            try:
                bpy.ops.object.modifier_apply(modifier=arm_mod.name)
                print(f"[POSE_UTIL] Pose aplicada y horneada en: {mesh_obj.name}")
            except Exception as e:
                print(f"[POSE_UTIL] ERROR aplicando modificador en {mesh_obj.name}: {e}")
                continue

            # Asignar nuevo armature padre si existe
            parent_arm = armature.parent if armature.parent and armature.parent.type == 'ARMATURE' else None
            if parent_arm:
                new_mod = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
                new_mod.object = parent_arm
                print(f"[POSE_UTIL] Nuevo modificador asignado a {mesh_obj.name} -> {parent_arm.name}")
            else:
                print(f"[POSE_UTIL] No se encontró armature padre para {armature.name}. No se asignó nuevo modificador.")

        print("[POSE_UTIL] Proceso completado.")
        return True


class UNIVERSALGTA_OT_reset_pose(Operator):
    """Resetear pose del armature"""
    bl_idname = "universalgta.reset_pose"
    bl_label = "Reset Pose"
    bl_description = "Resetea la pose del armature seleccionado"
    
    def execute(self, context):
        armature = context.active_object
        
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No hay armature válido seleccionado")
            return {'CANCELLED'}
        
        try:
            # Cambiar a modo pose
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            
            # Seleccionar todos los huesos
            bpy.ops.pose.select_all(action='SELECT')
            
            # Limpiar transformaciones
            bpy.ops.pose.transforms_clear()
            
            # Volver a modo objeto
            bpy.ops.object.mode_set(mode='OBJECT')
            
            self.report({'INFO'}, "Pose reseteada con éxito")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error al resetear pose: {str(e)}")
            
        return {'FINISHED'}


class UNIVERSALGTA_OT_copy_pose(Operator):
    """Copiar pose de un armature a otro"""
    bl_idname = "universalgta.copy_pose"
    bl_label = "Copy Pose"
    bl_description = "Copia la pose del armature fuente al armature destino"
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        source_armature = settings.source_armature
        target_armature = settings.target_armature
        
        if not source_armature or not target_armature:
            self.report({'ERROR'}, "Necesitas definir tanto el armature fuente como el destino")
            return {'CANCELLED'}
        
        if source_armature.type != 'ARMATURE' or target_armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Ambos objetos deben ser armatures")
            return {'CANCELLED'}
        
        try:
            success = self.copy_pose_between_armatures(source_armature, target_armature)
            
            if success:
                self.report({'INFO'}, "Pose copiada con éxito")
            else:
                self.report({'ERROR'}, "Error al copiar pose")
                
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            
        return {'FINISHED'}
    
    def copy_pose_between_armatures(self, source_armature, target_armature):
        """Copia la pose de un armature a otro"""
        print(f"[POSE_COPY] Copiando pose de {source_armature.name} a {target_armature.name}")
        
        # Obtener mapeos de huesos
        settings = bpy.context.scene.universal_gta_settings
        mappings = [
            (m.source_bone, m.target_bone)
            for m in settings.bone_mappings
            if m.enabled and m.source_bone and m.target_bone
        ]
        
        if not mappings:
            print("[POSE_COPY] No hay mapeos de huesos definidos")
            return False
        
        # Activar target armature y entrar en modo pose
        bpy.context.view_layer.objects.active = target_armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Copiar transformaciones
        copied_bones = 0
        for source_bone_name, target_bone_name in mappings:
            if (source_bone_name in source_armature.pose.bones and 
                target_bone_name in target_armature.pose.bones):
                
                source_bone = source_armature.pose.bones[source_bone_name]
                target_bone = target_armature.pose.bones[target_bone_name]
                
                # Copiar location, rotation y scale
                target_bone.location = source_bone.location.copy()
                target_bone.rotation_euler = source_bone.rotation_euler.copy()
                target_bone.rotation_quaternion = source_bone.rotation_quaternion.copy()
                target_bone.scale = source_bone.scale.copy()
                
                copied_bones += 1
                print(f"[POSE_COPY] Copiado: {source_bone_name} -> {target_bone_name}")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"[POSE_COPY] Copiados {copied_bones} huesos")
        
        return copied_bones > 0


class UNIVERSALGTA_OT_bake_pose(Operator):
    """Hornear pose en el armature"""
    bl_idname = "universalgta.bake_pose"
    bl_label = "Bake Pose"
    bl_description = "Hornea la pose actual del armature en su rest pose"
    
    def execute(self, context):
        armature = context.active_object
        
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No hay armature válido seleccionado")
            return {'CANCELLED'}
        
        try:
            # Activar armature y entrar en modo pose
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            
            # Aplicar pose como rest pose
            bpy.ops.pose.armature_apply()
            
            # Volver a modo objeto
            bpy.ops.object.mode_set(mode='OBJECT')
            
            self.report({'INFO'}, "Pose horneada con éxito")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error al hornear pose: {str(e)}")
            
        return {'FINISHED'}


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
