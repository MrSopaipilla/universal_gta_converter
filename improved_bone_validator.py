"""
Validador de huesos mejorado con lógica robusta
improved_bone_validator.py - Universal GTA SA Converter v4.0.1
"""

import bpy

class ImprovedBoneValidator:
    """Validador robusto que maneja problemas comunes de detección"""
    
    OFFICIAL_GTA_SA_BONES = [
        "Root", " Pelvis", " Spine", " Spine1", " Neck", " Head", "Jaw",
        "L Brow", "R Brow", "Bip01 L Clavicle", " L UpperArm", " L ForeArm", 
        " L Hand", " L Finger", "L Finger01", "Bip01 R Clavicle", " R UpperArm",
        " R ForeArm", " R Hand", " R Finger", "R Finger01", "L breast",
        "R breast", "Belly", " L Thigh", " L Calf", " L Foot", " L Toe0",
        " R Thigh", " R Calf", " R Foot", " R Toe0"
    ]
    
    @classmethod
    def get_armature_bones_robust(cls, armature_obj):
        """Obtener huesos de armature con múltiples métodos de respaldo"""
        if not armature_obj or armature_obj.type != 'ARMATURE':
            return []
        
        bones = []
        
        # Método 1: pose.bones (más confiable)
        try:
            if armature_obj.pose and armature_obj.pose.bones:
                bones = [b.name for b in armature_obj.pose.bones]
                print(f"[VALIDATOR] Método pose.bones: {len(bones)} huesos")
                return bones
        except Exception as e:
            print(f"[VALIDATOR] Error con pose.bones: {e}")
        
        # Método 2: data.bones (respaldo)
        try:
            if armature_obj.data and armature_obj.data.bones:
                bones = [b.name for b in armature_obj.data.bones]
                print(f"[VALIDATOR] Método data.bones: {len(bones)} huesos")
                return bones
        except Exception as e:
            print(f"[VALIDATOR] Error con data.bones: {e}")
        
        # Método 3: edit_bones (último recurso)
        try:
            original_active = bpy.context.view_layer.objects.active
            original_mode = bpy.context.mode
            
            bpy.context.view_layer.objects.active = armature_obj
            
            if original_mode != 'EDIT_ARMATURE':
                bpy.ops.object.mode_set(mode='EDIT')
                bones = [b.name for b in armature_obj.data.edit_bones]
                bpy.ops.object.mode_set(mode='OBJECT')
            else:
                bones = [b.name for b in armature_obj.data.edit_bones]
            
            if original_active:
                bpy.context.view_layer.objects.active = original_active
            
            print(f"[VALIDATOR] Método edit_bones: {len(bones)} huesos")
            return bones
            
        except Exception as e:
            print(f"[VALIDATOR] Error con edit_bones: {e}")
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
        
        print(f"[VALIDATOR] ⚠️ No se pudieron obtener huesos de {armature_obj.name}")
        return []
    
    @classmethod
    def bone_exists_flexible(cls, bone_name, bone_list):
        """Verificación flexible de existencia de hueso con múltiples criterios"""
        if not bone_name or not bone_list:
            return False
        
        # 1. Coincidencia exacta
        if bone_name in bone_list:
            return True
        
        # 2. Coincidencia con espacios normalizados
        bone_clean = bone_name.strip()
        for bone in bone_list:
            if bone.strip() == bone_clean:
                return True
        
        # 3. Coincidencia case-insensitive
        bone_lower = bone_name.lower()
        for bone in bone_list:
            if bone.lower() == bone_lower:
                return True
        
        # 4. Coincidencia con espacios diferentes
        for bone in bone_list:
            # Comparar versiones sin espacios
            if bone_clean.lower() == bone.strip().lower():
                return True
        
        # 5. Coincidencia parcial estricta (para casos específicos)
        if len(bone_name) > 5:  # Solo para nombres largos
            bone_words = bone_name.lower().split()
            for bone in bone_list:
                bone_words_list = bone.lower().split()
                if bone_words == bone_words_list:
                    return True
        
        return False
    
    @classmethod
    def find_best_match(cls, target_bone, available_bones):
        """Encontrar la mejor coincidencia para un hueso target"""
        if not target_bone or not available_bones:
            return None
        
        # Buscar coincidencias con diferentes niveles de precisión
        matches = []
        
        for bone in available_bones:
            score = 0
            
            # Coincidencia exacta
            if bone == target_bone:
                return bone
            
            # Coincidencia sin espacios
            if bone.strip() == target_bone.strip():
                score += 10
            
            # Coincidencia case-insensitive
            if bone.lower() == target_bone.lower():
                score += 8
            
            # Coincidencia sin espacios y case-insensitive
            if bone.strip().lower() == target_bone.strip().lower():
                score += 6
            
            # Coincidencia parcial
            if target_bone.lower() in bone.lower() or bone.lower() in target_bone.lower():
                score += 3
            
            if score > 0:
                matches.append((bone, score))
        
        # Devolver la mejor coincidencia
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            best_match, best_score = matches[0]
            
            if best_score >= 6:  # Umbral mínimo de confianza
                return best_match
        
        return None
    
    @classmethod
    def validate_mapping_robust(cls, source_bone, target_bone, source_armature, target_armature):
        """Validación robusta de un mapeo individual"""
        issues = []
        
        # Validar target bone
        if not target_bone:
            issues.append("Target bone vacío")
        else:
            target_bones = cls.get_armature_bones_robust(target_armature)
            if not cls.bone_exists_flexible(target_bone, target_bones):
                # Buscar alternativa
                alternative = cls.find_best_match(target_bone, target_bones)
                if alternative:
                    issues.append(f"Target '{target_bone}' no existe, posible alternativa: '{alternative}'")
                else:
                    issues.append(f"Target '{target_bone}' no existe")
        
        # Validar source bone (si hay source armature)
        if source_armature and source_bone:
            source_bones = cls.get_armature_bones_robust(source_armature)
            if not cls.bone_exists_flexible(source_bone, source_bones):
                alternative = cls.find_best_match(source_bone, source_bones)
                if alternative:
                    issues.append(f"Source '{source_bone}' no existe, posible alternativa: '{alternative}'")
                else:
                    issues.append(f"Source '{source_bone}' no existe")
        elif not source_bone:
            issues.append("Source bone vacío")
        
        return len(issues) == 0, issues
    
    @classmethod
    def auto_fix_mapping(cls, source_bone, target_bone, source_armature, target_armature):
        """Auto-corrección de mapeo con huesos similares"""
        fixed_source = source_bone
        fixed_target = target_bone
        fixes_applied = []
        
        # Corregir target
        if target_armature:
            target_bones = cls.get_armature_bones_robust(target_armature)
            if not cls.bone_exists_flexible(target_bone, target_bones):
                alternative = cls.find_best_match(target_bone, target_bones)
                if alternative:
                    fixed_target = alternative
                    fixes_applied.append(f"Target: '{target_bone}' -> '{alternative}'")
        
        # Corregir source
        if source_armature and source_bone:
            source_bones = cls.get_armature_bones_robust(source_armature)
            if not cls.bone_exists_flexible(source_bone, source_bones):
                alternative = cls.find_best_match(source_bone, source_bones)
                if alternative:
                    fixed_source = alternative
                    fixes_applied.append(f"Source: '{source_bone}' -> '{alternative}'")
        
        return fixed_source, fixed_target, fixes_applied
    
    @classmethod
    def diagnostic_report(cls, armature_obj):
        """Generar reporte diagnóstico de un armature"""
        if not armature_obj:
            return "No armature specified"
        
        report = []
        report.append(f"🔍 DIAGNOSTIC REPORT: {armature_obj.name}")
        report.append("=" * 40)
        
        bones = cls.get_armature_bones_robust(armature_obj)
        report.append(f"Total bones found: {len(bones)}")
        
        # Comparar con huesos oficiales GTA SA
        official_found = []
        for bone in bones:
            if bone in cls.OFFICIAL_GTA_SA_BONES:
                official_found.append(bone)
        
        coverage = (len(official_found) / len(cls.OFFICIAL_GTA_SA_BONES)) * 100
        report.append(f"GTA SA coverage: {coverage:.1f}% ({len(official_found)}/{len(cls.OFFICIAL_GTA_SA_BONES)})")
        
        # Mostrar primeros 10 huesos con análisis
        report.append("\nFirst 10 bones (detailed):")
        for i, bone in enumerate(bones[:10]):
            is_official = "✅" if bone in cls.OFFICIAL_GTA_SA_BONES else "❓"
            report.append(f"  {i+1:2d}. {is_official} {repr(bone)}")
        
        if len(bones) > 10:
            report.append(f"  ... and {len(bones) - 10} more bones")
        
        return "\n".join(report)

def test_improved_validator():
    """Probar el validador mejorado"""
    print("🧪 TESTING IMPROVED BONE VALIDATOR")
    print("=" * 50)
    
    try:
        settings = bpy.context.scene.universal_gta_settings
        
        if settings.target_armature:
            report = ImprovedBoneValidator.diagnostic_report(settings.target_armature)
            print(report)
            
            # Probar algunos mapeos
            if len(settings.bone_mappings) > 0:
                print("\n🔍 TESTING CURRENT MAPPINGS:")
                for i, mapping in enumerate(settings.bone_mappings[:5]):  # Primeros 5
                    is_valid, issues = ImprovedBoneValidator.validate_mapping_robust(
                        mapping.source_bone,
                        mapping.target_bone, 
                        settings.source_armature,
                        settings.target_armature
                    )
                    
                    status = "✅" if is_valid else "❌"
                    print(f"  {status} Mapping {i+1}: {mapping.source_bone} -> {mapping.target_bone}")
                    
                    if issues:
                        for issue in issues:
                            print(f"    ⚠️ {issue}")
        else:
            print("❌ No target armature selected")
    
    except Exception as e:
        print(f"❌ Error testing validator: {e}")

if __name__ == "__main__":
    test_improved_validator()
