"""Panel principal para Universal GTA SA Converter v1.0.
Implementa la interfaz gráfica principal y los paneles secundarios del addon.
"""

import bpy  # type: ignore
import os
from bpy.types import Panel  # type: ignore

# Importar operador de roll de piernas
try:
    from ..operators.leg_roll import UNIVERSALGTA_OT_apply_leg_roll
except ImportError:
    UNIVERSALGTA_OT_apply_leg_roll = None

def safe_operator_button(layout, operator_id, text, icon='NONE', enabled=True):
    """Crea botón de operador solo si está disponible"""
    try:
        # Intentar acceder al operador para ver si existe
        operator_parts = operator_id.split('.')
        if len(operator_parts) == 2:
            namespace, op_name = operator_parts
            if hasattr(bpy.ops, namespace) and hasattr(getattr(bpy.ops, namespace), op_name):
                if enabled:
                    return layout.operator(operator_id, text=text, icon=icon)
                else:
                    row = layout.row()
                    row.enabled = False
                    return row.operator(operator_id, text=text, icon=icon)
            else:
                # Operador no disponible, mostrar botón deshabilitado
                row = layout.row()
                row.enabled = False
                row.label(text=f"{text} (N/A)", icon='ERROR')
                return None
    except Exception as e:
        # Error accediendo al operador
        row = layout.row()
        row.enabled = False
        row.label(text=f"{text} (Error)", icon='ERROR')
        return None

# Cache global para previews de avatares
_avatar_previews = None

def get_avatar_previews():
    """Obtiene o crea la colección de previews de avatares"""
    global _avatar_previews
    if _avatar_previews is None:
        _avatar_previews = bpy.utils.previews.new()
    return _avatar_previews

def get_avatar_icon(avatar_name):
    """Carga y retorna el icon_id de una imagen de avatar"""
    addon_dir = os.path.dirname(os.path.dirname(__file__))
    avatar_path = os.path.join(addon_dir, "avatars", f"{avatar_name}.png")
    
    if not os.path.exists(avatar_path):
        print(f"[AVATAR] No se encuentra: {avatar_path}")
        return 0
    
    try:
        previews = get_avatar_previews()
        preview_key = f"avatar_{avatar_name}"
        
        if preview_key not in previews:
            previews.load(preview_key, avatar_path, 'IMAGE')
        
        if preview_key in previews:
            return previews[preview_key].icon_id
        
        return 0
    except Exception as e:
        print(f"[AVATAR] Error cargando {avatar_name}: {e}")
        import traceback
        traceback.print_exc()
        return 0

def get_blender5_icon(icon_name):
    """Obtener icono compatible con Blender 5.0"""
    icon_mapping = {
        'STAR': 'SOLO_ON',  
        'AUTO': 'AUTO',
        'PLAY': 'PLAY',
        'INFO': 'INFO',
        'ARMATURE_DATA': 'ARMATURE_DATA',
        'CONSTRAINT': 'CONSTRAINT',
        'CHECKMARK': 'CHECKMARK',
        'ERROR': 'ERROR',
        'CANCEL': 'CANCEL',
        'ADD': 'ADD',
        'TRASH': 'TRASH',
        'SETTINGS': 'SETTINGS',
        'DOT': 'DOT',
        'TRIA_UP': 'TRIA_UP',
        'TRIA_DOWN': 'TRIA_DOWN',
        'DUPLICATE': 'DUPLICATE',
        'REMOVE': 'REMOVE',
        'ARROW_LEFTRIGHT': 'ARROW_LEFTRIGHT',
        'FILE_FOLDER': 'FILE_FOLDER',
        'FILE_TICK': 'FILE_TICK',
        'NORMALS_FACE': 'NORMALS_FACE',
        'GROUP_VERTEX': 'GROUP_VERTEX',
        'MODIFIER': 'MODIFIER',
        'MESH_DATA': 'MESH_DATA',
        'EXPORT': 'EXPORT',
        'IMPORT': 'IMPORT',
        'LOOP_BACK': 'LOOP_BACK',
        'URL': 'URL',
        'COMMUNITY': 'COMMUNITY',
        'PRESET_NEW': 'PRESET_NEW',
        'TOOL_SETTINGS': 'TOOL_SETTINGS',
        'NODE_TEXTURE': 'NODE_TEXTURE',
        'IMAGE_DATA': 'IMAGE_DATA',
        'SHADING_RENDERED': 'SHADING_RENDERED',
        'TEXTURE': 'TEXTURE',
        'FILE_REFRESH': 'FILE_REFRESH',
        # Adiciones para uso consistente en este addon
        'USER': 'USER',
        'EDITMODE_HLT': 'EDITMODE_HLT',
        'POSE_HLT': 'POSE_HLT',
        'HELP': 'HELP',
        'HEART': 'HEART',
        'VIEWZOOM': 'VIEWZOOM',
        'SCRIPT': 'SCRIPT',
        'CONSOLE': 'CONSOLE',
        'X': 'X'
    }
    return icon_mapping.get(icon_name, 'NONE')

