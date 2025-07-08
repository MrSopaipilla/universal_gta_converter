"""
Operadores de mapeo corregidos - Solo excluye Root, mantiene Pelvis
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty


class UNIVERSALGTA_OT_add_target_bones(Operator):
    """Agregar todos los huesos del armature destino (solo excluye Root)"""
    bl_idname = "universalgta.add_target_bones"
    bl_label = "Add Target Bones"
    bl_description = "Add all target armature bones to mapping list (excludes only Root bone)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        target_armature = settings.target_armature
        
        if not target_armature or target_armature.type != 'ARMATURE':
            self.report({'WARNING'}, "No hay target armature asignado.")
            return {'CANCELLED'}
        
        # Limpiar mapeos existentes
        settings.bone_mappings.clear()
        
        # SOLO excluir huesos Root (mantener Pelvis)
        excluded_bones = {'Root', 'root', 'ROOT'}
        
        added_count = 0
        excluded_count = 0
        
        # Agregar huesos del target (excepto Root)
        for bone in target_armature.pose.bones:
            if bone.name in excluded_bones:
                print(f"[MAPPING] Hueso excluido automáticamente: {bone.name}")
                excluded_count += 1
                continue
            
            item = settings.bone_mappings.add()
            item.source_bone = ""
            item.target_bone = bone.name
            
            # Pelvis habilitado por defecto, otros también
            item.enabled = True
            item.detection_method = "Manual"
            item.confidence = 0.0
            added_count += 1
        
        settings.bone_mappings_index = 0
        self.report({'INFO'}, f"Agregados {added_count} huesos incluyendo Pelvis. {excluded_count} huesos Root excluidos.")
        return {'FINISHED'}


class UNIVERSALGTA_OT_auto_detect_mappings(Operator):
    """Detectar automáticamente mapeos de huesos (solo excluye Root)"""
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
        self.report({'INFO'}, f"Detectados {len(detected_mappings)} mapeos automáticamente (solo Root excluido, Pelvis incluido).")
        return {'FINISHED'}
    
    def detect_bone_mappings(self, source_armature, target_armature, settings):
        """
        Detecta automáticamente mapeos de huesos usando múltiples algoritmos
        SOLO EXCLUYE huesos Root (mantiene Pelvis)
        """
        import difflib
        
        source_bones = [bone.name for bone in source_armature.pose.bones]
        target_bones = [bone.name for bone in target_armature.pose.bones]
        
        # SOLO EXCLUIR HUESOS ROOT (mantener Pelvis y otros)
        excluded_bones = {'Root', 'root', 'ROOT'}
        
        # Filtrar solo huesos Root del target
        filtered_target_bones = [bone for bone in target_bones if bone not in excluded_bones]
        
        print(f"[AUTO_DETECT] Huesos target filtrados: {len(filtered_target_bones)} de {len(target_bones)}")
        print(f"[AUTO_DETECT] Solo excluidos: {excluded_bones.intersection(set(target_bones))}")
        print(f"[AUTO_DETECT] Pelvis incluido: {'Pelvis' in filtered_target_bones}")
        
        mappings = []
        threshold = settings.detection_threshold if hasattr(settings, 'detection_threshold') else 0.5
        
        # Patrones de mapeo inteligentes para GTA SA (nomenclatura EXACTA con espacios)
        gta_patterns = {
            # Columna vertebral (algunos con espacio al inicio, otros sin)
            'Pelvis': ['pelvis', 'hip', 'hips', 'root', 'base'],
            ' Spine': ['spine', 'back', 'torso', 'spine1'],     # CON espacio al inicio
            ' Spine1': ['spine1', 'chest', 'upper_torso', 'spine2'],  # CON espacio al inicio
            ' Neck': ['neck', 'cervical'],                     # CON espacio al inicio
            ' Head': ['head', 'skull'],                        # CON espacio al inicio
            
            # Brazos izquierdos (nomenclatura exacta GTA SA)
            'Bip01 L Clavicle': ['l_clavicle', 'left_clavicle', 'l_shoulder', 'left_shoulder', 'clavicle_l', 'clavicle.l', 'bip01_l_clavicle'],
            ' L UpperArm': ['l_upperarm', 'left_upperarm', 'l_arm', 'left_arm', 'l_humerus', 'upperarm_l', 'arm.l'],  # CON espacio al inicio
            ' L ForeArm': ['l_forearm', 'left_forearm', 'l_lower_arm', 'left_lower_arm', 'forearm_l', 'forearm.l'],   # CON espacio al inicio, ForeArm
            ' L Hand': ['l_hand', 'left_hand', 'hand_l', 'hand.l'],        # CON espacio al inicio
            ' L Finger': ['l_finger', 'left_finger', 'finger_l', 'finger.l'],  # CON espacio al inicio
            'L Finger01': ['l_finger01', 'left_finger01', 'finger01_l', 'finger01.l', 'l_finger_01'],  # SIN espacio al inicio
            
            # Brazos derechos (nomenclatura exacta GTA SA)
            'Bip01 R Clavicle': ['r_clavicle', 'right_clavicle', 'r_shoulder', 'right_shoulder', 'clavicle_r', 'clavicle.r', 'bip01_r_clavicle'],
            ' R UpperArm': ['r_upperarm', 'right_upperarm', 'r_arm', 'right_arm', 'r_humerus', 'upperarm_r', 'arm.r'],  # CON espacio al inicio
            ' R ForeArm': ['r_forearm', 'right_forearm', 'r_lower_arm', 'right_lower_arm', 'forearm_r', 'forearm.r'],   # CON espacio al inicio, ForeArm
            ' R Hand': ['r_hand', 'right_hand', 'hand_r', 'hand.r'],        # CON espacio al inicio
            ' R Finger': ['r_finger', 'right_finger', 'finger_r', 'finger.r'],  # CON espacio al inicio
            'R Finger01': ['r_finger01', 'right_finger01', 'finger01_r', 'finger01.r', 'r_finger_01'],  # SIN espacio al inicio
            
            # Piernas izquierdas (CON espacios al inicio - nomenclatura SA)
            ' L Thigh': ['l_thigh', 'left_thigh', 'l_leg', 'left_leg', 'l_femur', 'thigh_l', 'thigh.l', 'leg.l'],  # CON espacio al inicio
            ' L Calf': ['l_calf', 'left_calf', 'l_shin', 'left_shin', 'l_lower_leg', 'calf_l', 'calf.l', 'shin.l'],  # CON espacio al inicio
            ' L Foot': ['l_foot', 'left_foot', 'foot_l', 'foot.l'],         # CON espacio al inicio
            ' L Toe0': ['l_toe', 'left_toe', 'toe_l', 'toe.l', 'l_toe0', 'l_toe_0'],  # CON espacio al inicio
            
            # Piernas derechas (CON espacios al inicio - nomenclatura SA)
            ' R Thigh': ['r_thigh', 'right_thigh', 'r_leg', 'right_leg', 'r_femur', 'thigh_r', 'thigh.r', 'leg.r'],  # CON espacio al inicio
            ' R Calf': ['r_calf', 'right_calf', 'r_shin', 'right_shin', 'r_lower_leg', 'calf_r', 'calf.r', 'shin.r'],  # CON espacio al inicio
            ' R Foot': ['r_foot', 'right_foot', 'foot_r', 'foot.r'],         # CON espacio al inicio
            ' R Toe0': ['r_toe', 'right_toe', 'toe_r', 'toe.r', 'r_toe0', 'r_toe_0'],  # CON espacio al inicio
            
            # Huesos faciales (SIN espacios al inicio - nomenclatura SA)
            'Jaw': ['jaw', 'chin', 'mandible'],                # SIN espacio al inicio
            'L Brow': ['l_brow', 'left_brow', 'l_eyebrow', 'left_eyebrow', 'brow_l', 'brow.l'],  # SIN espacio al inicio
            'R Brow': ['r_brow', 'right_brow', 'r_eyebrow', 'right_eyebrow', 'brow_r', 'brow.r'],  # SIN espacio al inicio
            
            # Cuerpo especial (SIN espacios al inicio - nomenclatura exacta SA)
            'L breast': ['l_breast', 'left_breast', 'breast_l', 'breast.l'],  # SIN espacio al inicio
            'R breast': ['r_breast', 'right_breast', 'breast_r', 'breast.r'],  # SIN espacio al inicio
            'Belly': ['belly', 'abdomen', 'stomach', 'gut'],   # SIN espacio al inicio
        }
        
        # Algoritmo 1: Mapeo por patrones específicos de GTA SA
        used_source_bones = set()
        
        for target_bone in filtered_target_bones:  # Usar huesos filtrados (sin Root)
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
                
                # Log especial para Pelvis
                if target_bone == 'Pelvis':
                    print(f"[AUTO_DETECT] ⭐ PELVIS: {best_match} -> {target_bone} (confianza: {best_confidence:.2f})")
                else:
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
        
        # Partes del cuerpo (incluyendo pelvis y hip)
        body_parts = [
            'head', 'neck', 'spine', 'chest', 'back',
            'arm', 'shoulder', 'elbow', 'wrist', 'hand', 'finger',
            'leg', 'thigh', 'knee', 'ankle', 'foot', 'toe',
            'hip', 'hips', 'pelvis', 'clavicle', 'breast'  # Hip y pelvis incluidos
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
        
        # Lista de huesos que DEBERÍAN estar deshabilitados (solo Root)
        should_be_disabled = {'Root', 'root', 'ROOT'}
        
        for i, item in enumerate(settings.bone_mappings):
            line_num = i + 1
            
            # Verificar solo si huesos Root están habilitados (advertencia)
            if item.enabled and item.target_bone in should_be_disabled:
                warnings.append(f"Línea {line_num}: Hueso '{item.target_bone}' no debería ser mapeado (se recomienda deshabilitar)")
            
            # Mensaje especial para Pelvis
            if item.enabled and item.target_bone == 'Pelvis':
                print(f"[VALIDATION] ✅ Pelvis habilitado correctamente en línea {line_num}")
            
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
        
        # Verificar que Pelvis esté incluido
        pelvis_found = any(m.enabled and m.target_bone == 'Pelvis' for m in settings.bone_mappings)
        if pelvis_found:
            print("[VALIDATION] ✅ Pelvis encontrado en los mapeos activos")
        else:
            warnings.append("Pelvis no está mapeado - es importante para GTA SA")
        
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


class UNIVERSALGTA_OT_enable_all_mappings(Operator):
    """Habilitar todos los mapeos (excepto solo Root)"""
    bl_idname = "universalgta.enable_all_mappings"
    bl_label = "Enable All"
    bl_description = "Enable all bone mappings except Root bones (Pelvis included)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Solo excluir huesos Root (mantener Pelvis)
        excluded_bones = {'Root', 'root', 'ROOT'}
        
        enabled_count = 0
        excluded_count = 0
        pelvis_enabled = False
        
        for item in settings.bone_mappings:
            if item.target_bone in excluded_bones:
                if item.enabled:
                    item.enabled = False
                    excluded_count += 1
            elif not item.enabled:
                item.enabled = True
                enabled_count += 1
                
                # Verificar si habilitamos Pelvis
                if item.target_bone == 'Pelvis':
                    pelvis_enabled = True
        
        message = f"Habilitados {enabled_count} mapeos"
        if pelvis_enabled:
            message += " (incluyendo Pelvis)"
        message += "."
        
        if excluded_count > 0:
            message += f" {excluded_count} huesos Root deshabilitados automáticamente."
        
        self.report({'INFO'}, message)
        return {'FINISHED'}


class UNIVERSALGTA_OT_enable_high_confidence(Operator):
    """Habilitar solo mapeos de alta confianza (solo excluye Root)"""
    bl_idname = "universalgta.enable_high_confidence"
    bl_label = "Enable High Confidence"
    bl_description = "Enable only high confidence automatic mappings (excludes only Root bones)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        enabled_count = 0
        threshold = 0.7  # Umbral de alta confianza
        excluded_bones = {'Root', 'root', 'ROOT'}  # Solo Root
        pelvis_enabled = False
        
        for item in settings.bone_mappings:
            # Deshabilitar solo huesos Root automáticamente
            if item.target_bone in excluded_bones:
                item.enabled = False
            # Habilitar mapeos automáticos de alta confianza (incluyendo Pelvis)
            elif item.detection_method == "Auto" and item.confidence >= threshold:
                if not item.enabled:
                    item.enabled = True
                    enabled_count += 1
                    
                    if item.target_bone == 'Pelvis':
                        pelvis_enabled = True
            else:
                item.enabled = False
        
        message = f"Habilitados {enabled_count} mapeos de alta confianza (>{threshold})"
        if pelvis_enabled:
            message += " incluyendo Pelvis"
        message += ". Solo Root excluido."
        
        self.report({'INFO'}, message)
        return {'FINISHED'}


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


class UNIVERSALGTA_OT_load_mapping(Operator):
    """Cargar configuración de mapeo desde archivo"""
    bl_idname = "universalgta.load_mapping"
    bl_label = "Load Mapping"
    bl_description = "Load bone mapping configuration from file"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        # Placeholder para futuras funciones de carga
        self.report({'INFO'}, "Función de carga no implementada aún")
        return {'FINISHED'}


class UNIVERSALGTA_OT_save_mapping(Operator):
    """Guardar configuración de mapeo a archivo"""
    bl_idname = "universalgta.save_mapping"
    bl_label = "Save Mapping"
    bl_description = "Save bone mapping configuration to file"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        # Placeholder para futuras funciones de guardado
        self.report({'INFO'}, "Función de guardado no implementada aún")
        return {'FINISHED'}


class UNIVERSALGTA_OT_duplicate_mapping(Operator):
    """Duplicar mapeo seleccionado"""
    bl_idname = "universalgta.duplicate_mapping"
    bl_label = "Duplicate Mapping"
    bl_description = "Duplicate selected bone mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        index = settings.bone_mappings_index
        
        if 0 <= index < len(settings.bone_mappings):
            original = settings.bone_mappings[index]
            
            # Crear nuevo item
            item = settings.bone_mappings.add()
            item.source_bone = original.source_bone
            item.target_bone = original.target_bone + "_copy"
            item.enabled = original.enabled
            item.detection_method = "Manual"  # Los duplicados son manuales
            item.confidence = 0.0
            
            # Mover al final de la lista
            settings.bone_mappings_index = len(settings.bone_mappings) - 1
            self.report({'INFO'}, "Mapeo duplicado.")
        else:
            self.report({'WARNING'}, "No hay mapeo seleccionado para duplicar.")
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_invert_mapping(Operator):
    """Invertir mapeo seleccionado (intercambiar source y target)"""
    bl_idname = "universalgta.invert_mapping"
    bl_label = "Invert Mapping"
    bl_description = "Invert selected bone mapping (swap source and target)"
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
            
            # Marcar como manual ya que se modificó
            item.detection_method = "Manual"
            item.confidence = 0.0
            
            self.report({'INFO'}, "Mapeo invertido.")
        else:
            self.report({'WARNING'}, "No hay mapeo seleccionado para invertir.")
        
        return {'FINISHED'}


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_add_target_bones,
    UNIVERSALGTA_OT_auto_detect_mappings,
    UNIVERSALGTA_OT_add_custom_entry,
    UNIVERSALGTA_OT_remove_mapping_entry,
    UNIVERSALGTA_OT_move_mapping_up,
    UNIVERSALGTA_OT_move_mapping_down,
    UNIVERSALGTA_OT_clear_mappings,
    UNIVERSALGTA_OT_validate_mappings,
    UNIVERSALGTA_OT_enable_all_mappings,
    UNIVERSALGTA_OT_disable_all_mappings,
    UNIVERSALGTA_OT_enable_high_confidence,
    UNIVERSALGTA_OT_load_mapping,
    UNIVERSALGTA_OT_save_mapping,
    UNIVERSALGTA_OT_duplicate_mapping,
    UNIVERSALGTA_OT_invert_mapping,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
