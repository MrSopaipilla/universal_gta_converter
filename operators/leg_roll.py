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

        offset = context.scene.gta_leg_roll_angle
        
        # Valores de referencia GTA SA (Asimetria natural)
        ref_left = -14.2734
        ref_right = -148.123

        # Aplicar offset simetricamente (invertido para R para mantener simetria visual de la operacion)
        bone_names = {
            ' L Thigh': ref_left + offset,
            ' R Thigh': ref_right - offset
        }

        edit_bones = armature.data.edit_bones
        bones_modified = 0

        armature.data.update_tag()
        context.view_layer.update()

        for name, roll_angle in bone_names.items():
            if name in edit_bones:
                bone = edit_bones[name]
                try:
                    bone.roll = math.radians(roll_angle)
                    bones_modified += 1
                except Exception as e:
                    print(f"[LEG ROLL] Error en {name}: {e}")
        
        armature.data.update_tag()
        context.view_layer.update()

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
