#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG CONVERSION STATE - Universal GTA SA Converter
=================================================
Script de diagnóstico para identificar problemas en el estado de la escena

EJECUTAR EN BLENDER:
- Ve a Scripting
- Abre este archivo
- Ejecuta con Run Script
- Revisa la consola para el diagnóstico completo
"""

import bpy

def diagnose_conversion_state():
    """Diagnóstico completo del estado de conversión"""
    print("=" * 80)
    print("🔍 DIAGNÓSTICO DE ESTADO DE CONVERSIÓN GTA SA")
    print("=" * 80)
    
    # 1. OBJETOS EN LA ESCENA
    print("\n📦 OBJETOS EN LA ESCENA:")
    objects_by_type = {}
    corrupted_objects = []
    
    for obj in bpy.data.objects:
        try:
            obj_type = obj.type
            obj_name = obj.name
            
            if obj_type not in objects_by_type:
                objects_by_type[obj_type] = []
            objects_by_type[obj_type].append(obj_name)
            
        except Exception as e:
            corrupted_objects.append(f"CORRUPTED_OBJECT: {e}")
    
    for obj_type, obj_names in objects_by_type.items():
        print(f"  {obj_type}: {len(obj_names)} objetos")
        for name in obj_names:
            print(f"    - {name}")
    
    if corrupted_objects:
        print("  ❌ OBJETOS CORRUPTOS:")
        for corrupt in corrupted_objects:
            print(f"    - {corrupt}")
    
    # 2. CONTEXTO ACTIVO
    print("\n🎯 CONTEXTO ACTIVO:")
    try:
        active = bpy.context.view_layer.objects.active
        if active:
            print(f"  Objeto activo: {active.name} ({active.type})")
        else:
            print("  Objeto activo: None ✅")
    except Exception as e:
        print(f"  ❌ Error accediendo objeto activo: {e}")
    
    # 3. SELECCIONES
    print("\n🔍 OBJETOS SELECCIONADOS:")
    try:
        selected = bpy.context.selected_objects
        if selected:
            print(f"  {len(selected)} objetos seleccionados:")
            for obj in selected:
                print(f"    - {obj.name}")
        else:
            print("  Ningún objeto seleccionado ✅")
    except Exception as e:
        print(f"  ❌ Error accediendo selecciones: {e}")
    
    # 4. JERARQUÍAS PADRE-HIJO
    print("\n🌳 JERARQUÍAS PADRE-HIJO:")
    for obj in bpy.data.objects:
        try:
            if obj.parent:
                print(f"  {obj.name} ({obj.type}) -> Parent: {obj.parent.name}")
        except Exception as e:
            print(f"  ❌ Error en jerarquía de {obj.name}: {e}")
    
    # 5. MODIFICADORES ARMATURE
    print("\n🔧 MODIFICADORES ARMATURE:")
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            try:
                armature_modifiers = [m for m in obj.modifiers if m.type == 'ARMATURE']
                if armature_modifiers:
                    print(f"  {obj.name}:")
                    for mod in armature_modifiers:
                        target = mod.object.name if mod.object else "None"
                        print(f"    - {mod.name} -> {target}")
            except Exception as e:
                print(f"  ❌ Error verificando modificadores de {obj.name}: {e}")
    
    # 6. SHAPEKEYS
    print("\n🎭 SHAPEKEYS:")
    shapekey_objects = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            try:
                if obj.data.shape_keys:
                    shapekey_objects.append(obj.name)
            except Exception as e:
                print(f"  ❌ Error verificando shapekeys de {obj.name}: {e}")
    
    if shapekey_objects:
        print(f"  ⚠️ Objetos con shapekeys restantes: {shapekey_objects}")
    else:
        print("  ✅ No hay shapekeys en la escena")
    
    # 7. OBJETOS PROBLEMÁTICOS
    print("\n⚠️ OBJETOS PROBLEMÁTICOS:")
    problematic_names = ['unnamed', 'Unnamed', 'UNNAMED', 'temp', 'Temp']
    problematic_found = []
    
    for obj in bpy.data.objects:
        try:
            if any(pattern in obj.name for pattern in problematic_names):
                problematic_found.append(f"{obj.name} ({obj.type})")
        except:
            problematic_found.append("OBJETO_CORRUPTO")
    
    if problematic_found:
        print(f"  ❌ Objetos problemáticos encontrados:")
        for prob in problematic_found:
            print(f"    - {prob}")
    else:
        print("  ✅ No se encontraron objetos problemáticos")
    
    # 8. VERIFICACIÓN FINAL
    print("\n✅ VERIFICACIÓN FINAL:")
    mesh_obj = bpy.data.objects.get("Mesh")
    if mesh_obj:
        print(f"  ✅ Objeto 'Mesh' encontrado: {mesh_obj.name}")
        
        # Verificar modificador GTA_SA_SKIN
        gta_modifier = None
        for mod in mesh_obj.modifiers:
            if mod.name == "GTA_SA_SKIN":
                gta_modifier = mod
                break
        
        if gta_modifier:
            target = gta_modifier.object.name if gta_modifier.object else "None"
            print(f"  ✅ Modificador GTA_SA_SKIN encontrado -> {target}")
        else:
            print("  ❌ Modificador GTA_SA_SKIN NO encontrado")
        
        # Verificar jerarquía
        if mesh_obj.children:
            children_names = [child.name for child in mesh_obj.children]
            print(f"  ✅ Mesh tiene hijos: {children_names}")
        else:
            print("  ⚠️ Mesh no tiene hijos")
    else:
        print("  ❌ Objeto 'Mesh' NO encontrado")
    
    print("\n" + "=" * 80)
    print("🎯 DIAGNÓSTICO COMPLETADO")
    print("=" * 80)


if __name__ == "__main__":
    diagnose_conversion_state()
