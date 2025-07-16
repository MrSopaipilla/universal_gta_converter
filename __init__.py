bl_info = {
    "name": "Universal to GTA SA Converter (LEGACY)",
    "author": "YoshiMaincra + GPT + Claude",
    "version": (0, 0, 6),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Tool > Universal GTA",
    "description": "Convierte armatures personalizados a GTA SA con detección inteligente de huesos, sistema de animaciones mejorado, corrección de normales y herramientas avanzadas.",
    "category": "Rigging",
}

import bpy
from bpy.props import PointerProperty

# Importar configuración mejorada
from .config import UniversalGTASettings, BoneMappingItem, register_validation

# Importar el conversor principal
from .converter import UniversalGTAConverter

# Importar poses externas
from . import external_pose_caller

# Importar operadores de conversión
from .operators.conversion import (
    UNIVERSALGTA_OT_execute_conversion,
    UNIVERSALGTA_OT_preview_conversion,
    UNIVERSALGTA_OT_test_bone_mappings,
    UNIVERSALGTA_OT_clear_test_constraints,
    UNIVERSALGTA_OT_auto_detect_bones,
    UNIVERSALGTA_OT_validate_conversion
)

# Importar operadores de pose
from .operators.pose import UNIVERSALGTA_OT_apply_custom_pose

# Importar operadores de mapeo ACTUALIZADOS
from .operators.mapping import (
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
    UNIVERSALGTA_OT_enable_high_confidence
)

# Importar operadores de limpieza
from .operators.cleanup import (
    UNIVERSALGTA_OT_clean_model,
    UNIVERSALGTA_OT_purge_unused_data,
    UNIVERSALGTA_OT_purge_scene,
    UNIVERSALGTA_OT_clean_armatures,
    UNIVERSALGTA_OT_clean_empty_vertex_groups,
    UNIVERSALGTA_OT_fix_modifiers,
    UNIVERSALGTA_OT_remove_duplicates,
    UNIVERSALGTA_OT_optimize_mesh
)

# Importar operadores de normales
from .operators.normals import (
    UNIVERSALGTA_OT_fix_normals,
    UNIVERSALGTA_OT_auto_fix_normals_post_conversion,
    UNIVERSALGTA_OT_flip_normals,
    UNIVERSALGTA_OT_check_normals_consistency
)

# Importar operadores de nombres
from .operators.naming import (
    UNIVERSALGTA_OT_apply_custom_names,
    UNIVERSALGTA_OT_reset_names,
    UNIVERSALGTA_OT_validate_names,
    UNIVERSALGTA_OT_auto_generate_names
)

# SISTEMA DE ANIMACIONES MEJORADO
from .operators.animations import (
    UNIVERSALGTA_OT_load_animation,
    UNIVERSALGTA_OT_preview_animation,
    UNIVERSALGTA_OT_batch_load_animations,
    UNIVERSALGTA_OT_create_animation_files,
    UNIVERSALGTA_OT_clear_animations,
    UNIVERSALGTA_OT_apply_facial_expressiveness,
    UNIVERSALGTA_OT_refresh_animations_on_spacing_change
)

# Importar operadores de exportación y espaciado
from .operators.export import UNIVERSALGTA_OT_export_textures
from .operators.spacing import UNIVERSALGTA_OT_apply_spacing

# Importar paneles principales - SIN BONE MAPPING
from .panels.main_panel import (
    UNIVERSALGTA_PT_MainPanel,
    UNIVERSALGTA_PT_ConversionPanel,
    UNIVERSALGTA_PT_UtilitiesPanel
)

# PANEL DE ANIMACIONES
from .panels.animations_panel import UNIVERSALGTA_PT_AnimationsPanel

# Importar paneles adicionales
from .panels.credits import (
    UNIVERSALGTA_OT_open_yoshi_channel,
    UNIVERSALGTA_PT_CreditsPanel,
    UNIVERSALGTA_PT_TestingPanel,
    UNIVERSALGTA_PT_NamingPanel
)

