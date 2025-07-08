# external_pose_caller.py - Versión mejorada
"""
external_pose_caller.py - Funciones para aplicar poses personalizadas
VERSIÓN MEJORADA Y OPTIMIZADA
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
        if not _apply_armature_pose(armature):
            return False

        # Aplicar modificadores en hijos y crear nuevos
        success_count = 0
        for mesh_obj in children_meshes:
            if _process_mesh_object(mesh_obj, armature):
                success_count += 1

        print(f"[POSE_UTIL] Proceso completado. {success_count}/{len(children_meshes)} mallas procesadas exitosamente.")
        return success_count > 0

    except Exception as e:
        print(f"[POSE_UTIL] ERROR durante el proceso: {e}")
        import traceback
        traceback.print_exc()
        
        # Intentar volver a modo objeto en caso de error
        _safe_mode_set('OBJECT')
        return False


def _apply_armature_pose(armature):
    """Aplica la pose al armature"""
    try:
        context.view_layer.objects.active = armature
        ops.object.mode_set(mode='POSE')
        ops.pose.armature_apply()
        ops.object.mode_set(mode='OBJECT')
        print(f"[POSE_UTIL] Pose aplicada al armature: {armature.name}")
        return True
    except Exception as e:
        print(f"[POSE_UTIL] ERROR aplicando pose al armature: {e}")
        return False


def _process_mesh_object(mesh_obj, armature):
    """Procesa un objeto mesh individual"""
    print(f"[POSE_UTIL] Procesando mesh: {mesh_obj.name}")
    
    # Buscar modificador de armature
    arm_mod = _find_armature_modifier(mesh_obj, armature)
    
    if not arm_mod:
        print(f"[POSE_UTIL] {mesh_obj.name} no tiene modificador válido, se salta.")
        return False

    # Aplicar el modificador (hornear pose)
    if not _apply_modifier(mesh_obj, arm_mod):
        return False

    # Buscar y asignar nuevo armature padre
    parent_arm = _find_parent_armature(armature)
    if parent_arm:
        _create_new_modifier(mesh_obj, parent_arm)
    else:
        print(f"[POSE_UTIL] No se encontró armature padre para {armature.name}.")
    
    return True


def _find_armature_modifier(mesh_obj, armature):
    """Encuentra el modificador de armature en el mesh"""
    for mod in mesh_obj.modifiers:
        if mod.type == 'ARMATURE' and mod.object == armature:
            return mod
    return None


def _apply_modifier(mesh_obj, modifier):
    """Aplica un modificador al mesh"""
    try:
        context.view_layer.objects.active = mesh_obj
        ops.object.modifier_apply(modifier=modifier.name)
        print(f"[POSE_UTIL] Pose aplicada y horneada en: {mesh_obj.name}")
        return True
    except Exception as e:
        print(f"[POSE_UTIL] ERROR aplicando modificador en {mesh_obj.name}: {e}")
        return False


def _find_parent_armature(armature):
    """Encuentra el armature padre si existe"""
    if armature.parent and armature.parent.type == 'ARMATURE':
        return armature.parent
    return None


def _create_new_modifier(mesh_obj, parent_armature):
    """Crea un nuevo modificador de armature"""
    new_mod = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
    new_mod.object = parent_armature
    print(f"[POSE_UTIL] Nuevo modificador asignado a {mesh_obj.name} -> {parent_armature.name}")


def _safe_mode_set(mode):
    """Cambia de modo de forma segura"""
    try:
        ops.object.mode_set(mode=mode)
    except Exception:
        pass


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
        
        # Criterios de detección con pesos
        candidates = []
        
        for armature in armatures:
            score = 0
            
            # Puntos por número de huesos
            bone_count = len(armature.data.bones)
            score += bone_count
            
            # Penalizar si tiene "root" en el nombre
            if 'root' in armature.name.lower():
                score -= 50
            
            # Puntos por tener objetos mesh como hijos
            mesh_children = sum(1 for obj in bpy.data.objects 
                              if obj.type == 'MESH' and obj.parent == armature)
            score += mesh_children * 10
            
            # Puntos por ser más reciente (índice más alto en el nombre)
            if '.' in armature.name:
                try:
                    index = int(armature.name.split('.')[-1])
                    score += index
                except ValueError:
                    pass
            
            candidates.append((armature, score))
            
            if self.debug:
                print(f"[EXTERNAL_POSE] Candidato {armature.name}: score {score}")
        
        # Ordenar por score y devolver el mejor
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        if candidates and candidates[0][1] > 0:
            best_candidate = candidates[0][0]
            print(f"[EXTERNAL_POSE] Armature fuente detectado: {best_candidate.name}")
            return best_candidate
        
        return None
    
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
                bone_mappings = self._get_bone_mappings_from_settings()
            
            if not bone_mappings:
                print("[EXTERNAL_POSE] No hay mapeos de huesos disponibles")
                return False
            
            # Activar target armature y entrar en modo pose
            bpy.context.view_layer.objects.active = target_armature
            bpy.ops.object.mode_set(mode='POSE')
            
            copied_bones = 0
            
            for source_bone_name, target_bone_name in bone_mappings:
                if self._copy_bone_transforms(source_armature, target_armature, 
                                            source_bone_name, target_bone_name):
                    copied_bones += 1
                    if self.debug:
                        print(f"[EXTERNAL_POSE] Copiado: {source_bone_name} -> {target_bone_name}")
            
            bpy.ops.object.mode_set(mode='OBJECT')
            print(f"[EXTERNAL_POSE] Pose copiada exitosamente. {copied_bones} huesos procesados.")
            
            return copied_bones > 0
            
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error copiando pose: {e}")
            _safe_mode_set('OBJECT')
            return False
    
    def _get_bone_mappings_from_settings(self):
        """Obtiene los mapeos de huesos desde la configuración"""
        try:
            settings = bpy.context.scene.universal_gta_settings
            return [
                (m.source_bone, m.target_bone)
                for m in settings.bone_mappings
                if m.enabled and m.source_bone and m.target_bone
            ]
        except:
            return None
    
    def _copy_bone_transforms(self, source_armature, target_armature, 
                             source_bone_name, target_bone_name):
        """Copia las transformaciones de un hueso a otro"""
        try:
            if (source_bone_name not in source_armature.pose.bones or 
                target_bone_name not in target_armature.pose.bones):
                return False
            
            source_bone = source_armature.pose.bones[source_bone_name]
            target_bone = target_armature.pose.bones[target_bone_name]
            
            # Copiar transformaciones
            target_bone.location = source_bone.location.copy()
            target_bone.rotation_euler = source_bone.rotation_euler.copy()
            target_bone.rotation_quaternion = source_bone.rotation_quaternion.copy()
            target_bone.scale = source_bone.scale.copy()
            
            return True
            
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error copiando transformaciones: {e}")
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
            _safe_mode_set('OBJECT')
            return False


# Funciones de conveniencia para compatibilidad con código anterior
def apply_pose_to_armature(armature):
    """Función de conveniencia para aplicar pose a un armature"""
    return apply_manual_pose_to_children_and_reassign(armature)


def execute_external_pose_application(source_armature=None, target_armature=None):
    """Función de conveniencia para ejecutar aplicación de pose externa"""
    applier = ExternalPoseApplier()
    return applier.execute_full_pose_application(source_armature, target_armature)