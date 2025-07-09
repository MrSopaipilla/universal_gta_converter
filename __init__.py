bl_info = {
    "name": "Universal to GTA SA Converter",
    "author": "YoshiMaincra + GPT + Claude",
    "version": (3, 2, 3),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Universal GTA",
    "description": "Convierte armatures personalizados a GTA SA con detección inteligente de huesos, corrección de normales, animaciones predefinidas, soporte para Shape Keys y herramientas avanzadas. FLUJO COMPLETO v3.2.3",
    "category": "Rigging",
}

import bpy
from bpy.props import PointerProperty

# CORRECCIÓN: Manejo mejorado de importaciones con verificación de dependencias
def safe_import_module(module_path, module_name):
    """Importa un módulo de forma segura con manejo de errores"""
    try:
        module = __import__(module_path, fromlist=[module_name])
        return getattr(module, module_name, None)
    except ImportError as e:
        print(f"[ADDON] ⚠ Error importando {module_path}.{module_name}: {e}")
        return None
    except AttributeError as e:
        print(f"[ADDON] ⚠ Atributo no encontrado {module_name} en {module_path}: {e}")
        return None

# Importar configuración y clases base (REQUERIDAS)
try:
    from .config import UniversalGTASettings, BoneMappingItem, register_validation
    print("[ADDON] ✓ Configuración cargada exitosamente")
except ImportError as e:
    print(f"[ADDON] ✗ Error crítico cargando configuración: {e}")
    raise  # Error crítico, no puede continuar

# Importar el conversor principal (REQUERIDO)
try:
    from .converter import UniversalGTAConverter
    print("[ADDON] ✓ Conversor principal cargado exitosamente")
except ImportError as e:
    print(f"[ADDON] ✗ Error crítico cargando conversor: {e}")
    raise  # Error crítico, no puede continuar

# Importar poses externas (REQUERIDO)
try:
    from . import external_pose_caller
    print("[ADDON] ✓ Sistema de poses externas cargado exitosamente")
except ImportError as e:
    print(f"[ADDON] ✗ Error crítico cargando external_pose_caller: {e}")
    raise  # Error crítico, no puede continuar

# Importar operadores de conversión (REQUERIDOS)
try:
    from .operators.conversion import (
        UNIVERSALGTA_OT_execute_conversion,
        UNIVERSALGTA_OT_preview_conversion,
        UNIVERSALGTA_OT_test_bone_mappings,
        UNIVERSALGTA_OT_clear_test_constraints,
        UNIVERSALGTA_OT_auto_detect_bones,
        UNIVERSALGTA_OT_validate_conversion
    )
    CONVERSION_OPERATORS_AVAILABLE = True
    print("[ADDON] ✓ Operadores de conversión cargados exitosamente")
except ImportError as e:
    print(f"[ADDON] ✗ Error crítico cargando operadores de conversión: {e}")
    raise  # Error crítico, no puede continuar

# Importar operadores de pose (MANEJO ROBUSTO - OPCIONALES)
POSE_OPERATORS = []
try:
    from .operators.pose import (
        UNIVERSALGTA_OT_apply_custom_pose,
        UNIVERSALGTA_OT_test_pose_application,
        UNIVERSALGTA_OT_verify_pose_setup,
        UNIVERSALGTA_OT_apply_manual_pose,
        UNIVERSALGTA_OT_reset_pose,
        UNIVERSALGTA_OT_copy_pose,
        UNIVERSALGTA_OT_bake_pose
    )
    POSE_OPERATORS = [
        UNIVERSALGTA_OT_apply_custom_pose,
        UNIVERSALGTA_OT_test_pose_application,
        UNIVERSALGTA_OT_verify_pose_setup,
        UNIVERSALGTA_OT_apply_manual_pose,
        UNIVERSALGTA_OT_reset_pose,
        UNIVERSALGTA_OT_copy_pose,
        UNIVERSALGTA_OT_bake_pose
    ]
    print("[ADDON] ✓ Todos los operadores de pose cargados exitosamente")
