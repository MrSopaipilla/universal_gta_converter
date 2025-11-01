#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON MAPPING SYSTEM FIXER - Universal GTA SA Converter v4.0.1
==============================================================
CORRIGE PROBLEMAS CRÍTICOS:
1. ❌ No preserva espaciado original de huesos GTA SA 
2. ❌ Dependencia del nombre del armature source
3. ❌ Falta validación contra huesos oficiales GTA SA

SOLUCIONES:
✅ Lista oficial de huesos GTA SA con espacios correctos
✅ Normalización automática de nombres de huesos
✅ Save/Load independiente del nombre de armature
✅ Validación y corrección automática
"""

import os
import json
import shutil
from pathlib import Path

class GTASABoneValidator:
    """Validador y normalizador de huesos GTA SA"""
    
    # LISTA OFICIAL DE HUESOS GTA SA CON ESPACIOS EXACTOS
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
    
    def __init__(self):
        self.bone_variations = self._create_bone_variations_map()
        print(f"[VALIDATOR] Inicializado con {len(self.OFFICIAL_GTA_SA_BONES)} huesos oficiales GTA SA")
    
    def _create_bone_variations_map(self):
        """Crear mapeo de variaciones comunes a nombres oficiales"""
        variations = {}
        
        for official_bone in self.OFFICIAL_GTA_SA_BONES:
            # Versión sin espacios
            clean_name = official_bone.strip()
            variations[clean_name] = official_bone
            variations[clean_name.lower()] = official_bone
            
            # Versión original
            variations[official_bone] = official_bone
            variations[official_bone.lower()] = official_bone
            
            # Variaciones comunes
            if official_bone.startswith(" "):
                # Sin espacio inicial
                no_space = official_bone[1:]
                variations[no_space] = official_bone
                variations[no_space.lower()] = official_bone
                
                # Con diferentes espacios
                variations[f"  {no_space}"] = official_bone  # Doble espacio
                variations[f"\t{no_space}"] = official_bone  # Tab
            
            # Variaciones específicas conocidas
            specific_variations = {
                "Pelvis": " Pelvis",
                "pelvis": " Pelvis", 
                "Hip": " Pelvis",
                "hip": " Pelvis",
                "Hips": " Pelvis",
                "hips": " Pelvis",
                
                "Spine": " Spine",
                "spine": " Spine",
                "Back": " Spine",
                "back": " Spine",
                
                "Spine1": " Spine1",
                "spine1": " Spine1",
                "Chest": " Spine1",
                "chest": " Spine1",
                "Upper_Spine": " Spine1",
                
                "Neck": " Neck",
                "neck": " Neck",
                "Cervical": " Neck",
                
                "Head": " Head",
                "head": " Head",
                "Skull": " Head",
                "skull": " Head",
                
                "UpperArm.L": " L UpperArm",
                "upperarm.l": " L UpperArm",
                "Arm.L": " L UpperArm",
                "L_UpperArm": " L UpperArm",
                "L_Arm": " L UpperArm",
                "Left_UpperArm": " L UpperArm",
                
                "ForeArm.L": " L ForeArm",
                "forearm.l": " L ForeArm", 
                "LowerArm.L": " L ForeArm",
                "L_ForeArm": " L ForeArm",
                "L_LowerArm": " L ForeArm",
                
                "Hand.L": " L Hand",
                "hand.l": " L Hand",
                "L_Hand": " L Hand",
                "Left_Hand": " L Hand",
                
                "Thigh.L": " L Thigh",
                "thigh.l": " L Thigh",
                "Leg.L": " L Thigh",
                "L_Thigh": " L Thigh",
                "L_Leg": " L Thigh",
                "UpperLeg.L": " L Thigh",
                
                "Calf.L": " L Calf",
                "calf.l": " L Calf",
                "Shin.L": " L Calf",
                "LowerLeg.L": " L Calf",
                "L_Calf": " L Calf",
                "L_Shin": " L Calf",
                
                "Foot.L": " L Foot",
                "foot.l": " L Foot",
                "L_Foot": " L Foot",
                "Left_Foot": " L Foot",
                
                "Toe.L": " L Toe0",
                "toe.l": " L Toe0",
                "L_Toe": " L Toe0",
                "L_Toe0": " L Toe0",
            }
            
            variations.update(specific_variations)
        
        return variations
    
    def normalize_bone_name(self, bone_name):
        """Normalizar nombre de hueso a oficial GTA SA"""
        if not bone_name:
            return None
        
        # Buscar coincidencia exacta primero
        if bone_name in self.OFFICIAL_GTA_SA_BONES:
            return bone_name
        
        # Buscar en variaciones
        if bone_name in self.bone_variations:
            return self.bone_variations[bone_name]
        
        # Buscar case-insensitive
        bone_lower = bone_name.lower()
        if bone_lower in self.bone_variations:
            return self.bone_variations[bone_lower]
        
        # Buscar por similitud parcial para lados R/L
        if bone_name.endswith('.R') or bone_name.endswith('.r'):
            # Convertir formato .R a R
            base_name = bone_name[:-2]
            for official in self.OFFICIAL_GTA_SA_BONES:
                if 'R ' in official and base_name.lower() in official.lower():
                    return official
        
        if bone_name.endswith('.L') or bone_name.endswith('.l'):
            # Convertir formato .L a L
            base_name = bone_name[:-2]
            for official in self.OFFICIAL_GTA_SA_BONES:
                if 'L ' in official and base_name.lower() in official.lower():
                    return official
        
        # No se pudo normalizar
        return None
    
    def validate_bone_name(self, bone_name):
        """Validar si un nombre de hueso es oficial GTA SA"""
        return bone_name in self.OFFICIAL_GTA_SA_BONES
    
    def get_invalid_bones(self, bone_list):
        """Obtener lista de huesos inválidos"""
        return [bone for bone in bone_list if not self.validate_bone_name(bone)]
    
    def suggest_corrections(self, invalid_bone):
        """Sugerir correcciones para hueso inválido"""
        suggestions = []
        
        # Buscar normalización
        normalized = self.normalize_bone_name(invalid_bone)
        if normalized:
            suggestions.append(normalized)
        
        # Buscar similares por substring
        invalid_lower = invalid_bone.lower()
        for official in self.OFFICIAL_GTA_SA_BONES:
            if len(invalid_bone) > 3 and invalid_lower in official.lower():
                if official not in suggestions:
                    suggestions.append(official)
        
        return suggestions[:3]  # Máximo 3 sugerencias


class JSONMappingFixer:
    """Corrector del sistema JSON de mapeos"""
    
    def __init__(self):
        self.addon_root = Path(__file__).parent
        self.validator = GTASABoneValidator()
        self.backup_dir = self.addon_root / "json_backups"
        self.fixed_files = []
        self.errors = []
        
        print(f"[JSON_FIXER] Inicializado en: {self.addon_root}")
    
    def create_backup(self, file_path):
        """Crear backup del archivo original"""
        try:
            if not self.backup_dir.exists():
                self.backup_dir.mkdir()
            
            backup_file = self.backup_dir / f"{file_path.name}.backup"
            shutil.copy2(file_path, backup_file)
            print(f"💾 Backup: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return False
    
    def fix_mapping_operators(self):
        """Corregir operadores de mapeo para preservar espacios GTA SA"""
        print("\n🔧 FIXING: operators/mapping.py (preservar espacios)")
        file_path = self.addon_root / "operators" / "mapping.py"
        
        if not file_path.exists():
            self.errors.append("operators/mapping.py no existe")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar si ya tiene las correcciones
            if "GTASABoneValidator" in content:
                print("⚪ mapping.py ya está corregido")
                return True
            
            self.create_backup(file_path)
            
            # Buscar la clase UNIVERSALGTA_OT_save_mapping
            lines = content.split('\n')
            new_lines = []
            in_save_class = False
            save_class_indent = 0
            
            for i, line in enumerate(lines):
                if "class UNIVERSALGTA_OT_save_mapping" in line:
                    in_save_class = True
                    save_class_indent = len(line) - len(line.lstrip())
                    new_lines.append(line)
                    continue
                
                if in_save_class and line.strip() and len(line) - len(line.lstrip()) <= save_class_indent and not line.startswith(' ' * (save_class_indent + 1)):
                    # Fin de la clase save_mapping
                    in_save_class = False
                
                if in_save_class and 'def execute(self, context):' in line:
                    # Insertar validador antes del execute
                    indent = " " * (save_class_indent + 4)
                    validator_code = f'''
{indent}# LISTA OFICIAL GTA SA - PRESERVAR ESPACIOS EXACTOS
{indent}OFFICIAL_GTA_SA_BONES = [
{indent}    "Root", " Pelvis", " Spine", " Spine1", " Neck", " Head", "Jaw",
{indent}    "L Brow", "R Brow", "Bip01 L Clavicle", " L UpperArm", " L ForeArm",
{indent}    " L Hand", " L Finger", "L Finger01", "Bip01 R Clavicle", " R UpperArm",
{indent}    " R ForeArm", " R Hand", " R Finger", "R Finger01", "L breast",
{indent}    "R breast", "Belly", " L Thigh", " L Calf", " L Foot", " L Toe0",
{indent}    " R Thigh", " R Calf", " R Foot", " R Toe0"
{indent}]
{indent}
{indent}def normalize_target_bone(self, target_bone):
{indent}    """Normalizar target bone a nombre oficial GTA SA"""
{indent}    if target_bone in self.OFFICIAL_GTA_SA_BONES:
{indent}        return target_bone
{indent}    
{indent}    # Buscar versión con espacio
{indent}    for official in self.OFFICIAL_GTA_SA_BONES:
{indent}        if official.strip() == target_bone.strip():
{indent}            return official
{indent}    
{indent}    return target_bone  # Devolver original si no encuentra
{indent}
'''
                    new_lines.append(validator_code)
                
                new_lines.append(line)
                
                # Modificar la sección donde se crea mapping_entry
                if in_save_class and '"target_bone": mapping.target_bone.strip(),' in line:
                    # Reemplazar con normalización
                    new_line = line.replace(
                        '"target_bone": mapping.target_bone.strip(),',
                        '"target_bone": self.normalize_target_bone(mapping.target_bone.strip()),'
                    )
                    new_lines[-1] = new_line
                
                # Eliminar dependencia del nombre del armature source  
                if in_save_class and '"source_armature": settings.source_armature.name' in line:
                    # Comentar esta línea
                    new_lines[-1] = line.replace(
                        '"source_armature": settings.source_armature.name',
                        '"source_armature": "Auto-Detected"  # No depender del nombre específico'
                    )
            
            # Escribir contenido corregido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            self.fixed_files.append(str(file_path))
            print("✅ mapping.py corregido (preservación de espacios)")
            return True
            
        except Exception as e:
            self.errors.append(f"Error corrigiendo mapping.py: {e}")
            return False
    
    def fix_load_mapping_operator(self):
        """Corregir operador de carga para validar huesos GTA SA"""
        print("\n🔧 FIXING: UNIVERSALGTA_OT_load_mapping (validación)")
        file_path = self.addon_root / "operators" / "mapping.py"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar la clase load_mapping y agregar validación
            lines = content.split('\n')
            new_lines = []
            in_load_class = False
            load_class_indent = 0
            
            for i, line in enumerate(lines):
                if "class UNIVERSALGTA_OT_load_mapping" in line:
                    in_load_class = True
                    load_class_indent = len(line) - len(line.lstrip())
                    new_lines.append(line)
                    continue
                
                if in_load_class and line.strip() and len(line) - len(line.lstrip()) <= load_class_indent and not line.startswith(' ' * (load_class_indent + 1)):
                    in_load_class = False
                
                new_lines.append(line)
                
                # Agregar validación después de cargar mapeos
                if in_load_class and 'new_mapping.target_bone = str(target_bone).strip()' in line:
                    indent = " " * (len(line) - len(line.lstrip()))
                    validation_code = f'''
{indent}# VALIDAR Y NORMALIZAR TARGET BONE
{indent}normalized_target = self.normalize_target_bone(str(target_bone).strip())
{indent}new_mapping.target_bone = normalized_target
{indent}
{indent}if normalized_target != str(target_bone).strip():
{indent}    print(f"[LOAD_MAPPING] Target normalizado: '{{str(target_bone).strip()}}' -> '{{normalized_target}}'")
'''
                    new_lines.extend(validation_code.split('\n'))
                    # Quitar la línea original que ya se reemplazó
                    new_lines[-len(validation_code.split('\n'))-1] = f"{indent}# Original target_bone line replaced above"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print("✅ load_mapping corregido (validación)")
            return True
            
        except Exception as e:
            self.errors.append(f"Error corrigiendo load_mapping: {e}")
            return False
    
    def create_bone_validator_module(self):
        """Crear módulo separado para validación de huesos"""
        print("\n📦 CREATING: gta_sa_bones.py (módulo de validación)")
        
        validator_content = '''"""
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
            print(f"{i:2d}. \\"{bone}\\"")
        print(f"\\nTotal: {len(cls.OFFICIAL_BONES)} huesos")

