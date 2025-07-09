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

# Importar configuración mejorada
from .config import UniversalGTASettings, BoneMappingItem, register_validation

# Importar el conversor principal
from .converter import UniversalGTAConverter

# Importar poses externas
from . import external_pose_caller

# Importar operadores de conversión
from .operators.conversion import (
    UNIVERSALGTA_OT_execute_conversion,
    UNIVERSALGTA_OT_preview_conversion,
    UNIVERSALGTA_OT_test_bone_mappings,
    UNIVERSALGTA_OT_clear_test_constraints,
    UNIVERSALGTA_OT_auto_detect_bones,
    UNIVERSALGTA_OT_validate_conversion
)

# Importar operadores de pose (MANEJO ROBUSTO)
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
    POSE_OPERATORS_AVAILABLE = True
    print("[ADDON] ✓ Todos los operadores de pose cargados exitosamente")
except ImportError as e:
    # Fallback mínimo
    try:
        from .operators.pose import UNIVERSALGTA_OT_apply_custom_pose
        POSE_OPERATORS_AVAILABLE = False
        print(f"[ADDON] ⚠ Solo operador básico de pose disponible: {e}")
    except ImportError as e2:
        print(f"[ADDON] ✗ Error crítico cargando operadores de pose: {e2}")
        POSE_OPERATORS_AVAILABLE = False

# Importar operadores de mapeo
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

# Importar operadores de limpieza
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

# Importar operadores de normales
from .operators.normals import (
    UNIVERSALGTA_OT_fix_normals,
    UNIVERSALGTA_OT_auto_fix_normals_post_conversion,
    UNIVERSALGTA_OT_flip_normals,
    UNIVERSALGTA_OT_check_normals_consistency
)

# Importar operadores de nombres
from .operators.naming import (
    UNIVERSALGTA_OT_apply_custom_names,
    UNIVERSALGTA_OT_reset_names,
    UNIVERSALGTA_OT_validate_names,
    UNIVERSALGTA_OT_auto_generate_names
)

# Importar operadores de animaciones
from .operators.animations import (
    UNIVERSALGTA_OT_load_animation,
    UNIVERSALGTA_OT_clear_animations,
    UNIVERSALGTA_OT_refresh_animations_on_spacing_change,
    UNIVERSALGTA_OT_apply_facial_expressiveness,
    UNIVERSALGTA_OT_create_animation_files
)

# Importar operadores de exportación y espaciado
from .operators.export import UNIVERSALGTA_OT_export_textures
from .operators.spacing import UNIVERSALGTA_OT_apply_spacing

# Importar operadores de referencia GTA SA
from .operators.gta_reference import (
    UNIVERSALGTA_OT_show_gta_bone_reference,
    UNIVERSALGTA_OT_create_gta_armature_template
)

# Importar paneles principales
from .panels.main_panel import (
    UNIVERSALGTA_PT_MainPanel,
    UNIVERSALGTA_PT_ShapeKeysPanel,
    UNIVERSALGTA_PT_BoneMappingPanel,
    UNIVERSALGTA_PT_AdvancedPanel,
    UNIVERSALGTA_PT_UtilitiesPanel,
    UNIVERSALGTA_PT_AnimationsPanel,
    UNIVERSALGTA_PT_StatusPanel
)

# Importar paneles de créditos
from .panels.credits import (
    UNIVERSALGTA_OT_open_yoshi_channel,
    UNIVERSALGTA_PT_CreditsPanel,
    UNIVERSALGTA_PT_TestingPanel,
    UNIVERSALGTA_PT_NamingPanel
)

# Importar operadores de Shape Keys (MANEJO ROBUSTO)
try:
    from .operators.shape_keys import (
        UNIVERSALGTA_OT_apply_all_shape_keys,
        UNIVERSALGTA_OT_backup_shape_keys,
        UNIVERSALGTA_OT_restore_shape_keys_backup,
        UNIVERSALGTA_OT_list_shape_keys
    )
    SHAPE_KEYS_AVAILABLE = True
    print("[ADDON] ✓ Operadores de Shape Keys cargados exitosamente")
except ImportError as e:
    print(f"[ADDON] ⚠ Operadores de Shape Keys no disponibles: {e}")
    SHAPE_KEYS_AVAILABLE = False


