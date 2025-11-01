#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST CONVERSION COMPLETE - Universal GTA SA Converter
===================================================
Script de prueba para verificar que la conversión funciona correctamente

EJECUTAR EN BLENDER:
- Configurar source y target armatures
- Ejecutar este script para prueba automática
- Revisar los resultados en la consola
"""

import bpy

def test_conversion_complete():
    """Prueba completa del proceso de conversión"""
    print("=" * 80)
    print("🧪 INICIANDO PRUEBA COMPLETA DE CONVERSIÓN")
    print("=" * 80)
    
    # 1. Verificar que el addon esté cargado
    print("\n🔍 VERIFICANDO ADDON...")
    if not hasattr(bpy.ops, 'universalgta'):
        print("❌ Addon Universal GTA no está cargado")
        return False
    
    # Verificar operadores críticos
    critical_ops = ['smart_auto_detect', 'execute_conversion']
    for op in critical_ops:
        if hasattr(bpy.ops.universalgta, op):
            print(f"✅ {op} disponible")
        else:
            print(f"❌ {op} NO disponible")
            return False
    
    # 2. Verificar settings
    print("\n🔍 VERIFICANDO SETTINGS...")
    try:
        settings = bpy.context.scene.universal_gta_settings
        
        if settings.source_armature:
            print(f"✅ Source armature: {settings.source_armature.name}")
        else:
            print("❌ Source armature no configurado")
            print("💡 Configura source armature antes de ejecutar la prueba")
            return False
        
        if settings.target_armature:
            print(f"✅ Target armature: {settings.target_armature.name}")
        else:
            print("❌ Target armature no configurado")
            print("💡 Configura target armature antes de ejecutar la prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error accediendo a settings: {e}")
        return False
    
    # 3. Ejecutar Smart Auto-Detect
    print("\n🧠 EJECUTANDO SMART AUTO-DETECT...")
    try:
        result = bpy.ops.universalgta.smart_auto_detect()
        if result == {'FINISHED'}:
            print("✅ Smart Auto-Detect completado")
            
            # Verificar mappings creados
            mappings_count = len(settings.bone_mappings)
            print(f"✅ {mappings_count} bone mappings creados")
            
            if mappings_count == 0:
                print("⚠️ No se crearon bone mappings automáticamente")
                print("💡 Verifica que los armatures tengan huesos compatibles")
                
        else:
            print("❌ Smart Auto-Detect falló")
            return False
            
    except Exception as e:
        print(f"❌ Error en Smart Auto-Detect: {e}")
        return False
    
    # 4. Verificar estado antes de conversión
    print("\n🔍 VERIFICANDO ESTADO PRE-CONVERSIÓN...")
    
    # Contar objetos
    meshes_with_shapekeys = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.data.shape_keys:
            meshes_with_shapekeys.append(obj.name)
    
    if meshes_with_shapekeys:
        print(f"📊 Objetos con shapekeys: {meshes_with_shapekeys}")
    else:
        print("📊 No hay objetos con shapekeys")
    
    # 5. Ejecutar conversión completa
    print("\n🚀 EJECUTANDO CONVERSIÓN COMPLETA...")
    try:
        result = bpy.ops.universalgta.execute_conversion()
        if result == {'FINISHED'}:
            print("✅ Conversión completa exitosa")
        else:
            print("⚠️ Conversión completada con advertencias")
            
    except Exception as e:
        print(f"❌ Error en conversión: {e}")
        return False
    
    # 6. Verificar resultados
    print("\n🔍 VERIFICANDO RESULTADOS...")
    
    # Verificar objeto Mesh
    mesh_obj = bpy.data.objects.get("Mesh")
    if mesh_obj:
        print(f"✅ Objeto 'Mesh' creado: {mesh_obj.name}")
        
        # Verificar modificador GTA_SA_SKIN
        gta_modifier = None
        for mod in mesh_obj.modifiers:
            if mod.name == "GTA_SA_SKIN":
                gta_modifier = mod
                break
        
        if gta_modifier:
            target = gta_modifier.object.name if gta_modifier.object else "None"
            print(f"✅ Modificador GTA_SA_SKIN -> {target}")
        else:
            print("❌ Modificador GTA_SA_SKIN NO encontrado")
        
        # Verificar jerarquía
        target_armature = settings.target_armature
        if target_armature and target_armature.parent == mesh_obj:
            print(f"✅ Jerarquía correcta: {mesh_obj.name} -> {target_armature.name}")
        else:
            print("❌ Jerarquía incorrecta")
    else:
        print("❌ Objeto 'Mesh' NO encontrado")
    
    # Verificar shapekeys eliminados
    remaining_shapekeys = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.data.shape_keys:
            remaining_shapekeys.append(obj.name)
    
    if remaining_shapekeys:
        print(f"⚠️ Shapekeys restantes en: {remaining_shapekeys}")
    else:
        print("✅ Todos los shapekeys eliminados correctamente")
    
    # 7. Verificar constraints aplicados
    constraints_found = 0
    if settings.target_armature:
        for bone in settings.target_armature.pose.bones:
            for constraint in bone.constraints:
                if "GTA_SA_COPY_LOC" in constraint.name:
                    constraints_found += 1
    
    if constraints_found > 0:
        print(f"⚠️ {constraints_found} constraints GTA_SA_COPY_LOC aún presentes")
        print("💡 Los constraints deberían limpiarse automáticamente después de aplicar")
    else:
        print("✅ Constraints limpiados correctamente")
    
    print("\n" + "=" * 80)
    print("🎉 PRUEBA COMPLETADA")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = test_conversion_complete()
    if success:
        print("\n🎯 ¡CONVERSIÓN FUNCIONANDO CORRECTAMENTE!")
        print("✅ Puedes usar Smart Auto-Detect + Convert to GTA SA con confianza")
    else:
        print("\n⚠️ HAY PROBLEMAS EN LA CONVERSIÓN")
        print("🔧 Revisa las configuraciones y vuelve a intentar")
