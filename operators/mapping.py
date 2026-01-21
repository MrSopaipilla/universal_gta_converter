"""Operadores de mapeo de huesos."""



import bpy  # type: ignore
import json
from bpy.types import Operator  # type: ignore
from bpy.props import StringProperty, IntProperty  # type: ignore


# Lista oficial de huesos GTA SA
OFFICIAL_GTA_SA_BONES = [
    "Root", " Pelvis", " Spine", " Spine1", " Neck", " Head", "Jaw",
    "L Brow", "R Brow", "Bip01 L Clavicle", " L UpperArm", " L ForeArm",
    " L Hand", " L Finger", "L Finger01", "Bip01 R Clavicle", " R UpperArm",
    " R ForeArm", " R Hand", " R Finger", "R Finger01", "L breast",
    "R breast", "Belly", " L Thigh", " L Calf", " L Foot", " L Toe0",
    " R Thigh", " R Calf", " R Foot", " R Toe0"
]


class UNIVERSALGTA_OT_add_custom_entry(Operator):
    """Agregar entrada de mapeo personalizada"""
    bl_idname = "universalgta.add_custom_entry"
    bl_label = "Add Custom Entry"
    bl_description = "Agrega una entrada de mapeo personalizada"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Obtener índice actual
        current_index = settings.bone_mappings_index
        insert_index = current_index + 1 if current_index >= 0 else 0
        
        # Agregar nueva entrada al final primero
        mapping = settings.bone_mappings.add()
        mapping.source_bone = ""
        mapping.target_bone = ""
        mapping.enabled = True
        mapping.detection_method = "Manual"
        mapping.confidence = 1.0
        
        # Mover la nueva entrada a la posición deseada
        if insert_index < len(settings.bone_mappings) - 1:
            # Mover desde el final hasta la posición deseada
            for i in range(len(settings.bone_mappings) - 1, insert_index, -1):
                settings.bone_mappings.move(i, i - 1)
        
        # Seleccionar la nueva entrada
        settings.bone_mappings_index = insert_index
        
        self.report({'INFO'}, f"Entrada personalizada agregada en posición {insert_index + 1}")
        return {'FINISHED'}


class UNIVERSALGTA_OT_remove_mapping_entry(Operator):
    """Eliminar entrada de mapeo"""
    bl_idname = "universalgta.remove_mapping_entry"
    bl_label = "Remove Mapping Entry"
    bl_description = "Elimina la entrada de mapeo seleccionada"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if len(settings.bone_mappings) == 0:
            self.report({'WARNING'}, "No hay entradas para eliminar")
            return {'CANCELLED'}
        
        index = settings.bone_mappings_index
        if 0 <= index < len(settings.bone_mappings):
            settings.bone_mappings.remove(index)
            
            # Ajustar índice
            if settings.bone_mappings_index >= len(settings.bone_mappings):
                settings.bone_mappings_index = len(settings.bone_mappings) - 1
            
            self.report({'INFO'}, "Entrada eliminada")
            return {'FINISHED'}
        
        return {'CANCELLED'}


class UNIVERSALGTA_OT_move_mapping_up(Operator):
    """Mover mapeo hacia arriba"""
    bl_idname = "universalgta.move_mapping_up"
    bl_label = "Move Up"
    bl_description = "Mueve el mapeo seleccionado hacia arriba"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        if index > 0:
            settings.bone_mappings.move(index, index - 1)
            settings.bone_mappings_index = index - 1
        # Forzar refresco de la UI
        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}


class UNIVERSALGTA_OT_move_mapping_down(Operator):
    """Mover mapeo hacia abajo"""
    bl_idname = "universalgta.move_mapping_down"
    bl_label = "Move Down"
    bl_description = "Mueve el mapeo seleccionado hacia abajo"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        if index < len(settings.bone_mappings) - 1:
            settings.bone_mappings.move(index, index + 1)
            settings.bone_mappings_index = index + 1
        # Forzar refresco de la UI
        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}


