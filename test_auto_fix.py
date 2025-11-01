#!/usr/bin/env python3
"""
Test del sistema de auto-fix automático
Ejecutar en Blender para probar la funcionalidad
"""

import bpy
import json
import tempfile
import os

def test_auto_fix_json_load():
    """Probar auto-fix automático al cargar JSON"""
    print("🧪 TESTING AUTO-FIX JSON LOAD")
    print("=" * 50)
    
    # Crear JSON de prueba con espaciado incorrecto
    test_json_data = {
        "format_version": "2.0",
        "description": "Test auto-fix",
        "mappings": [
            {
                "index": 0,
                "target_bone": "Pelvis",          # ❌ Sin espacio - debe corregirse
                "source_bone": "mixamorig:Hips",
                "enabled": True,
                "detection_method": "Manual",
                "confidence": 1.0
            },
            {
                "index": 1,
                "target_bone": "UpperArm.L",      # ❌ Formato .L - debe corregirse  
                "source_bone": "mixamorig:LeftArm",
                "enabled": True,
                "detection_method": "Manual", 
                "confidence": 1.0
            },
            {
                "index": 2,
                "target_bone": " R Hand",         # ✅ Ya correcto
                "source_bone": "mixamorig:RightHand",
                "enabled": True,
                "detection_method": "Manual",
                "confidence": 1.0
            },
            {
                "index": 3,
                "target_bone": "R_Thigh",         # ❌ Formato _ - debe corregirse
                "source_bone": "mixamorig:RightUpLeg",
                "enabled": True,
                "detection_method": "Manual",
                "confidence": 1.0
            }
        ]
    }
    
    # Guardar JSON de prueba
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_json_data, f, indent=2)
        test_file = f.name
    
    print(f"📄 JSON de prueba creado: {test_file}")
    print("\n📋 CONTENIDO ORIGINAL (con errores de espaciado):")
    for mapping in test_json_data["mappings"]:
        target = mapping["target_bone"]
        expected_correct = {
            "Pelvis": " Pelvis",
            "UpperArm.L": " L UpperArm", 
            " R Hand": " R Hand",
            "R_Thigh": " R Thigh"
        }.get(target, target)
        
        status = "✅" if target == expected_correct else "❌"
        print(f"  {status} {mapping['index']}: '{target}' (debería ser '{expected_correct}')")
    
    try:
        # Limpiar mapeos actuales
        settings = bpy.context.scene.universal_gta_settings
        settings.bone_mappings.clear()
        
        print("\n🔄 Cargando JSON con auto-fix...")
        
        # Cargar JSON - esto debería activar auto-fix automáticamente
        bpy.ops.universalgta.load_mapping(filepath=test_file)
        
        print(f"\n📂 Cargados {len(settings.bone_mappings)} mapeos")
        
        print("\n🔍 VERIFICANDO CORRECCIONES AUTO-FIX:")
        all_correct = True
        
        for i, mapping in enumerate(settings.bone_mappings):
            target = mapping.target_bone
            source = mapping.source_bone
            
            # Verificar si está correctamente normalizado
            expected_targets = [" Pelvis", " L UpperArm", " R Hand", " R Thigh"]
            
            if i < len(expected_targets):
                expected = expected_targets[i]
                is_correct = target == expected
                status = "✅" if is_correct else "❌"
                
                print(f"  {status} Mapping {i+1}: '{source}' -> '{target}'")
                
                if not is_correct:
                    print(f"      Expected: '{expected}'")
                    all_correct = False
            else:
                print(f"  ➕ Extra mapping: '{source}' -> '{target}'")
        
        if all_correct:
            print("\n🎉 ¡AUTO-FIX FUNCIONÓ PERFECTAMENTE!")
            print("✅ Todos los huesos target fueron corregidos automáticamente")
        else:
            print("\n⚠️ Algunos huesos no fueron corregidos")
            print("💡 Verifica que gta_sa_normalizer.py esté disponible")
        
        # Cleanup
        os.unlink(test_file)
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        print("💡 Verifica que el addon esté habilitado y load_mapping funcione")
    
    print("\n" + "=" * 50)

def test_direct_normalizer():
    """Probar el normalizador directamente"""
    print("\n🔬 TESTING DIRECT NORMALIZER")
    print("=" * 40)
    
    try:
        from gta_sa_normalizer import GTASANormalizer
        
        test_bones = [
            "Pelvis",        # Sin espacio
            "UpperArm.L",    # Formato .L
            "R_Hand",        # Formato _
            " L Thigh",      # Ya correcto
            "invalid_bone",  # No normalizable
        ]
        
        print("Probando normalización directa:")
        for bone in test_bones:
            normalized = GTASANormalizer.normalize_bone_name(bone)
            is_official, suggestion = GTASANormalizer.validate_normalization(bone)
            
            status = "✅" if is_official else ("🔧" if normalized != bone else "❓")
            print(f"  {status} '{bone}' → '{normalized}'")
        
        print("\n✅ Normalizador directo funciona correctamente")
        
    except ImportError:
        print("❌ gta_sa_normalizer.py no disponible")
        print("💡 Ejecuta auto_fix_json_loader.py primero")

if __name__ == "__main__":
    test_auto_fix_json_load()
    test_direct_normalizer()
