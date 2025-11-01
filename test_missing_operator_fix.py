# SCRIPT DE PRUEBA - Verificar operador validate_mappings_and_disable_invalid
# Ve a Scripting > New > Pega este código > Run Script

import bpy

print("🔍 TESTING MISSING OPERATOR FIX")
print("=" * 60)

# Test específico para el operador problemático
operator_id = "universalgta.validate_mappings_and_disable_invalid"

print(f"🎯 Verificando operador: {operator_id}")

# Verificar si existe el namespace
if not hasattr(bpy.ops, 'universalgta'):
    print("❌ Namespace 'universalgta' no disponible")
    print("💡 El addon no está cargado correctamente")
else:
    print("✅ Namespace 'universalgta' disponible")
    
    # Listar todos los operadores universalgta
    ops = [op for op in dir(bpy.ops.universalgta) if not op.startswith('_')]
    print(f"📊 Total operadores universalgta: {len(ops)}")
    
    # Verificar el operador específico
    if hasattr(bpy.ops.universalgta, 'validate_mappings_and_disable_invalid'):
        print(f"✅ Operador '{operator_id}' ENCONTRADO")
        
        # Intentar obtener información del operador
        try:
            operator = getattr(bpy.ops.universalgta, 'validate_mappings_and_disable_invalid')
            print(f"✅ Operador es accesible: {operator}")
        except Exception as e:
            print(f"⚠️ Error accediendo al operador: {e}")
            
    else:
        print(f"❌ Operador '{operator_id}' NO ENCONTRADO")
        print("🔍 Operadores similares disponibles:")
        for op in ops:
            if 'validate' in op.lower() or 'mapping' in op.lower():
                print(f"  - {op}")

print("\n📋 TODOS LOS OPERADORES UNIVERSALGTA:")
if hasattr(bpy.ops, 'universalgta'):
    for i, op in enumerate(sorted(ops), 1):
        status = "✅" if op == "validate_mappings_and_disable_invalid" else "  "
        print(f"{status} {i:2d}. {op}")

print("\n" + "=" * 60)
if hasattr(bpy.ops, 'universalgta') and hasattr(bpy.ops.universalgta, 'validate_mappings_and_disable_invalid'):
    print("🎉 ¡OPERADOR DISPONIBLE! El fix funcionó correctamente")
    print("✅ El panel 'Universal GTA' debería funcionar sin errores")
else:
    print("❌ Operador aún no disponible")
    print("🔄 Intenta:")
    print("  1. Reiniciar Blender completamente")
    print("  2. Deshabilitar y volver a habilitar el addon")
    print("  3. Verificar si hay errores en la consola")

print("=" * 60)
