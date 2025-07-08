"""
Operador de referencia para mostrar los nombres exactos de huesos de GTA SA
"""

import bpy
from bpy.types import Operator


class UNIVERSALGTA_OT_show_gta_bone_reference(Operator):
    """Mostrar referencia de nombres de huesos de GTA SA"""
    bl_idname = "universalgta.show_gta_bone_reference"
    bl_label = "GTA SA Bone Reference"
    bl_description = "Muestra los nombres exactos de los huesos de GTA SA"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        # Mostrar en consola los nombres exactos
        bone_reference = self.get_gta_sa_bone_names()
        
        print("\n" + "="*50)
        print("REFERENCIA DE HUESOS GTA SAN ANDREAS")
        print("="*50)
        
        for category, bones in bone_reference.items():
            print(f"\n{category.upper()}:")
            for bone in bones:
                print(f"  - {bone}")
        
        print("\n" + "="*50)
        print("NOTAS IMPORTANTES:")
        print("- Los huesos con espacios usan exactamente esos nombres")
        print("- Los huesos sin espacios (Pelvis, belly, breast) no usan espacios")
        print("- Root siempre se excluye automáticamente")
        print("="*50 + "\n")
        
        self.report({'INFO'}, "Referencia de huesos GTA SA mostrada en consola")
        return {'FINISHED'}
    
    def get_gta_sa_bone_names(self):
        """Retorna los nombres exactos de los huesos de GTA SA organizados por categoría"""
        return {
            "columna_vertebral": [
                "Pelvis",      # Sin espacio al inicio
                " Spine",      # CON espacio al inicio
                " Spine1",     # CON espacio al inicio
                " Neck",       # CON espacio al inicio
                " Head"        # CON espacio al inicio
            ],
            "brazo_izquierdo": [
                "Bip01 L Clavicle",  # Sin espacio al inicio
                " L UpperArm",       # CON espacio al inicio
                " L ForeArm",        # CON espacio al inicio (y es ForeArm, no Forearm)
                " L Hand",           # CON espacio al inicio
                " L Finger",         # CON espacio al inicio
                "L Finger01"         # Sin espacio al inicio
            ],
            "brazo_derecho": [
                "Bip01 R Clavicle",  # Sin espacio al inicio
                " R UpperArm",       # CON espacio al inicio
                " R ForeArm",        # CON espacio al inicio (y es ForeArm, no Forearm)
                " R Hand",           # CON espacio al inicio
                " R Finger",         # CON espacio al inicio
                "R Finger01"         # Sin espacio al inicio
            ],
            "pierna_izquierda": [
                " L Thigh",          # CON espacio al inicio
                " L Calf",           # CON espacio al inicio
                " L Foot",           # CON espacio al inicio
                " L Toe0"            # CON espacio al inicio
            ],
            "pierna_derecha": [
                " R Thigh",          # CON espacio al inicio
                " R Calf",           # CON espacio al inicio
                " R Foot",           # CON espacio al inicio
                " R Toe0"            # CON espacio al inicio
            ],
            "facial": [
                "Jaw",               # Sin espacio al inicio
                "L Brow",            # Sin espacio al inicio
                "R Brow"             # Sin espacio al inicio
            ],
            "cuerpo_especial": [
                "L breast",          # Sin espacio al inicio
                "R breast",          # Sin espacio al inicio
                "Belly"              # Sin espacio al inicio
            ],
            "excluidos": [
                "Root"               # SIEMPRE excluido
            ]
        }",          # SIN espacio entre R y breast
                "Belly"              # Sin espacio, con B mayúscula
            ],
            "excluidos": [
                "Root"               # SIEMPRE excluido
            ]
        }


