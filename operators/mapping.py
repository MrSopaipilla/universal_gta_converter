"""
Operadores de mapeo de huesos para Universal GTA SA Converter
VERSIÓN COMPLETA CON TODAS LAS MEJORAS
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty


class UNIVERSALGTA_OT_add_custom_entry(Operator):
    """Agregar entrada personalizada de mapeo de huesos"""
    bl_idname = "universalgta.add_custom_entry"
    bl_label = "Add Custom Entry"
    bl_description = "Add a custom bone mapping entry"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        item = settings.bone_mappings.add()
        item.source_bone = ""
        item.target_bone = ""
        item.enabled = True
        item.detection_method = "Manual"
        item.confidence = 0.0
        settings.bone_mappings_index = len(settings.bone_mappings) - 1
        self.report({'INFO'}, "Entrada personalizada agregada.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_remove_mapping_entry(Operator):
    """Eliminar entrada de mapeo seleccionada"""
    bl_idname = "universalgta.remove_mapping_entry"
    bl_label = "Remove Entry"
    bl_description = "Remove selected bone mapping entry"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        if 0 <= index < len(settings.bone_mappings):
            settings.bone_mappings.remove(index)
            # Ajustar índice si es necesario
            if settings.bone_mappings_index >= len(settings.bone_mappings):
                settings.bone_mappings_index = len(settings.bone_mappings) - 1
            if settings.bone_mappings_index < 0:
                settings.bone_mappings_index = 0
            self.report({'INFO'}, "Entrada eliminada.")
        else:
            self.report({'WARNING'}, "No hay entrada seleccionada para eliminar.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_move_mapping_up(Operator):
    """Mover mapeo hacia arriba"""
    bl_idname = "universalgta.move_mapping_up"
    bl_label = "Move Up"
    bl_description = "Move selected bone mapping up"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        if index > 0:
            settings.bone_mappings.move(index, index - 1)
            settings.bone_mappings_index = index - 1
            self.report({'INFO'}, "Mapeo movido hacia arriba.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_move_mapping_down(Operator):
    """Mover mapeo hacia abajo"""
    bl_idname = "universalgta.move_mapping_down"
    bl_label = "Move Down"
    bl_description = "Move selected bone mapping down"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        if index < len(settings.bone_mappings) - 1:
            settings.bone_mappings.move(index, index + 1)
            settings.bone_mappings_index = index + 1
            self.report({'INFO'}, "Mapeo movido hacia abajo.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_clear_mappings(Operator):
    """Limpiar todos los mapeos"""
    bl_idname = "universalgta.clear_mappings"
    bl_label = "Clear All Mappings"
    bl_description = "Clear all bone mappings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        settings.bone_mappings.clear()
        settings.bone_mappings_index = 0
        self.report({'INFO'}, "Todos los mapeos eliminados.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_add_target_bones(Operator):
    """Agregar todos los huesos del armature destino"""
    bl_idname = "universalgta.add_target_bones"
    bl_label = "Add Target Bones"
    bl_description = "Add all target armature bones to mapping list"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        target_armature = settings.target_armature
        
        if not target_armature or target_armature.type != 'ARMATURE':
            self.report({'WARNING'}, "No hay target armature asignado.")
            return {'CANCELLED'}
        
        # Limpiar mapeos existentes
        settings.bone_mappings.clear()
        
        # Agregar todos los huesos del target
        for bone in target_armature.pose.bones:
            item = settings.bone_mappings.add()
            item.source_bone = ""
            item.target_bone = bone.name
            item.enabled = True
            item.detection_method = "Manual"
            item.confidence = 0.0
        
        settings.bone_mappings_index = 0
        self.report({'INFO'}, f"Agregados {len(target_armature.pose.bones)} huesos del target.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_auto_detect_mappings(Operator):
    """Detectar automáticamente mapeos de huesos"""
    bl_idname = "universalgta.auto_detect_mappings"
    bl_label = "Auto Detect Mappings"
    bl_description = "Automatically detect bone mappings between source and target armatures"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        source_armature = settings.source_armature
        target_armature = settings.target_armature
        
        if not source_armature or not target_armature:
            self.report({'ERROR'}, "Necesitas definir tanto el armature fuente como el destino")
            return {'CANCELLED'}
        
        if source_armature.type != 'ARMATURE' or target_armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Ambos objetos deben ser armatures")
            return {'CANCELLED'}
        
        detected_mappings = self.detect_bone_mappings(source_armature, target_armature, settings)
        
        # Limpiar mapeos existentes
        settings.bone_mappings.clear()
        
        # Agregar mapeos detectados
        for source_bone, target_bone, confidence in detected_mappings:
            item = settings.bone_mappings.add()
            item.source_bone = source_bone
            item.target_bone = target_bone
            item.enabled = True
            item.detection_method = "Auto"
            item.confidence = confidence
        
        settings.bone_mappings_index = 0
        self.report({'INFO'}, f"Detectados {len(detected_mappings)} mapeos automáticamente.")
        return {'FINISHED'}
    
    def detect_bone_mappings(self, source_armature, target_armature, settings):
        """
        Detecta automáticamente mapeos de huesos usando múltiples algoritmos
        
        Returns:
            List[Tuple]: Lista de (source_bone, target_bone, confidence)
        """
        import difflib
        
        source_bones = [bone.name for bone in source_armature.pose.bones]
        target_bones = [bone.name for bone in target_armature.pose.bones]
        
        mappings = []
        threshold = settings.detection_threshold if hasattr(settings, 'detection_threshold') else 0.5
        
        # Patrones de mapeo inteligentes para GTA SA
        gta_patterns = {
            # Columna vertebral
            'Root': ['root', 'base', 'origin', 'pelvis'],
            'Pelvis': ['pelvis', 'hip', 'root'],
            'Spine': ['spine', 'back', 'torso', 'spine1'],
            'Spine1': ['spine1', 'chest', 'upper_torso', 'spine2'],
            'Spine2': ['spine2', 'upper_chest', 'spine3'],
            'Neck': ['neck', 'cervical'],
            'Head': ['head', 'skull'],
            
            # Brazos izquierdos
            'L Clavicle': ['l_clavicle', 'left_clavicle', 'l_shoulder', 'left_shoulder', 'clavicle_l'],
            'L UpperArm': ['l_upperarm', 'left_upperarm', 'l_arm', 'left_arm', 'l_humerus', 'upperarm_l'],
            'L Forearm': ['l_forearm', 'left_forearm', 'l_lower_arm', 'left_lower_arm', 'forearm_l'],
            'L Hand': ['l_hand', 'left_hand', 'hand_l'],
            'L Finger': ['l_finger', 'left_finger', 'finger_l'],
            'L Finger1': ['l_finger1', 'left_finger1', 'finger1_l'],
            'L Finger01': ['l_finger01', 'left_finger01', 'finger01_l'],
            
            # Brazos derechos
            'R Clavicle': ['r_clavicle', 'right_clavicle', 'r_shoulder', 'right_shoulder', 'clavicle_r'],
            'R UpperArm': ['r_upperarm', 'right_upperarm', 'r_arm', 'right_arm', 'r_humerus', 'upperarm_r'],
            'R Forearm': ['r_forearm', 'right_forearm', 'r_lower_arm', 'right_lower_arm', 'forearm_r'],
            'R Hand': ['r_hand', 'right_hand', 'hand_r'],
            'R Finger': ['r_finger', 'right_finger', 'finger_r'],
            'R Finger1': ['r_finger1', 'right_finger1', 'finger1_r'],
            'R Finger01': ['r_finger01', 'right_finger01', 'finger01_r'],
            
            # Piernas izquierdas
            'L Thigh': ['l_thigh', 'left_thigh', 'l_leg', 'left_leg', 'l_femur', 'thigh_l'],
            'L Calf': ['l_calf', 'left_calf', 'l_shin', 'left_shin', 'l_lower_leg', 'calf_l'],
            'L Foot': ['l_foot', 'left_foot', 'foot_l'],
            'L Toe0': ['l_toe', 'left_toe', 'toe_l'],
            
            # Piernas derechas
            'R Thigh': ['r_thigh', 'right_thigh', 'r_leg', 'right_leg', 'r_femur', 'thigh_r'],
            'R Calf': ['r_calf', 'right_calf', 'r_shin', 'right_shin', 'r_lower_leg', 'calf_r'],
            'R Foot': ['r_foot', 'right_foot', 'foot_r'],
            'R Toe0': ['r_toe', 'right_toe', 'toe_r'],
            
            # Pechos (GTA SA específico)
            'L breast': ['l_breast', 'left_breast', 'breast_l'],
            'R breast': ['r_breast', 'right_breast', 'breast_r'],
        }
        
        # Algoritmo 1: Mapeo por patrones específicos de GTA SA
        used_source_bones = set()
        
        for target_bone in target_bones:
            best_match = None
            best_confidence = 0.0
            
            if target_bone in gta_patterns:
                patterns = gta_patterns[target_bone]
                
                for source_bone in source_bones:
                    if source_bone in used_source_bones:
                        continue
                        
                    source_lower = source_bone.lower()
                    
                    for pattern in patterns:
                        if pattern in source_lower:
                            # Calcular confianza basada en la especificidad del patrón
                            confidence = len(pattern) / len(source_lower)
                            confidence = min(confidence * 1.2, 1.0)  # Boost para patrones específicos
                            
                            if confidence > best_confidence:
                                best_match = source_bone
                                best_confidence = confidence
            
            # Algoritmo 2: Similitud de nombres si no se encontró patrón
            if not best_match or best_confidence < 0.6:
                matches = difflib.get_close_matches(target_bone, 
                                                  [b for b in source_bones if b not in used_source_bones], 
                                                  n=1, cutoff=threshold)
                if matches:
                    similarity = difflib.SequenceMatcher(None, target_bone.lower(), matches[0].lower()).ratio()
                    if similarity > best_confidence:
                        best_match = matches[0]
                        best_confidence = similarity
            
            # Algoritmo 3: Mapeo por palabras clave
            if not best_match or best_confidence < 0.4:
                target_keywords = self._extract_keywords(target_bone)
                
                for source_bone in source_bones:
                    if source_bone in used_source_bones:
                        continue
                        
                    source_keywords = self._extract_keywords(source_bone)
                    common_keywords = target_keywords.intersection(source_keywords)
                    
                    if common_keywords:
                        keyword_confidence = len(common_keywords) / max(len(target_keywords), len(source_keywords))
                        if keyword_confidence > best_confidence:
                            best_match = source_bone
                            best_confidence = keyword_confidence
            
            # Agregar mapeo si cumple el umbral
            if best_match and best_confidence >= threshold:
                mappings.append((best_match, target_bone, best_confidence))
                used_source_bones.add(best_match)
                print(f"[AUTO_DETECT] {best_match} -> {target_bone} (confianza: {best_confidence:.2f})")
        
        # Ordenar por confianza descendente
        mappings.sort(key=lambda x: x[2], reverse=True)
        
        return mappings
    
    def _extract_keywords(self, bone_name):
        """Extrae palabras clave de un nombre de hueso"""
        keywords = set()
        name_lower = bone_name.lower()
        
        # Lateralidad
        if any(x in name_lower for x in ['left', 'l_', '_l', '.l']):
            keywords.add('left')
        elif any(x in name_lower for x in ['right', 'r_', '_r', '.r']):
            keywords.add('right')
        
        # Partes del cuerpo
        body_parts = [
            'head', 'neck', 'spine', 'chest', 'back',
            'arm', 'shoulder', 'elbow', 'wrist', 'hand', 'finger',
            'leg', 'thigh', 'knee', 'ankle', 'foot', 'toe',
            'hip', 'pelvis', 'root', 'clavicle', 'breast'
        ]
        
        for part in body_parts:
            if part in name_lower:
                keywords.add(part)
        
        # Números y sufijos
        import re
        numbers = re.findall(r'\d+', bone_name)
        for num in numbers:
            keywords.add(f'num_{num}')
        
        return keywords


class UNIVERSALGTA_OT_load_mapping(Operator):
    """Cargar mapeo desde archivo"""
    bl_idname = "universalgta.load_mapping"
    bl_label = "Load Mapping"
    bl_description = "Load bone mapping from file"
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})
    
    def execute(self, context):
        import json
        
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            
            settings = context.scene.universal_gta_settings
            settings.bone_mappings.clear()
            
            for mapping in data.get('mappings', []):
                item = settings.bone_mappings.add()
                item.source_bone = mapping.get('source_bone', '')
                item.target_bone = mapping.get('target_bone', '')
                item.enabled = mapping.get('enabled', True)
                item.detection_method = mapping.get('detection_method', 'Manual')
                item.confidence = mapping.get('confidence', 0.0)
            
            settings.bone_mappings_index = 0
            self.report({'INFO'}, f"Cargados {len(data.get('mappings', []))} mapeos.")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error al cargar mapeo: {str(e)}")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class UNIVERSALGTA_OT_save_mapping(Operator):
    """Guardar mapeo en archivo"""
    bl_idname = "universalgta.save_mapping"
    bl_label = "Save Mapping"
    bl_description = "Save bone mapping to file"
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})
    
    def execute(self, context):
        import json
        from datetime import datetime
        
        try:
            settings = context.scene.universal_gta_settings
            
            data = {
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'addon_version': '3.2.2',
                    'source_armature': settings.source_armature.name if settings.source_armature else None,
                    'target_armature': settings.target_armature.name if settings.target_armature else None,
                    'total_mappings': len(settings.bone_mappings),
                    'enabled_mappings': sum(1 for m in settings.bone_mappings if m.enabled)
                },
                'mappings': []
            }
            
            for item in settings.bone_mappings:
                mapping = {
                    'source_bone': item.source_bone,
                    'target_bone': item.target_bone,
                    'enabled': item.enabled,
                    'detection_method': item.detection_method,
                    'confidence': item.confidence
                }
                data['mappings'].append(mapping)
            
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.report({'INFO'}, f"Guardados {len(data['mappings'])} mapeos.")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error al guardar mapeo: {str(e)}")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = "bone_mapping.json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class UNIVERSALGTA_OT_validate_mappings(Operator):
    """Validar mapeos de huesos"""
    bl_idname = "universalgta.validate_mappings"
    bl_label = "Validate Mappings"
    bl_description = "Validate bone mappings and show issues"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        source_armature = settings.source_armature
        target_armature = settings.target_armature
        
        if not source_armature or not target_armature:
            self.report({'ERROR'}, "Necesitas definir tanto el armature fuente como el destino")
            return {'CANCELLED'}
        
        issues = []
        warnings = []
        valid_mappings = 0
        
        source_bone_names = {bone.name for bone in source_armature.pose.bones}
        target_bone_names = {bone.name for bone in target_armature.pose.bones}
        
        for i, item in enumerate(settings.bone_mappings):
            line_num = i + 1
            
            if not item.enabled:
                continue
                
            # Verificar si el hueso fuente existe
            if item.source_bone and item.source_bone not in source_bone_names:
                issues.append(f"Línea {line_num}: Hueso fuente '{item.source_bone}' no existe")
            
            # Verificar si el hueso destino existe
            if item.target_bone and item.target_bone not in target_bone_names:
                issues.append(f"Línea {line_num}: Hueso destino '{item.target_bone}' no existe")
            
            # Verificar si ambos campos están llenos
            if not item.source_bone or not item.target_bone:
                issues.append(f"Línea {line_num}: Mapeo incompleto (fuente: '{item.source_bone}', destino: '{item.target_bone}')")
            
            # Verificar confianza baja para mapeos automáticos
            if item.detection_method == "Auto" and item.confidence < 0.4:
                warnings.append(f"Línea {line_num}: Baja confianza ({item.confidence:.2f}) para mapeo automático")
            
            # Contar mapeos válidos
            if (item.source_bone and item.target_bone and 
                item.source_bone in source_bone_names and 
                item.target_bone in target_bone_names):
                valid_mappings += 1
        
        # Verificar duplicados en source bones
        used_source_bones = {}
        for i, item in enumerate(settings.bone_mappings):
            if item.enabled and item.source_bone:
                if item.source_bone in used_source_bones:
                    issues.append(f"Línea {i+1}: Hueso fuente '{item.source_bone}' usado múltiples veces (también en línea {used_source_bones[item.source_bone]})")
                else:
                    used_source_bones[item.source_bone] = i + 1
        
        # Verificar duplicados en target bones
        used_target_bones = {}
        for i, item in enumerate(settings.bone_mappings):
            if item.enabled and item.target_bone:
                if item.target_bone in used_target_bones:
                    issues.append(f"Línea {i+1}: Hueso destino '{item.target_bone}' usado múltiples veces (también en línea {used_target_bones[item.target_bone]})")
                else:
                    used_target_bones[item.target_bone] = i + 1
        
        # Mostrar resultados
        if issues:
            print("[MAPPING_VALIDATION] Problemas críticos encontrados:")
            for issue in issues:
                print(f"  - {issue}")
            self.report({'ERROR'}, f"Se encontraron {len(issues)} problemas críticos. Ver consola para detalles.")
        elif warnings:
            print("[MAPPING_VALIDATION] Advertencias encontradas:")
            for warning in warnings:
                print(f"  - {warning}")
            self.report({'WARNING'}, f"Se encontraron {len(warnings)} advertencias. {valid_mappings} mapeos válidos.")
        else:
            self.report({'INFO'}, f"Todos los mapeos son válidos. {valid_mappings} mapeos activos listos para conversión.")
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_duplicate_mapping(Operator):
    """Duplicar entrada de mapeo seleccionada"""
    bl_idname = "universalgta.duplicate_mapping"
    bl_label = "Duplicate Entry"
    bl_description = "Duplicate selected bone mapping entry"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        
        if 0 <= index < len(settings.bone_mappings):
            original = settings.bone_mappings[index]
            
            # Crear nueva entrada
            new_item = settings.bone_mappings.add()
            new_item.source_bone = original.source_bone
            new_item.target_bone = original.target_bone + "_copy"
            new_item.enabled = original.enabled
            new_item.detection_method = "Manual"  # Las copias son siempre manuales
            new_item.confidence = 0.0
            
            # Mover la nueva entrada después de la original
            settings.bone_mappings.move(len(settings.bone_mappings) - 1, index + 1)
            settings.bone_mappings_index = index + 1
            
            self.report({'INFO'}, "Entrada duplicada.")
        else:
            self.report({'WARNING'}, "No hay entrada seleccionada para duplicar.")
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_invert_mapping(Operator):
    """Invertir mapeo seleccionado (intercambiar source y target)"""
    bl_idname = "universalgta.invert_mapping"
    bl_label = "Invert Mapping"
    bl_description = "Swap source and target bones for selected mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        
        if 0 <= index < len(settings.bone_mappings):
            item = settings.bone_mappings[index]
            
            # Intercambiar source y target
            temp = item.source_bone
            item.source_bone = item.target_bone
            item.target_bone = temp
            
            # Resetear método y confianza ya que el mapeo cambió
            item.detection_method = "Manual"
            item.confidence = 0.0
            
            self.report({'INFO'}, "Mapeo invertido.")
        else:
            self.report({'WARNING'}, "No hay entrada seleccionada para invertir.")
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_enable_all_mappings(Operator):
    """Habilitar todos los mapeos"""
    bl_idname = "universalgta.enable_all_mappings"
    bl_label = "Enable All"
    bl_description = "Enable all bone mappings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        enabled_count = 0
        for item in settings.bone_mappings:
            if not item.enabled:
                item.enabled = True
                enabled_count += 1
        
        self.report({'INFO'}, f"Habilitados {enabled_count} mapeos.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_disable_all_mappings(Operator):
    """Deshabilitar todos los mapeos"""
    bl_idname = "universalgta.disable_all_mappings"
    bl_label = "Disable All"
    bl_description = "Disable all bone mappings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        disabled_count = 0
        for item in settings.bone_mappings:
            if item.enabled:
                item.enabled = False
                disabled_count += 1
        
        self.report({'INFO'}, f"Deshabilitados {disabled_count} mapeos.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_enable_high_confidence(Operator):
    """Habilitar solo mapeos de alta confianza"""
    bl_idname = "universalgta.enable_high_confidence"
    bl_label = "Enable High Confidence"
    bl_description = "Enable only high confidence automatic mappings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        enabled_count = 0
        threshold = 0.7  # Umbral de alta confianza
        
        for item in settings.bone_mappings:
            if item.detection_method == "Auto" and item.confidence >= threshold:
                if not item.enabled:
                    item.enabled = True
                    enabled_count += 1
            else:
                item.enabled = False
        
        self.report({'INFO'}, f"Habilitados {enabled_count} mapeos de alta confianza (>{threshold}).")
        return {'FINISHED'}


# Lista de clases para registrar - COMPLETA CON TODAS LAS MEJORAS
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
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)