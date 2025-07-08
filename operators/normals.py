# operators/normals.py - Versión mejorada
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
        
        # Buscar el mesh principal
        target_mesh = self._find_target_mesh(settings)
        
        if not target_mesh:
            self.report({'ERROR'}, "No se encontró ningún mesh para corregir normales")
            return {'CANCELLED'}
        
        try:
            # Corregir normales principales
            self._fix_mesh_normals(target_mesh)
            
            # Si está habilitado, crear duplicado con normales invertidas
            if settings.duplicate_inverted_normals:
                self._create_inverted_duplicate(target_mesh, settings)
            
            self.report({'INFO'}, f"Normales corregidas en {target_mesh.name}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error corrigiendo normales: {str(e)}")
            return {'CANCELLED'}
    
    def _find_target_mesh(self, settings):
        """Encuentra el mesh objetivo para corregir normales"""
        # Buscar por nombres esperados
        possible_names = ["Mesh", settings.skin_name, "MySkin"]
        
        for obj_name in possible_names:
            if obj_name in bpy.data.objects:
                obj = bpy.data.objects[obj_name]
                if obj.type == 'MESH':
                    return obj
        
        # Buscar cualquier mesh en la escena
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and len(obj.data.vertices) > 0:
                return obj
        
        return None
    
    def _fix_mesh_normals(self, target_mesh):
        """Corrige las normales de un mesh"""
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
    
    def _create_inverted_duplicate(self, original_mesh, settings):
        """Crea una copia duplicada con normales invertidas"""
        try:
            # Duplicar el mesh
            bpy.context.view_layer.objects.active = original_mesh
            bpy.ops.object.duplicate()
            
            duplicate_mesh = bpy.context.active_object
            duplicate_mesh.name = f"{original_mesh.name}_Inverted"
            duplicate_mesh.data.name = f"{original_mesh.data.name}_Inverted"
            
            # Mantener la misma transformación
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
            self._safe_mode_set('OBJECT')
            return {'CANCELLED'}
    
    def _safe_mode_set(self, mode):
        """Cambia de modo de forma segura"""
        try:
            bpy.ops.object.mode_set(mode=mode)
        except:
            pass


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
            result = self._analyze_normals(active_obj)
            
            # Mostrar resultado
            if result['consistency'] > 90:
                self.report({'INFO'}, 
                           f"Normales consistentes: {result['consistency']:.1f}% "
                           f"({result['outward_faces']}/{result['total_faces']} caras)")
            elif result['consistency'] > 70:
                self.report({'WARNING'}, 
                           f"Normales parcialmente consistentes: {result['consistency']:.1f}% "
                           f"({result['outward_faces']}/{result['total_faces']} caras)")
            else:
                self.report({'ERROR'}, 
                           f"Normales inconsistentes: {result['consistency']:.1f}% "
                           f"({result['outward_faces']}/{result['total_faces']} caras)")
            
            # Información adicional en consola
            self._print_detailed_analysis(active_obj.name, result)
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error verificando normales: {str(e)}")
            return {'CANCELLED'}
    
    def _analyze_normals(self, obj):
        """Analiza las normales del mesh"""
        # Crear bmesh para análisis
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.normal_update()
        
        # Variables para análisis
        total_faces = len(bm.faces)
        outward_faces = 0
        inward_faces = 0
        problematic_faces = []
        
        # Calcular el centro del objeto
        center = Vector((0, 0, 0))
        for vert in bm.verts:
            center += vert.co
        center /= len(bm.verts)
        
        # Analizar cada cara
        for face in bm.faces:
            # Vector desde el centro de la cara al centro del objeto
            face_center = face.calc_center_median()
            to_center = (center - face_center).normalized()
            
            # Producto punto con la normal
            dot_product = face.normal.dot(to_center)
            
            # Si el producto punto es negativo, la normal apunta hacia afuera
            if dot_product < -0.1:  # Umbral para evitar caras perpendiculares
                outward_faces += 1
            elif dot_product > 0.1:
                inward_faces += 1
                problematic_faces.append(face.index)
        
        bm.free()
        
        # Calcular consistencia
        consistency = (outward_faces / total_faces) * 100 if total_faces > 0 else 0
        
        return {
            'total_faces': total_faces,
            'outward_faces': outward_faces,
            'inward_faces': inward_faces,
            'consistency': consistency,
            'problematic_faces': problematic_faces[:10]  # Limitar a 10 para no saturar
        }
    
    def _print_detailed_analysis(self, obj_name, result):
        """Imprime análisis detallado en consola"""
        print(f"\n[NORMALS_CHECK] Análisis de {obj_name}:")
        print(f"  Total de caras: {result['total_faces']}")
        print(f"  Caras con normales hacia afuera: {result['outward_faces']}")
        print(f"  Caras con normales hacia adentro: {result['inward_faces']}")
        print(f"  Consistencia: {result['consistency']:.1f}%")
        
        if result['problematic_faces']:
            print(f"  Primeras caras problemáticas: {result['problematic_faces']}")


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