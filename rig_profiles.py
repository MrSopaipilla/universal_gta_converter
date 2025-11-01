"""
rig_profiles_enhanced.py - Sistema completo de perfiles de rigs MEJORADO
Compatible con Mixamo, Source/SFM (bip01_ y bip_), Rigify y más
Universal GTA SA Converter v4.0.1 - CORREGIDO con umbral de confianza más bajo
"""

import bpy

class RigProfileSystem:
    """Sistema inteligente de detección y mapeo de rigs - MEJORADO"""
    
    def __init__(self):
        self.profiles = self._initialize_profiles()
    
    def _initialize_profiles(self):
        """Inicializa todos los perfiles de rigs disponibles"""
        return {
            "mixamo": self._get_mixamo_profile(),
            "source_sfm": self._get_source_sfm_profile(), 
            "source_sfm_bip": self._get_source_sfm_bip_profile(),  # NUEVO: Para prefix bip_
            "rigify": self._get_rigify_profile(),
            "accurig": self._get_accurig_profile(),
            "avatarsdk": self._get_avatarsdk_profile(),
            "valve_biped": self._get_valve_biped_profile(),
        }
    
    def detect_rig_type(self, armature):
        """
        Detecta automáticamente el tipo de rig basándose en los nombres de huesos
        CORREGIDO: Umbral más bajo y mejor detección para bip_
        
        Args:
            armature: Objeto armature de Blender
            
        Returns:
            tuple: (profile_name, confidence_score)
        """
        if not armature or armature.type != 'ARMATURE':
            return None, 0.0
            
        bone_names = [bone.name for bone in armature.data.bones]
        best_match = None
        highest_confidence = 0.0
        
        print(f"[RIG_DETECT] Analizando {len(bone_names)} huesos...")
        
        for profile_name, profile in self.profiles.items():
            confidence = self._calculate_confidence(bone_names, profile)
            
            print(f"[RIG_DETECT] {profile_name}: {confidence:.3f} confianza")
            
            if confidence > highest_confidence:
                highest_confidence = confidence
                best_match = profile_name
        
        # CORREGIDO: Umbral más bajo para aceptar detecciones
        if highest_confidence >= 0.4:  # Reducido de 0.6 a 0.4
            print(f"[RIG_DETECT] ✅ Detectado: {best_match} (confianza: {highest_confidence:.3f})")
            return best_match, highest_confidence
        
        print(f"[RIG_DETECT] ❌ Confianza insuficiente (mejor: {highest_confidence:.3f})")
        return None, highest_confidence
    
    def _calculate_confidence(self, bone_names, profile):
        """Calcula la confianza de que un armature coincida con un perfil - MEJORADO"""
        detection_patterns = profile.get("detection_patterns", [])
        bone_mapping = profile.get("bone_mapping", {})
        
        if not detection_patterns and not bone_mapping:
            return 0.0
        
        # CORREGIDO: Mejor puntuación por patrones de prefijo
        pattern_score = 0.0
        total_bones = len(bone_names)
        
        if detection_patterns and total_bones > 0:
            matching_bones = 0
            for bone_name in bone_names:
                bone_lower = bone_name.lower()
                for pattern in detection_patterns:
                    pattern_lower = pattern.lower()
                    # MEJORADO: Detección más flexible
                    if (pattern_lower in bone_lower or 
                        bone_lower.startswith(pattern_lower) or
                        any(word in bone_lower for word in pattern_lower.split('_'))):
                        matching_bones += 1
                        break
            
            pattern_score = matching_bones / total_bones
            print(f"[RIG_DETECT] {profile.get('name', 'Unknown')}: {matching_bones}/{total_bones} huesos coinciden con patrones")
        
        # CORREGIDO: Mejor puntuación por mapeos específicos conocidos
        mapping_score = 0.0
        mapped_bones = list(bone_mapping.keys())
        
        if mapped_bones:
            matching_mapped = 0
            for source_bone in mapped_bones:
                # MEJORADO: Buscar coincidencias parciales también
                for actual_bone in bone_names:
                    if (source_bone.lower() == actual_bone.lower() or
                        source_bone.lower() in actual_bone.lower() or
                        actual_bone.lower() in source_bone.lower()):
                        matching_mapped += 1
                        break
            
            mapping_score = matching_mapped / len(mapped_bones)
            print(f"[RIG_DETECT] {profile.get('name', 'Unknown')}: {matching_mapped}/{len(mapped_bones)} mapeos específicos encontrados")
        
        # CORREGIDO: Promedio ponderado ajustado (70% mapeo, 30% patrones)
        final_confidence = (mapping_score * 0.7) + (pattern_score * 0.3)
        
        # NUEVO: Bonus adicional para perfiles bip_ si hay muchos huesos bip_
        if profile.get("name") == "Source/SFM (bip_)":
            bip_count = sum(1 for bone in bone_names if bone.lower().startswith('bip_'))
            if bip_count > 20:  # Si hay más de 20 huesos bip_
                bonus = min(0.3, bip_count / 100)  # Bonus hasta 0.3
                final_confidence += bonus
                print(f"[RIG_DETECT] Bonus bip_: +{bonus:.3f} por {bip_count} huesos bip_")
        
        return min(final_confidence, 1.0)
    
    def apply_profile(self, source_armature, target_armature, profile_name):
        """
        Aplica un perfil específico para mapear huesos
        
        Args:
            source_armature: Armature fuente
            target_armature: Armature destino (GTA SA)
            profile_name: Nombre del perfil a aplicar
            
        Returns:
            dict: Resultado de la aplicación del perfil
        """
        if profile_name not in self.profiles:
            return {"success": False, "error": f"Profile '{profile_name}' not found"}
        
        profile = self.profiles[profile_name]
        bone_mapping = profile.get("bone_mapping", {})
        
        # Crear mapeos válidos
        valid_mappings = []
        invalid_mappings = []
        source_bones = [b.name for b in source_armature.data.bones]
        target_bones = [b.name for b in target_armature.data.bones]
        
        # MEJORADO: Buscar coincidencias más flexibles
        for source_pattern, target_bone in bone_mapping.items():
            # Buscar hueso fuente que coincida con el patrón
            found_source = None
            
            # 1. Coincidencia exacta
            if source_pattern in source_bones:
                found_source = source_pattern
            else:
                # 2. Coincidencia parcial (case-insensitive)
                pattern_lower = source_pattern.lower()
                for bone in source_bones:
                    bone_lower = bone.lower()
                    if (pattern_lower in bone_lower or 
                        bone_lower in pattern_lower or
                        bone_lower == pattern_lower):
                        found_source = bone
                        break
            
            # Verificar que el target también existe
            if found_source and target_bone in target_bones:
                valid_mappings.append((found_source, target_bone))
                print(f"[RIG_APPLY] ✅ Mapeo válido: {found_source} -> {target_bone}")
            else:
                invalid_mappings.append((source_pattern, target_bone))
                missing_info = []
                if not found_source:
                    missing_info.append(f"source '{source_pattern}' no encontrado")
                if target_bone not in target_bones:
                    missing_info.append(f"target '{target_bone}' no existe")
                print(f"[RIG_APPLY] ❌ Mapeo inválido: {source_pattern} -> {target_bone} ({', '.join(missing_info)})")
        
        result = {
            "success": True,
            "profile_name": profile_name,
            "profile_display_name": profile.get("name", profile_name),
            "mappings": valid_mappings,
            "invalid_mappings": invalid_mappings,
            "weight_influences": profile.get("weight_influences", []),
            "bones_to_delete": profile.get("bones_to_delete", []),
            "vertex_groups_to_delete": profile.get("vertex_groups_to_delete", []),
            "total_mappings": len(valid_mappings),
            "total_invalid": len(invalid_mappings),
            "available_source_bones": len(source_bones),
            "coverage_percentage": (len(valid_mappings) / len(source_bones)) * 100 if source_bones else 0
        }
        
        print(f"[RIG_APPLY] ✅ Perfil aplicado: {result['profile_display_name']}")
        print(f"[RIG_APPLY] Mapeos válidos: {len(valid_mappings)}")
        print(f"[RIG_APPLY] Mapeos inválidos: {len(invalid_mappings)}")
        
        return result
    
    # ============================================================================
    # PERFIL MIXAMO
    # ============================================================================
    def _get_mixamo_profile(self):
        """Perfil completo para rigs de Mixamo"""
        return {
            "name": "Mixamo",
            "description": "Adobe Mixamo character rigs",
            "detection_patterns": ["mixamorig:", "mixamorig_"],
            "confidence_threshold": 0.8,
            
            "bone_mapping": {
                # Core skeleton
                'mixamorig:Hips': ' Pelvis',
                'mixamorig:Spine': ' Spine',
                'mixamorig:Spine1': ' Spine1',
                'mixamorig:Spine2': ' Spine1',  # UNIFICAR en Spine1
                'mixamorig:Neck': ' Neck',
                'mixamorig:Head': ' Head',
                'mixamorig:Jaw': 'Jaw',
                
                # Left arm
                'mixamorig:LeftShoulder': 'Bip01 L Clavicle',
                'mixamorig:LeftArm': ' L UpperArm',
                'mixamorig:LeftForeArm': ' L ForeArm',
                'mixamorig:LeftHand': ' L Hand',
                'mixamorig:LeftHandIndex1': ' L Finger',
                'mixamorig:LeftHandIndex2': 'L Finger01',
                
                # Right arm
                'mixamorig:RightShoulder': 'Bip01 R Clavicle',
                'mixamorig:RightArm': ' R UpperArm',
                'mixamorig:RightForeArm': ' R ForeArm',
                'mixamorig:RightHand': ' R Hand',
                'mixamorig:RightHandIndex1': ' R Finger',
                'mixamorig:RightHandIndex2': 'R Finger01',
                
                # Left leg
                'mixamorig:LeftUpLeg': ' L Thigh',
                'mixamorig:LeftLeg': ' L Calf',
                'mixamorig:LeftFoot': ' L Foot',
                'mixamorig:LeftToeBase': ' L Toe0',
                
                # Right leg
                'mixamorig:RightUpLeg': ' R Thigh',
                'mixamorig:RightLeg': ' R Calf',
                'mixamorig:RightFoot': ' R Foot',
                'mixamorig:RightToeBase': ' R Toe0',
            },
            
            "weight_influences": [
                # RIGHT HAND
                ['mixamorig:RightHand', 'mixamorig:RightHandThumb1'],
                ['mixamorig:RightHand', 'mixamorig:RightHandThumb2'],
                ['mixamorig:RightHand', 'mixamorig:RightHandThumb3'],
                ['mixamorig:RightHandIndex1', 'mixamorig:RightHandMiddle1'],
                ['mixamorig:RightHandIndex1', 'mixamorig:RightHandRing1'],
                ['mixamorig:RightHandIndex1', 'mixamorig:RightHandPinky1'],
                ['mixamorig:RightHandIndex2', 'mixamorig:RightHandIndex3'],
                ['mixamorig:RightHandIndex2', 'mixamorig:RightHandMiddle2'],
                ['mixamorig:RightHandIndex2', 'mixamorig:RightHandMiddle3'],
                ['mixamorig:RightHandIndex2', 'mixamorig:RightHandRing2'],
                ['mixamorig:RightHandIndex2', 'mixamorig:RightHandRing3'],
                ['mixamorig:RightHandIndex2', 'mixamorig:RightHandPinky2'],
                ['mixamorig:RightHandIndex2', 'mixamorig:RightHandPinky3'],
                
                # LEFT HAND
                ['mixamorig:LeftHand', 'mixamorig:LeftHandThumb1'],
                ['mixamorig:LeftHand', 'mixamorig:LeftHandThumb2'],
                ['mixamorig:LeftHand', 'mixamorig:LeftHandThumb3'],
                ['mixamorig:LeftHandIndex1', 'mixamorig:LeftHandMiddle1'],
                ['mixamorig:LeftHandIndex1', 'mixamorig:LeftHandRing1'],
                ['mixamorig:LeftHandIndex1', 'mixamorig:LeftHandPinky1'],
                ['mixamorig:LeftHandIndex2', 'mixamorig:LeftHandIndex3'],
                ['mixamorig:LeftHandIndex2', 'mixamorig:LeftHandMiddle2'],
                ['mixamorig:LeftHandIndex2', 'mixamorig:LeftHandMiddle3'],
                ['mixamorig:LeftHandIndex2', 'mixamorig:LeftHandRing2'],
                ['mixamorig:LeftHandIndex2', 'mixamorig:LeftHandRing3'],
                ['mixamorig:LeftHandIndex2', 'mixamorig:LeftHandPinky2'],
                ['mixamorig:LeftHandIndex2', 'mixamorig:LeftHandPinky3'],
            ],
            
            "bones_to_delete": [
                'mixamorig:LeftHandThumb4', 'mixamorig:LeftHandIndex4', 'mixamorig:LeftHandMiddle4',
                'mixamorig:LeftHandRing4', 'mixamorig:LeftHandPinky4', 'mixamorig:LeftToe_End',
                'mixamorig:HeadTop_End', 'mixamorig:RightHandThumb4', 'mixamorig:RightHandIndex4',
                'mixamorig:RightHandMiddle4', 'mixamorig:RightHandRing4', 'mixamorig:RightHandPinky4',
                'mixamorig:RightToe_End'
            ],
            
            "vertex_groups_to_delete": [
                "mixamorig:Spine2", "mixamorig:LeftHandThumb1", "mixamorig:LeftHandThumb2",
                "mixamorig:LeftHandThumb3", "mixamorig:LeftHandIndex3", "mixamorig:LeftHandMiddle1",
                "mixamorig:LeftHandMiddle2", "mixamorig:LeftHandMiddle3", "mixamorig:LeftHandRing1",
                "mixamorig:LeftHandRing2", "mixamorig:LeftHandRing3", "mixamorig:RightHandThumb1",
                "mixamorig:RightHandThumb2", "mixamorig:RightHandThumb3", "mixamorig:RightHandIndex3",
                "mixamorig:RightHandMiddle1", "mixamorig:RightHandMiddle2", "mixamorig:RightHandMiddle3",
                "mixamorig:RightHandRing1", "mixamorig:RightHandRing2", "mixamorig:RightHandRing3", 
                "mixamorig:RightHandPinky1", "mixamorig:RightHandPinky2", "mixamorig:RightHandPinky3",
                "mixamorig:Nose", "Twist_Hand_Left", "Twist_ForeArm_Left", "Twist_ForeArm_Right",
                "Twist_Hand_Right", "mixamorig:LeftHandPinky1", "mixamorig:LeftHandPinky2",
                "mixamorig:LeftHandPinky3",
            ]
        }
    
    # ============================================================================
    # PERFIL SOURCE/SFM (bip01_)
    # ============================================================================
    def _get_source_sfm_profile(self):
        """Perfil para Source Engine/SFM con prefix bip01_"""
        return {
            "name": "Source/SFM (bip01_)",
            "description": "Source Engine games (Half-Life, TF2, Portal, etc.) - bip01_ prefix",
            "detection_patterns": ["bip01_"],
            "confidence_threshold": 0.8,
            
            "bone_mapping": {
                # Core skeleton
                'bip01_pelvis': ' Pelvis',
                'bip01_spine': ' Spine',
                'bip01_spine1': ' Spine1',
                'bip01_spine2': ' Spine1',
                'bip01_spine3': ' Spine1',
                'bip01_neck1': ' Neck',
                'bip01_head1': ' Head',
                
                # Left arm
                'bip01_l_clavicle': 'Bip01 L Clavicle',
                'bip01_l_upperarm': ' L UpperArm',
                'bip01_l_forearm': ' L Forearm',
                'bip01_l_hand': ' L Hand',
                'bip01_l_finger0': ' L Finger',
                'bip01_l_finger01': 'L Finger01',
                'bip01_l_finger1': ' L Finger',
                'bip01_l_finger11': 'L Finger01',
                
                # Right arm
                'bip01_r_clavicle': 'Bip01 R Clavicle',
                'bip01_r_upperarm': ' R UpperArm',
                'bip01_r_forearm': ' R Forearm',
                'bip01_r_hand': ' R Hand',
                'bip01_r_finger0': ' R Finger',
                'bip01_r_finger01': 'R Finger01',
                'bip01_r_finger1': ' R Finger',
                'bip01_r_finger11': 'R Finger01',
                
                # Left leg
                'bip01_l_thigh': ' L Thigh',
                'bip01_l_calf': ' L Calf',
                'bip01_l_foot': ' L Foot',
                'bip01_l_toe0': ' L Toe0',
                
                # Right leg
                'bip01_r_thigh': ' R Thigh',
                'bip01_r_calf': ' R Calf',
                'bip01_r_foot': ' R Foot',
                'bip01_r_toe0': ' R Toe0',
            },
            
            "weight_influences": [
                # Twist bones
                ['bip01_l_upperarm', 'bip01_l_upperarm_twist'],
                ['bip01_r_upperarm', 'bip01_r_upperarm_twist'],
                ['bip01_l_forearm', 'bip01_l_forearm_twist'],
                ['bip01_r_forearm', 'bip01_r_forearm_twist'],
                ['bip01_l_thigh', 'bip01_l_thigh_twist'],
                ['bip01_r_thigh', 'bip01_r_thigh_twist'],
                ['bip01_l_calf', 'bip01_l_calf_twist'],
                ['bip01_r_calf', 'bip01_r_calf_twist'],
                
                # Finger consolidation
                ['bip01_r_hand', 'bip01_r_finger0'],
                ['bip01_r_finger1', 'bip01_r_finger2'],
                ['bip01_r_finger1', 'bip01_r_finger3'],
                ['bip01_r_finger1', 'bip01_r_finger4'],
                ['bip01_l_hand', 'bip01_l_finger0'],
                ['bip01_l_finger1', 'bip01_l_finger2'],
                ['bip01_l_finger1', 'bip01_l_finger3'],
                ['bip01_l_finger1', 'bip01_l_finger4'],
            ],
            
            "bones_to_delete": [
                'bip01_l_upperarm_twist', 'bip01_r_upperarm_twist',
                'bip01_l_forearm_twist', 'bip01_r_forearm_twist',
                'bip01_l_thigh_twist', 'bip01_r_thigh_twist',
                'bip01_l_calf_twist', 'bip01_r_calf_twist',
                'bip01_l_finger2', 'bip01_l_finger3', 'bip01_l_finger4',
                'bip01_r_finger2', 'bip01_r_finger3', 'bip01_r_finger4',
                'bip01_head1_end', 'bip01_l_toe0_end', 'bip01_r_toe0_end',
            ],
            
            "vertex_groups_to_delete": [
                "bip01_l_upperarm_twist", "bip01_r_upperarm_twist",
                "bip01_l_forearm_twist", "bip01_r_forearm_twist",
                "bip01_l_thigh_twist", "bip01_r_thigh_twist",
                "bip01_l_calf_twist", "bip01_r_calf_twist",
                "bip01_l_finger2", "bip01_l_finger3", "bip01_l_finger4",
                "bip01_r_finger2", "bip01_r_finger3", "bip01_r_finger4",
            ]
        }

    # ==========================================================================
    # PERFIL ACCURIG (CC_Base_ prefijo)
    # ==========================================================================
    def _get_accurig_profile(self):
        """Perfil para rigs exportados por AccuRig con prefijo CC_Base_"""
        import os
        import json

        addon_dir = os.path.dirname(__file__)
        mapping_path = os.path.join(addon_dir, "mappings", "accurig_bone_mapping.json")

        bone_mapping = {}
        detection_patterns = ["CC_Base_", "cc_base_"]

        try:
            if os.path.exists(mapping_path):
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert mappings list into source->target dict
                    for item in data.get('mappings', []):
                        src = item.get('source_bone')
                        tgt = item.get('target_bone')
                        if src and tgt:
                            bone_mapping[src] = tgt
            else:
                print(f"[RIG_PROFILES] accurig mapping file not found: {mapping_path}")
        except Exception as e:
            print(f"[RIG_PROFILES] Error loading accurig mapping: {e}")

        return {
            "name": "AccuRig",
            "description": "AccuRig / CC_Base_ skeletons",
            "detection_patterns": detection_patterns,
            "confidence_threshold": 0.6,
            "bone_mapping": bone_mapping,
        }

    # ==========================================================================
    # PERFIL AVATARSDK
    # ==========================================================================
    def _get_avatarsdk_profile(self):
        """Perfil para AvatarSDK / common humanoid naming (Hips, LeftArm, RightArm, etc.)"""
        import os
        import json

        addon_dir = os.path.dirname(__file__)
        mapping_path = os.path.join(addon_dir, "mappings", "avatarsdk_bone_mapping.json")

        bone_mapping = {}
        # patrones comunes que ayudan a detectar Avatars exportados por AvatarSDK
        detection_patterns = ["hips", "leftarm", "rightarm", "avatarsdk", "leftforearm", "rightforearm"]

        try:
            if os.path.exists(mapping_path):
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get('mappings', []):
                        src = item.get('source_bone')
                        tgt = item.get('target_bone')
                        if src and tgt:
                            bone_mapping[src] = tgt
            else:
                print(f"[RIG_PROFILES] avatarsdk mapping file not found: {mapping_path}")
        except Exception as e:
            print(f"[RIG_PROFILES] Error loading avatarsdk mapping: {e}")

        return {
            "name": "AvatarSDK",
            "description": "AvatarSDK / common humanoid skeletons",
            "detection_patterns": detection_patterns,
            "confidence_threshold": 0.5,
            "bone_mapping": bone_mapping,
        }
    
    # ============================================================================
    # PERFIL SOURCE/SFM BIP_ (MEJORADO PARA TU CASO)
    # ============================================================================
    def _get_source_sfm_bip_profile(self):
        """Perfil ESPECIAL para Source Engine/SFM con prefix bip_ - MEJORADO"""
        return {
            "name": "Source/SFM (bip_)",
            "description": "Source Engine games con prefix bip_ - Para mapeo completo a GTA SA",
            "detection_patterns": ["bip_"],
            "confidence_threshold": 0.4,  # REDUCIDO para mayor detección
            
            "bone_mapping": {
                # ===== MAPEOS PRINCIPALES BASADOS EN TU BONE_MAPPING.JSON =====
                # Core skeleton
                'bip_pelvis': ' Pelvis',
                'bip_butt': ' Pelvis',
                'bip_butt_r': ' Pelvis',
                'bip_butt_l': ' Pelvis',
                'bip_hip': ' Pelvis',
                
                'bip_spine_0': ' Spine',
                'bip_spine': ' Spine',
                'bip_spine_1': ' Spine',
                
                'bip_spine_3': ' Spine1',
                'bip_spine_2': ' Spine1',
                'bip_spine_4': ' Spine1',
                'bip_spine1': ' Spine1',
                'bip_spine2': ' Spine1',
                
                'bip_neck': ' Neck',
                'bip_neck_1': ' Neck',
                'bip_neck1': ' Neck',
                
                'bip_head': ' Head',
                'bip_head1': ' Head',
                'bip_skull': ' Head',
                
                'Tongue': 'Jaw',
                'bip_jaw': 'Jaw',
                'bip_chin': 'Jaw',
                'bip_mouth': 'Jaw',
                
                # Left arm - MEJORADO CON MÁS VARIACIONES
                'bip_collar_l': 'Bip01 L Clavicle',
                'bip_clavicle_l': 'Bip01 L Clavicle',
                'bip_shoulder_l': 'Bip01 L Clavicle',
                
                'bip_UpperArm_twist2_l': ' L UpperArm',
                'bip_upperarm_l': ' L UpperArm',
                'bip_arm_l': ' L UpperArm',
                
                'bip_lowerArm_l_twist2': ' L ForeArm',
                'bip_forearm_l': ' L ForeArm',
                'bip_lowerarm_l': ' L ForeArm',
                
                'bip_hand_l': ' L Hand',
                'bip_thumb_2_l': ' L Hand',
                'bip_thumb_l': ' L Hand',
                'bip_thumb_0_l': ' L Hand',
                'bip_thumb_1_l': ' L Hand',
                
                'bip_pinky_0_l': ' L Finger',
                'bip_index_0_l': ' L Finger',
                'bip_middle_0_l': ' L Finger',
                'bip_ring_0_l': ' L Finger',
                
                'bip_pinky_2_l': 'L Finger01',
                'bip_index_1_l': 'L Finger01',
                'bip_index_2_l': 'L Finger01',
                'bip_middle_1_l': 'L Finger01',
                'bip_ring_1_l': 'L Finger01',
                'bip_pinky_1_l': 'L Finger01',
                
                # Right arm - MEJORADO CON MÁS VARIACIONES
                'bip_collar_r': 'Bip01 R Clavicle',
                'bip_clavicle_r': 'Bip01 R Clavicle',
                'bip_shoulder_r': 'Bip01 R Clavicle',
                
                'bip_UpperArm_twist2_r': ' R UpperArm',
                'bip_upperarm_r': ' R UpperArm',
                'bip_arm_r': ' R UpperArm',
                
                'bip_lowerArm_r_twist2': ' R ForeArm',
                'bip_forearm_r': ' R ForeArm',
                'bip_lowerarm_r': ' R ForeArm',
                
                'bip_hand_r': ' R Hand',
                'bip_thumb_2_r': ' R Hand',
                'bip_thumb_r': ' R Hand',
                'bip_thumb_0_r': ' R Hand',
                'bip_thumb_1_r': ' R Hand',
                
                'bip_pinky_0_r': ' R Finger',
                'bip_index_0_r': ' R Finger',
                'bip_middle_0_r': ' R Finger',
                'bip_ring_0_r': ' R Finger',
                
                'bip_pinky_2_r': 'R Finger01',
                'bip_index_1_r': 'R Finger01',
                'bip_index_2_r': 'R Finger01',
                'bip_middle_1_r': 'R Finger01',
                'bip_ring_1_r': 'R Finger01',
                'bip_pinky_1_r': 'R Finger01',
                
                # Left leg - MEJORADO CON MÁS VARIACIONES
                'bip_hip_l': ' L Thigh',
                'bip_thigh_l': ' L Thigh',
                
                'bip_knee_l': ' L Calf',
                'bip_calf_l': ' L Calf',
                'bip_shin_l': ' L Calf',
                
                'bip_foot_l': ' L Foot',
                'bip_ankle_l': ' L Foot',
                
                'bip_toe_l': ' L Toe0',
                'bip_bigtoe_l': ' L Toe0',
                'bip_toe_0_l': ' L Toe0',
                'bip_toe_1_l': ' L Toe0',
                
                # Right leg - MEJORADO CON MÁS VARIACIONES
                'bip_hip_r': ' R Thigh',
                'bip_thigh_r': ' R Thigh',
                
                'bip_knee_r': ' R Calf',
                'bip_calf_r': ' R Calf',
                'bip_shin_r': ' R Calf',
                
                'bip_foot_r': ' R Foot',
                'bip_ankle_r': ' R Foot',
                
                'bip_toe_r': ' R Toe0',
                'bip_bigtoe_r': ' R Toe0',
                'bip_toe_0_r': ' R Toe0',
                'bip_toe_1_r': ' R Toe0',
                
                # NUEVOS: Mapeos adicionales para huesos comunes en Source
                'bip_root': ' Pelvis',
                'bip_com': ' Pelvis',
                
                # Facial bones adicionales
                'bip_eyebrow_l': ' L Brow',
                'bip_eyebrow_r': ' R Brow',
                'bip_eyelid_upper_l': ' L Brow',
                'bip_eyelid_upper_r': ' R Brow',
                
                # Otros huesos que podrían aparecer
                'bip_breast_l': ' Spine1',
                'bip_breast_r': ' Spine1',
                'bip_belly': ' Spine',
                
                # Twist bones alternatives
                'bip_upperarm_twist_l': ' L UpperArm',
                'bip_upperarm_twist_r': ' R UpperArm',
                'bip_forearm_twist_l': ' L ForeArm',
                'bip_forearm_twist_r': ' R ForeArm',
                
                # Helper bones
                'bip_helper_pelvis': ' Pelvis',
                'bip_helper_spine': ' Spine',
                'bip_helper_chest': ' Spine1',
            },
            
            "weight_influences": [
                # Consolidar dedos thumb en hand
                ['bip_thumb_2_l', 'bip_thumb_0_l'],
                ['bip_thumb_2_l', 'bip_thumb_1_l'],
                ['bip_thumb_2_l', 'bip_thumb_l'],
                ['bip_thumb_2_r', 'bip_thumb_0_r'],
                ['bip_thumb_2_r', 'bip_thumb_1_r'],
                ['bip_thumb_2_r', 'bip_thumb_r'],
                
                # Consolidar otros dedos en finger
                ['bip_pinky_0_l', 'bip_index_0_l'],
                ['bip_pinky_0_l', 'bip_middle_0_l'],
                ['bip_pinky_0_l', 'bip_ring_0_l'],
                ['bip_pinky_0_r', 'bip_index_0_r'],
                ['bip_pinky_0_r', 'bip_middle_0_r'],
                ['bip_pinky_0_r', 'bip_ring_0_r'],
                
                # Consolidar segundas falanges
                ['bip_pinky_2_l', 'bip_index_1_l'],
                ['bip_pinky_2_l', 'bip_index_2_l'],
                ['bip_pinky_2_l', 'bip_middle_1_l'],
                ['bip_pinky_2_l', 'bip_ring_1_l'],
                ['bip_pinky_2_l', 'bip_pinky_1_l'],
                ['bip_pinky_2_r', 'bip_index_1_r'],
                ['bip_pinky_2_r', 'bip_index_2_r'],
                ['bip_pinky_2_r', 'bip_middle_1_r'],
                ['bip_pinky_2_r', 'bip_ring_1_r'],
                ['bip_pinky_2_r', 'bip_pinky_1_r'],
                
                # Twist bones si existen
                ['bip_UpperArm_twist2_l', 'bip_upperarm_twist_l'],
                ['bip_UpperArm_twist2_r', 'bip_upperarm_twist_r'],
                ['bip_lowerArm_l_twist2', 'bip_forearm_twist_l'],
                ['bip_lowerArm_r_twist2', 'bip_forearm_twist_r'],
                
                # Consolidar spines múltiples
                ['bip_spine_0', 'bip_spine'],
                ['bip_spine_3', 'bip_spine_2'],
                ['bip_spine_3', 'bip_spine_4'],
                
                # Consolidar pelvis múltiples
                ['bip_pelvis', 'bip_butt'],
                ['bip_pelvis', 'bip_butt_l'],
                ['bip_pelvis', 'bip_butt_r'],
                ['bip_pelvis', 'bip_hip'],
            ],
            
            "bones_to_delete": [
                # Finger extras (después del mixing)
                'bip_index_0_l', 'bip_middle_0_l', 'bip_ring_0_l',
                'bip_index_1_l', 'bip_middle_1_l', 'bip_ring_1_l', 'bip_pinky_1_l',
                'bip_index_2_l', 'bip_middle_2_l', 'bip_ring_2_l',
                'bip_index_0_r', 'bip_middle_0_r', 'bip_ring_0_r',
                'bip_index_1_r', 'bip_middle_1_r', 'bip_ring_1_r', 'bip_pinky_1_r',
                'bip_index_2_r', 'bip_middle_2_r', 'bip_ring_2_r',
                
                # Thumb extras
                'bip_thumb_0_l', 'bip_thumb_1_l', 'bip_thumb_l',
                'bip_thumb_0_r', 'bip_thumb_1_r', 'bip_thumb_r',
                
                # Twist bones
                'bip_upperarm_twist_l', 'bip_upperarm_twist_r',
                'bip_forearm_twist_l', 'bip_forearm_twist_r',
                
                # End bones y extras
                'bip_head_end', 'bip_toe_end_l', 'bip_toe_end_r',
                
                # Spine extras
                'bip_spine', 'bip_spine_2', 'bip_spine_4',
                
                # Pelvis extras
                'bip_butt', 'bip_butt_l', 'bip_butt_r', 'bip_hip',
                
                # Helper bones
                'bip_helper_pelvis', 'bip_helper_spine', 'bip_helper_chest',
            ],
            
            "vertex_groups_to_delete": [
                # Finger VGs
                "bip_index_0_l", "bip_middle_0_l", "bip_ring_0_l",
                "bip_index_1_l", "bip_middle_1_l", "bip_ring_1_l", "bip_pinky_1_l",
                "bip_index_2_l", "bip_middle_2_l", "bip_ring_2_l",
                "bip_index_0_r", "bip_middle_0_r", "bip_ring_0_r",
                "bip_index_1_r", "bip_middle_1_r", "bip_ring_1_r", "bip_pinky_1_r",
                "bip_index_2_r", "bip_middle_2_r", "bip_ring_2_r",
                
                # Thumb VGs
                "bip_thumb_0_l", "bip_thumb_1_l", "bip_thumb_l",
                "bip_thumb_0_r", "bip_thumb_1_r", "bip_thumb_r",
                
                # Twist VGs
                "bip_upperarm_twist_l", "bip_upperarm_twist_r",
                "bip_forearm_twist_l", "bip_forearm_twist_r",
                
                # Spine extras VGs
                "bip_spine", "bip_spine_2", "bip_spine_4",
                
                # Pelvis extras VGs
                "bip_butt", "bip_butt_l", "bip_butt_r", "bip_hip",
            ]
        }
    
    # ============================================================================
    # PERFIL RIGIFY (Blender)
    # ============================================================================
    def _get_rigify_profile(self):
        """Perfil para Rigify (sistema de rigging de Blender)"""
        return {
            "name": "Rigify",
            "description": "Blender Rigify generated rigs",
            "detection_patterns": ["spine", ".L", ".R", "upper_arm", "forearm", "thigh", "shin"],
            "confidence_threshold": 0.7,
            
            "bone_mapping": {
                # Core skeleton
                'pelvis': ' Pelvis',
                'spine': ' Spine',
                'spine.001': ' Spine1',
                'spine.002': ' Spine1',
                'spine.003': ' Spine1',
                'neck': ' Neck',
                'head': ' Head',
                
                # Left arm
                'shoulder.L': 'Bip01 L Clavicle',
                'upper_arm.L': ' L UpperArm',
                'forearm.L': ' L Forearm',
                'hand.L': ' L Hand',
                'thumb.01.L': ' L Finger',
                'thumb.02.L': 'L Finger01',
                'f_index.01.L': ' L Finger',
                'f_index.02.L': 'L Finger01',
                
                # Right arm
                'shoulder.R': 'Bip01 R Clavicle',
                'upper_arm.R': ' R UpperArm',
                'forearm.R': ' R Forearm',
                'hand.R': ' R Hand',
                'thumb.01.R': ' R Finger',
                'thumb.02.R': 'R Finger01',
                'f_index.01.R': ' R Finger',
                'f_index.02.R': 'R Finger01',
                
                # Left leg
                'thigh.L': ' L Thigh',
                'shin.L': ' L Calf',
                'foot.L': ' L Foot',
                'toe.L': ' L Toe0',
                
                # Right leg
                'thigh.R': ' R Thigh',
                'shin.R': ' R Calf',
                'foot.R': ' R Foot',
                'toe.R': ' R Toe0',
            },
            
            "weight_influences": [
                # LEFT HAND
                ['hand.L', 'thumb.01.L'],
                ['hand.L', 'thumb.02.L'],
                ['f_index.01.L', 'f_middle.01.L'],
                ['f_index.01.L', 'f_ring.01.L'],
                ['f_index.01.L', 'f_pinky.01.L'],
                ['f_index.02.L', 'f_middle.02.L'],
                ['f_index.02.L', 'f_ring.02.L'],
                ['f_index.02.L', 'f_pinky.02.L'],
                
                # RIGHT HAND
                ['hand.R', 'thumb.01.R'],
                ['hand.R', 'thumb.02.R'],
                ['f_index.01.R', 'f_middle.01.R'],
                ['f_index.01.R', 'f_ring.01.R'],
                ['f_index.01.R', 'f_pinky.01.R'],
                ['f_index.02.R', 'f_middle.02.R'],
                ['f_index.02.R', 'f_ring.02.R'],
                ['f_index.02.R', 'f_pinky.02.R'],
            ],
            
            "bones_to_delete": [
                'f_middle.01.L', 'f_ring.01.L', 'f_pinky.01.L',
                'f_middle.02.L', 'f_ring.02.L', 'f_pinky.02.L',
                'f_middle.01.R', 'f_ring.01.R', 'f_pinky.01.R',
                'f_middle.02.R', 'f_ring.02.R', 'f_pinky.02.R',
                'MCH-spine', 'MCH-spine.001', 'MCH-spine.002',
            ]
        }
    
    # ============================================================================
    # PERFIL VALVE BIPED (Source Engine alternativo)
    # ============================================================================
    def _get_valve_biped_profile(self):
        """Perfil para ValveBiped (algunos juegos de Source)"""
        return {
            "name": "ValveBiped",
            "description": "Valve Biped (some Source games)",
            "detection_patterns": ["ValveBiped."],
            "confidence_threshold": 0.8,
            
            "bone_mapping": {
                # Core skeleton
                'ValveBiped.Bip01_Pelvis': ' Pelvis',
                'ValveBiped.Bip01_Spine': ' Spine',
                'ValveBiped.Bip01_Spine1': ' Spine1',
                'ValveBiped.Bip01_Spine2': ' Spine1',
                'ValveBiped.Bip01_Spine3': ' Spine1',
                'ValveBiped.Bip01_Neck1': ' Neck',
                'ValveBiped.Bip01_Head1': ' Head',
                
                # Left arm
                'ValveBiped.Bip01_L_Clavicle': 'Bip01 L Clavicle',
                'ValveBiped.Bip01_L_UpperArm': ' L UpperArm',
                'ValveBiped.Bip01_L_Forearm': ' L Forearm',
                'ValveBiped.Bip01_L_Hand': ' L Hand',
                'ValveBiped.Bip01_L_Finger0': ' L Finger',
                'ValveBiped.Bip01_L_Finger01': 'L Finger01',
                'ValveBiped.Bip01_L_Finger1': ' L Finger',
                'ValveBiped.Bip01_L_Finger11': 'L Finger01',
                
                # Right arm
                'ValveBiped.Bip01_R_Clavicle': 'Bip01 R Clavicle',
                'ValveBiped.Bip01_R_UpperArm': ' R UpperArm',
                'ValveBiped.Bip01_R_Forearm': ' R Forearm',
                'ValveBiped.Bip01_R_Hand': ' R Hand',
                'ValveBiped.Bip01_R_Finger0': ' R Finger',
                'ValveBiped.Bip01_R_Finger01': 'R Finger01',
                'ValveBiped.Bip01_R_Finger1': ' R Finger',
                'ValveBiped.Bip01_R_Finger11': 'R Finger01',
                
                # Left leg
                'ValveBiped.Bip01_L_Thigh': ' L Thigh',
                'ValveBiped.Bip01_L_Calf': ' L Calf',
                'ValveBiped.Bip01_L_Foot': ' L Foot',
                'ValveBiped.Bip01_L_Toe0': ' L Toe0',
                
                # Right leg
                'ValveBiped.Bip01_R_Thigh': ' R Thigh',
                'ValveBiped.Bip01_R_Calf': ' R Calf',
                'ValveBiped.Bip01_R_Foot': ' R Foot',
                'ValveBiped.Bip01_R_Toe0': ' R Toe0',
            },
            
            "weight_influences": [
                # Twist bones
                ['ValveBiped.Bip01_L_UpperArm', 'ValveBiped.Bip01_L_UpperArm_Twist'],
                ['ValveBiped.Bip01_R_UpperArm', 'ValveBiped.Bip01_R_UpperArm_Twist'],
                ['ValveBiped.Bip01_L_Forearm', 'ValveBiped.Bip01_L_Forearm_Twist'],
                ['ValveBiped.Bip01_R_Forearm', 'ValveBiped.Bip01_R_Forearm_Twist'],
                
                # Finger consolidation
                ['ValveBiped.Bip01_L_Hand', 'ValveBiped.Bip01_L_Finger0'],
                ['ValveBiped.Bip01_L_Finger1', 'ValveBiped.Bip01_L_Finger2'],
                ['ValveBiped.Bip01_L_Finger1', 'ValveBiped.Bip01_L_Finger3'],
                ['ValveBiped.Bip01_L_Finger1', 'ValveBiped.Bip01_L_Finger4'],
                ['ValveBiped.Bip01_R_Hand', 'ValveBiped.Bip01_R_Finger0'],
                ['ValveBiped.Bip01_R_Finger1', 'ValveBiped.Bip01_R_Finger2'],
                ['ValveBiped.Bip01_R_Finger1', 'ValveBiped.Bip01_R_Finger3'],
                ['ValveBiped.Bip01_R_Finger1', 'ValveBiped.Bip01_R_Finger4'],
            ],
            
            "bones_to_delete": [
                'ValveBiped.Bip01_L_UpperArm_Twist', 'ValveBiped.Bip01_R_UpperArm_Twist',
                'ValveBiped.Bip01_L_Forearm_Twist', 'ValveBiped.Bip01_R_Forearm_Twist',
                'ValveBiped.Bip01_L_Finger2', 'ValveBiped.Bip01_L_Finger3', 'ValveBiped.Bip01_L_Finger4',
                'ValveBiped.Bip01_R_Finger2', 'ValveBiped.Bip01_R_Finger3', 'ValveBiped.Bip01_R_Finger4',
            ]
        }