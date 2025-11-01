"""
Helper module para iconos compatibles con Blender 5.0
Usar este módulo en todos los archivos del addon para evitar errores de iconos
"""

# Mapeo completo de iconos obsoletos a iconos válidos en Blender 5.0
BLENDER_5_ICON_MAPPING = {
    # Iconos principales que han cambiado
    'LIGHTPROBE_CUBEMAP': 'OUTLINER_DATA_LIGHTPROBE',
    'POSE_HLT': 'ARMATURE_DATA',
    'TRANSFORM_ORIGINS': 'OBJECT_ORIGIN',
    'CONSTRAINT_BONE': 'CONSTRAINT',
    'TOOL_SETTINGS': 'SETTINGS',
    'BONE_DATA': 'ARMATURE_DATA',
    'PRESET': 'PRESET_NEW',
    
    # Iconos que se mantienen pero verificamos por compatibilidad
    'CHECKMARK': 'CHECKMARK',
    'ERROR': 'ERROR',
    'INFO': 'INFO',
    'CANCEL': 'CANCEL',
    'TRASH': 'TRASH',
    'AUTO': 'AUTO',
    'PLAY': 'PLAY',
    'SETTINGS': 'SETTINGS',
    'RADIOBUT_OFF': 'RADIOBUT_OFF',
    'RADIOBUT_ON': 'RADIOBUT_ON',
    'TRIA_UP': 'TRIA_UP',
    'TRIA_DOWN': 'TRIA_DOWN',
    'TRIA_LEFT': 'TRIA_LEFT',
    'TRIA_RIGHT': 'TRIA_RIGHT',
    'DUPLICATE': 'DUPLICATE',
    'REMOVE': 'REMOVE',
    'ADD': 'ADD',
    'DOT': 'DOT',
    'ARROW_LEFTRIGHT': 'ARROW_LEFTRIGHT',
    
    # Iconos de datos
    'ARMATURE_DATA': 'ARMATURE_DATA',
    'MESH_DATA': 'MESH_DATA',
    'MATERIAL_DATA': 'MATERIAL_DATA',
    'TEXTURE_DATA': 'TEXTURE_DATA',
    'CAMERA_DATA': 'CAMERA_DATA',
    'LIGHT_DATA': 'LIGHT_DATA',
    'CURVE_DATA': 'CURVE_DATA',
    'LATTICE_DATA': 'LATTICE_DATA',
    'EMPTY_DATA': 'EMPTY_DATA',
    'SPEAKER_DATA': 'SPEAKER_DATA',
    
    # Iconos de outliner
    'OUTLINER_DATA_ARMATURE': 'OUTLINER_DATA_ARMATURE',
    'OUTLINER_DATA_MESH': 'OUTLINER_DATA_MESH',
    'OUTLINER_DATA_CAMERA': 'OUTLINER_DATA_CAMERA',
    'OUTLINER_DATA_LIGHT': 'OUTLINER_DATA_LIGHT',
    'OUTLINER_DATA_LIGHTPROBE': 'OUTLINER_DATA_LIGHTPROBE',
    'OUTLINER_OB_ARMATURE': 'OUTLINER_OB_ARMATURE',
    'OUTLINER_OB_MESH': 'OUTLINER_OB_MESH',
    'OUTLINER_OB_CAMERA': 'OUTLINER_OB_CAMERA',
    'OUTLINER_OB_LIGHT': 'OUTLINER_OB_LIGHT',
    'OUTLINER_OB_EMPTY': 'OUTLINER_OB_EMPTY',
    
    # Iconos de archivos
    'FILE_FOLDER': 'FILE_FOLDER',
    'FILE_TICK': 'FILE_TICK',
    'FILE_NEW': 'FILE_NEW',
    'FILE_BLANK': 'FILE_BLANK',
    'EXPORT': 'EXPORT',
    'IMPORT': 'IMPORT',
    
    # Iconos de modificadores
    'MODIFIER': 'MODIFIER',
    'MOD_ARMATURE': 'MOD_ARMATURE',
    'MOD_ARRAY': 'MOD_ARRAY',
    'MOD_MIRROR': 'MOD_MIRROR',
    'MOD_SUBSURF': 'MOD_SUBSURF',
    
    # Iconos de constraints
    'CONSTRAINT': 'CONSTRAINT',
    'CON_ARMATURE': 'CON_ARMATURE',
    'CON_CHILDOF': 'CON_CHILDOF',
    'CON_TRACKTO': 'CON_TRACKTO',
    'CON_TRANSFORM': 'CON_TRANSFORM',
    
    # Iconos de vertex groups y grupos
    'GROUP_VERTEX': 'GROUP_VERTEX',
    'GROUP_BONE': 'GROUP_BONE',
    'GROUP_UVS': 'GROUP_UVS',
    'GROUP_VCOL': 'GROUP_VCOL',
    'GROUP': 'GROUP',
    
    # Iconos de mesh y geometría
    'MESH_PLANE': 'MESH_PLANE',
    'MESH_CUBE': 'MESH_CUBE',
    'MESH_CIRCLE': 'MESH_CIRCLE',
    'MESH_UVSPHERE': 'MESH_UVSPHERE',
    'MESH_ICOSPHERE': 'MESH_ICOSPHERE',
    'MESH_CYLINDER': 'MESH_CYLINDER',
    'MESH_CONE': 'MESH_CONE',
    'MESH_GRID': 'MESH_GRID',
    'MESH_MONKEY': 'MESH_MONKEY',
    'MESH_TORUS': 'MESH_TORUS',
    'MESH_CAPSULE': 'MESH_CAPSULE',
    
    # Iconos de vista y navegación
    'HIDE_OFF': 'HIDE_OFF',
    'HIDE_ON': 'HIDE_ON',
    'RESTRICT_VIEW_OFF': 'RESTRICT_VIEW_OFF',
    'RESTRICT_VIEW_ON': 'RESTRICT_VIEW_ON',
    'RESTRICT_SELECT_OFF': 'RESTRICT_SELECT_OFF',
    'RESTRICT_SELECT_ON': 'RESTRICT_SELECT_ON',
    'RESTRICT_RENDER_OFF': 'RESTRICT_RENDER_OFF',
    'RESTRICT_RENDER_ON': 'RESTRICT_RENDER_ON',
    
    # Iconos de animación
    'PLAY': 'PLAY',
    'PAUSE': 'PAUSE',
    'REC': 'REC',
    'FF': 'FF',
    'REW': 'REW',
    'FRAME_PREV': 'FRAME_PREV',
    'FRAME_NEXT': 'FRAME_NEXT',
    'KEYFRAME': 'KEYFRAME',
    'KEYFRAME_HLT': 'KEYFRAME_HLT',
    
    # Iconos de espacios de trabajo
    'VIEW3D': 'VIEW3D',
    'OUTLINER': 'OUTLINER',
    'PROPERTIES': 'PROPERTIES',
    'NODETREE': 'NODETREE',
    'IMAGE': 'IMAGE',
    'UV': 'UV',
    'SEQUENCE': 'SEQUENCE',
    'GRAPH': 'GRAPH',
    'NLA': 'NLA',
    'CONSOLE': 'CONSOLE',
    'FILEBROWSER': 'FILEBROWSER',
    'SPREADSHEET': 'SPREADSHEET',
    
    # Iconos de brush y pintura
    'BRUSH_DATA': 'BRUSH_DATA',
    'VPAINT_HLT': 'VPAINT_HLT',
    'WPAINT_HLT': 'WPAINT_HLT',
    'TPAINT_HLT': 'TPAINT_HLT',
    'SCULPTMODE_HLT': 'SCULPTMODE_HLT',
    
    # Iconos de texto y fuentes
    'FONT_DATA': 'FONT_DATA',
    'TEXT': 'TEXT',
    
    # Iconos de mundo y scene
    'WORLD_DATA': 'WORLD_DATA',
    'SCENE_DATA': 'SCENE_DATA',
    'RENDER_RESULT': 'RENDER_RESULT',
    'RENDER_ANIMATION': 'RENDER_ANIMATION',
    'RENDER_STILL': 'RENDER_STILL',
    
    # Iconos especiales de Blender 5.0 (pueden ser nuevos)
    'GEOMETRY_NODES': 'GEOMETRY_NODES',
    'GEOMETRY_SET': 'GEOMETRY_SET',
    'POINTCLOUD_DATA': 'POINTCLOUD_DATA',
    'CURVES_DATA': 'CURVES_DATA',
    'VOLUME_DATA': 'VOLUME_DATA',
    
    # Iconos de warning y status
    'WARNING': 'ERROR',  # WARNING podría no existir, usar ERROR
    'QUESTION': 'QUESTION',
    'HELP': 'HELP',
    'BLENDER': 'BLENDER',
    'COMMUNITY': 'COMMUNITY',
}

