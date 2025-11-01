import bpy  # type: ignore


def clean_vertex_colors_for_source(settings=None):
    """Preserva o elimina vertex colors/color attributes en las mallas hijas del source_armature.

    - settings: objeto de configuración (scene.universal_gta_settings). Si es None, se toma de la escena.
    - Retorna tuple (changed: bool, message: str)
    """
    try:
        if settings is None:
            settings = getattr(bpy.context.scene, 'universal_gta_settings', None)
        if settings is None:
            return False, "No settings"

        preserve_flag = getattr(settings, 'preserve_vertex_data', None)
        if preserve_flag is None:
            preserve_flag = getattr(settings, 'keep_vertex_colors', False)

        # Si preserve activo, no hacemos nada
        if preserve_flag:
            return False, "Preserve active"

        source_arm = getattr(settings, 'source_armature', None)
        if not source_arm:
            return False, "No source_armature"

        cleaned_any = False
        children = getattr(source_arm, 'children_recursive', source_arm.children)
        for child in children:
            if not child or child.type != 'MESH':
                continue
            mesh = child.data
            if not mesh:
                continue

            removed = False
            # color_attributes API
            if hasattr(mesh, 'color_attributes') and len(mesh.color_attributes) > 0:
                # eliminar desde el índice 0 hasta acabar
                while len(mesh.color_attributes) > 0:
                    try:
                        mesh.color_attributes.remove(mesh.color_attributes[0])
                        removed = True
                    except Exception:
                        break

            # legacy vertex_colors
            if hasattr(mesh, 'vertex_colors') and len(mesh.vertex_colors) > 0:
                while len(mesh.vertex_colors) > 0:
                    try:
                        mesh.vertex_colors.remove(mesh.vertex_colors[0])
                        removed = True
                    except Exception:
                        break

            if removed:
                cleaned_any = True

        if cleaned_any:
            return True, "Vertex colors removed"
        return False, "No vertex colors found"

    except Exception as e:
        return False, f"Error: {e}"
