# external_pose_caller.py - CORREGIDO: Detección de pose y Shape Keys
"""
external_pose_caller.py - Funciones para aplicar poses personalizadas
VERSIÓN CORREGIDA: DETECCIÓN MEJORADA DE POSES Y SHAPE KEYS
"""

import bpy
from bpy import context, ops
from mathutils import Vector


def apply_manual_pose_to_children_and_reassign(armature=None):
    """
    Aplica la pose actual del armature a las mallas conectadas,
    procesando correctamente SHAPE KEYS y aplicando deformación del armature.
    
    PROCESO CORREGIDO:
    1. Encuentra el armature principal (Root)
    2. Encuentra meshes con modificador armature apuntando a ese armature
    3. PROCESA SHAPE KEYS CORRECTAMENTE (no vertex groups)
    4. Aplica el modificador armature (hornea la deformación)
    5. Crea nuevo modificador armature apuntando al mismo armature
    
    Args:
        armature: El armature target (Root). Si es None, se detecta automáticamente.
    
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario.
    """
    
    # Detectar armature principal si no se proporciona
    if not armature:
        armature = _find_main_armature_post_conversion()
        
    if not armature or armature.type != 'ARMATURE':
        print("[POSE_UTIL] No se encontró armature válido para aplicar pose.")
        return False

    print(f"[POSE_UTIL] === PROCESANDO ARMATURE POST-CONVERSIÓN: {armature.name} ===")

    # Verificar si hay poses para aplicar (MEJORADO)
    has_pose = _check_armature_has_pose_detailed(armature)
    print(f"[POSE_UTIL] Pose detectada: {has_pose}")

    # Encontrar meshes con modificador armature apuntando a este armature
    target_meshes = _find_meshes_with_armature_modifier(armature)

    if not target_meshes:
        print("[POSE_UTIL] No se encontraron meshes con modificador armature.")
        return False

    print(f"[POSE_UTIL] Encontrados {len(target_meshes)} meshes con modificador armature")

    try:
        # Asegurar que estamos en modo objeto
        _safe_mode_set('OBJECT')
        
        # Procesar cada mesh: shape keys, aplicar deformación y recrear modificador
        success_count = 0
        for mesh_obj in target_meshes:
            if _process_mesh_complete_corrected(mesh_obj, armature, has_pose):
                success_count += 1

        print(f"[POSE_UTIL] Proceso completado. {success_count}/{len(target_meshes)} meshes procesados exitosamente.")
        return success_count > 0

    except Exception as e:
        print(f"[POSE_UTIL] ERROR durante el proceso: {e}")
        import traceback
        traceback.print_exc()
        
        # Intentar volver a modo objeto en caso de error
        _safe_mode_set('OBJECT')
        return False


def _check_armature_has_pose_detailed(armature):
    """Verificación MEJORADA de pose con debug detallado"""
    try:
        print(f"[POSE_DEBUG] === VERIFICANDO POSE EN {armature.name} ===")
        
        # Cambiar a modo pose para verificar
        bpy.context.view_layer.objects.active = armature
        _safe_mode_set('OBJECT')
        bpy.ops.object.mode_set(mode='POSE')
        
        has_transforms = False
        transformed_bones = []
        
        for pose_bone in armature.pose.bones:
            # Verificar location, rotation y scale con umbrales más bajos
            has_location = pose_bone.location.length > 0.0001
            has_rotation = any(abs(rot) > 0.0001 for rot in pose_bone.rotation_euler)
            has_scale = any(abs(s - 1.0) > 0.0001 for s in pose_bone.scale)
            
            if has_location or has_rotation or has_scale:
                has_transforms = True
                transform_info = []
                if has_location:
                    transform_info.append(f"loc:{pose_bone.location.length:.3f}")
                if has_rotation:
                    transform_info.append(f"rot:{max(abs(r) for r in pose_bone.rotation_euler):.3f}")
                if has_scale:
                    transform_info.append(f"scale:{max(abs(s-1.0) for s in pose_bone.scale):.3f}")
                
                bone_info = f"{pose_bone.name}({','.join(transform_info)})"
                transformed_bones.append(bone_info)
                print(f"[POSE_DEBUG] Transformación detectada: {bone_info}")
        
        # Volver a modo objeto
        bpy.ops.object.mode_set(mode='OBJECT')
        
        if has_transforms:
            print(f"[POSE_DEBUG] ✓ POSE DETECTADA: {len(transformed_bones)} huesos con transformaciones")
            if len(transformed_bones) <= 10:
                for bone_info in transformed_bones:
                    print(f"[POSE_DEBUG]   - {bone_info}")
            else:
                for bone_info in transformed_bones[:10]:
                    print(f"[POSE_DEBUG]   - {bone_info}")
                print(f"[POSE_DEBUG]   ... y {len(transformed_bones)-10} más")
        else:
            print("[POSE_DEBUG] ✗ NO SE DETECTARON TRANSFORMACIONES DE POSE")
        
        return has_transforms
        
    except Exception as e:
        print(f"[POSE_DEBUG] Error verificando pose: {e}")
        _safe_mode_set('OBJECT')
        return False