class UNIVERSALGTA_OT_clear_mappings(Operator):
    """Limpiar todos los mapeos"""
    bl_idname = "universalgta.clear_mappings"
    bl_label = "Clear All Mappings"
    bl_description = "Elimina todos los mapeos de huesos"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        settings.bone_mappings.clear()
        settings.bone_mappings_index = 0
        
        self.report({'INFO'}, "Todos los mapeos eliminados")
        return {'FINISHED'}


class UNIVERSALGTA_OT_add_target_bones(Operator):
    """Agregar todos los huesos target disponibles"""
    bl_idname = "universalgta.add_target_bones"
    bl_label = "Add Target Bones"
    bl_description = "Agrega todos los huesos del target armature como mapeos vacíos"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No hay target armature seleccionado")
            return {'CANCELLED'}
        
        # Limpiar mapeos existentes
        settings.bone_mappings.clear()
        
        # Agregar todos los huesos target
        for bone in settings.target_armature.pose.bones:
            mapping = settings.bone_mappings.add()
            mapping.source_bone = ""
            mapping.target_bone = bone.name
            mapping.enabled = False  # Deshabilitado hasta que se asigne source
            mapping.detection_method = "Manual"
            mapping.confidence = 0.0
        
        self.report({'INFO'}, f"{len(settings.bone_mappings)} huesos target agregados")
        return {'FINISHED'}


class UNIVERSALGTA_OT_auto_detect_mappings(Operator):
    """Auto-detectar mapeos (legacy)"""
    bl_idname = "universalgta.auto_detect_mappings"
    bl_label = "Auto Detect Mappings"
    bl_description = "Detección automática legacy de mapeos"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Redirigir al Smart Auto-Detect
        return bpy.ops.universalgta.smart_auto_detect()


