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

    def apply_shape_keys(self, obj):
        """Aplica todas las shape keys con sus valores originales HORNEANDOLAS en la geometría"""
        print(f"[DEBUG] Aplicando shape keys en {obj.name}")
        
        if not obj.data.shape_keys:
            print(f"[DEBUG] {obj.name} no tiene shape keys")
            return
        
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Mostrar valores originales
        for key in obj.data.shape_keys.key_blocks:
            if key.name != "Basis":
                print(f"[DEBUG] Shape key: {key.name} valor: {key.value}")
        
        # MÉTODO SIMPLE: Usar operador mix para aplicar todas las shape keys
        original_name = obj.data.name
        
        # Crear shape key con todas las demás mezcladas
        bpy.ops.object.shape_key_add(from_mix=True)
        
        # Ahora eliminar todas las shape keys excepto la última (que tiene la mezcla)
        while len(obj.data.shape_keys.key_blocks) > 1:
            obj.active_shape_key_index = 0  # Siempre eliminar la primera
            bpy.ops.object.shape_key_remove()
        
        # Eliminar la última shape key (aplica la mezcla a la geometría base)
        if obj.data.shape_keys:
            bpy.ops.object.shape_key_remove(all=True)
        
        # Restaurar nombre
        obj.data.name = original_name
        print(f"[DEBUG] ✓ Shape keys HORNEADAS en la geometría")

    def cleanup_materials_and_textures(self, obj):
        """Limpia materiales del objeto: solo base color, preserva alpha, convierte colores RVA"""
        print(f"[DEBUG] Limpiando materiales de {obj.name}")
        
        for material in obj.data.materials:
            if not material or not material.use_nodes:
                continue
                
            print(f"[DEBUG] Procesando material: {material.name}")
            nodes = material.node_tree.nodes
            links = material.node_tree.links
            
            # Encontrar nodos importantes
            output_node = None
            bsdf_node = None
            
            for node in nodes:
                if node.type == 'OUTPUT_MATERIAL':
                    output_node = node
                elif node.type == 'BSDF_PRINCIPLED':
                    bsdf_node = node
            
            if not bsdf_node or not output_node:
                continue
            
            # PRESERVAR VALORES ORIGINALES
            original_alpha = bsdf_node.inputs['Alpha'].default_value
            original_base_color = bsdf_node.inputs['Base Color'].default_value
            
            # Verificar si tiene textura existente
            existing_texture_node = None
            if bsdf_node.inputs['Base Color'].is_linked:
                link = bsdf_node.inputs['Base Color'].links[0]
                if link.from_node.type == 'TEX_IMAGE':
                    existing_texture_node = link.from_node
                    if existing_texture_node.image:
                        self.fix_image_name(existing_texture_node.image)
            
            # LIMPIAR NODOS (mantener output, BSDF y textura existente)
            nodes_to_keep = [output_node, bsdf_node]
            if existing_texture_node:
                nodes_to_keep.append(existing_texture_node)
            
            for node in list(nodes):
                if node not in nodes_to_keep:
                    nodes.remove(node)
            
            # CREAR IMAGEN PARA COLOR SÓLIDO SI NO HAY TEXTURA
            if not existing_texture_node and original_base_color != (0.8, 0.8, 0.8, 1.0):
                print(f"[DEBUG] Creando imagen para color RVA: {original_base_color}")
                img_node = self.create_color_image(material, original_base_color)
                if img_node:
                    # CONECTAR INMEDIATAMENTE
                    links.new(img_node.outputs['Color'], bsdf_node.inputs['Base Color'])
                    print(f"[DEBUG] ✓ Color RVA conectado en {material.name}")
            
            # CONFIGURAR VALORES DEL BSDF
            if 'Specular IOR' in bsdf_node.inputs:
                bsdf_node.inputs['Specular IOR'].default_value = 1.0
            elif 'Specular' in bsdf_node.inputs:
                bsdf_node.inputs['Specular'].default_value = 0.0
            
            if 'Metallic' in bsdf_node.inputs:
                bsdf_node.inputs['Metallic'].default_value = 0.0
            
            if 'IOR' in bsdf_node.inputs:
                bsdf_node.inputs['IOR'].default_value = 1.5
            
            # RESTAURAR ALPHA ORIGINAL
            bsdf_node.inputs['Alpha'].default_value = original_alpha
            
            # CONECTAR OUTPUT AL BSDF SI NO ESTÁ CONECTADO
            if not output_node.inputs['Surface'].is_linked:
                links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
            
            print(f"[DEBUG] ✓ Material {material.name} procesado (alpha: {original_alpha:.3f})")

    def create_color_image(self, material, color):
        """Crea imagen 64x64 con color sólido y devuelve nodo de imagen"""
        img_name = f"{material.name}_d.png"
        
        # Eliminar imagen existente si hay conflicto
        existing_img = bpy.data.images.get(img_name)
        if existing_img:
            bpy.data.images.remove(existing_img)
        
        # Crear nueva imagen 64x64
        img = bpy.data.images.new(img_name, width=64, height=64)
        
        # Crear array de píxeles
        pixels = [color[0], color[1], color[2], color[3]] * (64 * 64)
        
        # Asignar píxeles
        img.pixels[:] = pixels
        img.update()
        
        # Empacar en archivo blend
        img.pack()
        
        # Crear y configurar nodo de imagen
        img_node = material.node_tree.nodes.new('ShaderNodeTexImage')
        img_node.image = img
        img_node.location = (-400, 200)
        img_node.label = "Color RVA"
        
        print(f"[DEBUG] ✓ Imagen creada: {img_name} con color RGBA({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f}, {color[3]:.2f})")
        return img_node

    def fix_image_name(self, image):
        """Corrige nombres de imágenes eliminando .001, rutas, etc."""
        if not image:
            return
            
        original_name = image.name
        
        # Quitar .001, .002, etc.
        import re
        new_name = re.sub(r'\.\d{3}$', '', original_name)
        
        # Quitar rutas como "txd/male07/"
        if '/' in new_name:
            new_name = new_name.split('/')[-1]
        
        # Asegurar extensión .png
        if not new_name.endswith('.png'):
            new_name += '.png'
        
        if new_name != original_name:
            image.name = new_name
            print(f"[DEBUG] Imagen renombrada: {original_name} -> {new_name}")

    def cleanup_unnamed_objects(self):
        """Elimina objetos 'unnamed' con cualquier sufijo"""
        print("[DEBUG] Eliminando objetos 'unnamed'")
        
        objects_to_remove = []
        for obj in bpy.data.objects:
            if obj.name.startswith('unnamed'):
                objects_to_remove.append(obj)
        
        for obj in objects_to_remove:
            print(f"[DEBUG] Eliminando objeto: {obj.name}")
            bpy.data.objects.remove(obj, do_unlink=True)

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
        
        # Hacer visibles todos los objetos hijos del armature fuente Y asegurar que estén en ViewLayer
        for obj in bpy.data.objects:
            if obj.parent == src:
                obj.hide_set(False)
                obj.hide_viewport = False
                if hasattr(obj, 'hide_select'):
                    obj.hide_select = False
                
                # Asegurar que esté en la ViewLayer
                if obj.name not in bpy.context.view_layer.objects:
                    try:
                        bpy.context.collection.objects.link(obj)
                        print(f"[DEBUG] Re-enlazado a ViewLayer: {obj.name}")
                    except:
                        print(f"[DEBUG] No se pudo re-enlazar: {obj.name}")
                        
                print(f"[DEBUG] Hecho visible: {obj.name}")
        
        # === PASO 0: VERIFICAR Y RENOMBRAR MESH EXISTENTE ===
        print("[DEBUG] === PASO 0: VERIFICAR MESH EXISTENTE ===")
        existing_mesh = None
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.name == "Mesh" and obj.parent != src:
                existing_mesh = obj
                break
        
        if existing_mesh:
            existing_mesh.name = "Base"
            existing_mesh.data.name = "Base"
            print(f"[DEBUG] Mesh existente renombrado a: {existing_mesh.name}")

        # === PASO 1: UNIFICAR MALLAS ===
        print("[DEBUG] === PASO 1: UNIFICAR MALLAS ===")
        mesh_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.parent == src]

        if not mesh_objs:
            print("[ERROR] No se encontraron objetos mesh hijos del armature fuente")
            return False

        # Filtrar solo objetos que estén en ViewLayer
        valid_mesh_objs = []
        for obj in mesh_objs:
            if obj.name in bpy.context.view_layer.objects:
                valid_mesh_objs.append(obj)
            else:
                print(f"[DEBUG] Objeto {obj.name} no está en ViewLayer, omitiendo")

        if not valid_mesh_objs:
            print("[ERROR] No hay objetos mesh válidos en ViewLayer")
            return False

        # Unificar objetos mesh
        bpy.ops.object.select_all(action='DESELECT')
        for obj in valid_mesh_objs:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = valid_mesh_objs[0]
        bpy.ops.object.join()
        unified_mesh = bpy.context.active_object
        
        # ASEGURAR NOMBRE CORRECTO DESDE EL INICIO
        unified_mesh.name = "Mesh"
        unified_mesh.data.name = "Mesh"
        
        # Si existe otro "Mesh", unirlo también
        other_mesh = None
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj != unified_mesh and obj.name.startswith("Mesh"):
                other_mesh = obj
                break
        
        if other_mesh:
            bpy.ops.object.select_all(action='DESELECT')
            unified_mesh.select_set(True)
            other_mesh.select_set(True)
            bpy.context.view_layer.objects.active = unified_mesh
            bpy.ops.object.join()
            unified_mesh = bpy.context.active_object
            unified_mesh.name = "Mesh"
            unified_mesh.data.name = "Mesh"
        
        unified_mesh.parent = src  # Mantener parent temporalmente

        print(f"[DEBUG] Mallas unificadas en: {unified_mesh.name}")

        # === PASO 2: PROCESAR ATRIBUTOS DE COLOR ===
        print("[DEBUG] === PASO 2: PROCESAR ATRIBUTOS DE COLOR ===")

        if not self.settings.keep_vertex_colors:
            # Eliminar vertex colors tradicionales
            while unified_mesh.data.vertex_colors:
                unified_mesh.data.vertex_colors.remove(unified_mesh.data.vertex_colors[0])
            
            # Color attributes (Blender 3.2+)
            if hasattr(unified_mesh.data, 'color_attributes'):
                while unified_mesh.data.color_attributes:
                    unified_mesh.data.color_attributes.remove(unified_mesh.data.color_attributes[0])
            
            print("[DEBUG] Atributos de color eliminados")
        else:
            print("[DEBUG] Vertex colors mantenidos")
        
        # Cambiar UV map activo a Float2
        if unified_mesh.data.uv_layers:
            unified_mesh.data.uv_layers.active.name = "Float2"
            print("[DEBUG] UV map activo renombrado a Float2")

        # === PASO 3: APLICAR SHAPE KEYS ===
        print("[DEBUG] === PASO 3: APLICAR SHAPE KEYS ===")
        self.apply_shape_keys(unified_mesh)

        # === PASO 4: APLICAR POSE EN LA MALLA ===
        print("[DEBUG] === PASO 4: APLICAR POSE EN LA MALLA ===")
        
        # Aplicar modificador armature existente para hornear la pose
        for mod in list(unified_mesh.modifiers):
            if mod.type == 'ARMATURE' and mod.object == src:
                print(f"[DEBUG] Aplicando modificador armature: {mod.name}")
                bpy.context.view_layer.objects.active = unified_mesh
                bpy.ops.object.modifier_apply(modifier=mod.name)
                print("[DEBUG] ✓ Pose aplicada en la malla")
                break

        # === PASO 5: CONFIGURAR MODIFICADOR DESPUÉS DE APLICAR POSE ===
        print("[DEBUG] === PASO 5: CONFIGURAR MODIFICADOR ===")
        # Limpiar todos los modificadores restantes
        for mod in list(unified_mesh.modifiers):
            unified_mesh.modifiers.remove(mod)
        
        # Agregar solo el modificador GTASA_SKIN
        mod = unified_mesh.modifiers.new(name="GTASA_SKIN", type='ARMATURE')
        mod.object = tgt
        print(f"[DEBUG] Modificador GTASA_SKIN configurado")

        # === PASO 6: APLICAR TRANSFORMACIONES ===
        print("[DEBUG] === PASO 6: APLICAR TRANSFORMACIONES ===")
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # Aplicar transformaciones al source_armature
        if src.name in bpy.context.view_layer.objects:
            src.select_set(True)
            bpy.context.view_layer.objects.active = src
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        else:
            print(f"[ERROR] Source armature {src.name} no está en ViewLayer")
            return False

        # Aplicar transformaciones a la malla unificada
        unified_mesh.select_set(True)
        bpy.context.view_layer.objects.active = unified_mesh
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        bpy.context.view_layer.objects.active = tgt
        bpy.ops.object.mode_set(mode='POSE')
        
        # --- APLICAR POSE PERSONALIZADA INMEDIATAMENTE ---
        if self.settings.auto_apply_custom_pose:
            try:
                print("[DEBUG] Aplicando pose personalizada...")
                applier = external_pose_caller.ExternalPoseApplier()
                pose_success = applier.execute_full_pose_application(
                    source_armature=src,
                    target_armature=tgt
                )
                if pose_success:
                    print("[DEBUG] ✓ Pose personalizada aplicada")
                else:
                    print("[DEBUG] ✗ Falló pose personalizada")
            except Exception as e:
                print(f"[DEBUG] Error en pose personalizada: {e}")
        
        # --- Aplicar y hornear la pose manual antes del COPY_LOCATION ---
        try:
            external_pose_caller.apply_manual_pose_to_children_and_reassign(self.settings.target_armature)
            print("[DEBUG] Pose manual aplicada y horneada")
        except Exception as e:
            print(f"[DEBUG] Error al hornear pose manual: {e}")

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

        # 5. Fusión de pesos mejorada - SOLO EN UNIFIED_MESH
        bpy.context.view_layer.objects.active = unified_mesh
        
        # Procesar cada grupo de huesos que mapean al mismo destino
        for target_bone, source_bones in target_to_sources.items():
            # Crear o encontrar el vertex group del hueso destino
            target_vg = None
            for vg in unified_mesh.vertex_groups:
                if vg.name == target_bone:
                    target_vg = vg
                    break
            
            if not target_vg:
                target_vg = unified_mesh.vertex_groups.new(name=target_bone)
            
            # Fusionar todos los pesos de las fuentes en el destino
            for source_bone in source_bones:
                source_vg = None
                for vg in unified_mesh.vertex_groups:
                    if vg.name == source_bone:
                        source_vg = vg
                        break
                
                if source_vg:
                    print(f"[DEBUG] Fusionando pesos de {source_bone} -> {target_bone}")
                    
                    # Transferir pesos del source al target
                    for v in unified_mesh.data.vertices:
                        for g in v.groups:
                            if g.group == source_vg.index:
                                # Añadir peso al target
                                target_vg.add([v.index], g.weight, 'ADD')
                    
                    # Guardar el nombre antes de eliminar
                    source_vg_name = source_vg.name
                    # Eliminar el vertex group fuente
                    unified_mesh.vertex_groups.remove(source_vg)
                    print(f"[DEBUG] Eliminado vertex group: {source_vg_name}")

        # 6. Limpiar vertex groups no mapeados de unified_mesh
        target_bone_names = [bone.name for bone in tgt.data.bones]
        groups_to_remove = []
        
        for vg in unified_mesh.vertex_groups:
            if vg.name not in target_bone_names:
                groups_to_remove.append((vg, vg.name))
        
        for vg, vg_name in groups_to_remove:
            unified_mesh.vertex_groups.remove(vg)
            print(f"[DEBUG] Eliminado vertex group no mapeado: {vg_name}")

        # 7. Configurar jerarquía: Mesh como padre de Root
        unified_mesh.parent = None
        tgt.parent = unified_mesh  # Root es hijo de Mesh
        
        # Asegurar nombres correctos finales
        unified_mesh.name = "Mesh"
        unified_mesh.data.name = "Mesh"
        print(f"[DEBUG] Jerarquía configurada: {tgt.name} es hijo de {unified_mesh.name}")
        print(f"[DEBUG] Nombres finales: objeto={unified_mesh.name}, datos={unified_mesh.data.name}")

        # 9. Asegurar que unified_mesh esté en ViewLayer antes de borrar src
        if unified_mesh.name not in bpy.context.view_layer.objects:
            try:
                bpy.context.collection.objects.link(unified_mesh)
                print(f"[DEBUG] unified_mesh re-enlazado a ViewLayer")
            except:
                print(f"[DEBUG] unified_mesh ya está en ViewLayer")
        
        # Hacer visible y seleccionable
        unified_mesh.hide_set(False)
        unified_mesh.hide_viewport = False
        if hasattr(unified_mesh, 'hide_select'):
            unified_mesh.hide_select = False
        
        # Borrar armature fuente
        bpy.data.objects.remove(src, do_unlink=True)
        print(f"[DEBUG] Source armature eliminado, unified_mesh protegido")

        # 10. Purgar objetos no visibles en la ViewLayer (PROTEGIENDO unified_mesh)
        used_names = {obj.name for obj in bpy.context.view_layer.objects if obj}
        # Asegurar que unified_mesh y target armature estén protegidos
        protected_objects = {unified_mesh.name, tgt.name}
        
        for obj in list(bpy.data.objects):
            if obj.name not in used_names and obj.name not in protected_objects:
                try:
                    print(f"[DEBUG] Purgando objeto no usado: {obj.name}")
                    bpy.data.objects.remove(obj, do_unlink=True)
                except:
                    pass

        # 11. Marcar armature destino como In Front
        tgt.show_in_front = True

        # 12. NO eliminar el padre si es el mismo unified_mesh
        if tgt.parent and tgt.parent != unified_mesh:
            parent_to_delete = tgt.parent
            print(f"[DEBUG] Eliminando padre de {tgt.name}: {parent_to_delete.name}")
            tgt.parent = None  # Desenlazar primero
            try:
                bpy.data.objects.remove(parent_to_delete, do_unlink=True)
                print(f"[DEBUG] ✓ Padre {parent_to_delete.name} eliminado exitosamente")
            except Exception as e:
                print(f"[DEBUG] ✗ Error eliminando padre: {e}")
        else:
            print(f"[DEBUG] Padre de {tgt.name} es {unified_mesh.name}, no se elimina")

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

        # === LIMPIEZA FINAL ===
        print("[DEBUG] === LIMPIEZA FINAL ===")
        
        # Limpiar materiales y texturas
        self.cleanup_materials_and_textures(unified_mesh)
        
        # Eliminar objetos 'unnamed'
        self.cleanup_unnamed_objects()
        
        print("[DEBUG] Conversión finalizada con éxito.")
        return True