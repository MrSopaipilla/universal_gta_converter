"""Panel de créditos para Universal GTA SA Converter."""

import bpy  # type: ignore
import os
import webbrowser
from bpy.types import Panel, Operator  # type: ignore


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
            print(f"[AVATAR] Cargado: {avatar_name} desde {avatar_path}")
        
        if preview_key in previews:
            icon_id = previews[preview_key].icon_id
            if icon_id:
                print(f"[AVATAR] Icon ID obtenido para {avatar_name}: {icon_id}")
            return icon_id
        
        print(f"[AVATAR] Preview no generado para {avatar_name}")
        return 0
    except Exception as e:
        print(f"[AVATAR] Error cargando {avatar_name}: {e}")
        import traceback
        traceback.print_exc()
        return 0


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
        
        header_box = layout.box()
        header_row = header_box.row()
        header_row.label(text="Universal GTA SA Converter", icon='ARMATURE_DATA')
        header_box.label(text="Version 1.0", icon='INFO')
        
        layout.separator()
        
        main_box = layout.box()
        main_box.label(text="Main Developer", icon='USER')
        
        yoshi_header = main_box.row()
        
        yoshi_icon = get_avatar_icon("yoshi")
        icon_col = yoshi_header.column()
        for _ in range(3):
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
                           icon='URL')
        
        roles_col = main_box.column()
        roles_col.scale_y = 0.9
        roles_col.label(text="• Assembler & Project Lead")
        roles_col.label(text="• Code Checker & Logic Design")
        roles_col.label(text="• Original Idea & Concept")
        roles_col.label(text="• Testing & Quality Assurance")
        
        layout.separator()
        
        dev_box = layout.box()
        dev_box.label(text="Development Team", icon='COMMUNITY')
        
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
        
        layout.separator()
        
        beta_box = layout.box()
        beta_box.label(text="Beta Testers", icon='COMMUNITY')
        
        lenx_row = beta_box.row()
        lenx_icon = get_avatar_icon("lenx")
        lenx_icon_col = lenx_row.column()
        for _ in range(2):
            if lenx_icon:
                lenx_icon_col.label(text="", icon_value=lenx_icon)
            else:
                lenx_icon_col.label(text="", icon='OUTLINER_OB_IMAGE')
        lenx_row.label(text="LenX")
        
        nyxxy_row = beta_box.row()
        nyxxy_icon = get_avatar_icon("nyxxy")
        nyxxy_icon_col = nyxxy_row.column()
        for _ in range(2):
            if nyxxy_icon:
                nyxxy_icon_col.label(text="", icon_value=nyxxy_icon)
            else:
                nyxxy_icon_col.label(text="", icon='OUTLINER_OB_IMAGE')
        nyxxy_row.label(text="NyxxyGirl")
        
        layout.separator()
        
        tech_box = layout.box()
        tech_box.label(text="Technical Info", icon='SETTINGS')
        tech_col = tech_box.column()
        tech_col.scale_y = 0.9
        tech_col.label(text=f"Blender: {bpy.app.version_string}")
        tech_col.label(text="Python: 3.x Compatible")
        tech_col.label(text="Compatible: Blender 5.0 & 5.0.1 (Recommended)")
        
        layout.separator()
        
        thanks_box = layout.box()
        thanks_box.label(text="Special Thanks", icon='HEART')
        thanks_col = thanks_box.column()
        thanks_col.scale_y = 0.9
        thanks_col.label(text="• GTA SA Modding Community")
        thanks_col.label(text="• Suscribers")
        
        layout.separator()
        
        footer_box = layout.box()
        footer_box.label(text="Contact & Support", icon='HELP')
        footer_col = footer_box.column()
        footer_col.scale_y = 0.9
        footer_col.label(text="Report bugs and suggestions")
        footer_col.label(text="through Yoshi Maincra's channel")
        
        layout.separator()
        version_row = layout.row()
        version_row.alignment = 'CENTER'
        version_row.label(text="Made with ❤️ for the GTA SA community")




# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_open_yoshi_channel,
    UNIVERSALGTA_PT_CreditsPanel,
]


def register():
    """Registra todos los paneles de créditos"""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Desregistra todos los paneles de créditos"""
    global _avatar_previews
    if _avatar_previews:
        bpy.utils.previews.remove(_avatar_previews)
        _avatar_previews = None
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)