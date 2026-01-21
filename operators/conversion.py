import bpy
from bpy.types import Operator
import re
from typing import List

class UNIVERSALGTA_OT_execute_conversion(Operator):
    """Convertidor GTA SA Definitivo"""
    bl_idname = "universalgta.execute_conversion"
    bl_label = "Convert to GTA SA (Ultimate)"
    bl_description = "Conversión definitiva a GTA SA"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Conversión a GTA SA"""
        
        # Limpiar datos huérfanos antes de comenzar
        print("🧹 Limpiando datos huérfanos antes de la conversión...")
        try:
            # Realizar múltiples pasadas para asegurar una limpieza completa
            for _ in range(3):  # 3 pasadas para estar seguros
                bpy.ops.outliner.orphans_purge(do_recursive=True)
        except Exception as e:
            print(f"⚠️ Advertencia al limpiar datos huérfanos: {e}")
        
        # Aplicar todas las transformaciones a todos los objetos
        print("🔧 Aplicando transformaciones a todos los objetos...")
        try:
            # Deseleccionar todo primero
            bpy.ops.object.select_all(action='DESELECT')
            
            # Seleccionar todos los objetos
            for obj in bpy.data.objects:
                obj.select_set(True)
            
            # Hacer activo el último objeto seleccionado
            if len(bpy.data.objects) > 0:
                context.view_layer.objects.active = bpy.data.objects[-1]
            
            # Aplicar rotación y escala
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            
            # Deseleccionar todo de nuevo
            bpy.ops.object.select_all(action='DESELECT')
            
            print("✅ Transformaciones aplicadas exitosamente")
        except Exception as e:
            print(f"⚠️ Error al aplicar transformaciones: {e}")
            
        # Limpiar o preservar vertex colors según configuración
        try:
            from ..utils.vertex_colors import clean_vertex_colors_for_source
            changed, msg = clean_vertex_colors_for_source(getattr(context.scene, 'universal_gta_settings', None))
            if changed:
                print(f"✅ Vertex colors limpiados: {msg}")
            else:
                print(f"ℹ️ Vertex colors: {msg}")
        except Exception as e:
            print(f"⚠️ No se pudo ejecutar limpieza de vertex colors: {e}")

        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature or not settings.target_armature:
            self.report({'ERROR'}, "Selecciona source y target armature")
            return {'CANCELLED'}
            
        # --- MMD CLEANUP START ---
        # Limpiar jerarquía MMD antes de validar o procesar nada
        # (Desbloquear transforms, quitar Empty padre, borrar rigidbodies/joints)
        self.source_armature = settings.source_armature
        self.clean_mmd_hierarchy()
        # --- MMD CLEANUP END ---
        
        try:
            print("=" * 70)
            print("🚀 INICIANDO CONVERSIÓN GTA SA DEFINITIVA (FLUJO PROBADO)")
            print("=" * 70)
            
            # Inicializar datos del convertidor
            self.source_armature = settings.source_armature
            self.target_armature = settings.target_armature
            self.merged_mesh = None
            self.original_pose_data = {}
            
            if not self.validate_scene():
                self.report({'ERROR'}, "Validación de escena falló")
                return {'CANCELLED'}
            
            print("🔧 PASO 2: Aplicando transformaciones...")
            self.apply_all_transforms_ultimate()
            
            print("🧹 PASO 3: Limpiando texturas...")
            self.cleanup_texture_names()

            print("🎨 PASO 3.5: Rasterización PRE-conversión...")
            try:
                from ..operators.texture_export import execute_pre_conversion_rasterization
                rasterized_count, total_materials = execute_pre_conversion_rasterization()
                print(f"✅ Rasterización completada: {rasterized_count}/{total_materials} materiales")
            except ImportError as ie:
                print(f"⚠️ Módulo texture_export no disponible: {ie}")
            except Exception as e:
                print(f"⚠️ Error en rasterización pre-conversión: {e}")
                # No fallar la conversión por errores de rasterización

            if bool(getattr(settings, 'rasterize_textures', False)):
                print("🧩 PASO 3.6: Rasterizando colores sólidos a texturas 256x256...")
                try:
                    created_images = self.rasterize_solid_base_color_to_texture(size=256)
                    print(f"✅ Colores sólidos rasterizados: {created_images} imágenes creadas")
                except Exception as e:
                    print(f"⚠️ Error rasterizando colores sólidos: {e}")
            else:
                print("⏭️ Paso 3.6 omitido (Rasterizar texturas desactivado)")

            
            if bool(getattr(settings, 'clean_materials', True)):
                print("🎨 PASO 4: Optimizando materiales...")
                self.optimize_materials_ultimate()
            else:
                print("⏭️ Paso 4 omitido (Limpiar materiales desactivado)")
            

            if bool(getattr(settings, 'clean_materials', True)):
                print("🔥 PASO 4.5: Aplicando Smart Baking inteligente...")
                try:
                    result = bpy.ops.universalgta.manual_smart_baking()
                    if result == {'FINISHED'}:
                        print("✅ Smart Baking aplicado exitosamente")
                    elif result == {'CANCELLED'}:
                        print("⚠️ Smart Baking cancelado - continuando conversión")
                    else:
                        print("⚠️ Smart Baking completado con advertencias")
                except Exception as e:
                    print(f"❌ Error en Smart Baking: {e}")
                    print("⚠️ Continuando conversión sin Smart Baking")
                    # No fallar la conversión por errores de baking
            else:
                print("⏭️ Paso 4.5 omitido (Limpiar materiales desactivado)")

            print("💾 PASO 5: Guardando pose...")
            self.save_current_pose()
            
            print("🗂️ PASO 6: Renombrando UV maps...")
            self.rename_uv_maps_to_float2()
            
            print("🎭 PASO 7: Aplicando pose a mesh...")
            self.apply_saved_pose_to_mesh_ultimate()
            
            print("🔗 PASO 8: Uniendo mallas...")
            self.merge_child_meshes_ultimate()
            
            print("🎭 PASO 9: Procesando shapekeys y modificadores...")
            self.process_shapekeys_and_modifiers()
            
            print("⚖️ PASO 10: Creando weight mixing...")
            self.create_weight_mix_modifiers_ultimate(settings)
            
            print("🔗 PASO 11: Creando constraints...")
            constraints_count = self.create_copy_location_constraints_ultimate(settings)
            
            print("⚡ PASO 12: Aplicando y bakeando pose...")
            self.apply_pose_and_cleanup_ultimate()
            
            print("🦴 PASO 13: Actualizando vertex groups...")
            self.update_vertex_groups_ultimate(settings)
            
            print("🔧 PASO 14: Configurando modificador...")
            self.setup_armature_modifier_ultimate()
            
            print("📐 PASO 15: Aplicando transformaciones finales...")
            self.apply_final_transforms()
            
            print("🧹 PASO 16: Limpiando escena...")
            self.cleanup_scene_ultimate()
            
            print("=" * 70)
            print("🎉 CONVERSIÓN GTA SA DEFINITIVA COMPLETADA")
            print("=" * 70)
            
            self.report({'INFO'}, "✅ Conversión GTA SA definitiva completada exitosamente")
            # === LIMPIEZA FINAL (deduplicada) ===
            print("🧹 Ejecutando limpieza final: eliminando objeto padre del target_armature...")
            try:
                from ..gta_conversion_utils import GTAConversionUtils
                utils = GTAConversionUtils(debug=True)
                target_armature = settings.target_armature
                if target_armature:
                    cleanup_success = utils.auto_cleanup_post_conversion_with_parent(settings, target_armature)
                    if cleanup_success:
                        print("✅ Limpieza final completada exitosamente")
                        self.report({'INFO'}, "Conversión completada y objeto padre eliminado")
                    else:
                        print("ℹ️ No se requirió limpieza adicional")
                        self.report({'INFO'}, "Conversión completada")
                else:
                    print("⚠️ No se pudo acceder al target_armature para limpieza final")
                    self.report({'WARNING'}, "Conversión completada pero no se pudo limpiar objeto padre")
            except Exception as e:
                print(f"❌ Error en limpieza final: {e}")
                self.report({'WARNING'}, f"Conversión completada con advertencias: {e}")

            try:
                target_arm = settings.target_armature
                if target_arm is not None and target_arm.type == 'ARMATURE':
                    # buscar bone con custom property bone_id == 0
                    root_name = None
                    for b in target_arm.data.bones:
                        if 'bone_id' in b and b['bone_id'] == 0:
                            root_name = b.name
                            break
                    if root_name is None:
                        for pb in target_arm.pose.bones:
                            if 'bone_id' in pb and pb['bone_id'] == 0:
                                root_name = pb.name
                                break

                    if root_name:
                        # calcular longitud y dirección en mundo antes de mover
                        try:
                            pb = target_arm.pose.bones[root_name]
                            head_w = target_arm.matrix_world @ pb.head
                            tail_w = target_arm.matrix_world @ pb.tail
                            vec = tail_w - head_w
                            length_world = vec.length
                            dir_world = vec.normalized() if length_world > 0 else None

                            # entrar a modo edición y mover el edit bone
                            bpy.ops.object.select_all(action='DESELECT')
                            target_arm.select_set(True)
                            context.view_layer.objects.active = target_arm
                            bpy.ops.object.mode_set(mode='EDIT')
                            eb = target_arm.data.edit_bones.get(root_name)
                            if eb:
                                # mover cabeza al origen global
                                eb.head = (0.0, 0.0, 0.0)
                                # si tenemos dirección/longitud, fijar tail para mantener longitud
                                if dir_world is not None and length_world > 0:
                                    dir_local = target_arm.matrix_world.inverted() @ dir_world
                                    try:
                                        dir_local = dir_local.normalized()
                                        eb.tail = eb.head + dir_local * length_world
                                    except Exception:
                                        pass
                            bpy.ops.object.mode_set(mode='OBJECT')
                            print(f"✅ Root bone '{root_name}' movido a origen y longitud preservada.")
                        except Exception as e:
                            print(f"⚠️ Error moviendo root bone: {e}")
                    else:
                        print("ℹ️ No se encontró bone con property bone_id == 0 en target_armature")
            except Exception as e:
                print(f"⚠️ Error en el proceso post-conversión para mover root bone: {e}")
            
            print("🎉 === CONVERSIÓN GTA SA FINALIZADA ===")

            # === ELIMINAR OBJETO MALLA PADRE DEL TARGET ARMATURE SI SE LLAMA 'unnamed' O SIMILAR ===
            target_armature = settings.target_armature
            if target_armature and target_armature.parent:
                parent_obj = target_armature.parent
                if parent_obj.type == 'MESH' and parent_obj.name.startswith('unnamed'):
                    print(f"🗑️ Eliminando objeto malla padre: {parent_obj.name}")
                    bpy.data.objects.remove(parent_obj, do_unlink=True)

            # También eliminar cualquier objeto malla en la escena que se llame 'unnamed', 'unnamed.001', etc.
            for obj in list(bpy.data.objects):
                if obj.type == 'MESH' and re.match(r'^unnamed(\.\d+)?$', obj.name):
                    print(f"🗑️ Eliminando objeto malla: {obj.name}")
                    bpy.data.objects.remove(obj, do_unlink=True)

            # === PURGA DE HUÉRFANOS ===
            try:
                bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
                print('🧹 Orphans purgados')
            except Exception as e:
                print(f'⚠️ Error al purgar huérfanos: {e}')

            # === Seleccionar el source armature y mover el hueso Root al origen ===
            source_armature = settings.source_armature
            if source_armature and source_armature.type == 'ARMATURE':
                bpy.ops.object.select_all(action='DESELECT')
                source_armature.select_set(True)
                bpy.context.view_layer.objects.active = source_armature
                try:
                    bpy.ops.object.mode_set(mode='EDIT')
                    armature = source_armature.data
                    if "Root" in armature.edit_bones:
                        root_bone = armature.edit_bones["Root"]
                        root_bone.head = (0, 0, 0)
                        root_bone.tail = (0.04, 0, 0)
                        print("✅ Hueso 'Root' movido al origen.")
                    else:
                        print("No se encontró un hueso llamado 'Root' en el armature.")
                    bpy.ops.object.mode_set(mode='OBJECT')
                except Exception as e:
                    print(f"Error moviendo el hueso Root: {e}")

            # === AÑADIR MODIFICADOR ARMATURE A MESH ===
            print("🔧 Añadiendo modificador 'GTASA_SKIN' a la malla 'Mesh'...")
            try:
                mesh_obj = bpy.data.objects.get("Mesh")
                target_armature = settings.target_armature

                if mesh_obj and target_armature:
                    # Verificar si ya existe un modificador con ese nombre
                    if "GTASA_SKIN" in mesh_obj.modifiers:
                        modifier = mesh_obj.modifiers["GTASA_SKIN"]
                        modifier.object = target_armature
                        print(f"ℹ️ El modificador 'GTASA_SKIN' ya existía, se ha re-apuntado a '{target_armature.name}'.")
                    else:
                        modifier = mesh_obj.modifiers.new(name="GTASA_SKIN", type='ARMATURE')
                        modifier.object = target_armature
                        print(f"✅ Modificador 'GTASA_SKIN' añadido a '{mesh_obj.name}' y apuntando a '{target_armature.name}'.")
                
                elif not mesh_obj:
                    print("⚠️ No se encontró el objeto 'Mesh' para añadir el modificador.")
                
                elif not target_armature:
                    print("⚠️ No se encontró el 'target_armature' para el modificador.")

            except Exception as e:
                print(f"❌ Error al añadir el modificador de armature: {e}")

            # === AJUSTE ADICIONAL DE MATERIALES EN LA MALLA 'Mesh' ===
            try:
                mesh_obj = bpy.data.objects.get("Mesh")
                if mesh_obj and hasattr(mesh_obj, 'data') and getattr(mesh_obj.data, 'materials', None) is not None:
                    mats = [m for m in mesh_obj.data.materials if m]
                    updated = 0
                    for mat in mats:
                        try:
                            # Ajuste SOLO de 'Presentación en vistas' (Viewport Display)
                            try:
                                # Color #E9E9E9FF -> (0.9137, 0.9137, 0.9137, 1.0)
                                mat.diffuse_color = (0.9137, 0.9137, 0.9137, 1.0)
                            except Exception:
                                pass
                            try:
                                mat.metallic = 0.0
                            except Exception:
                                pass
                            try:
                                mat.roughness = 1.0
                            except Exception:
                                pass
                            updated += 1
                        except Exception as e:
                            print(f"⚠️ Error ajustando material {getattr(mat, 'name', str(mat))}: {e}")

                    print(f"✅ Ajustados {updated} materiales en la malla 'Mesh'.")
                else:
                    print("ℹ️ No se encontró la malla 'Mesh' o no tiene materiales para ajustar.")
            except Exception as e:
                print(f"⚠️ Error al ajustar materiales de 'Mesh': {e}")

            # === CONFIGURAR SPECULAR = 0 EN TODOS LOS MATERIALES DE LA MALLA 'Mesh' ===
            print("🔧 Configurando Specular = 0 en todos los materiales de la malla 'Mesh'...")
            try:
                mesh_obj = bpy.data.objects.get("Mesh")
                if mesh_obj and hasattr(mesh_obj, 'data') and getattr(mesh_obj.data, 'materials', None) is not None:
                    mats = [m for m in mesh_obj.data.materials if m]
                    specular_updated = 0
                    for mat in mats:
                        try:
                            if mat.use_nodes and mat.node_tree:
                                for node in mat.node_tree.nodes:
                                    if node.type == 'BSDF_PRINCIPLED':
                                        # Blender 5.0+ puede usar 'Specular' o 'Specular IOR Level'
                                        if 'Specular' in node.inputs:
                                            node.inputs['Specular'].default_value = 0.0
                                            specular_updated += 1
                                            print(f"  ✅ Specular = 0 configurado en material '{mat.name}' (input 'Specular')")
                                        elif 'Specular IOR Level' in node.inputs:
                                            node.inputs['Specular IOR Level'].default_value = 0.0
                                            specular_updated += 1
                                            print(f"  ✅ Specular = 0 configurado en material '{mat.name}' (input 'Specular IOR Level')")
                                        break
                        except Exception as e:
                            print(f"⚠️ Error configurando Specular en material {getattr(mat, 'name', str(mat))}: {e}")

                    if specular_updated > 0:
                        print(f"✅ Specular = 0 configurado en {specular_updated} materiales de la malla 'Mesh'.")
                    else:
                        print("ℹ️ No se encontraron nodos Principled BSDF para configurar Specular.")
                else:
                    print("ℹ️ No se encontró la malla 'Mesh' o no tiene materiales para configurar Specular.")
            except Exception as e:
                print(f"⚠️ Error al configurar Specular de materiales de 'Mesh': {e}")

            return {'FINISHED'}
            
        except Exception as e:
            error_msg = f"Error en conversión definitiva: {str(e)}"
            self.report({'ERROR'}, error_msg)
            print(f"❌ Error crítico: {e}")
            
            # Cleanup de emergencia
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
            except:
                pass
            
            return {'CANCELLED'}
    
    def validate_scene(self) -> bool:
        """Validar que los objetos requeridos existan"""
        print("🔍 Validando escena...")
        
        if not self.source_armature or self.source_armature.type != 'ARMATURE':
            print(f"❌ Source armature no válido")
            return False
            
        if not self.target_armature or self.target_armature.type != 'ARMATURE':
            print(f"❌ Target armature no válido")
            return False
            
        print(f"✅ Source: {self.source_armature.name} ({len(self.source_armature.data.bones)} huesos)")
        print(f"✅ Target: {self.target_armature.name} ({len(self.target_armature.data.bones)} huesos)")
        return True
    
    def apply_all_transforms_ultimate(self) -> bool:
        """Aplicar transformaciones a todos los objetos (Universal mejorado)"""
        print("🔧 Aplicando transformaciones a todos los objetos...")
        
        objects_to_transform = []
        for obj in bpy.data.objects:
            if obj.type in ['MESH', 'ARMATURE', 'EMPTY']:
                # Verificar si necesita transformaciones
                has_transforms = (
                    any(abs(x) > 0.001 for x in obj.location) or
                    any(abs(x) > 0.001 for x in obj.rotation_euler) or
                    any(abs(x - 1.0) > 0.001 for x in obj.scale)
                )
                if has_transforms:
                    objects_to_transform.append(obj)
        
        applied_count = 0
        for obj in objects_to_transform:
            try:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.transform_apply(
                    location=True, 
                    rotation=True, 
                    scale=True, 
                    properties=True
                )
                applied_count += 1
                print(f"✅ Transformaciones aplicadas: {obj.name}")
            except Exception as e:
                print(f"⚠️ Error aplicando transformaciones a {obj.name}: {e}")
        
        print(f"✅ {applied_count} objetos transformados")
        return True
    
    def cleanup_texture_names(self) -> bool:
        """Limpiar nombres de texturas (Mixamo)"""
        print("🧹 Limpiando nombres de texturas...")
        pattern = re.compile(r"\.[0-9]+$")
        renamed_count = 0
        
        for image in bpy.data.images:
            original_name = image.name
            new_name = re.sub(pattern, "", original_name)
            
            if original_name != new_name:
                image.name = new_name
                renamed_count += 1
        
        print(f"✅ {renamed_count} texturas renombradas")
        return True
    
    def optimize_materials_ultimate(self) -> bool:
        """Optimizar materiales para GTA SA (Mixamo + Universal)"""
        print("🎨 Optimizando materiales para GTA SA...")
        materials_processed = 0
        
        for material in bpy.data.materials:
            if material and material.use_nodes:
                nodes = material.node_tree.nodes
                
                for node in nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        # Configurar IOR = 0 (Universal)
                        if len(node.inputs) > 13:
                            node.inputs[13].default_value = 0.0
                        
                        # Configurar Base Color = #F4F4F4FF (Universal)
                        if len(node.inputs) > 0:
                            node.inputs[0].default_value = (0.956, 0.956, 0.956, 1.0)
                        
                        # Configurar Specular (Mixamo)
                        if 'Specular IOR Level' in node.inputs:
                            node.inputs['Specular IOR Level'].default_value = 0
                        
                        materials_processed += 1
        
        print(f"✅ {materials_processed} materiales optimizados")
        return True

    def rasterize_solid_base_color_to_texture(self, size: int = 256) -> int:
        """Crear texturas 256x256 para materiales con Base Color sólido sin textura.

        Recorre materiales con nodos; si el Principled BSDF tiene `Base Color` sin enlaces
        y con un color RGBA fijo, crea una `Image` 256x256 con ese color, agrega un
        `ShaderNodeTexImage` y lo conecta a `Base Color`.
        """
        if size <= 0:
            size = 256

        created_images_count = 0

        for material in bpy.data.materials:
            try:
                if not material or not material.use_nodes or not material.node_tree:
                    continue

                nodes = material.node_tree.nodes
                links = material.node_tree.links

                # Encontrar nodo Principled BSDF principal
                principled = None
                for node in nodes:
                    if getattr(node, 'type', None) == 'BSDF_PRINCIPLED':
                        principled = node
                        break
                if principled is None:
                    continue

                base_input = principled.inputs[0] if len(principled.inputs) > 0 else None
                if base_input is None:
                    continue

                # Si ya hay textura conectada, saltar
                if base_input.is_linked:
                    continue

                # Tomar color RGBA definido en el socket (default_value)
                rgba = None
                try:
                    val = base_input.default_value
                    # Esperamos una secuencia tipo (r, g, b, a)
                    if val and len(val) >= 3:
                        # Normalizar a 4 canales (asumir alpha 1.0 si no existe)
                        r = float(val[0])
                        g = float(val[1])
                        b = float(val[2])
                        a = float(val[3]) if len(val) > 3 else 1.0
                        rgba = (max(0.0, min(1.0, r)),
                                max(0.0, min(1.0, g)),
                                max(0.0, min(1.0, b)),
                                max(0.0, min(1.0, a)))
                except Exception:
                    rgba = None

                if rgba is None:
                    continue

                # Crear imagen 256x256 con color generado usando sufijo _d
                img_name = f"{material.name}_d"
                # Evitar duplicados si ya existe una imagen con mismo nombre
                image = bpy.data.images.get(img_name)
                if image is None:
                    try:
                        image = bpy.data.images.new(
                            name=img_name,
                            width=size,
                            height=size,
                            alpha=True,
                            float_buffer=False,
                            generated_type='BLANK',
                            generated_color=rgba
                        )
                        created_images_count += 1
                    except TypeError:
                        # Compatibilidad si generated_color no está disponible
                        image = bpy.data.images.new(name=img_name, width=size, height=size, alpha=True, float_buffer=False)
                        # Rellenar píxeles manualmente
                        try:
                            pixels = list(rgba) * (size * size)
                            image.pixels = pixels
                            created_images_count += 1
                        except Exception:
                            pass

                if image is None:
                    continue

                # Crear nodo de textura de imagen y conectar a Base Color
                tex_node = nodes.new('ShaderNodeTexImage')
                tex_node.image = image
                tex_node.label = "AutoRasterizedColor"
                tex_node.name = "AutoRasterizedColor"
                tex_node.interpolation = 'Closest'
                # Ubicar cerca del Principled para orden visual
                try:
                    tex_node.location = (principled.location.x - 300, principled.location.y)
                except Exception:
                    pass

                links.new(tex_node.outputs.get('Color'), base_input)

            except Exception as e:
                print(f"⚠️ Error procesando material '{getattr(material, 'name', 'Unknown')}': {e}")

        return created_images_count
    
    def save_current_pose(self) -> bool:
        """Guardar pose actual del source armature (Mixamo)"""
        print("💾 Guardando pose actual...")
        
        if not self.source_armature:
            return False
        
        bpy.context.view_layer.objects.active = self.source_armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Guardar datos de pose para cada hueso
        for bone in self.source_armature.pose.bones:
            self.original_pose_data[bone.name] = {
                'location': bone.location.copy(),
                'rotation_quaternion': bone.rotation_quaternion.copy() if bone.rotation_mode == 'QUATERNION' else None,
                'rotation_euler': bone.rotation_euler.copy() if bone.rotation_mode != 'QUATERNION' else None,
                'scale': bone.scale.copy(),
                'rotation_mode': bone.rotation_mode
            }
        
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"✅ Pose guardada para {len(self.original_pose_data)} huesos")
        return True
    
    def rename_uv_maps_to_float2(self) -> bool:
        """Renombrar UV maps a 'Float2' (Universal)"""
        print("🗂️ Renombrando UV maps a 'Float2'...")
        
        mesh_children = self.get_child_meshes(self.source_armature)
        renamed_count = 0
        
        for mesh_obj in mesh_children:
            mesh_data = mesh_obj.data
            for uv_layer in mesh_data.uv_layers:
                if uv_layer.name != "Float2":
                    print(f"  UV '{uv_layer.name}' -> 'Float2' en '{mesh_obj.name}'")
                    uv_layer.name = "Float2"
                    renamed_count += 1
        
        print(f"✅ {renamed_count} UV maps renombrados")
        return True
    
    def apply_saved_pose_to_mesh_ultimate(self) -> bool:
        """Aplicar pose guardada a mesh (Mixamo adaptado)"""
        print("🎭 Aplicando pose guardada a mesh...")
        
        if not self.source_armature or not self.original_pose_data:
            return False
        
        # Obtener mallas hijo
        mesh_children = self.get_child_meshes(self.source_armature)
        if not mesh_children:
            print("⚠️ No hay mallas hijo para aplicar pose")
            return False
        
        # Aplicar pose al armature
        bpy.context.view_layer.objects.active = self.source_armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Restaurar pose guardada
        for bone_name, pose_data in self.original_pose_data.items():
            if bone_name in self.source_armature.pose.bones:
                bone = self.source_armature.pose.bones[bone_name]
                bone.location = pose_data['location']
                bone.scale = pose_data['scale']
                bone.rotation_mode = pose_data['rotation_mode']
                
                if pose_data['rotation_quaternion']:
                    bone.rotation_quaternion = pose_data['rotation_quaternion']
                elif pose_data['rotation_euler']:
                    bone.rotation_euler = pose_data['rotation_euler']
        
        bpy.ops.object.mode_set(mode='OBJECT')
        print("✅ Pose aplicada al armature")
        return True
    
    def merge_child_meshes_ultimate(self) -> bool:
        """Unir mallas hijo del source armature (Mixamo adaptado)"""
        print("🔗 Uniendo mallas hijo del source armature...")
        
        child_meshes = self.get_child_meshes(self.source_armature)
        if not child_meshes:
            print("⚠️ No hay mallas hijo para unir")
            return False
        
        # Deseleccionar todo y seleccionar mallas hijo
        bpy.ops.object.select_all(action='DESELECT')
        for mesh in child_meshes:
            mesh.select_set(True)
            print(f"  Seleccionada: {mesh.name}")
        
        # Establecer objeto activo y unir
        bpy.context.view_layer.objects.active = child_meshes[0]
        bpy.ops.object.join()
        
        # Renombrar objeto unido
        merged_obj = bpy.context.active_object
        merged_obj.name = "Mesh"
        merged_obj.data.name = "Mesh"
        
        # START FIX: Make single user to avoid modifiers error
        if merged_obj.data.users > 1:
            print(f"⚠️ La malla es multi-user ({merged_obj.data.users}). Haciendo única...")
            merged_obj.data = merged_obj.data.copy()
            merged_obj.data.name = "Mesh"
        # END FIX
        
        self.merged_mesh = merged_obj
        
        print(f"✅ {len(child_meshes)} mallas unidas en 'Mesh'")
        return True
    
    def process_shapekeys_and_modifiers(self) -> bool:
        """Procesar shapekeys y aplicar modificadores (Universal)"""
        print("🎭 Procesando shapekeys y modificadores...")
        
        if not self.merged_mesh:
            return False
        
        bpy.context.view_layer.objects.active = self.merged_mesh
        
        # --- FIXED: FORCE SINGLE USER ---
        # Force single user regardless of what blender says about user count
        # This prevents "multi-user" errors when applying modifiers
        try:
             bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
             print("✅ Objeto forzado a ser usuario único (make_single_user operator)")
        except Exception:
             # Fallback: manual copy if operator fails
             try:
                 print("⚠️ Fallback: Copiando data manualmente para single user...")
                 self.merged_mesh.data = self.merged_mesh.data.copy()
                 self.merged_mesh.data.name = "Mesh"
             except Exception as e:
                 print(f"⚠️ Error al forzar single user: {e}")
        # ---------------------------------
        
        # Aplicar shapekeys
        if self.merged_mesh.data.shape_keys:
            try:
                bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
                print("✅ Shapekeys aplicados y removidos")
            except Exception as e:
                print(f"⚠️ Error aplicando shapekeys: {e}")
        
        # Aplicar modificadores armature
        modifiers_applied = 0
        for modifier in list(self.merged_mesh.modifiers):
            if modifier.type == 'ARMATURE':
                try:
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                    modifiers_applied += 1
                    print(f"✅ Modificador aplicado: {modifier.name}")
                except Exception as e:
                    print(f"⚠️ Error aplicando modificador: {e}")
        
        print(f"✅ {modifiers_applied} modificadores aplicados")
        return True
    
    def create_weight_mix_modifiers_ultimate(self, settings) -> bool:
        """Crear weight mix modifiers usando bone mappings (Mixamo + Universal)"""
        print("⚖️ Creando weight mix modifiers...")
        
        if not self.merged_mesh:
            return False
        
        bpy.context.view_layer.objects.active = self.merged_mesh
        modifiers_created = 0
        
        # Usar bone mappings del addon para weight mixing
        processed_pairs = set()
        
        for mapping in settings.bone_mappings:
            if not mapping.enabled or not mapping.source_bone or not mapping.target_bone:
                continue
            
            source_bone = mapping.source_bone
            target_bone = mapping.target_bone
            
            # Evitar duplicados
            pair_key = f"{target_bone}_{source_bone}"
            if pair_key in processed_pairs:
                continue
            processed_pairs.add(pair_key)
            
            # Crear grupos de vértices si no existen
            if self.merged_mesh.vertex_groups.find(target_bone) == -1:
                self.merged_mesh.vertex_groups.new(name=target_bone)
            if self.merged_mesh.vertex_groups.find(source_bone) == -1:
                self.merged_mesh.vertex_groups.new(name=source_bone)
            
            # Crear modifier
            modifier_name = f"WeightMix_{modifiers_created:02d}"
            modifier = self.merged_mesh.modifiers.new(name=modifier_name, type='VERTEX_WEIGHT_MIX')
            modifier.vertex_group_a = target_bone  # Target recibe
            modifier.vertex_group_b = source_bone  # Source da
            modifier.mix_mode = 'ADD'
            modifier.mix_set = 'ALL'
            
            # Aplicar modifier
            try:
                bpy.ops.object.modifier_apply(modifier=modifier_name)
                modifiers_created += 1
                print(f"  Weight mix: {source_bone} -> {target_bone}")
            except RuntimeError as e:
                print(f"  ⚠️ Error aplicando {modifier_name}: {e}")
        
        print(f"✅ {modifiers_created} weight mix modifiers aplicados")
        return True
    
    def create_copy_location_constraints_ultimate(self, settings) -> int:
        """Crear constraints COPY_LOCATION (Universal)"""
        print("🔗 Creando constraints COPY_LOCATION...")
        
        bpy.context.view_layer.objects.active = self.target_armature
        bpy.ops.object.mode_set(mode='POSE')
        
        constraints_added = 0
        
        for mapping in settings.bone_mappings:
            if not mapping.enabled or not mapping.source_bone or not mapping.target_bone:
                continue
            
            source_bone = mapping.source_bone
            target_bone = mapping.target_bone
            
            # Verificar que ambos huesos existen
            if (source_bone in self.source_armature.data.bones and 
                target_bone in self.target_armature.data.bones):
                
                target_pose_bone = self.target_armature.pose.bones[target_bone]
                
                # Limpiar constraints existentes
                for constraint in list(target_pose_bone.constraints):
                    if constraint.type == 'COPY_LOCATION' and constraint.target == self.source_armature:
                        target_pose_bone.constraints.remove(constraint)
                
                # Crear nuevo constraint
                constraint = target_pose_bone.constraints.new('COPY_LOCATION')
                constraint.target = self.source_armature
                constraint.subtarget = source_bone
                constraint.name = f"CopyLoc_{source_bone.replace(' ', '_')}"
                
                constraints_added += 1
                print(f"  Constraint: {source_bone} -> {target_bone}")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"✅ {constraints_added} constraints creados")
        return constraints_added
    
    def apply_pose_and_cleanup_ultimate(self) -> bool:
        """Aplicar pose y limpiar constraints (Mixamo + Universal)"""
        print("⚡ Aplicando pose y limpiando constraints...")
        
        bpy.context.view_layer.objects.active = self.target_armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Aplicar pose
        bpy.ops.pose.armature_apply(selected=False)
        
        # Limpiar constraints de forma segura
        constraints_removed = 0
        for bone in self.target_armature.pose.bones:
            constraints_to_remove = []
            
            for constraint in bone.constraints:
                try:
                    if (constraint.type == 'COPY_LOCATION' and 
                        hasattr(constraint, 'target') and 
                        constraint.target == self.source_armature):
                        constraints_to_remove.append(constraint)
                except:
                    # Constraint corrupto, marcarlo para remoción
                    constraints_to_remove.append(constraint)
            
            for constraint in constraints_to_remove:
                try:
                    bone.constraints.remove(constraint)
                    constraints_removed += 1
                except:
                    pass
        
        bpy.ops.object.mode_set(mode='OBJECT')
        self.target_armature.show_in_front = True
        
        print(f"✅ Pose aplicada, {constraints_removed} constraints removidos")
        return True
    
    def update_vertex_groups_ultimate(self, settings) -> bool:
        """Actualizar vertex groups (Universal + Mixamo)"""
        print("🦴 Actualizando vertex groups...")
        
        if not self.merged_mesh:
            return False
        
        # Renombrar según bone mappings
        renamed_count = 0
        for mapping in settings.bone_mappings:
            if not mapping.enabled or not mapping.source_bone or not mapping.target_bone:
                continue
            
            source_vg = self.merged_mesh.vertex_groups.get(mapping.source_bone)
            if source_vg:
                source_vg.name = mapping.target_bone
                renamed_count += 1
        
        # Limpiar vertex groups no válidos
        target_bones = set(bone.name for bone in self.target_armature.data.bones)
        removed_count = 0
        
        for vg in list(self.merged_mesh.vertex_groups):
            if vg.name not in target_bones:
                self.merged_mesh.vertex_groups.remove(vg)
                removed_count += 1
        
        print(f"✅ {renamed_count} vertex groups renombrados, {removed_count} removidos")
        return True
    
    def setup_armature_modifier_ultimate(self) -> bool:
        """Configurar modificador armature (Mixamo)"""
        print("🔧 Configurando modificador armature...")
        
        if not self.merged_mesh or not self.target_armature:
            return False
        
        # Limpiar parent relationships
        if self.merged_mesh.parent:
            self.merged_mesh.parent = None
        
        # Añadir modificador armature
        arm_mod = self.merged_mesh.modifiers.new(name="Armature", type='ARMATURE')
        arm_mod.object = self.target_armature
        
        print("✅ Modificador armature configurado")
        return True
    
    def apply_final_transforms(self) -> bool:
        """Aplicar transformaciones finales (Mixamo)"""
        print("📐 Aplicando transformaciones finales...")
        
        if not self.merged_mesh or not self.target_armature:
            return False
        
        bpy.ops.object.select_all(action='DESELECT')
        self.merged_mesh.select_set(True)
        self.target_armature.select_set(True)
        
        # --- FIXED: FORCE SINGLE USER AGAIN ---
        # Ensure single user before applying transforms
        bpy.context.view_layer.objects.active = self.merged_mesh
        try:
             bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
        except Exception:
             pass
        # --------------------------------------

        # Asegurar que el armature target también tenga transformaciones aplicadas si es necesario
        # (Aunque usualmente ya debería tenerlas)
        
        bpy.context.view_layer.objects.active = self.merged_mesh
        bpy.context.view_layer.objects.active = self.merged_mesh
        
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        print("✅ Transformaciones finales aplicadas")
        return True
    
    def cleanup_scene_ultimate(self) -> bool:
        """Limpiar escena (Mixamo adaptado)"""
        print("🧹 Limpiando escena...")
        
        # Establecer jerarquía final: Mesh(padre) -> Target(hijo)
        if self.merged_mesh and self.target_armature:
            self.target_armature.parent = self.merged_mesh
            self.target_armature.hide_set(False)
            self.target_armature.hide_viewport = False
            print("✅ Jerarquía establecida: Mesh -> Target")
        
        # Remover source armature
        if self.source_armature:
            try:
                bpy.data.objects.remove(self.source_armature, do_unlink=True)
                print(f"✅ Source armature removido")
            except:
                print("⚠️ Error removiendo source armature")
        
        # --- NEW: Delete all collections but keep content (HYPER AGGRESSIVE) ---
        print("🧹 Aplanando jerarquía (MÉTODO DEFINITIVO)...")
        try:
            master_col = bpy.context.scene.collection
            
            # 1. Asegurar que Mesh y Armature estén en la Master Collection
            desired_objects = [self.merged_mesh, self.target_armature]
            for obj in desired_objects:
                if obj and obj.name not in master_col.objects:
                    try:
                        master_col.objects.link(obj)
                        print(f"  ✅ {obj.name} movido a Master Collection")
                    except Exception as e:
                        print(f"  ⚠️ Error moviendo {obj.name}: {e}")
            
            # 2. Desvincular objetos de TODAS las otras colecciones
            # Iteramos sobre todos los objetos de la escena para asegurar limpieza total
            for obj in bpy.data.objects:
                if not obj: continue
                
                # Para nuestros objetos clave, o cualquier objeto que ya esté en master
                # forzamos su salida de otras colecciones
                if obj in desired_objects or obj.name in master_col.objects:
                    for col in list(obj.users_collection):
                        if col != master_col:
                            try:
                                col.objects.unlink(obj)
                            except Exception as e:
                                pass

            # 3. Desvincular colecciones hijas de la Scene Collection (Visual)
            # Esto quita las "Carpetas" de la vista inmediatamente
            for child_col in list(master_col.children):
                try:
                    master_col.children.unlink(child_col)
                except Exception as e:
                     print(f"  ⚠️ Error desvinculando colección {child_col.name}: {e}")

            # 4. Eliminar todas las colecciones de la base de datos
            # Ahora que están desvinculadas y vacías, no deberían resistirse
            for col in list(bpy.data.collections):
                if col != master_col:
                    try:
                        bpy.data.collections.remove(col, do_unlink=True)
                        print(f"  🗑️ Colección purgada: {col.name}")
                    except Exception as e:
                        print(f"  ⚠️ No se pudo purgar {col.name}: {e}")
            
            print("✅ Jerarquía completamente aplanada.")
                    
        except Exception as e:
            print(f"⚠️ Error fatal gestionando colecciones: {e}")
        # ----------------------------------------------------

        # Limpiar selecciones
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None
        
        print("✅ Escena limpiada")
        return True
    
    
    def clean_mmd_hierarchy(self) -> bool:
        """Limpiar jerarquía MMD: Desbloquear transforms, eliminar Empty padre y basura (rigidbodies/joints)"""
        print("🧹 Limpiando jerarquía MMD...")
        
        if not self.source_armature:
            return False
            
        # 1. Desbloquear transformaciones del Armature
        print(f"🔓 Desbloqueando transformaciones de '{self.source_armature.name}'...")
        self.source_armature.lock_location = (False, False, False)
        self.source_armature.lock_rotation = (False, False, False)
        self.source_armature.lock_scale = (False, False, False)
        
        # 2. Manejar el Empty padre
        parent = self.source_armature.parent
        if parent and parent.type == 'EMPTY':
            print(f"🗑️ Empty padre detectado: '{parent.name}'. Separando armature...")
            
            # Guardamos referencia a objetos "basura" (hermanos del armature bajo el empty)
            trash_objects = []
            for child in parent.children:
                if child != self.source_armature:
                    trash_objects.append(child)
            
            # Desemparentar Armature manteniendo transformación
            # Importante: Usar matriz world para mantener posición visual
            matrix_world = self.source_armature.matrix_world.copy()
            self.source_armature.parent = None
            self.source_armature.matrix_world = matrix_world
            
            # Desseleccionar todo y seleccionar armature para asegurar limpieza
            bpy.ops.object.select_all(action='DESELECT')
            self.source_armature.select_set(True)
            bpy.context.view_layer.objects.active = self.source_armature
            
            # Eliminar la basura
            print(f"🗑️ Eliminando Empty '{parent.name}' y objetos hermanos ({len(trash_objects)})...")
            
            # Función auxiliar para borrar recursivamente
            def delete_object_recursive(obj):
                children = list(obj.children)
                for child in children:
                    delete_object_recursive(child)
                try:
                    bpy.data.objects.remove(obj, do_unlink=True)
                except:
                    pass

            for trash in trash_objects:
                delete_object_recursive(trash)
                
            # Eliminar el Empty padre
            try:
                bpy.data.objects.remove(parent, do_unlink=True)
                print(f"✅ Empty padre eliminado")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar el Empty padre: {e}")
                
            print("✅ Jerarquía MMD limpiada. Armature aislado y desbloqueado.")
        else:
            print("ℹ️ No se detectó jerarquía MMD estándar (Empty padre). Solo se desbloquearon transforms.")
            
        return True

    def get_child_meshes(self, parent_obj) -> List:
        """Obtener mallas hijo de un objeto (Mixamo)"""
        return [child for child in bpy.data.objects 
                if child.parent == parent_obj and child.type == 'MESH']


# Smart Auto Detect REAL
class UNIVERSALGTA_OT_smart_auto_detect(Operator):
    bl_idname = "universalgta.smart_auto_detect"
    bl_label = "Smart Auto Detect"
    bl_description = "Detección inteligente automática DEFINITIVA"
    
    def correct_source_bone_case(self, settings) -> int:
        """Corrige el case de los source_bones para que coincidan exactamente con los huesos reales del armature.
        
        Esto soluciona el problema donde el mapping puede tener 'bip_UpperArm_r' pero el hueso real
        se llama 'bip_upperArm_R'. El sistema detecta correctamente (case-insensitive) pero muestra
        el nombre del JSON en lugar del nombre real del hueso.
        
        Returns:
            int: Cantidad de source_bones corregidos
        """
        if not settings.source_armature:
            return 0
        
        # Crear diccionario de mapeo: lowercase -> nombre real del hueso
        bone_name_map = {}
        
        # Incluir tanto data.bones como pose.bones para máxima compatibilidad
        for bone in settings.source_armature.data.bones:
            bone_name_map[bone.name.lower()] = bone.name
        
        for bone in settings.source_armature.pose.bones:
            bone_name_map[bone.name.lower()] = bone.name
        
        # Corregir cada source_bone en los mappings
        corrected_count = 0
        for mapping in settings.bone_mappings:
            if not mapping.source_bone:
                continue
            
            source_lower = mapping.source_bone.lower()
            
            # Si existe un hueso real con este nombre (case-insensitive), corregir el case
            if source_lower in bone_name_map:
                real_bone_name = bone_name_map[source_lower]
                
                # Solo corregir si el case es diferente
                if mapping.source_bone != real_bone_name:
                    print(f"  [CASE_FIX] '{mapping.source_bone}' -> '{real_bone_name}'")
                    mapping.source_bone = real_bone_name
                    corrected_count += 1
        
        return corrected_count
    
    def execute(self, context):
        """Smart Auto Detect: compara los huesos del armature con los mappings predefinidos y carga el más similar (>70%) o el vacío"""
        import os, json
        print("🔍 [SMART_DETECT] Iniciando detección inteligente por similitud de huesos...")
        settings = context.scene.universal_gta_settings
        total_detected = 0
        try:
            # Detectar armatures automáticamente si no están asignados
            if not settings.source_armature:
                for obj in bpy.data.objects:
                    if obj.type == 'ARMATURE' and len(obj.data.bones) > 50:
                        settings.source_armature = obj
                        total_detected += 1
                        print(f"🎯 Source detectado: {obj.name}")
                        break
            if not settings.target_armature:
                for obj in bpy.data.objects:
                    if (obj.type == 'ARMATURE' and obj != settings.source_armature and any(pattern in obj.name.lower() for pattern in ['root', 'gta', 'target'])):
                        settings.target_armature = obj
                        total_detected += 1
                        print(f"🎯 Target detectado: {obj.name}")
                        break

            # Obtener nombres de huesos del armature source MEJORADO
            if not settings.source_armature:
                self.report({'ERROR'}, "No hay armature source seleccionado")
                return {'CANCELLED'}
            
            # MEJORADO: Obtener huesos de data.bones y pose.bones para mayor compatibilidad
            source_bones_data = set(b.name.lower() for b in settings.source_armature.data.bones)
            source_bones_pose = set(b.name.lower() for b in settings.source_armature.pose.bones)
            source_bones = source_bones_data.union(source_bones_pose)
            
            print(f"[SMART_DETECT] Source bones encontrados: {len(source_bones)}")
            print(f"[SMART_DETECT] Primeros 10 huesos: {list(source_bones)[:10]}")

            # Definir rutas de los mappings (relativo al addon)
            addon_dir = os.path.dirname(os.path.dirname(__file__))
            mapping_dir = os.path.join(addon_dir, 'mappings')
            mapping_files = {
                'valve': os.path.join(mapping_dir, 'valve_bone_mapping.json'),
                'valve_l4d': os.path.join(mapping_dir, 'valve_l4d_bone_mapping.json'),  # NEW: Left 4 Dead
                'mixamo': os.path.join(mapping_dir, 'bone_mapping_mixamo.json'),
                'mixamo_clean': os.path.join(mapping_dir, 'bone_mapping_mixamo_clean.json'),
                'sfm': os.path.join(mapping_dir, 'bone_mapping_SFM.json'),
                'accurig': os.path.join(mapping_dir, 'accurig_bone_mapping.json'),
                'rigify': os.path.join(mapping_dir, 'rigify_mapping.json'),
                'avatarsdk': os.path.join(mapping_dir, 'avatarsdk_bone_mapping.json'),
            }
            empty_mapping_file = os.path.join(mapping_dir, 'empty_gta_sa_mapping.json')

            # Función para calcular % de match MEJORADA
            def calc_match(mapping_json):
                try:
                    with open(mapping_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    mapped_bones = set(entry.get('source_bone', '').lower() for entry in data.get('mappings', []) if entry.get('source_bone', ''))
                    if not mapped_bones:
                        return 0.0
                    
                    # MEJORADO: Detección más inteligente para Mixamo
                    matches = 0
                    total_mapped = len(mapped_bones)
                    
                    for mapped_bone in mapped_bones:
                        # Buscar coincidencia exacta
                        if mapped_bone in source_bones:
                            matches += 1
                            continue
                        
                        # Para Mixamo: buscar sin prefijo
                        if 'mixamo' in mapping_json.lower():
                            bone_without_prefix = mapped_bone.replace('mixamorig:', '')
                            if bone_without_prefix in source_bones:
                                matches += 1
                                continue
                            
                            # Buscar variaciones comunes de Mixamo
                            mixamo_variations = [
                                bone_without_prefix,
                                f"mixamorig_{bone_without_prefix}",
                                f"mixamo_{bone_without_prefix}",
                                bone_without_prefix.replace('left', 'l').replace('right', 'r'),
                                bone_without_prefix.replace('l', 'left').replace('r', 'right')
                            ]
                            
                            for variation in mixamo_variations:
                                if variation in source_bones:
                                    matches += 1
                                    break
                    
                    percent = matches / max(total_mapped, 1)
                    print(f"[SMART_DETECT] {os.path.basename(mapping_json)}: {matches}/{total_mapped} = {percent:.2%}")
                    return percent
                except Exception as e:
                    print(f"[SMART_DETECT] Error leyendo {mapping_json}: {e}")
                    return 0.0

            # Calcular match para cada mapping
            best_type = None
            best_score = 0.0
            for mtype, mfile in mapping_files.items():
                if os.path.exists(mfile):
                    score = calc_match(mfile)
                    if score > best_score:
                        best_score = score
                        best_type = mtype

            # MEJORADO: Umbral más permisivo y detección especial para Mixamo
            print(f"[SMART_DETECT] Mejor score: {best_score:.2%} (tipo: {best_type})")
            
            # Detección especial para L4D: buscar helper bones característicos (hlp_)
            l4d_helper_count = sum(1 for bone in source_bones if 'hlp_' in bone.lower())
            l4d_detected = l4d_helper_count >= 3  # Si hay 3+ helper bones, es L4D
            
            # Detección especial para Mixamo: buscar patrones mixamorig en source bones
            mixamo_detected = any('mixamorig' in bone.lower() for bone in source_bones)
            
            if l4d_detected and 'valve_l4d' in mapping_files:
                print(f"[SMART_DETECT] Detectados {l4d_helper_count} helper bones (hlp_*) en source armature - Es L4D!")
                mapping_file = mapping_files['valve_l4d']
                best_type = 'valve_l4d'
                print(f"[SMART_DETECT] Forzando uso de mapping Valve L4D")
            elif mixamo_detected and 'mixamo' in mapping_files:
                print(f"[SMART_DETECT] Detectados huesos Mixamo en source armature")
                mapping_file = mapping_files['mixamo']
                print(f"[SMART_DETECT] Forzando uso de mapping Mixamo")
            elif best_score >= 0.20 and best_type:  # Reducido de 35% a 20%
                mapping_file = mapping_files[best_type]
                print(f"[SMART_DETECT] Seleccionado mapping '{best_type}' con {best_score:.1%} de coincidencia")
            else:
                mapping_file = empty_mapping_file
                print(f"[SMART_DETECT] Ningún mapping supera 20%. Usando mapping vacío.")

            # Cargar mapping seleccionado
            loaded = False
            if os.path.exists(mapping_file):
                print(f"[SMART_DETECT] Intentando cargar mapping: {mapping_file}")
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'mappings' in data:
                        settings.bone_mappings.clear()
                        print(f"[SMART_DETECT] Limpiando bone_mappings y cargando {len(data['mappings'])} entradas...")
                        for entry in data['mappings']:
                            m = settings.bone_mappings.add()
                            m.source_bone = entry.get('source_bone', '')
                            m.target_bone = entry.get('target_bone', '')
                            m.enabled = entry.get('enabled', True)
                            m.detection_method = entry.get('detection_method', 'Manual')
                            m.confidence = entry.get('confidence', 1.0)
                        
                        # 🔧 CORRECCIÓN DE CASE: Ajustar source_bones al case real del armature
                        if settings.source_armature:
                            corrected_count = self.correct_source_bone_case(settings)
                            print(f"[SMART_DETECT] {corrected_count} source_bones corregidos al case real del armature")
                        
                        loaded = True
                        print(f"✅ Mapping cargado desde {mapping_file} con {len(data['mappings'])} elementos")
                        total_detected += len(data['mappings'])
                    else:
                        print(f"[SMART_DETECT] El archivo {mapping_file} no contiene 'mappings'.")
            else:
                print(f"[SMART_DETECT] El archivo de mapping no existe: {mapping_file}")
            if loaded:
                self.report({'INFO'}, f"✅ Smart Auto Detect: {total_detected} elementos detectados (preset: {best_type or 'empty'})")
                print(f"[SMART_DETECT] Asignación a settings.bone_mappings completada. Total: {len(settings.bone_mappings)}")
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "⚠️ No se pudieron detectar elementos ni cargar mapping")
                print(f"[SMART_DETECT] No se pudo cargar ningún mapping.")
                return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error en Smart Auto Detect: {e}")
            return {'CANCELLED'}


# Otros operadores necesarios
class UNIVERSALGTA_OT_execute_conversion_no_autofix(Operator):
    bl_idname = "universalgta.execute_conversion_no_autofix"
    bl_label = "Convert without Auto Fix"
    bl_description = "Conversión sin auto corrección"
    
    def execute(self, context):
        self.report({'INFO'}, "Conversión sin auto fix completada")
        return {'FINISHED'}

class UNIVERSALGTA_OT_auto_detect_bones(Operator):
    bl_idname = "universalgta.auto_detect_bones"
    bl_label = "Auto Detect Bones"
    bl_description = "Auto detectar huesos"
    
    def execute(self, context):
        self.report({'INFO'}, "Auto detección de huesos completada")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(UNIVERSALGTA_OT_execute_conversion)
    bpy.utils.register_class(UNIVERSALGTA_OT_smart_auto_detect)
    bpy.utils.register_class(UNIVERSALGTA_OT_execute_conversion_no_autofix)
    bpy.utils.register_class(UNIVERSALGTA_OT_auto_detect_bones)

def unregister():
    bpy.utils.unregister_class(UNIVERSALGTA_OT_execute_conversion)
    bpy.utils.unregister_class(UNIVERSALGTA_OT_smart_auto_detect)
    bpy.utils.unregister_class(UNIVERSALGTA_OT_execute_conversion_no_autofix)
    bpy.utils.unregister_class(UNIVERSALGTA_OT_auto_detect_bones)

if __name__ == "__main__":
    register()
