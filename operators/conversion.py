"""
Operadores de conversión para Universal GTA SA Converter
VERSIÓN CORREGIDA - Arregla errores de importación y sintaxis
"""

import bpy
from bpy.types import Operator


class UNIVERSALGTA_OT_execute_conversion(Operator):
    """Ejecutar conversión a GTA SA"""
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
        
        try:
            print("[CONVERSION] Iniciando conversión a GTA SA...")
            
            # Crear y ejecutar el conversor con el procedimiento detallado
            converter = DetailedGTAConverter(settings)
            success = converter.execute_detailed_conversion()
            
            if success:
                self.report({'INFO'}, "Conversión completada con éxito")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Falló la conversión")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error durante la conversión: {str(e)}")
            print(f"[CONVERSION] Error en conversión: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
    
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
        
        # Compilar resultado
        result = {
            'valid': len(issues) == 0,
            'message': "; ".join(issues) if issues else "Configuración válida",
            'warnings': warnings
        }
        
        return result


class UNIVERSALGTA_OT_preview_conversion(Operator):
    """Vista previa de la conversión sin ejecutarla"""
    bl_idname = "universalgta.preview_conversion"
    bl_label = "Preview Conversion"
    bl_description = "Preview what the conversion will do without executing it"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Validar configuración
        converter_op = UNIVERSALGTA_OT_execute_conversion()
        validation_result = converter_op.validate_conversion_setup(settings)
        
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
        lines.append("=== VISTA PREVIA DE CONVERSIÓN DETALLADA ===")
        lines.append("")
        
        # Información de armatures
        lines.append("ARMATURES:")
        lines.append(f"  Fuente: {settings.source_armature.name} ({len(settings.source_armature.data.bones)} huesos)")
        lines.append(f"  Destino: {settings.target_armature.name} ({len(settings.target_armature.data.bones)} huesos)")
        lines.append("")
        
        # Información de mapeos
        enabled_mappings = [m for m in settings.bone_mappings if m.enabled]
        lines.append(f"MAPEOS DE HUESOS: {len(enabled_mappings)} habilitados de {len(settings.bone_mappings)} total")
        
        # Información de objetos mesh
        mesh_children = [obj for obj in bpy.data.objects 
                        if obj.type == 'MESH' and obj.parent == settings.source_armature]
        lines.append(f"OBJETOS MESH A PROCESAR: {len(mesh_children)}")
        for mesh in mesh_children:
            vertex_count = len(mesh.data.vertices)
            modifier_count = len([m for m in mesh.modifiers if m.type == 'ARMATURE'])
            shape_keys_count = len(mesh.data.shape_keys.key_blocks) if mesh.data.shape_keys else 0
            lines.append(f"  {mesh.name}: {vertex_count} vértices, {modifier_count} modificadores, {shape_keys_count} shape keys")
        
        lines.append("")
        
        # Proceso detallado que se ejecutará
        lines.append("PROCESO DE CONVERSIÓN DETALLADO:")
        lines.append("FASE 1: Preparación del Armature Source")
        lines.append("  1. Aplicar transformaciones al Source armature")
        lines.append("  2. Aplicar transformaciones a objetos hijos")
        
        lines.append("FASE 2: Limpieza de materiales y mallas")
        lines.append("  3. Modificar materiales (metallic=0, specular=0)")
        lines.append("  4. Unir todas las mallas en una sola")
        lines.append("  5. Limpiar nombres de texturas (.001, .002)")
        lines.append("  6. Fusionar materiales duplicados")
        
        lines.append("FASE 3: Shape Keys")
        lines.append("  7. Aplicar todas las Shape Keys")
        lines.append("  8. Eliminar shape keys restantes")
        
        lines.append("FASE 4: Modificadores y Armature")
        lines.append("  9. Aplicar modificador Armature del Source")
        lines.append("  10. Aplicar pose actual del Source")
        lines.append("  11. Eliminar Armature Source")
        
        lines.append("FASE 5: Reasignación al Target")
        lines.append("  12. Configurar Copy Location en Target")
        lines.append("  13. Aplicar pose copiada")
        lines.append("  14. Eliminar restricciones")
        
        lines.append("FASE 6: Limpieza final")
        lines.append("  15. Eliminar mallas no deseadas")
        lines.append("  16. Limpiar objetos intermedios")
        
        lines.append("FASE 7: Reconexión")
        lines.append("  17. Establecer Target como padre")
        lines.append("  18. Agregar modificador GTA_SKIN")
        
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
        # Usar el operador de mapeo existente
        bpy.ops.universalgta.auto_detect_mappings()
        return {'FINISHED'}


class UNIVERSALGTA_OT_validate_conversion(Operator):
    """Validar la configuración actual antes de la conversión"""
    bl_idname = "universalgta.validate_conversion"
    bl_label = "Validate Conversion"
    bl_description = "Validate the current setup before conversion"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Usar el método de validación del operador principal
        converter_op = UNIVERSALGTA_OT_execute_conversion()
        validation_result = converter_op.validate_conversion_setup(settings)
        
        # Mostrar resultados
        if validation_result['valid']:
            self.report({'INFO'}, "Validación exitosa. La conversión puede proceder.")
            print("[DEBUG] Validación exitosa")
        else:
            self.report({'ERROR'}, f"Validación falló: {validation_result['message']}")
            print(f"[DEBUG] Problemas de validación: {validation_result['message']}")
        
        return {'FINISHED'}


class DetailedGTAConverter:
    """Conversor detallado siguiendo el procedimiento paso a paso especificado"""
    
    def __init__(self, settings):
        self.settings = settings
        self.source_armature = settings.source_armature
        self.target_armature = settings.target_armature
        
    def execute_detailed_conversion(self):
        """Ejecuta la conversión completa siguiendo todos los pasos detallados"""
        try:
            print("[DETAILED_CONVERSION] Iniciando conversión detallada...")
            
            # FASE 1: Preparación del Armature Source
            if not self._phase1_prepare_source():
                return False
            
            # FASE 2: Limpieza de materiales y mallas
            if not self._phase2_cleanup_materials_meshes():
                return False
            
            # FASE 3: Shape Keys
            if not self._phase3_process_shape_keys():
                return False
            
            # FASE 4: Modificadores y Armature
            if not self._phase4_modifiers_armature():
                return False
            
            # FASE 5: Reasignación al Target
            if not self._phase5_reassign_to_target():
                return False
            
            # FASE 6: Limpieza final
            if not self._phase6_final_cleanup():
                return False
            
            # FASE 7: Reconexión
            if not self._phase7_reconnection():
                return False
            
            print("[DETAILED_CONVERSION] ✅ Conversión detallada completada con éxito")
            return True
            
        except Exception as e:
            print(f"[DETAILED_CONVERSION] ❌ Error durante la conversión: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _phase1_prepare_source(self):
        """FASE 1: Preparación del Armature Source"""
        print("[PHASE1] Preparando Armature Source...")
        
        try:
            # 1. Identificar el objeto Source
            if not self.source_armature or self.source_armature.type != 'ARMATURE':
                print("[PHASE1] Error: Source no es un armature válido")
                return False
            
            # 2. Aplicar transformaciones al Source
            bpy.context.view_layer.objects.active = self.source_armature
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Aplicar transformaciones del armature
            if any([self.source_armature.location, self.source_armature.rotation_euler, 
                   [s for s in self.source_armature.scale if s != 1.0]]):
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                print("[PHASE1] ✓ Transformaciones aplicadas al Source armature")
            
            # 3. Aplicar transformaciones a objetos hijos
            child_objects = [obj for obj in bpy.data.objects if obj.parent == self.source_armature]
            
            for child in child_objects:
                bpy.context.view_layer.objects.active = child
                if any([child.location, child.rotation_euler, [s for s in child.scale if s != 1.0]]):
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    print(f"[PHASE1] ✓ Transformaciones aplicadas a {child.name}")
            
            print("[PHASE1] ✅ Fase 1 completada")
            return True
            
        except Exception as e:
            print(f"[PHASE1] ❌ Error en Fase 1: {e}")
            return False
    
    def _phase2_cleanup_materials_meshes(self):
        """FASE 2: Limpieza de materiales y mallas"""
        print("[PHASE2] Limpiando materiales y mallas...")
        
        try:
            # 3. Modificar materiales
            self._fix_materials()
            
            # 4. Unir todas las mallas en una sola
            unified_mesh = self._join_all_meshes()
            if not unified_mesh:
                print("[PHASE2] Error: No se pudo unificar las mallas")
                return False
            
            # 5. Eliminar sufijos en nombres de texturas
            self._clean_texture_names()
            
            # 6. Fusionar materiales duplicados
            self._merge_duplicate_materials()
            
            print("[PHASE2] ✅ Fase 2 completada")
            return True
            
        except Exception as e:
            print(f"[PHASE2] ❌ Error en Fase 2: {e}")
            return False
    
    def _phase3_process_shape_keys(self):
        """FASE 3: Shape Keys"""
        print("[PHASE3] Procesando Shape Keys...")
        
        try:
            # Buscar el mesh unificado
            unified_mesh = self._find_unified_mesh()
            if not unified_mesh:
                print("[PHASE3] No se encontró mesh unificado")
                return True  # No es error crítico
            
            # 7. Aplicar todas las Shape Keys
            if unified_mesh.data.shape_keys:
                self._apply_all_shape_keys(unified_mesh)
            
            # 8. Eliminar todas las shape keys restantes
            self._remove_all_shape_keys(unified_mesh)
            
            print("[PHASE3] ✅ Fase 3 completada")
            return True
            
        except Exception as e:
            print(f"[PHASE3] ❌ Error en Fase 3: {e}")
            return False
    
    def _phase4_modifiers_armature(self):
        """FASE 4: Modificadores y Armature"""
        print("[PHASE4] Procesando modificadores y armature...")
        
        try:
            unified_mesh = self._find_unified_mesh()
            if not unified_mesh:
                print("[PHASE4] Error: No se encontró mesh unificado")
                return False
            
            # 9. Aplicar el modificador Armature que usa Source
            self._apply_source_armature_modifier(unified_mesh)
            
            # 10. Aplicar la pose actual del Armature Source
            self._apply_source_pose()
            
            # 11. Borrar el Armature Source (se hará en fase 6)
            print("[PHASE4] Source armature marcado para eliminación")
            
            print("[PHASE4] ✅ Fase 4 completada")
            return True
            
        except Exception as e:
            print(f"[PHASE4] ❌ Error en Fase 4: {e}")
            return False
    
    def _phase5_reassign_to_target(self):
        """FASE 5: Reasignación al Target"""
        print("[PHASE5] Reasignando al Target armature...")
        
        try:
            # 12. Entrar en modo Pose del Target
            bpy.context.view_layer.objects.active = self.target_armature
            bpy.ops.object.mode_set(mode='POSE')
            
            # 13. Agregar restricciones Copy Location
            self._add_copy_location_constraints()
            
            # 14. Aplicar la pose copiada
            self._apply_copied_pose()
            
            # 15. Eliminar todas las restricciones
            self._remove_all_constraints()
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            print("[PHASE5] ✅ Fase 5 completada")
            return True
            
        except Exception as e:
            print(f"[PHASE5] ❌ Error en Fase 5: {e}")
            return False
    
    def _phase6_final_cleanup(self):
        """FASE 6: Limpieza final"""
        print("[PHASE6] Limpieza final...")
        
        try:
            # 16. Eliminar la malla asociada a Target
            self._remove_target_mesh()
            
            # 17. Eliminar el Armature Source completamente
            self._remove_source_armature()
            
            print("[PHASE6] ✅ Fase 6 completada")
            return True
            
        except Exception as e:
            print(f"[PHASE6] ❌ Error en Fase 6: {e}")
            return False
    
    def _phase7_reconnection(self):
        """FASE 7: Reconexión final"""
        print("[PHASE7] Reconexión final...")
        
        try:
            unified_mesh = self._find_unified_mesh()
            if not unified_mesh:
                print("[PHASE7] Error: No se encontró mesh final")
                return False
            
            # 18. Establecer Target como padre
            unified_mesh.parent = self.target_armature
            unified_mesh.parent_type = 'ARMATURE'
            
            # 19. Confirmar que no tenga modificadores activos
            for mod in list(unified_mesh.modifiers):
                unified_mesh.modifiers.remove(mod)
            
            # 20. Agregar nuevo modificador GTA_SKIN
            gta_modifier = unified_mesh.modifiers.new(name="GTA_SKIN", type='ARMATURE')
            gta_modifier.object = self.target_armature
            
            print("[PHASE7] ✅ Fase 7 completada")
            return True
            
        except Exception as e:
            print(f"[PHASE7] ❌ Error en Fase 7: {e}")
            return False
    
    # Métodos auxiliares para cada fase
    
    def _fix_materials(self):
        """Modifica materiales: metallic=0, specular=0"""
        print("[MATERIALS] Corrigiendo materiales...")
        
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        # Establecer metallic y specular a 0
                        if 'Metallic' in node.inputs:
                            node.inputs['Metallic'].default_value = 0.0
                        if 'Specular' in node.inputs:
                            node.inputs['Specular'].default_value = 0.0
                        print(f"[MATERIALS] ✓ Material corregido: {material.name}")
    
    def _join_all_meshes(self):
        """Une todas las mallas hijas del Source en una sola"""
        print("[MESHES] Uniendo todas las mallas...")
        
        mesh_objects = [obj for obj in bpy.data.objects 
                       if obj.type == 'MESH' and obj.parent == self.source_armature]
        
        if not mesh_objects:
            print("[MESHES] No se encontraron mallas para unir")
            return None
        
        if len(mesh_objects) == 1:
            print(f"[MESHES] Solo hay una malla: {mesh_objects[0].name}")
            return mesh_objects[0]
        
        # Seleccionar todas las mallas
        bpy.ops.object.select_all(action='DESELECT')
        for mesh in mesh_objects:
            mesh.select_set(True)
        
        # Activar la primera como principal
        bpy.context.view_layer.objects.active = mesh_objects[0]
        
        # Unir
        bpy.ops.object.join()
        
        unified_mesh = bpy.context.active_object
        unified_mesh.name = f"{self.settings.skin_name or 'GTA_Skin'}_Unified"
        
        print(f"[MESHES] ✓ Mallas unidas en: {unified_mesh.name}")
        return unified_mesh
    
    def _clean_texture_names(self):
        """Elimina sufijos .001, .002 de nombres de texturas"""
        print("[TEXTURES] Limpiando nombres de texturas...")
        
        import re
        
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        original_name = node.image.name
                        # Eliminar sufijos .001, .002, etc.
                        clean_name = re.sub(r'\.\d+$', '', original_name)
                        if clean_name != original_name:
                            node.image.name = clean_name
                            print(f"[TEXTURES] ✓ Renombrado: {original_name} -> {clean_name}")
    
    def _merge_duplicate_materials(self):
        """Fusiona materiales que usan la misma textura"""
        print("[MATERIALS] Fusionando materiales duplicados...")
        
        # Agrupar materiales por textura principal
        texture_groups = {}
        
        for material in bpy.data.materials:
            main_texture = self._get_main_texture(material)
            if main_texture:
                if main_texture not in texture_groups:
                    texture_groups[main_texture] = []
                texture_groups[main_texture].append(material)
        
        # Fusionar grupos con múltiples materiales
        for texture, materials in texture_groups.items():
            if len(materials) > 1:
                # Mantener el primero, reasignar los demás
                primary_material = materials[0]
                for duplicate_material in materials[1:]:
                    self._reassign_material_slots(duplicate_material, primary_material)
                    print(f"[MATERIALS] ✓ Fusionado: {duplicate_material.name} -> {primary_material.name}")
    
    def _get_main_texture(self, material):
        """Obtiene la textura principal de un material"""
        if not material.use_nodes:
            return None
        
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                return node.image.name
        return None
    
    def _reassign_material_slots(self, old_material, new_material):
        """Reasigna slots de material"""
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material == old_material:
                        slot.material = new_material
    
    def _find_unified_mesh(self):
        """Encuentra el mesh unificado"""
        mesh_objects = [obj for obj in bpy.data.objects 
                       if obj.type == 'MESH' and obj.parent == self.source_armature]
        
        if mesh_objects:
            return mesh_objects[0]  # Debería ser solo uno después de la unión
        
        # Buscar por nombre
        skin_name = self.settings.skin_name or 'GTA_Skin'
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and skin_name in obj.name:
                return obj
        
        return None
    
    def _apply_all_shape_keys(self, mesh_obj):
        """Aplica todas las shape keys del mesh"""
        print("[SHAPE_KEYS] Aplicando shape keys...")
        
        if not mesh_obj.data.shape_keys:
            return
        
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Aplicar shape keys de la última a la primera
        key_blocks = mesh_obj.data.shape_keys.key_blocks
        for i in range(len(key_blocks) - 1, -1, -1):
            if i < len(mesh_obj.data.shape_keys.key_blocks):
                key_block = mesh_obj.data.shape_keys.key_blocks[i]
                if key_block.name != 'Basis':
                    mesh_obj.active_shape_key_index = i
                    # Establecer valor a 1.0 y aplicar
                    key_block.value = 1.0
                    bpy.ops.object.shape_key_remove(all=False)
                    print(f"[SHAPE_KEYS] ✓ Aplicada: {key_block.name}")
    
    def _remove_all_shape_keys(self, mesh_obj):
        """Elimina todas las shape keys restantes"""
        if mesh_obj.data.shape_keys:
            # Eliminar todas incluyendo Basis
            while mesh_obj.data.shape_keys.key_blocks:
                mesh_obj.active_shape_key_index = 0
                bpy.ops.object.shape_key_remove(all=False)
            print("[SHAPE_KEYS] ✓ Todas las shape keys eliminadas")
    
    def _apply_source_armature_modifier(self, mesh_obj):
        """Aplica el modificador armature del Source"""
        print("[MODIFIERS] Aplicando modificador armature del Source...")
        
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='OBJECT')
        
        for modifier in list(mesh_obj.modifiers):
            if modifier.type == 'ARMATURE' and modifier.object == self.source_armature:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
                print(f"[MODIFIERS] ✓ Aplicado modificador: {modifier.name}")
    
    def _apply_source_pose(self):
        """Aplica la pose actual del Source"""
        print("[POSE] Aplicando pose del Source...")
        
        # Hornear la pose en los vértices - esto ya se hizo al aplicar el modificador
        print("[POSE] ✓ Pose del Source aplicada")
    
    def _add_copy_location_constraints(self):
        """Agrega restricciones Copy Location según bone mappings"""
        print("[CONSTRAINTS] Agregando Copy Location constraints...")
        
        enabled_mappings = [m for m in self.settings.bone_mappings if m.enabled]
        
        for mapping in enabled_mappings:
            if (mapping.target_bone in self.target_armature.pose.bones and 
                mapping.source_bone in self.source_armature.pose.bones):
                
                target_bone = self.target_armature.pose.bones[mapping.target_bone]
                
                constraint = target_bone.constraints.new('COPY_LOCATION')
                constraint.target = self.source_armature
                constraint.subtarget = mapping.source_bone
                constraint.name = "GTA_COPY_LOCATION"
                
                print(f"[CONSTRAINTS] ✓ Constraint: {mapping.target_bone} <- {mapping.source_bone}")
    
    def _apply_copied_pose(self):
        """Aplica la pose copiada"""
        print("[POSE] Aplicando pose copiada...")
        
        # Actualizar vista para aplicar constraints
        bpy.context.view_layer.update()
        
        # Hornear la pose
        bpy.ops.pose.visual_transform_apply()
        
        print("[POSE] ✓ Pose copiada aplicada")
    
    def _remove_all_constraints(self):
        """Elimina todas las restricciones de los huesos del Target"""
        print("[CONSTRAINTS] Eliminando restricciones...")
        
        for bone in self.target_armature.pose.bones:
            for constraint in list(bone.constraints):
                bone.constraints.remove(constraint)
        
        print("[CONSTRAINTS] ✓ Todas las restricciones eliminadas")
    
    def _remove_target_mesh(self):
        """Elimina la malla asociada al Target (unnamed, etc.)"""
        print("[CLEANUP] Eliminando mallas no deseadas del Target...")
        
        # Buscar mallas con nombres como "unnamed", "unnamed.001", etc.
        meshes_to_remove = []
        
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                obj.parent == self.target_armature and
                ('unnamed' in obj.name.lower() or obj.name.startswith('Cube'))):
                meshes_to_remove.append(obj)
        
        for mesh in meshes_to_remove:
            print(f"[CLEANUP] ✓ Eliminando mesh no deseado: {mesh.name}")
            bpy.data.objects.remove(mesh, do_unlink=True)
    
    def _remove_source_armature(self):
        """Elimina completamente el Armature Source"""
        print("[CLEANUP] Eliminando Source armature...")
        
        if self.source_armature and self.source_armature.name in bpy.data.objects:
            bpy.data.objects.remove(self.source_armature, do_unlink=True)
            print(f"[CLEANUP] ✓ Source armature eliminado: {self.source_armature.name}")


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