if __name__ == "__main__":
    # Test del módulo
    GTASABones.print_official_bones()
    
    # Pruebas de normalización
    test_bones = ["Pelvis", "L UpperArm", "UpperArm.L", "invalid_bone"]
    print("\\nPRUEBAS DE NORMALIZACIÓN:")
    for bone in test_bones:
        normalized = GTASABones.normalize_bone(bone)
        print(f"'{bone}' -> '{normalized}'")
'''
        
        try:
            validator_file = self.addon_root / "gta_sa_bones.py"
            with open(validator_file, 'w', encoding='utf-8') as f:
                f.write(validator_content)
            
            self.fixed_files.append(str(validator_file))
            print("✅ gta_sa_bones.py creado")
            return True
            
        except Exception as e:
            self.errors.append(f"Error creando gta_sa_bones.py: {e}")
            return False
    
    def create_json_testing_script(self):
        """Crear script para probar el sistema JSON corregido"""
        print("\n🧪 CREATING: test_json_system.py")
        
        test_script = '''#!/usr/bin/env python3
"""
Test del sistema JSON corregido
Ejecutar en Blender para verificar correcciones
"""

import bpy
import json
import tempfile
import os

def test_json_save_load():
    """Probar save/load con preservación de espacios"""
    print("🧪 TESTING JSON SAVE/LOAD SYSTEM")
    print("=" * 50)
    
    try:
        settings = bpy.context.scene.universal_gta_settings
        
        # Crear mapeos de prueba con espacios incorrectos
        settings.bone_mappings.clear()
        
        test_mappings = [
            ("mixamorig:Hips", "Pelvis"),  # Sin espacio - debería corregirse
            ("mixamorig:Spine", " Spine"),  # Correcto
            ("mixamorig:LeftArm", "L UpperArm"),  # Sin espacio inicial
            ("mixamorig:RightArm", " R UpperArm"),  # Correcto
        ]
        
        print("📝 Creando mapeos de prueba:")
        for source, target in test_mappings:
            mapping = settings.bone_mappings.add()
            mapping.source_bone = source
            mapping.target_bone = target
            mapping.enabled = True
            print(f"  {source} -> '{target}'")
        
        # Guardar a archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        # Simular save_mapping
        try:
            bpy.ops.universalgta.save_mapping(filepath=temp_file)
            print(f"\\n💾 Guardado en: {temp_file}")
            
            # Leer el JSON y verificar espacios
            with open(temp_file, 'r') as f:
                saved_data = json.load(f)
            
            print("\\n🔍 VERIFICANDO ESPACIOS EN JSON:")
            if "mappings" in saved_data:
                for mapping in saved_data["mappings"]:
                    target = mapping.get("target_bone", "")
                    print(f"  Target: '{target}' - {'✅ Correcto' if target.startswith(' ') and 'UpperArm' in target else '⚠️ Revisar'}")
            
            # Limpiar mapeos y cargar
            settings.bone_mappings.clear()
            bpy.ops.universalgta.load_mapping(filepath=temp_file)
            
            print(f"\\n📂 Cargados {len(settings.bone_mappings)} mapeos")
            print("\\n🔍 VERIFICANDO ESPACIOS DESPUÉS DE CARGAR:")
            for mapping in settings.bone_mappings:
                target = mapping.target_bone
                valid = target in [" Pelvis", " Spine", " L UpperArm", " R UpperArm"]
                print(f"  '{mapping.source_bone}' -> '{target}' - {'✅' if valid else '❌'}")
            
            # Cleanup
            os.unlink(temp_file)
            print("\\n✅ Test completado")
            
        except Exception as e:
            print(f"❌ Error en operadores: {e}")
            print("💡 Verifica que el addon esté habilitado")
    
    except Exception as e:
        print(f"❌ Error general: {e}")

