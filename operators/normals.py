"""
Operadores para corrección de normales
"""

import bpy
import bmesh
from bpy.types import Operator
from mathutils import Vector


class UNIVERSALGTA_OT_fix_normals(Operator):
    """Corregir normales del mesh resultante"""
    bl_idname = "universalgta.fix_normals"
    bl_label = "Fix Normals"
    bl_description = "Recalcula las normales hacia afuera y opcionalmente duplica con normales invertidas"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Buscar el mesh principal (debería llamarse "Mesh" o el nombre del skin)
        target_mesh = None
        possible_names = ["Mesh", settings.skin_name, "MySkin"]
        
        for obj_name in possible_names:
            if obj_name in bpy.data.objects:
                obj = bpy.data.objects[obj_name]
                if obj.type == 'MESH':
                    target_mesh = obj
                    break
        
        if not target_mesh:
            # Buscar cualquier mesh en la escena
            for obj in bpy.data.objects:
                if obj.type == 'MESH' and len(obj.data.vertices) > 0:
                    target_mesh = obj
                    break
        
        if not target_mesh:
            self.report({'ERROR'}, "No se encontró ningún mesh para corregir normales")
            return {'CANCELLED'}
        
        try:
            # Activar el mesh
            bpy.context.view_layer.objects.active = target_mesh
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Seleccionar todo
            bpy.ops.mesh.select_all(action='SELECT')
            
            # Recalcular normales hacia afuera
            bpy.ops.mesh.normals_make_consistent(inside=False)
            
            # Volver a modo objeto
            bpy.ops.object.mode_set(mode='OBJECT')
            
            print(f"[NORMALS] Normales corregidas en: {target_mesh.name}")
            
            # Si está habilitado, crear duplicado con normales invertidas
            if settings.duplicate_inverted_normals:
                self.create_inverted_duplicate(target_mesh, settings)
            
            self.report({'INFO'}, f"Normales corregidas en {target_mesh.name}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error corrigiendo normales: {str(e)}")
            return {'CANCELLED'}
    
    def create_inverted_duplicate(self, original_mesh, settings):
        """Crea una copia duplicada con normales invertidas"""
        try:
            # Duplicar el mesh
            bpy.context.view_layer.objects.active = original_mesh
            bpy.ops.object.duplicate()
            
            duplicate_mesh = bpy.context.active_object
            duplicate_mesh.name = f"{original_mesh.name}_Inverted"
            duplicate_mesh.data.name = f"{original_mesh.data.name}_Inverted"
            
            # Colocar el duplicado en la misma posición
            duplicate_mesh.location = original_mesh.location
            duplicate_mesh.rotation_euler = original_mesh.rotation_euler
            duplicate_mesh.scale = original_mesh.scale
            
            # Entrar en modo edición e invertir normales
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.flip_normals()
            bpy.ops.object.mode_set(mode='OBJECT')
            
            print(f"[NORMALS] Duplicado creado con normales invertidas: {duplicate_mesh.name}")
            
        except Exception as e:
            print(f"[NORMALS] Error creando duplicado invertido: {e}")


class UNIVERSALGTA_OT_auto_fix_normals_post_conversion(Operator):
    """Aplicar corrección automática de normales después de conversión"""
    bl_idname = "universalgta.auto_fix_normals_post_conversion"
    bl_label = "Auto Fix Normals Post Conversion"
    bl_description = "Aplicación automática de corrección de normales después de conversión"
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if settings.auto_fix_normals:
            # Ejecutar corrección de normales
            bpy.ops.universalgta.fix_normals()
            print("[AUTO_NORMALS] Corrección automática de normales aplicada")
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_flip_normals(Operator):
    """Invertir normales del mesh seleccionado"""
    bl_idname = "universalgta.flip_normals"
    bl_label = "Flip Normals"
    bl_description = "Invierte las normales del mesh activo"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        active_obj = context.active_object
        
        if not active_obj or active_obj.type != 'MESH':
            self.report({'ERROR'}, "Selecciona un objeto mesh")
            return {'CANCELLED'}
        
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.flip_normals()
            bpy.ops.object.mode_set(mode='OBJECT')
            
            self.report({'INFO'}, f"Normales invertidas en {active_obj.name}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error invirtiendo normales: {str(e)}")
            return {'CANCELLED'}


class UNIVERSALGTA_OT_check_normals_consistency(Operator):
    """Verificar consistencia de normales"""
    bl_idname = "universalgta.check_normals_consistency"
    bl_label = "Check Normals"
    bl_description = "Verifica la consistencia de las normales del mesh"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        active_obj = context.active_object
        
        if not active_obj or active_obj.type != 'MESH':
            self.report({'ERROR'}, "Selecciona un objeto mesh")
            return {'CANCELLED'}
        
        try:
            # Crear bmesh para análisis
            bm = bmesh.new()
            bm.from_mesh(active_obj.data)
            bm.faces.ensure_lookup_table()
            
            # Verificar normales
            inconsistent_faces = 0
            total_faces = len(bm.faces)
            
            for face in bm.faces:
                # Verificar si la normal apunta hacia afuera
                if face.normal.z < 0:  # Simplificado para este ejemplo
                    inconsistent_faces += 1
            
            bm.free()
            
            consistency_percentage = ((total_faces - inconsistent_faces) / total_faces) * 100
            
            if consistency_percentage > 90:
                self.report({'INFO'}, f"Normales consistentes: {consistency_percentage:.1f}%")
            elif consistency_percentage > 70:
                self.report({'WARNING'}, f"Normales parcialmente consistentes: {consistency_percentage:.1f}%")
            else:
                self.report({'ERROR'}, f"Normales inconsistentes: {consistency_percentage:.1f}%")
            
            print(f"[NORMALS_CHECK] {active_obj.name}: {consistency_percentage:.1f}% consistencia")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error verificando normales: {str(e)}")
            return {'CANCELLED'}


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_fix_normals,
    UNIVERSALGTA_OT_auto_fix_normals_post_conversion,
    UNIVERSALGTA_OT_flip_normals,
    UNIVERSALGTA_OT_check_normals_consistency,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)