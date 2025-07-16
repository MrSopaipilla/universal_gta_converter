"""
Panel de créditos para Universal GTA SA Converter
"""

import bpy
import webbrowser
from bpy.types import Panel, Operator


class UNIVERSALGTA_OT_open_yoshi_channel(Operator):
    """Abrir canal de Yoshi Maincra"""
    bl_idname = "universalgta.open_yoshi_channel"
    bl_label = "Open Yoshi Channel"
    bl_description = "Abre el canal de YouTube de Yoshi Maincra"
    
    def execute(self, context):
        try:
            webbrowser.open("https://www.youtube.com/@YoshiMaincra")
            self.report({'INFO'}, "Abriendo canal de Yoshi Maincra...")
        except Exception as e:
            self.report({'ERROR'}, f"Error abriendo navegador: {str(e)}")
        return {'FINISHED'}


class UNIVERSALGTA_PT_CreditsPanel(Panel):
    """Panel de créditos del addon"""
    bl_label = "Credits"
    bl_idname = "UNIVERSALGTA_PT_credits_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        
        # Header del panel de créditos
        box = layout.box()
        box.label(text="Universal GTA SA Converter", icon='ARMATURE_DATA')
        box.label(text="Version 3.2.2", icon='INFO')
        
        layout.separator()
        
        # Crédito principal - Yoshi Maincra (clickeable)
        main_box = layout.box()
        main_box.label(text="Main Developer", icon='USER')
        
        # Botón clickeable para Yoshi Maincra
        yoshi_row = main_box.row()
        yoshi_row.scale_y = 1.2
        op = yoshi_row.operator("universalgta.open_yoshi_channel", 
                               text="🎮 Yoshi Maincra", 
                               icon='URL')
        
        # Roles de Yoshi
        roles_col = main_box.column()
        roles_col.label(text="• Assembler & Project Lead")
        roles_col.label(text="• Code Checker & Logic Design")
        roles_col.label(text="• Original Idea & Concept")
        roles_col.label(text="• Testing & Quality Assurance")
        
        layout.separator()
        
        # Créditos de desarrollo
        dev_box = layout.box()
        dev_box.label(text="Development Team", icon='COMMUNITY')
        
        # Claude
        claude_section = dev_box.box()
        claude_row = claude_section.row()
        claude_row.label(text="🤖 Claude (Anthropic)", icon='SCRIPT')
        claude_col = claude_section.column()
        claude_col.label(text="• Total Python Programming")
        claude_col.label(text="• System Architecture & Engineering")
        claude_col.label(text="• UI/UX Implementation")
        claude_col.label(text="• Advanced Features Development")
        
        # ChatGPT
        chatgpt_section = dev_box.box()
        chatgpt_row = chatgpt_section.row()
        chatgpt_row.label(text="💬 ChatGPT (OpenAI)", icon='CONSOLE')
        chatgpt_col = chatgpt_section.column()
        chatgpt_col.label(text="• Idea Consultant")
        chatgpt_col.label(text="• Code Completions")
        chatgpt_col.label(text="• Syntax Error Debugging")
        chatgpt_col.label(text="• Documentation Support")
        
        layout.separator()
        
        # Características del addon
        features_box = layout.box()
        features_box.label(text="Features", icon='SETTINGS')
        
        feature_col = features_box.column()
        feature_col.label(text="✓ Intelligent Bone Mapping")
        feature_col.label(text="✓ Drag & Drop Interface")
        feature_col.label(text="✓ Auto-Detection System")
        feature_col.label(text="✓ Custom Animations")
        feature_col.label(text="✓ Normal Correction")
        feature_col.label(text="✓ Facial Expressiveness")
        feature_col.label(text="✓ Advanced Cleanup Tools")
        
        layout.separator()
        
        # Información técnica
        tech_box = layout.box()
        tech_box.label(text="Technical Info", icon='TOOL_SETTINGS')
        
        tech_col = tech_box.column()
        tech_col.label(text=f"Blender: {bpy.app.version_string}")
        tech_col.label(text="Python: 3.x Compatible")
        tech_col.label(text="License: Custom")
        tech_col.label(text="Platform: Cross-Platform")
        
        layout.separator()
        
        # Agradecimientos especiales
        thanks_box = layout.box()
        thanks_box.label(text="Special Thanks", icon='HEART')
        
        thanks_col = thanks_box.column()
        thanks_col.label(text="• GTA SA Modding Community")
        thanks_col.label(text="• Blender Foundation")
        thanks_col.label(text="• Beta Testers & Users")
        thanks_col.label(text="• Open Source Contributors")
        
        layout.separator()
        
        # Footer con contacto
        footer_box = layout.box()
        footer_box.label(text="Contact & Support", icon='HELP')
        
        footer_col = footer_box.column()
        footer_col.label(text="Report bugs and suggestions")
        footer_col.label(text="through Yoshi Maincra's channel")
        
        # Información de versión
        layout.separator()
        version_row = layout.row()
        version_row.alignment = 'CENTER'
        version_row.label(text="Made with ❤️ for the GTA SA community")


