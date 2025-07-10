"""
Sistema de Feedback Visual 3D para Enhanced Bone Mapping
"""
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from mathutils import Vector


class VisualFeedbackManager:
    """Gestor central del sistema de feedback visual"""
    
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._lines = []
            cls._instance._highlights = []
        return cls._instance
    
    def __init__(self):
        pass  # Singleton, no reinit
    
    def clear_all_visuals(self):
        self.clear_connection_lines()
        self.clear_highlights()
    
    def clear_connection_lines(self):
        # Elimina objetos de línea creados
        for obj in self._lines:
            if obj and obj.name in bpy.data.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
        self._lines.clear()
    
    def clear_highlights(self):
        # Quita highlight de huesos
        for arm, bone_name in self._highlights:
            if arm and bone_name in arm.data.bones:
                arm.data.bones[bone_name].show_wire = False
        self._highlights.clear()
    
    def create_connection_line(self, start_pos, end_pos, mapping_info=None):
        # Crea una línea entre dos puntos en el 3D View
        import bpy, bmesh
        mesh = bpy.data.meshes.new("MappingLine")
        obj = bpy.data.objects.new("MappingLineObj", mesh)
        bpy.context.collection.objects.link(obj)
        bm = bmesh.new()
        v1 = bm.verts.new(start_pos)
        v2 = bm.verts.new(end_pos)
        bm.edges.new([v1, v2])
        bm.to_mesh(mesh)
        bm.free()
        obj.show_in_front = True
        obj.display_type = 'WIRE'
        self._lines.append(obj)
        return obj
    
    def get_connection_material(self, mapping_info=None):
        # Opcional: crear material para la línea
        return None
    
    def get_or_create_visualization_collection(self):
        # Opcional: usar una colección específica para las líneas
        return bpy.context.collection


class UNIVERSALGTA_OT_UpdateVisualizationSystem(Operator):
    """Actualiza todo el sistema de visualización"""
    bl_idname = "universalgta.update_visualization_system"
    bl_label = "Update Visualization System"
    bl_description = "Actualiza todas las visualizaciones del sistema de mapeo"
    bl_options = {'REGISTER'}
    
    clear_existing: BoolProperty(
        name="Clear Existing",
        description="Limpiar visualizaciones existentes",
        default=True
    )
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        vis = VisualFeedbackManager()
        if self.clear_existing:
            vis.clear_all_visuals()
        # Dibujar líneas para todos los mapeos activos
        if settings.source_armature and settings.target_armature:
            for m in settings.bone_mappings:
                if m.enabled and m.source_bone and m.target_bone:
                    start = self.get_bone_world_position(settings.source_armature, m.source_bone)
                    end = self.get_bone_world_position(settings.target_armature, m.target_bone)
                    if start and end:
                        vis.create_connection_line(start, end, mapping_info=m)
        self.report({'INFO'}, "Visualización actualizada")
        return {'FINISHED'}
    
    def get_bone_world_position(self, armature, bone_name):
        if armature and bone_name in armature.data.bones:
            bone = armature.data.bones[bone_name]
            return armature.matrix_world @ bone.head_local
        return None


class UNIVERSALGTA_OT_ClearAllVisualizations(Operator):
    """Limpia todas las visualizaciones"""
    bl_idname = "universalgta.clear_all_visualizations"
    bl_label = "Clear All Visualizations"
    bl_description = "Limpia todas las visualizaciones del sistema de mapeo"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        vis = VisualFeedbackManager()
        vis.clear_all_visuals()
        self.report({'INFO'}, "Visualizaciones eliminadas")
        return {'FINISHED'}


# Lista de clases para registro
classes = [
    UNIVERSALGTA_OT_UpdateVisualizationSystem,
    UNIVERSALGTA_OT_ClearAllVisualizations,
]


def register():
    for cls in classes:
        pass


def unregister():
    try:
        pass
    except:
        pass
    for cls in reversed(classes):
        pass
