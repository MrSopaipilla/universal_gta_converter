"""
Panel principal para el addon Universal GTA Converter
VERSIÓN COMPLETA CORREGIDA PARA BLENDER 5.0 - Iconos y drag & drop funcionales
"""

import bpy
from bpy.types import Panel


class UNIVERSALGTA_PT_MainPanel(Panel):
    """Panel principal del Universal GTA Converter"""
    bl_label = "Universal GTA Converter"
    bl_idname = "UNIVERSALGTA_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # Header con información del addon
        box = layout.box()
        row = box.row()
        row.label(text="Universal to GTA SA Converter", icon='ARMATURE_DATA')
        row = box.row()
        row.label(text="v3.2.2 - YoshiMaincra + AI", icon='INFO')
        
        # Configuración de Armatures
        layout.separator()
        box = layout.box()
        box.label(text="Armature Setup", icon='BONE_DATA')
        
        col = box.column()
        col.prop(settings, "source_armature", text="Source Armature")
        col.prop(settings, "target_armature", text="Target Armature")
        
        # Configuración de detección
        layout.separator()
        box = layout.box()
        box.label(text="Detection Settings", icon='SETTINGS')
        
        col = box.column()
        col.prop(settings, "auto_detect_mode", text="Auto Detection")
        if settings.auto_detect_mode:
            col.prop(settings, "detection_threshold", text="Threshold")
        
        col.prop(settings, "debug_mode", text="Debug Mode")
        
        # Configuración de pose personalizada
        layout.separator()
        box = layout.box()
        box.label(text="Pose Settings", icon='POSE_HLT')
        
        col = box.column()
        col.prop(settings, "auto_apply_custom_pose", text="Auto Apply Custom Pose")
        
        # Botón para aplicar pose manualmente - ICONO CORREGIDO
        row = col.row()
        row.operator("universalgta.apply_custom_pose", text="Apply Custom Pose", icon='ARMATURE_DATA')
        
        # Configuración de espaciado
        layout.separator()
        box = layout.box()
        box.label(text="Spacing Settings", icon='TRANSFORM_ORIGINS')
        
        col = box.column()
        col.prop(settings, "arm_spacing", text="Arm Spacing")
        col.prop(settings, "leg_spacing", text="Leg Spacing")
        
        row = col.row()
        row.operator("universalgta.apply_spacing", text="Apply Spacing", icon='BONE_DATA')
        
        # Configuración adicional
        layout.separator()
        box = layout.box()
        box.label(text="Additional Settings", icon='PREFERENCES')
        
        col = box.column()
        col.prop(settings, "keep_vertex_colors", text="Keep Vertex Colors")


