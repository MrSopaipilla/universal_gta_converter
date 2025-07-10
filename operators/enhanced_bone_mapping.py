"""
Utilidades complementarias para el sistema Enhanced Bone Mapping
Funciones auxiliares, validaciones y herramientas de debugging
"""

import bpy
import bmesh
from mathutils import Vector, Matrix
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty
import re
import json
import time


class BoneMappingValidator:
    """Validador avanzado para mapeos de huesos"""
    
    @staticmethod
    def validate_armature_structure(armature):
        """Valida la estructura básica de un armature"""
        if not armature or armature.type != 'ARMATURE':
            return False, "No es un armature válido"
        
        if not armature.data.bones:
            return False, "Armature sin huesos"
        
        # Verificar que tenga al menos huesos básicos
        bone_names = [bone.name.lower() for bone in armature.data.bones]
        essential_patterns = ['spine', 'pelvis', 'root', 'hip']
        
        has_essential = any(pattern in ' '.join(bone_names) for pattern in essential_patterns)
        if not has_essential:
            return False, "No se detectaron huesos esenciales (spine, pelvis, root, hip)"
        
        return True, "Armature válido"
    
    @staticmethod
    def validate_mapping_consistency(mappings):
        """Valida la consistencia de los mapeos"""
        issues = []
        
        # Verificar duplicados en target bones
        target_bones = [m.target_bone for m in mappings if m.enabled and m.target_bone]
        duplicates = set([tb for tb in target_bones if target_bones.count(tb) > 1])
        if duplicates:
            issues.append(f"Target bones duplicados: {', '.join(duplicates)}")
        
        # Verificar mapeos sin source bone
        empty_sources = [m.target_bone for m in mappings if m.enabled and not m.source_bone]
        if empty_sources:
            issues.append(f"Mapeos sin source bone: {', '.join(empty_sources)}")
        
        # Verificar mapeos con baja confianza
        low_confidence = [m.target_bone for m in mappings 
                         if m.enabled and m.detection_method == "Auto" and m.confidence < 0.5]
        if low_confidence:
            issues.append(f"Mapeos con baja confianza: {', '.join(low_confidence)}")
        
        return issues
    
    @staticmethod
    def validate_gta_sa_compliance(mappings):
        """Valida que los mapeos cumplan con los requisitos de GTA SA"""
        gta_required_bones = [
            'Pelvis', 'belly', 'chest', 'neck', 'head',
            'L Clavicle', 'L UpperArm', 'L Forearm', 'L Hand',
            'R Clavicle', 'R UpperArm', 'R Forearm', 'R Hand',
            'L Thigh', 'L Calf', 'L Foot',
            'R Thigh', 'R Calf', 'R Foot'
        ]
        
        mapped_targets = [m.target_bone for m in mappings if m.enabled and m.target_bone]
        missing_bones = [bone for bone in gta_required_bones if bone not in mapped_targets]
        
        return missing_bones


