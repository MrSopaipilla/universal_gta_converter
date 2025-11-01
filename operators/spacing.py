"""Operadores de espaciado."""

import bpy  # type: ignore
from bpy.types import Operator  # type: ignore


class UNIVERSALGTA_OT_apply_spacing(Operator):
    """Aplicar espaciado de brazos y piernas al armature objetivo"""
    bl_idname = "universalgta.apply_spacing"
    bl_label = "Set Arm/Leg Spacing"
    bl_description = "Apply arm and leg spacing to the target armature"
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        armature = settings.target_armature
        if not armature or armature.type != 'ARMATURE':
            self.report({'WARNING'}, "No hay armature asignado.")
            return {'CANCELLED'}
        
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        def move_bone(name, offset):
            if name in armature.pose.bones:
                bone = armature.pose.bones[name]
                bone.location.x += offset
        
        move_bone("L UpperArm",  settings.arm_spacing)
        move_bone("R UpperArm", -settings.arm_spacing)
        move_bone("L Thigh",     settings.leg_spacing)
        move_bone("R Thigh",    -settings.leg_spacing)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.report({'INFO'}, "Espaciado aplicado correctamente.")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(UNIVERSALGTA_OT_apply_spacing)


def unregister():
    bpy.utils.unregister_class(UNIVERSALGTA_OT_apply_spacing)


if __name__ == "__main__":
    register()
