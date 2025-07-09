"""
Sistema de estilos modernos para UI - Checkboxes y botones estilizados
Basado en el diseño de referencia proporcionado
"""

import bpy
from bpy.types import Panel, UIList


class ModernUIStyles:
    """Clase auxiliar para aplicar estilos modernos a elementos UI"""
    
    @staticmethod
    def draw_modern_checkbox(layout, item, prop_name, text="", icon_enabled='CHECKMARK', icon_disabled='CANCEL'):
        """Dibuja un checkbox moderno estilizado"""
        row = layout.row(align=True)
        row.scale_y = 1.2
        
        # Crear sub-layout para el checkbox
        checkbox_layout = row.row(align=True)
        checkbox_layout.scale_x = 0.8
        
        # Aplicar colores basados en estado
        if getattr(item, prop_name):
            checkbox_layout.alert = False
            checkbox_layout.prop(item, prop_name, text=text, toggle=True, 
                               icon=icon_enabled, icon_only=True)
        else:
            checkbox_layout.alert = True
            checkbox_layout.prop(item, prop_name, text=text, toggle=True, 
                               icon=icon_disabled, icon_only=True)
        
        return checkbox_layout
    
    @staticmethod
    def draw_increment_decrement_buttons(layout, item, prop_name, step=0.1, text=""):
        """Dibuja botones de incremento/decremento estilizados"""
        main_row = layout.row(align=True)
        main_row.scale_y = 1.1
        
        # Botón de decremento
        dec_btn = main_row.row(align=True)
        dec_btn.scale_x = 0.4
        dec_op = dec_btn.operator("universalgta.adjust_value", text="", icon='REMOVE')
        dec_op.prop_name = prop_name
        dec_op.adjustment = -step
        dec_op.item_index = getattr(item, 'index', 0)
        
        # Campo de valor central
        value_field = main_row.row(align=True)
        value_field.scale_x = 1.2
        value_field.prop(item, prop_name, text=text)
        
        # Botón de incremento
        inc_btn = main_row.row(align=True)
        inc_btn.scale_x = 0.4
        inc_op = inc_btn.operator("universalgta.adjust_value", text="", icon='ADD')
        inc_op.prop_name = prop_name
        inc_op.adjustment = step
        inc_op.item_index = getattr(item, 'index', 0)
        
        return main_row
    
    @staticmethod
    def draw_modern_button(layout, operator, text, icon=None, alert=False, scale_y=1.0):
        """Dibuja un botón moderno estilizado"""
        btn_row = layout.row(align=True)
        btn_row.scale_y = scale_y
        
        if alert:
            btn_row.alert = True
        
        if icon:
            btn_row.operator(operator, text=text, icon=icon)
        else:
            btn_row.operator(operator, text=text)
        
        return btn_row
    
    @staticmethod
    def draw_status_indicator(layout, status, text, icon_good='CHECKMARK', icon_bad='ERROR'):
        """Dibuja un indicador de estado estilizado"""
        indicator_row = layout.row(align=True)
        indicator_row.scale_y = 0.9
        
        if status:
            indicator_row.label(text=text, icon=icon_good)
        else:
            indicator_row.alert = True
            indicator_row.label(text=text, icon=icon_bad)
        
        return indicator_row
    
    @staticmethod
    def draw_info_box(layout, title, content_lines, icon='INFO'):
        """Dibuja una caja de información estilizada"""
        info_box = layout.box()
        
        # Header
        header_row = info_box.row()
        header_row.scale_y = 1.2
        header_row.label(text=title, icon=icon)
        
        # Contenido
        content_col = info_box.column(align=True)
        content_col.scale_y = 0.9
        
        for line in content_lines:
            content_col.label(text=line)
        
        return info_box
    
    @staticmethod
    def draw_progress_bar(layout, progress, text="", width=200):
        """Dibuja una barra de progreso estilizada usando botones"""
        progress_row = layout.row(align=True)
        progress_row.scale_y = 0.8
        
        # Calcular segmentos
        segments = 20
        filled_segments = int(progress * segments)
        
        for i in range(segments):
            segment = progress_row.row(align=True)
            segment.scale_x = 0.05
            
            if i < filled_segments:
                segment.label(text="", icon='SNAP_ON')
            else:
                segment.label(text="", icon='SNAP_OFF')
        
        # Texto de progreso
        if text:
            progress_row.label(text=f"{text} {progress*100:.0f}%")
        
        return progress_row


