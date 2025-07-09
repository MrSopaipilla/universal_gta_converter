"""
Operadores de mapeo mejorados con funcionalidad de guardado/carga JSON
Actualiza los operadores existentes para integrar con el nuevo sistema
"""

import bpy
import json
import os
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty


class UNIVERSALGTA_OT_save_mapping(Operator):
    """Guardar configuración de mapeo a archivo JSON - IMPLEMENTADO"""
    bl_idname = "universalgta.save_mapping"
    bl_label = "Save Mapping"
    bl_description = "Guarda la configuración actual de mapeo de huesos en un archivo JSON"
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(
        name="File Path",
        description="Ruta del archivo a guardar",
        maxlen=1024,
        subtype="FILE_PATH"
    )
    
    filename: StringProperty(
        name="File Name",
        description="Nombre del archivo",
        default="bone_mapping.json"
    )
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Generar nombre automático si no se especifica
        if not self.filepath:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filepath = f"mapping_{timestamp}.json"
        
        # Crear datos del mapeo
        mapping_data = {
            "version": "3.2.3",
            "addon": "Universal GTA SA Converter",
            "created": self._get_timestamp(),
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
        
        # Exportar todos los mapeos
        for item in settings.bone_mappings:
            mapping_data["mappings"].append({
                "source_bone": item.source_bone,
                "target_bone": item.target_bone,
                "enabled": item.enabled,
                "detection_method": item.detection_method,
                "confidence": float(item.confidence)
            })
        
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(mapping_data, f, indent=2, ensure_ascii=False)
            
            self.report({'INFO'}, f"Mapeo guardado exitosamente: {os.path.basename(self.filepath)}")
            print(f"[MAPPING] Guardado: {mapping_data['enabled_mappings']}/{mapping_data['total_mappings']} mapeos")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error guardando mapeo: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def _get_timestamp(self):
        """Obtiene timestamp actual"""
        import datetime
        return datetime.datetime.now().isoformat()


class UNIVERSALGTA_OT_load_mapping(Operator):
    """Cargar configuración de mapeo desde archivo JSON - IMPLEMENTADO"""
    bl_idname = "universalgta.load_mapping"
    bl_label = "Load Mapping"
    bl_description = "Carga una configuración de mapeo de huesos desde archivo JSON"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(
        name="File Path",
        description="Ruta del archivo a cargar",
        maxlen=1024,
        subtype="FILE_PATH"
    )
    
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )
    
    replace_existing: BoolProperty(
        name="Replace Existing",
        description="Reemplazar mapeos existentes o agregar a los actuales",
        default=True
    )
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "Archivo no encontrado")
            return {'CANCELLED'}
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
            
            # Validar formato básico
            if not self._validate_mapping_file(mapping_data):
                self.report({'ERROR'}, "Formato de archivo JSON no válido")
                return {'CANCELLED'}
            
            # Limpiar mapeos existentes si se solicita
            if self.replace_existing:
                while len(settings.bone_mappings) > 0:
                    settings.bone_mappings.remove(0)
            
            # Cargar configuraciones si están disponibles
            if "settings" in mapping_data:
                file_settings = mapping_data["settings"]
                if "arm_spacing" in file_settings:
                    settings.arm_spacing = file_settings["arm_spacing"]
                if "leg_spacing" in file_settings:
                    settings.leg_spacing = file_settings["leg_spacing"]
                if "detection_threshold" in file_settings:
                    settings.detection_threshold = file_settings["detection_threshold"]
            
            # Cargar mapeos
            loaded_count = 0
            valid_count = 0
            
            for mapping in mapping_data["mappings"]:
                item = settings.bone_mappings.add()
                item.source_bone = mapping.get("source_bone", "")
                item.target_bone = mapping.get("target_bone", "")
                item.enabled = mapping.get("enabled", True)
                item.detection_method = mapping.get("detection_method", "Manual")
                item.confidence = mapping.get("confidence", 0.0)
                
                loaded_count += 1
                if item.source_bone and item.target_bone:
                    valid_count += 1
            
            settings.bone_mappings_index = 0
            
            # Mostrar información detallada
            file_info = f"Archivo: {os.path.basename(self.filepath)}"
            mapping_info = f"Mapeos: {loaded_count} cargados, {valid_count} válidos"
            
            if "version" in mapping_data:
                version_info = f"Versión: {mapping_data['version']}"
                self.report({'INFO'}, f"{file_info} | {mapping_info} | {version_info}")
            else:
                self.report({'INFO'}, f"{file_info} | {mapping_info}")
            
            print(f"[MAPPING] Cargado desde: {self.filepath}")
            print(f"[MAPPING] Mapeos cargados: {loaded_count}")
            print(f"[MAPPING] Mapeos válidos: {valid_count}")
            
            return {'FINISHED'}
            
        except json.JSONDecodeError as e:
            self.report({'ERROR'}, f"Error de formato JSON: {str(e)}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error cargando mapeo: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def _validate_mapping_file(self, mapping_data):
        """Valida que el archivo tenga el formato correcto"""
        required_fields = ["mappings"]
        for field in required_fields:
            if field not in mapping_data:
                return False
        
        # Validar que mappings sea una lista
        if not isinstance(mapping_data["mappings"], list):
            return False
        
        # Validar estructura básica de cada mapeo
        for mapping in mapping_data["mappings"]:
            if not isinstance(mapping, dict):
                return False
            
            # Campos requeridos en cada mapeo
            required_mapping_fields = ["source_bone", "target_bone", "enabled"]
            for field in required_mapping_fields:
                if field not in mapping:
                    return False
        
        return True


class UNIVERSALGTA_OT_export_mapping_template(Operator):
    """Exportar plantilla de mapeo JSON para edición manual"""
    bl_idname = "universalgta.export_mapping_template"
    bl_label = "Export Template"
    bl_description = "Exporta una plantilla JSON con todos los huesos GTA SA para edición manual"
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(
        name="File Path",
        description="Ruta del archivo de plantilla",
        maxlen=1024,
        subtype="FILE_PATH"
    )