def _process_mesh_complete_corrected(mesh_obj, armature, has_pose):
    """
    Proceso completo CORREGIDO: shape keys, aplicar modificador armature y recrear
    """
    print(f"[POSE_UTIL] === PROCESANDO MESH: {mesh_obj.name} ===")
    
    try:
        # Paso 1: Activar el mesh
        bpy.context.view_layer.objects.active = mesh_obj
        _safe_mode_set('OBJECT')
        
        # Deseleccionar todo y seleccionar solo este mesh
        bpy.ops.object.select_all(action='DESELECT')
        mesh_obj.select_set(True)
        
        # Paso 2: Procesar Shape Keys (NO vertex groups)
        shape_keys_processed = _process_shape_keys_correctly(mesh_obj)
        if shape_keys_processed > 0:
            print(f"[POSE_UTIL] ✓ {shape_keys_processed} Shape keys procesadas en {mesh_obj.name}")
        else:
            print(f"[POSE_UTIL] ℹ No había shape keys en {mesh_obj.name}")
        
        # Paso 3: Buscar el modificador armature
        armature_modifier = None
        for modifier in mesh_obj.modifiers:
            if modifier.type == 'ARMATURE' and modifier.object == armature:
                armature_modifier = modifier
                break
        
        if not armature_modifier:
            print(f"[POSE_UTIL] ✗ No se encontró modificador armature en {mesh_obj.name}")
            return False
        
        # Paso 4: Verificar y habilitar el modificador
        if not armature_modifier.show_viewport:
            print(f"[POSE_UTIL] Habilitando modificador armature en {mesh_obj.name}")
            armature_modifier.show_viewport = True
        
        # Paso 5: Aplicar el modificador armature SOLO SI hay pose
        if has_pose:
            try:
                modifier_name = armature_modifier.name
                print(f"[POSE_UTIL] Aplicando modificador '{modifier_name}' en {mesh_obj.name} (pose detectada)")
                
                # Aplicar modificador - esto hornea la pose en la geometría
                bpy.ops.object.modifier_apply(modifier=modifier_name)
                
                print(f"[POSE_UTIL] ✓ Modificador aplicado exitosamente en {mesh_obj.name}")
                
                # Paso 6: Crear nuevo modificador armature apuntando al mismo armature
                new_modifier = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
                new_modifier.object = armature
                
                print(f"[POSE_UTIL] ✓ Nuevo modificador armature creado en {mesh_obj.name}")
                
            except Exception as e:
                print(f"[POSE_UTIL] ✗ Error aplicando modificador en {mesh_obj.name}: {e}")
                return False
        else:
            print(f"[POSE_UTIL] ℹ No se aplica modificador en {mesh_obj.name} (no hay pose)")
        
        print(f"[POSE_UTIL] ✓ {mesh_obj.name} procesado completamente")
        return True
        
    except Exception as e:
        print(f"[POSE_UTIL] ✗ Error procesando mesh {mesh_obj.name}: {e}")
        return False


