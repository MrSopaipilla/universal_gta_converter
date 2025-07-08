# converter.py - Versión mejorada
import bpy
from mathutils import Vector
from .utils.cleanup import CleanupUtils


class UniversalGTAConverter:
    """Conversor principal para armatures universales a GTA SA"""
    
    def __init__(self, settings):
        self.settings = settings

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
        CleanupUtils.apply_bone_spacing(self.settings.target_armature, self.settings.target_armature)
        
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