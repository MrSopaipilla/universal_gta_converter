"""Operadores para materiales GTA SA."""

import bpy  # type: ignore
from bpy.types import Operator  # type: ignore
from bpy.props import BoolProperty  # type: ignore

# Color optimizado para GTA SA
DEFAULT_GTA_COLOR = (0.906, 0.906, 0.906, 1.0)  # #E7E7E7FF


class UNIVERSALGTA_OT_configure_materials_gta(Operator):
    """Configurar todos los materiales para GTA SA"""
    bl_idname = "universalgta.configure_materials_gta"
    bl_label = "Configure Materials for GTA SA"
    bl_description = "Configura materiales con color #E7E7E7FF, especularidad 0 y DragonFF"
    bl_options = {'REGISTER', 'UNDO'}
    
    force_default_color: BoolProperty(
        name="Apply GTA SA Color (#E7E7E7FF)",
        description="Aplicar color por defecto a materiales sin textura",
        default=True
    )
    
    force_specular_zero: BoolProperty(
        name="Force Specular = 0",
        description="Forzar especularidad a 0 (requerido para GTA SA)",
        default=True
    )
    
    configure_dragonff: BoolProperty(
        name="Configure DragonFF",
        description="Configurar DragonFF automaticamente si esta disponible",
        default=True
    )
    
    def execute(self, context):
        materials_processed = 0
        colors_applied = 0
        specular_configured = 0
        dragonff_configured = 0
        
        self.report({'INFO'}, "Configurando materiales para GTA SA...")
        
        # Verificar DragonFF
        dragonff_available = self.check_dragonff_addon()
        if dragonff_available:
            self.report({'INFO'}, "DragonFF detectado")
        
        # Procesar materiales
        for material in bpy.data.materials:
            try:
                materials_processed += 1
                
                # Configurar especularidad = 0
                if self.force_specular_zero:
                    if self.configure_specular_zero(material):
                        specular_configured += 1
                
                # Aplicar color GTA SA
                if self.force_default_color:
                    if self.apply_gta_color(material):
                        colors_applied += 1
                
                # Configurar DragonFF
                if self.configure_dragonff and dragonff_available:
                    if self.setup_dragonff_properties(material):
                        dragonff_configured += 1
                        
            except Exception as e:
                self.report({'WARNING'}, f"Error en {material.name}: {e}")
                continue
        
        # Reporte final
        message = f"{materials_processed} materiales procesados"
        if specular_configured > 0:
            message += f", {specular_configured} con especularidad=0"
        if colors_applied > 0:
            message += f", {colors_applied} con color #E7E7E7FF"
        if dragonff_configured > 0:
            message += f", {dragonff_configured} con DragonFF"
        
        self.report({'INFO'}, message)
        return {'FINISHED'}
    
    def configure_specular_zero(self, material):
        """Configurar especularidad = 0 para Blender 5.0/4.x"""
        try:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        # Blender 5.0
                        if 'Specular IOR' in node.inputs:
                            node.inputs['Specular IOR'].default_value = 1.0
                            return True
                        # Blender 4.x
                        elif 'Specular' in node.inputs:
                            node.inputs['Specular'].default_value = 0.0
                            return True
                        break
            else:
                if hasattr(material, 'specular_intensity'):
                    material.specular_intensity = 0.0
                    return True
            return False
        except Exception:
            return False
    
    def apply_gta_color(self, material):
        """Aplicar color #E7E7E7FF"""
        try:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        if 'Base Color' in node.inputs and not node.inputs['Base Color'].is_linked:
                            current_color = node.inputs['Base Color'].default_value
                            # Solo si es color por defecto de Blender
                            if all(abs(current_color[i] - 0.8) < 0.1 for i in range(3)):
                                node.inputs['Base Color'].default_value = DEFAULT_GTA_COLOR
                                return True
                        break
            else:
                material.diffuse_color = DEFAULT_GTA_COLOR
                return True
            return False
        except Exception:
            return False
    
    def setup_dragonff_properties(self, material):
        """Configurar DragonFF optimizado para GTA SA"""
        try:
            dragonff_props = {
                'dragonff_ambient_shading': 1.0,
                'dragonff_specular_material': False,
                'dragonff_export_material': True,
                'dragonff_surface_properties': 0,
                'dragonff_lighting_model': 0,
                'dragonff_alpha_test': False,
                'dragonff_two_sided': False,
                'dragonff_vertex_alpha': False,
                'dragonff_modulate_color': True,
            }
            
            props_set = 0
            for prop_name, prop_value in dragonff_props.items():
                try:
                    if hasattr(material, prop_name):
                        setattr(material, prop_name, prop_value)
                        props_set += 1
                    else:
                        material[prop_name] = prop_value
                        props_set += 1
                except Exception:
                    continue
            
            return props_set > 0
        except Exception:
            return False
    
    def check_dragonff_addon(self):
        """Verificar DragonFF"""
        try:
            variations = ['DragonFF', 'dragonff', 'dragon_ff', 'io_scene_dff']
            return any(name in bpy.context.preferences.addons.keys() for name in variations)
        except Exception:
            return False


