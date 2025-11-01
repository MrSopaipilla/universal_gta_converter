# SCRIPT DE PRUEBA - Ejecutar en Blender después del fix
# Ve a Scripting > New > Pega este código > Run Script

import bpy

print("🎯 TESTING COMPREHENSIVE FIX v3.0")
print("=" * 60)

# Test 1: Verificar operadores críticos
critical_operators = [
    'validate_mappings_and_disable_invalid',
    'smart_auto_detect',
    'execute_conversion',
    'apply_custom_pose',
    'reset_pose',
    'copy_pose',
    'apply_constraints'
]

print("🔍 VERIFICANDO OPERADORES CRÍTICOS:")
all_critical_found = True

for op_name in critical_operators:
    if hasattr(bpy.ops, 'universalgta') and hasattr(bpy.ops.universalgta, op_name):
        print(f"✅ {op_name}")
    else:
        print(f"❌ {op_name} - FALTANTE")
        all_critical_found = False

# Test 2: Verificar otros operadores importantes
other_operators = [
    'add_target_bones',
    'enable_only_valid_mappings',
    'configure_materials_gta'
]

print("\n🔍 VERIFICANDO OTROS OPERADORES:")
for op_name in other_operators:
    if hasattr(bpy.ops.universalgta, op_name):
        print(f"✅ {op_name}")
    else:
        print(f"⚠️ {op_name} - opcional")

# Test 3: Listar todos los operadores universalgta
if hasattr(bpy.ops, 'universalgta'):
    ops = [op for op in dir(bpy.ops.universalgta) if not op.startswith('_')]
    print(f"\n📊 Total operadores universalgta: {len(ops)}")
    print("Operadores registrados:")
    for i, op in enumerate(sorted(ops), 1):
        print(f"  {i:2d}. {op}")
else:
    print("\n❌ Namespace universalgta no disponible")
    all_critical_found = False

# RESULTADO FINAL
print("\n" + "=" * 60)
if all_critical_found:
    print("🎉 ¡TODOS los operadores críticos encontrados!")
    print("✅ El botón 'Convert to GTA SA' debería funcionar")
    print("✅ El panel 'Universal GTA' debería estar sin errores")
    print("\n🎯 INSTRUCCIONES:")
    print("1. Abre el sidebar (N) en 3D Viewport")
    print("2. Ve a la pestaña 'Universal GTA'")
    print("3. Configura source y target armatures")
    print("4. Usa 'Smart Auto-Detect'")
    print("5. Haz clic en 'Convert to GTA SA'")
else:
    print("❌ Algunos operadores críticos faltan")
    print("🔄 Intenta ejecutar emergency_fix.py")
    print("🔄 O contacta soporte técnico")

print("=" * 60)
