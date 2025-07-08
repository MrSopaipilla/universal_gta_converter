# operators/pose_diagnostics.py
"""
Operadores para diagnóstico y reparación de problemas con poses personalizadas
"""

import bpy
from bpy.types import Operator
from .. import external_pose_caller


class UNIVERSALGTA_OT_diagnose_pose_issues(Operator):
    """Diagnosticar problemas comunes con la aplicación de pose personalizada"""
    bl_idname = "universalgta.diagnose_pose_issues"
    bl_label = "Diagnose Pose Issues"
    bl_description = "Analiza y reporta problemas comunes que pueden causar fallos en la aplicación de pose personalizada"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        print("\n" + "="*60)
        print("DIAGNÓSTICO DE POSE PERSONALIZADA")
        print("="*60)
        
        issues = []
        warnings = []
        info = []
        
        # 1. Verificar armatures disponibles
        armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
        print(f"\n1. ARMATURES EN ESCENA: {len(armatures)}")
        
        if not armatures:
            issues.append("No hay armatures en la escena")
        else:
            for arm in armatures:
                bone_count = len(arm.data.bones)
                mesh_count = len([obj for obj in bpy.data.objects 
                                if obj.type == 'MESH' and any(
                                    mod.type == 'ARMATURE' and mod.object == arm 
                                    for mod in obj.modifiers
                                )])
                print(f"   - {arm.name}: {bone_count} huesos, {mesh_count} meshes asociados")
                
                if bone_count == 0:
                    issues.append(f"Armature '{arm.name}' no tiene huesos")
                
                if mesh_count == 0:
                    warnings.append(f"Armature '{arm.name}' no tiene meshes asociados")
        
        # 2. Verificar target armature específico
        print(f"\n2. TARGET ARMATURE: {settings.target_armature.name if settings.target_armature else 'No definido'}")
        
        if not settings.target_armature:
            issues.append("No se ha definido target armature en configuración")
        elif settings.target_armature.type != 'ARMATURE':
            issues.append("El target armature no es válido")
        else:
            target = settings.target_armature
            print(f"   - Nombre: {target.name}")
            print(f"   - Huesos: {len(target.data.bones)}")
            print(f"   - Visible: {not target.hide_viewport}")
            print(f"   - En escena: {target.name in bpy.context.scene.objects}")
            
            if target.hide_viewport:
                warnings.append("Target armature está oculto")
            
            if target.name not in bpy.context.scene.objects:
                issues.append("Target armature no está en la escena actual")
        
        # 3. Verificar meshes con modificadores armature
        print(f"\n3. MESHES CON MODIFICADORES ARMATURE:")
        
        meshes_with_armature = []
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                armature_mods = [mod for mod in obj.modifiers if mod.type == 'ARMATURE']
                if armature_mods:
                    meshes_with_armature.append((obj, armature_mods))
        
        if not meshes_with_armature:
            issues.append("No se encontraron meshes con modificadores armature")
        else:
            for mesh, mods in meshes_with_armature:
                print(f"   - {mesh.name}:")
                for mod in mods:
                    target_name = mod.object.name if mod.object else "None"
                    enabled = "✓" if mod.show_viewport else "✗"
                    print(f"     • Modificador '{mod.name}' -> {target_name} ({enabled})")
                    
                    if not mod.object:
                        issues.append(f"Mesh '{mesh.name}' tiene modificador armature sin target")
                    elif not mod.show_viewport:
                        warnings.append(f"Mesh '{mesh.name}' tiene modificador armature deshabilitado")
        
        # 4. Verificar poses en armatures
        print(f"\n4. POSES EN ARMATURES:")
        
        for arm in armatures:
            has_pose_transforms = False
            transformed_bones = []
            
            for pose_bone in arm.pose.bones:
                if (pose_bone.location.length > 0.001 or 
                    any(abs(rot) > 0.001 for rot in pose_bone.rotation_euler) or
                    any(abs(s - 1.0) > 0.001 for s in pose_bone.scale)):
                    has_pose_transforms = True
                    transformed_bones.append(pose_bone.name)
            
            if has_pose_transforms:
                print(f"   - {arm.name}: {len(transformed_bones)} huesos con transformaciones")
                if len(transformed_bones) <= 5:
                    print(f"     Huesos: {', '.join(transformed_bones)}")
                else:
                    print(f"     Primeros huesos: {', '.join(transformed_bones[:5])}...")
            else:
                print(f"   - {arm.name}: Sin transformaciones de pose")
                info.append(f"Armature '{arm.name}' no tiene pose personalizada para aplicar")
        
        # 5. Verificar modo de operación actual
        print(f"\n5. ESTADO ACTUAL:")
        print(f"   - Modo: {bpy.context.mode}")
        print(f"   - Objeto activo: {bpy.context.active_object.name if bpy.context.active_object else 'None'}")
        print(f"   - Objetos seleccionados: {len(bpy.context.selected_objects)}")
        
        # 6. Verificar configuración del addon
        print(f"\n6. CONFIGURACIÓN DEL ADDON:")
        print(f"   - Auto aplicar pose: {settings.auto_apply_custom_pose}")
        print(f"   - Source armature: {settings.source_armature.name if settings.source_armature else 'None'}")
        print(f"   - Target armature: {settings.target_armature.name if settings.target_armature else 'None'}")
        
        # Resumen
        print(f"\n" + "="*60)
        print("RESUMEN DEL DIAGNÓSTICO")
        print("="*60)
        
        if issues:
            print(f"\n❌ PROBLEMAS CRÍTICOS ({len(issues)}):")
            for issue in issues:
                print(f"   • {issue}")
        
        if warnings:
            print(f"\n⚠️  ADVERTENCIAS ({len(warnings)}):")
            for warning in warnings:
                print(f"   • {warning}")
        
        if info:
            print(f"\n💡 INFORMACIÓN ({len(info)}):")
            for item in info:
                print(f"   • {item}")
        
        if not issues and not warnings:
            print(f"\n✅ Todo parece estar en orden para la aplicación de pose personalizada")
        
        print("="*60 + "\n")
        
        # Reportar resultado en UI
        if issues:
            self.report({'ERROR'}, f"Se encontraron {len(issues)} problemas críticos. Ver consola para detalles.")
        elif warnings:
            self.report({'WARNING'}, f"Se encontraron {len(warnings)} advertencias. Ver consola para detalles.")
        else:
            self.report({'INFO'}, "Diagnóstico completado. No se encontraron problemas.")
        
        return {'FINISHED'}