# UIList mejorada con drag & drop FUNCIONAL y visual como la imagen original
class UNIVERSALGTA_UL_BoneMappingList(bpy.types.UIList):
    """Lista UI para mapeos de huesos con drag & drop funcional y visual mejorado"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        """Dibuja cada elemento de la lista con estilo visual mejorado"""
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Crear layout principal con estilo compacto
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            
            # Checkbox para habilitar/deshabilitar (más prominente)
            checkbox_col = row.column()
            checkbox_col.scale_x = 0.8
            checkbox_col.prop(item, "enabled", text="")
            
            # Icono de hueso para source
            bone_col = row.column()
            bone_col.scale_x = 0.6
            bone_col.label(text="", icon='BONE_DATA')
            
            # Source bone (más ancho)
            source_col = row.column()
            source_col.scale_x = 2.0
            src_arm = data.source_armature
            if src_arm and src_arm.type == 'ARMATURE' and item.source_bone:
                # Mostrar nombre del hueso con validación visual
                if item.source_bone in [b.name for b in src_arm.pose.bones]:
                    source_col.label(text=item.source_bone, icon='CHECKMARK')
                else:
                    source_col.label(text=item.source_bone, icon='ERROR')
            else:
                source_col.label(text=item.source_bone if item.source_bone else "<None>", icon='DOT')
            
            # Flecha direccional (visual llamativa)
            arrow_col = row.column()
            arrow_col.scale_x = 0.8
            arrow_col.label(text="→", icon='FORWARD')
            
            # Target bone (más ancho)
            target_col = row.column()
            target_col.scale_x = 2.0
            tgt_arm = data.target_armature
            if tgt_arm and tgt_arm.type == 'ARMATURE' and item.target_bone:
                # Mostrar nombre del hueso con validación visual
                if item.target_bone in [b.name for b in tgt_arm.pose.bones]:
                    target_col.label(text=item.target_bone, icon='CHECKMARK')
                else:
                    target_col.label(text=item.target_bone, icon='ERROR')
            else:
                target_col.label(text=item.target_bone if item.target_bone else "<None>", icon='DOT')
            
            # Indicadores de estado
            status_col = row.column()
            status_col.scale_x = 1.2
            
            # Método de detección
            if item.detection_method == "Auto":
                status_col.label(text="", icon='AUTO')
            else:
                status_col.label(text="", icon='HAND')
            
            # Confianza (solo para automáticos)
            if item.detection_method == "Auto" and item.confidence > 0:
                conf_col = row.column()
                conf_col.scale_x = 0.8
                if item.confidence > 0.7:
                    conf_col.label(text=f"{item.confidence:.1f}", icon='CHECKMARK')
                elif item.confidence < 0.4:
                    conf_col.label(text=f"{item.confidence:.1f}", icon='ERROR')
                else:
                    conf_col.label(text=f"{item.confidence:.1f}", icon='DOT')
        
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.scale_y = 0.8
            if item.enabled:
                layout.label(text="", icon='CHECKMARK')
            else:
                layout.label(text="", icon='X')
    
    def draw_filter(self, context, layout):
        """Filtros para la lista (mejora la funcionalidad)"""
        row = layout.row()
        
        # Filtro por nombre
        subrow = row.row(align=True)
        subrow.prop(self, "filter_name", text="")
        subrow.prop(self, "use_filter_invert", text="", icon='ARROW_LEFTRIGHT')
        
        # Ordenamiento
        subrow = row.row(align=True)
        subrow.prop(self, "use_filter_sort_alpha", text="", icon='SORTBYEXT')
        subrow.prop(self, "use_filter_sort_reverse", text="", icon='SORT_ASC')
    
    def filter_items(self, context, data, propname):
        """Filtrado personalizado de elementos"""
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        
        # Filtrado por nombre
        flt_flags = []
        flt_neworder = []
        
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(
                self.filter_name, self.bitflag_filter_item, items, "target_bone",
                reverse=self.use_filter_invert
            )
        
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(items)
        
        # Ordenamiento alfabético si está habilitado
        if self.use_filter_sort_alpha:
            flt_neworder = helper_funcs.sort_items_by_name(items, "target_bone")
            if self.use_filter_sort_reverse:
                flt_neworder.reverse()
        
        return flt_flags, flt_neworder

# Lista de todas las clases para registrar (SIN bone mapping panel por ahora)
classes = [
    # Configuración
    BoneMappingItem,
    UniversalGTASettings,
    
    # UI
    UNIVERSALGTA_UL_BoneMappingList,
    
    # Operadores de conversión
    UNIVERSALGTA_OT_execute_conversion,
    UNIVERSALGTA_OT_preview_conversion,
    UNIVERSALGTA_OT_test_bone_mappings,
    UNIVERSALGTA_OT_clear_test_constraints,
    UNIVERSALGTA_OT_auto_detect_bones,
    UNIVERSALGTA_OT_validate_conversion,
    
    # Operadores de pose
    UNIVERSALGTA_OT_apply_custom_pose,
    
    # Operadores de mapeo
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
    
    # Operadores de normales
    UNIVERSALGTA_OT_fix_normals,
    UNIVERSALGTA_OT_auto_fix_normals_post_conversion,
    UNIVERSALGTA_OT_flip_normals,
    UNIVERSALGTA_OT_check_normals_consistency,
    
    # Operadores de nombres
    UNIVERSALGTA_OT_apply_custom_names,
    UNIVERSALGTA_OT_reset_names,
    UNIVERSALGTA_OT_validate_names,
    UNIVERSALGTA_OT_auto_generate_names,
    
    # SISTEMA DE ANIMACIONES MEJORADO
    UNIVERSALGTA_OT_load_animation,
    UNIVERSALGTA_OT_preview_animation,
    UNIVERSALGTA_OT_batch_load_animations,
    UNIVERSALGTA_OT_create_animation_files,
    UNIVERSALGTA_OT_clear_animations,
    UNIVERSALGTA_OT_apply_facial_expressiveness,
    UNIVERSALGTA_OT_refresh_animations_on_spacing_change,
    
    # Operadores de limpieza
    UNIVERSALGTA_OT_clean_model,
    UNIVERSALGTA_OT_purge_unused_data,
    UNIVERSALGTA_OT_purge_scene,
    UNIVERSALGTA_OT_clean_armatures,
    UNIVERSALGTA_OT_clean_empty_vertex_groups,
    UNIVERSALGTA_OT_fix_modifiers,
    UNIVERSALGTA_OT_remove_duplicates,
    UNIVERSALGTA_OT_optimize_mesh,
    
    # Operadores de exportación y espaciado
    UNIVERSALGTA_OT_export_textures,
    UNIVERSALGTA_OT_apply_spacing,
    
    # Paneles principales
    UNIVERSALGTA_PT_MainPanel,
    UNIVERSALGTA_PT_ConversionPanel,
    UNIVERSALGTA_PT_UtilitiesPanel,
    
    # PANEL DE ANIMACIONES
    UNIVERSALGTA_PT_AnimationsPanel,
    
    # Paneles adicionales y créditos
    UNIVERSALGTA_OT_open_yoshi_channel,
    UNIVERSALGTA_PT_CreditsPanel,
    UNIVERSALGTA_PT_TestingPanel,
    UNIVERSALGTA_PT_NamingPanel,
]

# Variable global para el converter
converter_instance = None

def register():
    """Registra todas las clases del addon"""
    print("[ADDON] Iniciando registro de Universal GTA Converter...")
    
    # Registrar todas las clases principales
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"[ERROR] No se pudo registrar {cls.__name__}: {e}")
    
    # Intentar importar y registrar el panel de bone mapping DESDE EL ARCHIVO CORRECTO
    try:
        from .panels.bone_mapping_panel import (
            UNIVERSALGTA_PT_BoneMappingPanel,
            UNIVERSALGTA_OT_auto_map_by_name,
            UNIVERSALGTA_OT_clear_unmapped
        )
        
        # Registrar clases del bone mapping
        bpy.utils.register_class(UNIVERSALGTA_PT_BoneMappingPanel)
        bpy.utils.register_class(UNIVERSALGTA_OT_auto_map_by_name)
        bpy.utils.register_class(UNIVERSALGTA_OT_clear_unmapped)
        print("[ADDON] ✅ Panel de Bone Mapping registrado exitosamente")
        
    except ImportError as e:
        print(f"[WARNING] ⚠️  No se pudo importar bone_mapping_panel: {e}")
        print("[INFO] 📋 Para habilitar bone mapping avanzado:")
        print("[INFO] 1. Verificar que existe: panels/bone_mapping_panel.py")
        print("[INFO] 2. Verificar que las clases estén correctamente definidas")
        print("[INFO] 3. Reiniciar Blender")
    except Exception as e:
        print(f"[ERROR] ❌ Error registrando bone mapping panel: {e}")
    
    # Registrar la propiedad principal en la escena
    bpy.types.Scene.universal_gta_settings = PointerProperty(type=UniversalGTASettings)
    
    # Registrar validadores de nombres
    try:
        register_validation()
        print("[CONFIG] Validadores de nombres registrados")
    except Exception as e:
        print(f"[ERROR] Error registrando validadores: {e}")
    
    print("[ADDON] ==========================================")
    print("[ADDON] Universal GTA Converter v3.2.6 REGISTRADO")
    print("[ADDON] ==========================================")
    print("[ADDON] Características disponibles:")
    print("[ADDON] • 🎯 Panel principal en Tool tab")
    print("[ADDON] • 🎬 Animaciones: Fat_Walk, Muscle_Walk, Talk, Facial")
    print("[ADDON] • 📁 Carga de animaciones por lotes")
    print("[ADDON] • 🎭 Preview de animaciones en tiempo real")
    print("[ADDON] • 🎨 Conversión de colores RVA a texturas")
    print("[ADDON] • 🔧 Corrección automática de normales")
    print("[ADDON] • 📝 Sistema de nombres personalizados")
    print("[ADDON] • 🎪 Expresividad facial avanzada")
    print("[ADDON] • 🧪 Panel de testing completo")
    print("[ADDON] • 📞 Panel de créditos con enlaces")
    print("[ADDON] ==========================================")
    print("[ADDON] Ubicación: View3D > Sidebar > Tool > Universal GTA")
    print("[ADDON] ==========================================")

def unregister():
    """Desregistra todas las clases del addon"""
    print("[ADDON] Desregistrando Universal GTA Converter...")
    
    # Intentar desregistrar el panel de bone mapping si existe
    try:
        from .panels.bone_mapping_panel import (
            UNIVERSALGTA_PT_BoneMappingPanel,
            UNIVERSALGTA_OT_auto_map_by_name,
            UNIVERSALGTA_OT_clear_unmapped
        )
        
        bpy.utils.unregister_class(UNIVERSALGTA_OT_clear_unmapped)
        bpy.utils.unregister_class(UNIVERSALGTA_OT_auto_map_by_name)
        bpy.utils.unregister_class(UNIVERSALGTA_PT_BoneMappingPanel)
        print("[ADDON] Panel de Bone Mapping desregistrado")
    except:
        pass  # No pasa nada si no existe
    
    # Desregistrar clases principales en orden inverso
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"[ERROR] No se pudo desregistrar {cls.__name__}: {e}")
    
    # Eliminar la propiedad de la escena
    if hasattr(bpy.types.Scene, 'universal_gta_settings'):
        del bpy.types.Scene.universal_gta_settings
    
    print("[ADDON] Universal GTA Converter desregistrado exitosamente")

if __name__ == "__main__":
    register()