# =============================================================================
# ENHANCED BONE MAPPING SYSTEM v3.2.3 - ESTRUCTURA COMPLETA
# =============================================================================
# 
# INSTRUCCIONES DE INSTALACIÓN:
# 1. Crear la estructura de carpetas en tu addon
# 2. Copiar cada archivo según los comentarios indicados
# 3. Modificar __init__.py con el código de integración
# 4. Reiniciar Blender y activar el addon
#
# =============================================================================

# =============================================================================
# ARCHIVO: enhanced_config.py (RAÍZ DEL ADDON)
# =============================================================================

"""
Enhanced Configuration - Extensión del archivo config.py existente
Propiedades adicionales para el sistema Enhanced Bone Mapping
"""
from bpy.props import (
    StringProperty, BoolProperty, FloatProperty, IntProperty, 
    EnumProperty, PointerProperty, CollectionProperty, FloatVectorProperty
)
from bpy.types import PropertyGroup


class EnhancedMappingTemplate(PropertyGroup):
    """Template de mapeos predefinidos"""
    name: StringProperty(
        name="Template Name",
        description="Nombre del template de mapeo",
        default="Unnamed Template"
    )
    
    description: StringProperty(
        name="Description",
        description="Descripción del template",
        default=""
    )
    
    source_armature_type: EnumProperty(
        name="Source Type",
        description="Tipo de armature origen",
        items=[
            ('MIXAMO', "Mixamo", "Armature de Mixamo"),
            ('RIGIFY', "Rigify", "Armature de Rigify"),
            ('MAKEHUMAN', "MakeHuman", "Armature de MakeHuman"),
            ('CUSTOM', "Custom", "Armature personalizado"),
            ('GENERIC', "Generic", "Armature genérico")
        ],
        default='GENERIC'
    )
    
    target_armature_type: EnumProperty(
        name="Target Type", 
        description="Tipo de armature destino",
        items=[
            ('GTA_SA', "GTA SA", "Armature de GTA San Andreas"),
            ('GTA_IV', "GTA IV", "Armature de GTA IV"),
            ('CUSTOM', "Custom", "Armature personalizado")
        ],
        default='GTA_SA'
    )
    
    template_data: StringProperty(
        name="Template Data",
        description="Datos del template en formato JSON",
        default=""
    )
    
    confidence_threshold: FloatProperty(
        name="Confidence Threshold",
        description="Umbral de confianza mínimo para este template",
        default=0.7,
        min=0.0,
        max=1.0
    )
    
    created_date: StringProperty(
        name="Created Date",
        description="Fecha de creación del template",
        default=""
    )


