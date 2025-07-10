"""
Utilidades para el manejo de entrada/salida de mapeos de huesos
"""
import json
import os
import bpy

class MappingIO:
    @staticmethod
    def export_mappings(context, filepath):
        """Exporta los mapeos actuales a un archivo JSON"""
        settings = context.scene.universal_gta_settings
        
        # Crear diccionario de datos
        data = {
            "version": "3.2.3",
            "addon": "Universal GTA SA Converter",
            "source_armature": settings.source_armature.name if settings.source_armature else "",
            "target_armature": settings.target_armature.name if settings.target_armature else "",
            "total_mappings": len(settings.bone_mappings),
            "enabled_mappings": sum(1 for m in settings.bone_mappings if m.enabled),
            "settings": {
                "arm_spacing": settings.arm_spacing,
                "leg_spacing": settings.leg_spacing,
                "detection_threshold": settings.detection_threshold
            },
            "mappings": []
        }
        
        # Agregar cada mapeo
        for mapping in settings.bone_mappings:
            mapping_data = {
                "source_bone": mapping.source_bone,
                "target_bone": mapping.target_bone,
                "enabled": mapping.enabled,
                "detection_method": mapping.detection_method,
                "confidence": mapping.confidence
            }
            data["mappings"].append(mapping_data)
            
        # Guardar archivo JSON
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error guardando mapeos: {e}")
            return False
            
    @staticmethod
    def import_mappings(context, filepath):
        """Importa mapeos desde un archivo JSON"""
        settings = context.scene.universal_gta_settings
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Validar versión y addon
            if data.get("addon") != "Universal GTA SA Converter":
                return False, "Archivo no válido para este addon"
                
            # Limpiar mapeos existentes
            while len(settings.bone_mappings) > 0:
                settings.bone_mappings.remove(0)
                
            # Cargar settings si existen
            if "settings" in data:
                settings.arm_spacing = data["settings"].get("arm_spacing", 0.1)
                settings.leg_spacing = data["settings"].get("leg_spacing", 0.0)
                settings.detection_threshold = data["settings"].get("detection_threshold", 0.7)
                
            # Cargar mapeos
            for mapping_data in data["mappings"]:
                mapping = settings.bone_mappings.add()
                mapping.source_bone = mapping_data.get("source_bone", "")
                mapping.target_bone = mapping_data.get("target_bone", "")
                mapping.enabled = mapping_data.get("enabled", True)
                mapping.detection_method = mapping_data.get("detection_method", "Manual")
                mapping.confidence = mapping_data.get("confidence", 0.0)
                
            return True, f"Se importaron {len(data['mappings'])} mapeos"
            
        except Exception as e:
            print(f"Error cargando mapeos: {e}")
            return False, str(e)
            
    @staticmethod
    def validate_mapping_file(filepath):
        """Valida un archivo de mapeos sin cargarlo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Verificar campos requeridos
            required_fields = ["version", "addon", "mappings"]
            for field in required_fields:
                if field not in data:
                    return False, f"Falta el campo requerido: {field}"
                    
            # Verificar addon
            if data["addon"] != "Universal GTA SA Converter":
                return False, "El archivo no es compatible con este addon"
                
            # Verificar estructura de mapeos
            if not isinstance(data["mappings"], list):
                return False, "Formato de mapeos inválido"
                
            # Contar mapeos válidos
            valid_count = 0
            for mapping in data["mappings"]:
                if isinstance(mapping, dict) and "target_bone" in mapping:
                    valid_count += 1
                    
            return True, f"Archivo válido con {valid_count} mapeos"
            
        except json.JSONDecodeError:
            return False, "Archivo JSON inválido"
        except Exception as e:
            return False, str(e)
