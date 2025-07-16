import bpy
import os
import shutil

class CleanupUtils:
    """Utilidades para limpieza de modelos y escenas"""
    
    @staticmethod
    def clean_empty_vertex_groups(obj):
        """Limpia vertex groups vacíos de un objeto mesh"""
        if obj.type != 'MESH':
            return 0
        
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
        
        removed_count = 0
        for vg in groups_to_remove:
            print(f"[DEBUG] Eliminando vertex group vacío: {vg.name}")
            obj.vertex_groups.remove(vg)
            removed_count += 1
        
        return removed_count

    @staticmethod
    def clean_unused_materials():
        """Limpia materiales no utilizados"""
        removed_count = 0
        for material in list(bpy.data.materials):
            if material.users == 0:
                bpy.data.materials.remove(material)
                removed_count += 1
        return removed_count

    @staticmethod
    def clean_armatures_keep_root_only(target_armature=None):
        """
        Elimina todos los armatures excepto el que tenga 'Root' en su nombre.
        Si no encuentra ninguno con 'Root', mantiene solo el target_armature.
        """
        print("[DEBUG] Limpiando armatures - manteniendo solo el Root...")
        
        # Obtener todos los armatures en la escena
        all_armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
        
        if len(all_armatures) <= 1:
            print("[DEBUG] Solo hay 1 o ningún armature, no es necesario limpiar.")
            return 0
        
        # Buscar armature con 'Root' en el nombre (case insensitive)
        root_armature = None
        for armature in all_armatures:
            if 'root' in armature.name.lower():
                root_armature = armature
                break
        
        # Si no encuentra 'Root', usar el target_armature
        if not root_armature:
            root_armature = target_armature
            if not root_armature:
                print("[WARNING] No se encontró armature con 'Root' ni target_armature definido.")
                return 0
        
        print(f"[DEBUG] Armature a mantener: {root_armature.name}")
        
        # Eliminar todos los otros armatures
        armatures_to_remove = [arm for arm in all_armatures if arm != root_armature]
        removed_count = 0
        
        for armature in armatures_to_remove:
            print(f"[DEBUG] Eliminando armature: {armature.name}")
            
            # Primero verificar si hay objetos mesh que dependan de este armature
            dependent_meshes = []
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    for modifier in obj.modifiers:
                        if modifier.type == 'ARMATURE' and modifier.object == armature:
                            dependent_meshes.append(obj)
            
            # Reasignar los mesh dependientes al root_armature
            for mesh in dependent_meshes:
                for modifier in mesh.modifiers:
                    if modifier.type == 'ARMATURE' and modifier.object == armature:
                        modifier.object = root_armature
                        print(f"[DEBUG] Reasignado modificador de {mesh.name} al armature Root")
            
            # Reasignar parent si algún objeto tiene como parent el armature a eliminar
            for obj in bpy.data.objects:
                if obj.parent == armature:
                    obj.parent = root_armature
                    print(f"[DEBUG] Reasignado parent de {obj.name} al armature Root")
            
            # Eliminar el armature
            try:
                bpy.data.objects.remove(armature, do_unlink=True)
                print(f"[DEBUG] Armature {armature.name} eliminado exitosamente")
                removed_count += 1
            except Exception as e:
                print(f"[ERROR] No se pudo eliminar armature {armature.name}: {e}")
        
        # Asegurar que el root_armature esté visible y seleccionable
        if root_armature:
            root_armature.hide_set(False)
            root_armature.hide_viewport = False
            if hasattr(root_armature, 'hide_select'):
                root_armature.hide_select = False
            
            # Opcional: renombrar el armature final como "Root" si no lo tiene ya
            if 'root' not in root_armature.name.lower():
                root_armature.name = "Root"
                print(f"[DEBUG] Armature renombrado a: {root_armature.name}")
        
        print(f"[DEBUG] Limpieza de armatures completada. Eliminados: {removed_count}")
        return removed_count

    @staticmethod
    def purge_unused_data():
        """Elimina todos los datos no utilizados del archivo blend"""
        # Purgar datos no utilizados
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        print("[DEBUG] Datos no utilizados eliminados.")

    @staticmethod
    def purge_unused_objects():
        """Elimina objetos no utilizados"""
        objects_removed = 0
        for obj in list(bpy.data.objects):
            if obj.users == 0:
                bpy.data.objects.remove(obj)
                objects_removed += 1
        return objects_removed

    @staticmethod
    def export_textures_to_directory(directory):
        """Exporta todas las texturas utilizadas en el modelo a un directorio"""
        if not directory:
            print("[ERROR] No se especificó directorio de destino.")
            return 0
        
        if not os.path.exists(directory):
            os.makedirs(directory)
        
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
                                dest_path = os.path.join(directory, filename)
                                try:
                                    shutil.copy2(source_path, dest_path)
                                    exported_count += 1
                                    print(f"[DEBUG] Textura exportada: {filename}")
                                except Exception as e:
                                    print(f"[ERROR] Error copiando {source_path}: {e}")
        
        return exported_count

    @staticmethod
    def clean_model_full(obj=None):
        """Limpieza completa del modelo"""
        cleaned_items = 0
        
        # Limpiar vertex groups vacíos
        objects_to_clean = [obj] if obj else bpy.data.objects
        
        for obj in objects_to_clean:
            if obj.type == 'MESH':
                cleaned_items += CleanupUtils.clean_empty_vertex_groups(obj)
        
        # Limpiar materiales no utilizados
        cleaned_items += CleanupUtils.clean_unused_materials()
        
        print(f"[DEBUG] Modelo limpiado. {cleaned_items} elementos eliminados.")
        return cleaned_items

    @staticmethod
    def reassign_armature_modifiers(old_armature, new_armature):
        """Reasigna modificadores de armature de un armature a otro"""
        reassigned_count = 0
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE' and modifier.object == old_armature:
                        modifier.object = new_armature
                        reassigned_count += 1
                        print(f"[DEBUG] Modificador reasignado: {obj.name} -> {new_armature.name}")
        
        return reassigned_count

    @staticmethod
    def make_objects_visible(objects_list):
        """Hace visibles una lista de objetos"""
        for obj in objects_list:
            obj.hide_set(False)
            obj.hide_viewport = False
            if hasattr(obj, 'hide_select'):
                obj.hide_select = False
            print(f"[DEBUG] Hecho visible: {obj.name}")

    @staticmethod
    def clean_vertex_groups_by_bone_list(obj, valid_bone_names):
        """Limpia vertex groups que no corresponden a huesos válidos"""
        if obj.type != 'MESH':
            return 0
        
        groups_to_remove = []
        for vg in obj.vertex_groups:
            if vg.name not in valid_bone_names:
                groups_to_remove.append(vg)
        
        removed_count = 0
        for vg in groups_to_remove:
            vg_name = vg.name
            obj.vertex_groups.remove(vg)
            print(f"[DEBUG] Eliminado vertex group no válido: {vg_name}")
            removed_count += 1
        
        return removed_count

    @staticmethod
    def apply_bone_spacing(armature, target_armature=None):
        """
        Aplica espaciado de huesos y realiza limpieza completa de armatures.
        Esta función consolida la funcionalidad de apply_bone_spacing del código original.
        """
        if not armature or armature.type != 'ARMATURE':
            print("[DEBUG] No hay armature válido para aplicar espaciado.")
            return False
        
        try:
            print("[DEBUG] === INICIANDO APPLY_BONE_SPACING ===")
            
            # Obtener todos los armatures en la escena
            all_armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
            print(f"[DEBUG] Armatures en escena: {[arm.name for arm in all_armatures]}")
            
            # DIAGNÓSTICO: Verificar meshes y sus modificadores
            print("[DEBUG] Meshes y sus modificadores de armature:")
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    print(f"  Mesh: {obj.name}")
                    for modifier in obj.modifiers:
                        if modifier.type == 'ARMATURE':
                            armature_name = modifier.object.name if modifier.object else "None"
                            print(f"    - Modifier: {modifier.name} -> {armature_name}")
            
            # PASO 1: Limpiar vertex groups vacíos de todos los objetos mesh
            print("[DEBUG] === LIMPIANDO VERTEX GROUPS VACÍOS ===")
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    CleanupUtils.clean_empty_vertex_groups(obj)
            
            # PASO 2: Reasignar modificadores
            print("[DEBUG] === REASIGNANDO MODIFICADORES ===")
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    bpy.context.view_layer.objects.active = obj
                    
                    for modifier in obj.modifiers:
                        if modifier.type == 'ARMATURE':
                            if modifier.object and modifier.object.name.startswith('Armature.'):
                                old_name = modifier.object.name
                                if target_armature:
                                    modifier.object = target_armature
                                    print(f"[DEBUG] Modificador reasignado: {old_name} -> {target_armature.name}")
                                else:
                                    obj.modifiers.remove(modifier)
                                    print(f"[DEBUG] Modificador eliminado: {old_name}")
            
            # PASO 3: Identificar armatures a eliminar
            print("[DEBUG] === IDENTIFICANDO ARMATURES A ELIMINAR ===")
            armatures_to_remove = []
            
            for obj in all_armatures:
                should_remove = False
                reason = ""
                
                # No eliminar el target_armature
                if obj == target_armature:
                    continue
                
                # Verificar si es Armature.001 o similar
                if obj.name.startswith('Armature.'):
                    should_remove = True
                    reason = "Armature.XXX no deseado"
                
                # Verificar si está vacío
                elif len(obj.data.bones) == 0:
                    should_remove = True
                    reason = "Armature vacío"
                
                if should_remove:
                    armatures_to_remove.append(obj)
                    print(f"[DEBUG] Marcado para eliminar: {obj.name} ({reason})")
            
            # PASO 4: Eliminar armatures
            print("[DEBUG] === ELIMINANDO ARMATURES ===")
            for arm_obj in armatures_to_remove:
                try:
                    print(f"[DEBUG] Eliminando: {arm_obj.name}")
                    
                    # Verificar si tiene usuarios antes de eliminar
                    if arm_obj.users > 0:
                        print(f"[DEBUG] Advertencia: {arm_obj.name} tiene {arm_obj.users} usuarios")
                    
                    bpy.data.objects.remove(arm_obj, do_unlink=True)
                    print(f"[DEBUG] ✓ Eliminado: {arm_obj.name}")
                    
                except Exception as e:
                    print(f"[DEBUG] ✗ Error eliminando {arm_obj.name}: {e}")
            
            # PASO 5: Aplicar espaciado al armature target si es necesario
            if target_armature and target_armature.type == 'ARMATURE':
                print("[DEBUG] === APLICANDO ESPACIADO ===")
                bpy.context.view_layer.objects.active = target_armature
                bpy.ops.object.mode_set(mode='EDIT')
                
                edit_bones = target_armature.data.edit_bones
                
                # Aplicar espaciado básico
                for bone in edit_bones:
                    if bone.parent and bone.length < 0.01:
                        bone.length = 0.01
                        print(f"[DEBUG] Ajustada longitud del hueso: {bone.name}")
                
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # PASO 6: Verificar resultado
            print("[DEBUG] === VERIFICANDO RESULTADO ===")
            remaining_armatures = []
            for obj in bpy.data.objects:
                if obj.type == 'ARMATURE':
                    remaining_armatures.append(obj.name)
            
            print(f"[DEBUG] Armatures restantes: {remaining_armatures}")
            
            # PASO 7: Limpiar datos huérfanos
            print("[DEBUG] === LIMPIANDO DATOS HUÉRFANOS ===")
            orphaned_count = 0
            for armature_data in list(bpy.data.armatures):
                if armature_data.users == 0:
                    print(f"[DEBUG] Eliminando datos huérfanos: {armature_data.name}")
                    bpy.data.armatures.remove(armature_data)
                    orphaned_count += 1
            
            print(f"[DEBUG] Datos huérfanos eliminados: {orphaned_count}")
            print("[DEBUG] === APPLY_BONE_SPACING COMPLETADO ===")
            return True
            
        except Exception as e:
            print(f"[DEBUG] ERROR GENERAL en apply_bone_spacing: {e}")
            import traceback
            traceback.print_exc()
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass
            return False