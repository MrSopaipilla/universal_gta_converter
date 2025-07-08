# utils/cleanup.py - Versión mejorada
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
            has_vertices = any(
                group.group == vg.index and group.weight > 0
                for vertex in obj.data.vertices
                for group in vertex.groups
            )
            
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
        
        # Buscar armature con 'Root' en el nombre
        root_armature = CleanupUtils._find_root_armature(all_armatures)
        
        # Si no encuentra 'Root', usar el target_armature
        if not root_armature:
            root_armature = target_armature
            if not root_armature:
                print("[WARNING] No se encontró armature con 'Root' ni target_armature definido.")
                return 0
        
        print(f"[DEBUG] Armature a mantener: {root_armature.name}")
        
        # Reasignar dependencias
        CleanupUtils._reassign_dependencies_to_root(all_armatures, root_armature)
        
        # Eliminar todos los otros armatures
        armatures_to_remove = [arm for arm in all_armatures if arm != root_armature]
        removed_count = CleanupUtils._remove_armatures_safely(armatures_to_remove)
        
        # Asegurar visibilidad del root
        CleanupUtils._ensure_armature_visibility(root_armature)
        
        print(f"[DEBUG] Limpieza de armatures completada. Eliminados: {removed_count}")
        return removed_count

    @staticmethod
    def _find_root_armature(armatures):
        """Busca el armature con 'Root' en el nombre"""
        for armature in armatures:
            if 'root' in armature.name.lower():
                return armature
        return None

    @staticmethod
    def _reassign_dependencies_to_root(all_armatures, root_armature):
        """Reasigna todas las dependencias al root armature"""
        for armature in all_armatures:
            if armature == root_armature:
                continue
                
            # Reasignar meshes dependientes
            dependent_meshes = CleanupUtils._find_dependent_meshes(armature)
            for mesh in dependent_meshes:
                CleanupUtils._reassign_mesh_modifiers(mesh, armature, root_armature)
            
            # Reasignar objetos con parent
            CleanupUtils._reassign_children(armature, root_armature)

    @staticmethod
    def _find_dependent_meshes(armature):
        """Encuentra meshes que dependen del armature"""
        dependent_meshes = []
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE' and modifier.object == armature:
                        dependent_meshes.append(obj)
                        break
        return dependent_meshes

    @staticmethod
    def _reassign_mesh_modifiers(mesh, old_armature, new_armature):
        """Reasigna modificadores de un mesh a un nuevo armature"""
        for modifier in mesh.modifiers:
            if modifier.type == 'ARMATURE' and modifier.object == old_armature:
                modifier.object = new_armature
                print(f"[DEBUG] Reasignado modificador de {mesh.name} al armature Root")

    @staticmethod
    def _reassign_children(old_parent, new_parent):
        """Reasigna objetos hijos a un nuevo parent"""
        for obj in bpy.data.objects:
            if obj.parent == old_parent:
                obj.parent = new_parent
                print(f"[DEBUG] Reasignado parent de {obj.name} al armature Root")

    @staticmethod
    def _remove_armatures_safely(armatures_to_remove):
        """Elimina armatures de forma segura"""
        removed_count = 0
        for armature in armatures_to_remove:
            try:
                print(f"[DEBUG] Eliminando armature: {armature.name}")
                bpy.data.objects.remove(armature, do_unlink=True)
                print(f"[DEBUG] Armature {armature.name} eliminado exitosamente")
                removed_count += 1
            except Exception as e:
                print(f"[ERROR] No se pudo eliminar armature {armature.name}: {e}")
        return removed_count

    @staticmethod
    def _ensure_armature_visibility(armature):
        """Asegura que el armature esté visible"""
        if not armature:
            return
            
        armature.hide_set(False)
        armature.hide_viewport = False
        if hasattr(armature, 'hide_select'):
            armature.hide_select = False
        
        # Renombrar si es necesario
        if 'root' not in armature.name.lower():
            armature.name = "Root"
            print(f"[DEBUG] Armature renombrado a: {armature.name}")

    @staticmethod
    def purge_unused_data():
        """Elimina todos los datos no utilizados del archivo blend"""
        # Purgar datos no utilizados
        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, 
            do_linked_ids=True, 
            do_recursive=True
        )
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
        errors = []
        
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        result = CleanupUtils._export_single_texture(
                            node.image, directory
                        )
                        if result['success']:
                            exported_count += 1
                        else:
                            errors.append(result['error'])
        
        if errors:
            print("[DEBUG] Errores durante la exportación:")
            for error in errors:
                print(f"  - {error}")
        
        return exported_count

    @staticmethod
    def _export_single_texture(image, directory):
        """Exporta una sola textura"""
        if not image.filepath:
            return {'success': False, 'error': f"Imagen {image.name} sin ruta de archivo"}
        
        source_path = bpy.path.abspath(image.filepath)
        if not os.path.exists(source_path):
            return {'success': False, 'error': f"Archivo no encontrado: {source_path}"}
        
        filename = os.path.basename(source_path)
        dest_path = os.path.join(directory, filename)
        
        try:
            shutil.copy2(source_path, dest_path)
            print(f"[DEBUG] Textura exportada: {filename}")
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': f"Error copiando {filename}: {e}"}

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
            
            # Diagnóstico: Verificar meshes y sus modificadores
            CleanupUtils._diagnose_mesh_modifiers()
            
            # Limpiar vertex groups vacíos de todos los objetos mesh
            CleanupUtils._clean_all_empty_vertex_groups()
            
            # Reasignar modificadores
            CleanupUtils._reassign_modifiers_to_target(target_armature)
            
            # Identificar y eliminar armatures no deseados
            CleanupUtils._cleanup_unwanted_armatures(all_armatures, target_armature)
            
            # Aplicar espaciado al armature target si es necesario
            if target_armature and target_armature.type == 'ARMATURE':
                CleanupUtils._apply_spacing_to_bones(target_armature)
            
            # Verificar resultado y limpiar datos huérfanos
            CleanupUtils._verify_and_cleanup_orphans()
            
            print("[DEBUG] === APPLY_BONE_SPACING COMPLETADO ===")
            return True
            
        except Exception as e:
            print(f"[DEBUG] ERROR GENERAL en apply_bone_spacing: {e}")
            import traceback
            traceback.print_exc()
            CleanupUtils._safe_mode_set('OBJECT')
            return False

    @staticmethod
    def _diagnose_mesh_modifiers():
        """Diagnóstico de meshes y sus modificadores"""
        print("[DEBUG] Meshes y sus modificadores de armature:")
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                print(f"  Mesh: {obj.name}")
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE':
                        armature_name = modifier.object.name if modifier.object else "None"
                        print(f"    - Modifier: {modifier.name} -> {armature_name}")

    @staticmethod
    def _clean_all_empty_vertex_groups():
        """Limpia vertex groups vacíos de todos los meshes"""
        print("[DEBUG] === LIMPIANDO VERTEX GROUPS VACÍOS ===")
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                CleanupUtils.clean_empty_vertex_groups(obj)

    @staticmethod
    def _reassign_modifiers_to_target(target_armature):
        """Reasigna modificadores al armature target"""
        if not target_armature:
            return
            
        print("[DEBUG] === REASIGNANDO MODIFICADORES ===")
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE':
                        if modifier.object and modifier.object.name.startswith('Armature.'):
                            old_name = modifier.object.name
                            modifier.object = target_armature
                            print(f"[DEBUG] Modificador reasignado: {old_name} -> {target_armature.name}")

    @staticmethod
    def _cleanup_unwanted_armatures(all_armatures, target_armature):
        """Identifica y elimina armatures no deseados"""
        print("[DEBUG] === IDENTIFICANDO ARMATURES A ELIMINAR ===")
        
        armatures_to_remove = []
        
        for obj in all_armatures:
            if obj == target_armature:
                continue
            
            should_remove = False
            reason = ""
            
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
        
        # Eliminar armatures
        CleanupUtils._remove_armatures_list(armatures_to_remove)

    @staticmethod
    def _remove_armatures_list(armatures_to_remove):
        """Elimina una lista de armatures"""
        print("[DEBUG] === ELIMINANDO ARMATURES ===")
        for arm_obj in armatures_to_remove:
            try:
                print(f"[DEBUG] Eliminando: {arm_obj.name}")
                
                if arm_obj.users > 0:
                    print(f"[DEBUG] Advertencia: {arm_obj.name} tiene {arm_obj.users} usuarios")
                
                bpy.data.objects.remove(arm_obj, do_unlink=True)
                print(f"[DEBUG] ✓ Eliminado: {arm_obj.name}")
                
            except Exception as e:
                print(f"[DEBUG] ✗ Error eliminando {arm_obj.name}: {e}")

    @staticmethod
    def _apply_spacing_to_bones(target_armature):
        """Aplica espaciado a los huesos del armature"""
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

    @staticmethod
    def _verify_and_cleanup_orphans():
        """Verifica el resultado y limpia datos huérfanos"""
        print("[DEBUG] === VERIFICANDO RESULTADO ===")
        
        remaining_armatures = [
            obj.name for obj in bpy.data.objects 
            if obj.type == 'ARMATURE'
        ]
        print(f"[DEBUG] Armatures restantes: {remaining_armatures}")
        
        # Limpiar datos huérfanos
        print("[DEBUG] === LIMPIANDO DATOS HUÉRFANOS ===")
        orphaned_count = 0
        
        for armature_data in list(bpy.data.armatures):
            if armature_data.users == 0:
                print(f"[DEBUG] Eliminando datos huérfanos: {armature_data.name}")
                bpy.data.armatures.remove(armature_data)
                orphaned_count += 1
        
        print(f"[DEBUG] Datos huérfanos eliminados: {orphaned_count}")

    @staticmethod
    def _safe_mode_set(mode):
        """Cambia de modo de forma segura"""
        try:
            bpy.ops.object.mode_set(mode=mode)
        except Exception:
            pass