class UNIVERSALGTA_PT_BoneMappingPanel(Panel):
    """Panel para configurar el mapeo de huesos - DRAG & DROP FUNCIONAL"""
    bl_label = "Bone Mapping"
    bl_idname = "UNIVERSALGTA_PT_bone_mapping_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # Controles de mapeo principales
        box = layout.box()
        box.label(text="Mapping Controls", icon='CONSTRAINT_BONE')
        
        # Primera fila de botones
        row = box.row()
        row.operator("universalgta.add_target_bones", text="Add Target Bones", icon='BONE_DATA')
        row.operator("universalgta.auto_detect_mappings", text="Auto Detect", icon='AUTO')
        
        # Segunda fila de botones
        row = box.row()
        row.operator("universalgta.add_custom_entry", text="Add Custom", icon='ADD')
        row.operator("universalgta.validate_mappings", text="Validate", icon='CHECKMARK')
        
        # Tercera fila - controles de archivo
        row = box.row()
        row.operator("universalgta.load_mapping", text="Load", icon='FILE_FOLDER')
        row.operator("universalgta.save_mapping", text="Save", icon='FILE_TICK')
        
        # Cuarta fila - controles de habilitación masiva
        row = box.row()
        row.operator("universalgta.enable_all_mappings", text="Enable All", icon='CHECKMARK')
        row.operator("universalgta.disable_all_mappings", text="Disable All", icon='X')
        
        # Quinta fila - limpiar
        row = box.row()
        row.operator("universalgta.clear_mappings", text="Clear All", icon='TRASH')
        row.operator("universalgta.enable_high_confidence", text="High Confidence", icon='FILTER')
        
        # SECCIÓN PRINCIPAL: Lista de mapeos MEJORADA
        layout.separator()
        box = layout.box()
        
        # Header con información
        header_row = box.row()
        header_row.label(text="Bone Mappings", icon='OUTLINER_DATA_ARMATURE')
        if len(settings.bone_mappings) > 0:
            enabled_count = sum(1 for m in settings.bone_mappings if m.enabled)
            header_row.label(text=f"({enabled_count}/{len(settings.bone_mappings)})")
        
        if len(settings.bone_mappings) > 0:
            # Container principal para la lista
            main_container = box.column()
            
            # Lista con template_list CORREGIDA
            list_row = main_container.row()
            
            # Columna principal para la lista
            list_col = list_row.column()
            list_col.template_list(
                "UNIVERSALGTA_UL_BoneMappingList",     # Lista UI personalizada
                "",                                    # Identificador único
                settings,                              # Datos fuente
                "bone_mappings",                       # Propiedad de colección
                settings,                              # Datos de índice
                "bone_mappings_index",                 # Propiedad de índice
                rows=6,                                # Filas visibles
                maxrows=10,                            # Máximo de filas
                sort_reverse=False,                    # Orden de sort
                sort_lock=False                        # Permitir reordenamiento
            )
            
            # Columna de controles laterales MEJORADA
            controls_col = list_row.column(align=True)
            controls_col.scale_x = 0.6
            controls_col.scale_y = 1.2
            
            # Botones de movimiento con mejor espaciado
            op_up = controls_col.operator("universalgta.move_mapping_up", text="", icon='TRIA_UP')
            op_down = controls_col.operator("universalgta.move_mapping_down", text="", icon='TRIA_DOWN')
            
            controls_col.separator()
            
            # Botón de eliminar
            op_remove = controls_col.operator("universalgta.remove_mapping_entry", text="", icon='REMOVE')
            
            controls_col.separator()
            
            # Botones adicionales
            op_duplicate = controls_col.operator("universalgta.add_custom_entry", text="", icon='DUPLICATE')
            
            # SECCIÓN DE EDICIÓN INDIVIDUAL del mapeo seleccionado
            if 0 <= settings.bone_mappings_index < len(settings.bone_mappings):
                layout.separator()
                item = settings.bone_mappings[settings.bone_mappings_index]
                
                edit_box = layout.box()
                edit_box.label(text=f"Edit Mapping #{settings.bone_mappings_index + 1}", icon='TOOL_SETTINGS')
                
                # Fila de habilitación
                enable_row = edit_box.row()
                enable_row.prop(item, "enabled", text="Enabled")
                enable_row.label(text=f"Method: {item.detection_method}")
                if item.confidence > 0:
                    confidence_text = f"Confidence: {item.confidence:.2f}"
                    enable_row.label(text=confidence_text)
                
                # Edición de huesos con búsqueda inteligente
                bones_col = edit_box.column()
                
                # Source bone con prop_search
                src_row = bones_col.row(align=True)
                src_row.label(text="Source:", icon='BONE_DATA')
                if settings.source_armature and settings.source_armature.type == 'ARMATURE':
                    src_row.prop_search(item, "source_bone", settings.source_armature.pose, "bones", text="")
                else:
                    src_row.prop(item, "source_bone", text="")
                
                # Target bone con prop_search
                tgt_row = bones_col.row(align=True)
                tgt_row.label(text="Target:", icon='BONE_DATA')
                if settings.target_armature and settings.target_armature.type == 'ARMATURE':
                    tgt_row.prop_search(item, "target_bone", settings.target_armature.pose, "bones", text="")
                else:
                    tgt_row.prop(item, "target_bone", text="")
                
                # Controles adicionales
                controls_row = edit_box.row()
                controls_row.operator("universalgta.invert_mapping", text="Swap", icon='ARROW_LEFTRIGHT')
                controls_row.operator("universalgta.duplicate_mapping", text="Duplicate", icon='DUPLICATE')
                
                # Estado del mapeo
                status_row = edit_box.row()
                if item.source_bone and item.target_bone:
                    if (settings.source_armature and item.source_bone in [b.name for b in settings.source_armature.pose.bones] and
                        settings.target_armature and item.target_bone in [b.name for b in settings.target_armature.pose.bones]):
                        status_row.label(text="Status: Valid", icon='CHECKMARK')
                    else:
                        status_row.label(text="Status: Invalid bones", icon='ERROR')
                else:
                    status_row.label(text="Status: Incomplete", icon='DOT')
        else:
            # Mensaje cuando no hay mapeos
            empty_box = box.box()
            empty_col = empty_box.column(align=True)
            empty_col.label(text="No bone mappings configured", icon='ERROR')
            empty_col.separator()
            empty_col.label(text="Getting Started:")
            empty_col.label(text="1. Set source and target armatures above")
            empty_col.label(text="2. Click 'Add Target Bones' or 'Auto Detect'")
            empty_col.label(text="3. Configure individual mappings")
        
        # ESTADÍSTICAS FINALES
        if len(settings.bone_mappings) > 0:
            layout.separator()
            stats_box = layout.box()
            stats_box.label(text="Mapping Statistics", icon='GRAPH')
            
            stats_row = stats_box.row()
            
            # Contar estadísticas
            total_mappings = len(settings.bone_mappings)
            enabled_mappings = sum(1 for m in settings.bone_mappings if m.enabled)
            auto_mappings = sum(1 for m in settings.bone_mappings if m.detection_method == "Auto")
            valid_mappings = 0
            
            if settings.source_armature and settings.target_armature:
                source_bones = {bone.name for bone in settings.source_armature.pose.bones}
                target_bones = {bone.name for bone in settings.target_armature.pose.bones}
                
                for mapping in settings.bone_mappings:
                    if (mapping.enabled and mapping.source_bone and mapping.target_bone and
                        mapping.source_bone in source_bones and mapping.target_bone in target_bones):
                        valid_mappings += 1
            
            # Mostrar estadísticas
            left_stats = stats_row.column()
            left_stats.label(text=f"Total: {total_mappings}")
            left_stats.label(text=f"Enabled: {enabled_mappings}")
            
            right_stats = stats_row.column()
            right_stats.label(text=f"Auto: {auto_mappings}")
            right_stats.label(text=f"Valid: {valid_mappings}")


