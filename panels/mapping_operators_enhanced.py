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
        # Drag & Drop: permite arrastrar el source_bone y soltar sobre target_bone
        op = layout.operator("universalgta.drop_bone_mapping", text="", icon='IMPORT', emboss=False)
        op.source_bone = item.source_bone
        op.target_bone = item.target_bone
        # ...resto del layout original...
        # (Puedes mantener el diseño visual actual debajo de este bloque)
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
    """Panel de mapeo de huesos con doble lista, drag & drop y selección"""
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

        # HEADER
        header = layout.box()
        header.label(text="🦴 Bone Mapping System (Enhanced)", icon='CONSTRAINT_BONE')

        # Doble lista: Source y Target
        row = layout.row(align=True)
        col_source = row.column(align=True)
        col_target = row.column(align=True)

        col_source.label(text="Source Bones", icon='ARMATURE_DATA')
        col_source.template_list(
            "UNIVERSALGTA_UL_SourceBonesList", "",
            settings, "source_bones_collection",
            settings, "source_bones_index",
            rows=10, maxrows=20
        )
        col_source.operator("universalgta.select_source_bone", text="Seleccionar en 3D").from_list = True
        col_source.operator("universalgta.sync_bone_lists", text="Actualizar lista fuente", icon='FILE_REFRESH')

        col_target.label(text="Target Bones", icon='BONE_DATA')
        col_target.template_list(
            "UNIVERSALGTA_UL_TargetBonesList", "",
            settings, "target_bones_collection",
            settings, "target_bones_index",
            rows=10, maxrows=20
        )
        col_target.operator("universalgta.select_target_bone", text="Seleccionar en 3D").from_list = True
        col_target.operator("universalgta.sync_bone_lists", text="Actualizar lista destino", icon='FILE_REFRESH')

        # Drag & Drop: instrucciones y botón demo
        layout.separator()
        drag_box = layout.box()
        drag_box.label(text="Arrastra un hueso fuente sobre uno destino para mapear", icon='MOUSE_LMB')
        drag_box.operator("universalgta.start_bone_drag", text="Demo Drag & Drop")
        # Aquí se podría implementar la lógica de arrastre real con eventos de UI personalizados

        # Feedback visual
        layout.operator("universalgta.update_mapping_visualization", text="Actualizar Visualización", icon='HIDE_OFF')

        # Lista de mapeos actual (compacta)
        layout.separator()
        layout.label(text="Bone Mappings", icon='OUTLINER_DATA_ARMATURE')
        layout.template_list(
            "UNIVERSALGTA_UL_ModernBoneMappingList", "",
            settings, "bone_mappings",
            settings, "bone_mappings_index",
            rows=8, maxrows=16
        )

        # Editor individual (igual que antes)
        if 0 <= settings.bone_mappings_index < len(settings.bone_mappings):
            item = settings.bone_mappings[settings.bone_mappings_index]
            edit_box = layout.box()
            edit_box.label(text=f"✏️ Edit: {item.target_bone or 'Unnamed'}", icon='TOOL_SETTINGS')
            status_row = edit_box.row(align=True)
            enable_col = status_row.column(align=True)
            enable_col.prop(item, "enabled", text="", toggle=True, icon='CHECKMARK' if item.enabled else 'CANCEL')
            info_col = status_row.column(align=True)
            info_col.label(text=f"Method: {item.detection_method}", icon='AUTO')
            if item.confidence > 0:
                info_col.label(text=f"Conf: {item.confidence:.2f}", icon='INFO')
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