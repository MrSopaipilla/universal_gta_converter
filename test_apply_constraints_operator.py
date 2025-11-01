# SCRIPT DE PRUEBA - Verificar operador apply_constraints
# Ve a Scripting > New > Pega este código > Run Script

import bpy

print("🔍 TESTING APPLY_CONSTRAINTS OPERATOR")
print("=" * 60)

# Verificar si el operador existe
operator_id = "universalgta.apply_constraints"

print(f"🎯 Verificando operador: {operator_id}")

if not hasattr(bpy.ops, 'universalgta'):
    print("❌ Namespace 'universalgta' no disponible")
else:
    print("✅ Namespace 'universalgta' disponible")
    
    if hasattr(bpy.ops.universalgta, 'apply_constraints'):
        print(f"✅ Operador '{operator_id}' ENCONTRADO")
        
        # Verificar que hay un armature target
        target_armature = None
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and ('Root' in obj.name or 'root' in obj.name.lower()):
                target_armature = obj
                break
        
        if target_armature:
            print(f"✅ Target armature encontrado: {target_armature.name}")
            print("🎯 ¿Quieres probar el operador? (Ejecuta manualmente)")
            print("   bpy.ops.universalgta.apply_constraints()")
        else:
            print("⚠️ No se encontró target armature")
            print("💡 Importa un modelo GTA SA o crea un armature llamado 'Root'")
            
    else:
        print(f"❌ Operador '{operator_id}' NO ENCONTRADO")
        print("🔍 Operadores similares disponibles:")
        ops = [op for op in dir(bpy.ops.universalgta) if not op.startswith('_')]
        for op in ops:
            if 'constraint' in op.lower() or 'apply' in op.lower():
                print(f"  - {op}")

print("\n" + "=" * 60)
if hasattr(bpy.ops, 'universalgta') and hasattr(bpy.ops.universalgta, 'apply_constraints'):
    print("🎉 ¡OPERADOR DISPONIBLE! El fix funcionó correctamente")
else:
    print("❌ Operador aún no disponible")
    print("🔄 Intenta:")
    print("  1. Reiniciar Blender completamente")
    print("  2. Deshabilitar y volver a habilitar el addon")

print("=" * 60)
