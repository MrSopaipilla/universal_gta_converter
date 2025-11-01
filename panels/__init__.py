"""Módulo de paneles para Universal GTA Converter."""

import bpy

# Importar paneles principales
try:
    from .main_panel import (
        UNIVERSALGTA_PT_MainPanel,           # bl_idname = "UNIVERSALGTA_PT_main_panel"
        UNIVERSALGTA_PT_AdvancedMappingPanel,# bl_idname = "UNIVERSALGTA_PT_advanced_mapping_panel"
        UNIVERSALGTA_PT_QuickActionsPanel,   # bl_idname = "UNIVERSALGTA_PT_quick_actions_panel"
        UNIVERSALGTA_PT_UtilitiesPanel,      # bl_idname = "UNIVERSALGTA_PT_utilities_panel"
        UNIVERSALGTA_PT_InfoPanel,           # bl_idname = "UNIVERSALGTA_PT_info_panel"
        UNIVERSALGTA_PT_NameAuthorPanel,     # bl_idname = "UNIVERSALGTA_PT_name_author_panel"
    )
    MAIN_PANELS_AVAILABLE = True
    print("[PANELS] ✅ Paneles principales importados")
except ImportError as e:
    print(f"[PANELS] ❌ Error importando main_panel.py: {e}")
    MAIN_PANELS_AVAILABLE = False

# Importar paneles de créditos
try:
    from .credits import (
        UNIVERSALGTA_OT_open_yoshi_channel,
        UNIVERSALGTA_PT_CreditsPanel,        # bl_idname = "UNIVERSALGTA_PT_credits_panel"
    )
    CREDITS_PANELS_AVAILABLE = True
    print("[PANELS] ✅ Paneles de créditos importados")
except ImportError as e:
    print(f"[PANELS] ⚠ credits.py no disponible: {e}")
    CREDITS_PANELS_AVAILABLE = False

# Lista de clases
available_classes = []

if MAIN_PANELS_AVAILABLE:
    available_classes.extend([
        UNIVERSALGTA_PT_MainPanel,
        UNIVERSALGTA_PT_AdvancedMappingPanel,
        UNIVERSALGTA_PT_QuickActionsPanel,
        UNIVERSALGTA_PT_UtilitiesPanel,
        UNIVERSALGTA_PT_InfoPanel,
        UNIVERSALGTA_PT_NameAuthorPanel,
    ])

if CREDITS_PANELS_AVAILABLE:
    available_classes.extend([
        UNIVERSALGTA_OT_open_yoshi_channel,
        UNIVERSALGTA_PT_CreditsPanel,
    ])

def register():
    """Registra todos los paneles"""
    print("[PANELS] 🚀 Iniciando registro de paneles...")
    print(f"[PANELS] Total paneles a registrar: {len(available_classes)}")
    
    registered_count = 0
    failed_count = 0
    
    for i, cls in enumerate(available_classes, 1):
        try:
            bpy.utils.register_class(cls)
            print(f"[PANELS] ✓ [{i:2d}/{len(available_classes)}] {cls.__name__}")
            registered_count += 1
        except Exception as e:
            print(f"[PANELS] ❌ [{i:2d}/{len(available_classes)}] {cls.__name__}: {e}")
            failed_count += 1
    
    print(f"[PANELS] ✅ Registro completado: {registered_count} registrados")
    if failed_count > 0:
        print(f"[PANELS] ⚠ {failed_count} errores de registro")
    
    if registered_count > 0:
        print("[PANELS] 🎯 Panel principal disponible como: UNIVERSALGTA_PT_main_panel")

def unregister():
    """Desregistra todos los paneles"""
    print("[PANELS] 🔄 Desregistrando paneles...")
    
    for cls in reversed(available_classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"[PANELS] ⚠ Error desregistrando {cls.__name__}: {e}")
    
    print("[PANELS] ✅ Desregistro completado")

if __name__ == "__main__":
    register()
