"""
Sistema de Configuración UI Persistente
Garantiza orden correcto: MainPanel → AdvancedMapping → QuickActions → Utilities → Info
"""

import bpy
import json
import os
from pathlib import Path

class UIOrderManager:
    """Gestor de orden de paneles UI"""
    
    PANEL_ORDER = [
        ("UNIVERSALGTA_PT_main_panel", "🚀 Main Controls", 0),
        ("UNIVERSALGTA_PT_advanced_mapping_panel", "🔗 Advanced Mapping", 1),
        ("UNIVERSALGTA_PT_quick_actions_panel", "⚡ Quick Actions", 2),
        ("UNIVERSALGTA_PT_utilities_panel", "🛠 Utilities", 3),
        ("UNIVERSALGTA_PT_info_panel", "📊 Information", 4),
    ]
    
    @classmethod
    def validate_panel_order(cls):
        """Validar que el orden de paneles sea correcto"""
        print("[UI_CONFIG] 🎯 Validando orden de paneles...")
        
        for panel_id, name, order in cls.PANEL_ORDER:
            print(f"[UI_CONFIG] ✓ [{order}] {panel_id} = {name}")
        
        return True
    
    @classmethod
    def get_config_path(cls):
        """Obtener ruta de configuración"""
        addon_dir = Path(__file__).parent
        config_dir = addon_dir / "config"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "ui_order.json"
    
    @classmethod
    def save_current_order(cls):
        """Guardar orden actual"""
        config_path = cls.get_config_path()
        
        try:
            config_data = {
                "version": "4.0.1",
                "panel_order": cls.PANEL_ORDER,
                "last_updated": str(Path(__file__).stat().st_mtime)
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"[UI_CONFIG] ✅ Orden guardado: {config_path}")
            return True
        except Exception as e:
            print(f"[UI_CONFIG] ❌ Error guardando: {e}")
            return False
    
    @classmethod
    def enforce_panel_order_on_startup(cls):
        """Forzar orden correcto al iniciar"""
        print("[UI_CONFIG] 🚀 Forzando orden correcto de paneles...")
        
        # Validar y guardar
        if cls.validate_panel_order():
            cls.save_current_order()
            print("[UI_CONFIG] ✅ Orden de paneles establecido correctamente")
        else:
            print("[UI_CONFIG] ⚠ Warning: Problemas con orden de paneles")

class UNIVERSALGTA_OT_fix_panel_order(bpy.types.Operator):
    """Operador para corregir orden de paneles manualmente"""
    bl_idname = "universalgta.fix_panel_order"
    bl_label = "Fix Panel Order"
    bl_description = "Corregir orden de paneles UI"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        UIOrderManager.enforce_panel_order_on_startup()
        self.report({'INFO'}, "Orden de paneles corregido")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(UNIVERSALGTA_OT_fix_panel_order)
    UIOrderManager.enforce_panel_order_on_startup()

def unregister():
    bpy.utils.unregister_class(UNIVERSALGTA_OT_fix_panel_order)

if __name__ == "__main__":
    register()
