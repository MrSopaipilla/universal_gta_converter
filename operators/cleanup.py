# operators/cleanup.py - Versión mejorada
"""
Operadores de limpieza para Universal GTA SA Converter
"""

import bpy
import os
import shutil
from bpy.types import Operator
from bpy.props import StringProperty
from ..utils.cleanup import CleanupUtils


class UNIVERSALGTA_OT_clean_model(Operator):
    """Limpia el modelo removiendo vertex groups y materiales no utilizados"""
    bl_idname = "universalgta.clean_model"
    bl_label = "Clean Model"
    bl_description = "Clean the model by removing unused vertex groups and materials"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        cleaned_items = CleanupUtils.clean_model_full()
        
        self.report({'INFO'}, f"Modelo limpiado. {cleaned_items} elementos eliminados.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_export_textures(Operator):
    """Exporta todas las texturas utilizadas en el modelo"""
    bl_idname = "universalgta.export_textures"
    bl_label = "Export Textures"
    bl_description = "Export all textures used in the model"
    bl_options = {'REGISTER'}
    
    directory: StringProperty(subtype="DIR_PATH")
    
    def execute(self, context):
        if not self.directory:
            self.report({'ERROR'}, "No se seleccionó directorio de destino.")
            return {'CANCELLED'}
        
        exported_count = CleanupUtils.export_textures_to_directory(self.directory)
        
        self.report({'INFO'}, f"Exportadas {exported_count} texturas a {self.directory}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class UNIVERSALGTA_OT_purge_unused_data(Operator):
    """Elimina todos los bloques de datos no utilizados del archivo blend"""
    bl_idname = "universalgta.purge_unused_data"
    bl_label = "Purge Unused Data"
    bl_description = "Remove all unused data blocks from the blend file"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        CleanupUtils.purge_unused_data()
        self.report({'INFO'}, "Datos no utilizados eliminados.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_purge_scene(Operator):
    """Limpia toda la escena y elimina objetos no utilizados"""
    bl_idname = "universalgta.purge_scene"
    bl_label = "Purge Scene"
    bl_description = "Clean the entire scene and remove unused objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        objects_removed = CleanupUtils.purge_unused_objects()
        
        # Purgar datos huérfanos adicionales
        CleanupUtils.purge_unused_data()
        
        self.report({'INFO'}, f"Escena limpiada. {objects_removed} objetos eliminados.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_clean_armatures(Operator):
    """Elimina armatures innecesarios y mantiene solo el principal"""
    bl_idname = "universalgta.clean_armatures"
    bl_label = "Clean Armatures"
    bl_description = "Remove unnecessary armatures and keep only the main one"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        removed_count = CleanupUtils.clean_armatures_keep_root_only(
            settings.target_armature
        )
        
        self.report({'INFO'}, f"Armatures limpiados. {removed_count} eliminados.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_clean_empty_vertex_groups(Operator):
    """Limpia vertex groups vacíos de todos los objetos mesh"""
    bl_idname = "universalgta.clean_empty_vertex_groups"
    bl_label = "Clean Empty Vertex Groups"
    bl_description = "Remove empty vertex groups from all mesh objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        cleaned_count = 0
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                cleaned_count += CleanupUtils.clean_empty_vertex_groups(obj)
        
        self.report({'INFO'}, f"Eliminados {cleaned_count} vertex groups vacíos.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_fix_modifiers(Operator):
    """Corrige modificadores de armature rotos o mal asignados"""
    bl_idname = "universalgta.fix_modifiers"
    bl_label = "Fix Modifiers"
    bl_description = "Fix broken or misassigned armature modifiers"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        target_armature = settings.target_armature
        
        if not target_armature or target_armature.type != 'ARMATURE':
            self.report({'WARNING'}, "No hay target armature asignado.")
            return {'CANCELLED'}
        
        fixed_count = self._fix_armature_modifiers(target_armature)
        
        self.report({'INFO'}, f"Corregidos {fixed_count} modificadores.")
        return {'FINISHED'}
    
    def _fix_armature_modifiers(self, target_armature):
        """Corrige modificadores de armature"""
        fixed_count = 0
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE':
                        needs_fix = False
                        
                        # Si el modificador no tiene objeto asignado
                        if not modifier.object:
                            needs_fix = True
                        # Si el objeto no es un armature
                        elif modifier.object.type != 'ARMATURE':
                            needs_fix = True
                        # Si apunta a un armature temporal
                        elif modifier.object.name.startswith('Armature.') and modifier.object != target_armature:
                            needs_fix = True
                        
                        if needs_fix:
                            modifier.object = target_armature
                            fixed_count += 1
                            print(f"[DEBUG] Modificador corregido en {obj.name}")
        
        return fixed_count


class UNIVERSALGTA_OT_remove_duplicates(Operator):
    """Elimina objetos duplicados en la escena"""
    bl_idname = "universalgta.remove_duplicates"
    bl_label = "Remove Duplicates"
    bl_description = "Remove duplicate objects in the scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        removed_count = self._remove_duplicate_objects()
        
        self.report({'INFO'}, f"Eliminados {removed_count} objetos duplicados.")
        return {'FINISHED'}
    
    def _remove_duplicate_objects(self):
        """Identifica y elimina objetos duplicados"""
        removed_count = 0
        object_base_names = {}
        objects_to_remove = []
        
        # Agrupar objetos por nombre base
        for obj in bpy.data.objects:
            base_name = self._get_base_name(obj.name)
            
            if base_name not in object_base_names:
                object_base_names[base_name] = []
            object_base_names[base_name].append(obj)
        
        # Identificar duplicados (mantener el primero)
        for base_name, obj_list in object_base_names.items():
            if len(obj_list) > 1:
                # Ordenar por número de sufijo
                obj_list.sort(key=lambda x: self._get_suffix_number(x.name))
                # Marcar todos menos el primero para eliminar
                objects_to_remove.extend(obj_list[1:])
        
        # Eliminar objetos duplicados
        for obj in objects_to_remove:
            try:
                obj_name = obj.name
                bpy.data.objects.remove(obj, do_unlink=True)
                removed_count += 1
                print(f"[DEBUG] Objeto duplicado eliminado: {obj_name}")
            except Exception as e:
                print(f"[DEBUG] Error eliminando {obj.name}: {e}")
        
        return removed_count
    
    def _get_base_name(self, name):
        """Obtiene el nombre base sin sufijos numéricos"""
        import re
        # Eliminar sufijos como .001, .002, etc.
        return re.sub(r'\.\d+$', '', name)
    
    def _get_suffix_number(self, name):
        """Obtiene el número del sufijo o 0 si no tiene"""
        import re
        match = re.search(r'\.(\d+)$', name)
        return int(match.group(1)) if match else 0


class UNIVERSALGTA_OT_optimize_mesh(Operator):
    """Optimiza la geometría del mesh eliminando vértices duplicados"""
    bl_idname = "universalgta.optimize_mesh"
    bl_label = "Optimize Mesh"
    bl_description = "Optimize mesh geometry by removing duplicate vertices"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        optimized_count = 0
        total_vertices_removed = 0
        
        # Guardar el objeto activo actual
        original_active = context.active_object
        original_mode = context.mode
        
        try:
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    vertices_removed = self._optimize_single_mesh(context, obj)
                    if vertices_removed > 0:
                        optimized_count += 1
                        total_vertices_removed += vertices_removed
            
            # Restaurar el objeto activo original
            if original_active:
                context.view_layer.objects.active = original_active
                if original_active.mode != original_mode:
                    bpy.ops.object.mode_set(mode=original_mode)
            
            self.report({'INFO'}, 
                       f"Optimizados {optimized_count} meshes. "
                       f"{total_vertices_removed} vértices duplicados eliminados.")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error durante la optimización: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def _optimize_single_mesh(self, context, obj):
        """Optimiza un mesh individual"""
        # Seleccionar y activar el objeto
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        # Contar vértices antes
        vertices_before = len(obj.data.vertices)
        
        # Entrar en modo edición
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Seleccionar todo
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Eliminar duplicados
        bpy.ops.mesh.remove_doubles()
        
        # Volver a modo objeto
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Contar vértices después
        vertices_after = len(obj.data.vertices)
        vertices_removed = vertices_before - vertices_after
        
        if vertices_removed > 0:
            print(f"[DEBUG] Mesh optimizado: {obj.name} - "
                  f"{vertices_removed} vértices eliminados")
        
        return vertices_removed


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_clean_model,
    UNIVERSALGTA_OT_export_textures,
    UNIVERSALGTA_OT_purge_unused_data,
    UNIVERSALGTA_OT_purge_scene,
    UNIVERSALGTA_OT_clean_armatures,
    UNIVERSALGTA_OT_clean_empty_vertex_groups,
    UNIVERSALGTA_OT_fix_modifiers,
    UNIVERSALGTA_OT_remove_duplicates,
    UNIVERSALGTA_OT_optimize_mesh,
]


def register():
    """Registra todas las clases"""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Desregistra todas las clases"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)