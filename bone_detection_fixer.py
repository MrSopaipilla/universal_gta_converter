#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BONE DETECTION FIXER - Universal GTA SA Converter v4.0.1
=========================================================
DIAGNOSTICA Y CORRIGE problemas de detección de huesos target:

PROBLEMAS COMUNES:
❌ Huesos existentes no reconocidos
❌ Validación demasiado estricta
❌ Problemas de encoding/espacios invisibles
❌ Lógica de comparación incorrecta
❌ Acceso incorrecto a datos del armature

SOLUCIONES:
✅ Diagnóstico completo de huesos reales vs esperados
✅ Corrección de lógica de validación
✅ Manejo robusto de espacios y encoding
✅ Validación flexible pero precisa
✅ Logging detallado para debug
"""

import os
import shutil
from pathlib import Path

class BoneDetectionDiagnostic:
    """Diagnóstico completo del sistema de detección de huesos"""
    
    def __init__(self):
        self.addon_root = Path(__file__).parent
        self.backup_dir = self.addon_root / "detection_backups"
        self.issues_found = []
        self.fixes_applied = []
        
        print("🔍 BONE DETECTION DIAGNOSTIC - Universal GTA SA Converter")
        print("=" * 60)
    
    def create_diagnostic_script(self):
        """Crear script de diagnóstico para ejecutar en Blender"""
        print("\n🔬 CREATING: bone_detection_diagnostic.py")
        
        diagnostic_content = '''#!/usr/bin/env python3
"""
BONE DETECTION DIAGNOSTIC
Ejecutar en Blender para diagnosticar problemas de detección
"""

import bpy
import json

def diagnose_armature_bones(armature_obj):
    """Diagnosticar huesos de un armature específico"""
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return None
    
    print(f"\\n🔍 DIAGNOSTICANDO: {armature_obj.name}")
    print("-" * 40)
    
    # Obtener huesos de diferentes formas para comparar
    bone_sources = {
        "data.bones": [b.name for b in armature_obj.data.bones],
        "pose.bones": [b.name for b in armature_obj.pose.bones] if armature_obj.pose else [],
        "data.edit_bones": []  # Requiere modo edit
    }
    
    # Obtener edit_bones si es posible
    try:
        bpy.context.view_layer.objects.active = armature_obj
        original_mode = bpy.context.mode
        
        if original_mode != 'EDIT_ARMATURE':
            bpy.ops.object.mode_set(mode='EDIT')
            bone_sources["data.edit_bones"] = [b.name for b in armature_obj.data.edit_bones]
            bpy.ops.object.mode_set(mode='OBJECT')
        else:
            bone_sources["data.edit_bones"] = [b.name for b in armature_obj.data.edit_bones]
            
    except Exception as e:
        print(f"⚠️ No se pudo acceder a edit_bones: {e}")
    
    # Mostrar resultados
    total_bones = len(bone_sources["data.bones"])
    print(f"📊 Total huesos encontrados: {total_bones}")
    
    for source_name, bone_list in bone_sources.items():
        if bone_list:
            print(f"\\n📋 {source_name}: {len(bone_list)} huesos")
            
            # Mostrar primeros 10 con encoding detallado
            for i, bone_name in enumerate(bone_list[:10]):
                # Análisis detallado del nombre
                repr_name = repr(bone_name)
                starts_with_space = bone_name.startswith(' ')
                byte_length = len(bone_name.encode('utf-8'))
                char_length = len(bone_name)
                
                print(f"  {i+1:2d}. {repr_name:<25} | Space: {starts_with_space} | Bytes: {byte_length} | Chars: {char_length}")
            
            if len(bone_list) > 10:
                print(f"     ... y {len(bone_list) - 10} huesos más")
    
    return bone_sources

def compare_with_official_gta_bones(actual_bones):
    """Comparar huesos reales con lista oficial GTA SA"""
    
    # Lista oficial GTA SA
    OFFICIAL_GTA_SA_BONES = [
        "Root", " Pelvis", " Spine", " Spine1", " Neck", " Head", "Jaw",
        "L Brow", "R Brow", "Bip01 L Clavicle", " L UpperArm", " L ForeArm", 
        " L Hand", " L Finger", "L Finger01", "Bip01 R Clavicle", " R UpperArm",
        " R ForeArm", " R Hand", " R Finger", "R Finger01", "L breast",
        "R breast", "Belly", " L Thigh", " L Calf", " L Foot", " L Toe0",
        " R Thigh", " R Calf", " R Foot", " R Toe0"
    ]
    
    print("\\n🔍 COMPARACIÓN CON HUESOS OFICIALES GTA SA")
    print("=" * 50)
    
    found_official = []
    missing_official = []
    extra_bones = []
    possible_matches = []
    
    for official_bone in OFFICIAL_GTA_SA_BONES:
        if official_bone in actual_bones:
            found_official.append(official_bone)
        else:
            missing_official.append(official_bone)
            
            # Buscar posibles coincidencias
            matches = []
            official_clean = official_bone.strip().lower()
            
            for actual_bone in actual_bones:
                actual_clean = actual_bone.strip().lower()
                
                # Coincidencia exacta sin espacios
                if official_clean == actual_clean:
                    matches.append(f"'{actual_bone}' (espacios diferentes)")
                # Coincidencia parcial
                elif official_clean in actual_clean or actual_clean in official_clean:
                    matches.append(f"'{actual_bone}' (parcial)")
            
            if matches:
                possible_matches.append((official_bone, matches))
    
    # Huesos extra (no oficiales)
    for actual_bone in actual_bones:
        if actual_bone not in OFFICIAL_GTA_SA_BONES:
            extra_bones.append(actual_bone)
    
    # Reporte detallado
    print(f"✅ Huesos oficiales encontrados: {len(found_official)}/{len(OFFICIAL_GTA_SA_BONES)}")
    print(f"❌ Huesos oficiales faltantes: {len(missing_official)}")
    print(f"➕ Huesos extra (no oficiales): {len(extra_bones)}")
    
    if found_official:
        print("\\n✅ HUESOS OFICIALES ENCONTRADOS:")
        for bone in found_official:
            print(f"  ✓ {repr(bone)}")
    
    if missing_official:
        print("\\n❌ HUESOS OFICIALES FALTANTES:")
        for bone in missing_official:
            print(f"  ✗ {repr(bone)}")
    
    if possible_matches:
        print("\\n🔍 POSIBLES COINCIDENCIAS PARA HUESOS FALTANTES:")
        for missing_bone, matches in possible_matches:
            print(f"  {repr(missing_bone)} podría ser:")
            for match in matches:
                print(f"    → {match}")
    
    if extra_bones:
        print("\\n➕ HUESOS EXTRA (no en lista oficial):")
        for i, bone in enumerate(extra_bones[:10]):  # Primeros 10
            print(f"  + {repr(bone)}")
        if len(extra_bones) > 10:
            print(f"    ... y {len(extra_bones) - 10} más")
    
    return {
        "found_official": found_official,
        "missing_official": missing_official, 
        "extra_bones": extra_bones,
        "possible_matches": possible_matches,
        "coverage_percentage": (len(found_official) / len(OFFICIAL_GTA_SA_BONES)) * 100
    }

def test_current_mapping_validation():
    """Probar el sistema actual de validación de mapeos"""
    print("\\n🧪 TESTING CURRENT MAPPING VALIDATION")
    print("=" * 50)
    
    try:
        settings = bpy.context.scene.universal_gta_settings
        
        if not settings.target_armature:
            print("❌ No hay target armature seleccionado")
            return False
        
        target_bones = [b.name for b in settings.target_armature.data.bones]
        print(f"Target armature: {settings.target_armature.name}")
        print(f"Huesos disponibles: {len(target_bones)}")
        
        # Probar mapeos existentes
        if len(settings.bone_mappings) > 0:
            print(f"\\nMapeos configurados: {len(settings.bone_mappings)}")
            
            valid_count = 0
            invalid_count = 0
            
            for i, mapping in enumerate(settings.bone_mappings):
                target_bone = mapping.target_bone
                source_bone = mapping.source_bone
                enabled = mapping.enabled
                
                # Verificar si target existe
                target_exists = target_bone in target_bones
                source_valid = bool(source_bone) if settings.source_armature else True
                
                status = "✅" if (target_exists and source_valid and enabled) else "❌"
                
                if target_exists and source_valid and enabled:
                    valid_count += 1
                else:
                    invalid_count += 1
                
                issues = []
                if not target_exists:
                    issues.append("target no existe")
                if not source_valid:
                    issues.append("source vacío")
                if not enabled:
                    issues.append("deshabilitado")
                
                issue_text = f" ({', '.join(issues)})" if issues else ""
                
                print(f"  {status} #{i+1}: {repr(source_bone)} -> {repr(target_bone)}{issue_text}")
            
            print(f"\\n📊 Resumen: {valid_count} válidos, {invalid_count} con problemas")
            
            if invalid_count > 0:
                print("\\n💡 RECOMENDACIONES:")
                print("1. Verificar que los nombres de target bones coincidan exactamente")
                print("2. Usar el diagnóstico de comparación arriba")
                print("3. Ejecutar auto-corrección si está disponible")
        
        else:
            print("⚠️ No hay mapeos configurados")
            print("💡 Usa 'Smart Auto-Detect' o 'Add Target Bones'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando validación: {e}")
        return False

def run_full_diagnostic():
    """Ejecutar diagnóstico completo"""
    print("🔬 BONE DETECTION FULL DIAGNOSTIC")
    print("=" * 60)
    
    try:
        settings = bpy.context.scene.universal_gta_settings
        
        # Diagnosticar source armature
        if settings.source_armature:
            print("\\n1️⃣ SOURCE ARMATURE:")
            source_bones = diagnose_armature_bones(settings.source_armature)
        else:
            print("\\n1️⃣ SOURCE ARMATURE: No seleccionado")
            source_bones = None
        
        # Diagnosticar target armature  
        if settings.target_armature:
            print("\\n2️⃣ TARGET ARMATURE:")
            target_bones = diagnose_armature_bones(settings.target_armature)
            
            if target_bones and target_bones["data.bones"]:
                print("\\n3️⃣ COMPARACIÓN CON GTA SA:")
                comparison = compare_with_official_gta_bones(target_bones["data.bones"])
                
                print(f"\\n📊 COBERTURA GTA SA: {comparison['coverage_percentage']:.1f}%")
                
                if comparison['coverage_percentage'] < 80:
                    print("⚠️ Baja cobertura - Este armature podría no ser GTA SA estándar")
                elif comparison['coverage_percentage'] > 95:
                    print("✅ Excelente cobertura - Armature GTA SA válido")
                else:
                    print("✅ Buena cobertura - Armature GTA SA con algunas diferencias")
        else:
            print("\\n2️⃣ TARGET ARMATURE: No seleccionado")
            target_bones = None
        
        # Probar sistema de validación actual
        print("\\n4️⃣ SISTEMA DE VALIDACIÓN:")
        test_current_mapping_validation()
        
        print("\\n" + "=" * 60)
        print("📋 DIAGNÓSTICO COMPLETADO")
        print("💡 Si hay problemas, ejecuta fix_bone_detection_system.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_full_diagnostic()
'''
        
        try:
            diagnostic_file = self.addon_root / "bone_detection_diagnostic.py"
            with open(diagnostic_file, 'w', encoding='utf-8') as f:
                f.write(diagnostic_content)
            
            print("✅ bone_detection_diagnostic.py creado")
            return True
            
        except Exception as e:
            self.issues_found.append(f"Error creando diagnostic: {e}")
            return False
    
    def fix_validation_operators(self):
        """Corregir operadores de validación para ser menos estrictos"""
        print("\n🔧 FIXING: Validation operators (menos restrictivos)")
        
        files_to_fix = [
            "operators/conversion.py",
            "operators/mapping.py", 
            "operators/validation_fixed.py"
        ]
        
        for file_name in files_to_fix:
            file_path = self.addon_root / file_name
            
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Backup
                self.create_backup(file_path)
                
                # Corregir validaciones demasiado estrictas
                fixes_applied = []
                
                # 1. Mejorar acceso a huesos
                old_pattern = "settings.target_armature.data.bones"
                new_pattern = "settings.target_armature.pose.bones"
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    fixes_applied.append("Acceso a pose.bones en lugar de data.bones")
                
                # 2. Manejo robusto de espacios
                old_validation = 'mapping.target_bone in tgt_bones'
                new_validation = 'self.bone_exists_flexible(mapping.target_bone, tgt_bones)'
                if old_validation in content and new_validation not in content:
                    # Agregar función helper
                    helper_function = '''
    def bone_exists_flexible(self, bone_name, bone_list):
        """Verificación flexible de existencia de hueso"""
        if not bone_name:
            return False
        
        # Coincidencia exacta
        if bone_name in bone_list:
            return True
        
        # Coincidencia con espacios normalizados
        bone_clean = bone_name.strip()
        for bone in bone_list:
            if bone.strip() == bone_clean:
                return True
        
        # Coincidencia case-insensitive
        bone_lower = bone_name.lower()
        for bone in bone_list:
            if bone.lower() == bone_lower:
                return True
        
        return False
'''
                    
                    # Insertar función después de la declaración de clase
                    lines = content.split('\n')
                    new_lines = []
                    class_found = False
                    
                    for line in lines:
                        new_lines.append(line)
                        
                        if 'class UNIVERSALGTA_OT_' in line and not class_found:
                            # Encontrar el primer método para insertar antes
                            for j, next_line in enumerate(lines[len(new_lines):], len(new_lines)):
                                if next_line.strip().startswith('def ') and j > len(new_lines):
                                    insert_idx = j
                                    break
                            else:
                                insert_idx = len(new_lines)
                            
                            new_lines.extend(helper_function.split('\n'))
                            class_found = True
                            break
                    
                    content = '\n'.join(new_lines)
                    
                    # Reemplazar validaciones
                    content = content.replace(old_validation, new_validation)
                    fixes_applied.append("Validación flexible de huesos")
                
                # 3. Mejorar manejo de errores
                old_error = 'self.report({\'ERROR\'}, f"Error accediendo a huesos: {str(e)}")'
                new_error = 'self.report({\'WARNING\'}, f"Problema accediendo a huesos: {str(e)}. Intentando alternativa...")'
                if old_error in content:
                    content = content.replace(old_error, new_error)
                    fixes_applied.append("Manejo de errores más tolerante")
                
                # 4. Agregar logging detallado
                if "print(f\"[" not in content and "def execute" in content:
                    # Buscar execute methods y agregar logging
                    lines = content.split('\n')
                    new_lines = []
                    
                    for line in lines:
                        new_lines.append(line)
                        
                        if 'def execute(self, context):' in line:
                            indent = ' ' * (len(line) - len(line.lstrip()) + 4)
                            log_line = f'{indent}print(f"[{{self.__class__.__name__}}] Ejecutando validación...")'
                            new_lines.append(log_line)
                    
                    content = '\n'.join(new_lines)
                    fixes_applied.append("Logging detallado agregado")
                
                # Escribir archivo corregido
                if fixes_applied:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.fixes_applied.append(f"{file_name}: {', '.join(fixes_applied)}")
                    print(f"✅ {file_name} corregido: {len(fixes_applied)} mejoras")
                
            except Exception as e:
                self.issues_found.append(f"Error corrigiendo {file_name}: {e}")
    
    def create_backup(self, file_path):
        """Crear backup de archivo"""
        try:
            if not self.backup_dir.exists():
                self.backup_dir.mkdir()
            
            backup_file = self.backup_dir / f"{file_path.name}.backup"
            shutil.copy2(file_path, backup_file)
            return True
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return False
    
    def create_improved_validator(self):
        """Crear validador mejorado con lógica robusta"""
        print("\n📦 CREATING: improved_bone_validator.py")
        
        validator_content = '''"""
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
        report.append("\\nFirst 10 bones (detailed):")
        for i, bone in enumerate(bones[:10]):
            is_official = "✅" if bone in cls.OFFICIAL_GTA_SA_BONES else "❓"
            report.append(f"  {i+1:2d}. {is_official} {repr(bone)}")
        
        if len(bones) > 10:
            report.append(f"  ... and {len(bones) - 10} more bones")
        
        return "\\n".join(report)

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
                print("\\n🔍 TESTING CURRENT MAPPINGS:")
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
'''
        
        try:
            validator_file = self.addon_root / "improved_bone_validator.py"
            with open(validator_file, 'w', encoding='utf-8') as f:
                f.write(validator_content)
            
            print("✅ improved_bone_validator.py creado")
            return True
            
        except Exception as e:
            self.issues_found.append(f"Error creando validator: {e}")
            return False
    
    def run_all_fixes(self):
        """Ejecutar todas las correcciones"""
        print("🚀 EJECUTANDO CORRECCIONES DE DETECCIÓN DE HUESOS...")
        print("=" * 60)
        
        fixes = [
            ("Diagnostic script", self.create_diagnostic_script),
            ("Validation operators", self.fix_validation_operators),
            ("Improved validator", self.create_improved_validator),
        ]
        
        successful = 0
        
        for fix_name, fix_func in fixes:
            print(f"\n{'='*15} {fix_name} {'='*15}")
            try:
                if fix_func():
                    successful += 1
                    print(f"✅ {fix_name} completado")
                else:
                    print(f"❌ {fix_name} falló")
            except Exception as e:
                print(f"💥 {fix_name} error: {e}")
                self.issues_found.append(f"{fix_name}: {e}")
        
        self.show_summary(successful, len(fixes))
    
    def show_summary(self, successful, total):
        """Mostrar resumen"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN CORRECCIONES DETECCIÓN DE HUESOS")
        print("=" * 60)
        
        print(f"✅ Correcciones exitosas: {successful}/{total}")
        print(f"🔧 Fixes aplicados: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            print("\\n🔧 MEJORAS APLICADAS:")
            for fix in self.fixes_applied:
                print(f"  • {fix}")
        
        if self.issues_found:
            print(f"\\n❌ Issues encontrados: {len(self.issues_found)}")
            for issue in self.issues_found:
                print(f"  • {issue}")
        
        print("\\n🎯 PRÓXIMOS PASOS:")
        print("1. Reiniciar Blender")
        print("2. Recargar addon")
        print("3. Ejecutar en Blender:")
        print("   exec(open('bone_detection_diagnostic.py').read())")
        print("4. Revisar el diagnóstico detallado")
        print("5. Usar el validador mejorado si hay problemas")
        
        print("\\n📋 ARCHIVOS CREADOS:")
        print("• bone_detection_diagnostic.py - Diagnóstico completo")
        print("• improved_bone_validator.py - Validador robusto")
        
        print("\\n💾 Backups en: detection_backups/")
        print("=" * 60)

if __name__ == "__main__":
    fixer = BoneDetectionDiagnostic()
    fixer.run_all_fixes()
    
    print("\\n⏸️ Presiona Enter para continuar...")
    input()
