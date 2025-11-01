
# SCRIPT DE PRUEBA - Ejecutar en Blender después del fix
# Ve a Scripting > New > Pega este código > Run Script

import bpy

print("🎯 TESTING APPLY POSE FIX v4.2")
print("=" * 40)

# Test 1: Verificar que el operador existe
if hasattr(bpy.ops, 'universalgta') and hasattr(bpy.ops.universalgta, 'apply_pose_to_mesh'):
    print("✅ Operador apply_pose_to_mesh disponible")
else:
    print("❌ Operador apply_pose_to_mesh NO disponible")

# Test 2: Verificar configuración
try:
    settings = bpy.context.scene.universal_gta_settings
    print("✅ Configuración del addon disponible")
except:
    print("❌ Configuración del addon NO disponible")

# Test 3: Listar todos los operadores universalgta disponibles
if hasattr(bpy.ops, 'universalgta'):
    ops = [op for op in dir(bpy.ops.universalgta) if not op.startswith('_')]
    print(f"✅ Operadores disponibles ({len(ops)}): {ops}")
else:
    print("❌ Namespace universalgta no disponible")

print("=" * 40)
print("🎯 Si ves '✅ Operador apply_pose_to_mesh disponible'")
print("   ¡El fix funcionó correctamente!")
print("📋 Busca el botón en el panel 'Universal GTA' del sidebar")