class UNIVERSALGTA_PT_MainPanel(Panel):
    """Panel principal con Quick Workflow"""
    bl_label = "Universal GTA Converter v1.0"
    bl_idname = "UNIVERSALGTA_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        info_box = layout.box()
        info_box.label(text="Universal GTA SA Converter", icon=get_blender5_icon('ARMATURE_DATA'))
        info_box.label(text="v1.0", icon=get_blender5_icon('INFO'))
        
        layout.separator()
        setup_box = layout.box()
        setup_box.label(text="Setup", icon=get_blender5_icon('SETTINGS'))
        
        setup_col = setup_box.column()
        setup_col.prop(settings, "source_armature", text="Your Character Armature")
        setup_col.prop(settings, "target_armature", text="GTA SA (Root)")
        
        layout.separator()
        workflow_box = layout.box()
        workflow_box.label(text="Quick Workflow", icon=get_blender5_icon('PLAY'))
        
        step1_col = workflow_box.column()
        step1_col.scale_y = 1.6
        step1_col.operator("universalgta.smart_auto_detect", 
                          text="🧠 1. Smart Auto-Detect", 
                          icon=get_blender5_icon('AUTO'))
        
        step2_col = workflow_box.column() 
        step2_col.scale_y = 1.4
        step2_col.operator("universalgta.execute_conversion", 
                          text="🚀 2. Convert to GTA SA", 
                          icon=get_blender5_icon('PLAY'))

        layout.separator()
        preserve_box = layout.box()
        preserve_box.scale_y = 0.8
        preserve_row = preserve_box.row()
        preserve_row.prop(settings, "preserve_vertex_data", 
             text="☑️ Preservar Vertex Colors / Atributos")
        raster_row = preserve_box.row()
        raster_row.prop(settings, "rasterize_textures", text="Limpiar materiales")
        clean_row = preserve_box.row()
        clean_row.prop(settings, "clean_materials", text="Rasterizar texturas RVA")

