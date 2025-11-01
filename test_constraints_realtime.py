# SCRIPT DE PRUEBA - Verificar Constraints en Tiempo Real
# Ve a Scripting > New > Pega este código > Run Script

import bpy

print("🔍 TESTING CONSTRAINTS REAL-TIME")
print("=" * 60)

# Buscar armature target
target_armature = None
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE' and ('Root' in obj.name or 'root' in obj.name.lower()):
        target_armature = obj
        break

if not target_armature:
    print("❌ No se encontró armature target")
else:
    print(f"✅ Armature target encontrado: {target_armature.name}")
    
    # Listar huesos disponibles
    bone_names = [b.name for b in target_armature.pose.bones]
    print(f"📊 Total huesos: {len(bone_names)}")
    
    # Mostrar huesos con espacios para verificar nombres correctos
    print("\n🦴 HUESOS CON ESPACIOS (primeros 10):")
    space_bones = [name for name in bone_names if name.startswith(' ')]
    for i, bone in enumerate(space_bones[:10], 1):
        print(f"  {i:2d}. '{bone}'")
    
    # Verificar constraints existentes
    print("\n🔗 CONSTRAINTS EXISTENTES:")
    constraint_count = 0
    for bone in target_armature.pose.bones:
        for constraint in bone.constraints:
            if constraint.name.startswith("GTA_SA_COPY_LOC"):
                print(f"  ✅ {bone.name} -> {constraint.subtarget}")
                constraint_count += 1
    
    print(f"\n📊 Total constraints GTA SA: {constraint_count}")
    
    if constraint_count == 0:
        print("⚠️ No hay constraints GTA SA")
        print("💡 Ejecuta la conversión o usa 'Apply Constraints' manual")
    else:
        print("✅ Constraints encontrados!")
        
        # Probar un constraint específico
        test_bone = None
        for bone_name in [' L UpperArm', ' R UpperArm', ' Spine1']:
            if bone_name in target_armature.pose.bones:
                test_bone = target_armature.pose.bones[bone_name]
                break
        
        if test_bone:
            print(f"\n🧪 PROBANDO CONSTRAINT: {test_bone.name}")
            constraints = [c for c in test_bone.constraints if c.name.startswith("GTA_SA_COPY_LOC")]
            
            if constraints:
                constraint = constraints[0]
                print(f"  Target: {constraint.target.name if constraint.target else 'None'}")
                print(f"  Subtarget: '{constraint.subtarget}'")
                print(f"  Influence: {constraint.influence}")
                print(f"  Use XYZ: {constraint.use_x}, {constraint.use_y}, {constraint.use_z}")
                
                # Verificar si el subtarget existe
                if constraint.subtarget in bone_names:
                    print(f"  ✅ Subtarget '{constraint.subtarget}' existe")
                else:
                    print(f"  ❌ Subtarget '{constraint.subtarget}' NO existe")
                    print(f"  💡 Posibles coincidencias:")
                    for bone in bone_names:
                        if constraint.subtarget.lower() in bone.lower():
                            print(f"    - '{bone}'")

print("\n" + "=" * 60)
print("💡 Si los constraints no funcionan:")
print("  1. Verifica que los nombres de huesos tengan espacios correctos")
print("  2. Ejecuta el master_comprehensive_fix.py")
print("  3. Recarga el addon completamente")
print("=" * 60)
