# -*- coding: utf-8 -*-
"""
GTA Conversion Utils - Enhanced & Refactored Edition

Utilidades profesionales y refactorizadas para la conversión de modelos
de GTA San Andreas. Este script consolida la lógica duplicada, mejora la
robustez y sigue las mejores prácticas para el scripting en Blender.
"""

import bpy
from typing import List, Optional, Set

class GTAConversionUtils:
    """
    Clase de utilidades para automatizar y limpiar la conversión de modelos
    para GTA:SA dentro de Blender.
    """
    
    # --- Constantes para nombres comunes y patrones ---
    
    # Nombres de objetos objetivo
    TARGET_MESH_NAME: str = "Mesh"
    TARGET_ROOT_NAME: str = "Root"
    TARGET_ARMATURE_MODIFIER_NAME: str = "GTA_SA_SKIN"
    
    # Nombres de datos
    UV_MAP_NAME: str = "Float2"
    
    # Patrones para identificar objetos/mallas problemáticos a eliminar
    PROBLEMATIC_PATTERNS: Set[str] = {
        'unnamed', 'Unnamed', 'UNNAMED', 
        'temp', 'Temp', 'TEMP', 
        'Empty', 'empty'
    }

    def __init__(self, debug: bool = True):
        """
        Inicializa las utilidades de conversión.

        Args:
            debug (bool): Si es True, imprimirá logs detallados en la consola.
        """
        self.debug = debug
        self.log("GTA Conversion Utils inicializado.")

    def log(self, message: str, level: str = "INFO") -> None:
        """
        Imprime un mensaje en la consola si el modo debug está activado.

        Args:
            message (str): El mensaje a mostrar.
            level (str): El nivel del log (e.g., INFO, WARNING, ERROR).
        """
        if self.debug:
            print(f"[GTA_UTILS] [{level}] {message}")

    # --- Métodos Principales de Flujo de Trabajo (Workflow) ---

    def auto_cleanup_post_conversion(self, settings, target_armature: bpy.types.Object) -> bool:
        """
        Ejecuta una secuencia completa de limpieza automática post-conversión.
        Esta es la función principal que orquesta toda la limpieza.

        Args:
            settings: Los ajustes de la escena del addon (e.g., bpy.context.scene.universal_gta_settings).
            target_armature (bpy.types.Object): El armature principal del modelo.

        Returns:
            bool: True si se realizó alguna acción de limpieza, False en caso contrario.
        """
        self.log("🧹 Iniciando limpieza automática post-conversión completa...")
        cleanup_performed = False

        # 1. Limpiar padre problemático del armature y asegurar jerarquía correcta.
        if self._cleanup_and_reparent_target_armature(target_armature):
            cleanup_performed = True

        # 2. Eliminar mallas residuales con nombres problemáticos.
        if self.clean_problematic_meshes():
            cleanup_performed = True

        # 3. Eliminar datos de vértices si el usuario no desea conservarlos.
        preserve_vdata = getattr(settings, 'universalgta_preserve_vertex_data', False)
        if not preserve_vdata:
            if self.remove_vertex_colors():
                cleanup_performed = True
            if self.apply_and_remove_shape_keys():
                cleanup_performed = True
        else:
            self.log("ℹ️ Colores de vértice y Shape Keys preservados por preferencia del usuario.")

        # 4. Forzar jerarquía final para máxima compatibilidad.
        if self._force_final_hierarchy(target_armature):
             cleanup_performed = True
             
        # 5. Purgar datos huérfanos de la escena.
        if self.cleanup_orphaned_data():
            cleanup_performed = True

        if cleanup_performed:
            self.log("🎉 Limpieza automática post-conversión completada exitosamente.")
        else:
            self.log("ℹ️ No se requirió ninguna limpieza adicional.")
            
        return cleanup_performed

    def auto_cleanup_post_conversion_with_parent(self, settings, target_armature: bpy.types.Object) -> bool:
        """
        Convierte la malla principal a geometría visual y purga datos huérfanos.
        Este proceso aplica todos los modificadores a la malla 'Mesh'.

        Returns:
            bool: True si la limpieza y conversión se realizaron exitosamente.
        """
        self.log("🧹 Iniciando limpieza post-conversión con conversión de malla...")
        
        mesh_obj = bpy.data.objects.get(self.TARGET_MESH_NAME)
        if not mesh_obj or mesh_obj.type != 'MESH':
            self.log(f"❌ No se encontró la malla principal '{self.TARGET_MESH_NAME}' para la conversión.", "ERROR")
            return False

        # Guardar estado de selección
        original_active = bpy.context.view_layer.objects.active
        original_selected = bpy.context.selected_objects[:]
        
        try:
            # Para la operación 'convert', el objeto debe estar seleccionado y activo
            bpy.ops.object.select_all(action='DESELECT')
            mesh_obj.select_set(True)
            bpy.context.view_layer.objects.active = mesh_obj
            
            self.log(f"Convirtiendo '{mesh_obj.name}' a malla (Visual Geometry to Mesh)...")
            bpy.ops.object.convert(target='MESH')
            self.log("✅ Malla convertida (modificadores aplicados).")

        except Exception as e:
            self.log(f"❌ Error al convertir la malla: {e}", "ERROR")
            return False
        finally:
            # Restaurar selección original
            bpy.ops.object.select_all(action='DESELECT')
            for obj in original_selected:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = original_active

        # Purgar datos huérfanos 3 veces para una limpieza profunda
        self.log("Purgando datos huérfanos (3 pasadas)...")
        for i in range(3):
            self.log(f"  -> Pasada de purga {i + 1}/3")
            if self.cleanup_orphaned_data():
                self.log("    ... purga completada.")
            else:
                self.log("    ... no se pudo purgar o no había nada que purgar.")
        
        self.log("🎉 Limpieza con conversión de malla completada.")
        return True

    # --- Métodos de Limpieza y Procesamiento de Geometría ---

    def clean_problematic_meshes(self) -> bool:
        """
        Busca y elimina todas las mallas cuyos nombres coincidan con los patrones
        problemáticos definidos en PROBLEMATIC_PATTERNS.
        Se asegura de reparentar los hijos de los objetos eliminados.
        """
        self.log("Buscando y eliminando mallas problemáticas...")
        cleaned_count = 0
        
        # Iterar sobre una copia de la lista para poder eliminar objetos de forma segura
        for obj in bpy.data.objects[:]:
            if obj.type == 'MESH' and any(pattern in obj.name for pattern in self.PROBLEMATIC_PATTERNS):
                obj_name = obj.name
                self.log(f"Encontrado objeto problemático para eliminar: {obj_name}")
                
                # Liberar a los hijos antes de eliminar el padre
                for child in obj.children:
                    child.parent = None
                    self.log(f"  -> Reparentado hijo: {child.name}")
                    
                try:
                    bpy.data.objects.remove(obj, do_unlink=True)
                    self.log(f"✅ Malla problemática '{obj_name}' eliminada.")
                    cleaned_count += 1
                except Exception as e:
                    self.log(f"❌ Error al eliminar la malla '{obj_name}': {e}", "ERROR")
        
        if cleaned_count > 0:
            self.log(f"Total de mallas problemáticas eliminadas: {cleaned_count}")
        return cleaned_count > 0

    def remove_vertex_colors(self) -> bool:
        """
        Elimina de forma segura todos los 'Color Attributes' (Blender 3.2+) y
        'Vertex Colors' (legacy) de todas las mallas en la escena.
        """
        self.log("Eliminando colores de vértice (Vertex Colors)...")
        removed_count = 0
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.data:
                # API moderna (Blender 3.2+)
                if hasattr(obj.data, 'color_attributes') and obj.data.color_attributes:
                    for attr in list(obj.data.color_attributes):
                        obj.data.color_attributes.remove(attr)
                        removed_count += 1
                
                # API antigua (legacy)
                if hasattr(obj.data, 'vertex_colors') and obj.data.vertex_colors:
                    while obj.data.vertex_colors:
                        obj.data.vertex_colors.remove(obj.data.vertex_colors[0])
                        removed_count += 1
        
        if removed_count > 0:
            self.log(f"✅ Atributos de color eliminados de los objetos.")
        return removed_count > 0

    def apply_and_remove_shape_keys(self) -> bool:
        """
        Aplica el estado mixto actual de los Shape Keys y los elimina de todas
        las mallas que los contengan.
        """
        self.log("Aplicando y eliminando Shape Keys...")
        processed_count = 0
        
        # Guardar objeto activo original
        original_active = bpy.context.view_layer.objects.active
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.data and obj.data.shape_keys:
                try:
                    # La operación requiere que el objeto sea el activo
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
                    self.log(f"✅ Shape Keys procesados en: {obj.name}")
                    processed_count += 1
                except Exception as e:
                    self.log(f"⚠️ No se pudieron procesar Shape Keys en '{obj.name}': {e}", "WARNING")
                finally:
                    # Restaurar el objeto activo original
                    bpy.context.view_layer.objects.active = original_active
        
        return processed_count > 0
        
    def cleanup_orphaned_data(self) -> bool:
        """
        Ejecuta el operador de Blender para purgar todos los bloques de datos
        huérfanos (no utilizados) de forma recursiva.
        """
        self.log("Limpiando datos huérfanos (Orphan Data)...")
        try:
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
            self.log("✅ Datos huérfanos purgados.")
            return True
        except Exception as e:
            self.log(f"❌ No se pudo purgar datos huérfanos: {e}", "ERROR")
            return False

    # --- Métodos de Jerarquía y Estructura de Objetos ---

    def _cleanup_and_reparent_target_armature(self, target_armature: bpy.types.Object) -> bool:
        """
        (Helper privado) Gestiona el padre del armature. Si es un objeto problemático,
        lo elimina. Si es una malla válida, asegura la jerarquía correcta.
        """
        parent_obj = target_armature.parent
        if not parent_obj:
            self.log("Armature no tiene padre. Se intentará establecer jerarquía con la malla principal.")
            return self._establish_mesh_armature_hierarchy(target_armature)

        is_problematic = any(pattern in parent_obj.name for pattern in self.PROBLEMATIC_PATTERNS)
        
        # Si el padre es una malla con vértices, es una malla importante. ¡No borrar!
        if parent_obj.type == 'MESH' and parent_obj.data and len(parent_obj.data.vertices) > 0:
            self.log(f"🛡️ Padre '{parent_obj.name}' es una malla importante. Se preservará la jerarquía.")
            return self._establish_mesh_armature_hierarchy(target_armature, parent_obj)

        if not is_problematic:
            self.log(f"ℹ️ Padre '{parent_obj.name}' no parece problemático. Se intentará re-jerarquizar.")
            return self._establish_mesh_armature_hierarchy(target_armature)

        # Si llegamos aquí, el padre es problemático y debe ser eliminado.
        self.log(f"🗑️ Eliminando objeto padre problemático: {parent_obj.name} ({parent_obj.type})")
        try:
            # Liberar al armature y otros hijos
            target_armature.parent = None
            for child in parent_obj.children:
                child.parent = None
            
            # Eliminar el objeto padre
            bpy.data.objects.remove(parent_obj, do_unlink=True)
            self.log(f"✅ Objeto padre problemático '{parent_obj.name}' eliminado.")
            
            # Intentar establecer la jerarquía correcta después de la eliminación
            return self._establish_mesh_armature_hierarchy(target_armature)
        except Exception as e:
            self.log(f"❌ Error eliminando objeto padre '{parent_obj.name}': {e}", "ERROR")
            return False

    def _establish_mesh_armature_hierarchy(self, armature_obj: bpy.types.Object, mesh_obj: Optional[bpy.types.Object] = None) -> bool:
        """
        (Helper privado) Establece la jerarquía correcta: Mesh (Padre) -> Armature (Hijo).
        Si no se proporciona una malla, la busca automáticamente.
        """
        if not mesh_obj:
            mesh_obj = bpy.data.objects.get(self.TARGET_MESH_NAME)

        if not mesh_obj or mesh_obj.type != 'MESH':
            self.log(f"❌ No se encontró la malla principal '{self.TARGET_MESH_NAME}' para establecer la jerarquía.", "ERROR")
            return False
        
        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.log("❌ No se proporcionó un armature válido.", "ERROR")
            return False

        # Desvincular el armature de cualquier padre anterior y resetear su matriz
        armature_obj.parent = None
        armature_obj.matrix_parent_inverse.identity()
        
        # Establecer la nueva jerarquía
        armature_obj.parent = mesh_obj
        armature_obj.parent_type = 'OBJECT'
        
        self.log(f"✅ Jerarquía establecida: {mesh_obj.name} (Padre) -> {armature_obj.name} (Hijo)")
        return True

    def _force_final_hierarchy(self, target_armature: bpy.types.Object) -> bool:
        """
        (Helper privado) Como último recurso, asegura que solo haya un armature (el target)
        y que sea hijo de la malla principal.
        """
        self.log("🔧 Forzando jerarquía final y limpiando armatures extra...")
        
        main_mesh = bpy.data.objects.get(self.TARGET_MESH_NAME)
        if not main_mesh:
            self.log(f"No se encontró la malla '{self.TARGET_MESH_NAME}' para forzar jerarquía.", "WARNING")
            return False

        armatures_in_scene = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
        
        # Eliminar cualquier armature que no sea el principal
        for arm in armatures_in_scene:
            if arm != target_armature:
                self.log(f"Eliminando armature extra: {arm.name}")
                bpy.data.objects.remove(arm, do_unlink=True)
        
        # Forzar la jerarquía
        return self._establish_mesh_armature_hierarchy(target_armature, main_mesh)

    # --- Métodos de Configuración Específica de Datos ---

    def process_uv_maps(self) -> bool:
        """
        Recorre todas las mallas y renombra la primera capa de UV a 'Float2',
        que es el nombre requerido por algunas herramientas de GTA.
        """
        self.log("Procesando y renombrando UV Maps...")
        processed_count = 0
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.data and obj.data.uv_layers:
                uv_layer = obj.data.uv_layers[0]
                if uv_layer.name != self.UV_MAP_NAME:
                    self.log(f"Renombrando UV Map en '{obj.name}': '{uv_layer.name}' -> '{self.UV_MAP_NAME}'")
                    uv_layer.name = self.UV_MAP_NAME
                    processed_count += 1
        
        if processed_count > 0:
            self.log(f"✅ {processed_count} UV Maps han sido renombrados a '{self.UV_MAP_NAME}'.")
        return processed_count > 0
        
    def ensure_single_armature_modifier(self, mesh_obj: bpy.types.Object, target_armature: bpy.types.Object) -> bool:
        """
        Asegura que la malla principal tenga exactamente un modificador de tipo
        'ARMATURE', vinculado al armature correcto y con el nombre estándar.
        """
        self.log(f"Asegurando modificador Armature único en: {mesh_obj.name}")
        
        # Eliminar todos los modificadores de armature existentes
        for mod in mesh_obj.modifiers[:]:
            if mod.type == 'ARMATURE':
                mesh_obj.modifiers.remove(mod)

        # Crear el modificador nuevo y configurado
        mod = mesh_obj.modifiers.new(name=self.TARGET_ARMATURE_MODIFIER_NAME, type='ARMATURE')
        mod.object = target_armature
        mod.use_vertex_groups = True
        
        self.log(f"✅ Modificador '{self.TARGET_ARMATURE_MODIFIER_NAME}' creado y vinculado a '{target_armature.name}'.")
        return True