class UNIVERSALGTA_OT_adjust_value(bpy.types.Operator):
    """Operador para ajustar valores con botones +/-"""
    bl_idname = "universalgta.adjust_value"
    bl_label = "Adjust Value"
    bl_description = "Ajusta un valor numérico"
    bl_options = {'REGISTER', 'UNDO'}
    
    prop_name: bpy.props.StringProperty()
    adjustment: bpy.props.FloatProperty()
    item_index: bpy.props.IntProperty(default=0)
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        try:
            # Obtener el item apropiado
            if self.prop_name in ['arm_spacing', 'leg_spacing', 'facial_expressiveness', 
                                 'eyebrow_intensity', 'jaw_expression', 'detection_threshold']:
                # Propiedades directas de settings
                current_value = getattr(settings, self.prop_name)
                new_value = current_value + self.adjustment
                setattr(settings, self.prop_name, new_value)
                
            elif hasattr(settings, 'bone_mappings') and self.item_index < len(settings.bone_mappings):
                # Propiedades de bone mapping items
                item = settings.bone_mappings[self.item_index]
                if hasattr(item, self.prop_name):
                    current_value = getattr(item, self.prop_name)
                    new_value = current_value + self.adjustment
                    setattr(item, self.prop_name, new_value)
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error ajustando valor: {str(e)}")
            return {'CANCELLED'}


