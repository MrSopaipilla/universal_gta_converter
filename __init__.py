"""
Universal GTA SA Converter v1.0

"""

bl_info = {
    "name": "Universal to GTA SA Converter",
    "author": "YoshiMaincra + Cursor AI",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Tool > Universal GTA",
    "description": "Convierte armatures personalizados a GTA SA con Smart Auto-Detect inteligente (Mixamo, Source/SFM, etc.), sistema de auto-corrección mejorado y herramientas avanzadas. Compatible con Blender 4.5",
    "category": "Rigging",
}

import bpy
import re
from bpy.props import PointerProperty, FloatProperty, BoolProperty

# Registro de propiedades personalizadas
def register_custom_properties():
    # Slider de brazos (permite sumar/restar; la aplicación se hace con el botón)
    bpy.types.Scene.gta_arm_angle = FloatProperty(
        name="Arm Angle",
        description="Ángulo de rotación para los brazos (+ derecho, - izquierdo)",
        default=0.0,
        min=-360.0,
        max=360.0,
        step=10,
        precision=1,
        subtype='ANGLE',
        unit='ROTATION'
    )
    # Bases persistentes para cálculo simétrico sin acumulación (grados)
    bpy.types.Scene.gta_arm_roll_base_left = FloatProperty(
        name="_arm_base_L",
        description="Base de roll para L UpperArm (oculto)",
        default=0.0,
        subtype='ANGLE',
        options={'HIDDEN'}
    )
    bpy.types.Scene.gta_arm_roll_base_right = FloatProperty(
        name="_arm_base_R",
        description="Base de roll para R UpperArm (oculto)",
        default=0.0,
        subtype='ANGLE',
        options={'HIDDEN'}
    )
    bpy.types.Scene.gta_arm_roll_has_base = BoolProperty(
        name="_arm_base_set",
        description="Indica si la base de brazos fue capturada",
        default=False,
        options={'HIDDEN'}
    )
    
    bpy.types.Scene.gta_leg_roll_angle = FloatProperty(
        name="Leg Roll Angle",
        description="Ángulo de rotación para las piernas (+ derecho, - izquierdo)",
        default=0.0,
        min=-360.0,
        max=360.0,
        step=10,
        precision=1,
        subtype='ANGLE',
        unit='ROTATION'
    )

    # Propiedad para ajuste de altura del skin (metros)
    bpy.types.Scene.gta_skin_height = FloatProperty(
        name="Skin Height (m)",
        description="Altura del skin en metros (medida en eje Z)",
        default=1.8,
        min=0.1,
        max=10.0,
        precision=3,
        unit='LENGTH'
    )

def unregister_custom_properties():
    if hasattr(bpy.types.Scene, "gta_arm_angle"):
        del bpy.types.Scene.gta_arm_angle
    if hasattr(bpy.types.Scene, "gta_arm_roll_base_left"):
        del bpy.types.Scene.gta_arm_roll_base_left
    if hasattr(bpy.types.Scene, "gta_arm_roll_base_right"):
        del bpy.types.Scene.gta_arm_roll_base_right
    if hasattr(bpy.types.Scene, "gta_arm_roll_has_base"):
        del bpy.types.Scene.gta_arm_roll_has_base
    if hasattr(bpy.types.Scene, "gta_leg_roll_angle"):
        del bpy.types.Scene.gta_leg_roll_angle
    if hasattr(bpy.types.Scene, "gta_skin_height"):
        del bpy.types.Scene.gta_skin_height

# Verificación de versión de Blender
def check_blender_version():
    """Verifica que estemos en Blender 5.0+"""
    if bpy.app.version < (5, 0, 0):
        print("[ADDON] [WARNING] Advertencia: Este addon fue diseñado para Blender 5.0+")
        print(f"[ADDON] Versión actual: {bpy.app.version_string}")
    else:
        print(f"[ADDON] [OK] Blender 5.0+ detectado: {bpy.app.version_string}")

check_blender_version()

# === PASO 1: IMPORTAR CONFIGURACIÓN (CRÍTICO) ===
print("[ADDON] === FASE 1: IMPORTANDO CONFIGURACIÓN ===")
try:
    from .config import UniversalGTASettings, BoneMappingItem, register_validation
    CONFIG_AVAILABLE = True
    print("[ADDON] [OK] Configuración importada correctamente")
