#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMART DETECT FIX - Universal GTA SA Converter
===========================================
MEJORA ESPECÍFICA del sistema Smart Auto-Detect

PROBLEMA IDENTIFICADO:
❌ Smart detect no reconoce huesos que SÍ existen
❌ Muchos warnings: "Huesos no encontrados en armature"
❌ No detecta variaciones de nombres (case-sensitive)

SOLUCIONES:
✅ Fuzzy matching para nombres similares
✅ Case-insensitive comparisons
✅ Detección de prefijos/sufijos comunes
✅ Sistema de score mejorado para matchings
"""

import bpy
from pathlib import Path

class SmartDetectFix:
    """Mejora específica del Smart Auto-Detect"""
    
    def __init__(self):
        print("🧠 SMART DETECT FIX - Mejorando detección de huesos")
        print("=" * 60)
    
    def create_improved_smart_detect(self):
        """Crear versión mejorada del smart detect en operators/conversion.py"""
        addon_root = Path(__file__).parent
        file_path = addon_root / "operators" / "conversion.py"
        
        if not file_path.exists():
            print("❌ No se encontró operators/conversion.py")
            return False
        
        # Leer contenido actual
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar la función smart_auto_detect y mejorarla
        improved_detect_method = '''
    
    def execute_with_duplicates_support(self, context):
        """Ejecutar con soporte para duplicados mejorado"""
        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature or not settings.target_armature:
            self.report({'ERROR'}, "Selecciona source y target armature")
            return {'CANCELLED'}
        
        try:
            from .improved_bone_mapping_system import ImprovedBoneMappingSystem
            
            # Intentar cargar desde caché primero
            cached_data = ImprovedBoneMappingSystem.load_cached_mapping(settings.source_armature)
            if cached_data and getattr(settings, 'autodetect_duplicates_enabled', True):
                applied = ImprovedBoneMappingSystem.apply_cached_mapping_to_settings(cached_data, settings)
                if applied:
                    self.report({'INFO'}, f"Cargados {len(cached_data.get('mappings', []))} mapeos desde caché")
                    return {'FINISHED'}
            
            # Proceder con autodetección normal
            source_bones = [bone.name for bone in settings.source_armature.pose.bones]
            target_bones = [bone.name for bone in settings.target_armature.pose.bones]
            
            print(f"[SMART_DETECT] Source bones: {len(source_bones)}")
            print(f"[SMART_DETECT] Target bones: {len(target_bones)}")
            
            # Preservar mapeos existentes con alta confianza si están habilitados duplicados
            existing_high_confidence = []
            if getattr(settings, 'autodetect_duplicates_enabled', True):
                confidence_threshold = getattr(settings, 'autodetect_confidence_threshold', 0.7)
                for mapping in settings.bone_mappings:
                    if mapping.enabled and mapping.confidence >= confidence_threshold:
                        existing_high_confidence.append({
                            'source': mapping.source_bone,
                            'target': mapping.target_bone,
                            'confidence': mapping.confidence,
                            'method': mapping.detection_method
                        })
            
            # Limpiar mapeos existentes
            settings.bone_mappings.clear()
            
            # Crear mapeos mejorados
            mappings_created = self.create_improved_mappings(source_bones, target_bones, settings)
            
            # Re-aplicar mapeos de alta confianza
            for existing in existing_high_confidence:
                found = False
                for mapping in settings.bone_mappings:
                    if mapping.source_bone == existing['source']:
                        if mapping.confidence < existing['confidence']:
                            mapping.target_bone = existing['target']
                            mapping.confidence = existing['confidence']
                            mapping.detection_method = f"Preserved: {existing['method']}"
                            mapping.enabled = True
                        found = True
                        break
                
                if not found:
                    # Crear mapeo preservado
                    new_mapping = settings.bone_mappings.add()
                    new_mapping.source_bone = existing['source']
                    new_mapping.target_bone = existing['target']
                    new_mapping.confidence = existing['confidence']
                    new_mapping.detection_method = f"Preserved: {existing['method']}"
                    new_mapping.enabled = True
                    mappings_created += 1
            
            self.report({'INFO'}, f"Smart Auto-Detect: {mappings_created} mapeos creados/actualizados")
            print(f"[SMART_DETECT] Total mapeos: {mappings_created}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en Smart Auto-Detect: {e}")
            return {'CANCELLED'}
    def execute(self, context):
        return self.execute_with_duplicates_support(context)
    
    def execute_original(self, context):
        """Smart Auto-Detect MEJORADO con fuzzy matching"""
        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature or not settings.target_armature:
            self.report({'ERROR'}, "Selecciona source y target armature")
            return {'CANCELLED'}
        
        try:
            print("[SMART_DETECT] Iniciando detección inteligente mejorada...")
            
            source_bones = [bone.name for bone in settings.source_armature.data.bones]
            target_bones = [bone.name for bone in settings.target_armature.data.bones]
            
            print(f"[SMART_DETECT] Source bones: {len(source_bones)}")
            print(f"[SMART_DETECT] Target bones: {len(target_bones)}")
            
            # Limpiar mapeos existentes
            settings.bone_mappings.clear()
            
            # IMPROVED: Sistema de matching avanzado
            mappings_created = self.create_improved_mappings(
                source_bones, target_bones, settings
            )
            
            self.report({'INFO'}, f"Smart Auto-Detect: {mappings_created} mapeos creados")
            print(f"[SMART_DETECT] Total mapeos creados: {mappings_created}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en Smart Auto-Detect: {e}")
            return {'CANCELLED'}
    
    def create_improved_mappings(self, source_bones, target_bones, settings):
        """Crear mapeos mejorados con fuzzy matching"""
        mappings_created = 0
        
        # Convertir a lowercase para comparaciones
        source_lower = {bone.lower(): bone for bone in source_bones}
        target_lower = {bone.lower(): bone for bone in target_bones}
        
        print("[SMART_DETECT] Iniciando fuzzy matching...")
        
        # 1. EXACT MATCHES (case-insensitive)
        for source_key, source_name in source_lower.items():
            if source_key in target_lower:
                target_name = target_lower[source_key]
                self.add_mapping(settings, source_name, target_name, "Exact Match", 1.0)
                mappings_created += 1
                print(f"[SMART_DETECT] Exact: {source_name} -> {target_name}")
        
        # 2. FUZZY MATCHES para huesos comunes
        fuzzy_mappings = {
            # Spine variations
            'bip_pelvis': ['pelvis', 'hip', 'root'],
            'bip_spine_0': ['spine', 'spine1', 'spine_01'],
            'bip_spine_1': ['spine1', 'spine2', 'spine_02'],
            'bip_spine_2': ['spine2', 'spine3', 'spine_03'],
            'bip_neck': ['neck', 'neck_01'],
            'bip_head': ['head', 'head_01'],
            
            # Arms L
            'bip_collar_l': ['bip01 l clavicle', 'l clavicle', 'clavicle_l'],
            'bip_upperarm_l': ['l upperarm', 'upperarm_l', 'arm_l'],
            'bip_lowerarm_l': ['l forearm', 'forearm_l', 'lowerarm_l'],
            'bip_hand_l': ['l hand', 'hand_l'],
            
            # Arms R  
            'bip_collar_r': ['bip01 r clavicle', 'r clavicle', 'clavicle_r'],
            'bip_upperarm_r': ['r upperarm', 'upperarm_r', 'arm_r'],
            'bip_lowerarm_r': ['r forearm', 'forearm_r', 'lowerarm_r'],
            'bip_hand_r': ['r hand', 'hand_r'],
            
            # Legs L
            'bip_hip_l': ['l thigh', 'thigh_l', 'leg_l'],
            'bip_knee_l': ['l calf', 'calf_l', 'shin_l'],
            'bip_foot_l': ['l foot', 'foot_l'],
            'bip_toe_l': ['l toe0', 'toe_l'],
            
            # Legs R
            'bip_hip_r': ['r thigh', 'thigh_r', 'leg_r'],
            'bip_knee_r': ['r calf', 'calf_r', 'shin_r'],
            'bip_foot_r': ['r foot', 'foot_r'],
            'bip_toe_r': ['r toe0', 'toe_r'],
        }
        
        for source_pattern, target_patterns in fuzzy_mappings.items():
            # Buscar source bone que contenga el patrón
            source_matches = [bone for bone_key, bone in source_lower.items() 
                            if source_pattern.lower() in bone_key]
            
            for source_bone in source_matches:
                # Buscar target bone que coincida con algún patrón
                for target_pattern in target_patterns:
                    target_matches = [bone for bone_key, bone in target_lower.items() 
                                    if target_pattern.lower() in bone_key]
                    
                    if target_matches:
                        target_bone = target_matches[0]  # Tomar el primero
                        # Verificar que no existe ya este mapeo
                        if not self.mapping_exists(settings, source_bone, target_bone):
                            confidence = 0.8  # Alta confianza para fuzzy matching
                            self.add_mapping(settings, source_bone, target_bone, 
                                           "Fuzzy Match", confidence)
                            mappings_created += 1
                            print(f"[SMART_DETECT] Fuzzy: {source_bone} -> {target_bone}")
                        break
        
        # 3. PARTIAL MATCHES para casos especiales
        for source_bone in source_bones:
            source_key = source_bone.lower()
            
            # Buscar coincidencias parciales
            for target_bone in target_bones:
                target_key = target_bone.lower()
                
                # Skip si ya existe mapeo
                if self.mapping_exists(settings, source_bone, target_bone):
                    continue
                
                # Coincidencias parciales comunes
                partial_matches = [
                    ('jaw', 'jaw'),
                    ('tongue', 'jaw'),  # Tongue suele mapearse a jaw
                    ('finger', 'finger'),
                    ('thumb', 'finger'),  # Thumb puede ir a finger general
                ]
                
                for source_part, target_part in partial_matches:
                    if source_part in source_key and target_part in target_key:
                        confidence = 0.6  # Menor confianza para partial
                        self.add_mapping(settings, source_bone, target_bone,
                                       "Partial Match", confidence)
                        mappings_created += 1
                        print(f"[SMART_DETECT] Partial: {source_bone} -> {target_bone}")
                        break
        
        return mappings_created
    
    def mapping_exists(self, settings, source_bone, target_bone):
        """Verificar si ya existe un mapeo"""
        for mapping in settings.bone_mappings:
            if mapping.source_bone == source_bone and mapping.target_bone == target_bone:
                return True
        return False
    
    def add_mapping(self, settings, source_bone, target_bone, method, confidence):
        """Agregar mapeo con información de detección"""
        mapping = settings.bone_mappings.add()
        mapping.source_bone = source_bone
        mapping.target_bone = target_bone
        mapping.enabled = True
        mapping.detection_method = f"Smart Auto-Detect ({method})"
        mapping.confidence = confidence
'''
        
        # Buscar y reemplazar el método execute en UNIVERSALGTA_OT_smart_auto_detect
        if 'class UNIVERSALGTA_OT_smart_auto_detect' in content:
            # Encontrar la clase y reemplazar su método execute
            lines = content.split('\n')
            new_lines = []
            inside_smart_detect = False
            inside_execute = False
            indent_level = 0
            
            for i, line in enumerate(lines):
                if 'class UNIVERSALGTA_OT_smart_auto_detect' in line:
                    inside_smart_detect = True
                    new_lines.append(line)
                elif inside_smart_detect and line.strip().startswith('class ') and 'UNIVERSALGTA_OT_smart_auto_detect' not in line:
                    # Nueva clase encontrada, salir
                    inside_smart_detect = False
                    new_lines.append(line)
                elif inside_smart_detect and '
    def execute_with_duplicates_support(self, context):
        """Ejecutar con soporte para duplicados mejorado"""
        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature or not settings.target_armature:
            self.report({'ERROR'}, "Selecciona source y target armature")
            return {'CANCELLED'}
        
        try:
            from .improved_bone_mapping_system import ImprovedBoneMappingSystem
            
            # Intentar cargar desde caché primero
            cached_data = ImprovedBoneMappingSystem.load_cached_mapping(settings.source_armature)
            if cached_data and getattr(settings, 'autodetect_duplicates_enabled', True):
                applied = ImprovedBoneMappingSystem.apply_cached_mapping_to_settings(cached_data, settings)
                if applied:
                    self.report({'INFO'}, f"Cargados {len(cached_data.get('mappings', []))} mapeos desde caché")
                    return {'FINISHED'}
            
            # Proceder con autodetección normal
            source_bones = [bone.name for bone in settings.source_armature.pose.bones]
            target_bones = [bone.name for bone in settings.target_armature.pose.bones]
            
            print(f"[SMART_DETECT] Source bones: {len(source_bones)}")
            print(f"[SMART_DETECT] Target bones: {len(target_bones)}")
            
            # Preservar mapeos existentes con alta confianza si están habilitados duplicados
            existing_high_confidence = []
            if getattr(settings, 'autodetect_duplicates_enabled', True):
                confidence_threshold = getattr(settings, 'autodetect_confidence_threshold', 0.7)
                for mapping in settings.bone_mappings:
                    if mapping.enabled and mapping.confidence >= confidence_threshold:
                        existing_high_confidence.append({
                            'source': mapping.source_bone,
                            'target': mapping.target_bone,
                            'confidence': mapping.confidence,
                            'method': mapping.detection_method
                        })
            
            # Limpiar mapeos existentes
            settings.bone_mappings.clear()
            
            # Crear mapeos mejorados
            mappings_created = self.create_improved_mappings(source_bones, target_bones, settings)
            
            # Re-aplicar mapeos de alta confianza
            for existing in existing_high_confidence:
                found = False
                for mapping in settings.bone_mappings:
                    if mapping.source_bone == existing['source']:
                        if mapping.confidence < existing['confidence']:
                            mapping.target_bone = existing['target']
                            mapping.confidence = existing['confidence']
                            mapping.detection_method = f"Preserved: {existing['method']}"
                            mapping.enabled = True
                        found = True
                        break
                
                if not found:
                    # Crear mapeo preservado
                    new_mapping = settings.bone_mappings.add()
                    new_mapping.source_bone = existing['source']
                    new_mapping.target_bone = existing['target']
                    new_mapping.confidence = existing['confidence']
                    new_mapping.detection_method = f"Preserved: {existing['method']}"
                    new_mapping.enabled = True
                    mappings_created += 1
            
            self.report({'INFO'}, f"Smart Auto-Detect: {mappings_created} mapeos creados/actualizados")
            print(f"[SMART_DETECT] Total mapeos: {mappings_created}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en Smart Auto-Detect: {e}")
            return {'CANCELLED'}
    def execute(self, context):
        return self.execute_with_duplicates_support(context)
    
    def execute_original(self, context):' in line:
                    inside_execute = True
                    # Agregar el método mejorado
                    new_lines.extend(improved_detect_method.split('\n'))
                    # Saltar el método original
                    continue
                elif inside_execute and (line.strip().startswith('def ') or 
                                       (line.strip().startswith('class ') and inside_smart_detect)):
                    inside_execute = False
                    new_lines.append(line)
                elif not inside_execute:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
        
        # Escribir el archivo actualizado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Smart Auto-Detect mejorado en operators/conversion.py")
        return True
    
    def run_fix(self):
        """Ejecutar mejora del smart detect"""
        print("🧠 Mejorando Smart Auto-Detect...")
        
        success = self.create_improved_smart_detect()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 SMART DETECT FIX COMPLETADO")
            print("=" * 60)
            
            print("\n🚀 MEJORAS IMPLEMENTADAS:")
            print("  ✅ Fuzzy matching para nombres similares")
            print("  ✅ Case-insensitive comparisons")
            print("  ✅ Detección de variaciones comunes de huesos")
            print("  ✅ Sistema de confidence scoring")
            print("  ✅ Partial matching para casos especiales")
            print("  ✅ Mapeos de tongue -> jaw automáticos")
            print("  ✅ Mejores coincidencias para fingers y thumbs")
            
            print("\n🎯 RESULTADOS ESPERADOS:")
            print("  - MENOS warnings 'Huesos no encontrados'")
            print("  - MÁS mapeos automáticos detectados")
            print("  - MEJOR reconocimiento de huesos existentes")
            print("  - Smart Auto-Detect más inteligente")
            
            print("\n🔄 Reinicia Blender y prueba Smart Auto-Detect")
            print("=" * 60)
        else:
            print("❌ Error mejorando Smart Auto-Detect")


def main():
    """Función principal"""
    print("🧠 Iniciando Smart Detect Fix...")
    print("🎯 Objetivo: Mejorar reconocimiento de huesos")
    print("=" * 60)
    
    fixer = SmartDetectFix()
    fixer.run_fix()


if __name__ == "__main__":
    main()