except ImportError as e:
    # Fallback: intentar cargar solo el operador básico
    try:
        from .operators.pose import UNIVERSALGTA_OT_apply_custom_pose
        POSE_OPERATORS = [UNIVERSALGTA_OT_apply_custom_pose]
        print(f"[ADDON] ⚠ Solo operador básico de pose disponible: {e}")
    except ImportError as e2:
        print(f"[ADDON] ✗ Error crítico cargando operadores de pose: {e2}")
        POSE_OPERATORS = []

# Importar operadores de mapeo (REQUERIDOS)
try:
    from .operators.mapping import (
        UNIVERSALGTA_OT_add_custom_entry,
        UNIVERSALGTA_OT_remove_mapping_entry,
        UNIVERSALGTA_OT_move_mapping_up,
        UNIVERSALGTA_OT_move_mapping_down,
        UNIVERSALGTA_OT_clear_mappings,
        UNIVERSALGTA_OT_add_target_bones,
        UNIVERSALGTA_OT_auto_detect_mappings,
        UNIVERSALGTA_OT_load_mapping,
        UNIVERSALGTA_OT_save_mapping,
        UNIVERSALGTA_OT_validate_mappings,
        UNIVERSALGTA_OT_duplicate_mapping,
        UNIVERSALGTA_OT_invert_mapping,
        UNIVERSALGTA_OT_enable_all_mappings,
        UNIVERSALGTA_OT_disable_all_mappings,
        UNIVERSALGTA_OT_enable_high_confidence
    )
    MAPPING_OPERATORS_AVAILABLE = True
    print("[ADDON] ✓ Operadores de mapeo cargados exitosamente")
except ImportError as e:
    print(f"[ADDON] ✗ Error crítico cargando operadores de mapeo: {e}")
    raise  # Error crítico, no puede continuar

# Importar operadores de limpieza (OPCIONALES)
CLEANUP_OPERATORS = []
try:
    from .operators.cleanup import (
        UNIVERSALGTA_OT_clean_model,
        UNIVERSALGTA_OT_purge_unused_data,
        UNIVERSALGTA_OT_purge_scene,
        UNIVERSALGTA_OT_clean_armatures,
        UNIVERSALGTA_OT_clean_empty_vertex_groups,
        UNIVERSALGTA_OT_fix_modifiers,
        UNIVERSALGTA_OT_remove_duplicates,
        UNIVERSALGTA_OT_optimize_mesh
    )
    CLEANUP_OPERATORS = [
        UNIVERSALGTA_OT_clean_model,
        UNIVERSALGTA_OT_purge_unused_data,
        UNIVERSALGTA_OT_purge_scene,
        UNIVERSALGTA_OT_clean_armatures,
        UNIVERSALGTA_OT_clean_empty_vertex_groups,
        UNIVERSALGTA_OT_fix_modifiers,
        UNIVERSALGTA_OT_remove_duplicates,
        UNIVERSALGTA_OT_optimize_mesh
    ]
    print("[ADDON] ✓ Operadores de limpieza cargados exitosamente")
except ImportError as e:
    print(f"[ADDON] ⚠ Operadores de limpieza no disponibles: {e}")

# Importar operadores de normales (OPCIONALES)
NORMALS_OPERATORS = []
try:
    from .operators.normals import (
        UNIVERSALGTA_OT_fix_normals,
        UNIVERSALGTA_OT_auto_fix_normals_post_conversion,
        UNIVERSALGTA_OT_flip_normals,
        UNIVERSALGTA_OT_check_normals_consistency
    )
    NORMALS_OPERATORS = [
        UNIVERSALGTA_OT_fix_normals,
        UNIVERSALGTA_OT_auto_fix_normals_post_conversion,
        UNIVERSALGTA_OT_flip_normals,
        UNIVERSALGTA_OT_check_normals_consistency
    ]
    print("[ADDON] ✓ Operadores de normales cargados exitosamente")
except ImportError as e:
    print(f"[ADDON] ⚠ Operadores de normales no disponibles: {e}")