class UNIVERSALGTA_OT_load_mapping(Operator):
    """Cargar mapeos desde archivo JSON"""
    bl_idname = "universalgta.load_mapping"
    bl_label = "Load Mapping"
    bl_description = "Carga mapeos de huesos desde un archivo JSON"
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(subtype="FILE_PATH")  # type: ignore
    
    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No se especificó archivo")
            return {'CANCELLED'}
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            settings = context.scene.universal_gta_settings
            settings.bone_mappings.clear()
            
            # Cargar según formato
            if "mappings" in data:
                # Formato v2.0
                for item in data["mappings"]:
                    mapping = settings.bone_mappings.add()
                    mapping.source_bone = item.get("source_bone", "")
                    mapping.target_bone = self.normalize_target_bone(item.get("target_bone", ""))
                    mapping.enabled = item.get("enabled", True)
                    mapping.detection_method = item.get("detection_method", "Loaded")
                    mapping.confidence = item.get("confidence", 1.0)
            else:
                # Formato v1.0 simple
                for source, target in data.items():
                    mapping = settings.bone_mappings.add()
                    mapping.source_bone = source
                    mapping.target_bone = self.normalize_target_bone(target)
                    mapping.enabled = True
                    mapping.detection_method = "Loaded"
                    mapping.confidence = 1.0
            
            # 🔧 CORRECCIÓN DE CASE: Ajustar source_bones al case real del armature
            if settings.source_armature:
                corrected_count = self.correct_source_bone_case(settings)
                print(f"[LOAD_MAPPING] {corrected_count} source_bones corregidos al case real del armature")
            
            self.report({'INFO'}, f"Cargados {len(settings.bone_mappings)} mapeos")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error cargando archivo: {e}")
            return {'CANCELLED'}
    
    def correct_source_bone_case(self, settings) -> int:
        """Corrige el case de los source_bones para que coincidan exactamente con los huesos reales del armature.
        
        Returns:
            int: Cantidad de source_bones corregidos
        """
        if not settings.source_armature:
            return 0
        
        # Crear diccionario de mapeo: lowercase -> nombre real del hueso
        bone_name_map = {}
        
        # Incluir tanto data.bones como pose.bones para máxima compatibilidad
        for bone in settings.source_armature.data.bones:
            bone_name_map[bone.name.lower()] = bone.name
        
        for bone in settings.source_armature.pose.bones:
            bone_name_map[bone.name.lower()] = bone.name
        
        # Corregir cada source_bone en los mappings
        corrected_count = 0
        for mapping in settings.bone_mappings:
            if not mapping.source_bone:
                continue
            
            source_lower = mapping.source_bone.lower()
            
            # Si existe un hueso real con este nombre (case-insensitive), corregir el case
            if source_lower in bone_name_map:
                real_bone_name = bone_name_map[source_lower]
                
                # Solo corregir si el case es diferente
                if mapping.source_bone != real_bone_name:
                    print(f"  [CASE_FIX] '{mapping.source_bone}' -> '{real_bone_name}'")
                    mapping.source_bone = real_bone_name
                    corrected_count += 1
        
        return corrected_count
    
    def normalize_target_bone(self, target_bone):
        """Normalizar target bone a oficial GTA SA"""
        if target_bone in OFFICIAL_GTA_SA_BONES:
            return target_bone
        
        # Buscar versión con espacio correcto
        for official in OFFICIAL_GTA_SA_BONES:
            if official.strip() == target_bone.strip():
                return official
        
        return target_bone
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class UNIVERSALGTA_OT_save_mapping(Operator):
    """Guardar mapeos a archivo JSON"""
    bl_idname = "universalgta.save_mapping"
    bl_label = "Save Mapping"
    bl_description = "Guarda mapeos de huesos a un archivo JSON"
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(subtype="FILE_PATH")  # type: ignore
    
    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No se especificó archivo")
            return {'CANCELLED'}
        
        try:
            settings = context.scene.universal_gta_settings
            
            # Crear datos en formato v2.0
            data = {
                "format_version": "2.0",
                "description": "Universal GTA SA Converter Bone Mappings",
                "mappings": []
            }
            
            for i, mapping in enumerate(settings.bone_mappings):
                mapping_entry = {
                    "index": i,
                    "source_bone": mapping.source_bone,
                    "target_bone": self.normalize_target_bone(mapping.target_bone),
                    "enabled": mapping.enabled,
                    "detection_method": mapping.detection_method,
                    "confidence": mapping.confidence
                }
                data["mappings"].append(mapping_entry)
            
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.report({'INFO'}, f"Guardados {len(settings.bone_mappings)} mapeos")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error guardando archivo: {e}")
            return {'CANCELLED'}
    
    def normalize_target_bone(self, target_bone):
        """Normalizar target bone a oficial GTA SA"""
        if target_bone in OFFICIAL_GTA_SA_BONES:
            return target_bone
        
        for official in OFFICIAL_GTA_SA_BONES:
            if official.strip() == target_bone.strip():
                return official
        
        return target_bone
    
    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = "bone_mappings.json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class UNIVERSALGTA_OT_validate_mappings(Operator):
    """Validar mapeos de huesos"""
    bl_idname = "universalgta.validate_mappings"
    bl_label = "Validate Mappings"
    bl_description = "Valida todos los mapeos de huesos"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        return bpy.ops.universalgta.validate_mappings_and_disable_invalid()


class UNIVERSALGTA_OT_duplicate_mapping(Operator):
    """Duplicar mapeo seleccionado"""
    bl_idname = "universalgta.duplicate_mapping"
    bl_label = "Duplicate Mapping"
    bl_description = "Duplica el mapeo seleccionado"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        
        if 0 <= index < len(settings.bone_mappings):
            original = settings.bone_mappings[index]
            insert_index = index + 1
            
            # Duplicar entrada al final primero
            mapping = settings.bone_mappings.add()
            mapping.source_bone = original.source_bone
            mapping.target_bone = original.target_bone
            mapping.enabled = original.enabled
            mapping.detection_method = "Duplicated"
            mapping.confidence = original.confidence
            
            # Mover directamente desde el final hasta la posición deseada
            if insert_index < len(settings.bone_mappings):
                last_index = len(settings.bone_mappings) - 1
                settings.bone_mappings.move(last_index, insert_index)
            
            # Seleccionar la entrada duplicada
            settings.bone_mappings_index = insert_index
            
            self.report({'INFO'}, f"Mapeo duplicado en posición {insert_index + 1}")
            return {'FINISHED'}
        
        self.report({'WARNING'}, "No hay entrada seleccionada para duplicar")
        return {'CANCELLED'}