class UNIVERSALGTA_PT_AdvancedMappingPanel(Panel):
    """Panel de mapeo avanzado"""
    bl_label = "Advanced Mapping"
    bl_idname = "UNIVERSALGTA_PT_advanced_mapping_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        io_box = layout.box()
        io_box.label(text="💾 Mapping I/O", icon=get_blender5_icon('FILE_FOLDER'))
        
        io_row = io_box.row()
        io_row.operator("universalgta.load_mapping", 
                       text="Load", icon=get_blender5_icon('FILE_FOLDER'))
        io_row.operator("universalgta.save_mapping", 
                       text="Save", icon=get_blender5_icon('FILE_TICK'))
        
        layout.separator()
        self.draw_mapping_operations(layout, context, settings)
        
        layout.separator()
        validation_box = layout.box()
        validation_box.label(text="✅ Validation Tools", icon=get_blender5_icon('CHECKMARK'))
        
        validation_row = validation_box.row()
        validation_row.operator("universalgta.validate_mappings", 
                               text="Full Validation", icon=get_blender5_icon('CHECKMARK'))
        validation_row.operator("universalgta.enable_only_valid_mappings", 
                               text="Valid Only", icon=get_blender5_icon('STAR'))
        
        layout.separator()
        self.draw_bone_mappings_section(layout, context, settings)

    def draw_mapping_operations(self, layout, context, settings):
        """Dibujar operaciones de mapeo"""
        ops_box = layout.box()
        ops_box.label(text="🔧 Mapping Operations", icon=get_blender5_icon('TOOL_SETTINGS'))
        
        spacer_row = ops_box.row()
        spacer_row.scale_y = 0.6
        spacer_row.label(text="")
        
        # Operaciones adicionales
        clear_row = ops_box.row()
        clear_row.operator("universalgta.clear_mappings", 
                          text="Clear All", icon=get_blender5_icon('TRASH'))
        clear_row.operator("universalgta.add_custom_entry", 
                          text="Add Custom", icon=get_blender5_icon('ADD'))

    def draw_bone_mappings_section(self, layout, context, settings):
        """Dibujar sección completa de bone mappings"""
        mapping_box = layout.box()
        
        header_row = mapping_box.row()
        header_row.label(text="Bone Mappings", icon=get_blender5_icon('ARMATURE_DATA'))
        
        if len(settings.bone_mappings) > 0:
            enabled_count = sum(1 for m in settings.bone_mappings if m.enabled)
            valid_count = 0
            
            # Contar mapeos validos
            for mapping in settings.bone_mappings:
                is_valid, _ = self.is_mapping_valid(mapping, settings)
                if is_valid:
                    valid_count += 1
            
            header_row.label(text=f"({enabled_count}/{len(settings.bone_mappings)})")
            
            if valid_count == enabled_count and enabled_count > 0:
                header_row.label(text="", icon=get_blender5_icon('CHECKMARK'))
            elif valid_count > 0:
                header_row.label(text="", icon=get_blender5_icon('INFO'))
            else:
                header_row.label(text="", icon=get_blender5_icon('CANCEL'))
        
        if len(settings.bone_mappings) > 0:
            row = mapping_box.row()
            row.template_list("UNIVERSALGTA_UL_BoneMappingList", "",
                            settings, "bone_mappings",
                            settings, "bone_mappings_index",
                            rows=6)
            
            col = row.column(align=True)
            col.operator("universalgta.move_mapping_up", text="", icon=get_blender5_icon('TRIA_UP'))
            col.operator("universalgta.move_mapping_down", text="", icon=get_blender5_icon('TRIA_DOWN'))
            col.separator()
            col.operator("universalgta.add_custom_entry", text="", icon=get_blender5_icon('ADD'))
            col.operator("universalgta.remove_mapping_entry", text="", icon=get_blender5_icon('REMOVE'))
            col.separator()
            col.operator("universalgta.duplicate_mapping", text="", icon=get_blender5_icon('DUPLICATE'))
            
            if 0 <= settings.bone_mappings_index < len(settings.bone_mappings):
                item = settings.bone_mappings[settings.bone_mappings_index]
                
                edit_box = layout.box()
                
                header_row = edit_box.row()
                header_row.label(text=f"Edit #{settings.bone_mappings_index + 1}", icon=get_blender5_icon('SETTINGS'))
                header_row.prop(item, "enabled", text="Enabled")
                
                if "Smart Auto" in item.detection_method:
                    method_row = edit_box.row()
                    method_row.label(text=f"🧠 {item.detection_method}", icon=get_blender5_icon('AUTO'))
                    if item.confidence > 0:
                        method_row.label(text=f"Confidence: {item.confidence:.1%}")
                
                bones_row = edit_box.row()
                
                source_col = bones_row.column()
                source_col.label(text="Source Bone")
                if settings.source_armature:
                    source_col.prop_search(item, "source_bone", 
                                         settings.source_armature.pose, "bones", 
                                         text="", icon=get_blender5_icon('ARMATURE_DATA'))
                else:
                    source_col.prop(item, "source_bone", text="")
                
                target_col = bones_row.column()
                target_col.label(text="Target Bone")
                if settings.target_armature:
                    target_col.prop_search(item, "target_bone", 
                                         settings.target_armature.pose, "bones", 
                                         text="", icon=get_blender5_icon('ARMATURE_DATA'))
                else:
                    target_col.prop(item, "target_bone", text="")
                
                is_valid, reason = self.is_mapping_valid(item, settings)
                status_row = edit_box.row()
                if is_valid:
                    status_row.label(text="✅ Valid mapping", icon=get_blender5_icon('CHECKMARK'))
                else:
                    status_row.alert = True
                    status_row.label(text=f"❌ {reason}", icon=get_blender5_icon('ERROR'))
        else:
            no_mappings_row = mapping_box.row()
            no_mappings_row.alert = True
            no_mappings_row.label(text="⚠ No mappings configured", icon=get_blender5_icon('ERROR'))
            
            help_row = mapping_box.row()
            if settings.source_armature and settings.target_armature:
                help_row.label(text="👆 Try '🧠 Smart Auto-Detect'")
            else:
                help_row.label(text="⚠ Select armatures above first")

    def is_mapping_valid(self, mapping, settings):
        """Validar un mapeo individual"""
        if not mapping.enabled:
            return False, "disabled"
        
        if not mapping.source_bone or not mapping.target_bone:
            return False, "empty bones"
        
        if not settings.source_armature or not settings.target_armature:
            return False, "no armatures"
        
        try:
            source_exists = mapping.source_bone in [b.name for b in settings.source_armature.pose.bones]
            target_exists = mapping.target_bone in [b.name for b in settings.target_armature.pose.bones]
            
            if not source_exists:
                return False, "source bone not found"
            if not target_exists:
                return False, "target bone not found"
            
            return True, "valid"
        except:
            return False, "error checking bones"

