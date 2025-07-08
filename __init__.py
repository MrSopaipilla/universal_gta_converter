bl_info = {
    "name": "Universal to GTA SA Converter",
    "author": "YoshiMaincra + GPT + Claude",
    "version": (3, 2, 3),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Universal GTA",
    "description": "Convierte armatures personalizados a GTA SA con detección inteligente de huesos, corrección de normales, animaciones predefinidas, soporte para Shape Keys y herramientas avanzadas. In-Dev",
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

# Importar operadores de pose (incluyendo los nuevos)
try:
    from .operators.pose import (
        UNIVERSALGTA_OT_apply_custom_pose,
        UNIVERSALGTA_OT_test_pose_application,
        UNIVERSALGTA_OT_verify_pose_setup
    )
    POSE_OPERATORS_AVAILABLE = True
    print("[ADDON] ✓ Operadores de pose cargados exitosamente")
except ImportError as e:
    from .operators.pose import UNIVERSALGTA_OT_apply_custom_pose
    POSE_OPERATORS_AVAILABLE = False
    print(f"[ADDON] ⚠ Operadores de pose básicos cargados (faltan operadores de prueba): {e}")

# Importar operadores de mapeo
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

# Importar operadores de animaciones
from .operators.animations import (
    UNIVERSALGTA_OT_load_animation,
    UNIVERSALGTA_OT_clear_animations,
    UNIVERSALGTA_OT_refresh_animations_on_spacing_change,
    UNIVERSALGTA_OT_apply_facial_expressiveness,
    UNIVERSALGTA_OT_create_animation_files
)

# Importar operadores de exportación y espaciado
from .operators.export import UNIVERSALGTA_OT_export_textures
from .operators.spacing import UNIVERSALGTA_OT_apply_spacing

# Importar operadores de referencia GTA SA
from .operators.gta_reference import (
    UNIVERSALGTA_OT_show_gta_bone_reference,
    UNIVERSALGTA_OT_create_gta_armature_template
)

# Importar paneles principales (solo los que existen)
from .panels.main_panel import (
    UNIVERSALGTA_PT_MainPanel,
    UNIVERSALGTA_PT_BoneMappingPanel,
    UNIVERSALGTA_PT_AdvancedPanel,
    UNIVERSALGTA_PT_UtilitiesPanel,
    UNIVERSALGTA_PT_AnimationsPanel,
    UNIVERSALGTA_PT_StatusPanel
)

# Importar paneles de créditos
from .panels.credits import (
    UNIVERSALGTA_OT_open_yoshi_channel,
    UNIVERSALGTA_PT_CreditsPanel,
    UNIVERSALGTA_PT_TestingPanel,
    UNIVERSALGTA_PT_NamingPanel
)

# Importar operadores de Shape Keys (con manejo de errores)
try:
    from .operators.shape_keys import (
        UNIVERSALGTA_OT_apply_all_shape_keys,
        UNIVERSALGTA_OT_backup_shape_keys,
        UNIVERSALGTA_OT_restore_shape_keys_backup,
        UNIVERSALGTA_OT_list_shape_keys
    )
    SHAPE_KEYS_AVAILABLE = True
    print("[ADDON] ✓ Operadores de Shape Keys cargados exitosamente")
except ImportError as e:
    print(f"[ADDON] ⚠ Advertencia: No se pudieron cargar operadores de Shape Keys: {e}")
    SHAPE_KEYS_AVAILABLE = False


# Panel de Shape Keys (definido aquí para evitar problemas de importación)
class UNIVERSALGTA_PT_ShapeKeysPanel(bpy.types.Panel):
    """Panel dedicado para Shape Keys"""
    bl_label = "Shape Keys Manager"
    bl_idname = "UNIVERSALGTA_PT_shape_keys_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        # Solo mostrar si los operadores de Shape Keys están disponibles
        return SHAPE_KEYS_AVAILABLE

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        if not SHAPE_KEYS_AVAILABLE:
            layout.label(text="Shape Keys no disponibles", icon='ERROR')
            return
        
        # Información sobre Shape Keys
        info_box = layout.box()
        info_box.label(text="Shape Keys Detection", icon='SHAPEKEY_DATA')
        
        # Verificar si hay shape keys en los meshes
        shape_keys_info = self._get_shape_keys_info(settings.source_armature)
        
        if shape_keys_info['total_meshes_with_keys'] > 0:
            info_col = info_box.column()
            info_col.label(text=f"✓ {shape_keys_info['total_meshes_with_keys']} meshes con shape keys")
            info_col.label(text=f"✓ {shape_keys_info['total_shape_keys']} shape keys totales")
            
            # Lista de meshes con shape keys
            for mesh_name, keys in shape_keys_info['meshes_details'].items():
                key_col = info_box.column()
                key_col.scale_y = 0.8
                key_col.label(text=f"• {mesh_name}: {len(keys)} keys")
        else:
            info_box.label(text="No se detectaron shape keys", icon='INFO')
        
        layout.separator()
        
        # Herramientas principales de Shape Keys
        tools_box = layout.box()
        tools_box.label(text="Shape Keys Tools", icon='TOOL_SETTINGS')
        
        # Primera fila - herramientas de información
        row1 = tools_box.row()
        row1.operator("universalgta.list_shape_keys", text="List Keys", icon='OUTLINER_DATA_MESH')
        if SHAPE_KEYS_AVAILABLE:
            row1.operator("universalgta.backup_shape_keys", text="Backup", icon='FILE_BACKUP')
        
        # Segunda fila - aplicación de shape keys
        row2 = tools_box.row()
        row2.scale_y = 1.2
        if SHAPE_KEYS_AVAILABLE:
            row2.operator("universalgta.apply_all_shape_keys", text="Apply All Shape Keys", icon='SHAPEKEY_DATA')
        
        # Configuración de aplicación
        layout.separator()
        config_box = layout.box()
        config_box.label(text="Application Settings", icon='PREFERENCES')
        
        col = config_box.column()
        col.label(text="✓ Apply ALL Shape Keys (including Basis)")
        col.label(text="✓ Auto Apply during Conversion: ON")
        col.label(text="✓ Remove Shape Keys after apply: ON")
        
        # Advertencias importantes
        layout.separator()
        warning_box = layout.box()
        warning_box.alert = True
        warning_box.label(text="⚠️ IMPORTANTE:", icon='ERROR')
        
        warning_col = warning_box.column()
        warning_col.scale_y = 0.8
        warning_col.label(text="• Las shape keys se aplican automáticamente")
        warning_col.label(text="  durante la conversión a GTA SA")
        warning_col.label(text="• TODAS las shape keys se eliminan")
        warning_col.label(text="• No se pueden deshacer después")
    
    def _get_shape_keys_info(self, source_armature):
        """Obtiene información sobre las shape keys disponibles"""
        info = {
            'total_meshes_with_keys': 0,
            'total_shape_keys': 0,
            'meshes_details': {}
        }
        
        if not source_armature:
            return info
        
        # Buscar meshes con shape keys
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                obj.parent == source_armature and 
                obj.data.shape_keys and 
                len(obj.data.shape_keys.key_blocks) > 0):
                
                shape_keys = [key.name for key in obj.data.shape_keys.key_blocks]
                info['meshes_details'][obj.name] = shape_keys
                info['total_meshes_with_keys'] += 1
                info['total_shape_keys'] += len(shape_keys)
        
        return info