class UNIVERSALGTA_UL_BoneMappingList(bpy.types.UIList):
    """Lista UI para mapeos de huesos con drag & drop funcional y visual mejorado"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Mostrar información del mapeo
            if item.enabled:
                layout.prop(item, "enabled", text="", emboss=False, icon='CHECKMARK')
            else:
                layout.prop(item, "enabled", text="", emboss=False, icon='CANCEL')
            
            # Mostrar bones con colores
            if item.source_bone and item.target_bone:
                layout.label(text=f"{item.source_bone} → {item.target_bone}", icon='BONE_DATA')
            elif item.target_bone:
                layout.label(text=f"❌ → {item.target_bone}", icon='ERROR')
            else:
                layout.label(text="❌ → ❌", icon='ERROR')
            
            # Mostrar confianza si es automático
            if item.detection_method == "Auto" and item.confidence > 0:
                conf_text = f"{item.confidence:.1f}"
                if item.confidence >= 0.8:
                    layout.label(text=conf_text, icon='CHECKMARK')
                elif item.confidence >= 0.5:
                    layout.label(text=conf_text, icon='QUESTION')
                else:
                    layout.label(text=conf_text, icon='ERROR')
        
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='BONE_DATA')


# RECOLECTAR TODAS LAS CLASES PARA REGISTRO
classes = [
    # Configuración
    BoneMappingItem,
    UniversalGTASettings,
    
    # UI Lists
    UNIVERSALGTA_UL_BoneMappingList,
    
    # Operadores de conversión
    UNIVERSALGTA_OT_execute_conversion,
    UNIVERSALGTA_OT_preview_conversion,
    UNIVERSALGTA_OT_test_bone_mappings,
    UNIVERSALGTA_OT_clear_test_constraints,
    UNIVERSALGTA_OT_auto_detect_bones,
    UNIVERSALGTA_OT_validate_conversion,
    
    # Operadores de mapeo
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
    UNIVERSALGTA_OT_enable_high_confidence,
    
    # Operadores de limpieza
    UNIVERSALGTA_OT_clean_model,
    UNIVERSALGTA_OT_purge_unused_data,
    UNIVERSALGTA_OT_purge_scene,
    UNIVERSALGTA_OT_clean_armatures,
    UNIVERSALGTA_OT_clean_empty_vertex_groups,
    UNIVERSALGTA_OT_fix_modifiers,
    UNIVERSALGTA_OT_remove_duplicates,
    UNIVERSALGTA_OT_optimize_mesh,
    
    # Operadores de normales
    UNIVERSALGTA_OT_fix_normals,
    UNIVERSALGTA_OT_auto_fix_normals_post_conversion,
    UNIVERSALGTA_OT_flip_normals,
    UNIVERSALGTA_OT_check_normals_consistency,
    
    # Operadores de nombres
    UNIVERSALGTA_OT_apply_custom_names,
    UNIVERSALGTA_OT_reset_names,
    UNIVERSALGTA_OT_validate_names,
    UNIVERSALGTA_OT_auto_generate_names,
    
    # Operadores de animaciones
    UNIVERSALGTA_OT_load_animation,
    UNIVERSALGTA_OT_clear_animations,
    UNIVERSALGTA_OT_refresh_animations_on_spacing_change,
    UNIVERSALGTA_OT_apply_facial_expressiveness,
    UNIVERSALGTA_OT_create_animation_files,
    
    # Operadores de exportación y espaciado
    UNIVERSALGTA_OT_export_textures,
    UNIVERSALGTA_OT_apply_spacing,
    
    # Operadores de referencia GTA SA
    UNIVERSALGTA_OT_show_gta_bone_reference,
    UNIVERSALGTA_OT_create_gta_armature_template,
    
    # Paneles principales
    UNIVERSALGTA_PT_MainPanel,
    UNIVERSALGTA_PT_ShapeKeysPanel,
    UNIVERSALGTA_PT_BoneMappingPanel,
    UNIVERSALGTA_PT_AdvancedPanel,
    UNIVERSALGTA_PT_UtilitiesPanel,
    UNIVERSALGTA_PT_AnimationsPanel,
    UNIVERSALGTA_PT_StatusPanel,
    
    # Paneles de créditos
    UNIVERSALGTA_OT_open_yoshi_channel,
    UNIVERSALGTA_PT_CreditsPanel,
    UNIVERSALGTA_PT_TestingPanel,
    UNIVERSALGTA_PT_NamingPanel,
]

# Agregar operadores de pose si están disponibles
if POSE_OPERATORS_AVAILABLE:
    classes.extend([
        UNIVERSALGTA_OT_apply_custom_pose,
        UNIVERSALGTA_OT_test_pose_application,
        UNIVERSALGTA_OT_verify_pose_setup,
        UNIVERSALGTA_OT_apply_manual_pose,
        UNIVERSALGTA_OT_reset_pose,
        UNIVERSALGTA_OT_copy_pose,
        UNIVERSALGTA_OT_bake_pose,
    ])

# Agregar operadores de Shape Keys si están disponibles
if SHAPE_KEYS_AVAILABLE:
    classes.extend([
        UNIVERSALGTA_OT_apply_all_shape_keys,
        UNIVERSALGTA_OT_backup_shape_keys,
        UNIVERSALGTA_OT_restore_shape_keys_backup,
        UNIVERSALGTA_OT_list_shape_keys,
    ])


def register():
    """Registro principal del addon"""
    print("[ADDON] === INICIANDO REGISTRO ===")
    
    # Registrar todas las clases
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
            print(f"[ADDON] ✓ Registrado: {cls.__name__}")
        except Exception as e:
            print(f"[ADDON] ✗ Error registrando {cls.__name__}: {e}")
    
    # CRÍTICO: Registrar las propiedades en Scene
    try:
        bpy.types.Scene.universal_gta_settings = PointerProperty(type=UniversalGTASettings)
        print("[ADDON] ✓ Propiedades registradas en Scene.universal_gta_settings")
    except Exception as e:
        print(f"[ADDON] ✗ Error crítico registrando propiedades: {e}")
    
    # Registrar validaciones
    register_validation()
    
    print("[ADDON] === REGISTRO COMPLETADO ===")
    print("[ADDON] ✓ Universal GTA SA Converter v3.2.3 ACTIVO")
    print("[ADDON] ✓ Accede desde: View3D > Sidebar > Universal GTA")


def unregister():
    """Desregistro del addon"""
    print("[ADDON] === INICIANDO DESREGISTRO ===")
    
    # Desregistrar propiedades de Scene
    try:
        del bpy.types.Scene.universal_gta_settings
        print("[ADDON] ✓ Propiedades eliminadas de Scene")
    except Exception as e:
        print(f"[ADDON] ⚠ Error eliminando propiedades: {e}")
    
    # Desregistrar todas las clases en orden inverso
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
            print(f"[ADDON] ✓ Desregistrado: {cls.__name__}")
        except Exception as e:
            print(f"[ADDON] ⚠ Error desregistrando {cls.__name__}: {e}")
    
    print("[ADDON] === DESREGISTRO COMPLETADO ===")


if __name__ == "__main__":
    register()