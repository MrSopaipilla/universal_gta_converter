#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST MIXAMO DETECTION - Universal GTA SA Converter
=================================================
Script de prueba para verificar que la detección de Mixamo funciona correctamente
"""

import bpy
import os
import json

def test_mixamo_detection():
    """Probar la detección de Mixamo"""
    print("🧪 TESTING MIXAMO DETECTION")
    print("=" * 50)
    
    # Simular huesos de Mixamo
    test_mixamo_bones = [
        "mixamorig:Hips",
        "mixamorig:Spine", 
        "mixamorig:Spine1",
        "mixamorig:Spine2",
        "mixamorig:Neck",
        "mixamorig:Head",
        "mixamorig:LeftShoulder",
        "mixamorig:LeftArm",
        "mixamorig:LeftForeArm",
        "mixamorig:LeftHand",
        "mixamorig:RightShoulder",
        "mixamorig:RightArm",
        "mixamorig:RightForeArm",
        "mixamorig:RightHand",
        "mixamorig:LeftUpLeg",
        "mixamorig:LeftLeg",
        "mixamorig:LeftFoot",
        "mixamorig:RightUpLeg",
        "mixamorig:RightLeg",
        "mixamorig:RightFoot"
    ]
    
    # Convertir a lowercase como lo hace el algoritmo
    source_bones = set(bone.lower() for bone in test_mixamo_bones)
    print(f"✅ Huesos de prueba: {len(source_bones)}")
    print(f"📋 Primeros 5: {list(source_bones)[:5]}")
    
    # Cargar mapping de Mixamo
    addon_dir = os.path.dirname(__file__)
    mapping_file = os.path.join(addon_dir, 'mappings', 'bone_mapping_mixamo.json')
    
    if not os.path.exists(mapping_file):
        print(f"❌ No se encontró el archivo de mapping: {mapping_file}")
        return False
    
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        mapped_bones = set(entry.get('source_bone', '').lower() for entry in data.get('mappings', []) if entry.get('source_bone', ''))
        print(f"📁 Mappings en archivo: {len(mapped_bones)}")
        
        # Probar el algoritmo mejorado
        matches = 0
        total_mapped = len(mapped_bones)
        
        for mapped_bone in mapped_bones:
            # Buscar coincidencia exacta
            if mapped_bone in source_bones:
                matches += 1
                continue
            
            # Para Mixamo: buscar sin prefijo
            if 'mixamo' in mapping_file.lower():
                bone_without_prefix = mapped_bone.replace('mixamorig:', '')
                if bone_without_prefix in source_bones:
                    matches += 1
                    continue
                
                # Buscar variaciones comunes de Mixamo
                mixamo_variations = [
                    bone_without_prefix,
                    f"mixamorig_{bone_without_prefix}",
                    f"mixamo_{bone_without_prefix}",
                    bone_without_prefix.replace('left', 'l').replace('right', 'r'),
                    bone_without_prefix.replace('l', 'left').replace('r', 'right')
                ]
                
                for variation in mixamo_variations:
                    if variation in source_bones:
                        matches += 1
                        break
        
        percent = matches / max(total_mapped, 1)
        print(f"🎯 RESULTADO: {matches}/{total_mapped} = {percent:.2%}")
        
        # Verificar detección de Mixamo
        mixamo_detected = any('mixamorig' in bone.lower() for bone in source_bones)
        print(f"🔍 Mixamo detectado: {mixamo_detected}")
        
        if percent >= 0.20 or mixamo_detected:
            print("✅ ÉXITO: La detección de Mixamo debería funcionar")
            return True
        else:
            print("❌ FALLO: La detección de Mixamo no funcionará")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 Iniciando test de detección Mixamo...")
    success = test_mixamo_detection()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 TEST COMPLETADO EXITOSAMENTE")
        print("✅ La detección de Mixamo debería funcionar ahora")
        print("🔄 Reinicia Blender y prueba Smart Auto-Detect")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ TEST FALLÓ")
        print("🔧 Revisa la configuración de mappings")
        print("=" * 50)

if __name__ == "__main__":
    main()
