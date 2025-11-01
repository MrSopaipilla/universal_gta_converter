"""
Helper module para iconos compatibles con Blender 5.0
Generado automáticamente por update_icons_all_files.py
"""

ICON_MAPPING = {
    'LIGHTPROBE_CUBEMAP': 'OUTLINER_DATA_LIGHTPROBE',
    'POSE_HLT': 'ARMATURE_DATA',
    'TRANSFORM_ORIGINS': 'OBJECT_ORIGIN',
    'CONSTRAINT_BONE': 'CONSTRAINT',
    'TOOL_SETTINGS': 'SETTINGS',
    'BONE_DATA': 'ARMATURE_DATA',
    'PRESET': 'PRESET_NEW',
    'WARNING': 'INFO',
}

def get_icon(icon_name):
    """Obtiene un icono compatible con Blender 5.0"""
    return ICON_MAPPING.get(icon_name, icon_name)

# Shortcuts comunes
ICONS = {
    'ARMATURE': get_icon('ARMATURE_DATA'),
    'BONE': get_icon('BONE_DATA'),
    'CONSTRAINT': get_icon('CONSTRAINT_BONE'),
    'SUCCESS': 'CHECKMARK',
    'ERROR': 'ERROR',
    'WARNING': get_icon('WARNING'),
    'INFO': 'INFO'
}
