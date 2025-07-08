# converter.py - FLUJO COMPLETO CORREGIDO según especificaciones
import bpy
import bmesh
from mathutils import Vector
from .utils.cleanup import CleanupUtils


class UniversalGTAConverter:
    """Conversor principal siguiendo el flujo EXACTO especificado para GTA SA"""
    
    def __init__(self, settings):
        self.settings = settings
        self.source_armature = None
        self.target_armature = None
        self.unified_mesh = None

    def convert(self) -> bool:
        """Función principal de conversión siguiendo el flujo EXACTO"""
        
        # Validar configuración inicial
        if not self._validate_conversion_setup():
            return False
        
        print("[CONVERTER] === INICIANDO CONVERSIÓN GTA SA - FLUJO COMPLETO ===")
        
        self.source_armature = self.settings.source_armature
        self.target_armature = self.settings.target_armature
        
        try:
            # FASE 1: Preparación - Source (Armature)
            print("[CONVERTER] FASE 1: Preparación Source")
            self._phase_1_prepare_source()
            
            # FASE 2: Limpieza de la Malla
            print("[CONVERTER] FASE 2: Limpieza de Malla")
            self._phase_2_cleanup_mesh()
            
            # FASE 3: Optimización de materiales
            print("[CONVERTER] FASE 3: Optimización de Materiales")
            self._phase_3_optimize_materials()
            
            # FASE 4: Procesar Shape Keys
            print("[CONVERTER] FASE 4: Procesar Shape Keys")
            self._phase_4_process_shape_keys()
            
            # FASE 5: Aplicar y borrar modificador Armature
            print("[CONVERTER] FASE 5: Aplicar Modificador Armature")
            self._phase_5_apply_armature_modifier()
            
            # FASE 6: Reasignación al Target (Root)
            print("[CONVERTER] FASE 6: Reasignación a Target")
            self._phase_6_reassign_to_target()
            
            # FASE 7: Limpieza de objetos antiguos
            print("[CONVERTER] FASE 7: Limpieza Final")
            self._phase_7_cleanup_old_objects()
            
            # FASE 8: Reconfiguración final
            print("[CONVERTER] FASE 8: Configuración Final")
            self._phase_8_final_setup()
            
            print("[CONVERTER] === CONVERSIÓN COMPLETADA EXITOSAMENTE ===")
            return True
            
        except Exception as e:
            print(f"[CONVERTER] ERROR durante la conversión: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _validate_conversion_setup(self) -> bool:
        """Valida que la configuración sea correcta"""
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
        
        # Verificar mapeos
        enabled_mappings = [m for m in self.settings.bone_mappings if m.enabled]
        if len(enabled_mappings) == 0:
            print("[ERROR] No hay mapeos de huesos habilitados.")
            return False
        
        return True

    def _phase_1_prepare_source(self):
        """FASE 1: Aplicar transformaciones al Source y sus hijos"""
        print("[PHASE 1] Aplicando transformaciones al Source Armature y sus hijos...")
        
        # Asegurar modo objeto
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # 1. Aplicar transformaciones al Source Armature
        bpy.context.view_layer.objects.active = self.source_armature
        bpy.ops.object.select_all(action='DESELECT')
        self.source_armature.select_set(True)
        
        print(f"[PHASE 1] Aplicando transformaciones a {self.source_armature.name}")
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        # 2. Aplicar transformaciones a todos los hijos del Source
        source_children = [obj for obj in bpy.data.objects if obj.parent == self.source_armature]
        
        for child in source_children:
            print(f"[PHASE 1] Aplicando transformaciones a hijo: {child.name}")
            bpy.ops.object.select_all(action='DESELECT')
            child.select_set(True)
            bpy.context.view_layer.objects.active = child
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        print(f"[PHASE 1] ✓ Transformaciones aplicadas a {len(source_children)} objetos hijos")

    def _phase_2_cleanup_mesh(self):
        """FASE 2: Configurar materiales y unir mallas"""
        print("[PHASE 2] Limpiando materiales y uniendo mallas...")
        
        # 1. Configurar materiales (metallic = 0, specular = 0)
        material_count = 0
        for material in bpy.data.materials:
            if material.use_nodes:
                # Buscar nodo Principled BSDF
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        # Establecer metallic y specular a 0
                        if 'Metallic' in node.inputs:
                            node.inputs['Metallic'].default_value = 0.0
                        if 'Specular' in node.inputs:
                            node.inputs['Specular'].default_value = 0.0
                        material_count += 1
                        print(f"[PHASE 2] Material configurado: {material.name}")
        
        print(f"[PHASE 2] ✓ {material_count} materiales configurados")
        
        # 2. Encontrar todas las mallas hijas del Source
        mesh_children = [obj for obj in bpy.data.objects 
                        if obj.type == 'MESH' and obj.parent == self.source_armature]
        
        if not mesh_children:
            raise Exception("No se encontraron mallas hijas del Source Armature")
        
        print(f"[PHASE 2] Encontradas {len(mesh_children)} mallas para unir")
        
        # 3. Unir todas las mallas
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        
        # Seleccionar todas las mallas
        for mesh_obj in mesh_children:
            mesh_obj.select_set(True)
            print(f"[PHASE 2] Seleccionada para unir: {mesh_obj.name}")
        
        # Activar la primera malla como principal
        bpy.context.view_layer.objects.active = mesh_children[0]
        
        # Unir objetos
        bpy.ops.object.join()
        
        # Renombrar el objeto unificado
        self.unified_mesh = bpy.context.active_object
        self.unified_mesh.name = "Mesh"
        self.unified_mesh.data.name = "Mesh"
        
        print(f"[PHASE 2] ✓ Mallas unificadas en: {self.unified_mesh.name}")

    def _phase_3_optimize_materials(self):
        """FASE 3: Optimizar materiales y texturas"""
        print("[PHASE 3] Optimizando materiales y texturas...")
        
        # 1. Eliminar sufijos .001, .002 de texturas
        texture_count = 0
        for image in bpy.data.images:
            original_name = image.name
            # Remover sufijos como .001, .002, etc.
            import re
            clean_name = re.sub(r'\.\d+$', '', original_name)
            if clean_name != original_name:
                image.name = clean_name
                texture_count += 1
                print(f"[PHASE 3] Textura renombrada: {original_name} -> {clean_name}")
        
        print(f"[PHASE 3] ✓ {texture_count} texturas renombradas")
        
        # 2. Unificar materiales que compartan la misma textura
        materials_by_texture = {}
        
        # Agrupar materiales por textura principal
        for material in bpy.data.materials:
            if material.use_nodes:
                main_texture = None
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        main_texture = node.image.name
                        break
                
                if main_texture:
                    if main_texture not in materials_by_texture:
                        materials_by_texture[main_texture] = []
                    materials_by_texture[main_texture].append(material)
        
        # Unificar materiales duplicados
        unified_count = 0
        for texture_name, materials in materials_by_texture.items():
            if len(materials) > 1:
                # Mantener el primer material, reemplazar referencias de los demás
                primary_material = materials[0]
                
                for duplicate_material in materials[1:]:
                    # Reemplazar en el mesh unificado
                    if self.unified_mesh and self.unified_mesh.data.materials:
                        for i, slot_material in enumerate(self.unified_mesh.data.materials):
                            if slot_material == duplicate_material:
                                self.unified_mesh.data.materials[i] = primary_material
                    
                    # Eliminar material duplicado
                    bpy.data.materials.remove(duplicate_material)
                    unified_count += 1
                    print(f"[PHASE 3] Material unificado: {duplicate_material.name} -> {primary_material.name}")
        
        print(f"[PHASE 3] ✓ {unified_count} materiales unificados")

    def _phase_4_process_shape_keys(self):
        """FASE 4: Aplicar y eliminar todas las Shape Keys"""
        print("[PHASE 4] Procesando Shape Keys...")
        
        if not self.unified_mesh or not self.unified_mesh.data.shape_keys:
            print("[PHASE 4] No hay Shape Keys para procesar")
            return
        
        # Activar el mesh unificado
        bpy.context.view_layer.objects.active = self.unified_mesh
        bpy.ops.object.mode_set(mode='OBJECT')
        
        key_blocks = self.unified_mesh.data.shape_keys.key_blocks
        initial_count = len(key_blocks)
        
        print(f"[PHASE 4] Encontradas {initial_count} Shape Keys")
        
        # Aplicar todas las shape keys desde la última hacia la primera
        applied_count = 0
        for i in range(len(key_blocks) - 1, -1, -1):
            try:
                if not self.unified_mesh.data.shape_keys or i >= len(self.unified_mesh.data.shape_keys.key_blocks):
                    continue
                
                current_key = self.unified_mesh.data.shape_keys.key_blocks[i]
                key_name = current_key.name
                
                print(f"[PHASE 4] Aplicando Shape Key: {key_name}")
                
                # Establecer como activa y aplicar
                self.unified_mesh.active_shape_key_index = i
                
                # Aplicar shape key
                bpy.ops.object.shape_key_remove(all=False)
                applied_count += 1
                
            except Exception as e:
                print(f"[PHASE 4] Error aplicando Shape Key {i}: {e}")
        
        print(f"[PHASE 4] ✓ {applied_count} Shape Keys aplicadas y eliminadas")

    def _phase_5_apply_armature_modifier(self):
        """FASE 5: Aplicar modificador Armature del Source y aplicar pose"""
        print("[PHASE 5] Aplicando modificador Armature y pose...")
        
        if not self.unified_mesh:
            raise Exception("No hay mesh unificado para procesar")
        
        # Activar el mesh unificado
        bpy.context.view_layer.objects.active = self.unified_mesh
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # 1. Encontrar y aplicar modificador Armature del Source
        armature_modifier = None
        for modifier in self.unified_mesh.modifiers:
            if modifier.type == 'ARMATURE' and modifier.object == self.source_armature:
                armature_modifier = modifier
                break
        
        if armature_modifier:
            modifier_name = armature_modifier.name
            print(f"[PHASE 5] Aplicando modificador Armature: {modifier_name}")
            
            # Aplicar el modificador
            bpy.ops.object.modifier_apply(modifier=modifier_name)
            print(f"[PHASE 5] ✓ Modificador {modifier_name} aplicado")
        else:
            print("[PHASE 5] ⚠ No se encontró modificador Armature del Source")
        
        # 2. Aplicar pose del Source Armature
        print("[PHASE 5] Aplicando pose del Source Armature...")
        
        bpy.context.view_layer.objects.active = self.source_armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Aplicar pose como rest pose
        bpy.ops.pose.armature_apply()
        print("[PHASE 5] ✓ Pose del Source aplicada como rest pose")
        
        bpy.ops.object.mode_set(mode='OBJECT')

    def _phase_6_reassign_to_target(self):
        """FASE 6: Crear constraints y aplicar pose al Target"""
        print("[PHASE 6] Reasignando al Target Armature...")
        
        # 1. Cambiar al Target en modo pose
        bpy.context.view_layer.objects.active = self.target_armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # 2. Obtener mapeos habilitados
        enabled_mappings = [(m.source_bone, m.target_bone) 
                           for m in self.settings.bone_mappings 
                           if m.enabled and m.source_bone and m.target_bone]
        
        print(f"[PHASE 6] Aplicando {len(enabled_mappings)} mapeos de huesos")
        
        # 3. Crear constraints COPY_LOCATION
        constraint_count = 0
        for source_bone, target_bone in enabled_mappings:
            if (source_bone in self.source_armature.pose.bones and 
                target_bone in self.target_armature.pose.bones):
                
                target_pose_bone = self.target_armature.pose.bones[target_bone]
                
                # Crear constraint
                constraint = target_pose_bone.constraints.new('COPY_LOCATION')
                constraint.target = self.source_armature
                constraint.subtarget = source_bone
                constraint.name = f"GTA_COPY_{source_bone}"
                
                constraint_count += 1
                print(f"[PHASE 6] Constraint creado: {target_bone} <- {source_bone}")
        
        print(f"[PHASE 6] ✓ {constraint_count} constraints creados")
        
        # 4. Aplicar pose del Target
        print("[PHASE 6] Aplicando pose del Target...")
        bpy.ops.pose.armature_apply()
        print("[PHASE 6] ✓ Pose del Target aplicada")
        
        # 5. Limpiar constraints
        print("[PHASE 6] Limpiando constraints...")
        constraint_count = 0
        for bone in self.target_armature.pose.bones:
            constraints_to_remove = list(bone.constraints)
            for constraint in constraints_to_remove:
                bone.constraints.remove(constraint)
                constraint_count += 1
        
        print(f"[PHASE 6] ✓ {constraint_count} constraints eliminados")
        
        bpy.ops.object.mode_set(mode='OBJECT')

    def _phase_7_cleanup_old_objects(self):
        """FASE 7: Eliminar objetos antiguos innecesarios"""
        print("[PHASE 7] Limpiando objetos antiguos...")
        
        # 1. Eliminar mallas asociadas al Target ("unnamed", etc.)
        target_children = [obj for obj in bpy.data.objects if obj.parent == self.target_armature]
        removed_meshes = 0
        
        for child in target_children:
            if child.type == 'MESH' and child != self.unified_mesh:
                child_name = child.name
                
                # Verificar si es una malla "unnamed" típica
                if any(keyword in child_name.lower() for keyword in ['unnamed', 'default', 'cube', 'plane']):
                    print(f"[PHASE 7] Eliminando malla antigua: {child_name}")
                    bpy.data.objects.remove(child, do_unlink=True)
                    removed_meshes += 1
        
        print(f"[PHASE 7] ✓ {removed_meshes} mallas antiguas eliminadas")
        
        # 2. Eliminar el Source Armature
        if self.source_armature and self.source_armature.name in bpy.data.objects:
            source_name = self.source_armature.name
            print(f"[PHASE 7] Eliminando Source Armature: {source_name}")
            
            # Asegurar que no esté activo
            if bpy.context.active_object == self.source_armature:
                bpy.context.view_layer.objects.active = self.target_armature
            
            # Eliminar
            bpy.data.objects.remove(self.source_armature, do_unlink=True)
            print(f"[PHASE 7] ✓ Source Armature {source_name} eliminado")
        
        # 3. Purgar datos huérfanos
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        print("[PHASE 7] ✓ Datos huérfanos purgados")

    def _phase_8_final_setup(self):
        """FASE 8: Configuración final del resultado"""
        print("[PHASE 8] Configuración final...")
        
        if not self.unified_mesh:
            raise Exception("No hay mesh unificado para la configuración final")
        
        # 1. Configurar jerarquía: Mesh como hijo del Target
        print("[PHASE 8] Configurando jerarquía...")
        self.unified_mesh.parent = self.target_armature
        self.unified_mesh.parent_type = 'ARMATURE'
        print(f"[PHASE 8] ✓ {self.unified_mesh.name} configurado como hijo de {self.target_armature.name}")
        
        # 2. Limpiar modificadores existentes del mesh
        existing_modifiers = list(self.unified_mesh.modifiers)
        for modifier in existing_modifiers:
            self.unified_mesh.modifiers.remove(modifier)
            print(f"[PHASE 8] Modificador eliminado: {modifier.name}")
        
        # 3. Agregar nuevo modificador Armature llamado "GTA_SKIN"
        gta_modifier = self.unified_mesh.modifiers.new(name="GTA_SKIN", type='ARMATURE')
        gta_modifier.object = self.target_armature
        print(f"[PHASE 8] ✓ Modificador 'GTA_SKIN' creado apuntando a {self.target_armature.name}")
        
        # 4. Configurar nombres finales
        self.target_armature.name = "Root"
        self.target_armature.data.name = "Root"
        
        # Aplicar nombres personalizados si están configurados
        if self.settings.skin_name and self.settings.skin_name != "MySkin":
            self.unified_mesh.name = self.settings.skin_name
            self.unified_mesh.data.name = self.settings.skin_name
        
        if self.settings.author_nickname and self.settings.author_nickname != "Author":
            # Renombrar el primer hueso si existe
            if len(self.target_armature.data.bones) > 0:
                bpy.context.view_layer.objects.active = self.target_armature
                bpy.ops.object.mode_set(mode='EDIT')
                first_bone = self.target_armature.data.edit_bones[0]
                first_bone.name = f"{self.settings.author_nickname}_Root"
                bpy.ops.object.mode_set(mode='OBJECT')
        
        # 5. Configurar visibilidad y propiedades finales
        self.target_armature.show_in_front = True
        self.unified_mesh.show_wire = False
        
        print("[PHASE 8] ✓ Configuración final completada")
        
        # 6. Resumen final
        print("\n" + "="*60)
        print("CONVERSIÓN COMPLETADA - RESUMEN FINAL:")
        print("="*60)
        print(f"✓ Armature Final: {self.target_armature.name}")
        print(f"✓ Mesh Final: {self.unified_mesh.name}")
        print(f"✓ Modificador: GTA_SKIN -> {self.target_armature.name}")
        print(f"✓ Materiales: {len(self.unified_mesh.data.materials)}")
        print(f"✓ Vértices: {len(self.unified_mesh.data.vertices)}")
        print(f"✓ Huesos: {len(self.target_armature.data.bones)}")
        print("="*60)
        
        # Aplicar corrección automática de normales si está habilitado
        if self.settings.auto_fix_normals:
            self._fix_normals_final()

    def _fix_normals_final(self):
        """Aplica corrección de normales al resultado final"""
        print("[PHASE 8] Aplicando corrección de normales...")
        
        try:
            bpy.context.view_layer.objects.active = self.unified_mesh
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')
            print("[PHASE 8] ✓ Normales corregidas")
        except Exception as e:
            print(f"[PHASE 8] ⚠ Error corrigiendo normales: {e}")
            bpy.ops.object.mode_set(mode='OBJECT')

    def get_final_objects(self):
        """Retorna los objetos finales de la conversión"""
        return {
            'armature': self.target_armature,
            'mesh': self.unified_mesh
        }