class UNIVERSALGTA_UL_BoneMappingList(bpy.types.UIList):
    """Lista UI para mapeos de huesos con drag & drop funcional y visual mejorado"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        """Dibuja cada elemento de la lista con estilo visual mejorado"""
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            
            # Checkbox para habilitar/deshabilitar
            checkbox_col = row.column()
            checkbox_col.scale_x = 0.8
            checkbox_col.prop(item, "enabled", text="")
            
            # Icono de hueso para source
            bone_col = row.column()
            bone_col.scale_x = 0.6
            bone_col.label(text="", icon='BONE_DATA')
            
            # Source bone
            source_col = row.column()
            source_col.scale_x = 2.0
            src_arm = data.source_armature
            
            if src_arm and src_arm.type == 'ARMATURE' and item.source_bone:
                icon_type = 'CHECKMARK' if item.source_bone in [b.name for b in src_arm.pose.bones] else 'ERROR'
                source_col.label(text=item.source_bone, icon=icon_type)
            else:
                source_col.label(text=item.source_bone or "<None>", icon='DOT')
            
            # Flecha direccional
            arrow_col = row.column()
            arrow_col.scale_x = 0.8
            arrow_col.label(text="→", icon='FORWARD')
            
            # Target bone
            target_col = row.column()
            target_col.scale_x = 2.0
            tgt_arm = data.target_armature
            
            if tgt_arm and tgt_arm.type == 'ARMATURE' and item.target_bone:
                icon_type = 'CHECKMARK' if item.target_bone in [b.name for b in tgt_arm.pose.bones] else 'ERROR'
                target_col.label(text=item.target_bone, icon=icon_type)
            else:
                target_col.label(text=item.target_bone or "<None>", icon='DOT')
            
            # Indicadores de estado
            status_col = row.column()
            status_col.scale_x = 1.2
            
            # Método de detección
            status_col.label(text="", icon='AUTO' if item.detection_method == "Auto" else 'HAND')
            
            # Confianza (solo para automáticos)
            if item.detection_method == "Auto" and item.confidence > 0:
                conf_col = row.column()
                conf_col.scale_x = 0.8
                
                if item.confidence > 0.7:
                    icon_type = 'CHECKMARK'
                elif item.confidence < 0.4:
                    icon_type = 'ERROR'
                else:
                    icon_type = 'DOT'
                
                conf_col.label(text=f"{item.confidence:.1f}", icon=icon_type)
        
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.scale_y = 0.8
            layout.label(text="", icon='CHECKMARK' if item.enabled else 'X')
    
    def draw_filter(self, context, layout):
        """Filtros para la lista"""
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
        
        flt_flags = []
        flt_neworder = []
        
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(
                self.filter_name, self.bitflag_filter_item, items, "target_bone",
                reverse=self.use_filter_invert
            )
        
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(items)
        
        if self.use_filter_sort_alpha:
            flt_neworder = helper_funcs.sort_items_by_name(items, "target_bone")
            if self.use_filter_sort_reverse:
                flt_neworder.reverse()
        
        return flt_flags, flt_neworder


# Lista de todas las clases para registrar
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
    
    # Operadores de pose básicos
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
    
    # Operadores de animaciones
    UNIVERSALGTA_OT_load_animation,
    UNIVERSALGTA_OT_clear_animations,
    UNIVERSALGTA_OT_refresh_animations_on_spacing_change,
    UNIVERSALGTA_OT_apply_facial_expressiveness,
    UNIVERSALGTA_OT_create_animation_files,
    
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
    
    # Operadores de referencia GTA SA
    UNIVERSALGTA_OT_show_gta_bone_reference,
    UNIVERSALGTA_OT_create_gta_armature_template,
    
    # Paneles principales
    UNIVERSALGTA_PT_MainPanel,
    UNIVERSALGTA_PT_ShapeKeysPanel,  # Definido en este archivo
    UNIVERSALGTA_PT_BoneMappingPanel,
    UNIVERSALGTA_PT_AdvancedPanel,
    UNIVERSALGTA_PT_UtilitiesPanel,
    UNIVERSALGTA_PT_AnimationsPanel,
    UNIVERSALGTA_PT_StatusPanel,
    
    # Paneles adicionales y créditos
    UNIVERSALGTA_OT_open_yoshi_channel,
    UNIVERSALGTA_PT_CreditsPanel,
    UNIVERSALGTA_PT_TestingPanel,
    UNIVERSALGTA_PT_NamingPanel,
]

# Agregar operadores de Shape Keys si están disponibles
if SHAPE_KEYS_AVAILABLE:
    classes.extend([
        UNIVERSALGTA_OT_apply_all_shape_keys,
        UNIVERSALGTA_OT_backup_shape_keys,
        UNIVERSALGTA_OT_restore_shape_keys_backup,
        UNIVERSALGTA_OT_list_shape_keys,
    ])

# Agregar operadores de pose adicionales si están disponibles
if POSE_OPERATORS_AVAILABLE:
    classes.extend([
        UNIVERSALGTA_OT_test_pose_application,
        UNIVERSALGTA_OT_verify_pose_setup,
    ])

# Variable global para el converter
converter_instance = None


def register():
    """Registra todas las clases del addon"""
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"[ERROR] No se pudo registrar la clase {cls.__name__}: {e}")
    
    # Registrar la propiedad principal en la escena
    bpy.types.Scene.universal_gta_settings = PointerProperty(type=UniversalGTASettings)
    
    # Registrar validadores de nombres
    register_validation()
    
    print("[ADDON] Universal GTA Converter v3.2.3 In-Dev registrado exitosamente")
    print("[ADDON] Nuevas características:")
    print("[ADDON] • Nomenclatura exacta de GTA SA (con espacios)")
    print("[ADDON] • Pelvis incluido correctamente")
    print("[ADDON] • Herramientas de referencia GTA SA")
    print("[ADDON] • Template creator con nombres exactos")
    print("[ADDON] • Corrección automática de normales")
    print("[ADDON] • Sistema de nombres personalizados")
    print("[ADDON] • Animaciones predefinidas desde .blend")
    print("[ADDON] • Expresividad facial avanzada")
    if SHAPE_KEYS_AVAILABLE:
        print("[ADDON] • ✓ Soporte completo para Shape Keys")
        print("[ADDON] • ✓ Eliminación automática de todas las Shape Keys")
        print("[ADDON] • ✓ Aplicación automática durante conversión")
    else:
        print("[ADDON] • ⚠ Shape Keys no disponibles (falta operators/shape_keys.py)")
    
    if POSE_OPERATORS_AVAILABLE:
        print("[ADDON] • ✓ Operadores de pose avanzados disponibles")
    else:
        print("[ADDON] • ⚠ Solo operadores de pose básicos disponibles")
    
    print("[ADDON] • Panel de testing completo")
    print("[ADDON] • Panel de créditos con enlaces")


def unregister():
    """Desregistra todas las clases del addon"""
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"[ERROR] No se pudo desregistrar la clase {cls.__name__}: {e}")
    
    # Eliminar la propiedad de la escena
    if hasattr(bpy.types.Scene, 'universal_gta_settings'):
        del bpy.types.Scene.universal_gta_settings
    
    print("[ADDON] Universal GTA Converter v3.2.3 In-Dev desregistrado exitosamente")


if __name__ == "__main__":
    register()