"""
Panel principal simplificado para el addon Universal GTA Converter
INTERFAZ AMIGABLE Y ORGANIZADA
"""

import bpy
from bpy.types import Panel


class UNIVERSALGTA_PT_MainPanel(Panel):
    """Panel principal simplificado del Universal GTA Converter"""
    bl_label = "Universal GTA Converter"
    bl_idname = "UNIVERSALGTA_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # Header compacto
        header_box = layout.box()
        header_row = header_box.row()
        header_row.label(text="Universal to GTA SA Converter", icon='ARMATURE_DATA')
        header_row.label(text="v3.2.2")
        
        # Configuración principal - más compacta
        layout.separator()
        main_box = layout.box()
        main_box.label(text="Setup", icon='SETTINGS')
        
        col = main_box.column()
        col.prop(settings, "source_armature", text="Source")
        col.prop(settings, "target_armature", text="Target")
        
        # Botones principales - más prominentes
        layout.separator()
        action_box = layout.box()
        action_box.label(text="Quick Actions", icon='PLAY')
        
        # Fila de botones principales
        btn_row = action_box.row()
        btn_row.scale_y = 1.3
        btn_row.operator("universalgta.auto_detect_mappings", text="Auto Setup", icon='AUTO')
        btn_row.operator("universalgta.execute_conversion", text="Convert", icon='ARMATURE_DATA')


class UNIVERSALGTA_PT_BoneMappingPanel(Panel):
    """Panel de mapeo de huesos simplificado"""
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
        
        # Controles principales simplificados
        controls_box = layout.box()
        controls_box.label(text="Mapping Controls", icon='CONSTRAINT_BONE')
        
        # Primera fila - botones más importantes
        row1 = controls_box.row()
        row1.operator("universalgta.auto_detect_mappings", text="Auto Detect", icon='AUTO')
        row1.operator("universalgta.validate_mappings", text="Validate", icon='CHECKMARK')
        
        # Segunda fila - controles adicionales
        row2 = controls_box.row()
        row2.operator("universalgta.add_target_bones", text="Add All Bones", icon='BONE_DATA')
        row2.operator("universalgta.clear_mappings", text="Clear", icon='TRASH')
        
        # Lista de mapeos - más compacta
        if len(settings.bone_mappings) > 0:
            layout.separator()
            mappings_box = layout.box()
            
            # Header con estadísticas
            enabled_count = sum(1 for m in settings.bone_mappings if m.enabled)
            mappings_box.label(text=f"Bone Mappings ({enabled_count}/{len(settings.bone_mappings)})", icon='OUTLINER_DATA_ARMATURE')
            
            # Lista simplificada
            list_container = mappings_box.column()
            
            # Template list más pequeña
            list_row = list_container.row()
            list_col = list_row.column()
            list_col.template_list(
                "UNIVERSALGTA_UL_BoneMappingList",
                "",
                settings,
                "bone_mappings",
                settings,
                "bone_mappings_index",
                rows=4,  # Menos filas por defecto
                maxrows=8
            )
            
            # Controles laterales simplificados
            controls_col = list_row.column(align=True)
            controls_col.scale_x = 0.7
            controls_col.operator("universalgta.move_mapping_up", text="", icon='TRIA_UP')
            controls_col.operator("universalgta.move_mapping_down", text="", icon='TRIA_DOWN')
            controls_col.separator()
            controls_col.operator("universalgta.remove_mapping_entry", text="", icon='REMOVE')
            
            # Editor simplificado para el mapeo seleccionado
            if 0 <= settings.bone_mappings_index < len(settings.bone_mappings):
                item = settings.bone_mappings[settings.bone_mappings_index]
                
                edit_box = mappings_box.box()
                edit_box.label(text=f"Edit: {item.target_bone or 'Unnamed'}", icon='TOOL_SETTINGS')
                
                # Habilitado y método
                info_row = edit_box.row()
                info_row.prop(item, "enabled", text="Enable")
                info_row.label(text=f"Method: {item.detection_method}")
                if item.confidence > 0:
                    info_row.label(text=f"Conf: {item.confidence:.1f}")
                
                # Edición de huesos
                bones_col = edit_box.column()
                
                # Source bone
                src_row = bones_col.row()
                src_row.label(text="From:", icon='BONE_DATA')
                if settings.source_armature and settings.source_armature.type == 'ARMATURE':
                    src_row.prop_search(item, "source_bone", settings.source_armature.pose, "bones", text="")
                else:
                    src_row.prop(item, "source_bone", text="")
                
                # Target bone
                tgt_row = bones_col.row()
                tgt_row.label(text="To:", icon='BONE_DATA')
                if settings.target_armature and settings.target_armature.type == 'ARMATURE':
                    tgt_row.prop_search(item, "target_bone", settings.target_armature.pose, "bones", text="")
                else:
                    tgt_row.prop(item, "target_bone", text="")
        else:
            # Mensaje cuando no hay mapeos
            layout.separator()
            info_box = layout.box()
            info_col = info_box.column(align=True)
            info_col.label(text="No mappings configured", icon='INFO')
            info_col.label(text="1. Set armatures above")
            info_col.label(text="2. Click 'Auto Detect'")