class UNIVERSALGTA_PT_ModernStylesDemo(Panel):
    """Panel de demostración de estilos modernos"""
    bl_label = "Modern UI Styles Demo"
    bl_idname = "UNIVERSALGTA_PT_modern_styles_demo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # === DEMO DE CHECKBOXES MODERNOS ===
        checkbox_box = layout.box()
        checkbox_box.label(text="🎨 Modern Checkboxes", icon='CHECKMARK')
        
        # Checkbox estilizado para debug mode
        ModernUIStyles.draw_modern_checkbox(
            checkbox_box, settings, "debug_mode", 
            text="Debug Mode", 
            icon_enabled='CONSOLE', 
            icon_disabled='CANCEL'
        )
        
        # Checkbox estilizado para auto apply
        ModernUIStyles.draw_modern_checkbox(
            checkbox_box, settings, "auto_apply_custom_pose", 
            text="Auto Apply Pose",
            icon_enabled='PLAY', 
            icon_disabled='PAUSE'
        )
        
        layout.separator()
        
        # === DEMO DE BOTONES INCREMENTO/DECREMENTO ===
        increment_box = layout.box()
        increment_box.label(text="🔢 Increment/Decrement Buttons", icon='PLUS')
        
        # Espaciado de brazos con botones +/-
        arm_row = increment_box.row()
        arm_row.label(text="Arm Spacing:")
        ModernUIStyles.draw_increment_decrement_buttons(
            arm_row, settings, "arm_spacing", step=0.1, text=""
        )
        
        # Espaciado de piernas con botones +/-
        leg_row = increment_box.row()
        leg_row.label(text="Leg Spacing:")
        ModernUIStyles.draw_increment_decrement_buttons(
            leg_row, settings, "leg_spacing", step=0.1, text=""
        )
        
        # Expresividad facial con botones +/-
        facial_row = increment_box.row()
        facial_row.label(text="Facial Expression:")
        ModernUIStyles.draw_increment_decrement_buttons(
            facial_row, settings, "facial_expressiveness", step=0.05, text=""
        )
        
        layout.separator()
        
        # === DEMO DE BOTONES MODERNOS ===
        buttons_box = layout.box()
        buttons_box.label(text="🚀 Modern Buttons", icon='PLAY')
        
        # Botón normal
        ModernUIStyles.draw_modern_button(
            buttons_box, "universalgta.auto_detect_mappings", 
            "🔍 Auto Detect", icon='AUTO', scale_y=1.2
        )
        
        # Botón de alerta
        ModernUIStyles.draw_modern_button(
            buttons_box, "universalgta.clear_mappings", 
            "🗑 Clear All", icon='TRASH', alert=True, scale_y=1.2
        )
        
        layout.separator()
        
        # === DEMO DE INDICADORES DE ESTADO ===
        status_box = layout.box()
        status_box.label(text="📊 Status Indicators", icon='INFO')
        
        # Indicadores de estado
        ModernUIStyles.draw_status_indicator(
            status_box, settings.source_armature is not None, 
            "Source Armature", icon_good='CHECKMARK', icon_bad='ERROR'
        )
        
        ModernUIStyles.draw_status_indicator(
            status_box, settings.target_armature is not None, 
            "Target Armature", icon_good='CHECKMARK', icon_bad='ERROR'
        )
        
        enabled_mappings = sum(1 for m in settings.bone_mappings if m.enabled)
        ModernUIStyles.draw_status_indicator(
            status_box, enabled_mappings > 0, 
            f"Active Mappings: {enabled_mappings}", 
            icon_good='BONE_DATA', icon_bad='CANCEL'
        )
        
        layout.separator()
        
        # === DEMO DE CAJA DE INFORMACIÓN ===
        ModernUIStyles.draw_info_box(
            layout, "💡 Style Information", 
            [
                "• Checkboxes con iconos dinámicos",
                "• Botones +/- para valores numéricos", 
                "• Indicadores de estado coloridos",
                "• Diseño basado en imagen de referencia"
            ],
            icon='QUESTION'
        )
        
        layout.separator()
        
        # === DEMO DE BARRA DE PROGRESO ===
        progress_box = layout.box()
        progress_box.label(text="📈 Progress Bar", icon='TIME')
        
        # Calcular progreso basado en mapeos
        total_mappings = len(settings.bone_mappings)
        if total_mappings > 0:
            progress = enabled_mappings / total_mappings
            ModernUIStyles.draw_progress_bar(
                progress_box, progress, "Mapping Progress"
            )
        else:
            ModernUIStyles.draw_progress_bar(
                progress_box, 0.0, "No Mappings"
            )