class BoneMappingAnalyzer:
    """Analizador avanzado de mapeos de huesos"""
    
    @staticmethod
    def analyze_mapping_quality(settings):
        """Analiza la calidad general de los mapeos"""
        if not settings.bone_mappings:
            return {"quality": "no_mappings", "score": 0.0, "issues": ["No hay mapeos configurados"]}
        
        total_mappings = len(settings.bone_mappings)
        enabled_mappings = sum(1 for m in settings.bone_mappings if m.enabled)
        complete_mappings = sum(1 for m in settings.bone_mappings 
                               if m.enabled and m.source_bone and m.target_bone)
        
        # Calcular score de confianza promedio
        confidence_scores = [m.confidence for m in settings.bone_mappings 
                           if m.enabled and m.confidence > 0]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Verificar huesos esenciales
        essential_bones = ['Pelvis', 'chest', 'head', 'L UpperArm', 'R UpperArm', 'L Thigh', 'R Thigh']
        mapped_essentials = sum(1 for bone in essential_bones 
                               if any(m.enabled and m.target_bone == bone 
                                     for m in settings.bone_mappings))
        
        # Calcular score final
        completion_score = complete_mappings / total_mappings if total_mappings > 0 else 0
        essential_score = mapped_essentials / len(essential_bones)
        final_score = (completion_score * 0.4 + avg_confidence * 0.3 + essential_score * 0.3)
        
        # Determinar calidad
        if final_score >= 0.8:
            quality = "excellent"
        elif final_score >= 0.6:
            quality = "good"
        elif final_score >= 0.4:
            quality = "fair"
        else:
            quality = "poor"
        
        issues = BoneMappingValidator.validate_mapping_consistency(settings.bone_mappings)
        missing_essentials = [bone for bone in essential_bones 
                             if not any(m.enabled and m.target_bone == bone 
                                       for m in settings.bone_mappings)]
        if missing_essentials:
            issues.append(f"Huesos esenciales faltantes: {', '.join(missing_essentials)}")
        
        return {
            "quality": quality,
            "score": final_score,
            "completion_rate": completion_score,
            "avg_confidence": avg_confidence,
            "essential_coverage": essential_score,
            "total_mappings": total_mappings,
            "enabled_mappings": enabled_mappings,
            "complete_mappings": complete_mappings,
            "issues": issues
        }
    
    @staticmethod
    def suggest_improvements(analysis_result):
        """Sugiere mejoras basadas en el análisis"""
        suggestions = []
        
        if analysis_result["completion_rate"] < 0.8:
            suggestions.append("Completar mapeos faltantes usando 'Add All Bones' y mapeo manual")
        
        if analysis_result["avg_confidence"] < 0.6:
            suggestions.append("Revisar mapeos automáticos con baja confianza y ajustar manualmente")
        
        if analysis_result["essential_coverage"] < 0.8:
            suggestions.append("Asegurar que huesos esenciales (Pelvis, chest, head, extremidades) estén mapeados")
        
        if "duplicados" in str(analysis_result["issues"]):
            suggestions.append("Resolver mapeos duplicados usando herramientas de validación")
        
        return suggestions


class UNIVERSALGTA_OT_AnalyzeMappingQuality(Operator):
    """Analiza la calidad de los mapeos actuales"""
    bl_idname = "universalgta.analyze_mapping_quality"
    bl_label = "Analyze Mapping Quality"
    bl_description = "Analiza la calidad y completitud de los mapeos actuales"
    bl_options = {'REGISTER'}
    
    show_detailed_report: BoolProperty(
        name="Show Detailed Report",
        description="Mostrar reporte detallado en la consola",
        default=True
    )
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Realizar análisis
        analysis = BoneMappingAnalyzer.analyze_mapping_quality(settings)
        suggestions = BoneMappingAnalyzer.suggest_improvements(analysis)
        
        # Mostrar resultado básico
        quality_text = {
            "excellent": "Excelente ✓",
            "good": "Buena ✓", 
            "fair": "Regular ⚠",
            "poor": "Pobre ✗",
            "no_mappings": "Sin mapeos ✗"
        }
        
        self.report({'INFO'}, 
                   f"Calidad de mapeos: {quality_text[analysis['quality']]} "
                   f"(Score: {analysis['score']:.1%})")
        
        # Mostrar reporte detallado si está habilitado
        if self.show_detailed_report:
            self.print_detailed_report(analysis, suggestions)
        
        # Guardar análisis en scene para acceso desde otros operadores
        settings.last_analysis_result = str(analysis)
        
        return {'FINISHED'}
    
    def print_detailed_report(self, analysis, suggestions):
        """Imprime un reporte detallado en la consola"""
        print("\n" + "="*60)
        print("BONE MAPPING QUALITY ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n📊 OVERALL QUALITY: {analysis['quality'].upper()}")
        print(f"📈 Overall Score: {analysis['score']:.1%}")
        
        print(f"\n📋 STATISTICS:")
        print(f"   • Total Mappings: {analysis['total_mappings']}")
        print(f"   • Enabled Mappings: {analysis['enabled_mappings']}")
        print(f"   • Complete Mappings: {analysis['complete_mappings']}")
        print(f"   • Completion Rate: {analysis['completion_rate']:.1%}")
        print(f"   • Average Confidence: {analysis['avg_confidence']:.1%}")
        print(f"   • Essential Bones Coverage: {analysis['essential_coverage']:.1%}")
        
        if analysis['issues']:
            print(f"\n⚠️  ISSUES FOUND:")
            for issue in analysis['issues']:
                print(f"   • {issue}")
        
        if suggestions:
            print(f"\n💡 IMPROVEMENT SUGGESTIONS:")
            for suggestion in suggestions:
                print(f"   • {suggestion}")
        
        print("\n" + "="*60)


