# operators/shape_keys.py - VERSIÓN CORREGIDA
"""
Operadores para manejo de Shape Keys en Universal GTA SA Converter
CORREGIDO: Aplica TODAS las shape keys independientemente de su valor (incluso 0)
           Elimina TODAS las shape keys incluyendo Basis
"""

import bpy
import bmesh
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty


class UNIVERSALGTA_OT_apply_all_shape_keys(Operator):
    """Aplicar TODAS las shape keys sin importar su valor (incluso 0)"""
    bl_idname = "universalgta.apply_all_shape_keys"
    bl_label = "Apply All Shape Keys"
    bl_description = "Aplica TODAS las shape keys de los meshes hijos del armature fuente (incluso las de valor 0)"
    bl_options = {'REGISTER', 'UNDO'}
    
    # OBSOLETO - Ahora siempre se eliminan todas
    preserve_basis: BoolProperty(
        name="Preserve Basis (OBSOLETO)",
        description="OBSOLETO - Ahora se eliminan todas las shape keys incluyendo Basis",
        default=False
    )
    
    apply_with_modifier: BoolProperty(
        name="Apply with Armature Modifier", 
        description="Aplicar shape keys junto con el modificador armature",
        default=False
    )
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        source_armature = settings.source_armature
        
        if not source_armature or source_armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No se ha definido un armature fuente válido")
            return {'CANCELLED'}
        
        try:
            # Encontrar todos los meshes hijos del source armature
            child_meshes = self._find_child_meshes(source_armature)
            
            if not child_meshes:
                self.report({'WARNING'}, f"No se encontraron meshes hijos de {source_armature.name}")
                return {'CANCELLED'}
            
            total_shape_keys_applied = 0
            processed_meshes = []
            
            # Procesar cada mesh hijo
            for mesh_obj in child_meshes:
                result = self._process_mesh_shape_keys_corrected(mesh_obj)
                total_shape_keys_applied += result['applied']
                if result['applied'] > 0:
                    processed_meshes.append(mesh_obj.name)
            
            # Reportar resultados
            if total_shape_keys_applied > 0:
                mesh_list = ", ".join(processed_meshes)
                self.report({'INFO'}, 
                           f"Aplicadas {total_shape_keys_applied} shape keys (incluyendo valor 0) en {len(processed_meshes)} meshes: {mesh_list}")
            else:
                self.report({'INFO'}, "No se encontraron shape keys para aplicar")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error aplicando shape keys: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
    
    def _find_child_meshes(self, armature):
        """Encuentra todos los meshes que son hijos del armature"""
        child_meshes = []
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.parent == armature:
                child_meshes.append(obj)
        
        print(f"[SHAPE_KEYS] Encontrados {len(child_meshes)} meshes hijos de {armature.name}")
        for mesh in child_meshes:
            print(f"[SHAPE_KEYS] - {mesh.name}")
        
        return child_meshes
    
    def _process_mesh_shape_keys_corrected(self, mesh_obj):
        """
        VERSIÓN CORREGIDA: Procesa TODAS las shape keys sin importar su valor
        Elimina TODAS las shape keys incluyendo Basis
        """
        result = {'applied': 0, 'errors': []}
        
        # Verificar si el mesh tiene shape keys
        if not mesh_obj.data.shape_keys or not mesh_obj.data.shape_keys.key_blocks:
            print(f"[SHAPE_KEYS] {mesh_obj.name} no tiene shape keys")
            return result
        
        print(f"[SHAPE_KEYS] === PROCESANDO {mesh_obj.name} (MÉTODO CORREGIDO) ===")
        
        # Obtener lista de shape keys
        key_blocks = mesh_obj.data.shape_keys.key_blocks
        shape_key_names = [key.name for key in key_blocks]
        total_keys = len(shape_key_names)
        
        print(f"[SHAPE_KEYS] Shape keys encontradas: {shape_key_names}")
        print(f"[SHAPE_KEYS] Total: {total_keys} shape keys")
        
        # Activar el mesh
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='OBJECT')
        
        try:
            # MÉTODO CORREGIDO: Aplicar TODAS las shape keys sin verificar valor
            applied_count = self._apply_all_shape_keys_regardless_of_value(mesh_obj)
            result['applied'] = applied_count
            
            print(f"[SHAPE_KEYS] ✓ {mesh_obj.name}: {applied_count} shape keys aplicadas")
            
        except Exception as e:
            error_msg = f"Error en {mesh_obj.name}: {str(e)}"
            result['errors'].append(error_msg)
            print(f"[SHAPE_KEYS] ✗ {error_msg}")
        
        return result
    
    def _apply_all_shape_keys_regardless_of_value(self, mesh_obj):
        """
        MÉTODO CORREGIDO: Aplica TODAS las shape keys sin importar su valor
        Elimina TODAS las shape keys incluyendo Basis
        """
        applied_count = 0
        
        # Verificar shape keys
        if not mesh_obj.data.shape_keys:
            return applied_count
        
        key_blocks = mesh_obj.data.shape_keys.key_blocks
        initial_count = len(key_blocks)
        
        print(f"[SHAPE_KEYS] === APLICANDO TODAS LAS SHAPE KEYS ===")
        print(f"[SHAPE_KEYS] Total inicial: {initial_count}")
        
        # Crear lista de shape keys a procesar (TODAS excepto Basis)
        shape_keys_to_process = []
        basis_key = None
        
        for key_block in key_blocks:
            if key_block.name == "Basis":
                basis_key = key_block
                print(f"[SHAPE_KEYS] Basis encontrada: {key_block.name}")
            else:
                shape_keys_to_process.append({
                    'name': key_block.name,
                    'original_value': key_block.value
                })
                print(f"[SHAPE_KEYS] Shape key a procesar: {key_block.name} (valor: {key_block.value})")
        
        if not shape_keys_to_process:
            print(f"[SHAPE_KEYS] Solo hay Basis, nada que procesar")
            # Eliminar Basis también
            if basis_key:
                mesh_obj.active_shape_key_index = 0
                bpy.ops.object.shape_key_remove(all=False)
                applied_count = 1
                print(f"[SHAPE_KEYS] Basis eliminada")
            return applied_count
        
        # PASO 1: Aplicar cada shape key individualmente sin importar su valor
        for i, shape_info in enumerate(shape_keys_to_process):
            try:
                # Verificar que todavía existe
                if not mesh_obj.data.shape_keys or len(mesh_obj.data.shape_keys.key_blocks) <= 1:
                    break
                
                # Buscar la shape key por nombre (el índice puede cambiar)
                key_index = self._find_shape_key_index_by_name(mesh_obj, shape_info['name'])
                
                if key_index == -1:
                    print(f"[SHAPE_KEYS] ⚠ Shape key {shape_info['name']} ya no existe")
                    continue
                
                # Seleccionar la shape key
                mesh_obj.active_shape_key_index = key_index
                current_key = mesh_obj.data.shape_keys.key_blocks[key_index]
                
                print(f"[SHAPE_KEYS] Procesando: {current_key.name} (valor original: {shape_info['original_value']})")
                
                # APLICAR sin modificar el valor - usar from_mix=True para aplicar la deformación actual
                bpy.ops.object.shape_key_add(from_mix=True)
                applied_count += 1
                
                print(f"[SHAPE_KEYS] ✓ Aplicada: {shape_info['name']}")
                
            except Exception as e:
                print(f"[SHAPE_KEYS] ✗ Error procesando {shape_info['name']}: {e}")
        
        # PASO 2: Eliminar TODAS las shape keys restantes (incluyendo Basis)
        print(f"[SHAPE_KEYS] === ELIMINANDO TODAS LAS SHAPE KEYS ===")
        
        elimination_count = 0
        while mesh_obj.data.shape_keys and len(mesh_obj.data.shape_keys.key_blocks) > 0:
            try:
                # Siempre eliminar la primera shape key
                mesh_obj.active_shape_key_index = 0
                key_name = mesh_obj.data.shape_keys.key_blocks[0].name
                
                bpy.ops.object.shape_key_remove(all=False)
                elimination_count += 1
                
                print(f"[SHAPE_KEYS] ✓ Eliminada: {key_name}")
                
            except Exception as e:
                print(f"[SHAPE_KEYS] ✗ Error eliminando shape key: {e}")
                break
        
        print(f"[SHAPE_KEYS] ✓ Proceso completado:")
        print(f"[SHAPE_KEYS]   - Shape keys aplicadas: {applied_count}")
        print(f"[SHAPE_KEYS]   - Shape keys eliminadas: {elimination_count}")
        
        # Verificar que no queden shape keys
        remaining_keys = len(mesh_obj.data.shape_keys.key_blocks) if mesh_obj.data.shape_keys else 0
        if remaining_keys == 0:
            print(f"[SHAPE_KEYS] ✓ Todas las shape keys eliminadas correctamente")
        else:
            print(f"[SHAPE_KEYS] ⚠ Quedan {remaining_keys} shape keys")
        
        return applied_count
    
    def _find_shape_key_index_by_name(self, mesh_obj, name):
        """Encuentra el índice de una shape key por nombre"""
        if not mesh_obj.data.shape_keys:
            return -1
        
        for i, key_block in enumerate(mesh_obj.data.shape_keys.key_blocks):
            if key_block.name == name:
                return i
        
        return -1


