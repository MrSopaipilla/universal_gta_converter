"""
Validador de Registro de Clases - Universal GTA Converter
Detecta problemas comunes de registro en Blender 5.0
"""

import bpy

class RegistrationValidator:
    """Validador de registro de clases"""
    
    EXPECTED_CLASSES = [
        # Paneles principales (ORDEN CRÍTICO)
        "UNIVERSALGTA_PT_MainPanel",
        "UNIVERSALGTA_PT_AdvancedMappingPanel", 
        "UNIVERSALGTA_PT_QuickActionsPanel",
        "UNIVERSALGTA_PT_UtilitiesPanel",
        "UNIVERSALGTA_PT_InfoPanel",
        
        # Paneles secundarios
        "UNIVERSALGTA_PT_CreditsPanel",
        "UNIVERSALGTA_PT_TestingPanel", 
        "UNIVERSALGTA_PT_NamingPanel",
        
        # Operadores principales
        "UNIVERSALGTA_OT_execute_conversion",
        "UNIVERSALGTA_OT_complete_gta_conversion",
        "UNIVERSALGTA_OT_smart_auto_detect",
    ]
    
    PANEL_HIERARCHY = {
        "UNIVERSALGTA_PT_CreditsPanel": "UNIVERSALGTA_PT_main_panel",
        "UNIVERSALGTA_PT_TestingPanel": "UNIVERSALGTA_PT_main_panel", 
        "UNIVERSALGTA_PT_NamingPanel": "UNIVERSALGTA_PT_main_panel",
    }
    
    @classmethod
    def validate_registration(cls, classes_to_register):
        """Validar lista de clases antes del registro"""
        print("
[VALIDATOR] 🔍 Iniciando validación de registro...")
        
        issues_found = []
        
        # 1. Verificar que MainPanel esté primero
        main_panel_found = False
        main_panel_index = -1
        
        for i, cls in enumerate(classes_to_register):
            if hasattr(cls, '__name__') and 'MainPanel' in cls.__name__:
                main_panel_found = True
                main_panel_index = i
                break
        
        if not main_panel_found:
            issues_found.append("❌ CRÍTICO: MainPanel no encontrado")
        elif main_panel_index > 0:
            issues_found.append(f"⚠ WARNING: MainPanel en posición {main_panel_index}, debería ser 0")
        else:
            print("[VALIDATOR] ✅ MainPanel en posición correcta (0)")
        
        # 2. Verificar jerarquía de paneles
        registered_panel_ids = set()
        
        for cls in classes_to_register:
            if hasattr(cls, 'bl_idname') and 'PT_' in cls.bl_idname:
                registered_panel_ids.add(cls.bl_idname)
        
        for child_class, parent_id in cls.PANEL_HIERARCHY.items():
            if parent_id not in registered_panel_ids:
                issues_found.append(f"❌ CRÍTICO: {child_class} busca parent '{parent_id}' no registrado")
        
        # 3. Mostrar resultados
        if issues_found:
            print("[VALIDATOR] ❌ PROBLEMAS ENCONTRADOS:")
            for issue in issues_found:
                print(f"[VALIDATOR] {issue}")
            return False
        else:
            print("[VALIDATOR] ✅ Validación exitosa - no se encontraron problemas")
            return True
    
    @classmethod
    def debug_registration_error(cls, failed_class, error_msg):
        """Debug específico para errores de registro"""
        print(f"
[DEBUG] 🐛 Error registrando {failed_class.__name__}:")
        print(f"[DEBUG] Error: {error_msg}")
        
        if hasattr(failed_class, 'bl_parent_id'):
            parent_id = failed_class.bl_parent_id
            print(f"[DEBUG] Busca parent: '{parent_id}'")
            
            # Verificar si el parent existe
            if parent_id in cls.PANEL_HIERARCHY.values():
                print(f"[DEBUG] ✅ Parent '{parent_id}' es válido")
            else:
                print(f"[DEBUG] ❌ Parent '{parent_id}' no existe o nombre incorrecto")
                print(f"[DEBUG] 💡 Parents válidos: {list(cls.PANEL_HIERARCHY.values())}")
        
        if hasattr(failed_class, 'bl_idname'):
            print(f"[DEBUG] bl_idname: '{failed_class.bl_idname}'")
        
        print("[DEBUG] 🔧 Posibles soluciones:")
        print("[DEBUG] 1. Verificar que MainPanel se registre primero")
        print("[DEBUG] 2. Verificar bl_parent_id sea exacto")
        print("[DEBUG] 3. Verificar bl_idname sea único")

def register():
    print("[VALIDATOR] 🚀 Validador de registro cargado")

def unregister():
    print("[VALIDATOR] 🔄 Validador de registro descargado")

if __name__ == "__main__":
    register()
