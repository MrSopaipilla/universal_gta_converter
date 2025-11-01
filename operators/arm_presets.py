import bpy
from bpy.types import Operator

class UNIVERSALGTA_OT_set_arm_preset_angles(Operator):
    """Aplica un ángulo predefinido a los brazos"""
    bl_idname = "universalgta.set_arm_preset_angles"
    bl_label = "Set Preset Arm Angle"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Obtener el armature activo
        armature = context.active_object
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Por favor selecciona un armature")
            return {'CANCELLED'}
            
        # Guardar el modo actual
        original_mode = armature.mode
        
        # Cambiar a modo edición
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Buscar los huesos
        edit_bones = armature.data.edit_bones
        l_upper_arm = edit_bones.get(" L UpperArm")
        r_upper_arm = edit_bones.get(" R UpperArm")
        
        if not (l_upper_arm and r_upper_arm):
            self.report({'ERROR'}, "Esqueleto GTA SA no encontrado")
            # Volver al modo original
            bpy.ops.object.mode_set(mode=original_mode)
            return {'CANCELLED'}
        
        # Aplicar las rotaciones predefinidas
        l_upper_arm.roll = 0.0
        r_upper_arm.roll = 0.0
        
        # Volver al modo original
        bpy.ops.object.mode_set(mode=original_mode)
        
        # Limpiar el valor del slider
        context.scene.gta_arm_angle = 0.0
        
        return {'FINISHED'}

# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_set_arm_preset_angles,
]

def register():
    """Registrar los operadores"""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Desregistrar los operadores"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