class UNIVERSALGTA_PT_AdvancedPanel(Panel):
    """Panel avanzado con opciones adicionales"""
    bl_label = "Advanced Options"
    bl_idname = "UNIVERSALGTA_PT_advanced_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # Configuración de conversión
        conv_box = layout.box()
        conv_box.label(text="Conversion Settings", icon='SETTINGS')
        
        col = conv_box.column()
        col.prop(settings, "auto_apply_custom_pose", text="Auto Apply Pose")
        col.prop(settings, "auto_fix_normals", text="Auto Fix Normals")
        col.prop(settings, "keep_vertex_colors", text="Keep Vertex Colors")
        
        # Espaciado
        layout.separator()
        spacing_box = layout.box()
        spacing_box.label(text="Bone Spacing", icon='TRANSFORM_ORIGINS')
        
        col = spacing_box.column()
        col.prop(settings, "arm_spacing", text="Arms")
        col.prop(settings, "leg_spacing", text="Legs")
        
        row = col.row()
        row.operator("universalgta.apply_spacing", text="Apply Spacing", icon='BONE_DATA')
        
        # Herramientas de testing
        layout.separator()
        test_box = layout.box()
        test_box.label(text="Testing Tools", icon='TOOL_SETTINGS')
        
        col = test_box.column()
        col.operator("universalgta.test_bone_mappings", text="Test Mappings", icon='PLAY')
        col.operator("universalgta.clear_test_constraints", text="Clear Test", icon='X')
        col.operator("universalgta.preview_conversion", text="Preview", icon='VIEWZOOM')


class UNIVERSALGTA_PT_UtilitiesPanel(Panel):
    """Panel de utilidades simplificado"""
    bl_label = "Cleanup & Tools"
    bl_idname = "UNIVERSALGTA_PT_utilities_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        
        # Herramientas principales de limpieza
        cleanup_box = layout.box()
        cleanup_box.label(text="Cleanup Tools", icon='BRUSH_DATA')
        
        col = cleanup_box.column()
        col.operator("universalgta.clean_model", text="Clean Model", icon='OUTLINER_OB_MESH')
        col.operator("universalgta.clean_armatures", text="Clean Armatures", icon='OUTLINER_OB_ARMATURE')
        col.operator("universalgta.purge_unused_data", text="Purge Unused", icon='TRASH')
        
        # Herramientas de normales
        layout.separator()
        normals_box = layout.box()
        normals_box.label(text="Normals", icon='NORMALS_FACE')
        
        col = normals_box.column()
        col.operator("universalgta.fix_normals", text="Fix Normals", icon='NORMALS_FACE')
        col.operator("universalgta.check_normals_consistency", text="Check Normals", icon='CHECKMARK')


