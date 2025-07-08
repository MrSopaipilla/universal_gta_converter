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
                " Pelvis",      # SIN espacio
                " Spine",
                " Spine1", 
                " Spine2",
                " Neck",
                " Head"
            ],
            "brazo_izquierdo": [
                "Bip01 L Clavicle",  # CON espacio
                " L UpperArm",  # CON espacio
                " L Forearm",   # CON espacio
                " L Hand",      # CON espacio
                " L Finger",    # CON espacio
                "L Finger01"   # CON espacio
            ],
            "brazo_derecho": [
                "R Clavicle",  # CON espacio
                "R UpperArm",  # CON espacio
                "R Forearm",   # CON espacio
                "R Hand",      # CON espacio
                "R Finger",    # CON espacio
                "R Finger1",   # CON espacio
                "R Finger01"   # CON espacio
            ],
            "pierna_izquierda": [
                "L Thigh",     # CON espacio
                "L Calf",      # CON espacio
                "L Foot",      # CON espacio
                "L Toe0"       # CON espacio
            ],
            "pierna_derecha": [
                "R Thigh",     # CON espacio
                "R Calf",      # CON espacio
                "R Foot",      # CON espacio
                "R Toe0"       # CON espacio
            ],
            "facial": [
                "L Brow",      # CON espacio
                "R Brow",      # CON espacio
                "Jaw"
            ],
            "cuerpo_especial": [
                "L breast",    # SIN espacio entre L y breast
                "R breast",    # SIN espacio entre R y breast
                "Belly"        # SIN espacio
            ],
            "excluidos": [
                "Root"         # SIEMPRE excluido
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
        """Define la estructura básica de huesos de GTA SA con posiciones"""
        return {
            # Columna vertebral
            "Pelvis": {
                'head': (0.0, 0.0, 0.0),
                'tail': (0.0, 0.0, 0.1),
                'parent': None
            },
            "Spine": {
                'head': (0.0, 0.0, 0.1),
                'tail': (0.0, 0.0, 0.3),
                'parent': "Pelvis"
            },
            "Spine1": {
                'head': (0.0, 0.0, 0.3),
                'tail': (0.0, 0.0, 0.5),
                'parent': "Spine"
            },
            "Spine2": {
                'head': (0.0, 0.0, 0.5),
                'tail': (0.0, 0.0, 0.7),
                'parent': "Spine1"
            },
            "Neck": {
                'head': (0.0, 0.0, 0.7),
                'tail': (0.0, 0.0, 0.8),
                'parent': "Spine2"
            },
            "Head": {
                'head': (0.0, 0.0, 0.8),
                'tail': (0.0, 0.0, 1.0),
                'parent': "Neck"
            },
            
            # Brazo izquierdo (CON ESPACIOS)
            "L Clavicle": {
                'head': (0.0, 0.0, 0.6),
                'tail': (0.2, 0.0, 0.6),
                'parent': "Spine2"
            },
            "L UpperArm": {
                'head': (0.2, 0.0, 0.6),
                'tail': (0.5, 0.0, 0.6),
                'parent': "L Clavicle"
            },
            "L Forearm": {
                'head': (0.5, 0.0, 0.6),
                'tail': (0.8, 0.0, 0.6),
                'parent': "L UpperArm"
            },
            "L Hand": {
                'head': (0.8, 0.0, 0.6),
                'tail': (0.9, 0.0, 0.6),
                'parent': "L Forearm"
            },
            
            # Brazo derecho (CON ESPACIOS)
            "R Clavicle": {
                'head': (0.0, 0.0, 0.6),
                'tail': (-0.2, 0.0, 0.6),
                'parent': "Spine2"
            },
            "R UpperArm": {
                'head': (-0.2, 0.0, 0.6),
                'tail': (-0.5, 0.0, 0.6),
                'parent': "R Clavicle"
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
            
            # Pierna izquierda (CON ESPACIOS)
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
            
            # Pierna derecha (CON ESPACIOS)
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
            
            # Facial (CON ESPACIOS)
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
            
            # Especiales (SIN ESPACIOS - nombres exactos)
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
            "belly": {
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
