"""
Panel principal con soporte para Shape Keys
INTERFAZ AMIGABLE Y ORGANIZADA - SIN DUPLICACIÓN DE PANELES
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
        header_row.label(text="v3.2.3")
        
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


class UNIVERSALGTA_PT_ShapeKeysPanel(Panel):
    """Panel dedicado para Shape Keys - VERSIÓN ÚNICA"""
    bl_label = "Shape Keys Manager"
    bl_idname = "UNIVERSALGTA_PT_shape_keys_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        # Solo mostrar si los operadores de Shape Keys están disponibles
        try:
            from ..operators.shape_keys import UNIVERSALGTA_OT_apply_all_shape_keys
            return True
        except ImportError:
            return False

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # Verificar si el módulo de shape keys está disponible
        try:
            from ..operators.shape_keys import UNIVERSALGTA_OT_apply_all_shape_keys
            shape_keys_available = True
        except ImportError:
            shape_keys_available = False
        
        if not shape_keys_available:
            layout.label(text="Shape Keys no disponibles", icon='ERROR')
            layout.label(text="Verificar operators/shape_keys.py")
            return
        
        # Información sobre Shape Keys
        info_box = layout.box()
        info_box.label(text="Shape Keys Detection", icon='SHAPEKEY_DATA')
        
        # Verificar si hay shape keys en los meshes
        shape_keys_info = self._get_shape_keys_info(settings.source_armature)
        
        if shape_keys_info['total_meshes_with_keys'] > 0:
            info_col = info_box.column()
            info_col.label(text=f"✓ {shape_keys_info['total_meshes_with_keys']} meshes con shape keys")
            info_col.label(text=f"✓ {shape_keys_info['total_shape_keys']} shape keys totales")
            
            # Lista de meshes con shape keys
            for mesh_name, keys in shape_keys_info['meshes_details'].items():
                key_col = info_box.column()
                key_col.scale_y = 0.8
                key_col.label(text=f"• {mesh_name}: {len(keys)} keys")
        else:
            info_box.label(text="No se detectaron shape keys", icon='INFO')
        
        layout.separator()
        
        # Herramientas principales de Shape Keys
        tools_box = layout.box()
        tools_box.label(text="Shape Keys Tools", icon='TOOL_SETTINGS')
        
        # Primera fila - herramientas de información
        row1 = tools_box.row()
        row1.operator("universalgta.list_shape_keys", text="List Keys", icon='OUTLINER_DATA_MESH')
        row1.operator("universalgta.backup_shape_keys", text="Backup", icon='FILE_BACKUP')
        
        # Segunda fila - aplicación de shape keys
        row2 = tools_box.row()
        row2.scale_y = 1.2
        row2.operator("universalgta.apply_all_shape_keys", text="Apply All Shape Keys", icon='SHAPEKEY_DATA')
        
        # Configuración de aplicación
        layout.separator()
        config_box = layout.box()
        config_box.label(text="Application Settings", icon='PREFERENCES')
        
        col = config_box.column()
        col.prop(settings, "preserve_basis_shape_key", text="Preserve Basis")
        col.prop(settings, "apply_shape_keys_with_modifier", text="Apply with Modifier")
        col.prop(settings, "create_shape_keys_backup", text="Auto Backup")
        
        # Tercera fila - restauración
        if shape_keys_info['backup_exists']:
            layout.separator()
            restore_box = layout.box()
            restore_box.label(text="Backup Management", icon='RECOVER_LAST')
            
            restore_row = restore_box.row()
            restore_row.operator("universalgta.restore_shape_keys_backup", text="Restore from Backup", icon='LOOP_BACK')
        
        # Advertencias importantes
        layout.separator()
        warning_box = layout.box()
        warning_box.alert = True
        warning_box.label(text="⚠️ IMPORTANTE:", icon='ERROR')
        
        warning_col = warning_box.column()
        warning_col.scale_y = 0.8
        warning_col.label(text="• Las shape keys se aplican automáticamente")
        warning_col.label(text="  durante la conversión a GTA SA")
        warning_col.label(text="• Usa 'Backup' antes de convertir")
        warning_col.label(text="• No se pueden deshacer después")
    
    def _get_shape_keys_info(self, source_armature):
        """Obtiene información sobre las shape keys disponibles"""
        info = {
            'total_meshes_with_keys': 0,
            'total_shape_keys': 0,
            'meshes_details': {},
            'backup_exists': False
        }
        
        if not source_armature:
            return info
        
        # Buscar meshes con shape keys
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                obj.parent == source_armature and 
                obj.data.shape_keys and 
                len(obj.data.shape_keys.key_blocks) > 1):
                
                shape_keys = [key.name for key in obj.data.shape_keys.key_blocks]
                info['meshes_details'][obj.name] = shape_keys
                info['total_meshes_with_keys'] += 1
                info['total_shape_keys'] += len(shape_keys)
        
        # Verificar si existen backups
        backup_objects = [obj for obj in bpy.data.objects 
                         if obj.name.endswith("_BACKUP_ShapeKeys")]
        info['backup_exists'] = len(backup_objects) > 0
        
        return info


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
    """Panel avanzado con opciones adicionales incluyendo Shape Keys"""
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
        
        # Configuración de Shape Keys
        layout.separator()
        shape_keys_box = layout.box()
        shape_keys_box.label(text="Shape Keys Settings", icon='SHAPEKEY_DATA')
        
        sk_col = shape_keys_box.column()
        sk_col.prop(settings, "auto_apply_shape_keys", text="Auto Apply Shape Keys")
        sk_col.prop(settings, "create_shape_keys_backup", text="Auto Create Backup")
        sk_col.prop(settings, "preserve_basis_shape_key", text="Preserve Basis")
        
        # Botón para configuración manual
        sk_row = sk_col.row()
        sk_row.operator("universalgta.apply_all_shape_keys", text="Manual Apply", icon='SHAPEKEY_DATA')
        
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
    """Panel de estado del sistema con información de Shape Keys"""
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
        info_col.label(text="• Con espacios: ' L Hand', ' R Thigh'")
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
        
        # Verificar Shape Keys
        shape_keys_info = self._get_shape_keys_status(settings.source_armature)
        if shape_keys_info['has_shape_keys']:
            col.label(text=f"✓ {shape_keys_info['meshes_count']} Meshes with Shape Keys", icon='SHAPEKEY_DATA')
            if shape_keys_info['backup_exists']:
                col.label(text="✓ Shape Keys Backup Available", icon='FILE_BACKUP')
            else:
                col.label(text="⚠ No Shape Keys Backup", icon='ERROR')
        else:
            col.label(text="○ No Shape Keys Detected", icon='DOT')
        
        # Estado general
        layout.separator()
        is_ready = (settings.source_armature and settings.target_armature and enabled_mappings > 0)
        
        if is_ready:
            ready_box = layout.box()
            if shape_keys_info['has_shape_keys'] and not shape_keys_info['backup_exists']:
                ready_box.alert = True
                ready_box.label(text="Ready! (Recommend Shape Keys Backup)", icon='ERROR')
            else:
                ready_box.label(text="Ready for Conversion!", icon='CHECKMARK')
        else:
            warning_box = layout.box()
            warning_box.label(text="Setup Required", icon='ERROR')
    
    def _get_shape_keys_status(self, source_armature):
        """Obtiene el estado de las shape keys"""
        status = {
            'has_shape_keys': False,
            'meshes_count': 0,
            'backup_exists': False
        }
        
        if not source_armature:
            return status
        
        # Contar meshes con shape keys
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                obj.parent == source_armature and 
                obj.data.shape_keys and 
                len(obj.data.shape_keys.key_blocks) > 1):
                status['meshes_count'] += 1
        
        status['has_shape_keys'] = status['meshes_count'] > 0
        
        # Verificar backups
        backup_objects = [obj for obj in bpy.data.objects 
                         if obj.name.endswith("_BACKUP_ShapeKeys")]
        status['backup_exists'] = len(backup_objects) > 0
        
        return status


# Lista de clases para registro (SIN DUPLICACIÓN DEL PANEL SHAPE KEYS)
classes = [
    UNIVERSALGTA_PT_MainPanel,
    UNIVERSALGTA_PT_ShapeKeysPanel,  # SOLO UNA VERSIÓN
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