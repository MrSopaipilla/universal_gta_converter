"""Operador para controlar el roll de las piernas en modo edición."""

import bpy  # type: ignore
from bpy.types import Operator  # type: ignore
import math
from mathutils import Matrix  # type: ignore

class UNIVERSALGTA_OT_apply_leg_roll(Operator):
    """Aplicar ángulo de roll a las piernas en modo edición"""
    bl_idname = "universalgta.apply_leg_roll"
    bl_label = "Apply Leg Roll"
    bl_description = "Aplicar ángulo de roll a L Thigh y R Thigh en modo edición"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.universal_gta_settings
        armature = settings.target_armature

        if not armature or armature.type != 'ARMATURE':
            self.report({'WARNING'}, "No se ha asignado un armature objetivo.")
            return {'CANCELLED'}

        # Activar el armature y entrar en modo edición
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')

        angle = context.scene.gta_leg_roll_angle
        
        # Valores de referencia solicitados para ángulo 0
        ref_left = -4.17456
        ref_right = 4.04106

        # Aplicar angle como offset sobre la base de referencia solicitada
        bone_rolls = {
            ' L Thigh': math.radians(ref_left) + (angle * 8.0),
            ' R Thigh': math.radians(ref_right) - (angle * 8.0)
        }

        edit_bones = armature.data.edit_bones
        bones_modified = 0

        for name, roll_val in bone_rolls.items():
            if name in edit_bones:
                bone = edit_bones[name]
                bone.roll = roll_val
                bones_modified += 1

        armature.data.update_tag()
        context.view_layer.update()
        
        armature.data.update_tag()
        context.view_layer.update()

        # Activar visualización de ejes en el armature
        if armature.data:
            armature.data.show_axes = True

        bpy.ops.object.mode_set(mode='OBJECT')

        if bones_modified > 0:
            self.report({'INFO'}, f"Roll angle aplicado a {bones_modified} huesos")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No se encontraron los huesos de las piernas")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(UNIVERSALGTA_OT_apply_leg_roll)

def unregister():
    bpy.utils.unregister_class(UNIVERSALGTA_OT_apply_leg_roll)

if __name__ == "__main__":
    register()
