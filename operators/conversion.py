"""
Operadores de conversión para Universal GTA SA Converter
VERSIÓN CORREGIDA - Arregla errores de importación y referencias
"""

import bpy
from bpy.types import Operator
from ..converter import UniversalGTAConverter  # CORRECCIÓN: Importar el conversor correcto


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
            
            # CORRECCIÓN: Usar UniversalGTAConverter en lugar de DetailedGTAConverter
            converter = UniversalGTAConverter(settings)
            success = converter.convert()  # CORRECCIÓN: Usar método convert() en lugar de execute_detailed_conversion()
            
            if success:
                # Aplicar pose personalizada automáticamente si está habilitado
                if settings.auto_apply_custom_pose:
                    try:
                        from .. import external_pose_caller
                        applier = external_pose_caller.ExternalPoseApplier()
                        applier.execute_full_pose_application(
                            source_armature=None,  # Ya no existe después de conversión
                            target_armature=settings.target_armature
                        )
                        print("[CONVERSION] Pose personalizada aplicada automáticamente")
                    except Exception as e:
                        print(f"[CONVERSION] Error aplicando pose automática: {e}")
                        # No fallar la conversión por esto
                
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
        
        lines.append("FASE 5: Reasignación al Target")
        lines.append("  11. Configurar Copy Location en Target")
        lines.append("  12. Aplicar pose copiada")
        lines.append("  13. Eliminar restricciones")
        
        lines.append("FASE 6: Limpieza final")
        lines.append("  14. Eliminar mallas no deseadas")
        lines.append("  15. Eliminar Source Armature")
        
        lines.append("FASE 7: Reconexión")
        lines.append("  16. Establecer Target como padre")
        lines.append("  17. Agregar modificador GTA_SKIN")
        
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