class UNIVERSALGTA_OT_GenerateMappingReport(Operator):
    """Genera un reporte completo de mapeos"""
    bl_idname = "universalgta.generate_mapping_report" 
    bl_label = "Generate Mapping Report"
    bl_description = "Genera un reporte completo de los mapeos en formato JSON"
    bl_options = {'REGISTER'}
    
    include_analysis: BoolProperty(
        name="Include Analysis",
        description="Incluir análisis de calidad en el reporte",
        default=True
    )
    
    include_suggestions: BoolProperty(
        name="Include Suggestions", 
        description="Incluir sugerencias de mejora",
        default=True
    )
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Generar reporte
        report = self.generate_report(settings, context)
        
        # Guardar en archivo temporal
        import tempfile
        temp_file = tempfile.mktemp(suffix=".json")
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            self.report({'INFO'}, f"Reporte generado: {temp_file}")
            print(f"\n📄 MAPPING REPORT SAVED TO: {temp_file}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error guardando reporte: {e}")
        
        return {'FINISHED'}
    
    def generate_report(self, settings, context):
        """Genera el reporte completo"""
        report = {
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "addon_version": "3.2.3",
                "blender_version": bpy.app.version_string,
                "source_armature": settings.source_armature.name if settings.source_armature else None,
                "target_armature": settings.target_armature.name if settings.target_armature else None
            },
            "settings": {
                "arm_spacing": settings.arm_spacing,
                "leg_spacing": settings.leg_spacing,
                "detection_threshold": settings.detection_threshold
            },
            "mappings": []
        }
        
        # Agregar mapeos
        for i, mapping in enumerate(settings.bone_mappings):
            mapping_data = {
                "index": i,
                "source_bone": mapping.source_bone,
                "target_bone": mapping.target_bone,
                "enabled": mapping.enabled,
                "detection_method": mapping.detection_method,
                "confidence": mapping.confidence
            }
            report["mappings"].append(mapping_data)
        
        # Agregar análisis si está habilitado
        if self.include_analysis:
            analysis = BoneMappingAnalyzer.analyze_mapping_quality(settings)
            report["quality_analysis"] = analysis
        
        # Agregar sugerencias si está habilitado
        if self.include_suggestions and self.include_analysis:
            suggestions = BoneMappingAnalyzer.suggest_improvements(analysis)
            report["improvement_suggestions"] = suggestions
        
        # Agregar validaciones
        armature_issues = []
        if settings.source_armature:
            valid, message = BoneMappingValidator.validate_armature_structure(settings.source_armature)
            armature_issues.append({"armature": "source", "valid": valid, "message": message})
        
        if settings.target_armature:
            valid, message = BoneMappingValidator.validate_armature_structure(settings.target_armature)
            armature_issues.append({"armature": "target", "valid": valid, "message": message})
        
        report["validations"] = {
            "armature_checks": armature_issues,
            "mapping_consistency": BoneMappingValidator.validate_mapping_consistency(settings.bone_mappings),
            "gta_sa_missing_bones": BoneMappingValidator.validate_gta_sa_compliance(settings.bone_mappings)
        }
        
        return report