class UNIVERSALGTA_OT_fix_pose_issues(Operator):
    """Intentar reparar automáticamente problemas comunes de pose"""
    bl_idname = "universalgta.fix_pose_issues"
    bl_label = "Fix Pose Issues"
    bl_description = "Intenta reparar automáticamente problemas comunes que impiden la aplicación de pose personalizada"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        fixes_applied = []
        
        print("[POSE_FIX] Iniciando reparación automática de problemas de pose...")
        
        # 1. Reparar modificadores armature rotos
        fixed_modifiers = self._fix_broken_armature_modifiers(settings)
        if fixed_modifiers > 0:
            fixes_applied.append(f"Reparados {fixed_modifiers} modificadores armature")
        
        # 2. Hacer visibles objetos necesarios
        visible_objects = self._make_necessary_objects_visible(settings)
        if visible_objects > 0:
            fixes_applied.append(f"Hechos visibles {visible_objects} objetos")
        
        # 3. Configurar objeto activo correctamente
        if self._set_correct_active_object(settings):
            fixes_applied.append("Configurado objeto activo correctamente")
        
        # 4. Limpiar modo de operación
        if self._ensure_object_mode():
            fixes_applied.append("Modo de operación corregido")
        
        # 5. Verificar y reparar jerarquías
        fixed_hierarchies = self._fix_object_hierarchies(settings)
        if fixed_hierarchies > 0:
            fixes_applied.append(f"Reparadas {fixed_hierarchies} jerarquías de objetos")
        
        # Reportar resultados
        if fixes_applied:
            fix_list = ", ".join(fixes_applied)
            self.report({'INFO'}, f"Reparaciones aplicadas: {fix_list}")
            print(f"[POSE_FIX] Reparaciones completadas: {fix_list}")
        else:
            self.report({'INFO'}, "No se encontraron problemas que reparar automáticamente")
            print("[POSE_FIX] No se encontraron problemas automáticamente reparables")
        
        return {'FINISHED'}
    
    def _fix_broken_armature_modifiers(self, settings):
        """Repara modificadores armature rotos"""
        fixed_count = 0
        target_armature = settings.target_armature
        
        if not target_armature:
            return fixed_count
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE':
                        needs_fix = False
                        
                        if not modifier.object:
                            needs_fix = True
                        elif modifier.object.type != 'ARMATURE':
                            needs_fix = True
                        elif modifier.object.name not in bpy.data.objects:
                            needs_fix = True
                        
                        if needs_fix:
                            modifier.object = target_armature
                            fixed_count += 1
                            print(f"[POSE_FIX] Modificador reparado en {obj.name}")
        
        return fixed_count
    
    def _make_necessary_objects_visible(self, settings):
        """Hace visibles objetos necesarios para la pose"""
        visible_count = 0
        
        if settings.target_armature:
            if settings.target_armature.hide_viewport:
                settings.target_armature.hide_viewport = False
                visible_count += 1
                print(f"[POSE_FIX] Target armature hecho visible")
        
        # Hacer visibles meshes con modificadores armature
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                has_armature_mod = any(mod.type == 'ARMATURE' for mod in obj.modifiers)
                if has_armature_mod and obj.hide_viewport:
                    obj.hide_viewport = False
                    visible_count += 1
                    print(f"[POSE_FIX] Mesh {obj.name} hecho visible")
        
        return visible_count
    
    def _set_correct_active_object(self, settings):
        """Configura el objeto activo correctamente"""
        if settings.target_armature and bpy.context.active_object != settings.target_armature:
            bpy.context.view_layer.objects.active = settings.target_armature
            print(f"[POSE_FIX] Objeto activo configurado: {settings.target_armature.name}")
            return True
        return False
    
    def _ensure_object_mode(self):
        """Asegura que estemos en modo objeto"""
        if bpy.context.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
                print("[POSE_FIX] Cambiado a modo objeto")
                return True
            except:
                print("[POSE_FIX] No se pudo cambiar a modo objeto")
        return False
    
    def _fix_object_hierarchies(self, settings):
        """Repara jerarquías de objetos problemáticas"""
        fixed_count = 0
        
        # Esta función se puede expandir según problemas específicos encontrados
        # Por ahora, es un placeholder
        
        return fixed_count


