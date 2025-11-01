from .adjust_skin_height import UNIVERSALGTA_OT_adjust_skin_height
"""Registro de operadores del addon."""

import bpy
from bpy.utils import register_class, unregister_class

# Importar operadores de texturas

try:
    from .texture_export import (
        UNIVERSALGTA_OT_pre_conversion_rasterization_advanced,
        UNIVERSALGTA_OT_pre_conversion_rasterization,
        UNIVERSALGTA_OT_quick_texture_export,
        UNIVERSALGTA_OT_export_textures_enhanced,
        UNIVERSALGTA_OT_export_textures_with_browser,
        UNIVERSALGTA_OT_quick_material_rgb_fix,
        UNIVERSALGTA_OT_manual_smart_baking,
    )
    TEXTURE_OPERATORS = [
        UNIVERSALGTA_OT_pre_conversion_rasterization_advanced,
        UNIVERSALGTA_OT_pre_conversion_rasterization,
        UNIVERSALGTA_OT_quick_texture_export,
        UNIVERSALGTA_OT_export_textures_enhanced,
        UNIVERSALGTA_OT_export_textures_with_browser,
        UNIVERSALGTA_OT_quick_material_rgb_fix,
        UNIVERSALGTA_OT_manual_smart_baking,
    ]
    print("[OPERATORS] ✅ Operadores de texturas importados correctamente")
except ImportError as e:
    print(f"[OPERATORS] ❌ Error importando texture_export: {e}")
    TEXTURE_OPERATORS = []

# Importar operador de ángulo de brazos

try:
    from .arm_angle import UNIVERSALGTA_OT_set_arm_angles
    ARM_ANGLE_OPERATORS = [UNIVERSALGTA_OT_set_arm_angles]
    print(f"[OPERATORS] ✅ Operador de ángulo de brazos importado: {UNIVERSALGTA_OT_set_arm_angles.bl_idname}")
except Exception as e:
    print(f"[OPERATORS] ❌ Error importando arm_angle: {str(e)}")
    ARM_ANGLE_OPERATORS = []

# Importar operador de ángulo de piernas

try:
    from .leg_roll import UNIVERSALGTA_OT_apply_leg_roll
    LEG_ROLL_OPERATORS = [UNIVERSALGTA_OT_apply_leg_roll]
    print(f"[OPERATORS] ✅ Operador de ángulo de piernas importado: {UNIVERSALGTA_OT_apply_leg_roll.bl_idname}")
except Exception as e:
    print(f"[OPERATORS] ❌ Error importando leg_roll: {str(e)}")
    LEG_ROLL_OPERATORS = []

# Importar otros operadores

# Lista para almacenar todos los operadores
ALL_OPERATORS = []
ALL_OPERATORS.extend(TEXTURE_OPERATORS)  # Texturas PRIMERO
ALL_OPERATORS.extend(ARM_ANGLE_OPERATORS)  # Añadir operador de ángulo de brazos
ALL_OPERATORS.extend(LEG_ROLL_OPERATORS)  # Añadir operador de ángulo de piernas
ALL_OPERATORS.extend([UNIVERSALGTA_OT_adjust_skin_height])

print("[OPERATORS] ✅ Estado de operadores de brazos:", ARM_ANGLE_OPERATORS)  # Debug

# Importar otros módulos de operadores disponibles
OPERATORS_MODULES = [
    'conversion', 'cleanup', 'export', 'mapping', 'materials', 
    'naming', 'normals', 'pose', 'spacing', 'validation_fixed',
    'animations', 'final_cleanup', 'gta_complete_conversion',
    'arm_angle', 'leg_roll'  # Añadir los módulos de control de ángulos
]

for module_name in OPERATORS_MODULES:
    try:
        module = __import__(f'.{module_name}', package=__name__, level=1)
        if hasattr(module, 'classes'):
            ALL_OPERATORS.extend(module.classes)
            print(f"[OPERATORS] ✅ {module_name} importado ({len(module.classes)} operadores)")
        elif hasattr(module, 'register'):
            # Módulo con función register pero sin lista de clases explícita
            print(f"[OPERATORS] ✅ {module_name} disponible (registro manual)")
    except ImportError as e:
        print(f"[OPERATORS] ⚠️ {module_name} no disponible: {e}")
    except Exception as e:
        print(f"[OPERATORS] ❌ Error cargando {module_name}: {e}")