class UNIVERSALGTA_OT_DebugMappingSystem(Operator):
    """Herramienta de debug para el sistema de mapeos"""
    bl_idname = "universalgta.debug_mapping_system"
    bl_label = "Debug Mapping System"
    bl_description = "Herramientas de debugging para el sistema de mapeos"
    bl_options = {'REGISTER'}
    
    debug_mode: EnumProperty(
        name="Debug Mode",
        items=[
            ('OVERVIEW', "Overview", "Vista general del sistema"),
            ('PROPERTIES', "Properties", "Debug de propiedades"),
            ('OPERATORS', "Operators", "Debug de operadores"),
            ('VALIDATION', "Validation", "Debug de validaciones"),
            ('PERFORMANCE', "Performance", "Análisis de rendimiento")
        ],
        default='OVERVIEW'
    )
    
    def execute(self, context):
        if self.debug_mode == 'OVERVIEW':
            self.debug_overview(context)
        elif self.debug_mode == 'PROPERTIES':
            self.debug_properties(context)
        elif self.debug_mode == 'OPERATORS':
            self.debug_operators(context)
        elif self.debug_mode == 'VALIDATION':
            self.debug_validation(context)
        elif self.debug_mode == 'PERFORMANCE':
            self.debug_performance(context)
        
        return {'FINISHED'}
    
    def debug_overview(self, context):
        """Debug general del sistema"""
        print("\n" + "="*50)
        print("BONE MAPPING SYSTEM DEBUG - OVERVIEW")
        print("="*50)
        
        settings = context.scene.universal_gta_settings
        
        print(f"✓ Settings object: {type(settings)}")
        print(f"✓ Source armature: {settings.source_armature}")
        print(f"✓ Target armature: {settings.target_armature}")
        print(f"✓ Total mappings: {len(settings.bone_mappings)}")
        
        # Verificar operadores disponibles
        available_ops = []
        test_ops = [
            'universalgta.quick_map_bones',
            'universalgta.batch_map_similar_names',
            'universalgta.mirror_mappings',
            'universalgta.update_mapping_visualization'
        ]
        
        for op in test_ops:
            try:
                if hasattr(bpy.ops, op.split('.')[0]):
                    available_ops.append(op)
            except:
                pass
        
        print(f"✓ Available enhanced operators: {len(available_ops)}")
        for op in available_ops:
            print(f"   • {op}")
    
    def debug_properties(self, context):
        """Debug de propiedades"""
        print("\n" + "="*50)
        print("BONE MAPPING SYSTEM DEBUG - PROPERTIES")
        print("="*50)
        
        settings = context.scene.universal_gta_settings
        
        # Listar todas las propiedades
        prop_names = [prop for prop in dir(settings) if not prop.startswith('_')]
        enhanced_props = [
            'source_bones_index', 'target_bones_index',
            'auto_update_visualization', 'show_mapping_confidence',
            'drag_active', 'highlighted_bone'
        ]
        
        print("📋 ALL PROPERTIES:")
        for prop in sorted(prop_names):
            try:
                value = getattr(settings, prop)
                is_enhanced = prop in enhanced_props
                marker = "🆕" if is_enhanced else "📝"
                print(f"   {marker} {prop}: {value}")
            except:
                print(f"   ❌ {prop}: <error accessing>")
    
    def debug_operators(self, context):
        """Debug de operadores"""
        print("\n" + "="*50)
        print("BONE MAPPING SYSTEM DEBUG - OPERATORS")  
        print("="*50)
        
        # Lista de operadores a verificar
        operators_to_check = [
            ('universalgta.quick_map_bones', 'Enhanced Quick Mapping'),
            ('universalgta.batch_map_similar_names', 'Batch Similar Names'),
            ('universalgta.mirror_mappings', 'Mirror Mappings'),
            ('universalgta.analyze_bone_hierarchy', 'Hierarchy Analysis'),
            ('universalgta.update_mapping_visualization', 'Visual Updates'),
            ('universalgta.create_mapping_preview', 'Mapping Preview'),
            ('universalgta.analyze_mapping_quality', 'Quality Analysis'),
            ('universalgta.generate_mapping_report', 'Report Generation')
        ]
        
        for op_id, description in operators_to_check:
            try:
                op_parts = op_id.split('.')
                if (hasattr(bpy.ops, op_parts[0]) and 
                    hasattr(getattr(bpy.ops, op_parts[0]), op_parts[1])):
                    print(f"   ✓ {description}: {op_id}")
                else:
                    print(f"   ❌ {description}: {op_id} (not found)")
            except Exception as e:
                print(f"   ❌ {description}: {op_id} (error: {e})")
    
    def debug_validation(self, context):
        """Debug de validaciones"""
        print("\n" + "="*50)
        print("BONE MAPPING SYSTEM DEBUG - VALIDATION")
        print("="*50)
        
        settings = context.scene.universal_gta_settings
        
        # Validar armatures
        if settings.source_armature:
            valid, msg = BoneMappingValidator.validate_armature_structure(settings.source_armature)
            print(f"   Source Armature: {'✓' if valid else '❌'} {msg}")
        else:
            print("   Source Armature: ❌ Not set")
        
        if settings.target_armature:
            valid, msg = BoneMappingValidator.validate_armature_structure(settings.target_armature)
            print(f"   Target Armature: {'✓' if valid else '❌'} {msg}")
        else:
            print("   Target Armature: ❌ Not set")
        
        # Validar mapeos
        if settings.bone_mappings:
            issues = BoneMappingValidator.validate_mapping_consistency(settings.bone_mappings)
            if issues:
                print("   Mapping Issues:")
                for issue in issues:
                    print(f"     ❌ {issue}")
            else:
                print("   ✓ No mapping consistency issues")
        else:
            print("   ❌ No mappings to validate")
    
    def debug_performance(self, context):
        """Debug de rendimiento"""
        print("\n" + "="*50)
        print("BONE MAPPING SYSTEM DEBUG - PERFORMANCE")
        print("="*50)
        
        settings = context.scene.universal_gta_settings
        
        if not settings.source_armature or not settings.target_armature:
            print("   ❌ Cannot test performance without both armatures")
            return
        
        # Test de rendimiento básico
        start_time = time.time()
        
        # Simular operaciones comunes
        source_bones = [bone.name for bone in settings.source_armature.pose.bones]
        target_bones = [bone.name for bone in settings.target_armature.pose.bones]
        
        bone_count_time = time.time()
        print(f"   ✓ Bone enumeration: {bone_count_time - start_time:.4f}s")
        print(f"     - Source bones: {len(source_bones)}")
        print(f"     - Target bones: {len(target_bones)}")
        
        # Test de similitud de nombres
        similarity_start = time.time()
        similarities = []
        for i, source in enumerate(source_bones[:10]):  # Limitar para test
            for target in target_bones[:10]:
                sim = self.calculate_test_similarity(source, target)
                similarities.append(sim)
        
        similarity_time = time.time()
        print(f"   ✓ Similarity calculation (100 pairs): {similarity_time - similarity_start:.4f}s")
        print(f"     - Average similarity: {sum(similarities)/len(similarities):.3f}")
        
        total_time = time.time() - start_time
        print(f"   ✓ Total test time: {total_time:.4f}s")
    
    def calculate_test_similarity(self, name1, name2):
        """Función simple de similitud para test de rendimiento"""
        n1 = name1.lower().replace("_", "").replace(" ", "")
        n2 = name2.lower().replace("_", "").replace(" ", "")
        
        if n1 == n2:
            return 1.0
        if n1 in n2 or n2 in n1:
            return 0.8
        
        common = set(n1) & set(n2)
        total = set(n1) | set(n2)
        return len(common) / len(total) if total else 0.0


# Lista de clases para registro
classes = [
    UNIVERSALGTA_OT_AnalyzeMappingQuality,
    UNIVERSALGTA_OT_GenerateMappingReport,
    UNIVERSALGTA_OT_DebugMappingSystem,
]


def register():
    """Registra todas las utilidades"""
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"[MAPPING_UTILS] Error registrando {cls.__name__}: {e}")


def unregister():
    """Desregistra todas las utilidades"""
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"[MAPPING_UTILS] Error desregistrando {cls.__name__}: {e}")


if __name__ == "__main__":
    register()