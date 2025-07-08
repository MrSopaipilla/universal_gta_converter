"""
Operadores de conversión para Universal GTA SA Converter
VERSIÓN CON MANEJO MEJORADO DE ERRORES DE POSE
"""

import bpy
from bpy.types import Operator
from ..converter import UniversalGTAConverter
from .. import external_pose_caller


class UNIVERSALGTA_OT_execute_conversion(Operator):
    """Ejecutar conversión a GTA SA con manejo mejorado de pose personalizada"""
    bl_idname = "universalgta.execute_conversion"
    bl_label = "Convert to GTA SA"
    bl_description = "Execute the conversion from custom armature to GTA SA format"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Validación exhaustiva antes de la conversión
        validation_result = self.validate_conversion_setup(settings)
        if not validation_result['valid']:
            self.report({'ERROR'}, validation_result['message'])
            return {'CANCELLED'}
        
        # Crear instancia del converter
        converter = UniversalGTAConverter(settings)
        
        try:
            print("[CONVERSION] Iniciando conversión a GTA SA...")
            
            # Ejecutar conversión
            success = converter.convert()
            
            if not success:
                self.report({'ERROR'}, "Falló la conversión")
                return {'CANCELLED'}
            
            # Conversión exitosa
            conversion_message = "Conversión completada con éxito"
            
            # Auto-aplicar pose personalizada si está habilitado
            if settings.auto_apply_custom_pose:
                pose_result = self._apply_custom_pose_safe(settings)
                
                if pose_result['success']:
                    conversion_message += " con pose personalizada aplicada"
                    self.report({'INFO'}, conversion_message)
                elif pose_result['attempted']:
                    # La pose falló pero la conversión fue exitosa
                    conversion_message += f" (advertencia en pose: {pose_result['message']})"
                    self.report({'WARNING'}, conversion_message)
                else:
                    # No se intentó aplicar pose
                    conversion_message += " (pose personalizada omitida)"
                    self.report({'INFO'}, conversion_message)
            else:
                self.report({'INFO'}, conversion_message)
            
            return {'FINISHED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error durante la conversión: {str(e)}")
            print(f"[CONVERSION] Error en conversión: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
    
    def _apply_custom_pose_safe(self, settings):
        """
        Aplica pose personalizada de forma segura sin fallar la conversión
        
        Returns:
            dict: {'success': bool, 'attempted': bool, 'message': str}
        """
        result = {
            'success': False,
            'attempted': False,
            'message': ''
        }
        
        try:
            print("[CONVERSION] === INICIANDO APLICACIÓN DE POSE PERSONALIZADA ===")
            result['attempted'] = True
            
            # Verificar setup post-conversión
            external_pose_caller.verify_post_conversion_setup()
            
            # Buscar el armature resultante de la conversión
            target_armature = self._find_conversion_result_armature(settings)
            
            if not target_armature:
                result['message'] = "No se encontró armature resultante"
                print("[CONVERSION] ✗ No se encontró armature para aplicar pose")
                return result
            
            print(f"[CONVERSION] ✓ Armature encontrado: {target_armature.name}")
            
            # Verificar que haya meshes con modificadores armature
            meshes_with_modifiers = self._count_meshes_with_armature_modifiers(target_armature)
            
            if meshes_with_modifiers == 0:
                result['message'] = "No hay meshes con modificadores armature para procesar"
                print("[CONVERSION] ⚠ No hay meshes con modificadores para aplicar pose")
                result['success'] = True  # No es un error crítico
                return result
            
            print(f"[CONVERSION] ✓ {meshes_with_modifiers} meshes con modificadores encontrados")
            
            # Crear aplicador de poses
            applier = external_pose_caller.ExternalPoseApplier()
            
            # Intentar aplicar pose
            pose_success = applier.execute_full_pose_application(
                source_armature=None,  # Ya no existe después de conversión
                target_armature=target_armature
            )
            
            if pose_success:
                result['success'] = True
                result['message'] = "Pose aplicada exitosamente"
                print("[CONVERSION] ✓ Pose personalizada aplicada correctamente")
            else:
                result['message'] = "No se pudo aplicar la pose completamente"
                print("[CONVERSION] ✗ Pose personalizada falló")
            
        except Exception as e:
            result['message'] = f"Error aplicando pose: {str(e)}"
            print(f"[CONVERSION] ✗ Error aplicando pose personalizada: {e}")
            import traceback
            traceback.print_exc()
            # No re-lanzar la excepción para no fallar la conversión
        
        print("[CONVERSION] === APLICACIÓN DE POSE PERSONALIZADA COMPLETADA ===")
        return result
    
    def _find_conversion_result_armature(self, settings):
        """Encuentra el armature resultante de la conversión"""
        # Buscar armature 'Root' o similar (resultado típico de conversión GTA SA)
        root_candidates = []
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                if obj.name.lower() in ['root', 'gta_root', 'gta_sa_root']:
                    root_candidates.append(obj)
        
        if root_candidates:
            # Preferir el que tenga más meshes asociados
            best_candidate = max(root_candidates, 
                               key=lambda x: self._count_meshes_with_armature_modifiers(x))
            print(f"[CONVERSION] ✓ Armature Root encontrado: {best_candidate.name}")
            return best_candidate
        
        # Si no hay Root, buscar el que tenga más meshes asociados
        all_armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
        if all_armatures:
            best_armature = max(all_armatures, 
                              key=lambda x: self._count_meshes_with_armature_modifiers(x))
            
            if self._count_meshes_with_armature_modifiers(best_armature) > 0:
                print(f"[CONVERSION] ✓ Armature principal encontrado: {best_armature.name}")
                return best_armature
        
        # Como última opción, usar target_armature si todavía existe
        if settings.target_armature and settings.target_armature.name in bpy.data.objects:
            print(f"[CONVERSION] ✓ Usando target armature: {settings.target_armature.name}")
            return settings.target_armature
        
        print("[CONVERSION] ✗ No se pudo encontrar armature resultante")
        return None
    
    def _count_meshes_with_armature_modifiers(self, armature):
        """Cuenta meshes que tienen modificador armature apuntando al armature dado"""
        count = 0
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE' and modifier.object == armature:
                        count += 1
                        break
        return count
    
    def validate_conversion_setup(self, settings):
        """
        Valida la configuración antes de ejecutar la conversión
        
        Returns:
            dict: {'valid': bool, 'message': str, 'warnings': list}
        """
        issues = []
        warnings = []
        
        # Validar armatures
        if not settings.source_armature:
            issues.append("No se ha seleccionado el armature fuente")
        elif settings.source_armature.type != 'ARMATURE':
            issues.append("El objeto fuente no es un armature")
        
        if not settings.target_armature:
            issues.append("No se ha seleccionado el armature destino")
        elif settings.target_armature.type != 'ARMATURE':
            issues.append("El objeto destino no es un armature")
        
        # Validar que no sean el mismo armature
        if (settings.source_armature and settings.target_armature and 
            settings.source_armature == settings.target_armature):
            issues.append("El armature fuente y destino no pueden ser el mismo")
        
        # Validar mapeos de huesos
        if len(settings.bone_mappings) == 0:
            issues.append("No hay mapeos de huesos definidos")
        else:
            enabled_mappings = [m for m in settings.bone_mappings if m.enabled]
            if len(enabled_mappings) == 0:
                issues.append("No hay mapeos de huesos habilitados")
            
            # Verificar mapeos válidos
            valid_mappings = 0
            if settings.source_armature and settings.target_armature:
                source_bones = {bone.name for bone in settings.source_armature.pose.bones}
                target_bones = {bone.name for bone in settings.target_armature.pose.bones}
                
                for mapping in enabled_mappings:
                    if not mapping.source_bone or not mapping.target_bone:
                        issues.append(f"Mapeo incompleto encontrado: '{mapping.source_bone}' -> '{mapping.target_bone}'")
                    elif mapping.source_bone not in source_bones:
                        issues.append(f"Hueso fuente '{mapping.source_bone}' no existe en {settings.source_armature.name}")
                    elif mapping.target_bone not in target_bones:
                        issues.append(f"Hueso destino '{mapping.target_bone}' no existe en {settings.target_armature.name}")
                    else:
                        valid_mappings += 1
                
                if valid_mappings == 0:
                    issues.append("No hay mapeos válidos de huesos")
                elif valid_mappings < len(enabled_mappings) // 2:
                    warnings.append(f"Solo {valid_mappings} de {len(enabled_mappings)} mapeos son válidos")
        
        # Validar objetos mesh
        if settings.source_armature:
            mesh_children = [obj for obj in bpy.data.objects 
                           if obj.type == 'MESH' and obj.parent == settings.source_armature]
            if len(mesh_children) == 0:
                warnings.append("El armature fuente no tiene objetos mesh como hijos")
            elif len(mesh_children) > 10:
                warnings.append(f"El armature fuente tiene muchos objetos mesh ({len(mesh_children)}), esto podría ser lento")
        
        # Verificar Shape Keys si está disponible el sistema
        if settings.source_armature:
            shape_keys_info = self._check_shape_keys_status(settings.source_armature)
            if shape_keys_info['has_shape_keys'] and not shape_keys_info['backup_recommended']:
                warnings.append(f"Se detectaron {shape_keys_info['count']} meshes con shape keys. Se recomienda hacer backup.")
        
        # Compilar resultado
        result = {
            'valid': len(issues) == 0,
            'message': "; ".join(issues) if issues else "Configuración válida",
            'warnings': warnings
        }
        
        return result
    
    def _check_shape_keys_status(self, source_armature):
        """Verifica el estado de las shape keys"""
        info = {
            'has_shape_keys': False,
            'count': 0,
            'backup_recommended': False
        }
        
        if not source_armature:
            return info
        
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                obj.parent == source_armature and 
                obj.data.shape_keys and 
                len(obj.data.shape_keys.key_blocks) > 1):
                info['count'] += 1
        
        info['has_shape_keys'] = info['count'] > 0
        
        # Verificar si existen backups
        backup_objects = [obj for obj in bpy.data.objects 
                         if obj.name.endswith("_BACKUP_ShapeKeys")]
        info['backup_recommended'] = info['has_shape_keys'] and len(backup_objects) == 0
        
        return info


class UNIVERSALGTA_OT_preview_conversion(Operator):
    """Vista previa de la conversión sin ejecutarla"""
    bl_idname = "universalgta.preview_conversion"
    bl_label = "Preview Conversion"
    bl_description = "Preview what the conversion will do without executing it"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Validar configuración
        validation_result = UNIVERSALGTA_OT_execute_conversion.validate_conversion_setup(None, settings)
        
        if not validation_result['valid']:
            self.report({'ERROR'}, validation_result['message'])
            return {'CANCELLED'}
        
        # Generar reporte de vista previa
        preview_text = self.generate_preview_report(settings)
        
        # Mostrar en consola
        print("[CONVERSION_PREVIEW]")
        print(preview_text)
        
        # Mostrar resumen en UI
        lines = preview_text.split('\n')
        summary = lines[0] if lines else "Vista previa generada"
        self.report({'INFO'}, summary)
        
        return {'FINISHED'}
    
    def generate_preview_report(self, settings):
        """Genera un reporte detallado de lo que hará la conversión"""
        lines = []
        
        # Header
        lines.append("=== VISTA PREVIA DE CONVERSIÓN ===")
        lines.append("")
        
        # Información de armatures
        lines.append("ARMATURES:")
        lines.append(f"  Fuente: {settings.source_armature.name} ({len(settings.source_armature.data.bones)} huesos)")
        lines.append(f"  Destino: {settings.target_armature.name} ({len(settings.target_armature.data.bones)} huesos)")
        lines.append("")
        
        # Información de mapeos
        enabled_mappings = [m for m in settings.bone_mappings if m.enabled]
        lines.append(f"MAPEOS DE HUESOS: {len(enabled_mappings)} habilitados de {len(settings.bone_mappings)} total")
        
        # Agrupar mapeos por método
        auto_mappings = [m for m in enabled_mappings if m.detection_method == "Auto"]
        manual_mappings = [m for m in enabled_mappings if m.detection_method == "Manual"]
        
        if auto_mappings:
            lines.append(f"  Automáticos: {len(auto_mappings)}")
            avg_confidence = sum(m.confidence for m in auto_mappings) / len(auto_mappings)
            lines.append(f"  Confianza promedio: {avg_confidence:.2f}")
        
        if manual_mappings:
            lines.append(f"  Manuales: {len(manual_mappings)}")
        
        lines.append("")
        
        # Información de objetos mesh
        mesh_children = [obj for obj in bpy.data.objects 
                        if obj.type == 'MESH' and obj.parent == settings.source_armature]
        lines.append(f"OBJETOS MESH A PROCESAR: {len(mesh_children)}")
        for mesh in mesh_children:
            vertex_count = len(mesh.data.vertices)
            modifier_count = len([m for m in mesh.modifiers if m.type == 'ARMATURE'])
            shape_keys_count = len(mesh.data.shape_keys.key_blocks) if mesh.data.shape_keys else 0
            
            mesh_info = f"  {mesh.name}: {vertex_count} vértices, {modifier_count} modificadores armature"
            if shape_keys_count > 1:
                mesh_info += f", {shape_keys_count} shape keys"
            lines.append(mesh_info)
        
        lines.append("")
        
        # Configuraciones especiales
        lines.append("CONFIGURACIONES:")
        lines.append(f"  Auto aplicar pose personalizada: {'Sí' if settings.auto_apply_custom_pose else 'No'}")
        lines.append(f"  Mantener vertex colors: {'Sí' if settings.keep_vertex_colors else 'No'}")
        lines.append(f"  Auto fix normales: {'Sí' if settings.auto_fix_normals else 'No'}")
        lines.append(f"  Modo debug: {'Sí' if settings.debug_mode else 'No'}")
        lines.append(f"  Espaciado brazos: {settings.arm_spacing}")
        lines.append(f"  Espaciado piernas: {settings.leg_spacing}")
        
        lines.append("")
        
        # Proceso que se ejecutará
        lines.append("PROCESO DE CONVERSIÓN:")
        lines.append("1. Detectar y procesar Shape Keys (si existen)")
        lines.append("2. Aplicar transformaciones a objetos fuente")
        lines.append("3. Configurar constraints de posición entre huesos")
        lines.append("4. Aplicar pose al armature destino")
        lines.append("5. Fusionar vertex groups según mapeos")
        lines.append("6. Unificar objetos mesh preservando Shape Keys")
        lines.append("7. Aplicar modificador armature al resultado")
        lines.append("8. Limpiar armatures y datos no utilizados")
        lines.append("9. Aplicar espaciado de huesos")
        if settings.auto_apply_custom_pose:
            lines.append("10. Aplicar pose personalizada (puede fallar sin afectar conversión)")
        
        return "\n".join(lines)


class UNIVERSALGTA_OT_test_bone_mappings(Operator):
    """Probar mapeos de huesos sin hacer conversión completa"""
    bl_idname = "universalgta.test_bone_mappings"
    bl_label = "Test Bone Mappings"
    bl_description = "Test bone mappings by creating temporary constraints"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature or not settings.target_armature:
            self.report({'ERROR'}, "Necesitas definir tanto el armature fuente como el destino")
            return {'CANCELLED'}
        
        # Obtener mapeos habilitados
        enabled_mappings = [
            (m.source_bone, m.target_bone)
            for m in settings.bone_mappings
            if m.enabled and m.source_bone and m.target_bone
        ]
        
        if not enabled_mappings:
            self.report({'ERROR'}, "No hay mapeos válidos para probar")
            return {'CANCELLED'}
        
        try:
            # Crear constraints temporales para visualizar mapeos
            bpy.context.view_layer.objects.active = settings.target_armature
            bpy.ops.object.mode_set(mode='POSE')
            
            created_constraints = []
            
            for source_bone, target_bone in enabled_mappings:
                if (source_bone in settings.source_armature.pose.bones and 
                    target_bone in settings.target_armature.pose.bones):
                    
                    target_pose_bone = settings.target_armature.pose.bones[target_bone]
                    
                    # Crear constraint temporal
                    constraint = target_pose_bone.constraints.new('COPY_LOCATION')
                    constraint.name = "TEMP_TEST_MAPPING"
                    constraint.target = settings.source_armature
                    constraint.subtarget = source_bone
                    constraint.influence = 0.5  # Influencia parcial para testing
                    
                    created_constraints.append((target_pose_bone, constraint))
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Informar resultado
            self.report({'INFO'}, f"Creados {len(created_constraints)} constraints de prueba. Usa 'Clear Test' para eliminar.")
            
            # Guardar referencia para limpiar después
            context.scene['temp_test_constraints'] = len(created_constraints)
            
        except Exception as e:
            self.report({'ERROR'}, f"Error durante la prueba: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_clear_test_constraints(Operator):
    """Limpiar constraints de prueba"""
    bl_idname = "universalgta.clear_test_constraints"
    bl_label = "Clear Test"
    bl_description = "Clear temporary test constraints"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'WARNING'}, "No hay armature destino definido")
            return {'CANCELLED'}
        
        try:
            bpy.context.view_layer.objects.active = settings.target_armature
            bpy.ops.object.mode_set(mode='POSE')
            
            removed_count = 0
            
            # Buscar y eliminar constraints temporales
            for bone in settings.target_armature.pose.bones:
                constraints_to_remove = [c for c in bone.constraints if c.name == "TEMP_TEST_MAPPING"]
                for constraint in constraints_to_remove:
                    bone.constraints.remove(constraint)
                    removed_count += 1
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Limpiar referencia
            if 'temp_test_constraints' in context.scene:
                del context.scene['temp_test_constraints']
            
            self.report({'INFO'}, f"Eliminados {removed_count} constraints de prueba.")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error limpiando constraints: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_auto_detect_bones(Operator):
    """Detectar automáticamente huesos basado en patrones de nombres"""
    bl_idname = "universalgta.auto_detect_bones"
    bl_label = "Auto Detect Bones"
    bl_description = "Automatically detect and map bones based on naming patterns"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature or not settings.target_armature:
            self.report({'ERROR'}, "Se requieren ambos armatures (fuente y destino)")
            return {'CANCELLED'}
        
        src_bones = [bone.name for bone in settings.source_armature.pose.bones]
        tgt_bones = [bone.name for bone in settings.target_armature.pose.bones]
        
        # Patrones de mapeo comunes
        bone_patterns = {
            # Columna vertebral
            'Spine': ['spine', 'back', 'torso'],
            'Spine1': ['spine1', 'chest', 'upper_torso'],
            'Spine2': ['spine2', 'upper_chest'],
            'Neck': ['neck', 'cervical'],
            'Head': ['head', 'skull'],
            
            # Brazos izquierdos
            'L Clavicle': ['l_clavicle', 'left_clavicle', 'l_shoulder', 'left_shoulder'],
            'L UpperArm': ['l_upperarm', 'left_upperarm', 'l_arm', 'left_arm', 'l_humerus'],
            'L Forearm': ['l_forearm', 'left_forearm', 'l_lower_arm', 'left_lower_arm'],
            'L Hand': ['l_hand', 'left_hand'],
            
            # Brazos derechos
            'R Clavicle': ['r_clavicle', 'right_clavicle', 'r_shoulder', 'right_shoulder'],
            'R UpperArm': ['r_upperarm', 'right_upperarm', 'r_arm', 'right_arm', 'r_humerus'],
            'R Forearm': ['r_forearm', 'right_forearm', 'r_lower_arm', 'right_lower_arm'],
            'R Hand': ['r_hand', 'right_hand'],
            
            # Piernas izquierdas
            'L Thigh': ['l_thigh', 'left_thigh', 'l_leg', 'left_leg', 'l_femur'],
            'L Calf': ['l_calf', 'left_calf', 'l_shin', 'left_shin', 'l_lower_leg'],
            'L Foot': ['l_foot', 'left_foot'],
            
            # Piernas derechas
            'R Thigh': ['r_thigh', 'right_thigh', 'r_leg', 'right_leg', 'r_femur'],
            'R Calf': ['r_calf', 'right_calf', 'r_shin', 'right_shin', 'r_lower_leg'],
            'R Foot': ['r_foot', 'right_foot'],
            
            # Otros
            'Pelvis': ['pelvis', 'hip', 'root'],
            'Root': ['root', 'base', 'origin'],
        }
        
        # Limpiar mapeos existentes
        # No se puede usar .clear() en una CollectionProperty, se debe iterar
        while len(settings.bone_mappings) > 0:
            settings.bone_mappings.remove(0)
        
        detected_count = 0
        
        # Buscar coincidencias
        for target_bone in tgt_bones:
            best_match = None
            best_confidence = 0.0
            
            for src_bone in src_bones:
                confidence = self._calculate_bone_similarity(src_bone, target_bone, bone_patterns)
                
                if confidence > best_confidence and confidence >= settings.detection_threshold:
                    best_match = src_bone
                    best_confidence = confidence
            
            # Agregar mapeo
            item = settings.bone_mappings.add()
            item.target_bone = target_bone
            item.source_bone = best_match if best_match else ""
            item.enabled = bool(best_match)
            item.detection_method = "Auto" if best_match else "Manual"
            item.confidence = best_confidence
            
            if best_match:
                detected_count += 1
                print(f"[DEBUG] Detectado: {best_match} -> {target_bone} (confianza: {best_confidence:.2f})")
        
        settings.bone_mappings_index = 0
        self.report({'INFO'}, f"Detección automática completada. {detected_count} huesos mapeados.")
        return {'FINISHED'}
    
    def _calculate_bone_similarity(self, src_bone, tgt_bone, patterns):
        """Calcula la similitud entre dos nombres de huesos"""
        src_lower = src_bone.lower()
        tgt_lower = tgt_bone.lower()
        
        # Coincidencia exacta
        if src_lower == tgt_lower:
            return 1.0
        
        # Buscar en patrones
        if tgt_bone in patterns:
            for pattern in patterns[tgt_bone]:
                if pattern in src_lower:
                    return 0.8
        
        # Similitud por subcadenas
        if tgt_lower in src_lower or src_lower in tgt_lower:
            return 0.6
        
        # Similitud por palabras clave
        keywords = ['left', 'right', 'l_', 'r_', 'arm', 'leg', 'hand', 'foot', 'head', 'spine']
        common_keywords = 0
        total_keywords = 0
        
        for keyword in keywords:
            if keyword in src_lower:
                total_keywords += 1
                if keyword in tgt_lower:
                    common_keywords += 1
            if keyword in tgt_lower:
                total_keywords += 1
        
        if total_keywords > 0:
            return (common_keywords / total_keywords) * 0.4
        
        return 0.0