class UNIVERSALGTA_PT_AnimationsPanel(Panel):
    """Panel de animaciones simplificado"""
    bl_label = "Animations"
    bl_idname = "UNIVERSALGTA_PT_animations_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # Animaciones predefinidas
        anim_box = layout.box()
        anim_box.label(text="Predefined Animations", icon='ANIM')
        
        col = anim_box.column()
        col.prop(settings, "predefined_animation", text="Type")
        
        row = col.row()
        row.operator("universalgta.load_animation", text="Load", icon='PLAY')
        row.operator("universalgta.clear_animations", text="Clear", icon='X')
        
        # Expresividad facial
        if settings.predefined_animation == 'FACIAL':
            layout.separator()
            facial_box = layout.box()
            facial_box.label(text="Facial Settings", icon='MESH_DATA')
            
            col = facial_box.column()
            col.prop(settings, "eyebrow_intensity", text="Eyebrows")
            col.prop(settings, "jaw_expression", text="Jaw")
            
            col.operator("universalgta.apply_facial_expressiveness", text="Apply Expression", icon='MESH_DATA')


class UNIVERSALGTA_PT_StatusPanel(Panel):
    """Panel de estado del sistema"""
    bl_label = "Status & Reference"
    bl_idname = "UNIVERSALGTA_PT_status_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # GTA SA Reference Tools
        ref_box = layout.box()
        ref_box.label(text="GTA SA Reference", icon='BONE_DATA')
        
        col = ref_box.column()
        col.operator("universalgta.show_gta_bone_reference", text="Show Bone Names", icon='CONSOLE')
        col.operator("universalgta.create_gta_armature_template", text="Create Template", icon='ARMATURE_DATA')
        
        info_col = ref_box.column()
        info_col.scale_y = 0.8
        info_col.label(text="Nombres exactos de huesos SA:")
        info_col.label(text="• Con espacios: 'L Hand', 'R Thigh'")
        info_col.label(text="• Sin espacios: 'Pelvis', 'belly'")
        info_col.label(text="• Siempre excluido: 'Root'")
        
        # Estado de la configuración
        layout.separator()
        status_box = layout.box()
        status_box.label(text="Configuration Status", icon='INFO')
        
        col = status_box.column()
        
        # Verificar armatures
        if settings.source_armature and settings.source_armature.type == 'ARMATURE':
            col.label(text="✓ Source Armature OK", icon='CHECKMARK')
        else:
            col.label(text="✗ Source Armature Missing", icon='ERROR')
        
        if settings.target_armature and settings.target_armature.type == 'ARMATURE':
            col.label(text="✓ Target Armature OK", icon='CHECKMARK')
        else:
            col.label(text="✗ Target Armature Missing", icon='ERROR')
        
        # Verificar mapeos
        enabled_mappings = sum(1 for m in settings.bone_mappings if m.enabled)
        if enabled_mappings > 0:
            col.label(text=f"✓ {enabled_mappings} Mappings Ready", icon='CHECKMARK')
            
            # Verificar específicamente Pelvis
            pelvis_mapped = any(m.enabled and m.target_bone == 'Pelvis' for m in settings.bone_mappings)
            if pelvis_mapped:
                col.label(text="✓ Pelvis Included", icon='CHECKMARK')
            else:
                col.label(text="⚠ Pelvis Not Mapped", icon='ERROR')
        else:
            col.label(text="✗ No Active Mappings", icon='ERROR')
        
        # Estado general
        layout.separator()
        is_ready = (settings.source_armature and settings.target_armature and enabled_mappings > 0)
        
        if is_ready:
            ready_box = layout.box()
            ready_box.label(text="Ready for Conversion!", icon='CHECKMARK')
        else:
            warning_box = layout.box()
            warning_box.label(text="Setup Required", icon='ERROR')


# Lista de clases para registro
classes = [
    UNIVERSALGTA_PT_MainPanel,
    UNIVERSALGTA_PT_BoneMappingPanel,
    UNIVERSALGTA_PT_AdvancedPanel,
    UNIVERSALGTA_PT_UtilitiesPanel,
    UNIVERSALGTA_PT_AnimationsPanel,
    UNIVERSALGTA_PT_StatusPanel,
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
