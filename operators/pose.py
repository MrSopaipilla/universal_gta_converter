"""
Operadores de pose para GTA SA
operators/pose.py - Universal GTA SA Converter v4.0.1
Aplicar pose personalizada
Reset pose
Copy pose
Integracion con external_pose_caller
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty


class UNIVERSALGTA_OT_apply_custom_pose(Operator):
    """Aplicar pose personalizada al armature"""
    bl_idname = "universalgta.apply_custom_pose"
    bl_label = "Apply Custom Pose"
    bl_description = "Aplica la nueva pose personalizada al modelo base"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:

            # Asegurar que estamos en modo OBJECT antes de cualquier operación de selección
            if context.object and context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Obtener configuración
            settings = getattr(context.scene, 'universal_gta_settings', None)
            target_armature = None
            
            # Intentar obtener armature desde settings
            if settings and settings.target_armature:
                target_armature = settings.target_armature
            
            # Fallback: Buscar por nombre si no está en settings
            if not target_armature:
                for obj in bpy.data.objects:
                    if obj.type == 'ARMATURE' and 'Root' in obj.name:
                        target_armature = obj
                        break
            
            if not target_armature:
                self.report({'ERROR'}, "No se encontró armature target (configure 'Target Armature' en el panel o use un armature con 'Root' en el nombre)")
                return {'CANCELLED'}

            print(f"[POSE] Target Armature: {target_armature.name}")
            
            # Buscamos mallas que tengan modificador Armature apuntando a este target
            meshes_to_process = []
            
            # Recorrer todos los objetos mesh
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    modifiers_to_apply = []
                    for mod in obj.modifiers:
                        if mod.type == 'ARMATURE' and mod.object == target_armature:
                            modifiers_to_apply.append(mod.name)
                    
                    if modifiers_to_apply:
                        meshes_to_process.append((obj, modifiers_to_apply))

            if not meshes_to_process:
                self.report({'WARNING'}, "No se encontraron mallas con modificador Armature apuntando al target")
            
            # Aplicar modificadores en las mallas encontradas
            for obj, mod_names in meshes_to_process:
                # Deseleccionar todo y seleccionar solo el objeto actual
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
                
                # Aplicar modificadores (en orden inverso por seguridad)
                for mod_name in reversed(mod_names):
                    try:
                        bpy.ops.object.modifier_apply(modifier=mod_name)
                        print(f"[POSE] Modificador '{mod_name}' aplicado en '{obj.name}'")
                    except Exception as e:
                        print(f"[POSE] Error aplicando modificador '{mod_name}' en '{obj.name}': {e}")
            

            try:
                bpy.ops.object.select_all(action='DESELECT')
                target_armature.select_set(True)
                context.view_layer.objects.active = target_armature
                
                bpy.ops.object.mode_set(mode='POSE')
                # Seleccionar todos los huesos para aplicar la pose
                bpy.ops.pose.select_all(action='SELECT')
                bpy.ops.pose.armature_apply(selected=False)
                bpy.ops.object.mode_set(mode='OBJECT')
                
                print(f"[POSE] Pose aplicada como Rest Pose en '{target_armature.name}'")
            except Exception as e:
                self.report({'ERROR'}, f"Error aplicando pose al armature: {e}")
                import traceback
                traceback.print_exc()
                # Intentar recuperar modo objeto
                if context.object and context.object.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
            

            modifiers_created = 0
            for obj, _ in meshes_to_process:
                try:
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    context.view_layer.objects.active = obj
                    
                    # Crear nuevo modificador
                    new_mod = obj.modifiers.new(name="Armature", type='ARMATURE')
                    new_mod.object = target_armature
                    new_mod.use_vertex_groups = True
                    modifiers_created += 1
                    print(f"[POSE] Nuevo modificador Armature creado en '{obj.name}'")
                    
                except Exception as e:
                    print(f"[POSE] Error recreando modificador en '{obj.name}': {e}")
            
            self.report({'INFO'}, f"Proceso completado. {modifiers_created} modificadores recreados.")
            return {'FINISHED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error crítico aplicando pose: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
    
    def apply_basic_pose(self, armature):
        """Aplicar pose basica si external_pose_caller falla"""
        try:
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            
            # Pose basica para GTA SA
            basic_rotations = {
                'L UpperArm': (0, 0, -0.2),
                'R UpperArm': (0, 0, 0.2),
                'L ForeArm': (0, 0, 0.3),
                'R ForeArm': (0, 0, -0.3),
            }
            
            for bone_name, rotation in basic_rotations.items():
                if bone_name in armature.pose.bones:
                    bone = armature.pose.bones[bone_name]
                    bone.rotation_euler = rotation
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
        except Exception as e:
            print(f"Error en pose basica: {e}")


class UNIVERSALGTA_OT_reset_pose(Operator):
    """Reset pose del armature"""
    bl_idname = "universalgta.reset_pose"
    bl_label = "Reset Pose"
    bl_description = "Resetea la pose del armature a la posicion rest"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            # Buscar armature
            armature = None
            for obj in bpy.context.selected_objects:
                if obj.type == 'ARMATURE':
                    armature = obj
                    break
            
            if not armature:
                for obj in bpy.data.objects:
                    if obj.type == 'ARMATURE':
                        armature = obj
                        break
            
            if not armature:
                self.report({'ERROR'}, "No se encontro armature")
                return {'CANCELLED'}
            
            # Reset pose
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.loc_clear()
            bpy.ops.pose.scale_clear()
            bpy.ops.object.mode_set(mode='OBJECT')
            
            self.report({'INFO'}, "Pose reseteada")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error reseteando pose: {e}")
            return {'CANCELLED'}


class UNIVERSALGTA_OT_copy_pose(Operator):
    """Copiar pose entre armatures"""
    bl_idname = "universalgta.copy_pose"
    bl_label = "Copy Pose"
    bl_description = "Copia la pose de un armature a otro"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            selected_objects = bpy.context.selected_objects
            armatures = [obj for obj in selected_objects if obj.type == 'ARMATURE']
            
            if len(armatures) < 2:
                self.report({'ERROR'}, "Selecciona al menos 2 armatures")
                return {'CANCELLED'}
            
            source_armature = armatures[0]
            target_armature = armatures[1]
            
            self.copy_pose_between_armatures(source_armature, target_armature)
            
            self.report({'INFO'}, f"Pose copiada de {source_armature.name} a {target_armature.name}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error copiando pose: {e}")
            return {'CANCELLED'}
    
    def copy_pose_between_armatures(self, source, target):
        """Copiar pose entre dos armatures"""
        try:
            # Mapeo de huesos comun
            bone_mapping = {
                'Root': 'Root',
                'Pelvis': 'Pelvis', 
                'Spine': 'Spine',
                'Spine1': 'Spine1',
                'Neck': 'Neck',
                'Head': 'Head',
                'L UpperArm': 'L UpperArm',
                'R UpperArm': 'R UpperArm',
                'L ForeArm': 'L ForeArm', 
                'R ForeArm': 'R ForeArm',
                'L Hand': 'L Hand',
                'R Hand': 'R Hand',
                'L Thigh': 'L Thigh',
                'R Thigh': 'R Thigh',
                'L Calf': 'L Calf',
                'R Calf': 'R Calf',
                'L Foot': 'L Foot',
                'R Foot': 'R Foot',
            }
            
            # Establecer target como activo
            bpy.context.view_layer.objects.active = target
            bpy.ops.object.mode_set(mode='POSE')
            
            for source_bone_name, target_bone_name in bone_mapping.items():
                try:
                    if (source_bone_name in source.pose.bones and 
                        target_bone_name in target.pose.bones):
                        
                        source_bone = source.pose.bones[source_bone_name]
                        target_bone = target.pose.bones[target_bone_name]
                        
                        # Copiar transformaciones
                        target_bone.rotation_euler = source_bone.rotation_euler.copy()
                        target_bone.location = source_bone.location.copy()
                        target_bone.scale = source_bone.scale.copy()
                        
                except Exception:
                    continue
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
        except Exception as e:
            print(f"Error copiando pose: {e}")


class UNIVERSALGTA_OT_apply_constraints(Operator):
    """Aplicar constraints COPY_LOCATION automaticos para GTA SA"""
    bl_idname = "universalgta.apply_constraints"
    bl_label = "Apply COPY_LOCATION Constraints"
    bl_description = "Aplica constraints COPY_LOCATION optimizados para sincronizacion GTA SA"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            # Buscar armature target
            target_armature = None
            for obj in bpy.data.objects:
                if obj.type == 'ARMATURE' and 'Root' in obj.name:
                    target_armature = obj
                    break
            
            if not target_armature:
                self.report({'ERROR'}, "No se encontro armature target")
                return {'CANCELLED'}
            
            constraints_applied = self.apply_copy_location_constraints(target_armature)
            
            self.report({'INFO'}, f"{constraints_applied} COPY_LOCATION constraints aplicados")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error aplicando constraints: {e}")
            return {'CANCELLED'}
    
    def apply_copy_location_constraints(self, armature):
        """Aplicar constraints COPY_LOCATION especificos para GTA SA"""
        try:
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            
            # Constraints COPY_LOCATION para sincronizacion GTA SA
            copy_location_setup = {
                # Columna vertebral - sincronizacion jerarquica
                'Spine1': 'Spine',      # Spine1 sigue a Spine
                'Neck': 'Spine1',       # Neck sigue a Spine1  
                'Head': 'Neck',         # Head sigue a Neck
                
                # Brazos izquierdos - cadena de sincronizacion
                'L UpperArm': 'Bip01 L Clavicle',  # UpperArm sigue a Clavicle
                'L ForeArm': 'L UpperArm',         # ForeArm sigue a UpperArm
                'L Hand': 'L ForeArm',             # Hand sigue a ForeArm
                
                # Brazos derechos - cadena de sincronizacion
                'R UpperArm': 'Bip01 R Clavicle',  # UpperArm sigue a Clavicle
                'R ForeArm': 'R UpperArm',         # ForeArm sigue a UpperArm  
                'R Hand': 'R ForeArm',             # Hand sigue a ForeArm
                
                # Piernas izquierdas - cadena de sincronizacion
                'L Calf': 'L Thigh',    # Calf sigue a Thigh
                'L Foot': 'L Calf',     # Foot sigue a Calf
                'L Toe0': 'L Foot',     # Toe sigue a Foot
                
                # Piernas derechas - cadena de sincronizacion
                'R Calf': 'R Thigh',    # Calf sigue a Thigh
                'R Foot': 'R Calf',     # Foot sigue a Calf
                'R Toe0': 'R Foot',     # Toe sigue a Foot
                
                # Dedos - sincronizacion
                'L Finger01': 'L Finger',  # Finger01 sigue a Finger
                'R Finger01': 'R Finger',  # Finger01 sigue a Finger
            }
            
            constraints_applied = 0
            
            for target_bone, source_bone in copy_location_setup.items():
                if (target_bone in armature.pose.bones and 
                    source_bone in armature.pose.bones):
                    
                    pose_bone = armature.pose.bones[target_bone]
                    
                    # Limpiar constraints existentes del mismo tipo
                    for constraint in pose_bone.constraints:
                        if constraint.name.startswith("GTA_SA_COPY_LOC"):
                            pose_bone.constraints.remove(constraint)
                    
                    try:
                        # Crear nuevo constraint COPY_LOCATION
                        constraint = pose_bone.constraints.new(type='COPY_LOCATION')
                        constraint.name = f"GTA_SA_COPY_LOC"
                        constraint.target = armature
                        constraint.subtarget = source_bone
                        
                        # Configurar propiedades optimizadas para GTA SA
                        constraint.use_x = True
                        constraint.use_y = True
                        constraint.use_z = True
                        constraint.invert_x = False
                        constraint.invert_y = False
                        constraint.invert_z = False
                        constraint.use_offset = False  # Sin offset para sincronizacion exacta
                        constraint.target_space = 'WORLD'
                        constraint.owner_space = 'WORLD'
                        constraint.influence = 1.0  # Influencia completa
                        
                        constraints_applied += 1
                        
                    except Exception:
                        continue
            
            bpy.ops.object.mode_set(mode='OBJECT')
            return constraints_applied
            
        except Exception:
            return 0


# Clases para registrar
classes = [
    UNIVERSALGTA_OT_apply_custom_pose,
    UNIVERSALGTA_OT_reset_pose,
    UNIVERSALGTA_OT_copy_pose,
    UNIVERSALGTA_OT_apply_constraints,
]


def register():
    """Registrar operadores de pose"""
    for cls in classes:
        bpy.utils.register_class(cls)
    print("[POSE] Operadores registrados")


def unregister():
    """Desregistrar operadores de pose"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)