def test_bone_validation():
    """Probar validación de huesos"""
    print("\\n🦴 TESTING BONE VALIDATION")
    print("=" * 50)
    
    try:
        from gta_sa_bones import GTASABones
        
        test_bones = [
            "Pelvis",        # Sin espacio - debería normalizarse
            " Pelvis",       # Correcto
            " L UpperArm",   # Correcto  
            "L UpperArm",    # Sin espacio - debería normalizarse
            "UpperArm.L",    # Formato .L - debería normalizarse
            "invalid_bone",  # Inválido
        ]
        
        print("Probando normalización:")
        for bone in test_bones:
            normalized = GTASABones.normalize_bone(bone)
            valid = GTASABones.is_valid_bone(normalized) if normalized else False
            status = "✅" if valid else "❌"
            print(f"  {status} '{bone}' -> '{normalized}'")
        
        print(f"\\n📊 Total huesos oficiales: {len(GTASABones.OFFICIAL_BONES)}")
        
    except ImportError:
        print("❌ gta_sa_bones.py no disponible")
        print("💡 Ejecuta fix_json_mapping_system.py primero")

if __name__ == "__main__":
    test_json_save_load()
    test_bone_validation()
'''
        
        try:
            test_file = self.addon_root / "test_json_system.py"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_script)
            
            self.fixed_files.append(str(test_file))
            print("✅ test_json_system.py creado")
            return True
            
        except Exception as e:
            self.errors.append(f"Error creando test_json_system.py: {e}")
            return False
    
    def run_all_fixes(self):
        """Ejecutar todas las correcciones JSON"""
        print("🚀 CORRIGIENDO SISTEMA JSON MAPPING...")
        print("=" * 60)
        
        fixes = [
            ("operators/mapping.py (espacios)", self.fix_mapping_operators),
            ("load_mapping (validación)", self.fix_load_mapping_operator), 
            ("gta_sa_bones.py (validador)", self.create_bone_validator_module),
            ("test_json_system.py (testing)", self.create_json_testing_script),
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
                self.errors.append(f"{fix_name}: {e}")
        
        self.show_summary(successful, len(fixes))
    
    def show_summary(self, successful, total):
        """Mostrar resumen de correcciones JSON"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN CORRECCIONES JSON SYSTEM")
        print("=" * 60)
        
        print(f"✅ Correcciones exitosas: {successful}/{total}")
        print(f"📁 Archivos modificados: {len(self.fixed_files)}")
        
        if self.fixed_files:
            print("\\n📝 ARCHIVOS MODIFICADOS:")
            for file_path in self.fixed_files:
                print(f"  • {file_path}")
        
        if self.errors:
            print(f"\\n❌ Errores: {len(self.errors)}")
            for error in self.errors:
                print(f"  • {error}")
        
        print("\\n🎯 MEJORAS APLICADAS:")
        print("✅ Preservación exacta de espacios en huesos GTA SA")
        print("✅ Independencia del nombre del armature source")
        print("✅ Validación contra lista oficial de huesos")
        print("✅ Normalización automática de nombres")
        print("✅ Mejor compatibilidad entre esqueletos")
        
        print("\\n🧪 TESTING:")
        print("1. Reiniciar Blender")
        print("2. Recargar addon")
        print("3. Ejecutar: exec(open('test_json_system.py').read())")
        
        print("\\n💾 Backups en: json_backups/")
        print("=" * 60)

if __name__ == "__main__":
    fixer = JSONMappingFixer()
    fixer.run_all_fixes()
    
    print("\\n⏸️ Presiona Enter para continuar...")
    input()