class UNIVERSALGTA_PT_TestingPanel(Panel):
    """Panel de testing para animaciones y herramientas"""
    bl_label = "Testing"
    bl_idname = "UNIVERSALGTA_PT_testing_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # Sección de animaciones predefinidas
        anim_box = layout.box()
        anim_box.label(text="Predefined Animations", icon='ANIM')
        
        # Selector de animación
        anim_col = anim_box.column()
        anim_col.prop(settings, "predefined_animation", text="Animation")
        
        # Botones de control de animación
        anim_row = anim_box.row()
        anim_row.operator("universalgta.load_animation", text="Load", icon='PLAY')
        anim_row.operator("universalgta.clear_animations", text="Clear", icon='X')
        
        # Advertencia sobre espaciado
        if settings.predefined_animation != 'NONE':
            warning_box = anim_box.box()
            warning_box.label(text="⚠️ Las animaciones se borran al cambiar espaciado", icon='ERROR')
        
        layout.separator()
        
        # Sección de expresividad facial
        facial_box = layout.box()
        facial_box.label(text="Facial Expressiveness", icon='MESH_DATA')
        
        facial_col = facial_box.column()
        facial_col.prop(settings, "facial_expressiveness", text="Overall")
        facial_col.prop(settings, "eyebrow_intensity", text="Eyebrows")
        facial_col.prop(settings, "jaw_expression", text="Jaw")
        
        facial_row = facial_box.row()
        facial_row.operator("universalgta.apply_facial_expressiveness", 
                           text="Apply Facial Expression", 
                           icon='MESH_DATA')
        
        layout.separator()
        
        # Sección de herramientas de testing
        test_box = layout.box()
        test_box.label(text="Testing Tools", icon='TOOL_SETTINGS')
        
        test_col = test_box.column()
        test_col.operator("universalgta.test_bone_mappings", 
                         text="Test Bone Mappings", 
                         icon='CONSTRAINT_BONE')
        test_col.operator("universalgta.clear_test_constraints", 
                         text="Clear Test Constraints", 
                         icon='X')
        test_col.operator("universalgta.preview_conversion", 
                         text="Preview Conversion", 
                         icon='VIEWZOOM')
        
        layout.separator()
        
        # Sección de corrección de normales
        normals_box = layout.box()
        normals_box.label(text="Normal Correction", icon='NORMALS_FACE')
        
        normals_col = normals_box.column()
        normals_col.prop(settings, "auto_fix_normals", text="Auto Fix Normals")
        normals_col.prop(settings, "duplicate_inverted_normals", text="Duplicate Inverted")
        
        normals_row = normals_box.row()
        normals_row.operator("universalgta.fix_normals", text="Fix Normals", icon='NORMALS_FACE')
        normals_row.operator("universalgta.flip_normals", text="Flip", icon='ARROW_LEFTRIGHT')
        
        check_row = normals_box.row()
        check_row.operator("universalgta.check_normals_consistency", 
                          text="Check Normals", 
                          icon='CHECKMARK')


class UNIVERSALGTA_PT_NamingPanel(Panel):
    """Panel para configurar nombres personalizados"""
    bl_label = "Custom Naming"
    bl_idname = "UNIVERSALGTA_PT_naming_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # Información sobre nombres
        info_box = layout.box()
        info_box.label(text="Custom Names Setup", icon='FONT_DATA')
        info_col = info_box.column()
        info_col.label(text="Solo se permiten:")
        info_col.label(text="• Letras (a-z, A-Z)")
        info_col.label(text="• Números (0-9)")
        info_col.label(text="• Guiones (_ -)")
        
        layout.separator()
        
        # Configuración de nombres
        names_box = layout.box()
        names_box.label(text="Name Configuration", icon='OUTLINER_OB_FONT')
        
        names_col = names_box.column()
        names_col.prop(settings, "skin_name", text="Skin Name")
        names_col.prop(settings, "author_nickname", text="Author Nickname")
        
        # Mostrar mensaje de validación si existe
        if settings.name_validation_message:
            validation_box = names_box.box()
            if "❌" in settings.name_validation_message:
                validation_box.alert = True
            validation_box.label(text=settings.name_validation_message)
        
        layout.separator()
        
        # Botones de control
        controls_box = layout.box()
        controls_box.label(text="Name Controls", icon='TOOL_SETTINGS')
        
        controls_row = controls_box.row()
        controls_row.operator("universalgta.validate_names", text="Validate", icon='CHECKMARK')
        controls_row.operator("universalgta.auto_generate_names", text="Auto Gen", icon='AUTO')
        
        apply_row = controls_box.row()
        apply_row.scale_y = 1.2
        apply_row.operator("universalgta.apply_custom_names", 
                          text="Apply Names", 
                          icon='FILE_TICK')
        
        reset_row = controls_box.row()
        reset_row.operator("universalgta.reset_names", text="Reset", icon='LOOP_BACK')
        
        layout.separator()
        
        # Información de aplicación
        usage_box = layout.box()
        usage_box.label(text="What happens when applied:", icon='INFO')
        usage_col = usage_box.column()
        usage_col.label(text="• Skin name → Mesh object name")
        usage_col.label(text="• Author name → Armature name")
        usage_col.label(text="• Author name → Root bone name")
        usage_col.label(text="• Mesh data gets same name")


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_open_yoshi_channel,
    UNIVERSALGTA_PT_CreditsPanel,
    UNIVERSALGTA_PT_TestingPanel,
    UNIVERSALGTA_PT_NamingPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)