def get_icon(icon_name):
    """
    Obtiene un icono compatible con Blender 5.0
    
    Args:
        icon_name (str): Nombre del icono solicitado
    
    Returns:
        str: Nombre del icono compatible con Blender 5.0
    
    Example:
        icon = get_icon('LIGHTPROBE_CUBEMAP')  # Retorna 'OUTLINER_DATA_LIGHTPROBE'
        layout.operator("my.operator", icon=get_icon('POSE_HLT'))
    """
    return BLENDER_5_ICON_MAPPING.get(icon_name, icon_name)

def update_operator_icon(operator_kwargs, fallback_icon='NONE'):
    """
    Actualiza el icono en argumentos de operador
    
    Args:
        operator_kwargs (dict): Diccionario de argumentos del operador
        fallback_icon (str): Icono a usar si no se encuentra uno válido
    
    Returns:
        dict: Argumentos actualizados con icono compatible
    
    Example:
        kwargs = {'text': 'My Button', 'icon': 'LIGHTPROBE_CUBEMAP'}
        kwargs = update_operator_icon(kwargs)
        layout.operator("my.operator", **kwargs)
    """
    if 'icon' in operator_kwargs:
        operator_kwargs['icon'] = get_icon(operator_kwargs['icon'])
    return operator_kwargs

