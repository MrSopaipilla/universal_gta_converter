"""Operadores de exportación."""

import bpy  # type: ignore
import os
import shutil
from bpy.types import Operator  # type: ignore
from bpy.props import StringProperty  # type: ignore


class UNIVERSALGTA_OT_export_textures(Operator):
    """Exportar todas las texturas utilizadas en el modelo"""
    bl_idname = "universalgta.export_textures"
    bl_label = "Export Textures"
    bl_description = "Export all textures used in the model"
    
    directory: StringProperty(subtype="DIR_PATH")
    
    def execute(self, context):
        if not self.directory:
            self.report({'ERROR'}, "No se seleccionó directorio de destino.")
            return {'CANCELLED'}
        
        exported_count = 0
        
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        image = node.image
                        if image.filepath:
                            source_path = bpy.path.abspath(image.filepath)
                            if os.path.exists(source_path):
                                filename = os.path.basename(source_path)
                                dest_path = os.path.join(self.directory, filename)
                                try:
                                    shutil.copy2(source_path, dest_path)
                                    exported_count += 1
                                except Exception as e:
                                    print(f"Error copiando {source_path}: {e}")
        
        self.report({'INFO'}, f"Exportadas {exported_count} texturas a {self.directory}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(UNIVERSALGTA_OT_export_textures)


def unregister():
    bpy.utils.unregister_class(UNIVERSALGTA_OT_export_textures)


if __name__ == "__main__":
    register()
