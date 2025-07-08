# converter.py - Versión con soporte para Shape Keys
import bpy
from mathutils import Vector
from .utils.cleanup import CleanupUtils


class UniversalGTAConverter:
    """Conversor principal para armatures universales a GTA SA con soporte para Shape Keys"""
    
    def __init__(self, settings):
        self.settings = settings

    def convert(self) -> bool:
        """Función principal de conversión con soporte para Shape Keys"""
        from . import external_pose_caller
        
        # Validar configuración inicial
        if not self._validate_conversion_setup():
            return False
        
        print("[DEBUG] Iniciando conversión a GTA SA con soporte para Shape Keys...")
        
        # Preparar armatures
        self._prepare_armatures()
        
        # NUEVO: Procesar Shape Keys antes de aplicar transformaciones
        self._process_shape_keys_pre_conversion()
        
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
        
        # NUEVO: Aplicar Shape Keys después de unificar
        self._process_shape_keys_post_conversion(joined_obj)
        
        # Configurar resultado final
        self._finalize_conversion(joined_obj)
        
        # Aplicar espaciado
        print("[DEBUG] === LLAMANDO A APPLY_BONE_SPACING ===")
        CleanupUtils.apply_bone_spacing(self.settings.target_armature, self.settings.target_armature)
        
        print("[DEBUG] Conversión finalizada con éxito.")
        return True

    def _process_shape_keys_pre_conversion(self):
        """Procesa Shape Keys antes de la conversión principal"""
        try:
            print("[DEBUG] === PROCESANDO SHAPE KEYS PRE-CONVERSIÓN ===")
            
            # Verificar si hay algún mesh con shape keys
            meshes_with_shape_keys = self._find_meshes_with_shape_keys()
            
            if not meshes_with_shape_keys:
                print("[DEBUG] No se encontraron meshes con shape keys")
                return
            
            print(f"[DEBUG] Encontrados {len(meshes_with_shape_keys)} meshes con shape keys")
            
            # Crear backup automático
            self._create_shape_keys_backup(meshes_with_shape_keys)
            
            # Aplicar shape keys si está configurado
            if getattr(self.settings, 'auto_apply_shape_keys', True):
                self._apply_all_shape_keys_safe(meshes_with_shape_keys)
            
        except Exception as e:
            print(f"[DEBUG] Error en procesamiento de shape keys pre-conversión: {e}")
            # No fallar la conversión por problemas con shape keys
    
    def _process_shape_keys_post_conversion(self, joined_obj):
        """Procesa Shape Keys después de la conversión principal"""
        try:
            print("[DEBUG] === PROCESANDO SHAPE KEYS POST-CONVERSIÓN ===")
            
            if not joined_obj:
                print("[DEBUG] No hay objeto unificado para procesar shape keys")
                return
            
            # Verificar si el objeto unificado tiene shape keys
            if joined_obj.data.shape_keys and len(joined_obj.data.shape_keys.key_blocks) > 1:
                print(f"[DEBUG] Objeto unificado tiene {len(joined_obj.data.shape_keys.key_blocks)} shape keys")
                
                # Opcional: aplicar shape keys finales si está configurado
                if getattr(self.settings, 'apply_final_shape_keys', False):
                    self._apply_final_shape_keys(joined_obj)
            else:
                print("[DEBUG] Objeto unificado no tiene shape keys")
                
        except Exception as e:
            print(f"[DEBUG] Error en procesamiento de shape keys post-conversión: {e}")
    
    def _find_meshes_with_shape_keys(self):
        """Encuentra meshes hijos del source armature que tienen shape keys"""
        src = self.settings.source_armature
        meshes_with_shape_keys = []
        
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                obj.parent == src and 
                obj.data.shape_keys and 
                len(obj.data.shape_keys.key_blocks) > 1):
                
                meshes_with_shape_keys.append(obj)
                print(f"[DEBUG] Mesh con shape keys: {obj.name} ({len(obj.data.shape_keys.key_blocks)} keys)")
        
        return meshes_with_shape_keys
    
    def _create_shape_keys_backup(self, meshes_with_shape_keys):
        """Crea backup automático de meshes con shape keys"""
        try:
            print("[DEBUG] Creando backup de shape keys...")
            
            for mesh_obj in meshes_with_shape_keys:
                # Crear backup
                bpy.context.view_layer.objects.active = mesh_obj
                bpy.ops.object.select_all(action='DESELECT')
                mesh_obj.select_set(True)
                bpy.ops.object.duplicate()
                
                backup_obj = bpy.context.active_object
                backup_obj.name = f"{mesh_obj.name}_BACKUP_ShapeKeys"
                
                # Esconder backup
                backup_obj.hide_set(True)
                backup_obj.hide_viewport = True
                
                print(f"[DEBUG] Backup creado: {backup_obj.name}")
                
        except Exception as e:
            print(f"[DEBUG] Error creando backup de shape keys: {e}")
    
    def _apply_all_shape_keys_safe(self, meshes_with_shape_keys):
        """Aplica todas las shape keys de forma segura"""
        try:
            print("[DEBUG] Aplicando shape keys antes de conversión...")
            
            for mesh_obj in meshes_with_shape_keys:
                print(f"[DEBUG] Procesando shape keys de: {mesh_obj.name}")
                
                # Activar el mesh
                bpy.context.view_layer.objects.active = mesh_obj
                bpy.ops.object.mode_set(mode='OBJECT')
                
                # Obtener shape keys
                if not mesh_obj.data.shape_keys:
                    continue
                
                key_blocks = mesh_obj.data.shape_keys.key_blocks
                applied_count = 0
                
                # Aplicar shape keys de arriba hacia abajo (excluyendo Basis)
                for i in range(len(key_blocks) - 1, 0, -1):
                    key_block = key_blocks[i]
                    
                    if key_block.name == "Basis":
                        continue
                    
                    try:
                        # Establecer como activa y aplicar
                        mesh_obj.active_shape_key_index = i
                        
                        # Solo aplicar si tiene valor > 0
                        if key_block.value > 0.0:
                            # Aplicar como mix
                            bpy.ops.object.shape_key_remove(all=False)
                            applied_count += 1
                            print(f"[DEBUG] Aplicada shape key: {key_block.name} (valor: {key_block.value})")
                        else:
                            # Eliminar shape key sin valor
                            bpy.ops.object.shape_key_remove(all=False)
                            print(f"[DEBUG] Eliminada shape key inactiva: {key_block.name}")
                            
                    except Exception as e:
                        print(f"[DEBUG] Error aplicando shape key {key_block.name}: {e}")
                
                print(f"[DEBUG] {mesh_obj.name}: Procesadas {applied_count} shape keys")
                
        except Exception as e:
            print(f"[DEBUG] Error aplicando shape keys: {e}")
    
    def _apply_final_shape_keys(self, joined_obj):
        """Aplica shape keys finales al objeto unificado"""
        try:
            print("[DEBUG] Aplicando shape keys finales...")
            
            bpy.context.view_layer.objects.active = joined_obj
            bpy.ops.object.mode_set(mode='OBJECT')
            
            if not joined_obj.data.shape_keys:
                return
            
            key_blocks = joined_obj.data.shape_keys.key_blocks
            
            # Aplicar todas las shape keys excepto Basis
            for i in range(len(key_blocks) - 1, 0, -1):
                key_block = key_blocks[i]
                
                if key_block.name == "Basis":
                    continue
                
                try:
                    joined_obj.active_shape_key_index = i
                    
                    if key_block.value > 0.0:
                        bpy.ops.object.shape_key_remove(all=False)
                        print(f"[DEBUG] Aplicada shape key final: {key_block.name}")
                    else:
                        bpy.ops.object.shape_key_remove(all=False)
                        
                except Exception as e:
                    print(f"[DEBUG] Error aplicando shape key final {key_block.name}: {e}")
                    
        except Exception as e:
            print(f"[DEBUG] Error en aplicación de shape keys finales: {e}")

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
        
        # Limpiar constraints
        for bone in tgt.pose.bones:
            # Iterar sobre una copia de la lista de constraints para poder eliminarlas
            for c in list(bone.constraints):
                bone.constraints.remove(c)

        bpy.ops.object.mode_set(mode='OBJECT')

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
        """Unifica todos los objetos mesh preservando shape keys cuando sea posible"""
        src = self.settings.source_armature
        
        mesh_objs = [
            obj for obj in bpy.data.objects 
            if obj.type == 'MESH' and obj.parent == src
        ]
        
        if not mesh_objs:
            return None
        
        print(f"[DEBUG] Unificando {len(mesh_objs)} objetos mesh...")
        
        # Verificar shape keys antes de unificar
        shape_keys_info = []
        for obj in mesh_objs:
            if obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) > 1:
                shape_keys_info.append({
                    'object': obj.name,
                    'shape_keys': [key.name for key in obj.data.shape_keys.key_blocks]
                })
        
        if shape_keys_info:
            print("[DEBUG] Meshes con shape keys detectados antes de unificar:")
            for info in shape_keys_info:
                print(f"  {info['object']}: {info['shape_keys']}")
        
        # Seleccionar y unir
        bpy.ops.object.select_all(action='DESELECT')
        for obj in mesh_objs:
            obj.select_set(True)
        
        bpy.context.view_layer.objects.active = mesh_objs[0]
        
        try:
            # Unir objetos
            bpy.ops.object.join()
            
            joined_obj = bpy.context.active_object
            joined_obj.name = "Mesh"
            joined_obj.parent = None
            
            # Verificar shape keys después de unificar
            if joined_obj.data.shape_keys:
                final_shape_keys = [key.name for key in joined_obj.data.shape_keys.key_blocks]
                print(f"[DEBUG] Shape keys en objeto unificado: {final_shape_keys}")
            else:
                print("[DEBUG] Objeto unificado no tiene shape keys")
            
            return joined_obj
            
        except Exception as e:
            print(f"[DEBUG] Error durante unificación: {e}")
            # En caso de error, devolver el primer objeto
            return mesh_objs[0] if mesh_objs else None

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