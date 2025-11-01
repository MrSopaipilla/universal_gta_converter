"""
Operadores de limpieza para Universal GTA SA Converter
"""

import bpy
import os
import shutil
from bpy.types import Operator
from bpy.props import StringProperty


class UNIVERSALGTA_OT_clean_model(Operator):
    """Limpia el modelo removiendo vertex groups y materiales no utilizados"""
    bl_idname = "universalgta.clean_model"
    bl_label = "Clean Model"
    bl_description = "Clean the model by removing unused vertex groups and materials"
    
    def execute(self, context):
        cleaned_items = 0
        
        # Limpiar vertex groups vacíos
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                groups_to_remove = []
                for vg in obj.vertex_groups:
                    has_vertices = False
                    for vertex in obj.data.vertices:
                        for group in vertex.groups:
                            if group.group == vg.index and group.weight > 0:
                                has_vertices = True
                                break
                        if has_vertices:
                            break
                    
                    if not has_vertices:
                        groups_to_remove.append(vg)
                
                for vg in groups_to_remove:
                    obj.vertex_groups.remove(vg)
                    cleaned_items += 1
        
        # Limpiar materiales no utilizados
        for material in list(bpy.data.materials):
            if material.users == 0:
                bpy.data.materials.remove(material)
                cleaned_items += 1
        
        self.report({'INFO'}, f"Modelo limpiado. {cleaned_items} elementos eliminados.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_export_textures(Operator):
    """Exporta todas las texturas utilizadas en el modelo"""
    bl_idname = "universalgta.export_textures"
    bl_label = "Export Textures"
    bl_description = "Export all textures used in the model"
    
    directory: StringProperty(subtype="DIR_PATH")
    
    def execute(self, context):
        if not self.directory:
            self.report({'ERROR'}, "No se seleccionó directorio de destino.")
            return {'CANCELLED'}
        
        exported_count = 0
        
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        image = node.image
                        if image.filepath:
                            source_path = bpy.path.abspath(image.filepath)
                            if os.path.exists(source_path):
                                filename = os.path.basename(source_path)
                                dest_path = os.path.join(self.directory, filename)
                                try:
                                    shutil.copy2(source_path, dest_path)
                                    exported_count += 1
                                except Exception as e:
                                    print(f"Error copiando {source_path}: {e}")
        
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
    
    def execute(self, context):
        # Purgar datos no utilizados
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        
        self.report({'INFO'}, "Datos no utilizados eliminados.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_purge_scene(Operator):
    """Limpia toda la escena y elimina objetos no utilizados"""
    bl_idname = "universalgta.purge_scene"
    bl_label = "Purge Scene"
    bl_description = "Clean the entire scene and remove unused objects"
    
    def execute(self, context):
        # Eliminar objetos no utilizados
        objects_removed = 0
        
        for obj in list(bpy.data.objects):
            if obj.users == 0:
                bpy.data.objects.remove(obj)
                objects_removed += 1
        
        # Purgar datos huérfanos
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        
        self.report({'INFO'}, f"Escena limpiada. {objects_removed} objetos eliminados.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_clean_armatures(Operator):
    """Elimina armatures innecesarios y mantiene solo el principal"""
    bl_idname = "universalgta.clean_armatures"
    bl_label = "Clean Armatures"
    bl_description = "Remove unnecessary armatures and keep only the main one"
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Usar la función del converter si está disponible
        if hasattr(context.scene, 'converter_instance'):
            converter = context.scene.converter_instance
            converter.clean_armatures_keep_root_only()
        else:
            # Implementación simple alternativa
            armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
            target_armature = settings.target_armature
            
            if target_armature and len(armatures) > 1:
                for armature in armatures:
                    if armature != target_armature:
                        # Reasignar modificadores antes de eliminar
                        for obj in bpy.data.objects:
                            if obj.type == 'MESH':
                                for modifier in obj.modifiers:
                                    if modifier.type == 'ARMATURE' and modifier.object == armature:
                                        modifier.object = target_armature
                        
                        # Eliminar armature
                        bpy.data.objects.remove(armature, do_unlink=True)
        
        self.report({'INFO'}, "Armatures limpiados.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_clean_empty_vertex_groups(Operator):
    """Limpia vertex groups vacíos de todos los objetos mesh"""
    bl_idname = "universalgta.clean_empty_vertex_groups"
    bl_label = "Clean Empty Vertex Groups"
    bl_description = "Remove empty vertex groups from all mesh objects"
    
    def execute(self, context):
        cleaned_count = 0
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                groups_to_remove = []
                for vg in obj.vertex_groups:
                    # Verificar si el vertex group tiene vértices asignados
                    has_vertices = False
                    for vertex in obj.data.vertices:
                        for group in vertex.groups:
                            if group.group == vg.index and group.weight > 0:
                                has_vertices = True
                                break
                        if has_vertices:
                            break
                    
                    if not has_vertices:
                        groups_to_remove.append(vg)
                
                for vg in groups_to_remove:
                    obj.vertex_groups.remove(vg)
                    cleaned_count += 1
        
        self.report({'INFO'}, f"Eliminados {cleaned_count} vertex groups vacíos.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_fix_modifiers(Operator):
    """Corrige modificadores de armature rotos o mal asignados"""
    bl_idname = "universalgta.fix_modifiers"
    bl_label = "Fix Modifiers"
    bl_description = "Fix broken or misassigned armature modifiers"
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        target_armature = settings.target_armature
        
        if not target_armature or target_armature.type != 'ARMATURE':
            self.report({'WARNING'}, "No hay target armature asignado.")
            return {'CANCELLED'}
        
        fixed_count = 0
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE':
                        # Si el modificador no tiene objeto asignado o es inválido
                        if not modifier.object or modifier.object.type != 'ARMATURE':
                            modifier.object = target_armature
                            fixed_count += 1
                        
                        # Si el modificador apunta a un armature con nombre tipo "Armature.001"
                        elif modifier.object.name.startswith('Armature.') and modifier.object != target_armature:
                            modifier.object = target_armature
                            fixed_count += 1
        
        self.report({'INFO'}, f"Corregidos {fixed_count} modificadores.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_remove_duplicates(Operator):
    """Elimina objetos duplicados en la escena"""
    bl_idname = "universalgta.remove_duplicates"
    bl_label = "Remove Duplicates"
    bl_description = "Remove duplicate objects in the scene"
    
    def execute(self, context):
        removed_count = 0
        object_names = set()
        objects_to_remove = []
        
        for obj in bpy.data.objects:
            # Buscar objetos con nombres como "Object.001", "Object.002", etc.
            if '.' in obj.name and obj.name.split('.')[0] in object_names:
                objects_to_remove.append(obj)
            else:
                base_name = obj.name.split('.')[0]
                object_names.add(base_name)
        
        # Eliminar objetos duplicados
        for obj in objects_to_remove:
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
                removed_count += 1
            except Exception:
                pass
        
        self.report({'INFO'}, f"Eliminados {removed_count} objetos duplicados.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_optimize_mesh(Operator):
    """Optimiza la geometría del mesh eliminando vértices duplicados"""
    bl_idname = "universalgta.optimize_mesh"
    bl_label = "Optimize Mesh"
    bl_description = "Optimize mesh geometry by removing duplicate vertices"
    
    def execute(self, context):
        optimized_count = 0
        
        # Guardar el objeto activo actual
        original_active = context.active_object
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                # Seleccionar y activar el objeto
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
                
                # Entrar en modo edición
                bpy.ops.object.mode_set(mode='EDIT')
                
                # Seleccionar todo y eliminar duplicados
                bpy.ops.mesh.select_all(action='SELECT')
                result = bpy.ops.mesh.remove_doubles()
                
                # Volver a modo objeto
                bpy.ops.object.mode_set(mode='OBJECT')
                
                if 'FINISHED' in str(result):
                    optimized_count += 1
                    print(f"[DEBUG] Mesh optimizado: {obj.name}")
        
        # Restaurar el objeto activo original
        if original_active:
            context.view_layer.objects.active = original_active
        
        self.report({'INFO'}, f"Optimizados {optimized_count} meshes.")
        return {'FINISHED'}


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
