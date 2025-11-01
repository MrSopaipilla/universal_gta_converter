"""
Sistema de Bone Mapping Mejorado
Permite carga automática de autodetecciones repetidas y mejor gestión
"""
import bpy
import json
from pathlib import Path
from bpy.types import Operator
from bpy.props import StringProperty

class ImprovedBoneMappingSystem:
    """Sistema mejorado de mapeo de huesos"""
    
    @staticmethod
    def get_mapping_cache_path():
        """Obtener ruta del caché de mapeos"""
        addon_dir = Path(__file__).parent
        cache_dir = addon_dir / "config" / "mapping_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    @staticmethod
    def generate_armature_signature(armature):
        """Generar firma única del armature basada en sus huesos"""
        if not armature or armature.type != 'ARMATURE':
            return None
        
        bone_names = sorted([bone.name for bone in armature.pose.bones])
        signature = "_".join(bone_names[:10])  # Primeros 10 huesos
        return signature[:50]  # Limitar longitud
    
    @classmethod
    def save_successful_mapping(cls, source_armature, target_armature, mappings):
        """Guardar mapeo exitoso en caché"""
        if not source_armature or not target_armature:
            return False
        
        signature = cls.generate_armature_signature(source_armature)
        if not signature:
            return False
        
        cache_path = cls.get_mapping_cache_path()
        mapping_file = cache_path / f"{signature}.json"
        
        mapping_data = {
            "signature": signature,
            "source_armature_name": source_armature.name,
            "target_armature_name": target_armature.name,
            "bone_count": len(source_armature.pose.bones),
            "mappings": []
        }
        
        for mapping in mappings:
            if mapping.enabled and mapping.source_bone and mapping.target_bone:
                mapping_data["mappings"].append({
                    "source_bone": mapping.source_bone,
                    "target_bone": mapping.target_bone,
                    "confidence": mapping.confidence,
                    "detection_method": mapping.detection_method
                })
        
        try:
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Mapeo guardado en caché: {mapping_file.name}")
            return True
        except Exception as e:
            print(f"Error guardando mapeo en caché: {e}")
            return False
    
    @classmethod
    def load_cached_mapping(cls, source_armature):
        """Cargar mapeo desde caché si existe"""
        if not source_armature:
            return None
        
        signature = cls.generate_armature_signature(source_armature)
        if not signature:
            return None
        
        cache_path = cls.get_mapping_cache_path()
        mapping_file = cache_path / f"{signature}.json"
        
        if not mapping_file.exists():
            return None
        
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
            
            # Verificar que la firma coincida
            if mapping_data.get("signature") != signature:
                return None
            
            print(f"📂 Mapeo cargado desde caché: {mapping_file.name}")
            return mapping_data
        except Exception as e:
            print(f"Error cargando mapeo desde caché: {e}")
            return None
    
    @classmethod
    def apply_cached_mapping_to_settings(cls, cached_data, settings):
        """Aplicar mapeo cacheado a settings"""
        if not cached_data or not settings:
            return False
        
        applied_count = 0
        
        for cached_mapping in cached_data.get("mappings", []):
            # Buscar si ya existe este mapeo
            existing_mapping = None
            for mapping in settings.bone_mappings:
                if mapping.source_bone == cached_mapping["source_bone"]:
                    existing_mapping = mapping
                    break
            
            if existing_mapping:
                # Actualizar mapeo existente si la confianza es mayor
                if cached_mapping.get("confidence", 0) > existing_mapping.confidence:
                    existing_mapping.target_bone = cached_mapping["target_bone"]
                    existing_mapping.confidence = cached_mapping["confidence"]
                    existing_mapping.detection_method = f"Cached: {cached_mapping.get('detection_method', 'Unknown')}"
                    existing_mapping.enabled = True
                    applied_count += 1
            else:
                # Crear nuevo mapeo
                new_mapping = settings.bone_mappings.add()
                new_mapping.source_bone = cached_mapping["source_bone"]
                new_mapping.target_bone = cached_mapping["target_bone"]
                new_mapping.confidence = cached_mapping.get("confidence", 1.0)
                new_mapping.detection_method = f"Cached: {cached_mapping.get('detection_method', 'Unknown')}"
                new_mapping.enabled = True
                applied_count += 1
        
        print(f"📥 Aplicados {applied_count} mapeos desde caché")
        return applied_count > 0

class UNIVERSALGTA_OT_load_cached_mapping(Operator):
    """Cargar mapeo desde caché automáticamente"""
    bl_idname = "universalgta.load_cached_mapping"
    bl_label = "Load Cached Mapping"
    bl_description = "Carga mapeo desde caché si está disponible"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature:
            self.report({'ERROR'}, "No hay source armature seleccionado")
            return {'CANCELLED'}
        
        cached_data = ImprovedBoneMappingSystem.load_cached_mapping(settings.source_armature)
        
        if not cached_data:
            self.report({'INFO'}, "No se encontró mapeo en caché para este armature")
            return {'FINISHED'}
        
        if ImprovedBoneMappingSystem.apply_cached_mapping_to_settings(cached_data, settings):
            self.report({'INFO'}, f"Mapeo cargado desde caché: {len(cached_data.get('mappings', []))} entries")
        else:
            self.report({'WARNING'}, "No se pudieron aplicar mapeos desde caché")
        
        return {'FINISHED'}

class UNIVERSALGTA_OT_save_current_mapping_to_cache(Operator):
    """Guardar mapeo actual en caché"""
    bl_idname = "universalgta.save_current_mapping_to_cache"
    bl_label = "Save Current Mapping to Cache"
    bl_description = "Guarda el mapeo actual en caché para uso futuro"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature or not settings.target_armature:
            self.report({'ERROR'}, "Selecciona source y target armature")
            return {'CANCELLED'}
        
        if len(settings.bone_mappings) == 0:
            self.report({'ERROR'}, "No hay mapeos para guardar")
            return {'CANCELLED'}
        
        if ImprovedBoneMappingSystem.save_successful_mapping(
            settings.source_armature, 
            settings.target_armature, 
            settings.bone_mappings
        ):
            self.report({'INFO'}, "Mapeo guardado en caché exitosamente")
        else:
            self.report({'ERROR'}, "Error guardando mapeo en caché")
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(UNIVERSALGTA_OT_load_cached_mapping)
    bpy.utils.register_class(UNIVERSALGTA_OT_save_current_mapping_to_cache)

def unregister():
    bpy.utils.unregister_class(UNIVERSALGTA_OT_load_cached_mapping)
    bpy.utils.unregister_class(UNIVERSALGTA_OT_save_current_mapping_to_cache)