# Importar operadores de nombres (OPCIONALES)
NAMING_OPERATORS = []
try:
    from .operators.naming import (
        UNIVERSALGTA_OT_apply_custom_names,
        UNIVERSALGTA_OT_reset_names,
        UNIVERSALGTA_OT_validate_names,
        UNIVERSALGTA_OT_auto_generate_names
    )
    NAMING_OPERATORS = [
        UNIVERSALGTA_OT_apply_custom_names,
        UNIVERSALGTA_OT_reset_names,
        UNIVERSALGTA_OT_validate_names,
        UNIVERSALGTA_OT_auto_generate_names
    ]
    print("[ADDON] ✓ Operadores de nombres cargados exitosamente")
except ImportError as e:
    print(f"[ADDON] ⚠ Operadores de nombres no disponibles: {e}")

# Importar operadores de animaciones (OPCIONALES)
ANIMATION_OPERATORS = []
try:
    from .operators.animations import (
        UNIVERSALGTA_OT_load_animation,
        UNIVERSALGTA_OT_clear_animations,
        UNIVERSALGTA_OT_refresh_animations_on_spacing_change,
        UNIVERSALGTA_OT_apply_facial_expressiveness,
        UNIVERSALGTA_OT_create_animation_files
    )
    ANIMATION_OPERATORS = [
        UNIVERSALGTA_OT_load_animation,
        UNIVERSALGTA_OT_clear_animations,
        UNIVERSALGTA_OT_refresh_animations_on_spacing_change,
        UNIVERSALGTA_OT_apply_facial_expressiveness,
        UNIVERSALGTA_OT_create_animation_files
    ]
    print("[ADDON] ✓ Operadores de animaciones cargados exitosamente")
except ImportError as e:
    print(f"[ADDON] ⚠ Operadores de animaciones no disponibles: {e}")

# Importar operadores adicionales (OPCIONALES)
ADDITIONAL_OPERATORS = []
try:
    from .operators.export import UNIVERSALGTA_OT_export_textures
    from .operators.spacing import UNIVERSALGTA_OT_apply_spacing
    ADDITIONAL_OPERATORS.extend([UNIVERSALGTA_OT_export_textures, UNIVERSALGTA_OT_apply_spacing])
except ImportError as e:
    print(f"[ADDON] ⚠ Operadores adicionales no disponibles: {e}")

# Importar operadores de referencia GTA SA (OPCIONALES)
GTA_REFERENCE_OPERATORS = []
try:
    from .operators.gta_reference import (
        UNIVERSALGTA_OT_show_gta_bone_reference,
        UNIVERSALGTA_OT_create_gta_armature_template
    )
    GTA_REFERENCE_OPERATORS = [
        UNIVERSALGTA_OT_show_gta_bone_reference,
        UNIVERSALGTA_OT_create_gta_armature_template
    ]
    print("[ADDON] ✓ Operadores de referencia GTA SA cargados exitosamente")
except ImportError as e:
    print(f"[ADDON] ⚠ Operadores de referencia GTA SA no disponibles: {e}")

# Importar paneles principales (REQUERIDOS)
try:
    from .panels.main_panel import (
        UNIVERSALGTA_PT_MainPanel,
        UNIVERSALGTA_PT_ShapeKeysPanel,
        UNIVERSALGTA_PT_BoneMappingPanel,
        UNIVERSALGTA_PT_AdvancedPanel,
        UNIVERSALGTA_PT_UtilitiesPanel,
        UNIVERSALGTA_PT_AnimationsPanel,
        UNIVERSALGTA_PT_StatusPanel
    )
    MAIN_PANELS_AVAILABLE = True
    print("[ADDON] ✓ Paneles principales cargados exitosamente")
except ImportError as e:
    print(f"[ADDON] ✗ Error crítico cargando paneles principales: {e}")
    raise  # Error crítico, no puede continuar

