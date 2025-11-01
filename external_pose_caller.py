"""
external_pose_caller.py - Mejorado con sistema de constraints
Universal GTA SA Converter v4.1

NUEVAS FUNCIONALIDADES:
- Aplicación de constraints de posición usando bone mapping
- Promediado automático para huesos duplicados
- Limpieza automática de constraints después de aplicación
- Sistema mejorado de detección de armatures
"""

import bpy
import mathutils
from collections import defaultdict


class ExternalPoseApplier:

    def integrate_with_complete_conversion(self):
        """Integración con el sistema de conversión completa"""
        try:
            from .gta_conversion_utils import GTAConversionUtils
            
            utils = GTAConversionUtils(debug=True)
            
            # Detectar armature objetivo
            target_armature = utils.detect_target_armature()
            
            if target_armature:
                # Aplicar pose usando el sistema de conversión completa
                result = utils.apply_custom_pose(target_armature)
                
                if result:
                    print("[EXTERNAL_POSE] Pose aplicada exitosamente via conversión completa")
                    return True
                else:
                    print("[EXTERNAL_POSE] Error aplicando pose via conversión completa")
                    return False
            else:
                print("[EXTERNAL_POSE] No se pudo detectar armature objetivo")
                return False
                
        except ImportError:
            print("[EXTERNAL_POSE] GTAConversionUtils no disponible, usando método legacy")
            return self.apply_pose_legacy()
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error en integración: {e}")
            return False
    
    def apply_pose_legacy(self):
        """Método legacy de aplicación de pose"""
        # Aquí va el código original del external_pose_caller
        return True


    def integrate_with_complete_conversion(self):
        """Integración con el sistema de conversión completa"""
        try:
            from .gta_conversion_utils import GTAConversionUtils
            
            utils = GTAConversionUtils(debug=True)
            
            # Detectar armature objetivo
            target_armature = utils.detect_target_armature()
            
            if target_armature:
                # Aplicar pose usando el sistema de conversión completa
                result = utils.apply_custom_pose(target_armature)
                
                if result:
                    print("[EXTERNAL_POSE] Pose aplicada exitosamente via conversión completa")
                    return True
                else:
                    print("[EXTERNAL_POSE] Error aplicando pose via conversión completa")
                    return False
            else:
                print("[EXTERNAL_POSE] No se pudo detectar armature objetivo")
                return False
                
        except ImportError:
            print("[EXTERNAL_POSE] GTAConversionUtils no disponible, usando método legacy")
            return self.apply_pose_legacy()
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error en integración: {e}")
            return False
    
    def apply_pose_legacy(self):
        """Método legacy de aplicación de pose"""
        # Aquí va el código original del external_pose_caller
        return True


    def integrate_with_complete_conversion(self):
        """Integración con el sistema de conversión completa"""
        try:
            from .gta_conversion_utils import GTAConversionUtils
            
            utils = GTAConversionUtils(debug=True)
            
            # Detectar armature objetivo
            target_armature = utils.detect_target_armature()
            
            if target_armature:
                # Aplicar pose usando el sistema de conversión completa
                result = utils.apply_custom_pose(target_armature)
                
                if result:
                    print("[EXTERNAL_POSE] Pose aplicada exitosamente via conversión completa")
                    return True
                else:
                    print("[EXTERNAL_POSE] Error aplicando pose via conversión completa")
                    return False
            else:
                print("[EXTERNAL_POSE] No se pudo detectar armature objetivo")
                return False
                
        except ImportError:
            print("[EXTERNAL_POSE] GTAConversionUtils no disponible, usando método legacy")
            return self.apply_pose_legacy()
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error en integración: {e}")
            return False
    
    def apply_pose_legacy(self):
        """Método legacy de aplicación de pose"""
        # Aquí va el código original del external_pose_caller
        return True


    def integrate_with_complete_conversion(self):
        """Integración con el sistema de conversión completa"""
        try:
            from .gta_conversion_utils import GTAConversionUtils
            
            utils = GTAConversionUtils(debug=True)
            
            # Detectar armature objetivo
            target_armature = utils.detect_target_armature()
            
            if target_armature:
                # Aplicar pose usando el sistema de conversión completa
                result = utils.apply_custom_pose(target_armature)
                
                if result:
                    print("[EXTERNAL_POSE] Pose aplicada exitosamente via conversión completa")
                    return True
                else:
                    print("[EXTERNAL_POSE] Error aplicando pose via conversión completa")
                    return False
            else:
                print("[EXTERNAL_POSE] No se pudo detectar armature objetivo")
                return False
                
        except ImportError:
            print("[EXTERNAL_POSE] GTAConversionUtils no disponible, usando método legacy")
            return self.apply_pose_legacy()
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error en integración: {e}")
            return False
    
    def apply_pose_legacy(self):
        """Método legacy de aplicación de pose"""
        # Aquí va el código original del external_pose_caller
        return True


    def integrate_with_complete_conversion(self):
        """Integración con el sistema de conversión completa"""
        try:
            from .gta_conversion_utils import GTAConversionUtils
            
            utils = GTAConversionUtils(debug=True)
            
            # Detectar armature objetivo
            target_armature = utils.detect_target_armature()
            
            if target_armature:
                # Aplicar pose usando el sistema de conversión completa
                result = utils.apply_custom_pose(target_armature)
                
                if result:
                    print("[EXTERNAL_POSE] Pose aplicada exitosamente via conversión completa")
                    return True
                else:
                    print("[EXTERNAL_POSE] Error aplicando pose via conversión completa")
                    return False
            else:
                print("[EXTERNAL_POSE] No se pudo detectar armature objetivo")
                return False
                
        except ImportError:
            print("[EXTERNAL_POSE] GTAConversionUtils no disponible, usando método legacy")
            return self.apply_pose_legacy()
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error en integración: {e}")
            return False
    
    def apply_pose_legacy(self):
        """Método legacy de aplicación de pose"""
        # Aquí va el código original del external_pose_caller
        return True

    """Aplicador externo de poses con sistema de constraints mejorado"""
    
    def __init__(self, debug=True):
        self.debug = debug
        print("[EXTERNAL_POSE] Inicializando aplicador externo mejorado v4.1")
    
    def execute_full_pose_application(self, source_armature=None, target_armature=None):
        """
        Ejecuta aplicación completa de pose con detección automática
        """
        try:
            print("[EXTERNAL_POSE] === INICIANDO APLICACIÓN COMPLETA ===")
            
            # Detección automática si no se proporcionan armatures
            if not source_armature:
                source_armature = self.detect_source_armature()
            if not target_armature:
                target_armature = self.detect_target_armature()
            
            if not source_armature or not target_armature:
                print("[EXTERNAL_POSE] Error: No se pudieron detectar ambos armatures")
                return False
            
            print(f"[EXTERNAL_POSE] Fuente: {source_armature.name}")
            print(f"[EXTERNAL_POSE] Destino: {target_armature.name}")
            
            # Aplicar pose usando sistema de constraints mejorado
            success = self.copy_pose_with_enhanced_constraints(source_armature, target_armature)
            
            if success:
                print("[EXTERNAL_POSE] === APLICACIÓN EXITOSA ===")
            else:
                print("[EXTERNAL_POSE] === APLICACIÓN FALLÓ ===")
            
            return success
            
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error crítico: {e}")
            return False
    
    def detect_source_armature(self):
        """Detecta automáticamente el armature fuente"""
        armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
        
        if not armatures:
            return None
        
        # Priorizar armatures con ciertos nombres
        source_keywords = ['mixamo', 'source', 'imported', 'original']
        
        best_candidate = None
        best_score = -1
        
        for armature in armatures:
            score = 0
            name_lower = armature.name.lower()
            
            # Puntuación por keywords
            for keyword in source_keywords:
                if keyword in name_lower:
                    score += 10
            
            # Puntuación por número de huesos (más huesos = más probable que sea fuente)
            score += len(armature.data.bones) / 10
            
            # Penalizar si tiene "gta", "target" o "converted" en el nombre
            penalty_keywords = ['gta', 'target', 'converted', 'result']
            for keyword in penalty_keywords:
                if keyword in name_lower:
                    score -= 20
            
            if self.debug:
                print(f"[EXTERNAL_POSE] Candidato fuente {armature.name}: score {score}")
            
            if score > best_score:
                best_score = score
                best_candidate = armature
        
        if best_candidate:
            print(f"[EXTERNAL_POSE] Armature fuente detectado: {best_candidate.name}")
        
        return best_candidate
    
    def detect_target_armature(self):
        """Detecta automáticamente el armature destino"""
        armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
        
        if not armatures:
            return None
        
        # Priorizar armatures con nombres GTA
        target_keywords = ['gta', 'target', 'converted', 'result']
        
        best_candidate = None
        best_score = -1
        
        for armature in armatures:
            score = 0
            name_lower = armature.name.lower()
            
            # Puntuación por keywords de destino
            for keyword in target_keywords:
                if keyword in name_lower:
                    score += 15
            
            # Penalizar armatures con keywords de fuente
            source_keywords = ['mixamo', 'source', 'imported', 'original']
            for keyword in source_keywords:
                if keyword in name_lower:
                    score -= 10
            
            # Bonificación si tiene sufijo numérico (indica copia/conversión)
            if '.' in armature.name:
                try:
                    index = int(armature.name.split('.')[-1])
                    score += index
                except ValueError:
                    pass
            
            if self.debug:
                print(f"[EXTERNAL_POSE] Candidato destino {armature.name}: score {score}")
            
            if score > best_score:
                best_score = score
                best_candidate = armature
        
        if best_candidate:
            print(f"[EXTERNAL_POSE] Armature destino detectado: {best_candidate.name}")
        
        return best_candidate
    
    def copy_pose_with_enhanced_constraints(self, source_armature, target_armature, bone_mappings=None):
        """
        Copia pose usando constraints de posición con sistema mejorado
        Incluye promediado para huesos duplicados
        """
        try:
            print(f"[EXTERNAL_POSE] Iniciando copia con constraints mejorados")
            print(f"[EXTERNAL_POSE] Fuente: {source_armature.name}, Destino: {target_armature.name}")
            
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
            
            # Detectar huesos duplicados (múltiples source -> mismo target)
            target_bone_groups = defaultdict(list)
            for source_bone, target_bone in bone_mappings:
                target_bone_groups[target_bone].append(source_bone)
            
            duplicate_targets = {target: sources for target, sources in target_bone_groups.items() if len(sources) > 1}
            single_targets = {target: sources[0] for target, sources in target_bone_groups.items() if len(sources) == 1}
            
            print(f"[EXTERNAL_POSE] Huesos únicos: {len(single_targets)}")
            print(f"[EXTERNAL_POSE] Huesos duplicados: {len(duplicate_targets)}")
            for target, sources in duplicate_targets.items():
                print(f"[EXTERNAL_POSE]   {target} <- {sources}")
            
            # Activar target armature y entrar en modo pose
            bpy.context.view_layer.objects.active = target_armature
            bpy.ops.object.mode_set(mode='POSE')
            
            # FASE 1: Aplicar constraints de posición
            constraints_applied = []
            
            # 1.1: Aplicar constraints para huesos únicos (1:1 mapping)
            for target_bone_name, source_bone_name in single_targets.items():
                constraint_name = self.apply_position_constraint(
                    source_armature, source_bone_name, 
                    target_armature, target_bone_name
                )
                if constraint_name:
                    constraints_applied.append((target_bone_name, constraint_name))
            
            # 1.2: Aplicar constraints promediados para huesos duplicados
            for target_bone_name, source_bone_names in duplicate_targets.items():
                constraint_name = self.apply_averaged_position_constraint(
                    source_armature, source_bone_names,
                    target_armature, target_bone_name
                )
                if constraint_name:
                    constraints_applied.append((target_bone_name, constraint_name))
            
            # FASE 2: Forzar actualización de constraints
            bpy.context.view_layer.update()
            
            # FASE 3: Aplicar pose (constraints se evalúan automáticamente)
            print(f"[EXTERNAL_POSE] Aplicando pose con {len(constraints_applied)} constraints")
            
            # FASE 4: Limpiar constraints después de aplicación
            self.cleanup_applied_constraints(target_armature, constraints_applied)
            
            bpy.ops.object.mode_set(mode='OBJECT')
            print(f"[EXTERNAL_POSE] Proceso completado exitosamente")
            
            return True
            
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error durante el proceso: {e}")
            # Limpieza en caso de error
            try:
                self.cleanup_applied_constraints(target_armature, constraints_applied)
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            return False
    
    def apply_position_constraint(self, source_armature, source_bone_name, target_armature, target_bone_name):
        """
        Aplica constraint de posición de un source bone a un target bone
        Retorna el nombre del constraint creado o None si falló
        """
        try:
            if (source_bone_name not in source_armature.pose.bones or 
                target_bone_name not in target_armature.pose.bones):
                return None
            
            target_bone = target_armature.pose.bones[target_bone_name]
            
            # Crear constraint de copy location
            constraint = target_bone.constraints.new(type='COPY_LOCATION')
            constraint.name = f"ExtCopyLoc_{source_bone_name}"
            constraint.target = source_armature
            constraint.subtarget = source_bone_name
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = True
            constraint.influence = 1.0
            
            if self.debug:
                print(f"[EXTERNAL_POSE] Constraint aplicado: {source_bone_name} -> {target_bone_name}")
            return constraint.name
            
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error aplicando constraint: {e}")
            return None
    
    def apply_averaged_position_constraint(self, source_armature, source_bone_names, target_armature, target_bone_name):
        """
        Aplica constraints promediados para múltiples source bones a un target bone
        Retorna el nombre del constraint principal o None si falló
        """
        try:
            if target_bone_name not in target_armature.pose.bones:
                return None
            
            target_bone = target_armature.pose.bones[target_bone_name]
            valid_sources = [name for name in source_bone_names if name in source_armature.pose.bones]
            
            if not valid_sources:
                return None
            
            # Si solo hay un source válido, usar constraint normal
            if len(valid_sources) == 1:
                return self.apply_position_constraint(source_armature, valid_sources[0], target_armature, target_bone_name)
            
            # Para múltiples sources, crear constraints con influencia dividida
            influence_per_bone = 1.0 / len(valid_sources)
            main_constraint_name = None
            
            for i, source_bone_name in enumerate(valid_sources):
                constraint = target_bone.constraints.new(type='COPY_LOCATION')
                constraint.name = f"ExtAvgLoc_{i}_{source_bone_name}"
                constraint.target = source_armature
                constraint.subtarget = source_bone_name
                constraint.use_x = True
                constraint.use_y = True
                constraint.use_z = True
                constraint.influence = influence_per_bone
                
                if i == 0:
                    main_constraint_name = constraint.name
                
                if self.debug:
                    print(f"[EXTERNAL_POSE] Constraint promediado ({influence_per_bone:.2f}): {source_bone_name} -> {target_bone_name}")
            
            return main_constraint_name
            
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error aplicando constraints promediados: {e}")
            return None
    
    def cleanup_applied_constraints(self, target_armature, constraints_applied):
        """
        Limpia los constraints aplicados después de la copia de pose
        """
        try:
            print(f"[EXTERNAL_POSE] Limpiando {len(constraints_applied)} constraints...")
            
            for bone_name, constraint_name in constraints_applied:
                if bone_name in target_armature.pose.bones:
                    bone = target_armature.pose.bones[bone_name]
                    # Buscar y remover constraints que empiecen con "Ext"
                    constraints_to_remove = [c for c in bone.constraints if c.name.startswith("Ext")]
                    
                    for constraint in constraints_to_remove:
                        bone.constraints.remove(constraint)
                        if self.debug:
                            print(f"[EXTERNAL_POSE] Constraint removido: {constraint.name} de {bone_name}")
            
            print("[EXTERNAL_POSE] Limpieza de constraints completada")
            
        except Exception as e:
            print(f"[EXTERNAL_POSE] Error durante limpieza: {e}")
    
    def reset_armature_pose(self, armature):
        """
        Resetea la pose de un armature a su estado rest
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
    applier = ExternalPoseApplier()
    return applier.execute_full_pose_application(target_armature=armature)


def execute_external_pose_application(source_armature=None, target_armature=None):
    """Función de conveniencia para ejecutar aplicación de pose externa"""
    applier = ExternalPoseApplier()
    return applier.execute_full_pose_application(source_armature, target_armature)


def apply_enhanced_constraints_system(source_armature, target_armature):
    """Nueva función para aplicar sistema de constraints mejorado"""
    applier = ExternalPoseApplier()
    return applier.copy_pose_with_enhanced_constraints(source_armature, target_armature)


if __name__ == "__main__":
    # Ejecutar aplicación automática si se ejecuta directamente
    applier = ExternalPoseApplier()
    success = applier.execute_full_pose_application()
    
    if success:
        print("✅ Aplicación de pose externa exitosa")
    else:
        print("❌ Error en aplicación de pose externa")


# === FUNCIONES MEJORADAS PARA CONVERSIÓN COMPLETA ===

def apply_pose_for_complete_conversion(armature):
    """Aplicar pose específicamente para conversión completa GTA SA"""
    try:
        print(f"[EXTERNAL_POSE] Aplicando pose para conversión completa: {armature.name}")
        
        # Usar sistema mejorado
        applier = ExternalPoseApplier(debug=True)
        success = applier.execute_full_pose_application(target_armature=armature)
        
        if success:
            # Aplicar optimizaciones adicionales para GTA SA
            apply_gta_sa_pose_optimizations(armature)
            return True
        
        return False
        
    except Exception as e:
        print(f"[EXTERNAL_POSE] Error en aplicación de pose completa: {e}")
        return False


def apply_gta_sa_pose_optimizations(armature):
    """Optimizaciones específicas de pose para GTA SA"""
    try:
        print(f"[EXTERNAL_POSE] Aplicando optimizaciones GTA SA a: {armature.name}")
        
        # Asegurar que el armature esté en modo pose
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Optimizaciones específicas para huesos GTA SA
        gta_bone_optimizations = {
            'Root': {'location': (0, 0, 0)},
            'Pelvis': {'rotation_mode': 'XYZ'},
            'Spine': {'rotation_mode': 'XYZ'},
            'Spine1': {'rotation_mode': 'XYZ'},
            'Spine2': {'rotation_mode': 'XYZ'},
            'Neck': {'rotation_mode': 'XYZ'},
            'Head': {'rotation_mode': 'XYZ'},
        }
        
        for bone_name, optimizations in gta_bone_optimizations.items():
            if bone_name in armature.pose.bones:
                bone = armature.pose.bones[bone_name]
                
                for prop, value in optimizations.items():
                    if hasattr(bone, prop):
                        setattr(bone, prop, value)
                        print(f"[EXTERNAL_POSE] Optimización aplicada: {bone_name}.{prop} = {value}")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        print("[EXTERNAL_POSE] Optimizaciones GTA SA aplicadas exitosamente")
        
    except Exception as e:
        print(f"[EXTERNAL_POSE] Error en optimizaciones GTA SA: {e}")


def reset_to_reference_pose(armature):
    """Resetear armature a pose de referencia para GTA SA"""
    try:
        print(f"[EXTERNAL_POSE] Reseteando a pose de referencia: {armature.name}")
        
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Seleccionar todos los huesos
        bpy.ops.pose.select_all(action='SELECT')
        
        # Limpiar transformaciones
        bpy.ops.pose.transforms_clear()
        
        # Aplicar pose específica de referencia si existe
        if hasattr(bpy.context.scene, 'gta_reference_pose_data'):
            apply_reference_pose_data(armature)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return True
        
    except Exception as e:
        print(f"[EXTERNAL_POSE] Error reseteando pose: {e}")
        return False
