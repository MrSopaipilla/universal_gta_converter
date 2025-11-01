"""
gta_sa_bones.py - Validador oficial de huesos GTA SA
Universal GTA SA Converter v4.0.1

HUESOS OFICIALES con espacios exactos preservados
"""

class GTASABones:
    """Clase con huesos oficiales GTA SA y utilidades de validación"""
    
    # LISTA OFICIAL - NO MODIFICAR ESPACIOS
    OFFICIAL_BONES = [
        "Root",
        " Pelvis",
        " Spine", 
        " Spine1",
        " Neck",
        " Head",
        "Jaw",
        "L Brow",
        "R Brow", 
        "Bip01 L Clavicle",
        " L UpperArm",
        " L ForeArm", 
        " L Hand",
        " L Finger",
        "L Finger01",
        "Bip01 R Clavicle",
        " R UpperArm",
        " R ForeArm",
        " R Hand", 
        " R Finger",
        "R Finger01",
        "L breast",
        "R breast",
        "Belly",
        " L Thigh",
        " L Calf",
        " L Foot",
        " L Toe0",
        " R Thigh", 
        " R Calf",
        " R Foot",
        " R Toe0"
    ]
    
    @classmethod
    def is_valid_bone(cls, bone_name):
        """Verificar si es hueso oficial GTA SA"""
        return bone_name in cls.OFFICIAL_BONES
    
    @classmethod
    def normalize_bone(cls, bone_name):
        """Normalizar nombre a oficial (preservando espacios)"""
        if not bone_name:
            return None
        
        # Ya es oficial
        if bone_name in cls.OFFICIAL_BONES:
            return bone_name
        
        # Buscar versión con espacios correctos
        clean_input = bone_name.strip()
        for official in cls.OFFICIAL_BONES:
            if official.strip() == clean_input:
                return official
        
        # Mapeos específicos conocidos
        mappings = {
            "Pelvis": " Pelvis",
            "pelvis": " Pelvis",
            "Hip": " Pelvis", 
            "Hips": " Pelvis",
            "Spine": " Spine",
            "spine": " Spine", 
            "Spine1": " Spine1",
            "spine1": " Spine1",
            "Chest": " Spine1",
            "Neck": " Neck",
            "neck": " Neck",
            "Head": " Head", 
            "head": " Head",
            "L UpperArm": " L UpperArm",
            "L_UpperArm": " L UpperArm",
            "UpperArm.L": " L UpperArm",
            "L ForeArm": " L ForeArm",
            "L_ForeArm": " L ForeArm", 
            "ForeArm.L": " L ForeArm",
            "L Hand": " L Hand",
            "L_Hand": " L Hand",
            "Hand.L": " L Hand",
            "L Thigh": " L Thigh",
            "L_Thigh": " L Thigh",
            "Thigh.L": " L Thigh",
            "L Calf": " L Calf",
            "L_Calf": " L Calf",
            "Calf.L": " L Calf",
            "L Foot": " L Foot",
            "L_Foot": " L Foot", 
            "Foot.L": " L Foot",
            "L Toe0": " L Toe0",
            "L_Toe0": " L Toe0",
            "Toe.L": " L Toe0",
            # Versiones derechas
            "R UpperArm": " R UpperArm",
            "R_UpperArm": " R UpperArm",
            "UpperArm.R": " R UpperArm",
            "R ForeArm": " R ForeArm",
            "R_ForeArm": " R ForeArm",
            "ForeArm.R": " R ForeArm", 
            "R Hand": " R Hand",
            "R_Hand": " R Hand",
            "Hand.R": " R Hand",
            "R Thigh": " R Thigh",
            "R_Thigh": " R Thigh", 
            "Thigh.R": " R Thigh",
            "R Calf": " R Calf",
            "R_Calf": " R Calf",
            "Calf.R": " R Calf",
            "R Foot": " R Foot",
            "R_Foot": " R Foot",
            "Foot.R": " R Foot", 
            "R Toe0": " R Toe0",
            "R_Toe0": " R Toe0",
            "Toe.R": " R Toe0",
        }
        
        # Buscar en mapeos case-insensitive
        for variant, official in mappings.items():
            if bone_name.lower() == variant.lower():
                return official
        
        return None  # No se pudo normalizar
    
    @classmethod
    def get_invalid_bones(cls, bone_list):
        """Obtener huesos inválidos de una lista"""
        return [bone for bone in bone_list if not cls.is_valid_bone(bone)]
    
    @classmethod
    def validate_mapping_dict(cls, mapping_dict):
        """Validar diccionario de mapeos y corregir targets"""
        corrected = {}
        issues = []
        
        for source, target in mapping_dict.items():
            normalized_target = cls.normalize_bone(target)
            
            if normalized_target:
                corrected[source] = normalized_target
                if normalized_target != target:
                    issues.append(f"Target corregido: '{target}' -> '{normalized_target}'")
            else:
                corrected[source] = target  # Mantener original si no se puede corregir
                issues.append(f"Target no reconocido: '{target}'")
        
        return corrected, issues
    
    @classmethod
    def print_official_bones(cls):
        """Imprimir lista oficial para debug"""
        print("HUESOS OFICIALES GTA SA:")
        print("-" * 40)
        for i, bone in enumerate(cls.OFFICIAL_BONES, 1):
            print(f"{i:2d}. \"{bone}\"")
        print(f"\nTotal: {len(cls.OFFICIAL_BONES)} huesos")

if __name__ == "__main__":
    # Test del módulo
    GTASABones.print_official_bones()
    
    # Pruebas de normalización
    test_bones = ["Pelvis", "L UpperArm", "UpperArm.L", "invalid_bone"]
    print("\nPRUEBAS DE NORMALIZACIÓN:")
    for bone in test_bones:
        normalized = GTASABones.normalize_bone(bone)
        print(f"'{bone}' -> '{normalized}'")
