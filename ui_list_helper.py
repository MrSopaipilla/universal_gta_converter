"""
UI List Helper - Auto-generado por Master Updater
Lista UI para configuración de layout de paneles
"""

import bpy
from bpy.types import UIList

class UNIVERSALGTA_UL_UILayoutList(UIList):
    """Lista UI para configuración de layout de paneles"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        """Dibujar cada elemento de la lista de layout UI"""
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            
            # Checkbox de habilitado
            checkbox_col = row.column()
            checkbox_col.scale_x = 0.8
            checkbox_col.prop(item, "enabled", text="")
            
            # Icono y nombre del panel
            name_col = row.column()
            name_col.scale_x = 3.0
            if item.enabled:
                name_col.label(text=item.display_name, icon='PANEL_HLT' if not item.collapsed else 'RIGHTARROW')
            else:
                name_col.label(text=item.display_name, icon='X')
            
            # Orden
            order_col = row.column()
            order_col.scale_x = 0.8
            order_col.label(text=f"#{item.order}")
            
            # Estado colapsado
            collapse_col = row.column()
            collapse_col.scale_x = 0.8
            collapse_col.prop(item, "collapsed", text="", icon='TRIA_DOWN' if not item.collapsed else 'TRIA_RIGHT')
        
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.scale_y = 0.8
            if item.enabled:
                layout.label(text=f"#{item.order}")
            else:
                layout.label(text="X")

def register():
    bpy.utils.register_class(UNIVERSALGTA_UL_UILayoutList)

def unregister():
    bpy.utils.unregister_class(UNIVERSALGTA_UL_UILayoutList)