def get_armature_icon():
    """Obtiene el icono estándar para armatures en Blender 5.0"""
    return get_icon('ARMATURE_DATA')

def get_bone_icon():
    """Obtiene el icono estándar para huesos en Blender 5.0"""
    return get_icon('BONE_DATA')  # Se mapea a ARMATURE_DATA

def get_constraint_icon():
    """Obtiene el icono estándar para constraints en Blender 5.0"""
    return get_icon('CONSTRAINT')

def get_mesh_icon():
    """Obtiene el icono estándar para mesh en Blender 5.0"""
    return get_icon('MESH_DATA')

def get_success_icon():
    """Obtiene el icono para indicar éxito/válido en Blender 5.0"""
    return get_icon('CHECKMARK')

def get_error_icon():
    """Obtiene el icono para indicar error en Blender 5.0"""
    return get_icon('ERROR')

def get_warning_icon():
    """Obtiene el icono para indicar advertencia en Blender 5.0"""
    return get_icon('INFO')  # Usar INFO en lugar de WARNING

def get_info_icon():
    """Obtiene el icono para información en Blender 5.0"""
    return get_icon('INFO')

def validate_icon_exists(icon_name):
    """
    Valida si un icono existe en Blender 5.0
    
    Args:
        icon_name (str): Nombre del icono a validar
    
    Returns:
        bool: True si el icono existe, False si no
    
    Note:
        Esta función es útil para debugging pero no es 100% precisa
        ya que no tenemos acceso directo a la lista de iconos de Blender
    """
    # Lista de iconos que sabemos que existen en Blender 5.0
    known_valid_icons = {
        'NONE', 'CHECKMARK', 'ERROR', 'INFO', 'CANCEL', 'ADD', 'REMOVE',
        'DUPLICATE', 'ARROW_LEFTRIGHT', 'TRIA_UP', 'TRIA_DOWN', 'TRIA_LEFT', 'TRIA_RIGHT',
        'RADIOBUT_OFF', 'RADIOBUT_ON', 'DOT', 'TRASH', 'AUTO', 'PLAY', 'SETTINGS',
        'ARMATURE_DATA', 'MESH_DATA', 'CONSTRAINT', 'OBJECT_ORIGIN', 'OUTLINER_DATA_LIGHTPROBE',
        'OUTLINER_DATA_ARMATURE', 'FILE_FOLDER', 'FILE_TICK', 'EXPORT', 'IMPORT',
        'MODIFIER', 'GROUP_VERTEX', 'HIDE_OFF', 'HIDE_ON', 'BRUSH_DATA',
        'GEOMETRY_NODES', 'POINTCLOUD_DATA', 'CURVES_DATA', 'VOLUME_DATA'
    }
    
    # Primero verificar si está en nuestro mapeo
    mapped_icon = get_icon(icon_name)
    
    # Luego verificar si está en la lista de iconos conocidos
    return mapped_icon in known_valid_icons