# Importar paneles de créditos (OPCIONALES)
CREDITS_PANELS = []
CREDITS_OPERATORS = []
try:
    from .panels.credits import (
        UNIVERSALGTA_OT_open_yoshi_channel,
        UNIVERSALGTA_PT_CreditsPanel,
        UNIVERSALGTA_PT_TestingPanel,
        UNIVERSALGTA_PT_NamingPanel
    )
    CREDITS_PANELS = [
        UNIVERSALGTA_PT_CreditsPanel,
        UNIVERSALGTA_PT_TestingPanel,
        UNIVERSALGTA_PT_NamingPanel
    ]
    CREDITS_OPERATORS = [UNIVERSALGTA_OT_open_yoshi_channel]
    print("[ADDON] ✓ Paneles de créditos cargados exitosamente")
except ImportError as e:
    print(f"[ADDON] ⚠ Paneles de créditos no disponibles: {e}")

# Importar operadores de Shape Keys (MANEJO ROBUSTO - OPCIONALES)
SHAPE_KEYS_OPERATORS = []
try:
    from .operators.shape_keys import (
        UNIVERSALGTA_OT_apply_all_shape_keys,
        UNIVERSALGTA_OT_backup_shape_keys,
        UNIVERSALGTA_OT_restore_shape_keys_backup,
        UNIVERSALGTA_OT_list_shape_keys
    )
    SHAPE_KEYS_OPERATORS = [
        UNIVERSALGTA_OT_apply_all_shape_keys,
        UNIVERSALGTA_OT_backup_shape_keys,
        UNIVERSALGTA_OT_restore_shape_keys_backup,
        UNIVERSALGTA_OT_list_shape_keys
    ]
    print("[ADDON] ✓ Operadores de Shape Keys cargados exitosamente")
except ImportError as e:
    print(f"[ADDON] ⚠ Operadores de Shape Keys no disponibles: {e}")


