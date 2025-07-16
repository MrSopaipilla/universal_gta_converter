"""
external_pose_caller.py - Funciones para aplicar poses personalizadas
VERSIÓN CORREGIDA
"""

import bpy
from bpy import context, ops


def apply_manual_pose_to_children_and_reassign(armature=None):
    """
    Aplica la pose actual del armature activo a sus mallas hijas,
    horneando la deformación y luego reasigna un nuevo modificador apuntando al armature padre.
    
    Args:
        armature: El armature al cual aplicar la pose. Si es None, usa el objeto activo.
    
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario.
    """
    
    if not armature:
        armature = context.active_object
        if not armature or armature.type != 'ARMATURE':
            print("[POSE_UTIL] No hay armature válido activo.")
            return False

    print(f"[POSE_UTIL] Procesando armature: {armature.name}")

    # Encontrar todas las mallas hijas del armature
    children_meshes = [
        obj for obj in bpy.data.objects
        if obj.type == 'MESH' and obj.parent == armature
    ]

    if not children_meshes:
        print("[POSE_UTIL] No se encontraron mallas hijas del armature.")
        return False

    print(f"[POSE_UTIL] Encontradas {len(children_meshes)} mallas hijas")

    try:
        # Aplicar pose al armature
        context.view_layer.objects.active = armature
        ops.object.mode_set(mode='POSE')
        ops.pose.armature_apply()
        ops.object.mode_set(mode='OBJECT')
        print(f"[POSE_UTIL] Pose aplicada al armature: {armature.name}")

        # Aplicar modificadores en hijos y crear nuevos
        for mesh_obj in children_meshes:
            print(f"[POSE_UTIL] Procesando mesh: {mesh_obj.name}")
            
            # Buscar modificador de armature
            arm_mod = None
            for mod in mesh_obj.modifiers:
                if mod.type == 'ARMATURE' and mod.object == armature:
                    arm_mod = mod
                    break

            if not arm_mod:
                print(f"[POSE_UTIL] {mesh_obj.name} no tiene modificador válido, se salta.")
                continue

            # Activar el mesh y aplicar el modificador (hornear pose)
            context.view_layer.objects.active = mesh_obj
            try:
                ops.object.modifier_apply(modifier=arm_mod.name)
                print(f"[POSE_UTIL] Pose aplicada y horneada en: {mesh_obj.name}")
            except Exception as e:
                print(f"[POSE_UTIL] ERROR aplicando modificador en {mesh_obj.name}: {e}")
                continue

            # Buscar armature padre para asignar nuevo modificador
            parent_arm = armature.parent if armature.parent and armature.parent.type == 'ARMATURE' else None
            if parent_arm:
                # Crear nuevo modificador apuntando al armature padre
                new_mod = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
                new_mod.object = parent_arm
                print(f"[POSE_UTIL] Nuevo modificador asignado a {mesh_obj.name} -> {parent_arm.name}")
            else:
                print(f"[POSE_UTIL] No se encontró armature padre para {armature.name}. No se asignó nuevo modificador.")

        print("[POSE_UTIL] Proceso completado exitosamente.")
        return True

    except Exception as e:
        print(f"[POSE_UTIL] ERROR durante el proceso: {e}")
        import traceback
        traceback.print_exc()
        
        # Intentar volver a modo objeto en caso de error
        try:
            ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass
        
        return False