class UNIVERSALGTA_PT_QuickActionsPanel(Panel):
    """Panel de acciones rápidas"""
    bl_label = "Quick Actions"
    bl_idname = "UNIVERSALGTA_PT_quick_actions_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings

        essential_box = layout.box()
        essential_box.label(text="⚡ Essential Actions", icon=get_blender5_icon('SETTINGS'))

        validate_row = essential_box.row()
        validate_row.scale_y = 1.2
        safe_operator_button(validate_row, "universalgta.validate_mappings_and_disable_invalid", 
                           "🔍 Validate Mappings", get_blender5_icon('CHECKMARK'))

        layout.separator()
        edit_box = layout.box()
        edit_box.label(text="⚡ Roll Angles (Edit Mode)", icon=get_blender5_icon('EDITMODE_HLT'))

        arms_box = edit_box.box()
        arms_box.label(text="Upper Arms Roll Angle")
        arms_box.prop(context.scene, "gta_arm_angle", text="Arm-Stretching")
        apply_row = arms_box.row()
        apply_row.scale_y = 1.2
        apply_row.operator("universalgta.set_arm_angles", text="Apply Arm Roll", icon=get_blender5_icon('CHECKMARK'))

        legs_box = edit_box.box()
        legs_box.label(text="Upper Legs Roll Angle")
        legs_box.prop(context.scene, "gta_leg_roll_angle", text="Leg-Stretching")
        leg_apply_row = legs_box.row()
        leg_apply_row.scale_y = 1.2
        leg_apply_row.operator("universalgta.apply_leg_roll", text="Apply Leg Roll", icon=get_blender5_icon('CHECKMARK'))

        layout.separator()
        pose_box = layout.box()
        pose_box.label(text="🤸 Pose Actions", icon=get_blender5_icon('POSE_HLT'))

        pose_row = pose_box.row()
        pose_row.operator("universalgta.apply_custom_pose", 
                         text="Apply Custom Pose", icon=get_blender5_icon('CONSTRAINT'))
        pose_row.operator("universalgta.reset_pose", 
                         text="Reset", icon=get_blender5_icon('LOOP_BACK'))

        layout.separator()
        height_box = layout.box()
        height_box.label(text="Ajuste de Altura del Skin", icon=get_blender5_icon('MESH_DATA'))
        height_row = height_box.row()
        height_row.prop(context.scene, 'gta_skin_height', text='Altura (m)')
        apply_row = height_box.row()
        apply_row.scale_y = 1.2
        safe_operator_button(apply_row, 'universalgta.adjust_skin_height', text='Apply Height', icon=get_blender5_icon('ARROW_LEFTRIGHT'))


