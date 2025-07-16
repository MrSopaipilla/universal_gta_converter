"""
Panel principal para el addon Universal GTA Converter
VERSIÓN COMPLETA CORREGIDA PARA BLENDER 5.0 - Sin Bone Mapping Panel
"""

import bpy
from bpy.types import Panel


class UNIVERSALGTA_PT_MainPanel(Panel):
    """Panel principal del Universal GTA Converter"""
    bl_label = "Universal GTA Converter"
    bl_idname = "UNIVERSALGTA_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # Header con información del addon
        box = layout.box()
        row = box.row()
        row.label(text="Universal to GTA SA Converter", icon='ARMATURE_DATA')
        row = box.row()
        row.label(text="v3.2.5 - YoshiMaincra + AI", icon='INFO')
        
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
        
        # Botón para aplicar pose manualmente
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


class UNIVERSALGTA_PT_ConversionPanel(Panel):
    """Panel para ejecutar la conversión"""
    bl_label = "Conversion"
    bl_idname = "UNIVERSALGTA_PT_ConversionPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_parent_id = "UNIVERSALGTA_PT_MainPanel"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # Botón principal de conversión
        box = layout.box()
        box.label(text="Convert to GTA SA", icon='ARMATURE_DATA')
        
        # Opciones de conversión
        col = box.column()
        col.prop(settings, "keep_vertex_colors", text="Mantener Vertex Colors")
        
        # Botón de conversión principal
        col.separator()
        col.scale_y = 1.5
        col.operator("universalgta.execute_conversion", text="Convert to GTA SA", icon='PLAY')
        
        # Información y ayuda
        layout.separator()
        info_box = layout.box()
        info_box.label(text="Información", icon='INFO')
        info_col = info_box.column()
        info_col.label(text="Universal GTA Converter v3.2.5", icon='ARMATURE_DATA')
        info_col.label(text="Convierte rigs personalizados a formato GTA SA")
        info_col.label(text="con detección inteligente de huesos")
        info_col.separator()
        info_col.label(text="Uso:")
        info_col.label(text="1. Configurar armatures fuente y destino")
        info_col.label(text="2. Configurar mapeo de huesos")
        info_col.label(text="3. Ejecutar conversión")
        info_col.label(text="4. Limpiar si es necesario")
        info_col.separator()
        info_col.label(text="Características:")
        info_col.label(text="• Mapeo individual de huesos con dropdowns")
        info_col.label(text="• Auto-detección inteligente")
        info_col.label(text="• Validación en tiempo real")
        info_col.label(text="• Aplicación de pose personalizada")
        info_col.label(text="• Herramientas de limpieza avanzadas")
        info_col.label(text="• Animaciones Fat/Muscle/Talk/Facial")


class UNIVERSALGTA_PT_UtilitiesPanel(Panel):
    """Panel de utilidades y herramientas de limpieza"""
    bl_label = "Utilidades"
    bl_idname = "UNIVERSALGTA_PT_UtilitiesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_parent_id = "UNIVERSALGTA_PT_MainPanel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        
        # Herramientas de limpieza
        box = layout.box()
        box.label(text="Cleanup Tools", icon='BRUSH_DATA')
        
        col = box.column()
        
        # Primera fila
        row = col.row()
        row.operator("universalgta.clean_model", text="Clean Model", icon='MESH_DATA')
        row.operator("universalgta.clean_armatures", text="Clean Armatures", icon='ARMATURE_DATA')
        
        # Segunda fila
        row = col.row()
        row.operator("universalgta.clean_empty_vertex_groups", text="Clean Vertex Groups", icon='GROUP_VERTEX')
        row.operator("universalgta.fix_modifiers", text="Fix Modifiers", icon='MODIFIER')
        
        # Tercera fila
        row = col.row()
        row.operator("universalgta.remove_duplicates", text="Remove Duplicates", icon='DUPLICATE')
        row.operator("universalgta.optimize_mesh", text="Optimize Mesh", icon='MESH_ICOSPHERE')
        
        # Cuarta fila
        row = col.row()
        row.operator("universalgta.purge_unused_data", text="Purge Unused Data", icon='TRASH')
        row.operator("universalgta.purge_scene", text="Purge Scene", icon='SCENE_DATA')
        
        # Herramientas de exportación
        layout.separator()
        export_box = layout.box()
        export_box.label(text="Export Tools", icon='EXPORT')
        
        col = export_box.column()
        col.operator("universalgta.export_textures", text="Export Textures", icon='TEXTURE')


# Lista de clases para registro
classes = [
    UNIVERSALGTA_PT_MainPanel,
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