class UNIVERSALGTA_OT_invert_mapping(Operator):
    """Invertir mapeo seleccionado"""
    bl_idname = "universalgta.invert_mapping"
    bl_label = "Invert Mapping"
    bl_description = "Invierte source y target del mapeo seleccionado"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        
        if 0 <= index < len(settings.bone_mappings):
            mapping = settings.bone_mappings[index]
            
            # Intercambiar source y target
            temp = mapping.source_bone
            mapping.source_bone = mapping.target_bone
            mapping.target_bone = temp
            mapping.detection_method = "Inverted"
            
            self.report({'INFO'}, "Mapeo invertido")
            return {'FINISHED'}
        
        return {'CANCELLED'}


class UNIVERSALGTA_OT_enable_all_mappings(Operator):
    """Habilitar todos los mapeos"""
    bl_idname = "universalgta.enable_all_mappings"
    bl_label = "Enable All"
    bl_description = "Habilita todos los mapeos"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        for mapping in settings.bone_mappings:
            mapping.enabled = True
        
        self.report({'INFO'}, f"Habilitados {len(settings.bone_mappings)} mapeos")
        return {'FINISHED'}


class UNIVERSALGTA_OT_disable_all_mappings(Operator):
    """Deshabilitar todos los mapeos"""
    bl_idname = "universalgta.disable_all_mappings"
    bl_label = "Disable All"
    bl_description = "Deshabilita todos los mapeos"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        for mapping in settings.bone_mappings:
            mapping.enabled = False
        
        self.report({'INFO'}, f"Deshabilitados {len(settings.bone_mappings)} mapeos")
        return {'FINISHED'}


class UNIVERSALGTA_OT_enable_high_confidence(Operator):
    """Habilitar solo mapeos de alta confianza"""
    bl_idname = "universalgta.enable_high_confidence"
    bl_label = "High Confidence Only"
    bl_description = "Habilita solo mapeos con alta confianza"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        threshold = 0.7
        
        enabled_count = 0
        for mapping in settings.bone_mappings:
            if mapping.confidence >= threshold:
                mapping.enabled = True
                enabled_count += 1
            else:
                mapping.enabled = False
        
        self.report({'INFO'}, f"Habilitados {enabled_count} mapeos de alta confianza")
        return {'FINISHED'}


class UNIVERSALGTA_OT_enable_only_valid_mappings(Operator):
    """Habilitar solo mapeos válidos"""
    bl_idname = "universalgta.enable_only_valid_mappings"
    bl_label = "Valid Mappings Only"
    bl_description = "Habilita solo mapeos válidos"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        return bpy.ops.universalgta.validate_mappings_and_disable_invalid()


# CLASES PARA REGISTRAR
classes = [
    UNIVERSALGTA_OT_add_custom_entry,
    UNIVERSALGTA_OT_remove_mapping_entry,
    UNIVERSALGTA_OT_move_mapping_up,
    UNIVERSALGTA_OT_move_mapping_down,
    UNIVERSALGTA_OT_clear_mappings,
    UNIVERSALGTA_OT_add_target_bones,
    UNIVERSALGTA_OT_auto_detect_mappings,
    UNIVERSALGTA_OT_load_mapping,
    UNIVERSALGTA_OT_save_mapping,
    UNIVERSALGTA_OT_validate_mappings,
    UNIVERSALGTA_OT_duplicate_mapping,
    UNIVERSALGTA_OT_invert_mapping,
    UNIVERSALGTA_OT_enable_all_mappings,
    UNIVERSALGTA_OT_disable_all_mappings,
    UNIVERSALGTA_OT_enable_high_confidence,
    UNIVERSALGTA_OT_enable_only_valid_mappings,
]


def register():
    """Registrar operadores de mapping"""
    for cls in classes:
        bpy.utils.register_class(cls)
    print("[MAPPING] Operadores de mapping registrados")


def unregister():
    """Desregistrar operadores de mapping"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