class UNIVERSALGTA_PT_NameAuthorPanel(Panel):
    bl_label = "Character Name & Author"
    bl_idname = "UNIVERSALGTA_PT_name_author_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    # Panel independiente, sin bl_parent_id
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        box = layout.box()
        box.label(text="Set Character Name & Author", icon=get_blender5_icon('USER'))
        box.prop(settings, "skin_name", text="Character Name")
        box.prop(settings, "author_nickname", text="Author")
        if settings.name_validation_message:
            box.label(text=settings.name_validation_message, icon='ERROR')
        box.operator("universalgta.apply_custom_names", text="Apply Names", icon=get_blender5_icon('CHECKMARK'))

class UNIVERSALGTA_PT_UtilitiesPanel(Panel):
    """Panel de utilidades y limpieza"""
    bl_label = "Utilities & Cleanup"
    bl_idname = "UNIVERSALGTA_PT_utilities_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        texture_box = layout.box()
        texture_box.label(text="🎨 Texture Tools", icon=get_blender5_icon('NODE_TEXTURE'))
        
        tex_row1 = texture_box.row()
        tex_row1.operator("universalgta.export_textures_with_browser", 
                         text="📁 Export Textures (Browse)", 
                         icon=get_blender5_icon('EXPORT'))
        
        tex_row2 = texture_box.row()
        tex_row2.operator("universalgta.quick_texture_export", 
                         text="⚡ Quick Export to /textures", 
                         icon=get_blender5_icon('FILE_REFRESH'))
        
        tex_row3 = texture_box.row()
        tex_row3.operator("universalgta.export_textures_enhanced", 
                         text="Export + Smart Processing", 
                         icon=get_blender5_icon('PRESET_NEW'))
        
        tex_row4 = texture_box.row()
        tex_row4.operator("universalgta.quick_material_rgb_fix", 
                         text="Quick RGB Fix", 
                         icon=get_blender5_icon('AUTO'))
        
        tex_row5 = texture_box.row()
        tex_row5.scale_y = 1.3
        tex_row5.operator("universalgta.manual_smart_baking", 
                         text="🔥 Smart Baking", 
                         icon=get_blender5_icon('SHADING_RENDERED'))
        
        # Info sobre las nuevas funciones
        info_box = texture_box.box()
        info_box.scale_y = 0.8
        info_col = info_box.column()
        info_col.label(text="✅ Sistema avanzado de baking")
        info_col.label(text="✅ Preservación de colores RGB/HEX")
        info_col.label(text="✅ Detección automática de resolución")
        info_col.label(text="✅ Soporte para Vector + Image + HSV")

