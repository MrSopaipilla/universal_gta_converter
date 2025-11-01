#!/usr/bin/env python3
"""
Test del sistema JSON corregido
Ejecutar en Blender para verificar correcciones
"""

import bpy
import json
import tempfile
import os

def test_json_save_load():
    """Probar save/load con preservación de espacios"""
    print("🧪 TESTING JSON SAVE/LOAD SYSTEM")
    print("=" * 50)
    
    try:
        settings = bpy.context.scene.universal_gta_settings
        
        # Crear mapeos de prueba con espacios incorrectos
        settings.bone_mappings.clear()
        
        test_mappings = [
            ("mixamorig:Hips", "Pelvis"),  # Sin espacio - debería corregirse
            ("mixamorig:Spine", " Spine"),  # Correcto
            ("mixamorig:LeftArm", "L UpperArm"),  # Sin espacio inicial
            ("mixamorig:RightArm", " R UpperArm"),  # Correcto
        ]
        
        print("📝 Creando mapeos de prueba:")
        for source, target in test_mappings:
            mapping = settings.bone_mappings.add()
            mapping.source_bone = source
            mapping.target_bone = target
            mapping.enabled = True
            print(f"  {source} -> '{target}'")
        
        # Guardar a archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        # Simular save_mapping
        try:
            bpy.ops.universalgta.save_mapping(filepath=temp_file)
            print(f"\n💾 Guardado en: {temp_file}")
            
            # Leer el JSON y verificar espacios
            with open(temp_file, 'r') as f:
                saved_data = json.load(f)
            
            print("\n🔍 VERIFICANDO ESPACIOS EN JSON:")
            if "mappings" in saved_data:
                for mapping in saved_data["mappings"]:
                    target = mapping.get("target_bone", "")
                    print(f"  Target: '{target}' - {'✅ Correcto' if target.startswith(' ') and 'UpperArm' in target else '⚠️ Revisar'}")
            
            # Limpiar mapeos y cargar
            settings.bone_mappings.clear()
            bpy.ops.universalgta.load_mapping(filepath=temp_file)
            
            print(f"\n📂 Cargados {len(settings.bone_mappings)} mapeos")
            print("\n🔍 VERIFICANDO ESPACIOS DESPUÉS DE CARGAR:")
            for mapping in settings.bone_mappings:
                target = mapping.target_bone
                valid = target in [" Pelvis", " Spine", " L UpperArm", " R UpperArm"]
                print(f"  '{mapping.source_bone}' -> '{target}' - {'✅' if valid else '❌'}")
            
            # Cleanup
            os.unlink(temp_file)
            print("\n✅ Test completado")
            
        except Exception as e:
            print(f"❌ Error en operadores: {e}")
            print("💡 Verifica que el addon esté habilitado")
    
    except Exception as e:
        print(f"❌ Error general: {e}")

def test_bone_validation():
    """Probar validación de huesos"""
    print("\n🦴 TESTING BONE VALIDATION")
    print("=" * 50)
    
    try:
        from gta_sa_bones import GTASABones
        
        test_bones = [
            "Pelvis",        # Sin espacio - debería normalizarse
            " Pelvis",       # Correcto
            " L UpperArm",   # Correcto  
            "L UpperArm",    # Sin espacio - debería normalizarse
            "UpperArm.L",    # Formato .L - debería normalizarse
            "invalid_bone",  # Inválido
        ]
        
        print("Probando normalización:")
        for bone in test_bones:
            normalized = GTASABones.normalize_bone(bone)
            valid = GTASABones.is_valid_bone(normalized) if normalized else False
            status = "✅" if valid else "❌"
            print(f"  {status} '{bone}' -> '{normalized}'")
        
        print(f"\n📊 Total huesos oficiales: {len(GTASABones.OFFICIAL_BONES)}")
        
    except ImportError:
        print("❌ gta_sa_bones.py no disponible")
        print("💡 Ejecuta fix_json_mapping_system.py primero")

if __name__ == "__main__":
    test_json_save_load()
    test_bone_validation()
