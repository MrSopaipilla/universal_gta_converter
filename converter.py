# converter.py - Versión mejorada
import bpy
from mathutils import Vector
from .utils.cleanup import CleanupUtils


class UniversalGTAConverter:
    """Conversor principal para armatures universales a GTA SA"""
    
    def __init__(self, settings):
        self.settings = settings
        self.cleanup_utils = CleanupUtils()

    def clean_empty_vertex_groups(self, obj):
        """Limpia vertex groups vacíos de un objeto mesh"""
        if obj.type != 'MESH':
            return
        
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
        
        for vg in groups_to_remove:
            print(f"[DEBUG] Eliminando vertex group vacío: {vg.name}")
            obj.vertex_groups.remove(vg)

    def apply_bone_spacing(self, target_armature):
        """Aplica espaciado y limpieza de armatures"""
        print("[DEBUG] === INICIANDO APPLY_BONE_SPACING ===")
        
        if not target_armature:
            print("[DEBUG] No hay target_armature definido")
            return
        
        try:
            # Cambiar a modo objeto antes de hacer cualquier cosa
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Obtener todos los armatures
            all_armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
            print(f"[DEBUG] Armatures encontrados: {[arm.name for arm in all_armatures]}")
            
            # Diagnóstico: Verificar meshes y sus modificadores
            self._diagnose_mesh_modifiers()
            
            # Limpiar vertex groups vacíos
            self._clean_all_vertex_groups()
            
            # Reasignar modificadores
            self._reassign_modifiers(target_armature)
            
            # Identificar y eliminar armatures no deseados
            self._cleanup_unwanted_armatures(target_armature, all_armatures)
            
            # Aplicar espaciado al armature target
            self._apply_spacing_to_armature(target_armature)
            
            # Verificar resultado y limpiar datos huérfanos
            self._verify_and_cleanup_orphans()
            
            print("[DEBUG] === APPLY_BONE_SPACING COMPLETADO ===")
            
        except Exception as e:
            print(f"[DEBUG] ERROR GENERAL en apply_bone_spacing: {e}")
            import traceback
            traceback.print_exc()
            self._safe_mode_set('OBJECT')

    def _diagnose_mesh_modifiers(self):
        """Diagnóstico de meshes y sus modificadores"""
        print("[DEBUG] Meshes y sus modificadores de armature:")
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                print(f"  Mesh: {obj.name}")
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE':
                        armature_name = modifier.object.name if modifier.object else "None"
                        print(f"    - Modifier: {modifier.name} -> {armature_name}")

    def _clean_all_vertex_groups(self):
        """Limpia vertex groups vacíos de todos los meshes"""
        print("[DEBUG] === LIMPIANDO VERTEX GROUPS VACÍOS ===")
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                self.clean_empty_vertex_groups(obj)

    def _reassign_modifiers(self, target_armature):
        """Reasigna modificadores de armature"""
        print("[DEBUG] === REASIGNANDO MODIFICADORES ===")
        
        for obj in bpy.context.scene.objects:
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

    def _cleanup_unwanted_armatures(self, target_armature, all_armatures):
        """Identifica y elimina armatures no deseados"""
        print("[DEBUG] === IDENTIFICANDO ARMATURES A ELIMINAR ===")
        
        armatures_to_remove = []
        
        for obj in all_armatures:
            if obj == target_armature:
                continue
            
            should_remove = False
            reason = ""
            
            if obj.name.startswith('Armature.'):
                should_remove = True
                reason = "Armature.XXX no deseado"
            elif len(obj.data.bones) == 0:
                should_remove = True
                reason = "Armature vacío"
            
            if should_remove:
                armatures_to_remove.append((obj, reason))
                print(f"[DEBUG] Marcado para eliminar: {obj.name} ({reason})")
        
        # Eliminar armatures
        self._remove_armatures(armatures_to_remove)

    def _remove_armatures(self, armatures_to_remove):
        """Elimina la lista de armatures"""
        print("[DEBUG] === ELIMINANDO ARMATURES ===")
        
        for arm_obj, reason in armatures_to_remove:
            try:
                print(f"[DEBUG] Eliminando: {arm_obj.name} - Razón: {reason}")
                
                if arm_obj.users > 0:
                    print(f"[DEBUG] Advertencia: {arm_obj.name} tiene {arm_obj.users} usuarios")
                
                bpy.data.objects.remove(arm_obj, do_unlink=True)
                print(f"[DEBUG] ✓ Eliminado: {arm_obj.name}")
                
            except Exception as e:
                print(f"[DEBUG] ✗ Error eliminando {arm_obj.name}: {e}")

    def _apply_spacing_to_armature(self, target_armature):
        """Aplica espaciado al armature target"""
        if not target_armature or target_armature.type != 'ARMATURE':
            return
            
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

    def _verify_and_cleanup_orphans(self):
        """Verifica el resultado y limpia datos huérfanos"""
        print("[DEBUG] === VERIFICANDO RESULTADO ===")
        
        remaining_armatures = [
            obj.name for obj in bpy.context.scene.objects 
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

    def _safe_mode_set(self, mode):
        """Cambia de modo de forma segura"""
        try:
            bpy.ops.object.mode_set(mode=mode)
        except Exception:
            pass

    def clean_armatures_keep_root_only(self):
        """
        Elimina todos los armatures excepto el que tenga 'Root' en su nombre.
        Si no encuentra ninguno con 'Root', mantiene solo el target_armature.
        """
        print("[DEBUG] Limpiando armatures - manteniendo solo el Root...")
        
        # Obtener todos los armatures en la escena
        all_armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
        
        if len(all_armatures) <= 1:
            print("[DEBUG] Solo hay 1 o ningún armature, no es necesario limpiar.")
            return
        
        # Buscar armature con 'Root' en el nombre
        root_armature = self._find_root_armature(all_armatures)
        
        if not root_armature:
            root_armature = self.settings.target_armature
            if not root_armature:
                print("[WARNING] No se encontró armature con 'Root' ni target_armature definido.")
                return
        
        print(f"[DEBUG] Armature a mantener: {root_armature.name}")
        
        # Reasignar dependencias antes de eliminar
        self._reassign_dependencies(all_armatures, root_armature)
        
        # Eliminar todos los otros armatures
        armatures_to_remove = [arm for arm in all_armatures if arm != root_armature]
        self._remove_armatures_safely(armatures_to_remove, root_armature)
        
        # Asegurar visibilidad del root
        self._ensure_armature_visibility(root_armature)
        
        print("[DEBUG] Limpieza de armatures completada.")

    def _find_root_armature(self, armatures):
        """Busca el armature con 'Root' en el nombre"""
        for armature in armatures:
            if 'root' in armature.name.lower():
                return armature
        return None

    def _reassign_dependencies(self, all_armatures, root_armature):
        """Reasigna todas las dependencias al root armature"""
        for armature in all_armatures:
            if armature == root_armature:
                continue
                
            # Reasignar meshes dependientes
            dependent_meshes = self._find_dependent_meshes(armature)
            for mesh in dependent_meshes:
                self._reassign_mesh_modifiers(mesh, armature, root_armature)
            
            # Reasignar objetos con parent
            self._reassign_children(armature, root_armature)

    def _find_dependent_meshes(self, armature):
        """Encuentra meshes que dependen del armature"""
        dependent_meshes = []
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE' and modifier.object == armature:
                        dependent_meshes.append(obj)
                        break
        return dependent_meshes

    def _reassign_mesh_modifiers(self, mesh, old_armature, new_armature):
        """Reasigna modificadores de un mesh a un nuevo armature"""
        for modifier in mesh.modifiers:
            if modifier.type == 'ARMATURE' and modifier.object == old_armature:
                modifier.object = new_armature
                print(f"[DEBUG] Reasignado modificador de {mesh.name} al armature Root")

    def _reassign_children(self, old_parent, new_parent):
        """Reasigna objetos hijos a un nuevo parent"""
        for obj in bpy.data.objects:
            if obj.parent == old_parent:
                obj.parent = new_parent
                print(f"[DEBUG] Reasignado parent de {obj.name} al armature Root")

    def _remove_armatures_safely(self, armatures_to_remove, root_armature):
        """Elimina armatures de forma segura"""
        for armature in armatures_to_remove:
            print(f"[DEBUG] Eliminando armature: {armature.name}")
            
            try:
                bpy.data.objects.remove(armature, do_unlink=True)
                print(f"[DEBUG] Armature {armature.name} eliminado exitosamente")
            except Exception as e:
                print(f"[ERROR] No se pudo eliminar armature {armature.name}: {e}")

    def _ensure_armature_visibility(self, armature):
        """Asegura que el armature esté visible"""
        armature.hide_set(False)
        armature.hide_viewport = False
        if hasattr(armature, 'hide_select'):
            armature.hide_select = False
        
        # Renombrar si es necesario
        if 'root' not in armature.name.lower():
            armature.name = "Root"
            print(f"[DEBUG] Armature renombrado a: {armature.name}")

    def convert(self) -> bool:
        """Función principal de conversión"""
        from . import external_pose_caller
        
        # Validar configuración inicial
        if not self._validate_conversion_setup():
            return False
        
        print("[DEBUG] Iniciando conversión a GTA SA...")
        
        # Preparar armatures
        self._prepare_armatures()
        
        # Aplicar transformaciones
        self._apply_transformations()
        
        # Aplicar pose manual antes del COPY_LOCATION
        self._apply_manual_pose()
        
        # Configurar mapeos de huesos
        mappings = self._get_enabled_mappings()
        if not mappings:
            print("[ERROR] No hay mapeos de huesos habilitados.")
            return False
        
        # Procesar mapeos
        target_to_sources = self._organize_mappings(mappings)
        
        # Aplicar constraints y pose
        self._apply_constraints_and_pose(target_to_sources)
        
        # Fusionar pesos
        self._merge_weights(target_to_sources)
        
        # Limpiar vertex groups no mapeados
        self._cleanup_unmapped_vertex_groups()
        
        # Unificar objetos
        joined_obj = self._unify_mesh_objects()
        
        # Configurar resultado final
        self._finalize_conversion(joined_obj)
        
        # Aplicar espaciado
        print("[DEBUG] === LLAMANDO A APPLY_BONE_SPACING ===")
        self.apply_bone_spacing(self.settings.target_armature)
        
        print("[DEBUG] Conversión finalizada con éxito.")
        return True

    def _validate_conversion_setup(self):
        """Valida la configuración antes de la conversión"""
        src = self.settings.source_armature
        tgt = self.settings.target_armature
        
        if not src or not tgt:
            print("[ERROR] Armature fuente o destino no definidos.")
            return False
            
        return True

    def _prepare_armatures(self):
        """Prepara los armatures para la conversión"""
        src = self.settings.source_armature
        
        # Hacer visible el armature fuente y sus hijos
        print("[DEBUG] Haciendo visible el armature fuente como medida de seguridad...")
        src.hide_set(False)
        src.hide_viewport = False
        if hasattr(src, 'hide_select'):
            src.hide_select = False
        
        # Hacer visibles todos los objetos hijos
        for obj in bpy.data.objects:
            if obj.parent == src:
                obj.hide_set(False)
                obj.hide_viewport = False
                if hasattr(obj, 'hide_select'):
                    obj.hide_select = False
                print(f"[DEBUG] Hecho visible: {obj.name}")

    def _apply_transformations(self):
        """Aplica transformaciones a los objetos"""
        src = self.settings.source_armature
        
        # Aplicar transformaciones al source_armature
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        src.select_set(True)
        bpy.context.view_layer.objects.active = src
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        # Aplicar a los hijos
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.parent == src:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    def _apply_manual_pose(self):
        """Aplica la pose manual antes del COPY_LOCATION"""
        try:
            from . import external_pose_caller
            external_pose_caller.apply_manual_pose_to_children_and_reassign(
                self.settings.target_armature
            )
            print("[DEBUG] Pose manual aplicada y horneada antes del copy_location")
        except Exception as e:
            print(f"[DEBUG] Error al hornear pose manual antes del copy_location: {e}")

    def _get_enabled_mappings(self):
        """Obtiene los mapeos habilitados"""
        return [
            (m.source_bone, m.target_bone)
            for m in self.settings.bone_mappings
            if m.enabled and m.source_bone and m.target_bone
        ]

    def _organize_mappings(self, mappings):
        """Organiza los mapeos por hueso destino y jerarquía"""
        src = self.settings.source_armature
        tgt = self.settings.target_armature
        
        target_to_sources = {}
        
        for source_bone, target_bone in mappings:
            if source_bone in src.pose.bones and target_bone in tgt.pose.bones:
                if target_bone not in target_to_sources:
                    target_to_sources[target_bone] = []
                target_to_sources[target_bone].append(source_bone)
        
        # Ordenar por jerarquía
        for target_bone in target_to_sources:
            source_bones = target_to_sources[target_bone]
            source_bones.sort(key=lambda x: self._get_bone_hierarchy_level(src, x))
            target_to_sources[target_bone] = source_bones
        
        return target_to_sources

    def _get_bone_hierarchy_level(self, armature, bone_name):
        """Obtiene el nivel de jerarquía del hueso"""
        if bone_name not in armature.pose.bones:
            return 999
            
        bone = armature.pose.bones[bone_name]
        level = 0
        parent = bone.parent
        
        while parent:
            level += 1
            parent = parent.parent
            
        return level

    def _apply_constraints_and_pose(self, target_to_sources):
        """Aplica constraints y pose"""
        src = self.settings.source_armature
        tgt = self.settings.target_armature
        
        bpy.context.view_layer.objects.active = tgt
        bpy.ops.object.mode_set(mode='POSE')
        
        # COPY LOCATION constraints
        for target_bone, source_bones in target_to_sources.items():
            if source_bones:
                primary_source = source_bones[0]
                tgt_bone = tgt.pose.bones[target_bone]
                constraint = tgt_bone.constraints.new('COPY_LOCATION')
                constraint.target = src
                constraint.subtarget = primary_source
                print(f"[DEBUG] {target_bone} seguirá la posición de {primary_source}")
        
        # Aplicar pose
        bpy.ops.pose.armature_apply()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Limpiar constraints
        for bone in tgt.pose.bones:
            bone.constraints.clear()

    def _merge_weights(self, target_to_sources):
        """Fusiona los pesos de los vertex groups"""
        src = self.settings.source_armature
        
        for obj in bpy.data.objects:
            if obj.type != 'MESH' or obj.parent != src:
                continue
            
            bpy.context.view_layer.objects.active = obj
            
            # Procesar cada grupo de huesos
            for target_bone, source_bones in target_to_sources.items():
                self._merge_vertex_group_weights(obj, target_bone, source_bones)

    def _merge_vertex_group_weights(self, obj, target_bone, source_bones):
        """Fusiona pesos de múltiples source bones en un target bone"""
        # Crear o encontrar el vertex group del hueso destino
        target_vg = self._get_or_create_vertex_group(obj, target_bone)
        
        # Fusionar todos los pesos de las fuentes
        for source_bone in source_bones:
            source_vg = self._find_vertex_group(obj, source_bone)
            
            if source_vg:
                print(f"[DEBUG] Fusionando pesos de {source_bone} -> {target_bone}")
                self._transfer_weights(obj, source_vg, target_vg)
                
                # Eliminar el vertex group fuente
                obj.vertex_groups.remove(source_vg)
                print(f"[DEBUG] Eliminado vertex group: {source_bone}")

    def _get_or_create_vertex_group(self, obj, name):
        """Obtiene o crea un vertex group"""
        for vg in obj.vertex_groups:
            if vg.name == name:
                return vg
        return obj.vertex_groups.new(name=name)

    def _find_vertex_group(self, obj, name):
        """Encuentra un vertex group por nombre"""
        for vg in obj.vertex_groups:
            if vg.name == name:
                return vg
        return None

    def _transfer_weights(self, obj, source_vg, target_vg):
        """Transfiere pesos de un vertex group a otro"""
        for vertex in obj.data.vertices:
            for group in vertex.groups:
                if group.group == source_vg.index:
                    target_vg.add([vertex.index], group.weight, 'ADD')

    def _cleanup_unmapped_vertex_groups(self):
        """Limpia vertex groups no mapeados"""
        src = self.settings.source_armature
        tgt = self.settings.target_armature
        
        target_bone_names = [bone.name for bone in tgt.data.bones]
        
        for obj in bpy.data.objects:
            if obj.type != 'MESH' or obj.parent != src:
                continue
            
            groups_to_remove = []
            
            for vg in obj.vertex_groups:
                if vg.name not in target_bone_names:
                    groups_to_remove.append((vg, vg.name))
            
            for vg, vg_name in groups_to_remove:
                obj.vertex_groups.remove(vg)
                print(f"[DEBUG] Eliminado vertex group no mapeado: {vg_name}")

    def _unify_mesh_objects(self):
        """Unifica todos los objetos mesh"""
        src = self.settings.source_armature
        
        mesh_objs = [
            obj for obj in bpy.data.objects 
            if obj.type == 'MESH' and obj.parent == src
        ]
        
        if not mesh_objs:
            return None
        
        # Seleccionar y unir
        bpy.ops.object.select_all(action='DESELECT')
        for obj in mesh_objs:
            obj.select_set(True)
        
        bpy.context.view_layer.objects.active = mesh_objs[0]
        bpy.ops.object.join()
        
        joined_obj = bpy.context.active_object
        joined_obj.name = "Mesh"
        joined_obj.parent = None
        
        return joined_obj

    def _finalize_conversion(self, joined_obj):
        """Finaliza la conversión"""
        src = self.settings.source_armature
        tgt = self.settings.target_armature
        
        # Agregar modificador de Armature
        if joined_obj:
            mod = joined_obj.modifiers.new(name="Armature", type='ARMATURE')
            mod.object = tgt
        
        # Borrar armature fuente
        bpy.data.objects.remove(src, do_unlink=True)
        
        # Purgar objetos no visibles
        self._purge_invisible_objects()
        
        # Marcar armature destino como In Front
        tgt.show_in_front = True
        
        # Eliminar el objeto padre del target_armature
        if tgt.parent and tgt.parent.name != tgt.name:
            try:
                bpy.data.objects.remove(tgt.parent, do_unlink=True)
            except:
                print("[DEBUG] No se pudo eliminar el padre del target_armature.")
        
        # Mover el hueso root a (0, 0, 0)
        self._move_root_to_origin(tgt)

    def _purge_invisible_objects(self):
        """Purga objetos no visibles en la ViewLayer"""
        used_names = {obj.name for obj in bpy.context.view_layer.objects if obj}
        
        for obj in list(bpy.data.objects):
            if obj.name not in used_names:
                try:
                    bpy.data.objects.remove(obj, do_unlink=True)
                except:
                    pass

    def _move_root_to_origin(self, armature):
        """Mueve el hueso root del armature a (0, 0, 0)"""
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
        
        try:
            if len(armature.data.edit_bones) > 0:
                root_bone = armature.data.edit_bones[0]
                
                # Guardar las propiedades originales
                original_length = root_bone.length
                original_vector = root_bone.tail - root_bone.head
                original_roll = root_bone.roll
                
                # Calcular el offset
                offset = Vector((0.0, 0.0, 0.0)) - root_bone.head
                
                # Mover el hueso
                root_bone.head += offset
                root_bone.tail += offset
                
                # Verificar integridad
                if abs(root_bone.length - original_length) > 0.0001:
                    root_bone.tail = root_bone.head + original_vector.normalized() * original_length
                
                root_bone.roll = original_roll
                
                print(f"[DEBUG] Hueso root movido a (0,0,0). Longitud: {root_bone.length:.4f}, Roll: {root_bone.roll:.4f}")
                
        except Exception as e:
            print(f"[DEBUG] No se pudo mover el hueso root: {e}")
        
        bpy.ops.object.mode_set(mode='OBJECT')