class UNIVERSALGTA_OT_apply_gta_color_all(Operator):
    """Aplicar color #E7E7E7FF a todos los materiales"""
    bl_idname = "universalgta.apply_gta_color_all"
    bl_label = "Apply GTA SA Color"
    bl_description = "Aplica color #E7E7E7FF a materiales sin textura"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        materials_updated = 0
        
        for material in bpy.data.materials:
            try:
                if material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            if 'Base Color' in node.inputs and not node.inputs['Base Color'].is_linked:
                                node.inputs['Base Color'].default_value = DEFAULT_GTA_COLOR
                                materials_updated += 1
                            break
                else:
                    material.diffuse_color = DEFAULT_GTA_COLOR
                    materials_updated += 1
            except Exception:
                continue
        
        self.report({'INFO'}, f"Color #E7E7E7FF aplicado a {materials_updated} materiales")
        return {'FINISHED'}


class UNIVERSALGTA_OT_verify_materials_gta(Operator):
    """Verificar configuracion de materiales para GTA SA"""
    bl_idname = "universalgta.verify_materials_gta"
    bl_label = "Verify GTA SA Materials"
    bl_description = "Verifica configuracion de materiales para GTA SA"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        total_materials = len(bpy.data.materials)
        
        if total_materials == 0:
            self.report({'INFO'}, "No hay materiales en la escena")
            return {'FINISHED'}
        
        correctly_configured = 0
        specular_issues = 0
        
        for material in bpy.data.materials:
            material_ok = True
            
            # Verificar especularidad
            if not self.check_specular_zero(material):
                specular_issues += 1
                material_ok = False
            
            if material_ok:
                correctly_configured += 1
        
        # Reporte
        if correctly_configured == total_materials:
            message = f"Todos los {total_materials} materiales configurados para GTA SA"
            self.report({'INFO'}, message)
        else:
            message = f"{correctly_configured}/{total_materials} OK. {specular_issues} con especularidad incorrecta"
            self.report({'WARNING'}, message)
        
        return {'FINISHED'}
    
    def check_specular_zero(self, material):
        """Verificar especularidad = 0"""
        try:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        if 'Specular IOR' in node.inputs:
                            return node.inputs['Specular IOR'].default_value == 1.0
                        elif 'Specular' in node.inputs:
                            return node.inputs['Specular'].default_value == 0.0
                        break
            else:
                if hasattr(material, 'specular_intensity'):
                    return material.specular_intensity == 0.0
            return True
        except Exception:
            return False


# Clases para registrar
classes = [
    UNIVERSALGTA_OT_configure_materials_gta,
    UNIVERSALGTA_OT_apply_gta_color_all,
    UNIVERSALGTA_OT_verify_materials_gta,
]


def register():
    """Registrar operadores"""
    for cls in classes:
        bpy.utils.register_class(cls)
    print("[MATERIALS] Operadores registrados")


def unregister():
    """Desregistrar operadores"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)