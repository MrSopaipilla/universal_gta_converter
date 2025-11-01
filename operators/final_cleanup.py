"""Operador de limpieza final post-conversión."""
import bpy  # type: ignore
from bpy.types import Operator  # type: ignore
from bpy.props import BoolProperty  # type: ignore

class UNIVERSALGTA_OT_final_cleanup(Operator):
    """Limpieza final personalizada post-conversión"""
    bl_idname = "universalgta.final_cleanup"
    bl_label = "Final Cleanup"
    bl_description = "Ejecuta limpieza final personalizada después de la conversión"
    bl_options = {'REGISTER', 'UNDO'}
    
    clean_unnamed: BoolProperty(
        name="Clean Unnamed Objects",
        description="Eliminar objetos 'unnamed' y problemáticos",
        default=True
    )
    
    remove_vertex_colors: BoolProperty(
        name="Remove Vertex Colors",
        description="Eliminar colores de vértice del mesh",
        default=True
    )
    
    clean_empty_groups: BoolProperty(
        name="Clean Empty Vertex Groups",
        description="Eliminar grupos de vértices vacíos",
        default=True
    )
    
    optimize_mesh: BoolProperty(
        name="Optimize Mesh",
        description="Optimizar mesh eliminando elementos innecesarios",
        default=True
    )
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        cleaned_items = []
        
        print("Iniciando limpieza final")
        
        try:
            if self.clean_unnamed:
                unnamed_count = self.cleanup_unnamed_objects()
                if unnamed_count > 0:
                    cleaned_items.append(f"{unnamed_count} objetos unnamed")
            
            preserve_data = getattr(bpy.context.scene, 'universalgta_preserve_vertex_data', False)
            if not preserve_data and self.remove_vertex_colors and not settings.keep_vertex_colors:
                if self.cleanup_vertex_colors():
                    cleaned_items.append("colores de vértice")
            
            if self.clean_empty_groups:
                empty_groups = self.cleanup_empty_vertex_groups()
                if empty_groups > 0:
                    cleaned_items.append(f"{empty_groups} grupos vacíos")
            
            if self.optimize_mesh:
                if self.optimize_final_mesh():
                    cleaned_items.append("optimización de mesh")
            
            if cleaned_items:
                message = f"Limpieza completada: {', '.join(cleaned_items)}"
                self.report({'INFO'}, message)
            else:
                self.report({'INFO'}, "No se requirió limpieza adicional")
            
            return {'FINISHED'}
            
        except Exception as e:
            error_msg = f"Error en limpieza final: {e}"
            self.report({'ERROR'}, error_msg)
            return {'CANCELLED'}
    
    def cleanup_unnamed_objects(self):
        """Limpiar objetos unnamed y problemáticos"""
        problematic_names = ['unnamed', 'Unnamed', 'UNNAMED', 'temp', 'Temp', 'TEMP']
        cleaned_count = 0
        
        for obj in bpy.data.objects[:]:
            if any(problem in obj.name for problem in problematic_names):
                children = [child for child in bpy.data.objects if child.parent == obj]
                for child in children:
                    child.parent = None
                
                bpy.data.objects.remove(obj, do_unlink=True)
                cleaned_count += 1
        
        return cleaned_count
    
    def cleanup_vertex_colors(self):
        """Eliminar colores de vértice del mesh principal"""
        mesh_obj = bpy.data.objects.get("Mesh")
        if not mesh_obj or mesh_obj.type != 'MESH':
            return False
        
        mesh_data = mesh_obj.data
        removed_count = 0
        
        preserve_data = getattr(bpy.context.scene, 'universalgta_preserve_vertex_data', False)
        
        while mesh_data.vertex_colors and not preserve_data:
            mesh_data.vertex_colors.remove(mesh_data.vertex_colors[0])
            removed_count += 1
        
        if hasattr(mesh_data, 'color_attributes'):
            while mesh_data.color_attributes and not preserve_data:
                mesh_data.color_attributes.remove(mesh_data.color_attributes[0])
                removed_count += 1
        
        return removed_count > 0
    
    def cleanup_empty_vertex_groups(self):
        """Eliminar grupos de vértices vacíos"""
        mesh_obj = bpy.data.objects.get("Mesh")
        if not mesh_obj or mesh_obj.type != 'MESH':
            return 0
        
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        removed_count = len(mesh_obj.vertex_groups)
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.0)
        removed_count = removed_count - len(mesh_obj.vertex_groups)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return removed_count
    
    def optimize_final_mesh(self):
        """Optimizar mesh final"""
        mesh_obj = bpy.data.objects.get("Mesh")
        if not mesh_obj or mesh_obj.type != 'MESH':
            return False
        
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return True
    
    def invoke(self, context, event):
        """Mostrar diálogo de confirmación con opciones"""
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        """Dibujar opciones en el diálogo"""
        layout = self.layout
        
        layout.label(text="Opciones de Limpieza Final:")
        layout.prop(self, "clean_unnamed")
        
        preserve_data = getattr(bpy.context.scene, 'universalgta_preserve_vertex_data', False)
        if not preserve_data:
            layout.prop(self, "remove_vertex_colors")
        
        layout.prop(self, "clean_empty_groups")
        layout.prop(self, "optimize_mesh")

def register():
    bpy.utils.register_class(UNIVERSALGTA_OT_final_cleanup)

def unregister():
    bpy.utils.unregister_class(UNIVERSALGTA_OT_final_cleanup)
