"""
gta_sa_normalizer.py - Normalizador automático de huesos GTA SA
Utilizado para auto-corrección al cargar JSON
"""

class GTASANormalizer:
    """Normalizador robusto de huesos GTA SA con auto-corrección"""
    
    # LISTA OFICIAL GTA SA - ESPACIOS EXACTOS (32 huesos)
    OFFICIAL_GTA_SA_BONES = [
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
    
    # MAPEO COMPLETO DE VARIACIONES A NOMBRES OFICIALES
    BONE_VARIATIONS_MAP = {
        # Pelvis variations
        "Pelvis": " Pelvis",
        "pelvis": " Pelvis",
        "Hip": " Pelvis",
        "hip": " Pelvis",
        "Hips": " Pelvis",
        "hips": " Pelvis",
        "Root_Pelvis": " Pelvis",
        
        # Spine variations
        "Spine": " Spine",
        "spine": " Spine",
        "Back": " Spine",
        "back": " Spine",
        "Torso": " Spine",
        "torso": " Spine",
        
        # Spine1 variations
        "Spine1": " Spine1",
        "spine1": " Spine1",
        "Chest": " Spine1",
        "chest": " Spine1",
        "Upper_Spine": " Spine1",
        "UpperSpine": " Spine1",
        "Spine_1": " Spine1",
        
        # Neck variations
        "Neck": " Neck",
        "neck": " Neck",
        "Cervical": " Neck",
        "cervical": " Neck",
        
        # Head variations
        "Head": " Head",
        "head": " Head",
        "Skull": " Head",
        "skull": " Head",
        "Cranium": " Head",
        
        # LEFT ARM variations
        "L UpperArm": " L UpperArm",
        "UpperArm.L": " L UpperArm",
        "upperarm.l": " L UpperArm",
        "L_UpperArm": " L UpperArm",
        "Left_UpperArm": " L UpperArm",
        "LeftUpperArm": " L UpperArm",
        "Arm.L": " L UpperArm",
        "L_Arm": " L UpperArm",
        "Left_Arm": " L UpperArm",
        "LUpperArm": " L UpperArm",
        
        "L ForeArm": " L ForeArm",
        "ForeArm.L": " L ForeArm",
        "forearm.l": " L ForeArm",
        "L_ForeArm": " L ForeArm",
        "L_Forearm": " L ForeArm",
        "Left_ForeArm": " L ForeArm",
        "LeftForeArm": " L ForeArm",
        "LowerArm.L": " L ForeArm",
        "L_LowerArm": " L ForeArm",
        "LForeArm": " L ForeArm",
        
        "L Hand": " L Hand",
        "Hand.L": " L Hand",
        "hand.l": " L Hand",
        "L_Hand": " L Hand",
        "Left_Hand": " L Hand",
        "LeftHand": " L Hand",
        "LHand": " L Hand",
        
        # RIGHT ARM variations
        "R UpperArm": " R UpperArm",
        "UpperArm.R": " R UpperArm",
        "upperarm.r": " R UpperArm",
        "R_UpperArm": " R UpperArm",
        "Right_UpperArm": " R UpperArm",
        "RightUpperArm": " R UpperArm",
        "Arm.R": " R UpperArm",
        "R_Arm": " R UpperArm",
        "Right_Arm": " R UpperArm",
        "RUpperArm": " R UpperArm",
        
        "R ForeArm": " R ForeArm",
        "ForeArm.R": " R ForeArm",
        "forearm.r": " R ForeArm",
        "R_ForeArm": " R ForeArm",
        "R_Forearm": " R ForeArm",
        "Right_ForeArm": " R ForeArm",
        "RightForeArm": " R ForeArm",
        "LowerArm.R": " R ForeArm",
        "R_LowerArm": " R ForeArm",
        "RForeArm": " R ForeArm",
        
        "R Hand": " R Hand",
        "Hand.R": " R Hand",
        "hand.r": " R Hand",
        "R_Hand": " R Hand",
        "Right_Hand": " R Hand",
        "RightHand": " R Hand",
        "RHand": " R Hand",
        
        # LEFT LEG variations
        "L Thigh": " L Thigh",
        "Thigh.L": " L Thigh",
        "thigh.l": " L Thigh",
        "L_Thigh": " L Thigh",
        "Left_Thigh": " L Thigh",
        "LeftThigh": " L Thigh",
        "Leg.L": " L Thigh",
        "L_Leg": " L Thigh",
        "Left_Leg": " L Thigh",
        "UpperLeg.L": " L Thigh",
        "L_UpperLeg": " L Thigh",
        "LThigh": " L Thigh",
        
        "L Calf": " L Calf",
        "Calf.L": " L Calf",
        "calf.l": " L Calf",
        "L_Calf": " L Calf",
        "Left_Calf": " L Calf",
        "LeftCalf": " L Calf",
        "Shin.L": " L Calf",
        "L_Shin": " L Calf",
        "Left_Shin": " L Calf",
        "LowerLeg.L": " L Calf",
        "L_LowerLeg": " L Calf",
        "LCalf": " L Calf",
        
        "L Foot": " L Foot",
        "Foot.L": " L Foot",
        "foot.l": " L Foot",
        "L_Foot": " L Foot",
        "Left_Foot": " L Foot",
        "LeftFoot": " L Foot",
        "LFoot": " L Foot",
        
        "L Toe0": " L Toe0",
        "Toe.L": " L Toe0",
        "toe.l": " L Toe0",
        "L_Toe": " L Toe0",
        "L_Toe0": " L Toe0",
        "Left_Toe": " L Toe0",
        "LeftToe": " L Toe0",
        "L_BigToe": " L Toe0",
        "LToe0": " L Toe0",
        
        # RIGHT LEG variations
        "R Thigh": " R Thigh",
        "Thigh.R": " R Thigh",
        "thigh.r": " R Thigh",
        "R_Thigh": " R Thigh",
        "Right_Thigh": " R Thigh",
        "RightThigh": " R Thigh",
        "Leg.R": " R Thigh",
        "R_Leg": " R Thigh",
        "Right_Leg": " R Thigh",
        "UpperLeg.R": " R Thigh",
        "R_UpperLeg": " R Thigh",
        "RThigh": " R Thigh",
        
        "R Calf": " R Calf",
        "Calf.R": " R Calf",
        "calf.r": " R Calf",
        "R_Calf": " R Calf",
        "Right_Calf": " R Calf",
        "RightCalf": " R Calf",
        "Shin.R": " R Calf",
        "R_Shin": " R Calf",
        "Right_Shin": " R Calf",
        "LowerLeg.R": " R Calf",
        "R_LowerLeg": " R Calf",
        "RCalf": " R Calf",
        
        "R Foot": " R Foot",
        "Foot.R": " R Foot",
        "foot.r": " R Foot",
        "R_Foot": " R Foot",
        "Right_Foot": " R Foot",
        "RightFoot": " R Foot",
        "RFoot": " R Foot",
        
        "R Toe0": " R Toe0",
        "Toe.R": " R Toe0",
        "toe.r": " R Toe0",
        "R_Toe": " R Toe0",
        "R_Toe0": " R Toe0",
        "Right_Toe": " R Toe0",
        "RightToe": " R Toe0",
        "R_BigToe": " R Toe0",
        "RToe0": " R Toe0",
        
        # FINGERS variations
        "L Finger": " L Finger",
        "Finger.L": " L Finger",
        "L_Finger": " L Finger",
        "Left_Finger": " L Finger",
        "LFinger": " L Finger",
        
        "R Finger": " R Finger",
        "Finger.R": " R Finger",
        "R_Finger": " R Finger",
        "Right_Finger": " R Finger",
        "RFinger": " R Finger",
    }
    
    @classmethod
    def normalize_bone_name(cls, bone_name):
        """
        Normalizar nombre de hueso a oficial GTA SA
        
        Args:
            bone_name (str): Nombre original del hueso
            
        Returns:
            str: Nombre oficial GTA SA o original si no se puede normalizar
        """
        if not bone_name:
            return bone_name
        
        # 1. Ya es oficial
        if bone_name in cls.OFFICIAL_GTA_SA_BONES:
            return bone_name
        
        # 2. Buscar en mapeo directo
        if bone_name in cls.BONE_VARIATIONS_MAP:
            return cls.BONE_VARIATIONS_MAP[bone_name]
        
        # 3. Buscar case-insensitive en mapeo
        bone_lower = bone_name.lower()
        for variation, official in cls.BONE_VARIATIONS_MAP.items():
            if variation.lower() == bone_lower:
                return official
        
        # 4. Buscar versión con espacios correctos
        bone_clean = bone_name.strip()
        for official in cls.OFFICIAL_GTA_SA_BONES:
            if official.strip() == bone_clean:
                return official
        
        # 5. Buscar case-insensitive con espacios
        for official in cls.OFFICIAL_GTA_SA_BONES:
            if official.strip().lower() == bone_clean.lower():
                return official
        
        # 6. No se pudo normalizar - devolver original
        return bone_name
    
    @classmethod
    def auto_fix_mapping_data(cls, mapping_data):
        """
        Auto-corregir datos de mapeo completos (para JSON)
        
        Args:
            mapping_data (dict): Datos de mapeo cargados del JSON
            
        Returns:
            tuple: (mapping_data_corregido, lista_de_correcciones)
        """
        corrections = []
        
        # Procesar según formato del JSON
        if isinstance(mapping_data, dict):
            if "mappings" in mapping_data:
                # Formato v2.0 (completo)
                for i, mapping in enumerate(mapping_data["mappings"]):
                    original_target = mapping.get("target_bone", "")
                    if original_target:
                        normalized_target = cls.normalize_bone_name(original_target)
                        
                        if normalized_target != original_target:
                            mapping["target_bone"] = normalized_target
                            corrections.append(f"#{i+1}: '{original_target}' → '{normalized_target}'")
            else:
                # Formato v1.0 (simple: {"source": "target"})
                for source, target in list(mapping_data.items()):
                    if isinstance(target, str):
                        normalized_target = cls.normalize_bone_name(target)
                        
                        if normalized_target != target:
                            mapping_data[source] = normalized_target
                            corrections.append(f"'{target}' → '{normalized_target}'")
        
        return mapping_data, corrections
    
    @classmethod
    def auto_fix_bone_mappings_list(cls, bone_mappings_list):
        """
        Auto-corregir lista de BoneMappingItem (para uso directo en Blender)
        
        Args:
            bone_mappings_list: Collection de BoneMappingItem de Blender
            
        Returns:
            list: Lista de correcciones aplicadas
        """
        corrections = []
        
        for i, mapping in enumerate(bone_mappings_list):
            original_target = mapping.target_bone
            if original_target:
                normalized_target = cls.normalize_bone_name(original_target)
                
                if normalized_target != original_target:
                    mapping.target_bone = normalized_target
                    corrections.append(f"Mapping #{i+1}: '{original_target}' → '{normalized_target}'")
        
        return corrections
    
    @classmethod
    def validate_normalization(cls, bone_name):
        """
        Validar si un hueso está correctamente normalizado
        
        Args:
            bone_name (str): Nombre del hueso a validar
            
        Returns:
            tuple: (es_oficial, sugerencia_si_no_es_oficial)
        """
        if bone_name in cls.OFFICIAL_GTA_SA_BONES:
            return True, None
        
        normalized = cls.normalize_bone_name(bone_name)
        if normalized != bone_name:
            return False, normalized
        
        return False, None
    
    @classmethod
    def get_correction_report(cls, corrections):
        """
        Generar reporte legible de correcciones
        
        Args:
            corrections (list): Lista de correcciones aplicadas
            
        Returns:
            str: Reporte formateado
        """
        if not corrections:
            return "✅ No se necesitaron correcciones - todos los huesos ya están normalizados"
        
        report = []
        report.append(f"🔧 AUTO-FIX APLICADO: {len(corrections)} correcciones")
        report.append("=" * 50)
        
        for correction in corrections:
            report.append(f"  ✅ {correction}")
        
        report.append("=" * 50)
        report.append("💡 Todos los huesos target ahora usan nombres oficiales GTA SA")
        
        return "\n".join(report)

# Test del normalizador
if __name__ == "__main__":
    # Probar algunas normalizaciones
    test_bones = [
        "Pelvis",        # Sin espacio
        " Pelvis",       # Correcto
        "UpperArm.L",    # Formato .L
        "L_Hand",        # Formato _
        "Thigh.R",       # Formato .R
        "R_Foot",        # Formato _
        "invalid_bone",  # No normalizable
    ]
    
    print("🧪 TESTING GTA SA NORMALIZER")
    print("=" * 40)
    
    for bone in test_bones:
        normalized = GTASANormalizer.normalize_bone_name(bone)
        is_official, suggestion = GTASANormalizer.validate_normalization(bone)
        
        status = "✅" if is_official else "🔧"
        print(f"{status} '{bone}' → '{normalized}'")
    
    print(f"\n📊 Total huesos oficiales: {len(GTASANormalizer.OFFICIAL_GTA_SA_BONES)}")