def _process_shape_keys_correctly(mesh_obj):
    """
    Procesa SHAPE KEYS correctamente (no vertex groups)
    
    Returns:
        int: Número de shape keys procesadas
    """
    # Verificar si el mesh tiene shape keys
    if not mesh_obj.data.shape_keys or not mesh_obj.data.shape_keys.key_blocks:
        return 0
    
    key_blocks = mesh_obj.data.shape_keys.key_blocks
    initial_count = len(key_blocks)
    
    print(f"[SHAPE_KEYS] {mesh_obj.name} tiene {initial_count} shape keys")
    
    try:
        # Listar todas las shape keys
        shape_key_names = [key.name for key in key_blocks]
        print(f"[SHAPE_KEYS] Shape keys encontradas: {shape_key_names}")
        
        # Aplicar todas las shape keys de arriba hacia abajo (desde la última hasta la primera)
        # Esto es importante porque los índices cambian cuando eliminas shape keys
        processed_count = 0
        
        for i in range(len(key_blocks) - 1, -1, -1):
            try:
                # Verificar que el índice todavía es válido
                if i >= len(mesh_obj.data.shape_keys.key_blocks):
                    continue
                    
                # Establecer como activa
                mesh_obj.active_shape_key_index = i
                key_name = key_blocks[i].name if i < len(key_blocks) else f"index_{i}"
                
                print(f"[SHAPE_KEYS] Procesando shape key: {key_name} (índice {i})")
                
                # Aplicar como mix (esto aplica la deformación y elimina la shape key)
                bpy.ops.object.shape_key_remove(all=False)
                
                print(f"[SHAPE_KEYS] ✓ Shape key '{key_name}' aplicada y eliminada")
                processed_count += 1
                
            except Exception as e:
                print(f"[SHAPE_KEYS] ✗ Error procesando shape key índice {i}: {e}")
        
        # Verificar que se eliminaron todas
        remaining_keys = len(mesh_obj.data.shape_keys.key_blocks) if mesh_obj.data.shape_keys else 0
        print(f"[SHAPE_KEYS] ✓ Procesamiento completo: {initial_count} -> {remaining_keys} shape keys")
        
        return processed_count
        
    except Exception as e:
        print(f"[SHAPE_KEYS] ✗ Error general procesando shape keys en {mesh_obj.name}: {e}")
        return 0


def _find_main_armature_post_conversion():
    """
    Encuentra el armature principal después de la conversión GTA SA.
    Debería ser el armature llamado 'Root' o similar.
    """
    armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
    
    if not armatures:
        print("[POSE_UTIL] No se encontraron armatures en la escena")
        return None
    
    # Buscar armature con nombre 'Root' o similar (PRIORIDAD)
    for armature in armatures:
        if armature.name.lower() in ['root', 'gta_root', 'gta_sa_root']:
            print(f"[POSE_UTIL] Armature principal encontrado: {armature.name}")
            return armature
    
    # Si no se encuentra Root, buscar el que tenga más meshes asociados
    best_armature = None
    max_meshes = 0
    
    for armature in armatures:
        mesh_count = len(_find_meshes_with_armature_modifier(armature))
        print(f"[POSE_UTIL] {armature.name}: {mesh_count} meshes asociados")
        if mesh_count > max_meshes:
            max_meshes = mesh_count
            best_armature = armature
    
    if best_armature:
        print(f"[POSE_UTIL] Armature principal detectado por asociaciones: {best_armature.name}")
        return best_armature
    
    # Como última opción, tomar el primero disponible
    if armatures:
        print(f"[POSE_UTIL] Usando primer armature disponible: {armatures[0].name}")
        return armatures[0]
    
    return None


def _find_meshes_with_armature_modifier(armature):
    """Encuentra meshes que tienen modificador armature apuntando al armature dado"""
    target_meshes = []
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE' and modifier.object == armature:
                    target_meshes.append(obj)
                    print(f"[POSE_UTIL] Mesh encontrado: {obj.name} -> {armature.name}")
                    break
    
    return target_meshes


def _safe_mode_set(mode):
    """Cambia de modo de forma segura"""
    try:
        current_mode = bpy.context.mode
        if current_mode != mode.upper():
            bpy.ops.object.mode_set(mode=mode)
            print(f"[POSE_UTIL] Modo cambiado: {current_mode} -> {mode}")
    except Exception as e:
        print(f"[POSE_UTIL] No se pudo cambiar a modo {mode}: {e}")