class UNIVERSALGTA_PT_ConversionPanel(Panel):
    """Panel para ejecutar la conversión"""
    bl_label = "Conversion"
    bl_idname = "UNIVERSALGTA_PT_conversion_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # Verificar si la configuración es válida
        has_source = settings.source_armature and settings.source_armature.type == 'ARMATURE'
        has_target = settings.target_armature and settings.target_armature.type == 'ARMATURE'
        has_mappings = len(settings.bone_mappings) > 0
        has_enabled_mappings = any(m.enabled for m in settings.bone_mappings)
        
        is_valid = has_source and has_target and has_mappings and has_enabled_mappings
        
        # Estado de la conversión
        box = layout.box()
        if is_valid:
            box.label(text="Ready for Conversion", icon='CHECKMARK')
        else:
            box.label(text="Configuration Incomplete", icon='ERROR')
            
            col = box.column()
            if not has_source:
                col.label(text="• Missing source armature", icon='DOT')
            if not has_target:
                col.label(text="• Missing target armature", icon='DOT')
            if not has_mappings:
                col.label(text="• No bone mappings configured", icon='DOT')
            elif not has_enabled_mappings:
                col.label(text="• No enabled bone mappings", icon='DOT')
        
        # Herramientas de preview y testing
        layout.separator()
        box = layout.box()
        box.label(text="Preview & Testing", icon='VIEW3D')
        
        row = box.row()
        row.operator("universalgta.preview_conversion", text="Preview", icon='VIEWZOOM')
        row.operator("universalgta.test_bone_mappings", text="Test", icon='PLAY')
        
        row = box.row()
        row.operator("universalgta.clear_test_constraints", text="Clear Test", icon='X')
        
        # Botón principal de conversión
        layout.separator()
        box = layout.box()
        box.label(text="Execute Conversion", icon='PLAY')
        
        col = box.column()
        col.scale_y = 1.5
        
        if is_valid:
            col.operator("universalgta.execute_conversion", 
                        text="Convert to GTA SA", 
                        icon='ARMATURE_DATA')
        else:
            col.enabled = False
            col.operator("universalgta.execute_conversion", 
                        text="Convert to GTA SA (Incomplete)", 
                        icon='ERROR')
        
        # Información adicional
        info_col = box.column()
        if settings.auto_apply_custom_pose:
            info_col.label(text="• Custom pose will be applied automatically", icon='INFO')
        if settings.debug_mode:
            info_col.label(text="• Debug mode enabled", icon='CONSOLE')


