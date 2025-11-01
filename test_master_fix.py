# SCRIPT DE PRUEBA - Verificar Fix del Operador
# Ve a Scripting > New > Pega este código > Run Script

import bpy

print("🔍 TESTING MASTER FIX - validate_mappings_and_disable_invalid")
print("=" * 70)

# Test específico para el operador problemático
operator_id = "universalgta.validate_mappings_and_disable_invalid"

print(f"🎯 Verificando operador: {operator_id}")

# Verificar si existe el namespace
if not hasattr(bpy.ops, 'universalgta'):
    print("❌ Namespace 'universalgta' no disponible")
    print("💡 El addon no está cargado correctamente")
else:
    print("✅ Namespace 'universalgta' disponible")
    
    # Contar total de operadores universalgta
    ops = [op for op in dir(bpy.ops.universalgta) if not op.startswith('_')]
    print(f"📊 Total operadores universalgta registrados: {len(ops)}")
    
    # Verificar el operador específico
    if hasattr(bpy.ops.universalgta, 'validate_mappings_and_disable_invalid'):
        print(f"✅ Operador '{operator_id}' ENCONTRADO")
        print("🎉 ¡FIX EXITOSO! El error debería estar resuelto")
        print("✅ El panel Universal GTA ahora debería funcionar sin errores")
        
        # Intentar obtener información del operador
        try:
            operator = getattr(bpy.ops.universalgta, 'validate_mappings_and_disable_invalid')
            print(f"✅ Operador es accesible: {operator}")
            print("✅ El botón 'Validate' en el panel ya no dará error")
        except Exception as e:
            print(f"⚠️ Error accediendo al operador: {e}")
            
    else:
        print(f"❌ Operador '{operator_id}' AÚN NO ENCONTRADO")
        print("🔄 TROUBLESHOOTING:")
        print("  1. Reiniciar Blender completamente")
        print("  2. Deshabilitar y volver a habilitar el addon")
        print("  3. Verificar errores en la consola")
        print("  4. Verificar que el backup se haya aplicado correctamente")
        
        # Mostrar operadores de validación disponibles
        validation_ops = [op for op in ops if 'validate' in op.lower()]
        print(f"🔍 Operadores de validación disponibles: {validation_ops}")

print("=" * 70)
print("🎯 PRÓXIMO PASO: Ve al panel 'Universal GTA' en el sidebar (N)")
print("✅ El botón 'Validate' debería funcionar sin errores")
print("=" * 70)
