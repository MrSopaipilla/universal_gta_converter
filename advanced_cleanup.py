#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADVANCED CLEANUP MODULE - Universal GTA SA Converter
==================================================
Módulo de limpieza avanzada para el proceso de conversión

FUNCIONES:
✅ Eliminación de shapekeys con apply_mix nativo
✅ Limpieza de mallas problemáticas
✅ Configuración de modificadores únicos
✅ Establecimiento de jerarquías correctas
"""

import bpy

class AdvancedCleanup:
    """Limpieza avanzada para conversión GTA SA"""
    
    @staticmethod
    def remove_all_shapekeys_native():
        """Eliminar todas las shapekeys usando función nativa de Blender"""
        print("[CLEANUP] Eliminando shapekeys con función nativa...")
        processed = 0
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.data.shape_keys:
                try:
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
                    processed += 1
                    print(f"[CLEANUP] ✅ Shapekeys eliminados: {obj.name}")
                except Exception as e:
                    print(f"[CLEANUP] ⚠️ Error en {obj.name}: {e}")
        
        print(f"[CLEANUP] Total procesados: {processed}")
        return processed
    
    @staticmethod
    def remove_problematic_meshes():
        """Eliminar mallas problemáticas como 'unnamed'"""
        print("[CLEANUP] Eliminando mallas problemáticas...")
        
        problematic_names = [
            'unnamed', 'Unnamed', 'UNNAMED',
            'temp', 'Temp', 'TEMP',
            'default', 'Default', 'DEFAULT'
        ]
        
        removed = 0
        for obj in bpy.data.objects[:]:
            if obj.type == 'MESH' and obj.name in problematic_names:
                # Reparentar hijos
                for child in bpy.data.objects:
                    if child.parent == obj:
                        child.parent = None
                
                obj_name = obj.name
                bpy.data.objects.remove(obj, do_unlink=True)
                print(f"[CLEANUP] ✅ Eliminado: {obj_name}")
                removed += 1
        
        print(f"[CLEANUP] Mallas problemáticas eliminadas: {removed}")
        return removed
    
    @staticmethod
    def setup_gta_modifier(target_armature, mesh_name="Mesh"):
        """Configurar modificador GTA_SA_SKIN único"""
        mesh_obj = bpy.data.objects.get(mesh_name)
        if not mesh_obj or not target_armature:
            print("[CLEANUP] ❌ Mesh o armature no encontrado")
            return False
        
        print(f"[CLEANUP] Configurando modificador en: {mesh_name}")
        
        # Eliminar modificadores armature existentes
        for modifier in mesh_obj.modifiers[:]:
            if modifier.type == 'ARMATURE':
                mesh_obj.modifiers.remove(modifier)
        
        # Crear modificador único
        modifier = mesh_obj.modifiers.new(name="GTA_SA_SKIN", type='ARMATURE')
        modifier.object = target_armature
        modifier.use_vertex_groups = True
        
        print(f"[CLEANUP] ✅ Modificador GTA_SA_SKIN -> {target_armature.name}")
        return True
    
    @staticmethod
    def setup_parent_hierarchy(target_armature, mesh_name="Mesh"):
        """Establecer jerarquía Mesh(padre) -> Armature(hijo)"""
        mesh_obj = bpy.data.objects.get(mesh_name)
        if not mesh_obj or not target_armature:
            print("[CLEANUP] ❌ No se puede establecer jerarquía")
            return False
        
        print("[CLEANUP] Estableciendo jerarquía...")
        
        # Limpiar parent del armature
        target_armature.parent = None
        
        # Establecer Mesh como padre
        target_armature.parent = mesh_obj
        target_armature.parent_type = 'OBJECT'
        
        print(f"[CLEANUP] ✅ {mesh_obj.name}(padre) -> {target_armature.name}(hijo)")
        return True
    
    @staticmethod
    def full_cleanup_process(target_armature):
        """Proceso completo de limpieza"""
        print("[CLEANUP] === INICIANDO LIMPIEZA COMPLETA ===")
        
        results = {
            'shapekeys': AdvancedCleanup.remove_all_shapekeys_native(),
            'problematic_meshes': AdvancedCleanup.remove_problematic_meshes(),
            'modifier_setup': AdvancedCleanup.setup_gta_modifier(target_armature),
            'hierarchy_setup': AdvancedCleanup.setup_parent_hierarchy(target_armature)
        }
        
        print("[CLEANUP] === LIMPIEZA COMPLETADA ===")
        for step, success in results.items():
            status = "✅" if success else "❌"
            print(f"[CLEANUP] {status} {step}")
        
        return all(results.values())


# Función de conveniencia para usar desde otros módulos
def run_advanced_cleanup(target_armature):
    """Ejecutar limpieza avanzada completa"""
    return AdvancedCleanup.full_cleanup_process(target_armature)