# Registro

def register():
    """Registrar todos los operadores"""
    print("\n[OPERATORS] ==========================================")
    print("[OPERATORS] INICIANDO REGISTRO DE OPERADORES")
    print("[OPERATORS] ==========================================")
    
    registered_count = 0
    failed_count = 0
    
    # Registrar operadores de la lista ALL_OPERATORS
    for operator_class in ALL_OPERATORS:
        try:
            register_class(operator_class)
            print(f"[OPERATORS] ✅ Registrado: {operator_class.bl_idname}")
            registered_count += 1
        except ValueError as e:
            if "already registered" in str(e):
                print(f"[OPERATORS] ⚠️ Ya registrado: {operator_class.bl_idname}")
                registered_count += 1
            else:
                print(f"[OPERATORS] ❌ Error registrando {operator_class.bl_idname}: {e}")
                failed_count += 1
        except Exception as e:
            print(f"[OPERATORS] ❌ Error crítico registrando {operator_class.bl_idname}: {e}")
            failed_count += 1
    
    # Registrar módulos con función register manual
    for module_name in OPERATORS_MODULES:
        try:
            module = __import__(f'.{module_name}', package=__name__, level=1)
            if hasattr(module, 'register') and not hasattr(module, 'classes'):
                module.register()
                print(f"[OPERATORS] ✅ Registrado manualmente: {module_name}")
                registered_count += 1
        except Exception as e:
            print(f"[OPERATORS] ❌ Error registro manual {module_name}: {e}")
            failed_count += 1
    
    print("[OPERATORS] ==========================================")
    print(f"[OPERATORS] REGISTRO COMPLETADO")
    print(f"[OPERATORS] ✅ Éxitos: {registered_count}")
    print(f"[OPERATORS] ❌ Errores: {failed_count}")
    print("[OPERATORS] ==========================================")
    
    # Verificación de operadores críticos de texturas
    critical_operators = [
        "universalgta.quick_texture_export",
        "universalgta.export_textures_enhanced", 
        "universalgta.export_textures_with_browser",
        "universalgta.quick_material_rgb_fix",
        "universalgta.manual_smart_baking",
        "universalgta.pre_conversion_rasterization_advanced",
        "universalgta.pre_conversion_rasterization"
    ]
    
    print("\n[OPERATORS] 🔍 VERIFICACIÓN DE OPERADORES CRÍTICOS:")
    for op_id in critical_operators:
        try:
            # Verificar si el operador existe en bpy.ops
            op_module, op_name = op_id.split('.')
            if hasattr(bpy.ops, op_module) and hasattr(getattr(bpy.ops, op_module), op_name):
                print(f"[OPERATORS] ✅ {op_id} - DISPONIBLE")
            else:
                print(f"[OPERATORS] ❌ {op_id} - NO DISPONIBLE")
        except Exception as e:
            print(f"[OPERATORS] ❌ {op_id} - ERROR VERIFICANDO: {e}")


def unregister():
    """Desregistrar todos los operadores"""
    print("\n[OPERATORS] Desregistrando operadores...")
    
    unregistered_count = 0
    
    # Desregistrar operadores de la lista ALL_OPERATORS
    for operator_class in reversed(ALL_OPERATORS):
        try:
            unregister_class(operator_class)
            unregistered_count += 1
        except ValueError:
            pass  # No estaba registrado
        except Exception as e:
            print(f"[OPERATORS] ❌ Error desregistrando {operator_class.bl_idname}: {e}")
    
    # Desregistrar módulos con función unregister manual
    for module_name in reversed(OPERATORS_MODULES):
        try:
            module = __import__(f'.{module_name}', package=__name__, level=1)
            if hasattr(module, 'unregister'):
                module.unregister()
                unregistered_count += 1
        except Exception as e:
            print(f"[OPERATORS] ❌ Error desregistro manual {module_name}: {e}")
    
    print(f"[OPERATORS] ✅ {unregistered_count} operadores desregistrados")


# Mantener compatibilidad con versiones anteriores
classes = ALL_OPERATORS

if __name__ == "__main__":
    register()
