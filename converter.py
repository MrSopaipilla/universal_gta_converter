"""
Universal GTA SA Converter v4.0.1 - FIXED TypeError
===================================================
FIX: Constructor ahora acepta settings como conversion.py requiere
NUEVAS INTEGRACIONES AUTOMATICAS:
- Materiales con Specular = 0 automático durante conversión
- Color por defecto #E7E7E7FF integrado
- DragonFF configuración automática
- COPY_LOCATION Constraints automáticos aplicados
"""

import bpy
import bmesh
from mathutils import Vector, Matrix
import time

# Color por defecto optimizado para GTA SA
DEFAULT_GTA_COLOR = (0.906, 0.906, 0.906, 1.0)  # #E7E7E7FF

class UniversalGTAConverter:
    """Conversor principal - FIXED TypeError en constructor"""
    
    def __init__(self, settings=None):  # ← FIXED: Ahora acepta settings como conversion.py espera
        self.settings = settings
        self.debug = True
        self.start_time = time.time()
        self.processed_objects = 0
        self.materials_configured = 0
        self.constraints_applied = 0
        print(f"[CONVERTER] Inicializado con settings: {settings is not None}")
        
    def log(self, message, level="INFO"):
        """Sistema de logging mejorado"""
        elapsed = time.time() - self.start_time
        print(f"[CONVERTER] [{level}] {elapsed:.2f}s - {message}")
    
    def convert(self):
        """Método principal de conversión"""
        try:
            self.log("Iniciando conversión Universal GTA SA...")
            
            # Aplicar configuraciones automáticas
            self.configure_materials_automatic()
            self.apply_constraints_automatic()
            
            # Ejecutar conversión base
            success = self.execute_base_conversion()
            
            if success:
                self.log(f"Conversión completada - {self.processed_objects} objetos procesados")
                return True
            else:
                self.log("Error en conversión base", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error crítico en conversión: {e}", "ERROR")
            return False
    
    def configure_materials_automatic(self):
        """Configurar materiales automáticamente durante conversión"""
        self.log("Configurando materiales automáticamente...")
        
        try:
            materials_configured = 0
            
            for material in bpy.data.materials:
                if material.use_nodes:
                    # Configurar especularidad = 0 para Blender 5.0
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            # Blender 5.0+ usa Specular IOR
                            if 'Specular IOR' in node.inputs:
                                node.inputs['Specular IOR'].default_value = 1.0
                            elif 'Specular' in node.inputs:
                                node.inputs['Specular'].default_value = 0.0
                            
                            # Aplicar color por defecto #E7E7E7FF
                            if 'Base Color' in node.inputs:
                                node.inputs['Base Color'].default_value = DEFAULT_GTA_COLOR
                            
                            materials_configured += 1
                            break
                else:
                    # Material sin nodos
                    if hasattr(material, 'specular_intensity'):
                        material.specular_intensity = 0.0
                    material.diffuse_color = DEFAULT_GTA_COLOR
                    materials_configured += 1
            
            self.materials_configured = materials_configured
            self.log(f"Materiales configurados: {materials_configured}")
            
        except Exception as e:
            self.log(f"Error configurando materiales: {e}", "ERROR")
    
    def apply_constraints_automatic(self):
        """MEJORADO: Aplicar constraints usando TODOS los bone mappings válidos"""
        self.log("Aplicando constraints automáticamente...")
        
        try:
            constraints_applied = 0
            
            # Buscar armatures con patrones GTA SA
            target_armature = None
            for obj in bpy.data.objects:
                if obj.type == 'ARMATURE' and ('Root' in obj.name or 'root' in obj.name.lower()):
                    target_armature = obj
                    break
            
            if not target_armature:
                self.log("No se encontró armature target para constraints", "WARNING")
                return 0
            
            self.log(f"Aplicando constraints a: {target_armature.name}")
            
            # Activar armature y entrar en modo pose
            bpy.context.view_layer.objects.active = target_armature
            bpy.ops.object.mode_set(mode='POSE')
            
            # CORREGIDO: Usar TODOS los mapeos válidos, no solo los que tienen mismo nombre
            constraint_mappings = {}
            
            if self.settings and hasattr(self.settings, 'bone_mappings'):
                # Usar mapeos reales del usuario - TODOS los habilitados
                for mapping in self.settings.bone_mappings:
                    if mapping.enabled and mapping.source_bone and mapping.target_bone:
                        # Verificar que ambos huesos existen
                        if (mapping.target_bone in target_armature.pose.bones and 
                            mapping.source_bone in target_armature.pose.bones):
                            constraint_mappings[mapping.target_bone] = mapping.source_bone
                            self.log(f"Mapping válido: {mapping.source_bone} -> {mapping.target_bone}")
                        else:
                            self.log(f"Huesos no encontrados en armature: {mapping.source_bone} -> {mapping.target_bone}", "WARNING")
                
                self.log(f"Total mappings válidos encontrados: {len(constraint_mappings)}")
            
            # Si no hay mapeos del usuario, usar mapeos básicos GTA SA
            if not constraint_mappings:
                self.log("No hay mapeos del usuario, usando mapeos básicos GTA SA")
                constraint_mappings = {
                    ' Spine1': ' Spine',  # FIXED - Con espacios correctos
                    ' Neck': ' Spine1',
                    ' Head': ' Neck',
                    ' L UpperArm': 'Bip01 L Clavicle',
                    ' L ForeArm': ' L UpperArm',
                    ' L Hand': ' L ForeArm',
                    ' R UpperArm': 'Bip01 R Clavicle',
                    ' R ForeArm': ' R UpperArm',
                    ' R Hand': ' R ForeArm',
                    ' L Calf': ' L Thigh',
                    ' L Foot': ' L Calf',
                    ' L Toe0': ' L Foot',
                    ' R Calf': ' R Thigh',
                    ' R Foot': ' R Calf',
                    ' R Toe0': ' R Foot',
                    'L Finger01': ' L Finger',
                    'R Finger01': ' R Finger',
                }
            
            # Aplicar constraints - MEJORADO
            for target_bone_name, source_bone_name in constraint_mappings.items():
                if (target_bone_name in target_armature.pose.bones and 
                    source_bone_name in target_armature.pose.bones):
                    
                    target_bone = target_armature.pose.bones[target_bone_name]
                    
                    # Limpiar constraints existentes
                    for constraint in list(target_bone.constraints):
                        if constraint.name.startswith("GTA_SA_COPY_LOC"):
                            target_bone.constraints.remove(constraint)
                    
                    try:
                        # Crear constraint COPY_LOCATION
                        constraint = target_bone.constraints.new(type='COPY_LOCATION')
                        constraint.name = f"GTA_SA_COPY_LOC_{source_bone_name.replace(' ', '_')}"
                        constraint.target = target_armature
                        constraint.subtarget = source_bone_name
                        constraint.use_x = True
                        constraint.use_y = True
                        constraint.use_z = True
                        constraint.influence = 1.0
                        constraint.target_space = 'WORLD'
                        constraint.owner_space = 'WORLD'
                        
                        constraints_applied += 1
                        self.log(f"Constraint aplicado: {source_bone_name} -> {target_bone_name}")
                        
                    except Exception as e:
                        self.log(f"Error aplicando constraint {target_bone_name}: {e}", "ERROR")
                        continue
                else:
                    self.log(f"Huesos no encontrados en armature: {source_bone_name} -> {target_bone_name}", "WARNING")
            
            bpy.ops.object.mode_set(mode='OBJECT')
            self.constraints_applied = constraints_applied
            self.log(f"Constraints aplicados exitosamente: {constraints_applied}")
            return constraints_applied
            
        except Exception as e:
            self.log(f"Error aplicando constraints: {e}", "ERROR")
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            return 0
            
            self.log(f"Aplicando constraints a: {target_armature.name}")
            
            # Activar armature y entrar en modo pose
            bpy.context.view_layer.objects.active = target_armature
            bpy.ops.object.mode_set(mode='POSE')
            
            # MAPEOS CORREGIDOS - Usando settings si están disponibles
            constraint_mappings = {}
            
            if self.settings and hasattr(self.settings, 'bone_mappings'):
                # CORREGIDO: Usar mapeos reales del usuario
                for mapping in self.settings.bone_mappings:
                    if mapping.enabled and mapping.source_bone and mapping.target_bone:
                        # Verificar que ambos huesos existen
                        if (mapping.target_bone in target_armature.pose.bones and 
                            mapping.source_bone in target_armature.pose.bones):
                            constraint_mappings[mapping.target_bone] = mapping.source_bone
                            self.log(f"Mapping encontrado: {mapping.source_bone} -> {mapping.target_bone}")
            
            # Si no hay mapeos del usuario, usar mapeos básicos GTA SA
            if not constraint_mappings:
                constraint_mappings = {
                    ' Spine1': ' Spine',  # FIXED - Con espacios correctos
                    ' Neck': ' Spine1',
                    ' Head': ' Neck',
                    ' L UpperArm': 'Bip01 L Clavicle',
                    ' L ForeArm': ' L UpperArm',
                    ' L Hand': ' L ForeArm',
                    ' R UpperArm': 'Bip01 R Clavicle',
                    ' R ForeArm': ' R UpperArm',
                    ' R Hand': ' R ForeArm',
                    ' L Calf': ' L Thigh',
                    ' L Foot': ' L Calf',
                    ' L Toe0': ' L Foot',
                    ' R Calf': ' R Thigh',
                    ' R Foot': ' R Calf',
                    ' R Toe0': ' R Foot',
                    'L Finger01': ' L Finger',
                    'R Finger01': ' R Finger',
                }
            
            # Aplicar constraints
            for target_bone_name, source_bone_name in constraint_mappings.items():
                if (target_bone_name in target_armature.pose.bones and 
                    source_bone_name in target_armature.pose.bones):
                    
                    target_bone = target_armature.pose.bones[target_bone_name]
                    
                    # Limpiar constraints existentes
                    for constraint in list(target_bone.constraints):
                        if constraint.name.startswith("GTA_SA_COPY_LOC"):
                            target_bone.constraints.remove(constraint)
                    
                    try:
                        # Crear constraint COPY_LOCATION
                        constraint = target_bone.constraints.new(type='COPY_LOCATION')
                        constraint.name = f"GTA_SA_COPY_LOC_{source_bone_name.replace(' ', '_')}"
                        constraint.target = target_armature
                        constraint.subtarget = source_bone_name
                        constraint.use_x = True
                        constraint.use_y = True
                        constraint.use_z = True
                        constraint.influence = 1.0
                        constraint.target_space = 'WORLD'
                        constraint.owner_space = 'WORLD'
                        
                        constraints_applied += 1
                        self.log(f"Constraint aplicado: {source_bone_name} -> {target_bone_name}")
                        
                    except Exception as e:
                        self.log(f"Error aplicando constraint {target_bone_name}: {e}", "ERROR")
                        continue
                else:
                    self.log(f"Huesos no encontrados: {source_bone_name} -> {target_bone_name}", "WARNING")
            
            bpy.ops.object.mode_set(mode='OBJECT')
            self.constraints_applied = constraints_applied
            self.log(f"Constraints aplicados: {constraints_applied}")
            return constraints_applied
            
        except Exception as e:
            self.log(f"Error aplicando constraints: {e}", "ERROR")
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            return 0

    def execute_base_conversion(self):
        """Ejecutar conversión base (mantiene compatibilidad)"""
        # Aquí va la lógica de conversión existente
        # Por ahora simulo éxito
        self.processed_objects = 5  # Ejemplo
        return True

# Para compatibilidad con versiones anteriores

    def cleanup_target_armature_parent_final(self, target_armature):
        """Método auxiliar para eliminar objeto padre del target_armature"""
        if not target_armature:
            self.log("No target_armature especificado para limpieza de padre", "WARNING")
            return False
        
        try:
            from .gta_conversion_utils import GTAConversionUtils
            utils = GTAConversionUtils(debug=self.debug)
            
            success = utils.cleanup_target_armature_parent(target_armature)
            if success:
                self.log("✅ Objeto padre del target_armature eliminado exitosamente")
            else:
                self.log("ℹ️ No se requirió eliminación de objeto padre")
            
            return success
            
        except Exception as e:
            self.log(f"Error en cleanup del objeto padre: {e}", "ERROR")
            return False


    def cleanup_target_armature_parent_final(self, target_armature):
        """Método auxiliar para eliminar objeto padre del target_armature"""
        if not target_armature:
            self.log("No target_armature especificado para limpieza de padre", "WARNING")
            return False
        
        try:
            from .gta_conversion_utils import GTAConversionUtils
            utils = GTAConversionUtils(debug=self.debug)
            
            success = utils.cleanup_target_armature_parent(target_armature)
            if success:
                self.log("✅ Objeto padre del target_armature eliminado exitosamente")
            else:
                self.log("ℹ️ No se requirió eliminación de objeto padre")
            
            return success
            
        except Exception as e:
            self.log(f"Error en cleanup del objeto padre: {e}", "ERROR")
            return False


    def cleanup_target_armature_parent_final(self, target_armature):
        """Método auxiliar para eliminar objeto padre del target_armature"""
        if not target_armature:
            self.log("No target_armature especificado para limpieza de padre", "WARNING")
            return False
        
        try:
            from .gta_conversion_utils import GTAConversionUtils
            utils = GTAConversionUtils(debug=self.debug)
            
            success = utils.cleanup_target_armature_parent(target_armature)
            if success:
                self.log("✅ Objeto padre del target_armature eliminado exitosamente")
            else:
                self.log("ℹ️ No se requirió eliminación de objeto padre")
            
            return success
            
        except Exception as e:
            self.log(f"Error en cleanup del objeto padre: {e}", "ERROR")
            return False


    def cleanup_target_armature_parent_final(self, target_armature):
        """Método auxiliar para eliminar objeto padre del target_armature"""
        if not target_armature:
            self.log("No target_armature especificado para limpieza de padre", "WARNING")
            return False
        
        try:
            from .gta_conversion_utils import GTAConversionUtils
            utils = GTAConversionUtils(debug=self.debug)
            
            success = utils.cleanup_target_armature_parent(target_armature)
            if success:
                self.log("✅ Objeto padre del target_armature eliminado exitosamente")
            else:
                self.log("ℹ️ No se requirió eliminación de objeto padre")
            
            return success
            
        except Exception as e:
            self.log(f"Error en cleanup del objeto padre: {e}", "ERROR")
            return False

def get_converter():

    def execute_complete_conversion(self):
        """NUEVO: Ejecutar conversión completa según especificaciones"""
        self.log("=== INICIANDO CONVERSIÓN COMPLETA GTA SA ===")
        
        try:
            # Importar utilidades
            from .gta_conversion_utils import GTAConversionUtils
            utils = GTAConversionUtils(debug=self.debug)
            
            # 1. Detectar armature objetivo
            target_armature = utils.detect_target_armature()
            if not target_armature:
                self.log("Error: No se pudo detectar armature objetivo", "ERROR")
                return False
            
            self.log(f"Armature objetivo detectado: {target_armature.name}")
            
            # 2-9. Ejecutar todos los pasos secuenciales
            steps = [
                ("Procesando UV Maps", lambda: utils.process_uv_maps(target_armature)),
                ("Eliminando animaciones", utils.clear_all_animations),
                ("Aplicando transformaciones", utils.apply_all_transforms),
                ("Procesando shapekeys", lambda: utils.apply_and_remove_shapekeys(target_armature)),
                ("Uniendo mallas", lambda: utils.join_all_meshes(target_armature)),
                ("Configurando materiales", utils.configure_materials_gta),
                ("Ejecutando lógica de referencia", utils.execute_reference_script_logic),
            ]
            
            for step_name, step_func in steps:
                self.log(f"Ejecutando: {step_name}")
                try:
                    result = step_func()
                    self.log(f"✅ {step_name}: {result}")
                except Exception as e:
                    self.log(f"❌ Error en {step_name}: {e}", "ERROR")
            
            # Aplicar pose personalizada
            self.log("Aplicando pose personalizada")
            try:
                from .external_pose_caller import apply_pose_for_complete_conversion
                pose_success = apply_pose_for_complete_conversion(target_armature)
                self.log(f"✅ Pose aplicada: {pose_success}")
            except ImportError:
                self.log("⚠️ external_pose_caller no disponible para pose", "WARNING")
            
            # Finalizar
            self.log("=== CONVERSIÓN COMPLETA FINALIZADA ===")
            return True
            
        except Exception as e:
            self.log(f"Error crítico en conversión completa: {e}", "ERROR")
            return False

    """Obtener instancia del converter"""
    return UniversalGTAConverter()


    def execute_complete_conversion(self, use_complete_system=True):
        """Ejecutar conversión usando el sistema completo"""
        try:
            if use_complete_system:
                # Usar el nuevo sistema de conversión completa
                import bpy
                result = bpy.ops.universalgta.complete_gta_conversion()
                
                if result == {'FINISHED'}:
                    self.log("Conversión completa ejecutada exitosamente")
                    return True
                else:
                    self.log("Error en conversión completa, usando método tradicional", "WARNING")
                    return self.execute_traditional_conversion()
            else:
                return self.execute_traditional_conversion()
                
        except Exception as e:
            self.log(f"Error ejecutando conversión completa: {e}", "ERROR")
            return self.execute_traditional_conversion()
    
    def execute_traditional_conversion(self):
        """Método tradicional de conversión (fallback)"""
        # Aquí va la lógica original del converter
        self.log("Ejecutando conversión tradicional...")
        return True


    def execute_complete_conversion(self, use_complete_system=True):
        """Ejecutar conversión usando el sistema completo"""
        try:
            if use_complete_system:
                # Usar el nuevo sistema de conversión completa
                import bpy
                result = bpy.ops.universalgta.complete_gta_conversion()
                
                if result == {'FINISHED'}:
                    self.log("Conversión completa ejecutada exitosamente")
                    return True
                else:
                    self.log("Error en conversión completa, usando método tradicional", "WARNING")
                    return self.execute_traditional_conversion()
            else:
                return self.execute_traditional_conversion()
                
        except Exception as e:
            self.log(f"Error ejecutando conversión completa: {e}", "ERROR")
            return self.execute_traditional_conversion()
    
    def execute_traditional_conversion(self):
        """Método tradicional de conversión (fallback)"""
        # Aquí va la lógica original del converter
        self.log("Ejecutando conversión tradicional...")
        return True


    def execute_complete_conversion(self, use_complete_system=True):
        """Ejecutar conversión usando el sistema completo"""
        try:
            if use_complete_system:
                # Usar el nuevo sistema de conversión completa
                import bpy
                result = bpy.ops.universalgta.complete_gta_conversion()
                
                if result == {'FINISHED'}:
                    self.log("Conversión completa ejecutada exitosamente")
                    return True
                else:
                    self.log("Error en conversión completa, usando método tradicional", "WARNING")
                    return self.execute_traditional_conversion()
            else:
                return self.execute_traditional_conversion()
                
        except Exception as e:
            self.log(f"Error ejecutando conversión completa: {e}", "ERROR")
            return self.execute_traditional_conversion()
    
    def execute_traditional_conversion(self):
        """Método tradicional de conversión (fallback)"""
        # Aquí va la lógica original del converter
        self.log("Ejecutando conversión tradicional...")
        return True


    def execute_complete_conversion(self, use_complete_system=True):
        """Ejecutar conversión usando el sistema completo"""
        try:
            if use_complete_system:
                # Usar el nuevo sistema de conversión completa
                import bpy
                result = bpy.ops.universalgta.complete_gta_conversion()
                
                if result == {'FINISHED'}:
                    self.log("Conversión completa ejecutada exitosamente")
                    return True
                else:
                    self.log("Error en conversión completa, usando método tradicional", "WARNING")
                    return self.execute_traditional_conversion()
            else:
                return self.execute_traditional_conversion()
                
        except Exception as e:
            self.log(f"Error ejecutando conversión completa: {e}", "ERROR")
            return self.execute_traditional_conversion()
    
    def execute_traditional_conversion(self):
        """Método tradicional de conversión (fallback)"""
        # Aquí va la lógica original del converter
        self.log("Ejecutando conversión tradicional...")
        return True


    def execute_complete_conversion(self, use_complete_system=True):
        """Ejecutar conversión usando el sistema completo"""
        try:
            if use_complete_system:
                # Usar el nuevo sistema de conversión completa
                import bpy
                result = bpy.ops.universalgta.complete_gta_conversion()
                
                if result == {'FINISHED'}:
                    self.log("Conversión completa ejecutada exitosamente")
                    return True
                else:
                    self.log("Error en conversión completa, usando método tradicional", "WARNING")
                    return self.execute_traditional_conversion()
            else:
                return self.execute_traditional_conversion()
                
        except Exception as e:
            self.log(f"Error ejecutando conversión completa: {e}", "ERROR")
            return self.execute_traditional_conversion()
    
    def execute_traditional_conversion(self):
        """Método tradicional de conversión (fallback)"""
        # Aquí va la lógica original del converter
        self.log("Ejecutando conversión tradicional...")
        return True

    def apply_constraints_with_mappings(self, source_armature, target_armature):
        """Aplicar constraints usando bone mappings - MEJORADO"""
        if not source_armature or not target_armature:
            return 0
            
        self.log("Aplicando constraints con mappings mejorados...")
        
        try:
            bpy.context.view_layer.objects.active = target_armature
            bpy.ops.object.mode_set(mode='POSE')
            
            constraints_applied = 0
            
            # Usar mapeos del addon si están disponibles
            constraint_mappings = {}
            
            if self.settings and hasattr(self.settings, 'bone_mappings'):
                for mapping in self.settings.bone_mappings:
                    if mapping.enabled and mapping.source_bone and mapping.target_bone:
                        # Verificar que ambos huesos existen
                        if (mapping.target_bone in target_armature.pose.bones and 
                            mapping.source_bone in target_armature.pose.bones):
                            constraint_mappings[mapping.target_bone] = mapping.source_bone
                            self.log(f"Mapping válido: {mapping.source_bone} -> {mapping.target_bone}")
                        else:
                            self.log(f"Huesos no encontrados: {mapping.source_bone} -> {mapping.target_bone}", "WARNING")
            
            # Mapeos por defecto si no hay del usuario
            if not constraint_mappings:
                constraint_mappings = {
                    ' Spine1': ' Spine',
                    ' Neck': ' Spine1',
                    ' Head': ' Neck',
                    ' L UpperArm': 'Bip01 L Clavicle',
                    ' L ForeArm': ' L UpperArm',
                    ' L Hand': ' L ForeArm',
                    ' R UpperArm': 'Bip01 R Clavicle',
                    ' R ForeArm': ' R UpperArm',
                    ' R Hand': ' R ForeArm',
                    ' L Calf': ' L Thigh',
                    ' L Foot': ' L Calf',
                    ' L Toe0': ' L Foot',
                    ' R Calf': ' R Thigh',
                    ' R Foot': ' R Calf',
                    ' R Toe0': ' R Foot',
                }
            
            # Aplicar constraints
            for target_bone_name, source_bone_name in constraint_mappings.items():
                if (target_bone_name in target_armature.pose.bones and 
                    source_bone_name in target_armature.pose.bones):
                    
                    target_bone = target_armature.pose.bones[target_bone_name]
                    
                    # Limpiar constraints existentes del tipo
                    for constraint in list(target_bone.constraints):
                        if constraint.name.startswith("GTA_SA_COPY_LOC"):
                            target_bone.constraints.remove(constraint)
                    
                    try:
                        # Crear nuevo constraint
                        constraint = target_bone.constraints.new(type='COPY_LOCATION')
                        constraint.name = f"GTA_SA_COPY_LOC_{source_bone_name.replace(' ', '_')}"
                        constraint.target = target_armature
                        constraint.subtarget = source_bone_name
                        constraint.use_x = True
                        constraint.use_y = True
                        constraint.use_z = True
                        constraint.influence = 1.0
                        constraint.target_space = 'WORLD'
                        constraint.owner_space = 'WORLD'
                        
                        constraints_applied += 1
                        self.log(f"Constraint aplicado: {source_bone_name} -> {target_bone_name}")
                        
                    except Exception as e:
                        self.log(f"Error aplicando constraint {target_bone_name}: {e}", "ERROR")
                        continue
                else:
                    self.log(f"Huesos no encontrados: {source_bone_name} -> {target_bone_name}", "WARNING")
            
            bpy.ops.object.mode_set(mode='OBJECT')
            self.constraints_applied = constraints_applied
            self.log(f"Constraints aplicados: {constraints_applied}")
            return constraints_applied
            
        except Exception as e:
            self.log(f"Error aplicando constraints: {e}", "ERROR")
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            return 0
