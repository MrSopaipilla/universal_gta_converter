# operators/pose.py - Versión CORREGIDA
import bpy
from bpy.types import Operator
from .. import external_pose_caller


class UNIVERSALGTA_OT_apply_custom_pose(Operator):
    """Aplicar pose personalizada usando el script externo"""
    bl_idname = "universalgta.apply_custom_pose"
    bl_label = "Apply Custom Pose"
    bl_description = "Aplica pose personalizada usando el script externo"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        try:
            # Usar el aplicador de poses externo
            applier = external_pose_caller.ExternalPoseApplier()
            success = applier.execute_full_pose_application(
                source_armature=settings.source_armature,
                target_armature=settings.target_armature
            )
            
            if success:
                self.report({'INFO'}, "Pose personalizada aplicada con éxito")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Error al aplicar pose personalizada")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}


class UNIVERSALGTA_OT_test_pose_application(Operator):
    """Probar aplicación de pose personalizada con shape keys"""
    bl_idname = "universalgta.test_pose_application"
    bl_label = "Test Pose Application"
    bl_description = "Prueba la aplicación de pose personalizada procesando shape keys y aplicando modificadores"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("\n" + "="*60)
        print("PRUEBA DE APLICACIÓN DE POSE PERSONALIZADA CON SHAPE KEYS")
        print("="*60)
        
        try:
            # Verificar setup
            print("[TEST] Verificando setup post-conversión...")
            external_pose_caller.verify_post_conversion_setup()
            
            # Buscar armature principal
            main_armature = external_pose_caller._find_main_armature_post_conversion()
            
            if not main_armature:
                self.report({'ERROR'}, "No se encontró armature principal")
                return {'CANCELLED'}
            
            print(f"[TEST] ✓ Armature principal: {main_armature.name}")
            
            # Buscar meshes con modificadores
            meshes = external_pose_caller._find_meshes_with_armature_modifier(main_armature)
            
            if not meshes:
                self.report({'WARNING'}, "No hay meshes con modificadores armature")
                return {'CANCELLED'}
            
            print(f"[TEST] ✓ {len(meshes)} meshes con modificadores encontrados")
            
            # Verificar shape keys en los meshes
            shape_keys_count = 0
            for mesh in meshes:
                if mesh.data.shape_keys and len(mesh.data.shape_keys.key_blocks) > 0:
                    keys_count = len(mesh.data.shape_keys.key_blocks)
                    shape_keys_count += keys_count
                    print(f"[TEST] {mesh.name} tiene {keys_count} shape keys")
            
            if shape_keys_count > 0:
                print(f"[TEST] ⚠ TOTAL: {shape_keys_count} shape keys serán aplicadas y eliminadas")
            else:
                print("[TEST] ℹ No hay shape keys para procesar")
            
            # Verificar si hay pose para aplicar
            applier = external_pose_caller.ExternalPoseApplier()
            has_pose = applier._armature_has_pose_transforms(main_armature)
            
            if not has_pose:
                self.report({'INFO'}, "No hay transformaciones de pose para aplicar")
                print("[TEST] ℹ No hay pose para aplicar, pero se procesarán shape keys")
            else:
                print("[TEST] ✓ Pose detectada, se aplicará después de procesar shape keys")
            
            # Confirmar con el usuario
            print("[TEST] 🚀 Iniciando aplicación de pose...")
            
            # Aplicar pose (esto procesará shape keys y aplicará modificadores)
            success = external_pose_caller.apply_manual_pose_to_children_and_reassign(main_armature)
            
            if success:
                self.report({'INFO'}, "✓ Pose aplicada exitosamente (shape keys procesadas)")
                print("[TEST] ✅ ÉXITO: Aplicación de pose completada exitosamente")
                print("[TEST] - Shape keys aplicadas y eliminadas")
                print("[TEST] - Modificadores armature aplicados y recreados")
            else:
                self.report({'WARNING'}, "⚠ Pose aplicada parcialmente")
                print("[TEST] ⚠ PARCIAL: Aplicación de pose completada con advertencias")
            
            return {'FINISHED'}
            
        except Exception as e:
            error_msg = f"Error durante la prueba: {str(e)}"
            self.report({'ERROR'}, error_msg)
            print(f"[TEST] ❌ ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
        
        finally:
            print("="*60 + "\n")


class UNIVERSALGTA_OT_verify_pose_setup(Operator):
    """Verificar setup de pose sin aplicar cambios"""
    bl_idname = "universalgta.verify_pose_setup"
    bl_label = "Verify Pose Setup"
    bl_description = "Verifica el setup actual sin aplicar cambios"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        try:
            external_pose_caller.verify_post_conversion_setup()
            self.report({'INFO'}, "Verificación completada. Ver consola para detalles.")
        except Exception as e:
            self.report({'ERROR'}, f"Error en verificación: {str(e)}")
        return {'FINISHED'}


class UNIVERSALGTA_OT_apply_manual_pose(Operator):
    """Aplicar pose manual al armature y sus hijos"""
    bl_idname = "universalgta.apply_manual_pose"
    bl_label = "Apply Manual Pose"
    bl_description = "Aplica la pose actual del armature activo a sus mallas hijas"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        armature = context.active_object
        
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No hay armature válido seleccionado")
            return {'CANCELLED'}
        
        try:
            success = external_pose_caller.apply_manual_pose_to_children_and_reassign(armature)
            
            if success:
                self.report({'INFO'}, "Pose manual aplicada con éxito")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Error al aplicar pose manual")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_apply_custom_pose,
    UNIVERSALGTA_OT_test_pose_application,
    UNIVERSALGTA_OT_verify_pose_setup,
    UNIVERSALGTA_OT_apply_manual_pose,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()