class UNIVERSALGTA_PT_UtilitiesPanel(Panel):
    """Panel para herramientas de limpieza y utilidades"""
    bl_label = "Utilities"
    bl_idname = "UNIVERSALGTA_PT_utilities_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        
        # Herramientas de limpieza
        box = layout.box()
        box.label(text="Cleanup Tools", icon='BRUSH_DATA')
        
        col = box.column()
        col.operator("universalgta.clean_model", text="Clean Model", icon='OUTLINER_OB_MESH')
        col.operator("universalgta.clean_armatures", text="Clean Armatures", icon='OUTLINER_OB_ARMATURE')
        col.operator("universalgta.clean_empty_vertex_groups", text="Clean Vertex Groups", icon='GROUP_VERTEX')
        col.operator("universalgta.fix_modifiers", text="Fix Modifiers", icon='MODIFIER')
        
        # Segunda columna de limpieza
        col.separator()
        col.operator("universalgta.purge_unused_data", text="Purge Unused Data", icon='TRASH')
        col.operator("universalgta.purge_scene", text="Purge Scene", icon='SCENE_DATA')
        col.operator("universalgta.remove_duplicates", text="Remove Duplicates", icon='DUPLICATE')
        col.operator("universalgta.optimize_mesh", text="Optimize Mesh", icon='MOD_REMESH')
        
        # Herramientas de exportación
        layout.separator()
        box = layout.box()
        box.label(text="Export Tools", icon='EXPORT')
        
        col = box.column()
        col.operator("universalgta.export_textures", text="Export Textures", icon='TEXTURE')
        
        # Información y ayuda
        layout.separator()
        box = layout.box()
        box.label(text="Information", icon='HELP')
        
        col = box.column()
        col.label(text="Universal GTA Converter v3.2.2", icon='ARMATURE_DATA')
        col.label(text="Converts custom rigs to GTA SA format")
        col.label(text="with intelligent bone detection")
        
        col.separator()
        col.label(text="Usage:")
        col.label(text="1. Set source and target armatures")
        col.label(text="2. Configure bone mappings")
        col.label(text="3. Execute conversion")
        col.label(text="4. Clean up if needed")
        
        col.separator()
        col.label(text="Features:")
        col.label(text="• Drag & drop bone mapping")
        col.label(text="• Intelligent auto-detection")
        col.label(text="• Real-time validation")
        col.label(text="• Custom pose application")
        col.label(text="• Advanced cleanup tools")


# Lista de clases para registro
classes = [
    UNIVERSALGTA_PT_MainPanel,
    UNIVERSALGTA_PT_BoneMappingPanel,
    UNIVERSALGTA_PT_ConversionPanel,
    UNIVERSALGTA_PT_UtilitiesPanel,
]


def register():
    """Registra todos los paneles"""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Desregistra todos los paneles"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