class UNIVERSALGTA_PT_InfoPanel(Panel):
    """Panel de información y créditos"""
    bl_label = "Info"
    bl_idname = "UNIVERSALGTA_PT_info_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        info_box = layout.box()
        info_box.label(text="Universal GTA Converter v1.0", icon=get_blender5_icon('INFO'))
        info_col = info_box.column()
        info_col.scale_y = 0.8
        info_col.label(text="🧠 Smart Auto-Detect for:")
        info_col.label(text="• Mixamo, Source/SFM, ValveBiped, AvatarSDK")

        layout.separator()
        credits_box = layout.box()
        credits_box.label(text="Credits", icon=get_blender5_icon('USER'))
        
        yoshi_box = credits_box.box()
        yoshi_box.label(text="Main Developer", icon=get_blender5_icon('USER'))
        yoshi_header = yoshi_box.row()
        
        yoshi_icon = get_avatar_icon("yoshi")
        icon_col = yoshi_header.column()
        if yoshi_icon:
            icon_col.label(text="", icon_value=yoshi_icon)
        else:
            icon_col.label(text="", icon='OUTLINER_OB_IMAGE')
        
        yoshi_info = yoshi_header.column()
        yoshi_info.scale_y = 1.4
        yoshi_info.label(text="Yoshi Maincra")
        yoshi_info.separator(factor=0.5)
        yoshi_info.operator("universalgta.open_yoshi_channel", 
                           text="Abrir Canal de YouTube", 
                           icon=get_blender5_icon('URL'))
        yoshi_col = yoshi_box.column()
        yoshi_col.scale_y = 0.9
        yoshi_col.label(text="• Assembler & Project Lead")
        yoshi_col.label(text="• Code Checker & Logic Design")
        yoshi_col.label(text="• Original Idea & Concept")
        yoshi_col.label(text="• Testing & Quality Assurance")

        dev_box = credits_box.box()
        dev_box.label(text="Development Team", icon=get_blender5_icon('COMMUNITY'))
        cursor_section = dev_box.box()
        cursor_row = cursor_section.row()
        cursor_row.label(text="", icon='CONSOLE')
        cursor_row.label(text="Cursor AI")
        cursor_col = cursor_section.column()
        cursor_col.scale_y = 0.9
        cursor_col.label(text="• AI-Powered Code Development")
        cursor_col.label(text="• System Architecture & Engineering")
        cursor_col.label(text="• UI/UX Implementation")
        cursor_col.label(text="• Advanced Features Development")
        
        beta_box = credits_box.box()
        beta_box.label(text="Beta Testers", icon=get_blender5_icon('COMMUNITY'))
        lenx_row = beta_box.row()
        lenx_icon = get_avatar_icon("lenx")
        lenx_icon_col = lenx_row.column()
        if lenx_icon:
            lenx_icon_col.label(text="", icon_value=lenx_icon)
        else:
            lenx_icon_col.label(text="", icon='OUTLINER_OB_IMAGE')
        lenx_row.label(text="LenX")
        nyxxy_row = beta_box.row()
        nyxxy_icon = get_avatar_icon("nyxxy")
        nyxxy_icon_col = nyxxy_row.column()
        if nyxxy_icon:
            nyxxy_icon_col.label(text="", icon_value=nyxxy_icon)
        else:
            nyxxy_icon_col.label(text="", icon='OUTLINER_OB_IMAGE')
        nyxxy_row.label(text="NyxxyGirl")

        layout.separator()
        tech_box = layout.box()
        tech_box.label(text="Technical Info", icon=get_blender5_icon('SETTINGS'))
        tech_col = tech_box.column()
        tech_col.scale_y = 0.9
        tech_col.label(text=f"Blender: {bpy.app.version_string}")
        tech_col.label(text="Python: 3.x Compatible")
        tech_col.label(text="Compatible: Blender 4.5+ & 5.0")

        layout.separator()
        thanks_box = layout.box()
        thanks_box.label(text="Special Thanks", icon=get_blender5_icon('HEART'))
        thanks_col = thanks_box.column()
        thanks_col.scale_y = 0.9
        thanks_col.label(text="• GTA SA Modding Community")
        thanks_col.label(text="• Suscribers")

        layout.separator()
        footer_box = layout.box()
        footer_box.label(text="Contact & Support", icon=get_blender5_icon('HELP'))
        footer_col = footer_box.column()
        footer_col.label(text="Report bugs and suggestions")
        footer_col.label(text="through Yoshi Maincra's channel")
        layout.separator()
        version_row = layout.row()
        version_row.alignment = 'CENTER'
        version_row.label(text="Made with ❤️ for the GTA SA community")


classes = [
    UNIVERSALGTA_PT_MainPanel,
    UNIVERSALGTA_PT_AdvancedMappingPanel,
    UNIVERSALGTA_PT_QuickActionsPanel,
    UNIVERSALGTA_PT_NameAuthorPanel,
    UNIVERSALGTA_PT_UtilitiesPanel,
    UNIVERSALGTA_PT_InfoPanel,
    UNIVERSALGTA_OT_apply_leg_roll,
]

def register():
    """Registrar paneles principales"""
    for cls in classes:
        bpy.utils.register_class(cls)
    print("[PANELS] Paneles principales v2 ORDEN CORRECTO registrados")

def unregister():
    """Desregistrar paneles principales"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("[PANELS] Paneles principales v2 desregistrados")