class ExternalPoseApplier:
    """Clase para aplicar poses personalizadas POST-CONVERSIÓN"""
    
    def __init__(self):
        self.debug = True
    
    def execute_full_pose_application(self, source_armature=None, target_armature=None):
        """
        Ejecuta la aplicación completa de pose personalizada POST-CONVERSIÓN
        
        Args:
            source_armature: IGNORADO - ya no existe después de conversión
            target_armature: Armature destino (Root)
        
        Returns:
            bool: True si fue exitoso
        """
        try:
            print("[EXTERNAL_POSE] === INICIANDO APLICACIÓN DE POSE POST-CONVERSIÓN ===")
            
            # El source_armature ya no existe después de la conversión GTA SA
            # Solo necesitamos el target_armature (Root)
            if not target_armature:
                target_armature = _find_main_armature_post_conversion()
            
            if not target_armature:
                print("[EXTERNAL_POSE] ✗ No se encontró armature válido")
                return False
            
            print(f"[EXTERNAL_POSE] ✓ Usando armature: {target_armature.name}")
            
            # Verificar que el armature tenga una pose para aplicar (MEJORADO)
            has_pose = _check_armature_has_pose_detailed(target_armature)
            
            if not has_pose:
                print("[EXTERNAL_POSE] ℹ No hay transformaciones de pose para aplicar")
                print("[EXTERNAL_POSE] ⚠ PERO SE PROCESARÁN SHAPE KEYS SI EXISTEN")
                # No retornar False - continúar para procesar Shape Keys
            
            # Aplicar pose usando la función principal (SIEMPRE ejecutar para Shape Keys)
            success = apply_manual_pose_to_children_and_reassign(target_armature)
            
            if success:
                if has_pose:
                    print("[EXTERNAL_POSE] ✓ Pose personalizada aplicada exitosamente")
                else:
                    print("[EXTERNAL_POSE] ✓ Shape Keys procesadas exitosamente (sin pose)")
            else:
                print("[EXTERNAL_POSE] ✗ Falló el procesamiento")
            
            print("[EXTERNAL_POSE] === APLICACIÓN DE POSE COMPLETADA ===")
            return success
            
        except Exception as e:
            print(f"[EXTERNAL_POSE] ✗ Error durante la aplicación de pose: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _armature_has_pose_transforms(self, armature):
        """Verifica si el armature tiene transformaciones de pose - MÉTODO LEGACY"""
        return _check_armature_has_pose_detailed(armature)


# Funciones de conveniencia para compatibilidad
def apply_pose_to_armature(armature):
    """Función de conveniencia para aplicar pose a un armature"""
    return apply_manual_pose_to_children_and_reassign(armature)


def execute_external_pose_application(source_armature=None, target_armature=None):
    """Función de conveniencia para ejecutar aplicación de pose externa"""
    applier = ExternalPoseApplier()
    return applier.execute_full_pose_application(source_armature, target_armature)


# Función adicional para verificar el estado post-conversión
def verify_post_conversion_setup():
    """Verifica que el setup post-conversión sea correcto"""
    print("\n[VERIFICATION] === Verificando setup post-conversión ===")
    
    # Verificar armatures
    armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
    print(f"[VERIFICATION] Armatures encontrados: {[arm.name for arm in armatures]}")
    
    # Verificar meshes con modificadores
    meshes_with_modifiers = []
    meshes_with_shape_keys = []
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            # Verificar modificadores armature
            armature_mods = [mod for mod in obj.modifiers if mod.type == 'ARMATURE']
            if armature_mods:
                for mod in armature_mods:
                    target_name = mod.object.name if mod.object else "None"
                    meshes_with_modifiers.append(f"{obj.name}->{target_name}")
            
            # Verificar shape keys
            if obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) > 0:
                shape_count = len(obj.data.shape_keys.key_blocks)
                shape_names = [key.name for key in obj.data.shape_keys.key_blocks]
                meshes_with_shape_keys.append(f"{obj.name}({shape_count}): {shape_names}")
    
    print(f"[VERIFICATION] Meshes con modificadores: {meshes_with_modifiers}")
    print(f"[VERIFICATION] Meshes con shape keys: {meshes_with_shape_keys}")
    
    # Buscar armature principal
    main_armature = _find_main_armature_post_conversion()
    if main_armature:
        print(f"[VERIFICATION] ✓ Armature principal: {main_armature.name}")
        
        # Verificar pose
        has_pose = _check_armature_has_pose_detailed(main_armature)
        print(f"[VERIFICATION] Tiene pose para aplicar: {has_pose}")
    else:
        print("[VERIFICATION] ✗ No se encontró armature principal")
    
    print("[VERIFICATION] === Verificación completada ===\n")