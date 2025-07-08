# operators/shape_keys.py
"""
Operadores para manejo de Shape Keys en Universal GTA SA Converter
"""

import bpy
import bmesh
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty


class UNIVERSALGTA_OT_apply_all_shape_keys(Operator):
    """Aplicar todas las shape keys de los meshes hijos del Source armature"""
    bl_idname = "universalgta.apply_all_shape_keys"
    bl_label = "Apply All Shape Keys"
    bl_description = "Aplica todas las shape keys de los meshes hijos del armature fuente"
    bl_options = {'REGISTER', 'UNDO'}
    
    preserve_basis: BoolProperty(
        name="Preserve Basis",
        description="Mantener la shape key Basis después de aplicar las otras",
        default=True
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
                result = self._process_mesh_shape_keys(mesh_obj)
                total_shape_keys_applied += result['applied']
                if result['applied'] > 0:
                    processed_meshes.append(mesh_obj.name)
            
            # Reportar resultados
            if total_shape_keys_applied > 0:
                mesh_list = ", ".join(processed_meshes)
                self.report({'INFO'}, 
                           f"Aplicadas {total_shape_keys_applied} shape keys en {len(processed_meshes)} meshes: {mesh_list}")
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
    
    def _process_mesh_shape_keys(self, mesh_obj):
        """Procesa las shape keys de un mesh individual"""
        result = {'applied': 0, 'errors': []}
        
        # Verificar si el mesh tiene shape keys
        if not mesh_obj.data.shape_keys or not mesh_obj.data.shape_keys.key_blocks:
            print(f"[SHAPE_KEYS] {mesh_obj.name} no tiene shape keys")
            return result
        
        print(f"[SHAPE_KEYS] Procesando {mesh_obj.name}")
        
        # Obtener lista de shape keys
        key_blocks = mesh_obj.data.shape_keys.key_blocks
        shape_key_names = [key.name for key in key_blocks]
        
        print(f"[SHAPE_KEYS] Shape keys encontradas: {shape_key_names}")
        
        # Activar el mesh
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='OBJECT')
        
        try:
            # Aplicar shape keys según configuración
            if self.apply_with_modifier:
                applied = self._apply_shape_keys_with_modifier(mesh_obj)
            else:
                applied = self._apply_shape_keys_standard(mesh_obj)
            
            result['applied'] = applied
            
        except Exception as e:
            error_msg = f"Error en {mesh_obj.name}: {str(e)}"
            result['errors'].append(error_msg)
            print(f"[SHAPE_KEYS] {error_msg}")
        
        return result
    
    def _apply_shape_keys_standard(self, mesh_obj):
        """Aplica shape keys usando el método estándar de Blender"""
        applied_count = 0
        
        # Verificar shape keys
        if not mesh_obj.data.shape_keys:
            return applied_count
        
        key_blocks = mesh_obj.data.shape_keys.key_blocks
        
        # Crear lista de shape keys a aplicar (excluyendo Basis si se preserva)
        shape_keys_to_apply = []
        
        for key_block in key_blocks:
            if key_block.name == "Basis" and self.preserve_basis:
                continue
            
            # Solo aplicar shape keys que tengan valor > 0
            if key_block.value > 0.0:
                shape_keys_to_apply.append(key_block)
        
        if not shape_keys_to_apply:
            print(f"[SHAPE_KEYS] {mesh_obj.name}: No hay shape keys activas para aplicar")
            return applied_count
        
        print(f"[SHAPE_KEYS] {mesh_obj.name}: Aplicando {len(shape_keys_to_apply)} shape keys")
        
        # Aplicar cada shape key de arriba hacia abajo
        for key_block in reversed(shape_keys_to_apply):
            try:
                # Seleccionar la shape key
                mesh_obj.active_shape_key_index = self._get_shape_key_index(mesh_obj, key_block.name)
                
                # Aplicar la shape key como mix
                bpy.ops.object.shape_key_remove(all=False)
                applied_count += 1
                
                print(f"[SHAPE_KEYS] Aplicada shape key: {key_block.name}")
                
            except Exception as e:
                print(f"[SHAPE_KEYS] Error aplicando {key_block.name}: {e}")
        
        return applied_count
    
    def _apply_shape_keys_with_modifier(self, mesh_obj):
        """Aplica shape keys junto con modificadores armature"""
        applied_count = 0
        
        # Verificar que tenga shape keys
        if not mesh_obj.data.shape_keys:
            return applied_count
        
        # Crear una copia temporal para hacer la aplicación
        bpy.ops.object.select_all(action='DESELECT')
        mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = mesh_obj
        
        # Duplicar el objeto
        bpy.ops.object.duplicate()
        temp_obj = bpy.context.active_object
        temp_obj.name = f"{mesh_obj.name}_temp_shape_keys"
        
        try:
            # Aplicar todas las shape keys en el objeto temporal
            if temp_obj.data.shape_keys:
                key_blocks = temp_obj.data.shape_keys.key_blocks
                
                for key_block in key_blocks:
                    if key_block.name == "Basis" and self.preserve_basis:
                        continue
                    
                    if key_block.value > 0.0:
                        # Establecer la shape key como activa
                        temp_obj.active_shape_key_index = self._get_shape_key_index(temp_obj, key_block.name)
                        
                        # Aplicar shape key
                        bpy.ops.object.shape_key_remove(all=False)
                        applied_count += 1
                        
                        print(f"[SHAPE_KEYS] Aplicada shape key con modifier: {key_block.name}")
            
            # Aplicar modificadores si existen
            for modifier in temp_obj.modifiers:
                if modifier.type == 'ARMATURE':
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                    print(f"[SHAPE_KEYS] Aplicado modificador: {modifier.name}")
            
            # Transferir la geometría de vuelta al objeto original
            self._transfer_mesh_data(temp_obj, mesh_obj)
            
        finally:
            # Limpiar objeto temporal
            bpy.data.objects.remove(temp_obj, do_unlink=True)
        
        return applied_count
    
    def _get_shape_key_index(self, obj, shape_key_name):
        """Obtiene el índice de una shape key por nombre"""
        if not obj.data.shape_keys:
            return -1
        
        for i, key_block in enumerate(obj.data.shape_keys.key_blocks):
            if key_block.name == shape_key_name:
                return i
        
        return -1
    
    def _transfer_mesh_data(self, source_obj, target_obj):
        """Transfiere datos de mesh de un objeto a otro"""
        # Crear nuevo mesh data desde el source
        new_mesh = source_obj.data.copy()
        
        # Reemplazar mesh data del target
        old_mesh = target_obj.data
        target_obj.data = new_mesh
        
        # Limpiar mesh data antiguo
        bpy.data.meshes.remove(old_mesh)
        
        print(f"[SHAPE_KEYS] Datos de mesh transferidos a {target_obj.name}")


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
        print("SHAPE KEYS ENCONTRADAS")
        print("="*50)
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.parent == source_armature:
                if obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) > 1:
                    meshes_with_shape_keys += 1
                    print(f"\nMesh: {obj.name}")
                    
                    for i, key_block in enumerate(obj.data.shape_keys.key_blocks):
                        value_str = f"(valor: {key_block.value:.2f})" if key_block.value > 0 else ""
                        print(f"  {i}: {key_block.name} {value_str}")
                        total_shape_keys += 1
                else:
                    print(f"\nMesh: {obj.name} - Sin shape keys")
        
        print("\n" + "="*50)
        print(f"RESUMEN: {total_shape_keys} shape keys en {meshes_with_shape_keys} meshes")
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