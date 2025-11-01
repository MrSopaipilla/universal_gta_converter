# SCRIPT DE REPORTE - Nombres Reales de Huesos
# Ve a Scripting > New > Pega este código > Run Script

import bpy

print("📋 BONE NAMES REPORT")
print("=" * 60)

# Buscar todos los armatures
armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']

if not armatures:
    print("❌ No se encontraron armatures")
else:
    for armature in armatures:
        print(f"\n🦴 ARMATURE: {armature.name}")
        print("-" * 40)
        
        bone_names = [b.name for b in armature.data.bones]
        
        for i, bone_name in enumerate(bone_names, 1):
            # Mostrar el nombre exacto con comillas para ver espacios
            print(f"{i:2d}. \"{bone_name}\"")
        
        print(f"\nTotal huesos: {len(bone_names)}")
        
        # Análisis de espacios
        with_spaces = [name for name in bone_names if name.startswith(' ')]
        without_spaces = [name for name in bone_names if not name.startswith(' ')]
        
        print(f"Con espacios iniciales: {len(with_spaces)}")
        print(f"Sin espacios iniciales: {len(without_spaces)}")
        
        if with_spaces:
            print("\nHuesos CON espacios:")
            for bone in with_spaces[:5]:  # Primeros 5
                print(f"  '{bone}'")
            if len(with_spaces) > 5:
                print(f"  ... y {len(with_spaces) - 5} más")

print("\n" + "=" * 60)
print("💡 Guarda este reporte para corregir rig_profiles.py")
print("=" * 60)