class UNIVERSALGTA_OT_validate_conversion(Operator):
    """Validar la configuración actual antes de la conversión"""
    bl_idname = "universalgta.validate_conversion"
    bl_label = "Validate Conversion"
    bl_description = "Validate the current setup before conversion"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        issues = []
        
        # Validar armatures
        if not settings.source_armature:
            issues.append("No se ha seleccionado el armature fuente")
        elif settings.source_armature.type != 'ARMATURE':
            issues.append("El objeto fuente no es un armature")
        
        if not settings.target_armature:
            issues.append("No se ha seleccionado el armature destino")
        elif settings.target_armature.type != 'ARMATURE':
            issues.append("El objeto destino no es un armature")
        
        # Validar mapeos
        if len(settings.bone_mappings) == 0:
            issues.append("No hay mapeos de huesos definidos")
        else:
            enabled_mappings = [m for m in settings.bone_mappings if m.enabled]
            if len(enabled_mappings) == 0:
                issues.append("No hay mapeos de huesos habilitados")
            
            # Verificar mapeos válidos
            invalid_mappings = []
            for i, mapping in enumerate(settings.bone_mappings):
                if mapping.enabled:
                    if not mapping.source_bone or not mapping.target_bone:
                        invalid_mappings.append(f"Mapeo {i+1}: hueso fuente o destino vacío")
                    elif (settings.source_armature and 
                          mapping.source_bone not in [b.name for b in settings.source_armature.pose.bones]):
                        invalid_mappings.append(f"Mapeo {i+1}: hueso fuente '{mapping.source_bone}' no existe")
                    elif (settings.target_armature and 
                          mapping.target_bone not in [b.name for b in settings.target_armature.pose.bones]):
                        invalid_mappings.append(f"Mapeo {i+1}: hueso destino '{mapping.target_bone}' no existe")
            
            issues.extend(invalid_mappings)
        
        # Validar objetos mesh
        if settings.source_armature:
            mesh_children = [obj for obj in bpy.data.objects 
                           if obj.type == 'MESH' and obj.parent == settings.source_armature]
            if len(mesh_children) == 0:
                issues.append("El armature fuente no tiene objetos mesh como hijos")
        
        # Mostrar resultados
        if issues:
            issue_text = "\n".join([f"• {issue}" for issue in issues])
            self.report({'ERROR'}, f"Validación falló:\n{issue_text}")
            print(f"[DEBUG] Problemas de validación:\n{issue_text}")
        else:
            self.report({'INFO'}, "Validación exitosa. La conversión puede proceder.")
            print("[DEBUG] Validación exitosa")
        
        return {'FINISHED'}


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_execute_conversion,
    UNIVERSALGTA_OT_preview_conversion,
    UNIVERSALGTA_OT_test_bone_mappings,
    UNIVERSALGTA_OT_clear_test_constraints,
    UNIVERSALGTA_OT_auto_detect_bones,
    UNIVERSALGTA_OT_validate_conversion,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)