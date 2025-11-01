import bpy
from bpy.props import FloatProperty
from mathutils import Vector, Matrix


class UNIVERSALGTA_OT_adjust_skin_height(bpy.types.Operator):
    bl_idname = "universalgta.adjust_skin_height"
    bl_label = "Aplicar Altura"
    bl_description = "Escala la malla y armature para ajustar la altura del skin en metros"

    def execute(self, context):
        scene = context.scene
        height = getattr(scene, 'gta_skin_height', 1.8)

        # Paso 1: usar objetos seleccionados si hay, sino fallback heurístico
        sel_objs = [o for o in context.selected_objects if o.type in {'MESH', 'ARMATURE'}]
        if not sel_objs:
            objs = [o for o in context.scene.objects if o.type in {'MESH', 'ARMATURE'}]
            if not objs:
                self.report({'ERROR'}, "No se encontraron objetos MESH o ARMATURE en la escena")
                return {'CANCELLED'}
            sel_objs = objs

        # Expandir selección: si hay armature(s) seleccionados, incluir mallas parented a ellos
        # o mallas que usan un Armature modifier apuntando a ese armature
        extra = []
        for a in [o for o in sel_objs if o.type == 'ARMATURE']:
            # children (direct) that are meshes
            for child in a.children:
                if child.type == 'MESH' and child not in sel_objs:
                    extra.append(child)
            # meshes with Armature modifier pointing to this armature
            for m in [o for o in context.scene.objects if o.type == 'MESH']:
                for mod in m.modifiers:
                    try:
                        if mod.type == 'ARMATURE' and mod.object == a and m not in sel_objs:
                            extra.append(m)
                    except Exception:
                        pass
        if extra:
            sel_objs.extend(extra)

        # Detectar armature de referencia y registrar datos del bone_id==0 (dirección y longitud en espacio mundial)
        def find_bone_by_id(arm_obj, target_id=0):
            """Buscar un bone por custom property 'bone_id' en un armature.
            Intenta varias formas de acceso y hace fallback a nombres comunes.
            """
            if arm_obj is None:
                return None

            def matches(val):
                try:
                    return float(val) == float(target_id)
                except Exception:
                    return False

            print(f"\nBuscando bone con bone_id={target_id} en armature {arm_obj.name}:")

            # Intentar data.bones
            try:
                for b in arm_obj.data.bones:
                    try:
                        # intento acceso directo como dict (la forma más común en custom props)
                        v = None
                        try:
                            v = b['bone_id']
                            print(f"  - {b.name}: tiene bone_id={v} (acceso directo)")
                        except Exception:
                            try:
                                v = b.get('bone_id', None)
                                if v is not None:
                                    print(f"  - {b.name}: tiene bone_id={v} (via get)")
                            except Exception:
                                v = None
                        if v is not None and matches(v):
                            print(f"  ✓ Encontrado bone_id={target_id} en: {b.name}")
                            return b.name
                    except Exception as e:
                        print(f"  ! Error accediendo bone {b.name}: {str(e)}")
            except Exception as e:
                print(f"  ! Error accediendo data.bones: {str(e)}")

            # Intentar pose.bones
            try:
                for pb in arm_obj.pose.bones:
                    try:
                        v = None
                        try:
                            v = pb['bone_id']
                        except Exception:
                            try:
                                v = pb.get('bone_id', None)
                            except Exception:
                                v = None
                        if v is not None and matches(v):
                            return pb.name
                    except Exception:
                        pass
                    try:
                        # algunos addons guardan la prop en pb.bone
                        if hasattr(pb, 'bone'):
                            v2 = None
                            try:
                                v2 = pb.bone['bone_id']
                            except Exception:
                                try:
                                    v2 = pb.bone.get('bone_id', None)
                                except Exception:
                                    v2 = None
                            if v2 is not None and matches(v2):
                                return pb.name
                    except Exception:
                        pass
            except Exception:
                pass

            # Fallback por nombre común
            try:
                for candidate in ('Root', 'root'):
                    if candidate in arm_obj.data.bones:
                        return candidate
            except Exception:
                pass

            return None
        # Si no encontramos, y queremos depurar, imprimir listado de bones y sus bone_id
        def debug_list_bone_ids(arm_obj):
            try:
                lines = []
                for b in arm_obj.data.bones:
                    try:
                        vid = b.get('bone_id', None)
                    except Exception:
                        try:
                            vid = b['bone_id'] if 'bone_id' in b else None
                        except Exception:
                            vid = None
                    lines.append(f"DATA_BONE: {b.name} -> bone_id={vid}")
                for pb in arm_obj.pose.bones:
                    try:
                        vid = pb.get('bone_id', None)
                    except Exception:
                        vid = None
                    lines.append(f"POSE_BONE: {pb.name} -> bone_id={vid}")
                # imprimir por consola y en report (no muy largo)
                for l in lines:
                    print(l)
                try:
                    # reporte corto
                    if len(lines) > 0:
                        bpy.ops.wm.console_toggle() if False else None
                except Exception:
                    pass
            except Exception:
                pass

        root_bone_name = None
        root_dir_world = None
        root_length_world = None
        root_head_world = None
        root_tail_world = None
        ref_armature = next((o for o in sel_objs if o.type == 'ARMATURE'), None)
        if ref_armature is None:
            ref_armature = next((o for o in context.scene.objects if o.type == 'ARMATURE'), None)
        if ref_armature is not None:
            # Buscar root bone por custom property 'bone_id' (valor 0)
            root_bone_name = find_bone_by_id(ref_armature, 0)
            # si lo encontramos, calcular dirección y longitud en espacio mundial
            if root_bone_name is not None:
                try:
                    pb = ref_armature.pose.bones[root_bone_name]
                    head_w = ref_armature.matrix_world @ pb.head
                    tail_w = ref_armature.matrix_world @ pb.tail
                    vec = tail_w - head_w
                    root_length_world = vec.length
                    if root_length_world > 0.0:
                        root_dir_world = vec.normalized()
                        root_head_world = head_w.copy()
                        root_tail_world = tail_w.copy()
                        # Debug: informar en consola que encontramos el bone y sus posiciones
                        try:
                            msg = f"root bone found: {root_bone_name}, head_world={root_head_world}, tail_world={root_tail_world}, length={root_length_world:.6f}"
                            print(msg)
                            self.report({'INFO'}, msg)
                        except Exception:
                            pass
                except Exception:
                    root_bone_name = None

        # elegir referencia mesh para calcular la altura actual
        ref_mesh = next((o for o in sel_objs if o.type == 'MESH'), None)
        if ref_mesh is None:
            # fallback a cualquier mesh en escena
            ref_mesh = next((o for o in context.scene.objects if o.type == 'MESH'), None)
        if ref_mesh is None:
            self.report({'ERROR'}, "No se encontró ninguna malla para medir la altura")
            return {'CANCELLED'}

        # Paso 2: colocar 3D cursor en X=0,Y=0,Z=-1
        cursor = context.scene.cursor
        cursor.location = (0.0, 0.0, -1.0)

        # Paso 3: calcular factor de escala (Z) usando la malla de referencia
        bbox_world = [ref_mesh.matrix_world @ Vector(corner) for corner in ref_mesh.bound_box]
        z_values = [v.z for v in bbox_world]
        current_height = max(z_values) - min(z_values)
        if current_height == 0:
            self.report({'ERROR'}, "Altura actual del mesh es cero; no se puede escalar")
            return {'CANCELLED'}

        scale_factor = height / current_height

        # Preparar lista de objetos a escalar: evitar doble-escala evitando hijos de otros seleccionados
        objs_to_scale = []
        sel_set = set(sel_objs)
        for o in sel_objs:
            # si algún ancestro está en la selección, saltar este objeto
            p = o.parent
            skip = False
            while p:
                if p in sel_set:
                    skip = True
                    break
                p = p.parent
            if not skip:
                objs_to_scale.append(o)

        # Guardar y desparentar sólo los objetos cuyos padres NO están en la selección
        parent_map = {}
        for o in sel_objs:
            if o.parent is not None and o.parent not in sel_set:
                parent_map[o] = o.parent
                wm = o.matrix_world.copy()
                o.parent = None
                o.matrix_world = wm

        # Aplicar escala a los objetos top-level calculados
        prev_active = context.view_layer.objects.active
        prev_selected = [o for o in context.selected_objects]

        try:
            bpy.ops.object.select_all(action='DESELECT')

            # Determinar armature de referencia (si existe) para el ajuste de hueso
            ref_armature = next((o for o in sel_objs if o.type == 'ARMATURE'), None)
            if ref_armature is None:
                ref_armature = next((o for o in context.scene.objects if o.type == 'ARMATURE'), None)

            cursor_loc = context.scene.cursor.location.copy()
            scale_mat = Matrix.Translation(cursor_loc) @ Matrix.Scale(scale_factor, 4) @ Matrix.Translation(-cursor_loc)

            # Aplicar la matriz de escala a cada objeto top-level preparado
            for obj in objs_to_scale:
                obj.matrix_world = scale_mat @ obj.matrix_world

            # Paso 4: aplicar todas las transformaciones a los objetos modificados
            for obj in objs_to_scale:
                context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                obj.select_set(False)

            # Después de las transformaciones parciales, aplicar transform a TODOS los objetos
            # para garantizar que local/world transforms queden aplicados.
            # Asegurarse de estar en Object mode antes de operar.
            try:
                if bpy.ops.object.mode_set.poll():
                    bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass
            bpy.ops.object.select_all(action='SELECT')
            try:
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            except Exception:
                # En caso de que aplicar a algún tipo falle, continuar
                pass
            bpy.ops.object.select_all(action='DESELECT')

            # Paso 5: detectar hueso raíz mediante custom property bone_id == 0 en el armature de referencia
            root_bone_name = find_bone_by_id(ref_armature, 0) if ref_armature is not None else None
            if root_bone_name is None:
                self.report({'WARNING'}, "No se encontró hueso con custom property bone_id == 0 en el armature de referencia")
            else:
                # Paso 6: mover el hueso root al pivote (origin) del armature en espacio mundial
                bpy.ops.object.select_all(action='DESELECT')
                ref_armature.select_set(True)
                context.view_layer.objects.active = ref_armature
                bpy.ops.object.mode_set(mode='EDIT')
                eb = ref_armature.data.edit_bones.get(root_bone_name)
                if eb:
                    # Código simple y directo como en el script que funciona
                    try:
                        # Desconectar/desparentar primero
                        eb.use_connect = False
                        eb.parent = None
                        
                        # Mover directo al origin como en tu script
                        eb.head = Vector((0.0, 0.0, 0.0))
                        eb.tail = Vector((0.04, 0.0, 0.0))
                        
                        self.report({'INFO'}, "Root bone moved to origin (direct approach)")
                    except Exception as e:
                        self.report({'WARNING'}, f"Failed to move bone: {str(e)}")
                bpy.ops.object.mode_set(mode='OBJECT')

            # Restaurar padres originales (se ejecuta siempre)
            for o, p in parent_map.items():
                try:
                    if p is not None:
                        # conservar transform mundial
                        wm = o.matrix_world.copy()
                        o.parent = p
                        o.matrix_world = wm
                except Exception:
                    pass

        finally:
            # Restaurar selección
            bpy.ops.object.select_all(action='DESELECT')
            for o in prev_selected:
                o.select_set(True)
            context.view_layer.objects.active = prev_active

        self.report({'INFO'}, f"Altura aplicada: factor {scale_factor:.4f}")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(UNIVERSALGTA_OT_adjust_skin_height)


def unregister():
    bpy.utils.unregister_class(UNIVERSALGTA_OT_adjust_skin_height)