class UNIVERSALGTA_UL_BoneMappingList(bpy.types.UIList):
    """Lista UI para mapeos de huesos con drag & drop funcional y visual mejorado"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Icono basado en estado
            if item.enabled:
                status_icon = 'CHECKMARK' if item.source_bone and item.target_bone else 'ERROR'
            else:
                status_icon = 'CHECKBOX_DEHLT'
            
            # Layout principal
            row = layout.row(align=True)
            row.prop(item, "enabled", text="", icon=status_icon)
            
            # Información del mapeo
            if item.target_bone:
                # Mostrar target bone (más importante)
                row.label(text=item.target_bone, icon='BONE_DATA')
                
                # Mostrar source bone si existe
                if item.source_bone:
                    row.label(text=f"← {item.source_bone}")
                else:
                    row.label(text="← (sin asignar)", icon='ERROR')
                
                # Mostrar confianza si es automático
                if item.detection_method == "Auto" and item.confidence > 0:
                    confidence_text = f"{item.confidence:.1f}"
                    confidence_icon = 'CHECKMARK' if item.confidence > 0.7 else 'ERROR' if item.confidence < 0.4 else 'DOT'
                    row.label(text=confidence_text, icon=confidence_icon)
                elif item.detection_method == "Manual":
                    row.label(text="M", icon='TOOL_SETTINGS')
            else:
                row.label(text="(sin configurar)", icon='ERROR')
        
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon=status_icon)


# CORRECCIÓN: Compilar lista de todas las clases a registrar de forma dinámica
def get_all_classes():
    """Recopila todas las clases disponibles para registro"""
    classes = []
    
    # Agregar clases de configuración (REQUERIDAS)
    classes.extend([
        UniversalGTASettings,
        BoneMappingItem,
        UNIVERSALGTA_UL_BoneMappingList
    ])
    
    # Agregar operadores de conversión (REQUERIDOS)
    classes.extend([
        UNIVERSALGTA_OT_execute_conversion,
        UNIVERSALGTA_OT_preview_conversion,
        UNIVERSALGTA_OT_test_bone_mappings,
        UNIVERSALGTA_OT_clear_test_constraints,
        UNIVERSALGTA_OT_auto_detect_bones,
        UNIVERSALGTA_OT_validate_conversion
    ])
    
    # Agregar operadores de mapeo (REQUERIDOS)  
    classes.extend([
        UNIVERSALGTA_OT_add_custom_entry,
        UNIVERSALGTA_OT_remove_mapping_entry,
        UNIVERSALGTA_OT_move_mapping_up,
        UNIVERSALGTA_OT_move_mapping_down,
        UNIVERSALGTA_OT_clear_mappings,
        UNIVERSALGTA_OT_add_target_bones,
        UNIVERSALGTA_OT_auto_detect_mappings,
        UNIVERSALGTA_OT_load_mapping,
        UNIVERSALGTA_OT_save_mapping,
        UNIVERSALGTA_OT_validate_mappings,
        UNIVERSALGTA_OT_duplicate_mapping,
        UNIVERSALGTA_OT_invert_mapping,
        UNIVERSALGTA_OT_enable_all_mappings,
        UNIVERSALGTA_OT_disable_all_mappings,
        UNIVERSALGTA_OT_enable_high_confidence
    ])
    
    # Agregar paneles principales (REQUERIDOS)
    classes.extend([
        UNIVERSALGTA_PT_MainPanel,
        UNIVERSALGTA_PT_ShapeKeysPanel,
        UNIVERSALGTA_PT_BoneMappingPanel,
        UNIVERSALGTA_PT_AdvancedPanel,
        UNIVERSALGTA_PT_UtilitiesPanel,
        UNIVERSALGTA_PT_AnimationsPanel,
        UNIVERSALGTA_PT_StatusPanel
    ])
    
    # Agregar operadores opcionales si están disponibles
    classes.extend(POSE_OPERATORS)
    classes.extend(CLEANUP_OPERATORS)
    classes.extend(NORMALS_OPERATORS)
    classes.extend(NAMING_OPERATORS)
    classes.extend(ANIMATION_OPERATORS)
    classes.extend(ADDITIONAL_OPERATORS)
    classes.extend(GTA_REFERENCE_OPERATORS)
    classes.extend(SHAPE_KEYS_OPERATORS)
    classes.extend(CREDITS_PANELS)
    classes.extend(CREDITS_OPERATORS)


    from .operators.enhanced_bone_mapping_panel import (
    UNIVERSALGTA_OT_save_mapping,
    UNIVERSALGTA_OT_load_mapping,
    UNIVERSALGTA_OT_export_mapping_template,
    UNIVERSALGTA_OT_import_mapping_from_names,
    UNIVERSALGTA_OT_validate_mapping_file,
)

from .panels.mapping_operators_enhanced import (
    UNIVERSALGTA_UL_ModernBoneMappingList,
    UNIVERSALGTA_OT_save_bone_mapping,
    UNIVERSALGTA_OT_load_bone_mapping,
    UNIVERSALGTA_PT_ModernBoneMappingPanel,
)

from .ui.modern_styles import (
    UNIVERSALGTA_OT_adjust_value,
    UNIVERSALGTA_PT_ModernStylesDemo,
    UNIVERSALGTA_PT_StyledBoneMappingPanel,
    
)
    

# Agregar estas importaciones:
from .operators.enhanced_bone_mapping_panel import (
    UNIVERSALGTA_OT_save_mapping,
    UNIVERSALGTA_OT_load_mapping,
    UNIVERSALGTA_OT_export_mapping_template,
    UNIVERSALGTA_OT_import_mapping_from_names,
    UNIVERSALGTA_OT_validate_mapping_file,
)

from .panels.mapping_operators_enhanced import (
    UNIVERSALGTA_UL_ModernBoneMappingList,
    UNIVERSALGTA_OT_save_bone_mapping,
    UNIVERSALGTA_OT_load_bone_mapping,
    UNIVERSALGTA_PT_ModernBoneMappingPanel,
)

from .ui.modern_styles import (
    UNIVERSALGTA_OT_adjust_value,
    UNIVERSALGTA_PT_ModernStylesDemo,
    UNIVERSALGTA_PT_StyledBoneMappingPanel,
)

# En tu __init__.py, agregar las importaciones:
from .enhanced_bone_mapping_panel import (
    UNIVERSALGTA_UL_ModernBoneMappingList,
    UNIVERSALGTA_OT_save_bone_mapping,
    UNIVERSALGTA_OT_load_bone_mapping,
    UNIVERSALGTA_PT_ModernBoneMappingPanel,
)

from .mapping_operators_enhanced import (
    UNIVERSALGTA_OT_save_mapping,
    UNIVERSALGTA_OT_load_mapping,
    UNIVERSALGTA_OT_export_mapping_template,
    UNIVERSALGTA_OT_import_mapping_from_names,
    UNIVERSALGTA_OT_validate_mapping_file,
)

from .modern_ui_styles import (
    UNIVERSALGTA_OT_adjust_value,
    UNIVERSALGTA_PT_ModernStylesDemo,
    UNIVERSALGTA_PT_StyledBoneMappingPanel,
)

# Agregar a la lista classes:
classes.extend([
    # Mapping Enhanced
    UNIVERSALGTA_OT_save_mapping,
    UNIVERSALGTA_OT_load_mapping,
    UNIVERSALGTA_OT_export_mapping_template,
    UNIVERSALGTA_OT_import_mapping_from_names,
    UNIVERSALGTA_OT_validate_mapping_file,
    
    # Modern Bone Mapping
    UNIVERSALGTA_UL_ModernBoneMappingList,
    UNIVERSALGTA_OT_save_bone_mapping,
    UNIVERSALGTA_OT_load_bone_mapping,
    UNIVERSALGTA_PT_ModernBoneMappingPanel,
    
    # Modern Styles
    UNIVERSALGTA_OT_adjust_value,
    UNIVERSALGTA_PT_ModernStylesDemo,
    UNIVERSALGTA_PT_StyledBoneMappingPanel,
])

    


def register():
    """Registra todas las clases del addon de forma segura"""
    try:
        # Registrar validadores de configuración
        register_validation()
        
        # Obtener todas las clases disponibles
        classes = get_all_classes()
        
        # Registrar cada clase de forma segura
        registered_count = 0
        failed_count = 0
        
        for cls in classes:
            try:
                bpy.utils.register_class(cls)
                registered_count += 1
            except Exception as e:
                print(f"[ADDON] ⚠ Error registrando {cls.__name__}: {e}")
                failed_count += 1
        
        # Registrar property group en la escena
        try:
            bpy.types.Scene.universal_gta_settings = PointerProperty(type=UniversalGTASettings)
            print("[ADDON] ✓ Property group registrado en Scene")
        except Exception as e:
            print(f"[ADDON] ✗ Error registrando property group: {e}")
            raise
        
        print(f"[ADDON] ✓ Registro completado: {registered_count} clases registradas, {failed_count} fallidas")
        
        if failed_count > 0:
            print(f"[ADDON] ⚠ El addon funcionará con funcionalidad limitada debido a {failed_count} errores de registro")
    
    except Exception as e:
        print(f"[ADDON] ✗ Error crítico durante el registro: {e}")
        raise


def unregister():
    """Desregistra todas las clases del addon de forma segura"""
    try:
        # Desregistrar property group
        if hasattr(bpy.types.Scene, 'universal_gta_settings'):
            delattr(bpy.types.Scene, 'universal_gta_settings')
            print("[ADDON] ✓ Property group desregistrado")
        
        # Obtener y desregistrar todas las clases
        classes = get_all_classes()
        
        unregistered_count = 0
        failed_count = 0
        
        for cls in reversed(classes):
            try:
                bpy.utils.unregister_class(cls)
                unregistered_count += 1
            except Exception as e:
                print(f"[ADDON] ⚠ Error desregistrando {cls.__name__}: {e}")
                failed_count += 1
        
        print(f"[ADDON] ✓ Desregistro completado: {unregistered_count} clases desregistradas, {failed_count} fallidas")
    
    except Exception as e:
        print(f"[ADDON] ✗ Error durante el desregistro: {e}")


if __name__ == "__main__":
    register()