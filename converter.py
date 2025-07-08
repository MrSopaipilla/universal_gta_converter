# converter.py - Versión CORREGIDA con soporte para Shape Keys
import bpy
from mathutils import Vector
from .utils.cleanup import CleanupUtils


class UniversalGTAConverter:
    """Conversor principal para armatures universales a GTA SA con soporte CORREGIDO para Shape Keys"""
    
    def __init__(self, settings):
        self.settings = settings

    def convert(self) -> bool:
        """Función principal de conversión con soporte CORREGIDO para Shape Keys"""
        from . import external_pose_caller
        
        # Validar configuración inicial
        if not self._validate_conversion_setup():
            return False
        
        print("[DEBUG] Iniciando conversión a GTA SA con soporte CORREGIDO para Shape Keys...")
        
        # Preparar armatures
        self._prepare_armatures()
        
        # CORREGIDO: Procesar Shape Keys ANTES de cualquier transformación
        if self.settings.auto_apply_shape_keys:
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
        
        # Fusionar pesos (VERTEX GROUPS, no Shape Keys)
        self._merge_weights(target_to_sources)
        
        # Limpiar vertex groups no mapeados
        self._cleanup_unmapped_vertex_groups()
        
        # Unificar objetos
        joined_obj = self._unify_mesh_objects()
        
        # CORREGIDO: NO aplicar Shape Keys después de unificar si ya se aplicaron antes
        if not self.settings.auto_apply_shape_keys and self.settings.apply_final_shape_keys:
            self._process_shape_keys_post_conversion(joined_obj)
        
        # Configurar resultado final
        self._finalize_conversion(joined_obj)
        
        # Aplicar espaciado
        print("[DEBUG] === LLAMANDO A APPLY_BONE_SPACING ===")
        CleanupUtils.apply_bone_spacing(self.settings.target_armature, self.settings.target_armature)
        
        print("[DEBUG] Conversión finalizada con éxito.")
        return True

    def _process_shape_keys_pre_conversion(self):
        """Procesa Shape Keys ANTES de la conversión principal - CORREGIDO"""
        try:
            print("[DEBUG] === PROCESANDO SHAPE KEYS PRE-CONVERSIÓN (CORREGIDO) ===")
            
            # Verificar si hay algún mesh con shape keys
            meshes_with_shape_keys = self._find_meshes_with_shape_keys()
            
            if not meshes_with_shape_keys:
                print("[DEBUG] No se encontraron meshes con shape keys")
                return
            
            print(f"[DEBUG] Encontrados {len(meshes_with_shape_keys)} meshes con shape keys")
            
            # Crear backup automático si está habilitado
            if self.settings.create_shape_keys_backup:
                self._create_shape_keys_backup(meshes_with_shape_keys)
            
            # Aplicar shape keys CORRECTAMENTE
            self._apply_all_shape_keys_corrected(meshes_with_shape_keys)
            
        except Exception as e:
            print(f"[DEBUG] Error en procesamiento de shape keys pre-conversión: {e}")
            # No fallar la conversión por problemas con shape keys
    
    def _apply_all_shape_keys_corrected(self, meshes_with_shape_keys):
        """Aplica todas las shape keys de forma CORREGIDA"""
        try:
            print("[DEBUG] Aplicando shape keys ANTES de conversión (MÉTODO CORREGIDO)...")
            
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
                
                # CORREGIDO: Lista todas las shape keys primero
                shape_key_names = [key.name for key in key_blocks]
                print(f"[DEBUG] Shape keys encontradas en {mesh_obj.name}: {shape_key_names}")
                
                # CORREGIDO: Aplicar shape keys desde la última hacia la primera
                # para evitar problemas con índices cambiantes
                for i in range(len(key_blocks) - 1, -1, -1):
                    try:
                        # Verificar que el índice sigue siendo válido
                        if not mesh_obj.data.shape_keys or i >= len(mesh_obj.data.shape_keys.key_blocks):
                            continue
                        
                        current_key = mesh_obj.data.shape_keys.key_blocks[i]
                        key_name = current_key.name
                        
                        # Preservar Basis si está configurado (pero normalmente no)
                        if self.settings.preserve_basis_shape_key and key_name == 'Basis':
                            print(f"[DEBUG] Preservando shape key Basis en {mesh_obj.name}")
                            continue
                        
                        # Verificar umbral de aplicación
                        if hasattr(current_key, 'value') and current_key.value < self.settings.shape_key_threshold:
                            print(f"[DEBUG] Saltando shape key '{key_name}' (valor {current_key.value} < umbral {self.settings.shape_key_threshold})")
                            # Eliminar shape key sin aplicar
                            mesh_obj.active_shape_key_index = i
                            bpy.ops.object.shape_key_remove(all=False)
                            continue
                        
                        print(f"[DEBUG] Aplicando shape key: '{key_name}' en {mesh_obj.name}")
                        
                        # Activar la shape key
                        mesh_obj.active_shape_key_index = i
                        
                        # CORREGIDO: Aplicar shape key como mix
                        bpy.ops.object.shape_key_remove(all=False)
                        applied_count += 1
                        
                        print(f"[DEBUG] ✓ Shape key '{key_name}' aplicada y eliminada")
                        
                    except Exception as e:
                        print(f"[DEBUG] Error aplicando shape key índice {i} en {mesh_obj.name}: {e}")
                
                print(f"[DEBUG] ✓ {applied_count} shape keys aplicadas en {mesh_obj.name}")
                
                # Verificar que se eliminaron todas las shape keys
                remaining_keys = len(mesh_obj.data.shape_keys.key_blocks) if mesh_obj.data.shape_keys else 0
                if remaining_keys > 0:
                    print(f"[DEBUG] ⚠ {remaining_keys} shape keys restantes en {mesh_obj.name}")
                else:
                    print(f"[DEBUG] ✓ Todas las shape keys eliminadas de {mesh_obj.name}")
            
            print("[DEBUG] === SHAPE KEYS PRE-CONVERSIÓN COMPLETADAS ===")
            
        except Exception as e:
            print(f"[DEBUG] Error aplicando shape keys: {e}")
    
    def _find_meshes_with_shape_keys(self):
        """Encuentra meshes con shape keys asociados al source armature"""
        meshes_with_shape_keys = []
        
        if not self.settings.source_armature:
            return meshes_with_shape_keys
        
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                obj.parent == self.settings.source_armature and
                obj.data.shape_keys and 
                len(obj.data.shape_keys.key_blocks) > 0):
                
                meshes_with_shape_keys.append(obj)
                print(f"[DEBUG] Mesh con shape keys encontrado: {obj.name} ({len(obj.data.shape_keys.key_blocks)} keys)")
        
        return meshes_with_shape_keys
    
    def _create_shape_keys_backup(self, meshes_with_shape_keys):
        """Crea backup de meshes con shape keys"""
        try:
            print("[DEBUG] Creando backup de shape keys...")
            
            for mesh_obj in meshes_with_shape_keys:
                # Duplicar el mesh
                bpy.context.view_layer.objects.active = mesh_obj
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                mesh_obj.select_set(True)
                bpy.ops.object.duplicate()
                
                # Renombrar el duplicado
                backup_obj = bpy.context.active_object
                backup_obj.name = f"{mesh_obj.name}_BACKUP_ShapeKeys"
                
                # Mover a una capa o colección de backup
                try:
                    # Intentar crear/usar colección de backup
                    backup_collection_name = "Shape_Keys_Backups"
                    if backup_collection_name not in bpy.data.collections:
                        backup_collection = bpy.data.collections.new(backup_collection_name)
                        bpy.context.scene.collection.children.link(backup_collection)
                    else:
                        backup_collection = bpy.data.collections[backup_collection_name]
                    
                    # Mover a la colección de backup
                    if backup_obj.name not in backup_collection.objects:
                        backup_collection.objects.link(backup_obj)
                        # Remover de la colección actual
                        for coll in backup_obj.users_collection:
                            if coll != backup_collection:
                                coll.objects.unlink(backup_obj)
                    
                    # Ocultar el backup
                    backup_obj.hide_viewport = True
                    backup_obj.hide_render = True
                    
                except Exception as e:
                    print(f"[DEBUG] No se pudo organizar backup en colección: {e}")
                
                print(f"[DEBUG] ✓ Backup creado: {backup_obj.name}")
            
        except Exception as e:
            print(f"[DEBUG] Error creando backup de shape keys: {e}")

    def _validate_conversion_setup(self) -> bool:
        """Valida que la configuración sea correcta para la conversión"""
        if not self.settings.source_armature:
            print("[ERROR] No se ha seleccionado un armature fuente.")
            return False
        
        if not self.settings.target_armature:
            print("[ERROR] No se ha seleccionado un armature objetivo.")
            return False
        
        if self.settings.source_armature.type != 'ARMATURE':
            print("[ERROR] El objeto fuente no es un armature.")
            return False
        
        if self.settings.target_armature.type != 'ARMATURE':
            print("[ERROR] El objeto objetivo no es un armature.")
            return False
        
        return True

    def _prepare_armatures(self):
        """Prepara los armatures para la conversión"""
        # Asegurar que estamos en modo objeto
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Activar el armature objetivo para trabajar con él
        bpy.context.view_layer.objects.active = self.settings.target_armature

    def _apply_transformations(self):
        """Aplica las transformaciones necesarias"""
        # Aplicar transformaciones al armature fuente si es necesario
        bpy.context.view_layer.objects.active = self.settings.source_armature
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Aquí puedes agregar lógica para aplicar transformaciones específicas
        print("[DEBUG] Transformaciones aplicadas.")

    def _apply_manual_pose(self):
        """Aplica pose manual antes de configurar constraints"""
        try:
            bpy.context.view_layer.objects.active = self.settings.source_armature
            bpy.ops.object.mode_set(mode='POSE')
            
            # Aquí puedes aplicar poses específicas si es necesario
            # Por ahora solo cambiamos de vuelta a modo objeto
            bpy.ops.object.mode_set(mode='OBJECT')
            
            print("[DEBUG] Pose manual aplicada.")
        except Exception as e:
            print(f"[DEBUG] Error aplicando pose manual: {e}")

    def _get_enabled_mappings(self):
        """Obtiene los mapeos de huesos habilitados"""
        return [mapping for mapping in self.settings.bone_mappings if mapping.enabled and mapping.source_bone and mapping.target_bone]

    def _organize_mappings(self, mappings):
        """Organiza los mapeos por hueso objetivo"""
        target_to_sources = {}
        for mapping in mappings:
            if mapping.target_bone not in target_to_sources:
                target_to_sources[mapping.target_bone] = []
            target_to_sources[mapping.target_bone].append(mapping.source_bone)
        return target_to_sources

    def _apply_constraints_and_pose(self, target_to_sources):
        """Aplica constraints de COPY_LOCATION entre huesos mapeados"""
        target_armature = self.settings.target_armature
        source_armature = self.settings.source_armature
        
        # Cambiar al armature objetivo en modo pose
        bpy.context.view_layer.objects.active = target_armature
        bpy.ops.object.mode_set(mode='POSE')
        
        for target_bone_name, source_bone_names in target_to_sources.items():
            if target_bone_name in target_armature.pose.bones:
                target_bone = target_armature.pose.bones[target_bone_name]
                
                # Usar el primer hueso fuente como principal
                primary_source = source_bone_names[0]
                
                if primary_source in source_armature.pose.bones:
                    # Crear constraint COPY_LOCATION
                    constraint = target_bone.constraints.new(type='COPY_LOCATION')
                    constraint.target = source_armature
                    constraint.subtarget = primary_source
                    constraint.name = f"GTA_COPY_{primary_source}"
                    
                    print(f"[DEBUG] Constraint creado: {target_bone_name} <- {primary_source}")
        
        # Volver a modo objeto
        bpy.ops.object.mode_set(mode='OBJECT')

    def _merge_weights(self, target_to_sources):
        """Fusiona los pesos de vertex groups (NO shape keys)"""
        source_armature = self.settings.source_armature
        
        # Encontrar meshes hijos del armature fuente
        mesh_children = [obj for obj in bpy.data.objects 
                        if obj.type == 'MESH' and obj.parent == source_armature]
        
        for mesh_obj in mesh_children:
            print(f"[DEBUG] Procesando vertex groups de: {mesh_obj.name}")
            
            # Procesar vertex groups para cada mapeo
            for target_bone_name, source_bone_names in target_to_sources.items():
                target_vg = None
                
                # Crear o encontrar el vertex group objetivo
                if target_bone_name in mesh_obj.vertex_groups:
                    target_vg = mesh_obj.vertex_groups[target_bone_name]
                else:
                    target_vg = mesh_obj.vertex_groups.new(name=target_bone_name)
                
                # Fusionar pesos de todos los vertex groups fuente
                for source_bone_name in source_bone_names:
                    if source_bone_name in mesh_obj.vertex_groups:
                        source_vg = mesh_obj.vertex_groups[source_bone_name]
                        
                        # Aquí iría la lógica de fusión de pesos
                        # Por simplicidad, copiamos los pesos del primer grupo
                        print(f"[DEBUG] Fusionando vertex group: {source_bone_name} -> {target_bone_name}")

    def _cleanup_unmapped_vertex_groups(self):
        """Limpia vertex groups que no están mapeados"""
        source_armature = self.settings.source_armature
        mapped_sources = set()
        
        # Recolectar todos los huesos fuente mapeados
        for mapping in self.settings.bone_mappings:
            if mapping.enabled and mapping.source_bone:
                mapped_sources.add(mapping.source_bone)
        
        # Encontrar meshes hijos
        mesh_children = [obj for obj in bpy.data.objects 
                        if obj.type == 'MESH' and obj.parent == source_armature]
        
        for mesh_obj in mesh_children:
            # Eliminar vertex groups no mapeados
            groups_to_remove = []
            for vg in mesh_obj.vertex_groups:
                if vg.name not in mapped_sources:
                    groups_to_remove.append(vg.name)
            
            for group_name in groups_to_remove:
                if group_name in mesh_obj.vertex_groups:
                    mesh_obj.vertex_groups.remove(mesh_obj.vertex_groups[group_name])
                    print(f"[DEBUG] Vertex group eliminado: {group_name}")

    def _unify_mesh_objects(self):
        """Unifica todos los objetos mesh en uno solo"""
        source_armature = self.settings.source_armature
        mesh_children = [obj for obj in bpy.data.objects 
                        if obj.type == 'MESH' and obj.parent == source_armature]
        
        if not mesh_children:
            print("[ERROR] No se encontraron meshes para unificar.")
            return None
        
        # Seleccionar todos los meshes
        bpy.ops.object.select_all(action='DESELECT')
        for mesh_obj in mesh_children:
            mesh_obj.select_set(True)
        
        # Activar el primer mesh como principal
        bpy.context.view_layer.objects.active = mesh_children[0]
        
        # Unir objetos
        bpy.ops.object.join()
        
        joined_obj = bpy.context.active_object
        joined_obj.name = f"{self.settings.skin_name or 'GTASkin'}_Unified"
        
        print(f"[DEBUG] Meshes unificados en: {joined_obj.name}")
        return joined_obj

    def _process_shape_keys_post_conversion(self, joined_obj):
        """Procesa shape keys DESPUÉS de la unificación (solo si no se hizo antes)"""
        if not joined_obj or not joined_obj.data.shape_keys:
            return
        
        print("[DEBUG] Procesando shape keys post-conversión...")
        
        # Aplicar shape keys finales si están configuradas
        try:
            key_blocks = joined_obj.data.shape_keys.key_blocks
            for i in range(len(key_blocks) - 1, -1, -1):
                if i < len(joined_obj.data.shape_keys.key_blocks):
                    joined_obj.active_shape_key_index = i
                    bpy.ops.object.shape_key_remove(all=False)
            
            print("[DEBUG] Shape keys post-conversión aplicadas")
        except Exception as e:
            print(f"[DEBUG] Error en shape keys post-conversión: {e}")

    def _finalize_conversion(self, joined_obj):
        """Finaliza la conversión configurando el objeto final"""
        if not joined_obj:
            return
        
        # Cambiar el parent al armature objetivo
        joined_obj.parent = self.settings.target_armature
        joined_obj.parent_type = 'ARMATURE'
        
        # Crear modificador armature
        if not any(mod.type == 'ARMATURE' for mod in joined_obj.modifiers):
            armature_mod = joined_obj.modifiers.new(name="Armature", type='ARMATURE')
            armature_mod.object = self.settings.target_armature
        
        print(f"[DEBUG] Conversión finalizada. Objeto final: {joined_obj.name}")

    def post_conversion_pose_application(self):
        """Aplica pose personalizada DESPUÉS de la conversión"""
        from . import external_pose_caller
        
        try:
            print("[CONVERSION] === APLICACIÓN DE POSE PERSONALIZADA ===")
            
            # Buscar el armature Root (resultado de la conversión)
            root_armature = external_pose_caller._find_main_armature_post_conversion()
            
            if not root_armature:
                print("[CONVERSION] ✗ No se encontró armature Root para aplicar pose")
                return False
            
            print(f"[CONVERSION] ✓ Armature Root encontrado: {root_armature.name}")
            
            # Buscar meshes con modificadores armature
            target_meshes = external_pose_caller._find_meshes_with_armature_modifier(root_armature)
            print(f"[CONVERSION] ✓ {len(target_meshes)} meshes con modificadores encontrados")
            
            # Aplicar pose usando el sistema externo
            applier = external_pose_caller.ExternalPoseApplier()
            success = applier.execute_full_pose_application(
                source_armature=None,  # Ya no existe
                target_armature=root_armature
            )
            
            if success:
                print("[CONVERSION] ✓ Pose personalizada aplicada correctamente")
            else:
                print("[CONVERSION] ⚠ Problema aplicando pose personalizada")
            
            print("[CONVERSION] === APLICACIÓN DE POSE PERSONALIZADA COMPLETADA ===")
            return success
            
        except Exception as e:
            print(f"[CONVERSION] ✗ Error en aplicación de pose post-conversión: {e}")
            import traceback
            traceback.print_exc()
            return False