class UNIVERSALGTA_OT_backup_shape_keys(Operator):
    """Crear backup de todas las shape keys antes de aplicarlas"""
    bl_idname = "universalgta.backup_shape_keys"
    bl_label = "Backup Shape Keys"
    bl_description = "Crea una copia de seguridad de todos los meshes con shape keys"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        source_armature = settings.source_armature
        
        if not source_armature:
            self.report({'ERROR'}, "No se ha definido un armature fuente")
            return {'CANCELLED'}
        
        try:
            backup_count = 0
            
            # Encontrar meshes con shape keys
            for obj in bpy.data.objects:
                if (obj.type == 'MESH' and 
                    obj.parent == source_armature and 
                    obj.data.shape_keys and 
                    len(obj.data.shape_keys.key_blocks) > 1):
                    
                    # Crear backup
                    backup_obj = self._create_backup_mesh(obj)
                    if backup_obj:
                        backup_count += 1
                        print(f"[SHAPE_KEYS] Backup creado: {backup_obj.name}")
            
            if backup_count > 0:
                self.report({'INFO'}, f"Creados {backup_count} backups de meshes con shape keys")
            else:
                self.report({'INFO'}, "No se encontraron meshes con shape keys para hacer backup")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error creando backups: {str(e)}")
            return {'CANCELLED'}
    
    def _create_backup_mesh(self, original_obj):
        """Crea una copia de backup de un mesh con shape keys"""
        # Duplicar objeto
        bpy.context.view_layer.objects.active = original_obj
        bpy.ops.object.select_all(action='DESELECT')
        original_obj.select_set(True)
        bpy.ops.object.duplicate()
        
        backup_obj = bpy.context.active_object
        backup_obj.name = f"{original_obj.name}_BACKUP_ShapeKeys"
        
        # Mover a una colección específica o esconder
        backup_obj.hide_set(True)
        backup_obj.hide_viewport = True
        
        return backup_obj