def get_safe_icon(icon_name, fallback='NONE'):
    """
    Obtiene un icono seguro, con fallback si no existe
    
    Args:
        icon_name (str): Nombre del icono solicitado
        fallback (str): Icono de fallback si el solicitado no existe
    
    Returns:
        str: Icono seguro para usar
    """
    mapped_icon = get_icon(icon_name)
    
    if validate_icon_exists(mapped_icon):
        return mapped_icon
    else:
        print(f"[ICON_HELPER] Advertencia: Icono '{icon_name}' -> '{mapped_icon}' podría no existir, usando fallback '{fallback}'")
        return fallback

# Funciones de conveniencia para tipos comunes de iconos
def get_ui_icon(ui_element_type):
    """
    Obtiene iconos apropiados para elementos de UI comunes
    
    Args:
        ui_element_type (str): Tipo de elemento ('button', 'panel', 'menu', etc.)
    
    Returns:
        str: Icono apropiado para el elemento
    """
    ui_icons = {
        'button': 'NONE',
        'panel': 'SETTINGS',
        'menu': 'TRIA_DOWN',
        'tab': 'TRIA_RIGHT',
        'success': 'CHECKMARK',
        'error': 'ERROR',
        'warning': 'INFO',
        'info': 'INFO',
        'add': 'ADD',
        'remove': 'REMOVE',
        'edit': 'SETTINGS',
        'duplicate': 'DUPLICATE',
        'move_up': 'TRIA_UP',
        'move_down': 'TRIA_DOWN',
        'expand': 'TRIA_DOWN',
        'collapse': 'TRIA_RIGHT',
        'armature': 'ARMATURE_DATA',
        'bone': 'ARMATURE_DATA',
        'mesh': 'MESH_DATA',
        'constraint': 'CONSTRAINT',
        'modifier': 'MODIFIER',
        'material': 'MATERIAL_DATA',
        'texture': 'TEXTURE_DATA',
        'file': 'FILE_BLANK',
        'folder': 'FILE_FOLDER',
        'save': 'FILE_TICK',
        'load': 'FILE_FOLDER',
        'export': 'EXPORT',
        'import': 'IMPORT'
    }
    
    return get_icon(ui_icons.get(ui_element_type, 'NONE'))

# Diccionario de shortcuts para importación fácil
ICONS = {
    'ARMATURE': get_armature_icon(),
    'BONE': get_bone_icon(),
    'CONSTRAINT': get_constraint_icon(),
    'MESH': get_mesh_icon(),
    'SUCCESS': get_success_icon(),
    'ERROR': get_error_icon(),
    'WARNING': get_warning_icon(),
    'INFO': get_info_icon(),
    'ADD': get_icon('ADD'),
    'REMOVE': get_icon('REMOVE'),
    'DUPLICATE': get_icon('DUPLICATE'),
    'SETTINGS': get_icon('SETTINGS'),
    'PLAY': get_icon('PLAY'),
    'AUTO': get_icon('AUTO')
}

# Función para debug - mostrar todos los mapeos
def print_icon_mappings():
    """Imprime todos los mapeos de iconos disponibles (útil para debug)"""
    print("[ICON_HELPER] === MAPEOS DE ICONOS PARA BLENDER 5.0 ===")
    for old_icon, new_icon in BLENDER_5_ICON_MAPPING.items():
        if old_icon != new_icon:
            print(f"[ICON_HELPER] {old_icon} -> {new_icon}")
    print(f"[ICON_HELPER] Total: {len(BLENDER_5_ICON_MAPPING)} iconos mapeados")

# Auto-test al importar el módulo (solo en modo debug)
def _self_test():
    """Test básico del sistema de iconos"""
    test_icons = ['LIGHTPROBE_CUBEMAP', 'POSE_HLT', 'CONSTRAINT_BONE', 'ARMATURE_DATA']
    
    print("[ICON_HELPER] === AUTO-TEST ===")
    for test_icon in test_icons:
        mapped = get_icon(test_icon)
        valid = validate_icon_exists(mapped)
        status = "✅" if valid else "⚠️"
        print(f"[ICON_HELPER] {status} {test_icon} -> {mapped}")

# Ejecutar auto-test si se importa el módulo directamente
if __name__ == "__main__":
    _self_test()
    print_icon_mappings()