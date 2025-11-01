import bpy  # type: ignore
from bpy.props import FloatProperty  # type: ignore
from bpy.types import Operator  # type: ignore
import math

def register_properties():
    bpy.types.Scene.gta_arm_angle = FloatProperty(
        name="Arm Angle",
        description="Ángulo de rotación para los brazos (+ derecho, - izquierdo)",
        default=0.0,
        min=-360.0,
        max=360.0,
        subtype='ANGLE'
    )

def unregister_properties():
    if hasattr(bpy.types.Scene, "gta_arm_angle"):
        del bpy.types.Scene.gta_arm_angle

class UNIVERSALGTA_OT_set_arm_angles(Operator):
    bl_idname = "universalgta.set_arm_angles"
    bl_label = "Set Arm Angles"
    bl_description = "Aplica el ángulo de rotación a los brazos"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Obtener el armature desde settings
        settings = context.scene.universal_gta_settings
        armature = settings.target_armature
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Por favor selecciona un armature")
            return {'CANCELLED'}

        original_mode = armature.mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        edit_bones = armature.data.edit_bones
        l_upper_arm = edit_bones.get(" L UpperArm")
        r_upper_arm = edit_bones.get(" R UpperArm")
        
        if not (l_upper_arm and r_upper_arm):
            self.report({'ERROR'}, "Esqueleto GTA SA no encontrado")
            bpy.ops.object.mode_set(mode=original_mode)
            return {'CANCELLED'}
        
        scene = context.scene
        if not getattr(scene, 'gta_arm_roll_has_base', False):
            scene.gta_arm_roll_base_left = math.degrees(l_upper_arm.roll)
            scene.gta_arm_roll_base_right = math.degrees(r_upper_arm.roll)
            scene.gta_arm_roll_has_base = True
        base_left = scene.gta_arm_roll_base_left
        base_right = scene.gta_arm_roll_base_right
        
        angle = context.scene.gta_arm_angle
        
        l_upper_arm.roll = math.radians(base_left + angle)
        r_upper_arm.roll = math.radians(base_right - angle)
        
        bpy.ops.object.mode_set(mode=original_mode)
        
        return {'FINISHED'}

classes = (UNIVERSALGTA_OT_set_arm_angles,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_properties()

def unregister():
    unregister_properties()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