class UNIVERSALGTA_OT_restore_shape_keys_backup(Operator):
    """Restaurar shape keys desde backup"""
    bl_idname = "universalgta.restore_shape_keys_backup"
    bl_label = "Restore Shape Keys"
    bl_description = "Restaura las shape keys desde los backups creados"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            restored_count = 0
            
            # Buscar backups
            backup_objects = [obj for obj in bpy.data.objects 
                            if obj.name.endswith("_BACKUP_ShapeKeys")]
            
            for backup_obj in backup_objects:
                # Obtener nombre original
                original_name = backup_obj.name.replace("_BACKUP_ShapeKeys", "")
                
                if original_name in bpy.data.objects:
                    original_obj = bpy.data.objects[original_name]
                    
                    # Restaurar shape keys
                    if self._restore_shape_keys_from_backup(backup_obj, original_obj):
                        restored_count += 1
            
            if restored_count > 0:
                self.report({'INFO'}, f"Restauradas shape keys en {restored_count} objetos")
            else:
                self.report({'WARNING'}, "No se encontraron backups para restaurar")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error restaurando backups: {str(e)}")
            return {'CANCELLED'}
    
    def _restore_shape_keys_from_backup(self, backup_obj, original_obj):
        """Restaura shape keys desde un backup específico"""
        try:
            # Copiar mesh data del backup al original
            if backup_obj.data.shape_keys:
                # Crear nueva mesh data con shape keys
                new_mesh = backup_obj.data.copy()
                
                # Reemplazar mesh data
                old_mesh = original_obj.data
                original_obj.data = new_mesh
                
                # Limpiar mesh antiguo
                bpy.data.meshes.remove(old_mesh)
                
                print(f"[SHAPE_KEYS] Shape keys restauradas en {original_obj.name}")
                return True
            
        except Exception as e:
            print(f"[SHAPE_KEYS] Error restaurando {original_obj.name}: {e}")
        
        return False


class UNIVERSALGTA_OT_list_shape_keys(Operator):
    """Listar todas las shape keys de los meshes hijos"""
    bl_idname = "universalgta.list_shape_keys"
    bl_label = "List Shape Keys"
    bl_description = "Lista todas las shape keys encontradas en los meshes hijos"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        source_armature = settings.source_armature
        
        if not source_armature:
            self.report({'ERROR'}, "No se ha definido un armature fuente")
            return {'CANCELLED'}
        
        # Encontrar y listar shape keys
        total_shape_keys = 0
        meshes_with_shape_keys = 0
        
        print("\n" + "="*50)
        print("SHAPE KEYS ENCONTRADAS - MÉTODO CORREGIDO")
        print("="*50)
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.parent == source_armature:
                if obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) > 1:
                    meshes_with_shape_keys += 1
                    print(f"\nMesh: {obj.name}")
                    
                    for i, key_block in enumerate(obj.data.shape_keys.key_blocks):
                        value_str = f"(valor: {key_block.value:.3f})" if key_block.value != 0 else "(valor: 0 - SE APLICARÁ IGUAL)"
                        print(f"  {i}: {key_block.name} {value_str}")
                        total_shape_keys += 1
                else:
                    print(f"\nMesh: {obj.name} - Sin shape keys")
        
        print("\n" + "="*50)
        print(f"RESUMEN: {total_shape_keys} shape keys en {meshes_with_shape_keys} meshes")
        print("NOTA: TODAS las shape keys se aplicarán, incluso las de valor 0")
        print("="*50 + "\n")
        
        self.report({'INFO'}, 
                   f"Encontradas {total_shape_keys} shape keys en {meshes_with_shape_keys} meshes. Ver consola para detalles.")
        
        return {'FINISHED'}


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_apply_all_shape_keys,
    UNIVERSALGTA_OT_backup_shape_keys,
    UNIVERSALGTA_OT_restore_shape_keys_backup,
    UNIVERSALGTA_OT_list_shape_keys,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)