"""
Panel de mapeo de huesos mejorado con diseño moderno y funcionalidad de guardado/carga
Basado en el estilo visual de la imagen de referencia
"""

import bpy
import json
import os
from bpy.types import Panel, Operator, UIList
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper


class UNIVERSALGTA_UL_ModernBoneMappingList(UIList):
    """Lista UI moderna para mapeos de huesos con diseño estilizado"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Contenedor principal con estilo moderno
            main_row = layout.row(align=True)
            main_row.scale_y = 1.1
            
            # Checkbox estilizado con color
            if item.enabled:
                checkbox_row = main_row.row(align=True)
                checkbox_row.alert = False
                checkbox_row.prop(item, "enabled", text="", emboss=True, 
                                icon='CHECKMARK', icon_only=True)
                checkbox_row.enabled = True
            else:
                checkbox_row = main_row.row(align=True)
                checkbox_row.alert = True
                checkbox_row.prop(item, "enabled", text="", emboss=True, 
                                icon='CANCEL', icon_only=True)
            
            # Separador visual
            main_row.separator(factor=0.5)
            
            # Información del mapeo con iconos
            content_row = main_row.row(align=True)
            content_row.scale_x = 1.0
            
            if item.source_bone and item.target_bone:
                # Mapeo completo - verde
                source_col = content_row.column(align=True)
                source_col.scale_x = 0.8
                source_col.label(text=item.source_bone, icon='BONE_DATA')
                
                # Flecha de mapeo
                arrow_col = content_row.column(align=True)
                arrow_col.scale_x = 0.3
                arrow_col.label(text="→", icon='FORWARD')
                
                target_col = content_row.column(align=True)
                target_col.scale_x = 0.8
                target_col.label(text=item.target_bone, icon='ARMATURE_DATA')
                
            elif item.target_bone:
                # Solo target - amarillo/advertencia
                content_row.alert = True
                empty_col = content_row.column(align=True)
                empty_col.scale_x = 0.8
                empty_col.label(text="❌ Sin origen", icon='ERROR')
                
                arrow_col = content_row.column(align=True)
                arrow_col.scale_x = 0.3
                arrow_col.label(text="→")
                
                target_col = content_row.column(align=True)
                target_col.scale_x = 0.8
                target_col.label(text=item.target_bone, icon='ARMATURE_DATA')
            else:
                # Mapeo vacío - rojo
                content_row.alert = True
                content_row.label(text="❌ Mapeo incompleto", icon='ERROR')
            
            # Indicador de confianza estilizado
            if item.detection_method == "Auto" and item.confidence > 0:
                conf_row = main_row.row(align=True)
                conf_row.scale_x = 0.4
                
                if item.confidence >= 0.8:
                    conf_row.label(text=f"{item.confidence:.1f}", icon='CHECKMARK')
                elif item.confidence >= 0.5:
                    conf_row.alert = True
                    conf_row.label(text=f"{item.confidence:.1f}", icon='QUESTION')
                else:
                    conf_row.alert = True
                    conf_row.label(text=f"{item.confidence:.1f}", icon='ERROR')
        
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            if item.enabled:
                layout.label(text="", icon='CHECKMARK')
            else:
                layout.label(text="", icon='CANCEL')


class UNIVERSALGTA_OT_save_bone_mapping(Operator, ExportHelper):
    """Guardar mapeo de huesos a archivo JSON"""
    bl_idname = "universalgta.save_bone_mapping"
    bl_label = "Guardar Mapping"
    bl_description = "Guarda el mapeo actual de huesos en un archivo JSON"
    bl_options = {'REGISTER'}
    
    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Crear datos del mapeo
        mapping_data = {
            "version": "3.2.3",
            "addon": "Universal GTA SA Converter",
            "source_armature": settings.source_armature.name if settings.source_armature else "",
            "target_armature": settings.target_armature.name if settings.target_armature else "",
            "mappings": []
        }
        
        # Exportar todos los mapeos
        for item in settings.bone_mappings:
            mapping_data["mappings"].append({
                "source_bone": item.source_bone,
                "target_bone": item.target_bone,
                "enabled": item.enabled,
                "detection_method": item.detection_method,
                "confidence": item.confidence
            })
        
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(mapping_data, f, indent=2, ensure_ascii=False)
            
            self.report({'INFO'}, f"Mapeo guardado: {os.path.basename(self.filepath)}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error guardando: {str(e)}")
            return {'CANCELLED'}


class UNIVERSALGTA_OT_load_bone_mapping(Operator, ImportHelper):
    """Cargar mapeo de huesos desde archivo JSON"""
    bl_idname = "universalgta.load_bone_mapping"
    bl_label = "Cargar Mapping"
    bl_description = "Carga un mapeo de huesos desde archivo JSON"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
            
            # Validar formato
            if "mappings" not in mapping_data:
                self.report({'ERROR'}, "Archivo JSON no válido")
                return {'CANCELLED'}
            
            # Limpiar mapeos existentes
            while len(settings.bone_mappings) > 0:
                settings.bone_mappings.remove(0)
            
            # Cargar mapeos
            loaded_count = 0
            for mapping in mapping_data["mappings"]:
                item = settings.bone_mappings.add()
                item.source_bone = mapping.get("source_bone", "")
                item.target_bone = mapping.get("target_bone", "")
                item.enabled = mapping.get("enabled", True)
                item.detection_method = mapping.get("detection_method", "Manual")
                item.confidence = mapping.get("confidence", 0.0)
                loaded_count += 1
            
            settings.bone_mappings_index = 0
            
            self.report({'INFO'}, f"Cargados {loaded_count} mapeos desde {os.path.basename(self.filepath)}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error cargando: {str(e)}")
            return {'CANCELLED'}


class UNIVERSALGTA_PT_ModernBoneMappingPanel(Panel):
    """Panel de mapeo de huesos con diseño moderno mejorado"""
    bl_label = "Bone Mapping - Enhanced"
    bl_idname = "UNIVERSALGTA_PT_modern_bone_mapping_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Universal GTA"
    bl_parent_id = "UNIVERSALGTA_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # === HEADER MODERNO ===
        header_box = layout.box()
        header_row = header_box.row(align=True)
        header_row.scale_y = 1.3
        header_row.label(text="🦴 Bone Mapping System", icon='CONSTRAINT_BONE')
        
        # Estadísticas en tiempo real
        enabled_count = sum(1 for m in settings.bone_mappings if m.enabled)
        total_count = len(settings.bone_mappings)
        
        stats_row = header_box.row(align=True)
        stats_row.scale_y = 0.9
        if enabled_count > 0:
            stats_row.label(text=f"✓ {enabled_count}/{total_count} Active", icon='CHECKMARK')
            
            # Verificar Pelvis
            pelvis_mapped = any(m.enabled and m.target_bone == 'Pelvis' for m in settings.bone_mappings)
            if pelvis_mapped:
                stats_row.label(text="• Pelvis ✓", icon='BONE_DATA')
            else:
                stats_row.alert = True
                stats_row.label(text="• Pelvis ✗", icon='ERROR')
        else:
            stats_row.alert = True
            stats_row.label(text="No mappings configured", icon='ERROR')
        
        layout.separator()
        
        # === CONTROLES PRINCIPALES ESTILIZADOS ===
        controls_box = layout.box()
        controls_box.label(text="Quick Actions", icon='SETTINGS')
        
        # Primera fila - acciones principales
        main_row = controls_box.row(align=True)
        main_row.scale_y = 1.4
        
        auto_btn = main_row.row(align=True)
        auto_btn.operator("universalgta.auto_detect_mappings", 
                         text="🔍 Auto Detect", icon='AUTO')
        
        validate_btn = main_row.row(align=True)
        validate_btn.operator("universalgta.validate_mappings", 
                             text="✓ Validate", icon='CHECKMARK')
        
        # Segunda fila - gestión de mapeos
        mgmt_row = controls_box.row(align=True)
        mgmt_row.scale_y = 1.2
        
        add_btn = mgmt_row.row(align=True)
        add_btn.operator("universalgta.add_target_bones", 
                        text="📋 Add All", icon='BONE_DATA')
        
        clear_btn = mgmt_row.row(align=True)
        clear_btn.alert = True
        clear_btn.operator("universalgta.clear_mappings", 
                          text="🗑 Clear", icon='TRASH')
        
        layout.separator()
        
        # === SISTEMA DE GUARDADO/CARGA MODERNO ===
        save_load_box = layout.box()
        save_load_box.label(text="💾 Save & Load System", icon='FILE')
        
        file_row = save_load_box.row(align=True)
        file_row.scale_y = 1.3
        
        save_btn = file_row.row(align=True)
        save_btn.operator("universalgta.save_bone_mapping", 
                         text="💾 Save Mapping", icon='FILE_TICK')
        
        load_btn = file_row.row(align=True)
        load_btn.operator("universalgta.load_bone_mapping", 
                         text="📂 Load Mapping", icon='FILE_FOLDER')
        
        # Información del sistema
        info_row = save_load_box.row()
        info_row.scale_y = 0.8
        info_row.label(text="Exports/Imports JSON format", icon='INFO')
        
        layout.separator()
        
        # === LISTA DE MAPEOS MEJORADA ===
        if len(settings.bone_mappings) > 0:
            mappings_box = layout.box()
            
            # Header de la lista con controles de selección masiva
            list_header = mappings_box.row(align=True)
            list_header.label(text=f"📋 Bone Mappings ({enabled_count}/{total_count})", 
                            icon='OUTLINER_DATA_ARMATURE')
            
            # Controles de selección masiva estilizados
            bulk_row = mappings_box.row(align=True)
            bulk_row.scale_y = 0.9
            
            enable_all = bulk_row.row(align=True)
            enable_all.operator("universalgta.enable_all_mappings", 
                               text="✓ All", icon='CHECKMARK')
            
            disable_all = bulk_row.row(align=True)
            disable_all.operator("universalgta.disable_all_mappings", 
                                text="✗ None", icon='CANCEL')
            
            high_conf = bulk_row.row(align=True)
            high_conf.operator("universalgta.enable_high_confidence", 
                              text="🎯 High Conf", icon='FILTER')
            
            # Lista principal con diseño moderno
            list_container = mappings_box.column()
            list_row = list_container.row()
            
            # Template list mejorada
            list_col = list_row.column()
            list_col.template_list(
                "UNIVERSALGTA_UL_ModernBoneMappingList",
                "",
                settings,
                "bone_mappings",
                settings,
                "bone_mappings_index",
                rows=5,
                maxrows=10
            )
            
            # Controles laterales estilizados
            controls_col = list_row.column(align=True)
            controls_col.scale_x = 0.7
            controls_col.scale_y = 1.1
            
            # Botones de movimiento con iconos modernos
            move_up = controls_col.row()
            move_up.operator("universalgta.move_mapping_up", text="", icon='TRIA_UP')
            
            move_down = controls_col.row()
            move_down.operator("universalgta.move_mapping_down", text="", icon='TRIA_DOWN')
            
            controls_col.separator()
            
            # Botones de gestión
            add_custom = controls_col.row()
            add_custom.operator("universalgta.add_custom_entry", text="", icon='ADD')
            
            remove_btn = controls_col.row()
            remove_btn.alert = True
            remove_btn.operator("universalgta.remove_mapping_entry", text="", icon='REMOVE')
            
            layout.separator()
            
            # === EDITOR DE MAPEO INDIVIDUAL MEJORADO ===
            if 0 <= settings.bone_mappings_index < len(settings.bone_mappings):
                item = settings.bone_mappings[settings.bone_mappings_index]
                
                edit_box = mappings_box.box()
                
                # Header del editor
                edit_header = edit_box.row(align=True)
                edit_header.scale_y = 1.2
                edit_header.label(text=f"✏️ Edit: {item.target_bone or 'Unnamed'}", 
                                icon='TOOL_SETTINGS')
                
                # Estado y método
                status_row = edit_box.row(align=True)
                
                # Checkbox grande estilizado
                enable_col = status_row.column(align=True)
                enable_col.scale_x = 0.3
                enable_col.scale_y = 1.3
                enable_col.prop(item, "enabled", text="", toggle=True, 
                              icon='CHECKMARK' if item.enabled else 'CANCEL')
                
                # Información del método
                info_col = status_row.column(align=True)
                method_row = info_col.row(align=True)
                method_row.scale_y = 0.9
                method_row.label(text=f"Method: {item.detection_method}", icon='AUTO')
                
                if item.confidence > 0:
                    conf_row = info_col.row(align=True)
                    conf_row.scale_y = 0.9
                    if item.confidence >= 0.8:
                        conf_row.label(text=f"Confidence: {item.confidence:.2f}", icon='CHECKMARK')
                    elif item.confidence >= 0.5:
                        conf_row.alert = True
                        conf_row.label(text=f"Confidence: {item.confidence:.2f}", icon='QUESTION')
                    else:
                        conf_row.alert = True
                        conf_row.label(text=f"Confidence: {item.confidence:.2f}", icon='ERROR')
                
                # Editor de huesos mejorado
                bones_box = edit_box.box()
                bones_box.label(text="Bone Assignment", icon='BONE_DATA')
                
                # Source bone con search estilizado
                source_row = bones_box.row(align=True)
                source_row.label(text="From:", icon='EXPORT')
                
                if settings.source_armature and settings.source_armature.type == 'ARMATURE':
                    source_search = source_row.row(align=True)
                    source_search.scale_x = 1.2
                    source_search.prop_search(item, "source_bone", 
                                           settings.source_armature.pose, "bones", text="")
                else:
                    source_input = source_row.row(align=True)
                    source_input.scale_x = 1.2
                    source_input.prop(item, "source_bone", text="")
                
                # Target bone con search estilizado
                target_row = bones_box.row(align=True)
                target_row.label(text="To:", icon='IMPORT')
                
                if settings.target_armature and settings.target_armature.type == 'ARMATURE':
                    target_search = target_row.row(align=True)
                    target_search.scale_x = 1.2
                    target_search.prop_search(item, "target_bone", 
                                           settings.target_armature.pose, "bones", text="")
                else:
                    target_input = target_row.row(align=True)
                    target_input.scale_x = 1.2
                    target_input.prop(item, "target_bone", text="")
                
                # Acciones adicionales
                actions_row = edit_box.row(align=True)
                actions_row.scale_y = 1.1
                
                duplicate_btn = actions_row.row(align=True)
                duplicate_btn.operator("universalgta.duplicate_mapping", 
                                      text="📋 Duplicate", icon='DUPLICATE')
                
                invert_btn = actions_row.row(align=True)
                invert_btn.operator("universalgta.invert_mapping", 
                                  text="🔄 Invert", icon='ARROW_LEFTRIGHT')
        
        else:
            # Mensaje de estado vacío mejorado
            empty_box = layout.box()
            empty_col = empty_box.column(align=True)
            empty_col.scale_y = 1.2
            
            empty_col.label(text="📭 No mappings configured", icon='INFO')
            
            steps_col = empty_box.column(align=True)
            steps_col.scale_y = 0.9
            steps_col.label(text="1. Set Source & Target armatures")
            steps_col.label(text="2. Click '🔍 Auto Detect'")
            steps_col.label(text="3. Validate and adjust mappings")
            
            # Botón de inicio rápido
            quick_start = empty_box.row()
            quick_start.scale_y = 1.4
            quick_start.operator("universalgta.auto_detect_mappings", 
                                text="🚀 Quick Start", icon='PLAY')


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_UL_ModernBoneMappingList,
    UNIVERSALGTA_OT_save_bone_mapping,
    UNIVERSALGTA_OT_load_bone_mapping,
    UNIVERSALGTA_PT_ModernBoneMappingPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)