class UNIVERSALGTA_OT_create_gta_armature_template(Operator):
    """Crear un armature template con los nombres exactos de GTA SA"""
    bl_idname = "universalgta.create_gta_armature_template"
    bl_label = "Create GTA Template"
    bl_description = "Crea un armature con los nombres exactos de huesos de GTA SA"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            # Crear nuevo armature
            bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
            armature_obj = context.active_object
            armature_obj.name = "GTA_SA_Template"
            armature_obj.data.name = "GTA_SA_Template"
            
            # Limpiar hueso por defecto
            bpy.ops.armature.select_all(action='SELECT')
            bpy.ops.armature.delete()
            
            # Crear estructura de huesos básica
            bone_structure = self._get_basic_bone_structure()
            created_bones = {}
            
            # Crear huesos
            for bone_name, bone_info in bone_structure.items():
                bone = armature_obj.data.edit_bones.new(bone_name)
                bone.head = bone_info['head']
                bone.tail = bone_info['tail']
                created_bones[bone_name] = bone
            
            # Establecer relaciones padre-hijo
            for bone_name, bone_info in bone_structure.items():
                if 'parent' in bone_info and bone_info['parent']:
                    parent_name = bone_info['parent']
                    if parent_name in created_bones:
                        created_bones[bone_name].parent = created_bones[parent_name]
            
            # Volver a modo objeto
            bpy.ops.object.mode_set(mode='OBJECT')
            
            self.report({'INFO'}, f"Template GTA SA creado: {armature_obj.name}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error creando template: {str(e)}")
            return {'CANCELLED'}
    
    def _get_basic_bone_structure(self):
        """Define la estructura básica de huesos de GTA SA con posiciones y nombres EXACTOS"""
        return {
            # Columna vertebral (algunos con espacio al inicio, otros sin)
            "Pelvis": {
                'head': (0.0, 0.0, 0.0),
                'tail': (0.0, 0.0, 0.1),
                'parent': None
            },
            " Spine": {  # CON espacio al inicio
                'head': (0.0, 0.0, 0.1),
                'tail': (0.0, 0.0, 0.3),
                'parent': "Pelvis"
            },
            " Spine1": {  # CON espacio al inicio
                'head': (0.0, 0.0, 0.3),
                'tail': (0.0, 0.0, 0.5),
                'parent': " Spine"
            },
            " Neck": {  # CON espacio al inicio
                'head': (0.0, 0.0, 0.5),
                'tail': (0.0, 0.0, 0.6),
                'parent': " Spine1"
            },
            " Head": {  # CON espacio al inicio
                'head': (0.0, 0.0, 0.6),
                'tail': (0.0, 0.0, 0.8),
                'parent': " Neck"
            },
            
            # Brazo izquierdo (nombres exactos)
            "Bip01 L Clavicle": {  # SIN espacio al inicio
                'head': (0.0, 0.0, 0.45),
                'tail': (0.2, 0.0, 0.45),
                'parent': " Spine1"
            },
            " L UpperArm": {  # CON espacio al inicio
                'head': (0.2, 0.0, 0.45),
                'tail': (0.5, 0.0, 0.45),
                'parent': "Bip01 L Clavicle"
            },
            " L ForeArm": {  # CON espacio al inicio, ForeArm (no Forearm)
                'head': (0.5, 0.0, 0.45),
                'tail': (0.8, 0.0, 0.45),
                'parent': " L UpperArm"
            },
            " L Hand": {  # CON espacio al inicio
                'head': (0.8, 0.0, 0.45),
                'tail': (0.9, 0.0, 0.45),
                'parent': " L ForeArm"
            },
            " L Finger": {  # CON espacio al inicio
                'head': (0.9, 0.0, 0.45),
                'tail': (0.95, 0.0, 0.45),
                'parent': " L Hand"
            },
            "L Finger01": {  # SIN espacio al inicio
                'head': (0.95, 0.0, 0.45),
                'tail': (1.0, 0.0, 0.45),
                'parent': " L Finger"
            },
            
            # Brazo derecho (nombres exactos)
            "Bip01 R Clavicle": {  # SIN espacio al inicio
                'head': (0.0, 0.0, 0.45),
                'tail': (-0.2, 0.0, 0.45),
                'parent': " Spine1"
            },
            " R UpperArm": {  # CON espacio al inicio
                'head': (-0.2, 0.0, 0.45),
                'tail': (-0.5, 0.0, 0.45),
                'parent': "Bip01 R Clavicle"
            },
            " R ForeArm": {  # CON espacio al inicio, ForeArm (no Forearm)
                'head': (-0.5, 0.0, 0.45),
                'tail': (-0.8, 0.0, 0.45),
                'parent': " R UpperArm"
            },
            " R Hand": {  # CON espacio al inicio
                'head': (-0.8, 0.0, 0.45),
                'tail': (-0.9, 0.0, 0.45),
                'parent': " R ForeArm"
            },
            " R Finger": {  # CON espacio al inicio
                'head': (-0.9, 0.0, 0.45),
                'tail': (-0.95, 0.0, 0.45),
                'parent': " R Hand"
            },
            "R Finger01": {  # SIN espacio al inicio
                'head': (-0.95, 0.0, 0.45),
                'tail': (-1.0, 0.0, 0.45),
                'parent': " R Finger"
            },
            
            # Piernas izquierdas (CON espacios al inicio)
            " L Thigh": {  # CON espacio al inicio
                'head': (0.1, 0.0, 0.0),
                'tail': (0.1, 0.0, -0.4),
                'parent': "Pelvis"
            },
            " L Calf": {  # CON espacio al inicio
                'head': (0.1, 0.0, -0.4),
                'tail': (0.1, 0.0, -0.8),
                'parent': " L Thigh"
            },
            " L Foot": {  # CON espacio al inicio
                'head': (0.1, 0.0, -0.8),
                'tail': (0.1, 0.2, -0.8),
                'parent': " L Calf"
            },
            " L Toe0": {  # CON espacio al inicio
                'head': (0.1, 0.2, -0.8),
                'tail': (0.1, 0.25, -0.8),
                'parent': " L Foot"
            },
            
            # Piernas derechas (CON espacios al inicio)
            " R Thigh": {  # CON espacio al inicio
                'head': (-0.1, 0.0, 0.0),
                'tail': (-0.1, 0.0, -0.4),
                'parent': "Pelvis"
            },
            " R Calf": {  # CON espacio al inicio
                'head': (-0.1, 0.0, -0.4),
                'tail': (-0.1, 0.0, -0.8),
                'parent': " R Thigh"
            },
            " R Foot": {  # CON espacio al inicio
                'head': (-0.1, 0.0, -0.8),
                'tail': (-0.1, 0.2, -0.8),
                'parent': " R Calf"
            },
            " R Toe0": {  # CON espacio al inicio
                'head': (-0.1, 0.2, -0.8),
                'tail': (-0.1, 0.25, -0.8),
                'parent': " R Foot"
            },
            
            # Facial (SIN espacios al inicio)
            "Jaw": {  # SIN espacio al inicio
                'head': (0.0, 0.05, 0.75),
                'tail': (0.0, 0.08, 0.75),
                'parent': " Head"
            },
            "L Brow": {  # SIN espacio al inicio
                'head': (0.05, 0.08, 0.77),
                'tail': (0.05, 0.1, 0.77),
                'parent': " Head"
            },
            "R Brow": {  # SIN espacio al inicio
                'head': (-0.05, 0.08, 0.77),
                'tail': (-0.05, 0.1, 0.77),
                'parent': " Head"
            },
            
            # Cuerpo especial (SIN espacios al inicio)
            "L breast": {  # SIN espacio al inicio
                'head': (0.08, 0.05, 0.35),
                'tail': (0.08, 0.1, 0.35),
                'parent': " Spine1"
            },
            "R breast": {  # SIN espacio al inicio
                'head': (-0.08, 0.05, 0.35),
                'tail': (-0.08, 0.1, 0.35),
                'parent': " Spine1"
            },
            "Belly": {  # SIN espacio al inicio
                'head': (0.0, 0.05, 0.2),
                'tail': (0.0, 0.1, 0.2),
                'parent': " Spine"
            }
        }head': (0.0, 0.0, 0.6),
                'tail': (-0.2, 0.0, 0.6),
                'parent': "Spine2"
            },
            "R UpperArm": {
                'head': (-0.2, 0.0, 0.6),
                'tail': (-0.5, 0.0, 0.6),
                'parent': "Bip01 R Clavicle"
            },
            "R Forearm": {
                'head': (-0.5, 0.0, 0.6),
                'tail': (-0.8, 0.0, 0.6),
                'parent': "R UpperArm"
            },
            "R Hand": {
                'head': (-0.8, 0.0, 0.6),
                'tail': (-0.9, 0.0, 0.6),
                'parent': "R Forearm"
            },
            "R Finger": {
                'head': (-0.9, 0.0, 0.6),
                'tail': (-0.95, 0.0, 0.6),
                'parent': "R Hand"
            },
            "R Finger1": {
                'head': (-0.95, 0.0, 0.6),
                'tail': (-0.97, 0.0, 0.6),
                'parent': "R Finger"
            },
            "R Finger01": {
                'head': (-0.97, 0.0, 0.6),
                'tail': (-1.0, 0.0, 0.6),
                'parent': "R Finger1"
            },
            
            # Pierna izquierda (nombres exactos con espacios)
            "L Thigh": {
                'head': (0.1, 0.0, 0.0),
                'tail': (0.1, 0.0, -0.4),
                'parent': "Pelvis"
            },
            "L Calf": {
                'head': (0.1, 0.0, -0.4),
                'tail': (0.1, 0.0, -0.8),
                'parent': "L Thigh"
            },
            "L Foot": {
                'head': (0.1, 0.0, -0.8),
                'tail': (0.1, 0.2, -0.8),
                'parent': "L Calf"
            },
            "L Toe0": {
                'head': (0.1, 0.2, -0.8),
                'tail': (0.1, 0.25, -0.8),
                'parent': "L Foot"
            },
            
            # Pierna derecha (nombres exactos con espacios)
            "R Thigh": {
                'head': (-0.1, 0.0, 0.0),
                'tail': (-0.1, 0.0, -0.4),
                'parent': "Pelvis"
            },
            "R Calf": {
                'head': (-0.1, 0.0, -0.4),
                'tail': (-0.1, 0.0, -0.8),
                'parent': "R Thigh"
            },
            "R Foot": {
                'head': (-0.1, 0.0, -0.8),
                'tail': (-0.1, 0.2, -0.8),
                'parent': "R Calf"
            },
            "R Toe0": {
                'head': (-0.1, 0.2, -0.8),
                'tail': (-0.1, 0.25, -0.8),
                'parent': "R Foot"
            },
            
            # Facial (nombres exactos con espacios)
            "L Brow": {
                'head': (0.05, 0.08, 0.95),
                'tail': (0.05, 0.1, 0.95),
                'parent': "Head"
            },
            "R Brow": {
                'head': (-0.05, 0.08, 0.95),
                'tail': (-0.05, 0.1, 0.95),
                'parent': "Head"
            },
            "Jaw": {
                'head': (0.0, 0.05, 0.85),
                'tail': (0.0, 0.08, 0.85),
                'parent': "Head"
            },
            
            # Cuerpo especial (nombres exactos - sin espacios)
            "L breast": {
                'head': (0.08, 0.05, 0.45),
                'tail': (0.08, 0.1, 0.45),
                'parent': "Spine1"
            },
            "R breast": {
                'head': (-0.08, 0.05, 0.45),
                'tail': (-0.08, 0.1, 0.45),
                'parent': "Spine1"
            },
            "Belly": {
                'head': (0.0, 0.05, 0.2),
                'tail': (0.0, 0.1, 0.2),
                'parent': "Spine"
            }
        }                'tail': (0.05, 0.1, 0.95),
                'parent': "Head"
            },
            "R Brow": {
                'head': (-0.05, 0.08, 0.95),
                'tail': (-0.05, 0.1, 0.95),
                'parent': "Head"
            },
            "Jaw": {
                'head': (0.0, 0.05, 0.85),
                'tail': (0.0, 0.08, 0.85),
                'parent': "Head"
            },
            
            # Cuerpo especial (nombres exactos - sin espacios)
            "L breast": {
                'head': (0.08, 0.05, 0.45),
                'tail': (0.08, 0.1, 0.45),
                'parent': "Spine1"
            },
            "R breast": {
                'head': (-0.08, 0.05, 0.45),
                'tail': (-0.08, 0.1, 0.45),
                'parent': "Spine1"
            },
            "Belly": {
                'head': (0.0, 0.05, 0.2),
                'tail': (0.0, 0.1, 0.2),
                'parent': "Spine"
            }
        }


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_show_gta_bone_reference,
    UNIVERSALGTA_OT_create_gta_armature_template,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