# Integración con el panel principal de mapeo existente
class UNIVERSALGTA_PT_StyledBoneMappingPanel(Panel):
    """Panel de mapeo de huesos con estilos modernos aplicados"""
    bl_label = "Bone Mapping - Styled"
    bl_idname = "UNIVERSALGTA_PT_styled_bone_mapping_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # === HEADER CON ESTILO MODERNO ===
        header_box = layout.box()
        header_row = header_box.row(align=True)
        header_row.scale_y = 1.4
        header_row.label(text="🦴 Bone Mapping System", icon='ARMATURE_DATA')
        
        # Estadísticas estilizadas
        enabled_count = sum(1 for m in settings.bone_mappings if m.enabled)
        total_count = len(settings.bone_mappings)
        
        if total_count > 0:
            progress = enabled_count / total_count
            ModernUIStyles.draw_progress_bar(
                header_box, progress, f"Mappings: {enabled_count}/{total_count}"
            )
        
        layout.separator()
        
        # === CONTROLES PRINCIPALES CON ESTILO ===
        controls_box = layout.box()
        controls_box.label(text="🎮 Quick Actions", icon='PLAY')
        
        # Botones principales estilizados
        actions_row = controls_box.row(align=True)
        actions_row.scale_y = 1.3
        
        ModernUIStyles.draw_modern_button(
            actions_row, "universalgta.auto_detect_mappings", 
            "🔍 Auto Detect", icon='AUTO'
        )
        
        ModernUIStyles.draw_modern_button(
            actions_row, "universalgta.validate_mappings", 
            "✓ Validate", icon='CHECKMARK'
        )
        
        # Segunda fila de acciones
        mgmt_row = controls_box.row(align=True)
        mgmt_row.scale_y = 1.2
        
        ModernUIStyles.draw_modern_button(
            mgmt_row, "universalgta.add_target_bones", 
            "📋 Add All", icon='BONE_DATA'
        )
        
        ModernUIStyles.draw_modern_button(
            mgmt_row, "universalgta.clear_mappings", 
            "🗑 Clear", icon='TRASH', alert=True
        )
        
        layout.separator()
        
        # === SISTEMA DE GUARDADO/CARGA ESTILIZADO ===
        save_box = layout.box()
        save_box.label(text="💾 Save & Load System", icon='FILE')
        
        file_actions = save_box.row(align=True)
        file_actions.scale_y = 1.3
        
        ModernUIStyles.draw_modern_button(
            file_actions, "universalgta.save_mapping", 
            "💾 Save", icon='FILE_TICK'
        )
        
        ModernUIStyles.draw_modern_button(
            file_actions, "universalgta.load_mapping", 
            "📂 Load", icon='FILE_FOLDER'
        )
        
        ModernUIStyles.draw_modern_button(
            file_actions, "universalgta.export_mapping_template", 
            "📋 Template", icon='TEXT'
        )
        
        layout.separator()
        
        # === INDICADORES DE ESTADO ===
        status_box = layout.box()
        status_box.label(text="📊 System Status", icon='INFO')
        
        ModernUIStyles.draw_status_indicator(
            status_box, settings.source_armature is not None, 
            "Source Armature Connected"
        )
        
        ModernUIStyles.draw_status_indicator(
            status_box, settings.target_armature is not None, 
            "Target Armature Connected"
        )
        
        ModernUIStyles.draw_status_indicator(
            status_box, enabled_count > 0, 
            f"Active Mappings: {enabled_count}"
        )
        
        # Verificar Pelvis específicamente
        pelvis_mapped = any(m.enabled and m.target_bone == 'Pelvis' for m in settings.bone_mappings)
        ModernUIStyles.draw_status_indicator(
            status_box, pelvis_mapped, 
            "Pelvis Mapped (Required for GTA SA)"
        )
        
        # === CONFIGURACIÓN AVANZADA ===
        if total_count > 0:
            layout.separator()
            
            config_box = layout.box()
            config_box.label(text="⚙️ Advanced Settings", icon='PREFERENCES')
            
            # Controles de selección masiva estilizados
            bulk_row = config_box.row(align=True)
            bulk_row.scale_y = 1.1
            
            ModernUIStyles.draw_modern_button(
                bulk_row, "universalgta.enable_all_mappings", 
                "✓ Enable All", icon='CHECKMARK'
            )
            
            ModernUIStyles.draw_modern_button(
                bulk_row, "universalgta.disable_all_mappings", 
                "✗ Disable All", icon='CANCEL'
            )
            
            ModernUIStyles.draw_modern_button(
                bulk_row, "universalgta.enable_high_confidence", 
                "🎯 High Confidence", icon='FILTER'
            )
            
            # Threshold de detección con botones +/-
            threshold_row = config_box.row()
            threshold_row.label(text="Detection Threshold:")
            ModernUIStyles.draw_increment_decrement_buttons(
                threshold_row, settings, "detection_threshold", step=0.1, text=""
            )
        
        # === INFORMACIÓN ÚTIL ===
        if total_count == 0:
            ModernUIStyles.draw_info_box(
                layout, "🚀 Quick Start Guide", 
                [
                    "1. Set Source & Target armatures above",
                    "2. Click '🔍 Auto Detect' to find mappings",
                    "3. Use '✓ Validate' to check configuration",
                    "4. Save your mapping with '💾 Save' button"
                ],
                icon='QUESTION'
            )


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_adjust_value,
    UNIVERSALGTA_PT_ModernStylesDemo,
    UNIVERSALGTA_PT_StyledBoneMappingPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)