except ImportError as e:
    print(f"[ADDON] [ERROR] ERROR CRÍTICO - config.py: {e}")
    CONFIG_AVAILABLE = False

if not CONFIG_AVAILABLE:
    def register():
        print("[ADDON] [ERROR] No se puede cargar el addon sin config.py")
        return
        
    def unregister():
        print("[ADDON] [ERROR] No se puede descargar el addon sin config.py")
        pass
else:
    # === PASO 2: IMPORTAR SISTEMA DE PERFILES ===
    print("[ADDON] === FASE 2: IMPORTANDO SISTEMA DE PERFILES ===")
    try:
        from .rig_profiles import RigProfileSystem
        RIG_PROFILES_AVAILABLE = True
        print("[ADDON] [OK] Sistema de perfiles de rigs (Smart Auto-Detect) disponible")
    except ImportError as e:
        print(f"[ADDON] [WARNING] rig_profiles.py no disponible: {e}")
        RIG_PROFILES_AVAILABLE = False

    # === PASO 3: IMPORTAR CONVERSOR PRINCIPAL ===
    print("[ADDON] === FASE 3: IMPORTANDO CONVERSOR ===")
    try:
        from .converter import UniversalGTAConverter
        CONVERTER_AVAILABLE = True
        print("[ADDON] [OK] Conversor principal disponible")
    except ImportError as e:
        print(f"[ADDON] [WARNING] converter.py no disponible: {e}")
        CONVERTER_AVAILABLE = False

    # === PASO 4: IMPORTAR EXTERNAL POSE CALLER ===
    print("[ADDON] === FASE 4: IMPORTANDO EXTERNAL POSE CALLER ===")
    try:
        from . import external_pose_caller
        EXTERNAL_POSE_AVAILABLE = True
        print("[ADDON] [OK] External pose caller disponible")
    except ImportError as e:
        print(f"[ADDON] [WARNING] external_pose_caller.py no disponible: {e}")
        EXTERNAL_POSE_AVAILABLE = False

    # === PASO 5: IMPORTAR OPERADORES (CRÍTICO) ===
    print("[ADDON] === FASE 5: IMPORTANDO OPERADORES ===")
    
    # Operadores de conversión (OBLIGATORIOS) - SINTAXIS CORREGIDA
    CONVERSION_OPERATORS = []
    
    # Importar operadores de conversión básicos
    try:
        from .operators.conversion import (
            UNIVERSALGTA_OT_execute_conversion,
            UNIVERSALGTA_OT_smart_auto_detect,
            UNIVERSALGTA_OT_execute_conversion_no_autofix,
            UNIVERSALGTA_OT_auto_detect_bones,
        )
        CONVERSION_OPERATORS.extend([
            UNIVERSALGTA_OT_execute_conversion,
            UNIVERSALGTA_OT_smart_auto_detect,
            UNIVERSALGTA_OT_execute_conversion_no_autofix,
            UNIVERSALGTA_OT_auto_detect_bones,
        ])
        print("[OPERATORS] ✅ conversion.py importado")
    except ImportError as e:
        print(f"[ADDON] [ERROR] Error importando operadores básicos: {e}")

    # Importar operador de conversión completa
    try:
        from .operators.gta_complete_conversion import UNIVERSALGTA_OT_complete_gta_conversion
        CONVERSION_OPERATORS.append(UNIVERSALGTA_OT_complete_gta_conversion)
        print("[OPERATORS] ✅ gta_complete_conversion.py importado")
    except ImportError as e:
        print(f"[ADDON] [WARNING] No se pudo importar complete_gta_conversion: {e}")
        print("[ADDON] [INFO] El addon funcionará sin este operador")

    print(f"[ADDON] [INFO] Total operadores de conversión cargados: {len(CONVERSION_OPERATORS)}")

    # Operadores de mapeo (IMPORTANTES)
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
            UNIVERSALGTA_OT_enable_high_confidence,
            UNIVERSALGTA_OT_enable_only_valid_mappings,
        )
        MAPPING_OPERATORS = [
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
            UNIVERSALGTA_OT_enable_only_valid_mappings,
        ]
        print("[ADDON] [OK] Operadores de mapeo importados")
    except ImportError as e:
        print(f"[ADDON] [WARNING] operators/mapping.py: {e}")
        MAPPING_OPERATORS = []

    # Operadores de validación (IMPORTANTES)
    try:
        from .operators.validation_fixed import (
            UNIVERSALGTA_OT_validate_mappings_fixed,
            UNIVERSALGTA_OT_fix_mappings_automatically,
            UNIVERSALGTA_OT_ignore_naming_warnings,
            UNIVERSALGTA_OT_validate_mappings_and_disable_invalid,
        )
        VALIDATION_OPERATORS = [
            UNIVERSALGTA_OT_validate_mappings_fixed,
            UNIVERSALGTA_OT_fix_mappings_automatically,
            UNIVERSALGTA_OT_ignore_naming_warnings,
            UNIVERSALGTA_OT_validate_mappings_and_disable_invalid,
        ]
        print("[ADDON] [OK] Operadores de validación importados")
    except ImportError as e:
        print(f"[ADDON] [WARNING] operators/validation_fixed.py: {e}")
        VALIDATION_OPERATORS = []

    # Operadores de materiales
    try:
        from .operators.materials import (
            UNIVERSALGTA_OT_configure_materials_gta,
            UNIVERSALGTA_OT_apply_gta_color_all,
            UNIVERSALGTA_OT_verify_materials_gta,
        )
        MATERIAL_OPERATORS = [
            UNIVERSALGTA_OT_configure_materials_gta,
            UNIVERSALGTA_OT_apply_gta_color_all,
            UNIVERSALGTA_OT_verify_materials_gta,
        ]
        print("[ADDON] [OK] Operadores de materiales importados")
    except ImportError as e:
        print(f"[ADDON] [WARNING] operators/materials.py: {e}")
        MATERIAL_OPERATORS = []
        
    # === OPERADORES DE TEXTURAS (COMPLETOS) ===
    try:
        from .operators.texture_export import (
            UNIVERSALGTA_OT_pre_conversion_rasterization,
            UNIVERSALGTA_OT_quick_texture_export,
            UNIVERSALGTA_OT_export_textures_enhanced,
            UNIVERSALGTA_OT_export_textures_with_browser,
            UNIVERSALGTA_OT_quick_material_rgb_fix,
            UNIVERSALGTA_OT_manual_smart_baking,
        )
        TEXTURE_EXPORT_OPERATORS = [
            UNIVERSALGTA_OT_pre_conversion_rasterization,
            UNIVERSALGTA_OT_quick_texture_export,
            UNIVERSALGTA_OT_export_textures_enhanced,
            UNIVERSALGTA_OT_export_textures_with_browser,
            UNIVERSALGTA_OT_quick_material_rgb_fix,
            UNIVERSALGTA_OT_manual_smart_baking,
        ]
        print("[ADDON] ✅ Operadores de texturas importados desde texture_export.py")
    except ImportError as e:
        print(f"[ADDON] ❌ Error importando texture_export.py: {e}")
        TEXTURE_EXPORT_OPERATORS = []

    # Operadores de pose
    try:
        from .operators.pose import (
            UNIVERSALGTA_OT_apply_custom_pose,
            UNIVERSALGTA_OT_reset_pose,
            UNIVERSALGTA_OT_copy_pose,
            UNIVERSALGTA_OT_apply_constraints,
        )
        POSE_OPERATORS = [
            UNIVERSALGTA_OT_apply_custom_pose,
            UNIVERSALGTA_OT_reset_pose,
            UNIVERSALGTA_OT_copy_pose,
            UNIVERSALGTA_OT_apply_constraints,
        ]
        print("[ADDON] [OK] Pose operators imported (Apply Pose to Mesh included)")
    except ImportError as e:
        print(f"[ADDON] [WARNING] pose operators error: {e}")
        POSE_OPERATORS = []

    # Operadores opcionales (resto)
    OPTIONAL_OPERATORS = []
    
    # Cleanup (clean_model y clean_armatures removidos - eran redundantes)
    try:
        from .operators.cleanup import (
            UNIVERSALGTA_OT_purge_unused_data,
            UNIVERSALGTA_OT_purge_scene,
            UNIVERSALGTA_OT_clean_empty_vertex_groups,
            UNIVERSALGTA_OT_fix_modifiers,
            UNIVERSALGTA_OT_remove_duplicates,
            UNIVERSALGTA_OT_optimize_mesh
        )
        OPTIONAL_OPERATORS.extend([
            UNIVERSALGTA_OT_purge_unused_data,
            UNIVERSALGTA_OT_purge_scene,
            UNIVERSALGTA_OT_clean_empty_vertex_groups,
            UNIVERSALGTA_OT_fix_modifiers,
            UNIVERSALGTA_OT_remove_duplicates,
            UNIVERSALGTA_OT_optimize_mesh
        ])
    except ImportError:
        pass

    # Normals
    try:
        from .operators.normals import (
            UNIVERSALGTA_OT_fix_normals,
            UNIVERSALGTA_OT_auto_fix_normals_post_conversion,
            UNIVERSALGTA_OT_flip_normals,
            UNIVERSALGTA_OT_check_normals_consistency
        )
        OPTIONAL_OPERATORS.extend([
            UNIVERSALGTA_OT_fix_normals,
            UNIVERSALGTA_OT_auto_fix_normals_post_conversion,
            UNIVERSALGTA_OT_flip_normals,
            UNIVERSALGTA_OT_check_normals_consistency
        ])
    except ImportError:
        pass

    # Naming
    try:
        from .operators.naming import (
            UNIVERSALGTA_OT_apply_custom_names,
            UNIVERSALGTA_OT_reset_names,
            UNIVERSALGTA_OT_validate_names,
            UNIVERSALGTA_OT_auto_generate_names
        )
        OPTIONAL_OPERATORS.extend([
            UNIVERSALGTA_OT_apply_custom_names,
            UNIVERSALGTA_OT_reset_names,
            UNIVERSALGTA_OT_validate_names,
            UNIVERSALGTA_OT_auto_generate_names
        ])
    except ImportError:
        pass

    # Export y Spacing
    try:
        from .operators.export import UNIVERSALGTA_OT_export_textures
        OPTIONAL_OPERATORS.append(UNIVERSALGTA_OT_export_textures)
    except ImportError:
        pass

    try:
        from .operators.spacing import UNIVERSALGTA_OT_apply_spacing
        OPTIONAL_OPERATORS.append(UNIVERSALGTA_OT_apply_spacing)
    except ImportError:
        pass

    # === PASO 6: IMPORTAR UI LIST ===
    print("[ADDON] === FASE 6: IMPORTANDO UI LIST ===")
    class UNIVERSALGTA_UL_BoneMappingList(bpy.types.UIList):
        def filter_items(self, context, data, propname):
            # Solo filtra, NO ordena, así el orden visual respeta la colección
            items = getattr(data, propname)
            filter_name = self.filter_name
            flt_flags = []
            if filter_name:
                filter_name = filter_name.lower()
                for item in items:
                    src = getattr(item, 'source_bone', '').lower()
                    tgt = getattr(item, 'target_bone', '').lower()
                    if filter_name in src or filter_name in tgt:
                        flt_flags.append(self.bitflag_filter_item)
                    else:
                        flt_flags.append(0)
            else:
                flt_flags = [self.bitflag_filter_item] * len(items)
            # NO ordenar: dejar flt_neworder vacío para respetar el orden real
            flt_neworder = []
            return flt_flags, flt_neworder
        
        
        def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
            """Dibuja cada elemento de la lista con info de Smart Auto-Detect"""
            
            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                row = layout.row(align=True)
                row.alignment = 'LEFT'
                
                # Checkbox
                checkbox_col = row.column()
                checkbox_col.scale_x = 0.8
                checkbox_col.prop(item, "enabled", text="")
                
                # Icono especial para Smart Auto-Detect
                if "Smart Auto" in item.detection_method:
                    icon_col = row.column()
                    icon_col.scale_x = 0.6
                    icon_col.label(text="[BRAIN]", icon='AUTO')
                
                # Source bone
                source_col = row.column()
                source_col.scale_x = 2.0
                if item.source_bone:
                    source_col.label(text=item.source_bone)
                else:
                    source_col.label(text="<None>")
                
                # Flecha
                arrow_col = row.column()
                arrow_col.scale_x = 0.6
                arrow_col.label(text="→")
                
                # Target bone
                target_col = row.column()
                target_col.scale_x = 2.0
                if item.target_bone:
                    target_col.label(text=item.target_bone)
                else:
                    target_col.label(text="<None>")
                
                # Confidence para Smart Auto-Detect
                if "Smart Auto" in item.detection_method and item.confidence > 0.6:
                    conf_col = row.column()
                    conf_col.scale_x = 0.7
                    conf_col.label(text=f"{item.confidence:.1%}")
            
            elif self.layout_type == 'GRID':
                layout.alignment = 'CENTER'
                layout.scale_y = 0.8
                if "Smart Auto" in item.detection_method:
                    layout.label(text="[BRAIN]")
                elif item.enabled:
                    layout.label(text="✓")
                else:
                    layout.label(text="[ERROR]")

    # === PASO 7: IMPORTAR PANELES ===
    print("[ADDON] === FASE 7: IMPORTANDO PANELES ===")
    try:
        from .panels.main_panel import (
            UNIVERSALGTA_PT_MainPanel,           
            UNIVERSALGTA_PT_AdvancedMappingPanel,
            UNIVERSALGTA_PT_QuickActionsPanel,   
            UNIVERSALGTA_PT_UtilitiesPanel,      
            UNIVERSALGTA_PT_InfoPanel,
            UNIVERSALGTA_PT_NameAuthorPanel,    
        )
        MAIN_PANELS = [
            UNIVERSALGTA_PT_MainPanel,           # 1. Principal
            UNIVERSALGTA_PT_NameAuthorPanel,     # 2. Name/Author
            UNIVERSALGTA_PT_AdvancedMappingPanel,# 3. Advanced (CORRECTO)  
            UNIVERSALGTA_PT_QuickActionsPanel,   # 4. Quick Actions (CORRECTO)
            UNIVERSALGTA_PT_UtilitiesPanel,      # 5. Utilities
            UNIVERSALGTA_PT_InfoPanel,           # 6. Info
        ]
        print("[PANELS] ✅ Paneles principales importados correctamente")
    except ImportError as e:
        print(f"[ADDON] [WARNING] panels/main_panel.py: {e}")
        MAIN_PANELS = []


    try:
        from .panels.credits import (
            UNIVERSALGTA_OT_open_yoshi_channel,
        )
        CREDITS_PANELS = [
            UNIVERSALGTA_OT_open_yoshi_channel,
        ]
        print("[PANELS] ✅ Operador de créditos importado correctamente")
    except ImportError as e:
        print(f"[ADDON] [WARNING] panels/credits.py: {e}")
        CREDITS_PANELS = []

    # === CONSTRUIR LISTA FINAL DE CLASES ===
    print("[ADDON] === FASE 8: CONSTRUYENDO LISTA DE CLASES ===")
    
    # ORDEN CRÍTICO: PropertyGroups primero
    all_classes = [
        BoneMappingItem,
        UniversalGTASettings,
        UNIVERSALGTA_UL_BoneMappingList,
    ]
    
    # Luego operadores (orden específico)
    all_classes.extend(CONVERSION_OPERATORS)      # Conversión PRIMERO (incluye complete_gta_conversion)
    all_classes.extend(POSE_OPERATORS)            # Pose SEGUNDO
    all_classes.extend(MAPPING_OPERATORS)         # Mapeo TERCERO
    all_classes.extend(VALIDATION_OPERATORS)      # Validación CUARTO
    all_classes.extend(TEXTURE_EXPORT_OPERATORS)  # Texturas QUINTO
    all_classes.extend(MATERIAL_OPERATORS)        # Materiales SEXTO
    all_classes.extend(OPTIONAL_OPERATORS)        # Opcionales ÚLTIMO
    
    # Finalmente paneles (padre primero)
    all_classes.extend(MAIN_PANELS)               # Main panels PRIMERO
    all_classes.extend(CREDITS_PANELS)            # Paneles de créditos

    # Registrar operador de ángulo de pierna
    try:
        from .operators.leg_roll import UNIVERSALGTA_OT_apply_leg_roll
        all_classes.append(UNIVERSALGTA_OT_apply_leg_roll)
        print("[ADDON] ✓ Operador de ángulo de pierna registrado")
    except Exception as e:
        print(f"[ADDON] [ERROR] No se pudo registrar el operador de ángulo de pierna: {e}")

    # Registrar operador de ajuste de altura del skin
    try:
        from .operators.adjust_skin_height import UNIVERSALGTA_OT_adjust_skin_height
        all_classes.append(UNIVERSALGTA_OT_adjust_skin_height)
        print("[ADDON] ✓ Operador adjust_skin_height registrado")
    except Exception as e:
        print(f"[ADDON] [ERROR] No se pudo registrar adjust_skin_height: {e}")

    # Eliminar duplicados de clases
    seen = set()
    all_classes = [cls for cls in all_classes if not (cls in seen or seen.add(cls))]

    # === FUNCIONES DE REGISTRO ===
    def register():
        """Registra todas las clases del addon EN ORDEN CORRECTO"""
        print("[ADDON] ==========================================")
        print("[ADDON] Iniciando registro de Universal GTA Converter v4.0.1")
        print(f"[ADDON] Compatible con Blender 5.0+ (actual: {bpy.app.version_string})")
        
        # Registrar propiedades personalizadas
        register_custom_properties()
        print("[ADDON] ✓ Propiedades personalizadas registradas")
        # Registrar operador de ángulo de brazo
        try:
            from .operators.arm_angle import UNIVERSALGTA_OT_set_arm_angles
            bpy.utils.register_class(UNIVERSALGTA_OT_set_arm_angles)
            print("[ADDON] ✓ Operador de ángulo de brazo registrado")
        except Exception as e:
            print(f"[ADDON] [ERROR] No se pudo registrar el operador de ángulo de brazo: {e}")
        
        # VALIDAR ORDEN DE REGISTRO DE PANELES
        print("[ADDON] 🎯 Validando orden de paneles...")
        panel_order_check = [
            "UNIVERSALGTA_PT_main_panel",
            "UNIVERSALGTA_PT_advanced_mapping_panel", 
            "UNIVERSALGTA_PT_quick_actions_panel",
            "UNIVERSALGTA_PT_utilities_panel",
            "UNIVERSALGTA_PT_info_panel"
        ]
        print(f"[ADDON] ✓ Orden esperado: {' → '.join(panel_order_check)}")
        
        if not CONVERSION_OPERATORS:
            print("[ADDON] [ERROR] ERROR CRÍTICO: No hay operadores de conversión")
            return
        
        registered_count = 0
        failed_count = 0
        
        print(f"[ADDON] Total de clases a registrar: {len(all_classes)}")
        
        for i, cls in enumerate(all_classes):
            try:
                bpy.utils.register_class(cls)
                registered_count += 1
                print(f"[ADDON] ✓ [{i+1:2d}/{len(all_classes)}] {cls.__name__}")
            except Exception as e:
                failed_count += 1
                print(f"[ADDON] [ERROR] [{i+1:2d}/{len(all_classes)}] {cls.__name__}: Error: {e}")
        
        # Registrar la propiedad principal en la escena
        if not hasattr(bpy.types.Scene, 'universal_gta_settings'):
            try:
                bpy.types.Scene.universal_gta_settings = PointerProperty(type=UniversalGTASettings)
                print("[ADDON] ✓ Propiedad universal_gta_settings registrada")
            except Exception as e:
                print(f"[ADDON] [ERROR] Error registrando propiedad: {e}")
                failed_count += 1
        else:
            print("[ADDON] [INFO] universal_gta_settings ya estaba registrada")
        
        # Registrar validadores
        try:
            register_validation()
            print("[CONFIG] Validadores de nombres registrados")
            print("[ADDON] ✓ Validadores registrados")
        except Exception as e:
            print(f"[ADDON] [WARNING] Error registrando validadores: {e}")
        
        print("[ADDON] ==========================================")
        print(f"[ADDON] REGISTRO COMPLETADO: {registered_count} clases registradas")
        if failed_count > 0:
            print(f"[ADDON] [WARNING] {failed_count} errores de registro")
        else:
            print("[ADDON] [PARTY] REGISTRO PERFECTO - Sin errores!")
        
        print("[ADDON] ==========================================")
        print("[ADDON] [NEW] CARACTERÍSTICAS v4.0.1:")
        print("[ADDON] - [BRAIN] Smart Auto-Detect inteligente")
        print("[ADDON] - [TARGET] Detección automática de rigs")
        print("[ADDON] - [TOOL] Auto-correccion mejorada")
        print("[ADDON] - [ART] Configuracion de materiales (#E7E7E7FF)")
        print("[ADDON] - [LINK] Integracion DragonFF automatica")
        print("[ADDON] - [PC] Compatible con Blender 5.0")
        print("[ADDON] ==========================================")
        print("[ADDON] MÓDULOS DISPONIBLES:")
        print(f"[ADDON] - [OK] Configuración (config.py)")
        print(f"[ADDON] - {'[OK]' if CONVERSION_OPERATORS else '[ERROR]'} Operadores de conversión (CORE)")
        print(f"[ADDON] - {'[OK]' if RIG_PROFILES_AVAILABLE else '[WARNING]'} Sistema de perfiles de rigs")
        print(f"[ADDON] - {'[OK]' if CONVERTER_AVAILABLE else '[WARNING]'} Conversor principal")
        print(f"[ADDON] - {'[OK]' if EXTERNAL_POSE_AVAILABLE else '[WARNING]'} External pose caller")
        print(f"[ADDON] - {'[OK]' if MAPPING_OPERATORS else '[WARNING]'} Operadores de mapeo")
        print(f"[ADDON] - {'[OK]' if VALIDATION_OPERATORS else '[WARNING]'} Operadores de validación")
        print(f"[ADDON] - {'[OK]' if MAIN_PANELS else '[WARNING]'} Paneles principales")
        print(f"[ADDON] - {'[OK]' if CREDITS_PANELS else '[WARNING]'} Paneles de créditos")
        print("[ADDON] ==========================================")
        
        if registered_count > 0:
            print("[ADDON] [TARGET] CÓMO USAR:")
            print("[ADDON] 1. Abrir sidebar (N) en 3D Viewport")
            print("[ADDON] 2. Ir a pestaña 'Universal GTA'")
            print("[ADDON] 3. Seleccionar armatures en 'Setup'")
            print("[ADDON] 4. Usar '[BRAIN] Smart Auto-Detect'")
            print("[ADDON] 5. Hacer clic en '[ROCKET] Convert to GTA SA'")
            print("[ADDON] ==========================================")

    def unregister():
        """Desregistra todas las clases del addon EN ORDEN INVERSO"""
        print("[ADDON] Desregistrando Universal GTA Converter v4.0.1...")
        
        # Desregistrar previews de avatares
        try:
            from .panels.credits import unregister as credits_unregister
            credits_unregister()
        except Exception:
            pass
        
        # Desregistrar operador de ángulo de brazo
        try:
            from .operators.arm_angle import UNIVERSALGTA_OT_set_arm_angles
            bpy.utils.unregister_class(UNIVERSALGTA_OT_set_arm_angles)
            print("[ADDON] ✓ Operador de ángulo de brazo desregistrado")
        except Exception as e:
            print(f"[ADDON] [ERROR] No se pudo desregistrar el operador de ángulo de brazo: {e}")
        # Eliminar la propiedad de la escena PRIMERO
        try:
            if hasattr(bpy.types.Scene, 'universal_gta_settings'):
                del bpy.types.Scene.universal_gta_settings
            print("[ADDON] ✓ Propiedad universal_gta_settings eliminada")
        except Exception as e:
            print(f"[ADDON] [ERROR] Error eliminando propiedad: {e}")
        
        # Desregistrar clases EN ORDEN INVERSO
        failed_count = 0
        for cls in reversed(all_classes):
            try:
                bpy.utils.unregister_class(cls)
            except Exception as e:
                if "missing bl_rna" not in str(e):
                    print(f"[ADDON] [ERROR] Error desregistrando {cls.__name__}: {e}")
                    failed_count += 1
        
        if failed_count == 0:
            print("[ADDON] [OK] Universal GTA Converter v4.0.1 desregistrado correctamente")
        else:
            print(f"[ADDON] [WARNING] Desregistrado con {failed_count} errores menores")


if __name__ == "__main__":
    register()