class ExternalPoseApplier:
    """Clase para aplicar poses personalizadas usando scripts externos"""
    
    def __init__(self):
        self.debug = True
    
    def execute_full_pose_application(self, source_armature=None, target_armature=None):
        """
        Ejecuta la aplicación completa de pose personalizada
        
        Args:
            source_armature: Armature fuente (puede ser None para autodetección)
            target_armature: Armature destino
        
        Returns:
            bool: True si fue exitoso, False en caso contrario
        """
        try:
            print("[EXTERNAL_POSE] Iniciando aplicación de pose personalizada...")
            
            # Autodetectar source_armature si no se proporciona
            if not source_armature:
                source_armature = self._auto_detect_source_armature(target_armature)
            
            if not source_armature:
                print("[EXTERNAL_POSE] No se pudo detectar armature fuente")
                return False
            
            if not target_armature:
                print("[EXTERNAL_POSE] No se proporcionó armature destino")
                return False
            
            print(f"[EXTERNAL_POSE] Aplicando pose de {source_armature.name} a {target_armature.name}")
            
            # Aplicar la pose usando la función principal
            success = apply_manual_pose_to_children_and_reassign(target_armature)
            
            if success:
                print("[EXTERNAL_POSE] Pose personalizada aplicada exitosamente")
            else:
                print("[EXTERNAL_POSE] Error al aplicar pose personalizada")
            
            return success
            
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error durante la aplicación de pose: {e}")
            return False
    
    def _auto_detect_source_armature(self, target_armature):
        """
        Autodetecta el armature fuente basándose en criterios heurísticos
        
        Args:
            target_armature: Armature destino para referencia
        
        Returns:
            Object: Armature fuente detectado o None si no se encuentra
        """
        armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
        
        # Filtrar el target_armature
        if target_armature in armatures:
            armatures.remove(target_armature)
        
        if not armatures:
            print("[EXTERNAL_POSE] No hay otros armatures para detectar como fuente")
            return None
        
        # Criterios de detección:
        # 1. Armature con más huesos
        # 2. Armature que no contenga "root" en el nombre
        # 3. Armature con objetos mesh como hijos
        
        best_candidate = None
        best_score = -1
        
        for armature in armatures:
            score = 0
            
            # Puntos por número de huesos
            bone_count = len(armature.data.bones)
            score += bone_count
            
            # Penalizar si tiene "root" en el nombre
            if 'root' in armature.name.lower():
                score -= 50
            
            # Puntos por tener objetos mesh como hijos
            mesh_children = [obj for obj in bpy.data.objects 
                           if obj.type == 'MESH' and obj.parent == armature]
            score += len(mesh_children) * 10
            
            # Puntos por ser más reciente (índice más alto en el nombre)
            if '.' in armature.name:
                try:
                    index = int(armature.name.split('.')[-1])
                    score += index
                except ValueError:
                    pass
            
            print(f"[EXTERNAL_POSE] Candidato {armature.name}: score {score}")
            
            if score > best_score:
                best_score = score
                best_candidate = armature
        
        if best_candidate:
            print(f"[EXTERNAL_POSE] Armature fuente detectado: {best_candidate.name}")
        
        return best_candidate
    
    def copy_pose_between_armatures(self, source_armature, target_armature, bone_mappings=None):
        """
        Copia pose entre armatures usando mapeos específicos
        
        Args:
            source_armature: Armature fuente
            target_armature: Armature destino  
            bone_mappings: Lista de tuplas (source_bone, target_bone)
        
        Returns:
            bool: True si fue exitoso
        """
        try:
            print(f"[EXTERNAL_POSE] Copiando pose de {source_armature.name} a {target_armature.name}")
            
            if not bone_mappings:
                # Usar mapeos de la configuración si están disponibles
                settings = bpy.context.scene.universal_gta_settings
                bone_mappings = [
                    (m.source_bone, m.target_bone)
                    for m in settings.bone_mappings
                    if m.enabled and m.source_bone and m.target_bone
                ]
            
            if not bone_mappings:
                print("[EXTERNAL_POSE] No hay mapeos de huesos disponibles")
                return False
            
            # Activar target armature y entrar en modo pose
            bpy.context.view_layer.objects.active = target_armature
            bpy.ops.object.mode_set(mode='POSE')
            
            copied_bones = 0
            
            for source_bone_name, target_bone_name in bone_mappings:
                if (source_bone_name in source_armature.pose.bones and 
                    target_bone_name in target_armature.pose.bones):
                    
                    source_bone = source_armature.pose.bones[source_bone_name]
                    target_bone = target_armature.pose.bones[target_bone_name]
                    
                    # Copiar transformaciones
                    target_bone.location = source_bone.location.copy()
                    target_bone.rotation_euler = source_bone.rotation_euler.copy()
                    target_bone.rotation_quaternion = source_bone.rotation_quaternion.copy()
                    target_bone.scale = source_bone.scale.copy()
                    
                    copied_bones += 1
                    if self.debug:
                        print(f"[EXTERNAL_POSE] Copiado: {source_bone_name} -> {target_bone_name}")
            
            bpy.ops.object.mode_set(mode='OBJECT')
            print(f"[EXTERNAL_POSE] Pose copiada exitosamente. {copied_bones} huesos procesados.")
            
            return copied_bones > 0
            
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error copiando pose: {e}")
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass
            return False
    
    def reset_armature_pose(self, armature):
        """
        Resetea la pose de un armature a su estado rest
        
        Args:
            armature: Armature a resetear
        
        Returns:
            bool: True si fue exitoso
        """
        try:
            print(f"[EXTERNAL_POSE] Reseteando pose de {armature.name}")
            
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            
            # Seleccionar todos los huesos y limpiar transformaciones
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.transforms_clear()
            
            bpy.ops.object.mode_set(mode='OBJECT')
            print(f"[EXTERNAL_POSE] Pose de {armature.name} reseteada exitosamente")
            
            return True
            
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error reseteando pose: {e}")
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass
            return False


# Funciones de conveniencia para compatibilidad con código anterior
def apply_pose_to_armature(armature):
    """Función de conveniencia para aplicar pose a un armature"""
    return apply_manual_pose_to_children_and_reassign(armature)


def execute_external_pose_application(source_armature=None, target_armature=None):
    """Función de conveniencia para ejecutar aplicación de pose externa"""
    applier = ExternalPoseApplier()
    return applier.execute_full_pose_application(source_armature, target_armature)