class UNIVERSALGTA_OT_manual_apply_pose(Operator):
    """Aplicar pose personalizada manualmente con diagnóstico detallado"""
    bl_idname = "universalgta.manual_apply_pose"
    bl_label = "Manual Apply Pose"
    bl_description = "Aplica manualmente la pose personalizada con diagnóstico detallado de errores"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Primero ejecutar diagnóstico
        print("[MANUAL_POSE] Ejecutando diagnóstico previo...")
        bpy.ops.universalgta.diagnose_pose_issues()
        
        # Intentar reparaciones automáticas
        print("[MANUAL_POSE] Aplicando reparaciones automáticas...")
        bpy.ops.universalgta.fix_pose_issues()
        
        # Aplicar pose
        print("[MANUAL_POSE] Intentando aplicar pose personalizada...")
        
        try:
            applier = external_pose_caller.ExternalPoseApplier()
            success = applier.execute_full_pose_application(
                source_armature=None,
                target_armature=settings.target_armature
            )
            
            if success:
                self.report({'INFO'}, "Pose personalizada aplicada exitosamente")
            else:
                self.report({'WARNING'}, "La pose personalizada se aplicó parcialmente. Ver consola para detalles.")
            
        except Exception as e:
            self.report({'ERROR'}, f"Error aplicando pose: {str(e)}")
            print(f"[MANUAL_POSE] Error: {e}")
            import traceback
            traceback.print_exc()
        
        return {'FINISHED'}


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_diagnose_pose_issues,
    UNIVERSALGTA_OT_fix_pose_issues,
    UNIVERSALGTA_OT_manual_apply_pose,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)