class EnhancedVisualizationSettings(PropertyGroup):
    """Configuración avanzada de visualización"""
    
    connection_line_width: FloatProperty(
        name="Line Width",
        description="Grosor de las líneas de conexión",
        default=2.0,
        min=0.5,
        max=10.0
    )
    
    connection_line_color: FloatVectorProperty(
        name="Line Color",
        description="Color de las líneas de conexión",
        subtype='COLOR',
        default=(0.0, 1.0, 0.0, 1.0),
        size=4,
        min=0.0,
        max=1.0
    )
    
    highlight_active_mapping: BoolProperty(
        name="Highlight Active",
        description="Resaltar el mapeo actualmente seleccionado",
        default=True
    )
    
    show_bone_names_3d: BoolProperty(
        name="Show Bone Names in 3D",
        description="Mostrar nombres de huesos en el viewport 3D",
        default=False
    )
    
    auto_zoom_to_bones: BoolProperty(
        name="Auto Zoom to Bones",
        description="Hacer zoom automático a los huesos seleccionados",
        default=False
    )
    
    highlight_color_source: FloatVectorProperty(
        name="Source Highlight Color",
        description="Color de highlight para huesos origen",
        subtype='COLOR', 
        default=(0.0, 0.0, 1.0, 0.8),
        size=4,
        min=0.0,
        max=1.0
    )
    
    highlight_color_target: FloatVectorProperty(
        name="Target Highlight Color", 
        description="Color de highlight para huesos destino",
        subtype='COLOR',
        default=(1.0, 0.0, 0.0, 0.8),
        size=4,
        min=0.0,
        max=1.0
    )
    
    preview_constraint_influence: FloatProperty(
        name="Preview Influence",
        description="Influencia de los constraints de preview",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    preview_duration: FloatProperty(
        name="Preview Duration",
        description="Duración del preview en segundos",
        default=3.0,
        min=0.5,
        max=10.0
    )


class EnhancedAutoMappingSettings(PropertyGroup):
    """Configuración avanzada de mapeo automático"""
    
    use_name_similarity: BoolProperty(
        name="Name Similarity",
        description="Usar similitud de nombres para mapeo automático",
        default=True
    )
    
    use_hierarchy_analysis: BoolProperty(
        name="Hierarchy Analysis",
        description="Usar análisis de jerarquía para mapeo automático",
        default=True
    )
    
    use_bone_length_comparison: BoolProperty(
        name="Bone Length Comparison",
        description="Comparar longitudes de huesos para mapeo",
        default=False
    )
    
    use_position_analysis: BoolProperty(
        name="Position Analysis", 
        description="Analizar posiciones relativas de huesos",
        default=False
    )
    
    name_similarity_weight: FloatProperty(
        name="Name Weight",
        description="Peso de la similitud de nombres",
        default=0.6,
        min=0.0,
        max=1.0
    )
    
    hierarchy_weight: FloatProperty(
        name="Hierarchy Weight",
        description="Peso del análisis de jerarquía",
        default=0.3,
        min=0.0,
        max=1.0
    )
    
    position_weight: FloatProperty(
        name="Position Weight",
        description="Peso del análisis de posición",
        default=0.1,
        min=0.0,
        max=1.0
    )
    
    ignore_case: BoolProperty(
        name="Ignore Case",
        description="Ignorar mayúsculas/minúsculas en nombres",
        default=True
    )
    
    ignore_separators: BoolProperty(
        name="Ignore Separators",
        description="Ignorar separadores (_, -, espacios) en nombres",
        default=True
    )
    
    use_fuzzy_matching: BoolProperty(
        name="Fuzzy Matching",
        description="Usar coincidencia difusa para nombres",
        default=True
    )
    
    min_bone_length: FloatProperty(
        name="Min Bone Length",
        description="Longitud mínima de hueso para considerar",
        default=0.001,
        min=0.0,
        max=1.0
    )
    
    exclude_helper_bones: BoolProperty(
        name="Exclude Helper Bones",
        description="Excluir huesos auxiliares (ik, pole, etc.)",
        default=True
    )
    
    helper_bone_patterns: StringProperty(
        name="Helper Patterns",
        description="Patrones de nombres para huesos auxiliares (separados por coma)",
        default="ik,pole,target,ctrl,control,helper"
    )


class EnhancedPerformanceSettings(PropertyGroup):
    """Configuración de rendimiento y optimización"""
    
    auto_update_frequency: EnumProperty(
        name="Update Frequency",
        description="Frecuencia de actualización automática",
        items=[
            ('REALTIME', "Real-time", "Actualización en tiempo real"),
            ('ON_CHANGE', "On Change", "Actualizar al cambiar"),
            ('MANUAL', "Manual", "Actualización manual únicamente")
        ],
        default='ON_CHANGE'
    )
    
    max_preview_bones: IntProperty(
        name="Max Preview Bones",
        description="Máximo número de huesos para preview simultáneo",
        default=20,
        min=1,
        max=100
    )
    
    enable_background_processing: BoolProperty(
        name="Background Processing",
        description="Procesar mapeos automáticos en segundo plano",
        default=False
    )
    
    cache_similarity_results: BoolProperty(
        name="Cache Results",
        description="Cachear resultados de similitud para mejor rendimiento",
        default=True
    )
    
    max_undo_steps: IntProperty(
        name="Max Undo Steps",
        description="Máximo número de pasos de deshacer",
        default=10,
        min=1,
        max=50
    )
    
    cleanup_temp_objects: BoolProperty(
        name="Auto Cleanup",
        description="Limpiar automáticamente objetos temporales",
        default=True
    )


def extend_universal_gta_settings():
    """Extiende la clase UniversalGTASettings con propiedades enhanced"""
    
    if not hasattr(bpy.types, 'UniversalGTASettings'):
        pass
    settings_class = bpy.types.UniversalGTASettings
    try:
        pass
    except Exception as e:
        pass

def register_enhanced_properties():
    """Registra todas las property groups enhanced"""
    try:
        pass
    except Exception as e:
        pass

def unregister_enhanced_properties():
    """Desregistra todas las property groups enhanced"""
    try:
        pass
    except Exception as e:
        pass

def validate_enhanced_config(context):
    """Valida que la configuración enhanced esté correctamente instalada"""
    if not hasattr(context.scene, 'universal_gta_settings'):
        pass
    settings = context.scene.universal_gta_settings
    required_props = [
        'source_bones_index', 'target_bones_index',
        'auto_update_visualization', 'enhanced_mode_enabled'
    ]
    missing_props = []
    for prop in required_props:
        pass
    if missing_props:
        pass
    return

def get_enhanced_config_info(context):
    """Obtiene información sobre el estado de la configuración enhanced"""
    info = {
        'enhanced_available': False,
        'property_groups_loaded': [],
        'missing_properties': [],
        'version': '1.0'
    }
    if hasattr(context.scene, 'universal_gta_settings'):
        pass
    return info

if __name__ == "__main__":
    register_enhanced_properties()
