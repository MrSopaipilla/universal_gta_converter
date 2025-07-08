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
            
            # DIAGNÓSTICO: Verificar meshes y sus modificadores
            print("[DEBUG] Meshes y sus modificadores de armature:")
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH':
                    print(f"  Mesh: {obj.name}")
                    for modifier in obj.modifiers:
                        if modifier.type == 'ARMATURE':
                            armature_name = modifier.object.name if modifier.object else "None"
                            print(f"    - Modifier: {modifier.name} -> {armature_name}")
            
            # PASO 1: Limpiar vertex groups vacíos de todos los objetos mesh
            print("[DEBUG] === LIMPIANDO VERTEX GROUPS VACÍOS ===")
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH':
                    self.clean_empty_vertex_groups(obj)
            
            # PASO 2: Reasignar modificadores
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
            for obj in bpy.context.scene.objects:
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
            
        except Exception as e:
            print(f"[DEBUG] ERROR GENERAL en apply_bone_spacing: {e}")
            import traceback
            traceback.print_exc()
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
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
        
        # Buscar armature con 'Root' en el nombre (case insensitive)
        root_armature = None
        for armature in all_armatures:
            if 'root' in armature.name.lower():
                root_armature = armature
                break
        
        # Si no encuentra 'Root', usar el target_armature
        if not root_armature:
            root_armature = self.settings.target_armature
            if not root_armature:
                print("[WARNING] No se encontró armature con 'Root' ni target_armature definido.")
                return
        
        print(f"[DEBUG] Armature a mantener: {root_armature.name}")
        
        # Eliminar todos los otros armatures
        armatures_to_remove = [arm for arm in all_armatures if arm != root_armature]
        
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
            except Exception as e:
                print(f"[ERROR] No se pudo eliminar armature {armature.name}: {e}")
        
        # Asegurar que el root_armature esté visible y seleccionable
        root_armature.hide_set(False)
        root_armature.hide_viewport = False
        if hasattr(root_armature, 'hide_select'):
            root_armature.hide_select = False
        
        # Opcional: renombrar el armature final como "Root" si no lo tiene ya
        if 'root' not in root_armature.name.lower():
            root_armature.name = "Root"
            print(f"[DEBUG] Armature renombrado a: {root_armature.name}")
        
        print("[DEBUG] Limpieza de armatures completada.")

    def convert(self) -> bool:
        """Función principal de conversión"""
        from . import external_pose_caller
        
        src = self.settings.source_armature
        tgt = self.settings.target_armature
        if not src or not tgt:
            print("[ERROR] Armature fuente o destino no definidos.")
            return False
        print("[DEBUG] Iniciando conversión a GTA SA...")
        
        # MEDIDA DE SEGURIDAD: Hacer visible el armature fuente y sus hijos
        print("[DEBUG] Haciendo visible el armature fuente como medida de seguridad...")
        src.hide_set(False)
        src.hide_viewport = False
        if hasattr(src, 'hide_select'):
            src.hide_select = False
        
        # Hacer visibles todos los objetos hijos del armature fuente
        for obj in bpy.data.objects:
            if obj.parent == src:
                obj.hide_set(False)
                obj.hide_viewport = False
                if hasattr(obj, 'hide_select'):
                    obj.hide_select = False
                print(f"[DEBUG] Hecho visible: {obj.name}")
        
        # Aplicar transformaciones al source_armature y sus hijos
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        src.select_set(True)
        bpy.context.view_layer.objects.active = src
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.parent == src:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        bpy.context.view_layer.objects.active = tgt
        bpy.ops.object.mode_set(mode='POSE')
        
        # --- Aplicar y hornear la pose manual antes del COPY_LOCATION ---
        try:
            external_pose_caller.apply_manual_pose_to_children_and_reassign(self.settings.target_armature)
            print("[DEBUG] Pose manual aplicada y horneada antes del copy_location")
        except Exception as e:
            print(f"[DEBUG] Error al hornear pose manual antes del copy_location: {e}")

        mappings = [
            (m.source_bone, m.target_bone)
            for m in self.settings.bone_mappings
            if m.enabled and m.source_bone and m.target_bone
        ]

        # 1. Organizar mapeos por hueso destino y jerarquía
        target_to_sources = {}
        for source_bone, target_bone in mappings:
            if source_bone in src.pose.bones and target_bone in tgt.pose.bones:
                if target_bone not in target_to_sources:
                    target_to_sources[target_bone] = []
                target_to_sources[target_bone].append(source_bone)
        
        # Ordenar por jerarquía (huesos padre primero)
        def get_bone_hierarchy_level(armature, bone_name):
            """Obtiene el nivel de jerarquía del hueso (0 = root, 1 = hijo de root, etc.)"""
            if bone_name not in armature.pose.bones:
                return 999
            bone = armature.pose.bones[bone_name]
            level = 0
            parent = bone.parent
            while parent:
                level += 1
                parent = parent.parent
            return level
        
        # Para cada hueso destino, ordenar los fuentes por jerarquía
        for target_bone in target_to_sources:
            source_bones = target_to_sources[target_bone]
            # Ordenar por nivel de jerarquía (padres primero)
            source_bones.sort(key=lambda x: get_bone_hierarchy_level(src, x))
            target_to_sources[target_bone] = source_bones
        
        # 2. COPY LOCATION constraints (solo para el hueso principal de cada grupo)
        for target_bone, source_bones in target_to_sources.items():
            if source_bones:
                # Solo el primer hueso (más arriba en jerarquía) controla la posición
                primary_source = source_bones[0]
                tgt_bone = tgt.pose.bones[target_bone]
                constraint = tgt_bone.constraints.new('COPY_LOCATION')
                constraint.target = src
                constraint.subtarget = primary_source
                print(f"[DEBUG] {target_bone} seguirá la posición de {primary_source} (jerarquía principal)")

        # 3. Aplicar pose
        bpy.ops.pose.armature_apply()
        bpy.ops.object.mode_set(mode='OBJECT')

        # 4. Limpiar constraints
        for bone in tgt.pose.bones:
            for c in bone.constraints:
                bone.constraints.remove(c)

        # 5. Fusión de pesos mejorada con soporte para múltiples fuentes
        for obj in bpy.data.objects:
            if obj.type != 'MESH' or obj.parent != src:
                continue
            
            bpy.context.view_layer.objects.active = obj
            
            # Procesar cada grupo de huesos que mapean al mismo destino
            for target_bone, source_bones in target_to_sources.items():
                # Crear o encontrar el vertex group del hueso destino
                target_vg = None
                for vg in obj.vertex_groups:
                    if vg.name == target_bone:
                        target_vg = vg
                        break
                
                if not target_vg:
                    target_vg = obj.vertex_groups.new(name=target_bone)
                
                # Fusionar todos los pesos de las fuentes en el destino
                for source_bone in source_bones:
                    source_vg = None
                    for vg in obj.vertex_groups:
                        if vg.name == source_bone:
                            source_vg = vg
                            break
                    
                    if source_vg:
                        print(f"[DEBUG] Fusionando pesos de {source_bone} -> {target_bone}")
                        
                        # Transferir pesos del source al target
                        for v in obj.data.vertices:
                            for g in v.groups:
                                if g.group == source_vg.index:
                                    # Añadir peso al target
                                    target_vg.add([v.index], g.weight, 'ADD')
                        
                        # Guardar el nombre antes de eliminar
                        source_vg_name = source_vg.name
                        # Eliminar el vertex group fuente
                        obj.vertex_groups.remove(source_vg)
                        print(f"[DEBUG] Eliminado vertex group: {source_vg_name}")

        # 6. Limpiar vertex groups no mapeados
        for obj in bpy.data.objects:
            if obj.type != 'MESH' or obj.parent != src:
                continue
            
            target_bone_names = [bone.name for bone in tgt.data.bones]
            groups_to_remove = []
            
            for vg in obj.vertex_groups:
                if vg.name not in target_bone_names:
                    groups_to_remove.append((vg, vg.name))
            
            for vg, vg_name in groups_to_remove:
                obj.vertex_groups.remove(vg)
                print(f"[DEBUG] Eliminado vertex group no mapeado: {vg_name}")

        # 7. Unificar todos los objetos hijos del armature fuente
        mesh_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.parent == src]
        if mesh_objs:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in mesh_objs:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = mesh_objs[0]
            bpy.ops.object.join()
            joined_obj = bpy.context.active_object
            joined_obj.name = "Mesh"
            joined_obj.parent = None

            # 8. Agregar modificador de Armature apuntando al destino
            mod = joined_obj.modifiers.new(name="Armature", type='ARMATURE')
            mod.object = tgt

        # 9. Borrar armature fuente
        bpy.data.objects.remove(src, do_unlink=True)

        # 10. Purgar objetos no visibles en la ViewLayer
        used_names = {obj.name for obj in bpy.context.view_layer.objects if obj}
        for obj in list(bpy.data.objects):
            if obj.name not in used_names:
                try:
                    bpy.data.objects.remove(obj, do_unlink=True)
                except:
                    pass

        # 11. Marcar armature destino como In Front
        tgt.show_in_front = True

        # 12. Eliminar el objeto padre del target_armature (si no es None ni self)
        if tgt.parent and tgt.parent.name != tgt.name:
            try:
                bpy.data.objects.remove(tgt.parent, do_unlink=True)
            except:
                print("[DEBUG] No se pudo eliminar el padre del target_armature.")

        # 13. Mover el hueso root del target_armature a (0, 0, 0) manteniendo sus propiedades originales
        bpy.context.view_layer.objects.active = tgt
        bpy.ops.object.mode_set(mode='EDIT')
        try:
            if len(tgt.data.edit_bones) > 0:
                root_bone = tgt.data.edit_bones[0]
                
                # Guardar las propiedades originales
                original_length = root_bone.length
                original_vector = root_bone.tail - root_bone.head
                original_roll = root_bone.roll
                
                # Calcular el offset para mover el hueso
                offset = Vector((0.0, 0.0, 0.0)) - root_bone.head
                
                # Mover el hueso manteniendo su orientación y longitud
                root_bone.head += offset
                root_bone.tail += offset
                
                # Verificar que la longitud y orientación se mantienen
                if abs(root_bone.length - original_length) > 0.0001:
                    # Si por alguna razón cambió la longitud, restaurarla
                    root_bone.tail = root_bone.head + original_vector.normalized() * original_length
                
                # Mantener el roll original
                root_bone.roll = original_roll
                
                print(f"[DEBUG] Hueso root movido a (0,0,0). Longitud: {root_bone.length:.4f}, Roll: {root_bone.roll:.4f}")
                
        except Exception as e:
            print("[DEBUG] No se pudo mover el hueso root:", e)
        bpy.ops.object.mode_set(mode='OBJECT')

        # 14. APLICAR ESPACIADO AL FINAL DE TODO
        print("[DEBUG] === LLAMANDO A APPLY_BONE_SPACING ===")
        self.apply_bone_spacing(tgt)

        print("[DEBUG] Conversión finalizada con éxito.")
        return True