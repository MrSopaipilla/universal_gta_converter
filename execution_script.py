#!/usr/bin/env python3
"""
SCRIPT EJECUTOR PRINCIPAL
Ejecuta las actualizaciones del Master Updater Script
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Ejecutar actualizaciones del addon"""
    
    print("🚀 UNIVERSAL GTA CONVERTER - ACTUALIZADOR PRINCIPAL")
    print("=" * 60)
    
    # Ruta del addon
    addon_path = r"C:\Users\Alumnos\AppData\Roaming\Blender Foundation\Blender\5.0\scripts\addons\yoshimaincra_universal_gta_converter_legacy"
    
    print(f"📁 Ruta del addon: {addon_path}")
    
    if not os.path.exists(addon_path):
        print(f"❌ ERROR: No se encuentra el addon en: {addon_path}")
        return
    
    print("\n🔧 EJECUTANDO ACTUALIZACIONES...")
    
    # Importar y ejecutar el master updater
    try:
        # Agregar la ruta del addon al path para importar módulos
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Ejecutar actualizaciones
        from master_updater_script import MasterUpdater
        
        updater = MasterUpdater(addon_path)
        updater.run_all_updates()
        
        # Crear UI List Helper
        create_ui_list_helper(addon_path)
        
        print("\n✅ TODAS LAS ACTUALIZACIONES COMPLETADAS")
        
    except Exception as e:
        print(f"❌ ERROR EJECUTANDO ACTUALIZACIONES: {e}")
        import traceback
        traceback.print_exc()

def create_ui_list_helper(addon_path):
    """Crear archivo UI List Helper"""
    print("\n📝 Creando UI List Helper...")
    
    ui_list_content = '''"""
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
'''
    
    ui_list_path = Path(addon_path) / "ui_list_helper.py"
    with open(ui_list_path, 'w', encoding='utf-8') as f:
        f.write(ui_list_content)
    
    print(f"✅ UI List Helper creado: {ui_list_path.name}")

if __name__ == "__main__":
    main()
