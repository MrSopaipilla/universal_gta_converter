"""Operadores de texturas: baking y exportación."""

import bpy
import os
import bmesh
from bpy.types import Operator, PropertyGroup
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    IntProperty,
    PointerProperty,
)
from bpy_extras.io_utils import ExportHelper
from mathutils import Color, Vector
from mathutils import Color, Vector


FORMAT_EXTENSION_MAP = {
    'PNG': '.png',
    'JPEG': '.jpg',
    'JPEG2000': '.jp2',
    'TARGA': '.tga',
    'TARGA_RAW': '.tga',
    'BMP': '.bmp',
    'TIFF': '.tif',
    'OPEN_EXR': '.exr',
    'OPEN_EXR_MULTILAYER': '.exr',
    'HDR': '.hdr',
    'WEBP': '.webp',
    'DDS': '.dds',
    'CINEON': '.cin',
    'DPX': '.dpx',
    'IRIS': '.rgb',
}

FORCED_FORMAT_ITEMS = [
    ('PNG', "PNG", "Guardar como PNG"),
    ('JPEG', "JPEG", "Guardar como JPEG (comprimido)"),
    ('TIFF', "TIFF", "Guardar como TIFF (sin pérdida)"),
    ('OPEN_EXR', "OpenEXR", "Guardar como OpenEXR (alto rango dinámico)"),
    ('TARGA', "TGA", "Guardar como TGA"),
    ('BMP', "BMP", "Guardar como BMP"),
    ('HDR', "HDR", "Guardar como HDR (rango dinámico alto)"),
]

EXPORT_MODE_ITEMS = [
    ('ALL', "Todas las Texturas", "Exportar todas las texturas del proyecto", 'MATERIAL', 0),
    ('SELECTED', "Solo del Objeto Seleccionado", "Exportar solo las texturas del objeto seleccionado", 'RESTRICT_SELECT_OFF', 1),
]

SUFFIXES_TO_REMOVE = ['_png', '_jpg', '_jpeg', '_tga', '_bmp', '_tiff', '_exr', '_hdr']


def get_extension_for_format(file_format: str) -> str:
    return FORMAT_EXTENSION_MAP.get(file_format, '.png')


class TextureExporterProperties(PropertyGroup):
    export_path: StringProperty(
        name="Carpeta de Exportación",
        description="Selecciona la carpeta donde guardar las texturas",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    export_mode: EnumProperty(
        name="Modo de Exportación",
        description="Selecciona qué texturas exportar",
        items=EXPORT_MODE_ITEMS,
        default='ALL'
    )

    force_format_enabled: BoolProperty(
        name="Forzar formato",
        description="Exportar todas las texturas en un formato específico",
        default=False
    )

    forced_format: EnumProperty(
        name="Formato objetivo",
        description="Formato final para todas las texturas exportadas",
        items=FORCED_FORMAT_ITEMS,
        default='PNG'
    )


def _get_texture_exporter_props(context):
    return getattr(context.scene, "texture_exporter_props", None)


def _collect_images_to_export(context, export_mode):
    images_to_export = set()

    if export_mode == 'ALL':
        images_to_export = set(bpy.data.images)
    elif export_mode == 'SELECTED':
        selected_objects = list(context.selected_objects) if hasattr(context, 'selected_objects') else []
        if not selected_objects:
            return None, "No hay ningún objeto seleccionado"

        found_any_materials = False
        for obj in selected_objects:
            if not hasattr(obj, 'data') or not hasattr(obj.data, 'materials') or not obj.data.materials:
                continue
            found_any_materials = True
            for material_slot in obj.material_slots:
                if material_slot.material and material_slot.material.use_nodes:
                    for node in material_slot.material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                            images_to_export.add(node.image)
                            print(f"📷 Encontrada textura: {node.image.name} en objeto {obj.name}, material {material_slot.material.name}")

        if not found_any_materials:
            return None, "Los objetos seleccionados no tienen materiales"

    return images_to_export, None


def _normalize_export_path(path: str) -> str:
    return os.path.abspath(os.path.normpath(os.path.expanduser(path)))


def _describe_export_mode(context, export_mode):
    if export_mode == 'ALL':
        return "todas las texturas"
    num_sel = len(context.selected_objects) if hasattr(context, 'selected_objects') else (1 if context.active_object else 0)
    return f"texturas de la selección ({num_sel} objeto(s))"


def _export_images(images_to_export, export_path, force_format_enabled, forced_format):
    exported = []
    failed = []

    for image in images_to_export:
        if not image or not getattr(image, "size", None):
            failed.append(getattr(image, "name", "desconocida"))
            continue

        if image.size[0] <= 0 or image.size[1] <= 0:
            print(f"⚠️ Imagen no válida para exportar: {image.name}")
            failed.append(image.name)
            continue

        image_name = bpy.path.clean_name(image.name)
        name_without_ext = os.path.splitext(image_name)[0]

        for suffix in SUFFIXES_TO_REMOVE:
            if name_without_ext.lower().endswith(suffix):
                name_without_ext = name_without_ext[:-len(suffix)]
                break

        original_format_setting = getattr(image, 'file_format', None) or 'PNG'
        target_format = forced_format if force_format_enabled and forced_format else original_format_setting or 'PNG'
        extension = get_extension_for_format(target_format)
        image_name = name_without_ext + extension
        export_file = os.path.join(export_path, image_name)

        try:
            original_filepath = image.filepath_raw
            previous_format_setting = getattr(image, 'file_format', None)

            image.use_fake_user = True
            image.filepath_raw = export_file
            image.file_format = target_format
            image.save()

            image.filepath_raw = original_filepath
            if previous_format_setting is not None:
                image.file_format = previous_format_setting

            print(f"✅ Exportada: {export_file}")
            exported.append(image_name)
        except Exception as e:
            print(f"❌ Error exportando {image.name}: {e}")
            failed.append(image.name)
            image.filepath_raw = original_filepath
            if previous_format_setting is not None:
                image.file_format = previous_format_setting

    return exported, failed


def _report_export_summary(operator, context, exported, failed, export_mode, force_format_enabled, forced_format):
    mode_text = _describe_export_mode(context, export_mode)
    format_suffix = f" • Formato: {forced_format}" if force_format_enabled else ""

    if exported:
        operator.report({'INFO'}, f"Exportadas {len(exported)} {mode_text} exitosamente (sin pérdida de color){format_suffix}")
    else:
        operator.report({'WARNING'}, f"No se pudo exportar ninguna textura de {mode_text}{format_suffix}")

    if failed:
        operator.report({'WARNING'}, f"{len(failed)} texturas fallaron al exportar")

    print(f"\n📁 Exportación terminada ({mode_text}).")
    print(f"Total exportadas: {len(exported)}")
    print(f"No exportadas: {len(failed)}")
    if force_format_enabled:
        print(f"Formato final aplicado: {forced_format}")
    if failed:
        print("Estas no se exportaron:")
        for name in failed:
            print(f" - {name}")


def get_original_texture_resolution(material):
    """
    AVANZADO: Detectar resolución original de texturas en el material
    Busca en todos los nodos Image Texture del material
    """
    try:
        if not material or not material.use_nodes:
            return 1024  # Default fallback
        
        nodes = material.node_tree.nodes
        max_resolution = 512  # Mínimo GTA-compatible
        
        for node in nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                width, height = node.image.size
                if width > 0 and height > 0:
                    # Usar la dimensión mayor
                    current_res = max(width, height)
                    max_resolution = max(max_resolution, current_res)
                    print(f"🔍 Textura encontrada: {node.image.name} - {width}x{height}")
        
        # Redondear a potencia de 2 más cercana para optimización
        import math
        final_res = 2 ** round(math.log2(max_resolution))
        final_res = min(final_res, 2048)  # Limitar a 2K max
        
        print(f"✅ Resolución detectada: {final_res}x{final_res}")
        return final_res
        
    except Exception as e:
        print(f"❌ Error detectando resolución: {e}")
        return 1024


def evaluate_material_visual_color(material):
    """
    AVANZADO: Evaluar color visual real del material
    Considera nodos HSV, ColorRamp, MixRGB, etc.
    """
    try:
        if not material or not material.use_nodes:
            return [0.906, 0.906, 0.906, 1.0]
        
        nodes = material.node_tree.nodes
        
        # Buscar Principled BSDF
        principled = None
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled = node
                break
        
        if not principled:
            return [0.906, 0.906, 0.906, 1.0]
        
        base_color_input = principled.inputs['Base Color']
        
        # CASO 1: Sin conexiones - usar valor directo
        if not base_color_input.is_linked:
            color = base_color_input.default_value
            return [color[0], color[1], color[2], color[3]]
        
        # CASO 2: Conexiones complejas - evaluar cadena de nodos
        return evaluate_node_chain_color(base_color_input.links[0].from_node)
        
    except Exception as e:
        print(f"❌ Error evaluando color visual: {e}")
        return [0.906, 0.906, 0.906, 1.0]


def evaluate_node_chain_color(node, visited=None):
    """
    AVANZADO: Evaluar color resultante de cadena de nodos
    Maneja Image Texture + HSV + ColorRamp + MixRGB
    """
    if visited is None:
        visited = set()
    
    if node in visited:
        return [0.906, 0.906, 0.906, 1.0]
    visited.add(node)
    
    try:
        # CASE: Image Texture Node
        if node.type == 'TEX_IMAGE' and node.image:
            return sample_image_color(node.image)
        
        # CASE: HSV (Hue Saturation Value) Node
        elif node.type == 'HUE_SAT':
            # Evaluar input Color recursivamente
            color_input = node.inputs['Color']
            if color_input.is_linked:
                base_color = evaluate_node_chain_color(color_input.links[0].from_node, visited)
            else:
                base_color = [1.0, 1.0, 1.0, 1.0]
            
            # Aplicar transformaciones HSV
            hue = node.inputs['Hue'].default_value
            saturation = node.inputs['Saturation'].default_value
            value = node.inputs['Value'].default_value
            
            return apply_hsv_transform(base_color, hue, saturation, value)
        
        # CASE: ColorRamp Node
        elif node.type == 'VALTORGB':
            # Evaluar input Fac
            fac_input = node.inputs['Fac']
            if fac_input.is_linked:
                fac_node = fac_input.links[0].from_node
                # Para simplificar, usar valor medio del ColorRamp
                color_ramp = node.color_ramp
                if len(color_ramp.elements) > 0:
                    mid_element = color_ramp.elements[len(color_ramp.elements) // 2]
                    return [mid_element.color[0], mid_element.color[1], mid_element.color[2], mid_element.color[3]]
            
            return [0.5, 0.5, 0.5, 1.0]
        
        # CASE: Mix RGB Node
        elif node.type == 'MIX_RGB' or node.type == 'MIX':
            # Evaluar ambos inputs y hacer mix simple
            color1_input = node.inputs['Color1'] if 'Color1' in node.inputs else node.inputs[1]
            color2_input = node.inputs['Color2'] if 'Color2' in node.inputs else node.inputs[2]
            
            color1 = [0.5, 0.5, 0.5, 1.0]
            color2 = [0.5, 0.5, 0.5, 1.0]
            
            if color1_input.is_linked:
                color1 = evaluate_node_chain_color(color1_input.links[0].from_node, visited)
            else:
                color1 = color1_input.default_value[:4]
            
            if color2_input.is_linked:
                color2 = evaluate_node_chain_color(color2_input.links[0].from_node, visited)
            else:
                color2 = color2_input.default_value[:4]
            
            # Mix simple (50/50)
            return [(color1[i] + color2[i]) / 2 for i in range(4)]
        
        # CASE: Otros nodos - valor por defecto
        else:
            if 'Color' in node.outputs:
                return [0.906, 0.906, 0.906, 1.0]
            elif 'Value' in node.outputs:
                val = 0.906
                return [val, val, val, 1.0]
        
    except Exception as e:
        print(f"❌ Error evaluando nodo {node.type}: {e}")
    
    return [0.906, 0.906, 0.906, 1.0]


def sample_image_color(image, sample_count=16):
    """
    AVANZADO: Samplear color promedio de imagen de forma inteligente
    Toma múltiples puntos para obtener color representativo
    """
    try:
        if not image.pixels or len(image.pixels) == 0:
            return [0.906, 0.906, 0.906, 1.0]
        
        width, height = image.size
        if width <= 0 or height <= 0:
            return [0.906, 0.906, 0.906, 1.0]
        
        # Samplear múltiples puntos de la imagen
        sample_points = []
        step = max(1, min(width, height) // 4)  # Dividir en una grilla 4x4
        
        for y in range(step, height - step, step):
            for x in range(step, width - step, step):
                pixel_index = (y * width + x) * 4
                if pixel_index + 3 < len(image.pixels):
                    r = image.pixels[pixel_index]
                    g = image.pixels[pixel_index + 1]
                    b = image.pixels[pixel_index + 2]
                    a = image.pixels[pixel_index + 3]
                    sample_points.append([r, g, b, a])
        
        if not sample_points:
            # Fallback: usar píxel central
            center_x, center_y = width // 2, height // 2
            pixel_index = (center_y * width + center_x) * 4
            if pixel_index + 3 < len(image.pixels):
                return [
                    image.pixels[pixel_index],
                    image.pixels[pixel_index + 1], 
                    image.pixels[pixel_index + 2],
                    image.pixels[pixel_index + 3]
                ]
        
        # Promedio de todos los samples
        avg_color = [0, 0, 0, 0]
        for sample in sample_points:
            for i in range(4):
                avg_color[i] += sample[i]
        
        for i in range(4):
            avg_color[i] /= len(sample_points)
        
        print(f"✅ Color sampled: RGB({avg_color[0]:.3f}, {avg_color[1]:.3f}, {avg_color[2]:.3f})")
        return avg_color
        
    except Exception as e:
        print(f"❌ Error sampleando imagen: {e}")
        return [0.906, 0.906, 0.906, 1.0]


def apply_hsv_transform(base_color, hue, saturation, value):
    """
    AVANZADO: Aplicar transformación HSV a color base
    """
    try:
        # Convertir RGB a HSV
        color = Color(base_color[:3])
        h, s, v = color.hsv
        
        # Aplicar transformaciones
        h = (h + hue) % 1.0  # Hue es cíclico
        s = max(0, min(1, s + saturation))  # Saturación clamped
        v = max(0, min(1, v * value))  # Value como multiplicador
        
        # Convertir de vuelta a RGB
        color.hsv = (h, s, v)
        
        return [color.r, color.g, color.b, base_color[3]]
        
    except Exception as e:
        print(f"❌ Error aplicando HSV: {e}")
        return base_color


def _is_image_basically_white_or_empty(image):
    """Checks if an image is completely white, transparent, or empty."""
    try:
        if not image.pixels or len(image.pixels) == 0:
            return True
        
        # Samplear el centro y algunas esquinas para ser rápido
        width, height = image.size
        # Indices de sampleo: centro y esquinas
        indices = [
            0, # esq inf izq
            (width - 1) * 4, # esq inf der
            (height - 1) * width * 4, # esq sup izq
            (width * height - 1) * 4, # esq sup der
            ((height // 2) * width + (width // 2)) * 4 # centro
        ]
        
        is_all_white = True
        is_all_transparent = True
        
        for idx in indices:
            if idx < len(image.pixels) - 4:
                r = image.pixels[idx]
                g = image.pixels[idx+1]
                b = image.pixels[idx+2]
                a = image.pixels[idx+3]
                
                # Check transparencia (si tiene algo opaco, no es empty)
                if a > 0.05:
                    is_all_transparent = False
                
                # Check blanco (si algo no es blanco puro, no es white)
                if r < 0.95 or g < 0.95 or b < 0.95:
                    is_all_white = False

        if is_all_transparent: return True # Vacio
        if is_all_white: return True # Blanco puro (fallo típico de bake)
        
        return False
    except:
        return True # Asumir fallo si error

def perform_advanced_baking(material, resolution=None):
    """
    AVANZADO: Bake usando estrategia 'EMIT' pura (Guia Manual).
    Conecta Color/MixColor -> Emission -> Output.
    """
    try:
        print(f"🔥 INICIANDO BAKING (EMIT MANUAL): {material.name}")
        
        if resolution is None:
            resolution = get_original_texture_resolution(material)

        obj, slot_index = _find_object_with_material(material)
        if not obj: return None

        # Guardar estado
        original_visibility = {}
        for o in bpy.data.objects:
            original_visibility[o.name] = o.hide_render
        original_auto_smooth = False
        if hasattr(obj.data, "use_auto_smooth"):
            original_auto_smooth = obj.data.use_auto_smooth

        try:
            # Configurar Escena
            if bpy.context.scene.render.engine != 'CYCLES':
                bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.device = 'CPU'
            bpy.context.scene.cycles.samples = 1
            bpy.context.scene.cycles.max_bounces = 0

            # Aislar Objeto
            if bpy.context.object and bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            for o in bpy.data.objects: o.hide_render = True
            obj.hide_render = False
            if hasattr(obj.data, "use_auto_smooth"):
                obj.data.use_auto_smooth = False

            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

            # Sync UVs
            if getattr(obj.data, 'uv_layers', None):
                uv_layers = obj.data.uv_layers
                # Fix API Error: active_render -> render
                if uv_layers.render and uv_layers.active != uv_layers.render:
                    uv_layers.active = uv_layers.render

            # SETUP NODOS (EMISSION STRATEGY)
            nodes = material.node_tree.nodes
            links = material.node_tree.links
            principled = _find_principled(material)
            output_node = _get_output_node(material)

            # Crear Imagen Target
            baked_name = f"{material.name}_r_d"
            if baked_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[baked_name])
            baked_image = bpy.data.images.new(baked_name, width=resolution, height=resolution, alpha=True)

            # Nodo Target
            for n in nodes: n.select = False
            target_node = nodes.new('ShaderNodeTexImage')
            target_node.image = baked_image
            target_node.select = True
            nodes.active = target_node

            # Nodo Emission
            emission = nodes.new('ShaderNodeEmission')
            emission.location = (principled.location.x + 200, principled.location.y + 200)
            
            # Conexión Inteligente (Mix Shader support simple)
            # Si el Principled tiene algo en Base Color, lo usamos.
            base_socket = principled.inputs.get('Base Color')
            input_source = None
            if base_socket and base_socket.is_linked:
                input_source = base_socket.links[0].from_socket
                links.new(input_source, emission.inputs['Color'])
            else:
                default_col = base_socket.default_value if base_socket else [1,1,1,1]
                emission.inputs['Color'].default_value = default_col
            
            # Conectar a Output
            final_surface = output_node.inputs['Surface']
            orig_link_source = None
            if final_surface.is_linked:
                orig_link_source = final_surface.links[0].from_socket
            
            links.new(emission.outputs['Emission'], final_surface)

            # BAKE
            print(f"   ⏳ Bakeando {resolution}x{resolution} (EMIT)...")
            bpy.context.scene.render.bake.use_selected_to_active = False
            bpy.context.scene.render.bake.use_cage = False
            bpy.context.scene.render.bake.margin = 0
            bpy.context.scene.render.bake.use_clear = True
            bpy.context.scene.render.bake.target = 'IMAGE_TEXTURES'
            
            bpy.ops.object.bake(type='EMIT')
            
            # Restaurar Nodos
            nodes.remove(emission)
            nodes.remove(target_node)
            if orig_link_source:
                links.new(orig_link_source, final_surface)
            
            baked_image.pack()
            baked_image.use_fake_user = True
            
            return baked_image

        finally:
            # Restaurar Global
            for n, h in original_visibility.items():
                if n in bpy.data.objects: bpy.data.objects[n].hide_render = h
            if obj and hasattr(obj.data, "use_auto_smooth"):
                obj.data.use_auto_smooth = original_auto_smooth
    except Exception as e:
        print(f"❌ Error Bake: {e}")
        return None


def replace_material_with_baked(material, baked_image):
    """
    AVANZADO: Reemplazar material complejo con textura baked
    Conserva Alpha original si existe
    """
    try:
        if not material.use_nodes:
            return False
        
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        principled = _find_principled(material)
        output_node = _get_output_node(material)
        if not principled: return False
        
        # Detectar conexión Alpha antes de borrar
        alpha_socket = principled.inputs.get('Alpha')
        alpha_source_socket = None
        alpha_source_node = None
        
        nodes_to_keep = {principled, output_node}
        
        if alpha_socket and alpha_socket.is_linked:
            alpha_link = alpha_socket.links[0]
            alpha_source_socket = alpha_link.from_socket
            alpha_source_node = alpha_link.from_node
            
            # Si el nodo de origen es una imagen o mapping, intentar preservarlo
            # (Un análisis profundo preservaría toda la cadena, aquí hacemos best-effort)
            nodes_to_keep.add(alpha_source_node)
            
            # Si tiene mapping atras, guardarlo tambien
            if hasattr(alpha_source_node, 'inputs'):
                for inp in alpha_source_node.inputs:
                    if inp.is_linked:
                        nodes_to_keep.add(inp.links[0].from_node)

        # Validarlo con el usuario: quiere "clean strict"
        # Si preservamos nodos basura, fallamos el propósito.
        # Pero si el Alpha es vital...
        # Vamos a reconectar el Alpha solo si sobrevivió a la purga o si es externo.
        # Mejor estrategia: NO borrar los nodos que alimentan el Alpha.
        # O borrar todo y que el usuario se arregle?
        # El requerimiento es "Limpiar materiales", pero "Rasterizar difuso visible".
        # Si el alpha no estaba bakeado, se perderá si borramos todo.
        # Preservamos lo marcado en nodes_to_keep.

        # Eliminar nodos no deseados
        nodes_to_remove = [n for n in nodes if n not in nodes_to_keep]
        for n in nodes_to_remove:
            nodes.remove(n)
        
        # Crear nodo imagen baked
        image_node = nodes.new(type='ShaderNodeTexImage')
        image_node.image = baked_image
        image_node.location = (principled.location.x - 300, principled.location.y)
        image_node.label = "Rasterized Diffuse"
        
        # Conectar Color
        base_color = principled.inputs.get('Base Color')
        if base_color:
             # Limpiar primero
            while base_color.is_linked: links.remove(base_color.links[0])
            links.new(image_node.outputs['Color'], base_color)
            
        # El Alpha ya debería estar conectado si preservamos los nodos y enlaces.
        # Si se rompió el enlace (porque borramos nodos intermedios que no trackeamos), intentamos reconectar
        # si alpha_source_node sigue vivo.
        if alpha_source_socket and alpha_source_node in nodes.keys(): # check invalid ref
             if alpha_socket and not alpha_socket.is_linked:
                 links.new(alpha_source_socket, alpha_socket)

        print(f"✅ Material reemplazado con baked: {material.name}")
        return True
        
    except Exception as e:
        print(f"❌ Error reemplazando material: {e}")
        return False


def has_alpha_texture_connected(material):
    """
    Verifica si el material tiene Alpha conectado usando la lógica unificada
    de revisión de píxeles (check_real_pixel_transparency).
    """
    return check_real_pixel_transparency(material)


# ========================================================================================
# OPERADORES AVANZADOS
# ========================================================================================

def _find_principled(material):
    """Devuelve el nodo BSDF Principled del material (o None)."""
    try:
        if not material or not material.use_nodes or not material.node_tree:
            return None
        for node in material.node_tree.nodes:
            if getattr(node, 'type', None) == 'BSDF_PRINCIPLED':
                return node
    except Exception:
        pass
    return None


def _trace_nearest_image_to_base_color(principled):
    """Traza desde `Base Color` hacia atrás y devuelve el primer nodo TEX_IMAGE si existe.
    Retorna (image_node, chain_nodes) donde chain_nodes son los nodos recorridos.
    """
    if principled is None:
        return None, []
    base_input = principled.inputs.get('Base Color')
    if not base_input or not base_input.is_linked:
        return None, []

    visited = set()
    chain_nodes = []
    stack = [base_input.links[0].from_node]
    while stack:
        node = stack.pop(0)  # BFS: más cercano primero
        if node in visited:
            continue
        visited.add(node)
        chain_nodes.append(node)
        if getattr(node, 'type', '') == 'TEX_IMAGE':
            return node, chain_nodes
        # Encolar entradas linkeadas
        try:
            for socket in getattr(node, 'inputs', []):
                if socket.is_linked:
                    stack.append(socket.links[0].from_node)
        except Exception:
            pass
    return None, chain_nodes


def _get_output_node(material):
    try:
        for n in material.node_tree.nodes:
            if getattr(n, 'type', None) == 'OUTPUT_MATERIAL':
                return n
    except Exception:
        pass
    return None


def _material_is_simple(material, principled):
    """Material simple estricto:
    - Debe existir exactamente UNA `TEX_IMAGE` conectada DIRECTO a `Base Color`.
    - `Alpha` del Principled debe estar sin enlace o enlazado al `Alpha` de ESA misma imagen.
    - No deben existir otros nodos distintos a: `Principled`, `Output`, y esa `TEX_IMAGE`.
    """
    try:
        nodes = material.node_tree.nodes
        output_node = _get_output_node(material)
        if principled is None or output_node is None:
            return False

        base_input = principled.inputs.get('Base Color')
        if not base_input or not base_input.is_linked:
            return False
        image_node = base_input.links[0].from_node
        if getattr(image_node, 'type', '') != 'TEX_IMAGE':
            return False

        # Alpha debe ser None o provenir de la misma imagen
        alpha_input = principled.inputs.get('Alpha')
        if alpha_input and alpha_input.is_linked:
            if getattr(alpha_input.links[0].from_node, 'name', None) != getattr(image_node, 'name', None):
                return False

        # Solo 3 nodos permitidos
        allowed = {principled, output_node, image_node}
        for n in nodes:
            if n not in allowed:
                return False
        return True
    except Exception:
        return False


def _connect_alpha_if_available(material, image_node, principled):
    try:
        if not image_node or not principled:
            return
        links = material.node_tree.links
        alpha_socket = image_node.outputs.get('Alpha')
        principled_alpha = principled.inputs.get('Alpha')
        if alpha_socket and principled_alpha:
            # Verificar si el alpha de la imagen tiene información útil
            effective = True
            try:
                img = getattr(image_node, 'image', None)
                if img and img.size[0] > 0 and img.size[1] > 0 and img.pixels:
                    alphas = list(img.pixels[3::4])
                    if sum(alphas) < 1e-3:
                        effective = False
            except Exception:
                pass
            # Si el alpha no es efectivo, desconectar y fijar alpha=1.0
            if not effective:
                while principled_alpha.is_linked:
                    links.remove(principled_alpha.links[0])
                try:
                    principled_alpha.default_value = 1.0
                except Exception:
                    pass
                try:
                    if hasattr(material, 'blend_method'):
                        material.blend_method = 'OPAQUE'
                except Exception:
                    pass
            else:
                while principled_alpha.is_linked:
                    links.remove(principled_alpha.links[0])
                links.new(alpha_socket, principled_alpha)
    except Exception:
        pass


def _simplify_to_nearest_image(material, principled) -> bool:
    """Mantiene solo la TEX_IMAGE más cercana al Base Color y conecta Color/Alpha.
    Devuelve True si se simplificó algo.
    """
    try:
        image_node, chain_nodes = _trace_nearest_image_to_base_color(principled)
        if image_node is None:
            return False

        nodes = material.node_tree.nodes
        links = material.node_tree.links

        # Conectar color directamente al Principled
        base_input = principled.inputs.get('Base Color')
        if base_input:
            # Limpiar enlaces existentes del Base Color
            while base_input.is_linked:
                links.remove(base_input.links[0])
            links.new(image_node.outputs.get('Color'), base_input)

        # Conectar alpha si procede (sustituye cualquier conexión existente)
        _connect_alpha_if_available(material, image_node, principled)

        # Eliminar todo lo que no sea Principled, Output o el image_node encontrado
        to_keep = {principled, image_node}
        for n in nodes:
            if getattr(n, 'type', None) == 'OUTPUT_MATERIAL':
                to_keep.add(n)
        remove_list = [n for n in nodes if n not in to_keep]
        for n in remove_list:
            nodes.remove(n)

        print(f"🧹 {material.name}: limpieza realizada (nodos eliminados={len(remove_list)})")

        return True
    except Exception:
        return False


def _duplicate_image_as_baked(src_image, baked_name):
    """Crea una nueva Image copiando píxeles de otra imagen."""
    try:
        if not src_image or src_image.size[0] <= 0 or src_image.size[1] <= 0:
            return None
        width, height = src_image.size
        # Remover si existe
        if baked_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[baked_name])
        new_img = bpy.data.images.new(baked_name, width=width, height=height, alpha=True)
        # Copiar píxeles si están disponibles
        try:
            if src_image.pixels and len(src_image.pixels) == width * height * 4:
                new_img.pixels = list(src_image.pixels[:])
        except Exception:
            pass
        new_img.pack()
        new_img.use_fake_user = True
        return new_img
    except Exception:
        return None


def _get_alpha_image_node(principled):
    """Devuelve el nodo TEX_IMAGE conectado directamente al Alpha del Principled, si existe."""
    try:
        alpha_in = principled.inputs.get('Alpha')
        if alpha_in and alpha_in.is_linked:
            node = alpha_in.links[0].from_node
            if getattr(node, 'type', '') == 'TEX_IMAGE':
                return node
    except Exception:
        pass
    return None


def _rebuild_material_with_image(material, principled, baked_image, alpha_image=None):
    """Reconstruye el material dejando solo Output, Principled y un ImageTexture con baked_image.
    Si alpha_image se provee, crea otro ImageTexture para usar su Alpha en el Principled.
    """
    try:
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        # Mantener Principled y Output
        keep = {principled}
        for n in nodes:
            if getattr(n, 'type', None) == 'OUTPUT_MATERIAL':
                keep.add(n)
        for n in [n for n in nodes if n not in keep]:
            nodes.remove(n)

        tex = nodes.new(type='ShaderNodeTexImage')
        tex.image = baked_image
        tex.location = (-300, 0)
        # Conectar color y alpha
        base = principled.inputs.get('Base Color')
        if base:
            while base.is_linked:
                links.remove(base.links[0])
            links.new(tex.outputs['Color'], base)
        # Alpha: si se solicitó mantener alpha original desde otra imagen, conectarlo
        if alpha_image is not None:
            try:
                alpha_tex = nodes.new(type='ShaderNodeTexImage')
                alpha_tex.image = alpha_image
                alpha_tex.location = (-300, -200)
                principled_alpha = principled.inputs.get('Alpha')
                if principled_alpha:
                    while principled_alpha.is_linked:
                        links.remove(principled_alpha.links[0])
                    links.new(alpha_tex.outputs['Alpha'], principled_alpha)
            except Exception:
                _connect_alpha_if_available(material, tex, principled)
        else:
            _connect_alpha_if_available(material, tex, principled)
        return True
    except Exception:
        return False


def _find_object_with_material(material):
    """Encuentra un objeto MESH que use el material dado y devuelve (obj, slot_index) o (None, -1)."""
    try:
        for obj in bpy.data.objects:
            if getattr(obj, 'type', None) == 'MESH' and getattr(obj.data, 'materials', None):
                for idx, slot in enumerate(obj.material_slots):
                    if slot.material == material:
                        return obj, idx
    except Exception:
        pass
    return None, -1


def _enable_cycles_gpu_if_available():
    """Activa GPU en Cycles si hay dispositivos disponibles.
    Configura preferencias de CUDA/OPTIX/HIP según disponibilidad.
    """
    prefs = bpy.context.preferences
    cycles_prefs = getattr(prefs.addons.get('cycles'), 'preferences', None)
    if not cycles_prefs:
        return False
    # Intentar OPTIX, luego CUDA, luego HIP
    for backend in ['OPTIX', 'CUDA', 'HIP', 'METAL']:
        try:
            cycles_prefs.compute_device_type = backend
            # Habilitar todos los dispositivos GPU disponibles
            for device in cycles_prefs.get_devices()[0]:
                device.use = True
            bpy.context.scene.cycles.device = 'GPU'
            return True
        except Exception:
            continue
    return False


def _bake_visual_to_image(material, principled, target_name, width, height):
    """Baking visual del material a una imagen nueva usando UVs. Devuelve la imagen o None."""
    try:
        obj, slot_index = _find_object_with_material(material)
        if not obj or not getattr(obj.data, 'uv_layers', None) or len(obj.data.uv_layers) == 0:
            return None

        # Crear imagen destino
        if target_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[target_name])
        bake_img = bpy.data.images.new(target_name, width=width, height=height, alpha=True)

        # Preparar escena para bake
        prev_engine = bpy.context.scene.render.engine
        bpy.context.scene.render.engine = 'CYCLES'
        # Intentar GPU si está disponible; fallback a CPU
        try:
            _enable_cycles_gpu_if_available()
        except Exception:
            try:
                bpy.context.scene.cycles.device = 'CPU'
            except Exception:
                pass
        bpy.context.scene.render.bake.margin = 2
        bpy.context.scene.render.bake.use_clear = True
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True

        nodes = material.node_tree.nodes
        links = material.node_tree.links

        # Crear nodo temporal de imagen y activarlo para recibir el bake
        temp_image_node = nodes.new(type='ShaderNodeTexImage')
        temp_image_node.image = bake_img
        temp_image_node.select = True
        nodes.active = temp_image_node
        
        # Forzar material opaco temporalmente para evitar efectos de transparencia al hornear
        try:
            if hasattr(material, 'blend_method'):
                material.blend_method = 'OPAQUE'
        except Exception:
            pass

        # Selección del objeto y material activo
        for o in bpy.data.objects:
            o.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass
        try:
            if slot_index >= 0:
                obj.active_material_index = slot_index
                obj.active_material = material
        except Exception:
            pass
        # Asegurar UV activa
        try:
            obj.data.uv_layers.active_index = 0
        except Exception:
            pass

        # Ejecutar bake DIFFUSE (solo color)
        bpy.ops.object.bake(type='DIFFUSE')

        # Limpiar nodo temporal
        nodes.remove(temp_image_node)

        # Restaurar engine
        bpy.context.scene.render.engine = prev_engine

        # Validar resultado; si viene vacío/transparente, fallback a duplicado
        try:
            px = list(bake_img.pixels[:])
            if not px:
                return None
            # Detectar bake negro
            r_sum = sum(px[0::4])
            g_sum = sum(px[1::4])
            b_sum = sum(px[2::4])
            if (r_sum + g_sum + b_sum) < 1e-6:
                return None
            # Asegurar alpha 1.0 si la mayor parte está en 0
            alphas = px[3::4]
            if sum(alphas) < 1e-3:
                for i in range(3, len(px), 4):
                    px[i] = 1.0
                bake_img.pixels = px
        except Exception:
            pass

        bake_img.pack()
        bake_img.use_fake_user = True
        return bake_img
    except Exception as e:
        try:
            nodes = material.node_tree.nodes
            # intentar limpiar temp si existe
            for n in list(nodes):
                if getattr(n, 'type', None) == 'TEX_IMAGE' and getattr(n, 'image', None) and getattr(n, 'label', '') == '':
                    pass
        except Exception:
            pass
        return None


def check_real_pixel_transparency(material):
    """
    Verifica si el material tiene transparencia basándose ÚNICAMENTE en la textura
    conectada a Base Color.
    - Si la textura Base tiene píxeles transparentes -> True (Skip Bake).
    - Si la textura Base es opaca (o no hay textura) -> False (Force Bake).
    Se ignora lo que esté conectado al socket Alpha del nodo.
    """
    try:
        principled = _find_principled(material)
        if not principled: return False
        
        # 1. Buscamos la imagen source en Base Color
        base_socket = principled.inputs.get('Base Color')
        if not base_socket or not base_socket.is_linked:
            return False # Procedural/Color solido -> Considerar Opaco para que se bakee
            
        # Rastreo simple del nodo conectado
        node = base_socket.links[0].from_node
        
        # Si no es imagen (ej: Mix, Ramp), asumimos opaco/bakeable
        if node.type != 'TEX_IMAGE' or not node.image:
            return False 
            
        img = node.image
        
        # 2. Check rápido por metadatos
        if img.alpha_mode == 'NONE':
            return False # Es opaca
            
        # 3. Check de píxeles (sampling)
        # Si tiene canal alpha (depth 32), chequeamos valores
        if len(img.pixels) > 0 and img.channels == 4:
             w, h = img.size
             # Samplear esquinas y centro
             indices = [0, (w-1)*4, (w*h-w)*4, (w*h-1)*4, ((h//2)*w + w//2)*4]
             
             # Si la imagen es pequeña, sampleamos todo el alpha channel (saltando de 4 en 4)
             if w*h < 10000:
                 for i in range(3, len(img.pixels), 4):
                     if img.pixels[i] < 0.99: return True
             else:
                 # Sampleo disperso para imágenes grandes
                 for idx in indices:
                     if idx+3 < len(img.pixels):
                         if img.pixels[idx+3] < 0.99: return True
                         
             return False # Alpha channel parece todo blanco
        
        return False # No channels alpha detectados
    except:
        return False


def execute_pre_conversion_rasterization():
    """Aplica la regla solicitada durante la conversión:
    - Material simple: se omite.
    - Material complejo: BAKE (Estrategia Diffuse/Emit).
    - Preservación de Alpha: Si tiene alpha REAL (pixeles), el bake lo debe capturar.
    Devuelve (procesados, total_materiales).
    """
    processed = 0
    total = 0
    try:
        materials = [m for m in bpy.data.materials if m and m.use_nodes]
        total = len(materials)
        
        # Respetar toggles globales
        settings = getattr(bpy.context.scene, 'universal_gta_settings', None)
        global_do_rasterize = bool(getattr(settings, 'rasterize_textures', False)) if settings else False
        global_do_clean = bool(getattr(settings, 'clean_materials', True)) if settings else True

        if not global_do_rasterize and not global_do_clean:
            print("🛑 Pre-rasterización omitida")
            return processed, total
            
        print("\n" + "="*60)
        print("🧠 PRE-RASTERIZACIÓN ROBUSTA (Universal GTA)")
        print("="*60)
        
        for mat in materials:
            try:
                principled = _find_principled(mat)
                if principled is None: continue

                # 1. Simple -> Salir
                if _material_is_simple(mat, principled):
                    print(f"ℹ️ {mat.name}: Simple (SKIP)")
                    continue

                # 2. Análisis
                base_input = principled.inputs.get('Base Color')
                has_direct_image = bool(base_input and base_input.is_linked and base_input.links[0].from_node.type == 'TEX_IMAGE')
                
                # Check Alpha INTELIGENTE (Pixeles reales)
                has_real_alpha = check_real_pixel_transparency(mat)

                # 3. DECISIÓN: ¿BAKE O CLEAN?
                should_bake = False
                
                # --- REGLA: SI TIENE ALPHA REAL -> PROHIBIDO BAKEAR ---
                if has_real_alpha:
                     print(f"ℹ️ {mat.name}: Transparencia Real detectada -> Solo Limpieza")
                     if global_do_clean:
                         if _simplify_to_nearest_image(mat, principled):
                             processed += 1
                     continue

                # A) Si YA tiene imagen directa (y es opaca)
                if has_direct_image:
                    if global_do_clean:
                        print(f"ℹ️ {mat.name}: Tiene imagen directa (Opaca). Limpieza.")
                        if _simplify_to_nearest_image(mat, principled):
                            processed += 1
                        continue
                    else:
                        continue
                
                # B) Si NO tiene imagen directa (procedural/mix) -> BAKE
                if global_do_rasterize:
                    should_bake = True
                
                # 4. EJECUCIÓN
                if should_bake:
                    print(f"⚡ {mat.name}: Requiere BAKE MANUAL (Opaco/Procedural)")
                    resolution = get_original_texture_resolution(mat)
                    baked_img = perform_advanced_baking(mat, resolution)
                    if baked_img and replace_material_with_baked(mat, baked_img):
                        processed += 1
                        print(f"✅ {mat.name}: Rasterizado Exitosamente")
                    else:
                        print(f"❌ {mat.name}: Falló el Bake")

            except Exception as e:
                print(f"❌ {mat.name}: Error procesando: {e}")

    except Exception:
        print("❌ Error global en pre-rasterización")

    # --- Renombrar Nodos (Label = Image Name) [Scripts Usuario] ---
    print("🏷️ Actualizando etiquetas de nodos de imagen (Scope: Selected Objects)...")
    try:
        processed_mats_labels = set()
        # Usamos selected_objects porque son los que estamos convirtiendo
        objects_to_check = list(bpy.context.selected_objects)
        
        # Si no hay seleccionados (raro en este punto), fallback a todos los objetos visibles/mesh
        if not objects_to_check:
             objects_to_check = [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide_viewport]

        for obj in objects_to_check:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material:
                        mat = slot.material
                        if mat in processed_mats_labels: continue
                        processed_mats_labels.add(mat)
                        
                        if mat.use_nodes and mat.node_tree:
                            for node in mat.node_tree.nodes:
                                if node.type == 'TEX_IMAGE' and node.image:
                                    node.label = node.image.name
                                    # print(f"   🏷️ {mat.name} -> {node.image.name}")
    except Exception as e:
        print(f"⚠️ Error menor actualizando etiquetas: {e}")

    print(f"📊 Resultado: procesados={processed} / total={total}")
    return processed, total

class UNIVERSALGTA_OT_pre_conversion_rasterization_advanced(Operator):
    """Rasterización pre-conversión AVANZADA con baking inteligente"""
    bl_idname = "universalgta.pre_conversion_rasterization_advanced"
    bl_label = "🧠 Pre-Conversion Rasterization ADVANCED"
    bl_description = "Sistema avanzado de rasterización con baking inteligente y preservación de colores"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Propiedades configurables
    auto_resolution: BoolProperty(
        name="Auto Resolution",
        description="Detectar resolución automáticamente",
        default=True
    )
    
    manual_resolution: IntProperty(
        name="Manual Resolution",
        description="Resolución manual (potencia de 2)",
        default=1024,
        min=256,
        max=2048
    )
    
    skip_alpha_materials: BoolProperty(
        name="Skip Alpha Materials",
        description="Saltar materiales con Alpha conectado",
        default=True
    )

    def execute(self, context):
        try:
            print("\n" + "="*60)
            print("🚀 INICIANDO RASTERIZACIÓN AVANZADA")
            print("="*60)
            
            materials = [mat for mat in bpy.data.materials if mat and mat.use_nodes]
            processed_count = 0
            alpha_exceptions = 0
            
            for material in materials:
                print(f"\n🔍 Analizando material: {material.name}")
                
                # Verificar excepción Alpha
                if self.skip_alpha_materials and has_alpha_texture_connected(material):
                    print(f"🚫 SALTANDO (Alpha detectado): {material.name}")
                    alpha_exceptions += 1
                    continue
                
                # Determinar resolución
                resolution = self.manual_resolution
                if self.auto_resolution:
                    resolution = get_original_texture_resolution(material)
                
                # Realizar baking avanzado
                baked_image = perform_advanced_baking(material, resolution)
                if not baked_image:
                    continue
                
                # Reemplazar material con versión baked
                if replace_material_with_baked(material, baked_image):
                    processed_count += 1
                    print(f"✅ PROCESADO: {material.name}")
            
            # Reporte final
            print(f"\n📊 RESULTADO FINAL:")
            print(f"   ✅ Materiales procesados: {processed_count}")
            print(f"   🚫 Excepciones Alpha: {alpha_exceptions}")
            print(f"   📁 Total materiales: {len(materials)}")
            
            if processed_count > 0:
                self.report({'INFO'}, f"✅ Rasterización avanzada: {processed_count}/{len(materials)} materiales")
            else:
                self.report({'INFO'}, "ℹ️ No se encontraron materiales para procesar")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en rasterización avanzada: {e}")
            return {'CANCELLED'}

    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "auto_resolution")
        if not self.auto_resolution:
            layout.prop(self, "manual_resolution")
        layout.prop(self, "skip_alpha_materials")


class UNIVERSALGTA_OT_quick_texture_export(Operator):
    """Exportación rápida reutilizando la última configuración"""
    bl_idname = "universalgta.quick_texture_export"
    bl_label = "⚡ Quick Texture Export"
    bl_description = "Exporta rápidamente usando la última carpeta seleccionada"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = _get_texture_exporter_props(context)
        if not props:
            self.report({'ERROR'}, "Propiedades de exportación no disponibles")
            return {'CANCELLED'}

        export_path = props.export_path
        if not export_path or not os.path.exists(export_path):
            self.report({'ERROR'}, "Primero selecciona una carpeta válida con 'Export Textures (Browse)'")
            return {'CANCELLED'}

        if props.export_mode == 'SELECTED':
            selected_objects = list(context.selected_objects) if hasattr(context, 'selected_objects') else []
            if not selected_objects:
                self.report({'ERROR'}, "Selecciona uno o más objetos para exportar sus texturas")
                return {'CANCELLED'}

        images_to_export, error_msg = _collect_images_to_export(context, props.export_mode)
        if error_msg:
            self.report({'ERROR'}, error_msg)
            return {'CANCELLED'}

        if not images_to_export:
            self.report({'WARNING'}, "No se encontraron texturas para exportar")
            return {'CANCELLED'}

        export_path = _normalize_export_path(export_path)
        try:
            os.makedirs(export_path, exist_ok=True)
        except Exception as e:
            self.report({'ERROR'}, f"No se pudo crear la carpeta: {e}")
            return {'CANCELLED'}

        exported, failed = _export_images(
            images_to_export,
            export_path,
            props.force_format_enabled,
            props.forced_format if props.force_format_enabled else None,
        )

        props.export_path = export_path

        _report_export_summary(self, context, exported, failed, props.export_mode, props.force_format_enabled, props.forced_format)
        return {'FINISHED'}


class UNIVERSALGTA_OT_export_textures_enhanced(Operator, ExportHelper):
    """Exportación avanzada usando el nuevo sistema universal"""
    bl_idname = "universalgta.export_textures_enhanced"
    bl_label = "🎨 Enhanced Texture Export"
    bl_description = "Exporta texturas con opciones de formato y selección personalizadas"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ""
    use_filter_folder = True

    directory: StringProperty(
        name="Carpeta de Destino",
        description="Selecciona la carpeta donde guardar las texturas",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    export_mode: EnumProperty(
        name="Modo de Exportación",
        description="Selecciona qué texturas exportar",
        items=EXPORT_MODE_ITEMS,
        default='ALL'
    )

    force_format_enabled: BoolProperty(
        name="Forzar formato",
        description="Exportar todas las texturas en un formato específico",
        default=True
    )

    forced_format: EnumProperty(
        name="Formato objetivo",
        description="Formato final para todas las texturas exportadas",
        items=FORCED_FORMAT_ITEMS,
        default='PNG'
    )

    def execute(self, context):
        if not self.directory:
            self.report({'ERROR'}, "Selecciona una carpeta válida")
            return {'CANCELLED'}

        export_path = _normalize_export_path(self.directory)
        try:
            os.makedirs(export_path, exist_ok=True)
        except Exception as e:
            self.report({'ERROR'}, f"No se pudo crear la carpeta: {e}")
            return {'CANCELLED'}

        images_to_export, error_msg = _collect_images_to_export(context, self.export_mode)
        if error_msg:
            self.report({'ERROR'}, error_msg)
            return {'CANCELLED'}

        if not images_to_export:
            self.report({'WARNING'}, "No se encontraron texturas para exportar")
            return {'CANCELLED'}

        exported, failed = _export_images(
            images_to_export,
            export_path,
            self.force_format_enabled,
            self.forced_format if self.force_format_enabled else None,
        )

        props = _get_texture_exporter_props(context)
        if props:
            props.export_path = export_path
            props.export_mode = self.export_mode
            props.force_format_enabled = self.force_format_enabled
            props.forced_format = self.forced_format

        _report_export_summary(self, context, exported, failed, self.export_mode, self.force_format_enabled, self.forced_format)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "export_mode", text="Modo")
        layout.prop(self, "force_format_enabled")
        row = layout.row()
        row.enabled = self.force_format_enabled
        row.prop(self, "forced_format", text="Formato")

    def invoke(self, context, event):
        props = _get_texture_exporter_props(context)
        if props:
            if props.export_path:
                self.directory = props.export_path
            self.export_mode = props.export_mode
            self.force_format_enabled = props.force_format_enabled
            self.forced_format = props.forced_format

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class UNIVERSALGTA_OT_export_textures_with_browser(Operator, ExportHelper):
    """Exportador con navegador de archivos basado en el nuevo sistema"""
    bl_idname = "universalgta.export_textures_with_browser"
    bl_label = "📁 Export Textures (Browse)"
    bl_description = "Exporta texturas seleccionando la carpeta de destino"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ""
    use_filter_folder = True

    directory: StringProperty(
        name="Carpeta de Destino",
        description="Selecciona la carpeta donde guardar las texturas",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    def execute(self, context):
        props = _get_texture_exporter_props(context)
        if not props:
            self.report({'ERROR'}, "Propiedades de exportación no disponibles")
            return {'CANCELLED'}

        if not self.directory:
            self.report({'ERROR'}, "Selecciona un directorio válido")
            return {'CANCELLED'}

        export_path = _normalize_export_path(self.directory)
        try:
            os.makedirs(export_path, exist_ok=True)
        except Exception as e:
            self.report({'ERROR'}, f"No se pudo crear la carpeta: {e}")
            return {'CANCELLED'}

        images_to_export, error_msg = _collect_images_to_export(context, props.export_mode)
        if error_msg:
            self.report({'ERROR'}, error_msg)
            return {'CANCELLED'}

        if not images_to_export:
            self.report({'WARNING'}, "No se encontraron texturas para exportar")
            return {'CANCELLED'}

        exported, failed = _export_images(
            images_to_export,
            export_path,
            props.force_format_enabled,
            props.forced_format if props.force_format_enabled else None,
        )

        props.export_path = export_path

        _report_export_summary(self, context, exported, failed, props.export_mode, props.force_format_enabled, props.forced_format)
        return {'FINISHED'}

    def invoke(self, context, event):
        props = _get_texture_exporter_props(context)
        if props and props.export_path:
            self.directory = props.export_path
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class UNIVERSALGTA_OT_quick_material_rgb_fix(Operator):
    """Fix rápido de colores RGB en materiales"""
    bl_idname = "universalgta.quick_material_rgb_fix"
    bl_label = "🎨 Quick Material RGB Fix"
    bl_description = "Aplica fix rápido de colores RGB en todos los materiales"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            # Color GTA estándar
            gta_color = [0.906, 0.906, 0.906, 1.0]
            fixed = 0
            
            for material in bpy.data.materials:
                if material and material.use_nodes:
                    nodes = material.node_tree.nodes
                    for node in nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            node.inputs['Base Color'].default_value = gta_color
                            fixed += 1
                            break
            
            self.report({'INFO'}, f"✅ RGB fix aplicado a {fixed} materiales")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en RGB fix: {e}")
            return {'CANCELLED'}


class UNIVERSALGTA_OT_manual_smart_baking(Operator):
    """Sistema de baking manual inteligente - ESPECIFICACIONES EXACTAS"""
    bl_idname = "universalgta.manual_smart_baking"
    bl_label = "🔥 Manual Smart Baking"
    bl_description = "Baking inteligente: verifica objeto, limpia nodos, bakea según casos específicos"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            print("🔥 Manual Smart Baking (Vía Unified Rasterization)...")
            from .texture_export import execute_pre_conversion_rasterization
            
            # Ejecutar la lógica unificada robusta
            processed, total = execute_pre_conversion_rasterization()
            
            if processed > 0:
                self.report({'INFO'}, f"✅ Baking unificado aplicado a {processed}/{total} materiales")
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, f"Proceso finalizado (0/{total} modificados)")
                return {'FINISHED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error en smart baking wrapper: {e}")
            return {'CANCELLED'}

    def _verify_and_select_object(self, context):
        return None # Obsoleto

    def _process_material_smart_baking(self, material, context):
        return False # Obsoleto
    
    def _has_image_texture_in_base_color(self, base_color_input):
        """Verifica si hay Image Texture conectado al Base Color"""
        if not base_color_input.is_linked:
            return False
        
        # Recorrer la cadena de nodos hacia atrás
        current_node = base_color_input.links[0].from_node
        
        while current_node:
            if current_node.type == 'TEX_IMAGE':
                return True
            
            # Continuar hacia atrás si hay más conexiones
            if hasattr(current_node, 'inputs') and len(current_node.inputs) > 0:
                for input_socket in current_node.inputs:
                    if input_socket.is_linked:
                        current_node = input_socket.links[0].from_node
                        break
                else:
                    break
            else:
                break
        
        return False
    
    def _is_image_texture_connected_to_alpha(self, alpha_input, image_texture_nodes):
        """Verifica si algún Image Texture está conectado también al Alpha"""
        if not alpha_input.is_linked:
            return False
        
        alpha_node = alpha_input.links[0].from_node
        return alpha_node in image_texture_nodes
    
    def _clean_nodes_preserve_image_texture(self, material, principled_bsdf, material_output):
        """Limpia nodos pero mantiene Image Texture, ColorRamp, RGB Curves, HSV, Brillo/Contraste"""
        nodes = material.node_tree.nodes
        
        # Nodos a mantener SIEMPRE
        preserve_nodes = {material_output, principled_bsdf}
        
        # Nodos a evaluar para mantener
        for node in nodes:
            if node.type in ['TEX_IMAGE', 'TEX_COORD', 'MAPPING']:
                preserve_nodes.add(node)
            elif node.type in ['VALTORGB', 'CURVE_RGB', 'HUE_SAT', 'BRIGHTCONTRAST']:
                # Solo mantener si usan Image Texture como entrada
                if self._node_uses_image_texture_input(node):
                    preserve_nodes.add(node)
        
        # Eliminar todos los demás nodos
        nodes_to_remove = [node for node in nodes if node not in preserve_nodes]
        
        for node in nodes_to_remove:
            nodes.remove(node)
        
        print(f"🧹 Limpieza completada: eliminados {len(nodes_to_remove)} nodos, mantenidos {len(preserve_nodes)}")
    
    def _node_uses_image_texture_input(self, node):
        """Verifica si un nodo usa Image Texture como entrada"""
        for input_socket in node.inputs:
            if input_socket.is_linked:
                source_node = input_socket.links[0].from_node
                if source_node.type == 'TEX_IMAGE':
                    return True
                # Verificar recursivamente
                if self._node_uses_image_texture_input(source_node):
                    return True
        return False
    
    def _rasterize_direct_color(self, material, principled_bsdf, base_color_input, alpha_input):
        """CASO 2: Crear Image Texture de 256x256 rasterizando color directo"""
        try:
            # Obtener color actual del Base Color
            if base_color_input.is_linked:
                # Si está conectado a algún nodo, evaluar el color
                current_color = self._evaluate_node_color(base_color_input.links[0].from_node)
            else:
                # Usar valor por defecto del socket
                current_color = list(base_color_input.default_value)
            
            # Asegurar que tenemos 4 valores (RGBA)
            if len(current_color) == 3:
                current_color.append(1.0)  # Alpha = 1.0
            
            # Crear nueva Image Texture de 256x256
            image_name = f"{material.name}_rasterized"
            
            # Remover imagen existente si ya existe
            if image_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[image_name])
            
            # Crear nueva imagen
            new_image = bpy.data.images.new(image_name, width=256, height=256, alpha=True)
            
            # Llenar con el color
            pixel_count = 256 * 256
            pixels = current_color * pixel_count
            new_image.pixels = pixels
            
            # Empacar y proteger
            new_image.pack()
            new_image.use_fake_user = True
            
            # Limpiar nodos y crear setup nuevo
            nodes = material.node_tree.nodes
            links = material.node_tree.links
            
            # Eliminar todos excepto BSDF y Output
            nodes_to_remove = [node for node in nodes 
                             if node.type not in ['BSDF_PRINCIPLED', 'OUTPUT_MATERIAL']]
            
            for node in nodes_to_remove:
                nodes.remove(node)
            
            # Crear nuevo nodo Image Texture
            tex_node = nodes.new(type='ShaderNodeTexImage')
            tex_node.image = new_image
            tex_node.location = (-300, 0)
            
            # Conectar al Base Color y Alpha
            links.new(tex_node.outputs['Color'], principled_bsdf.inputs['Base Color'])
            links.new(tex_node.outputs['Alpha'], principled_bsdf.inputs['Alpha'])
            
            print(f"✅ Color rasterizado: {material.name} -> {image_name} (256x256)")
            return True
            
        except Exception as e:
            print(f"❌ Error rasterizando color en {material.name}: {e}")
            return False
    
    def _evaluate_node_color(self, node):
        """Evalúa el color de un nodo conectado"""
        if node.type == 'RGB':
            return list(node.outputs[0].default_value)
        elif node.type == 'VALTORGB':  # ColorRamp
            # Usar color del primer punto del ColorRamp
            if len(node.color_ramp.elements) > 0:
                return list(node.color_ramp.elements[0].color)
        
        # Para otros tipos, devolver blanco por defecto
        return [1.0, 1.0, 1.0, 1.0]
    
    def _perform_smart_bake(self, material, context):
        """Realiza bake real del material usando EMISSION (Bake más robusto)"""
        try:
            # Configurar motor de render (Cycles es necesario para Bake)
            if context.scene.render.engine != 'CYCLES':
                context.scene.render.engine = 'CYCLES'
            
            # Ajustes de performance para bake
            context.scene.cycles.device = 'CPU'
            context.scene.cycles.samples = 1
            context.scene.cycles.preview_samples = 1
            context.scene.cycles.max_bounces = 0
            
            # Obtener resolución de configuración
            settings = getattr(context.scene, 'universal_gta_settings', None)
            res_str = getattr(settings, 'bake_resolution', '512')
            resolution = int(res_str)
            
            # Validar objeto
            active_obj = context.active_object
            if not active_obj or not active_obj.data.uv_layers:
                print(f"⚠️ Objeto sin UVs, usando bake directo para {material.name}")
                return self._create_direct_bake(material)
            
            # === ASEGURAR CONTEXTO DE BAKE ===
            # 1. Modo Objeto
            if bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
                
            # 2. Selección explícita
            bpy.ops.object.select_all(action='DESELECT')
            active_obj.select_set(True)
            context.view_layer.objects.active = active_obj
            
            # 3. Sincronizar UVs
            uv_layers = active_obj.data.uv_layers
            render_uv = uv_layers.active_render
            if render_uv and uv_layers.active != render_uv:
                uv_layers.active = render_uv
            
            # Setup Imagen
            bake_name = f"{material.name}_rasterized"
            if bake_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[bake_name])
            
            bake_image = bpy.data.images.new(bake_name, width=resolution, height=resolution, alpha=True)
            
            nodes = material.node_tree.nodes
            links = material.node_tree.links
            
            # Identificar nodos clave
            principled = None
            output_node = None
            for n in nodes:
                if n.type == 'BSDF_PRINCIPLED':
                    principled = n
                elif n.type == 'OUTPUT_MATERIAL':
                    output_node = n
            
            if not principled or not output_node:
                return False
                
            # === ESTRATEGIA EMISSION BAKE ===
            emission = nodes.new('ShaderNodeEmission')
            emission.location = (principled.location.x + 200, principled.location.y + 200)
            
            # Preservar Alpha Link
            original_alpha_link_node = None
            original_alpha_link_socket = None
            if principled.inputs['Alpha'].is_linked:
                lnk = principled.inputs['Alpha'].links[0]
                original_alpha_link_node = lnk.from_node
                original_alpha_link_socket = lnk.from_socket
            
            # Conectar BaseColor a Emission
            if principled.inputs['Base Color'].is_linked:
                source_link = principled.inputs['Base Color'].links[0]
                links.new(source_link.from_socket, emission.inputs['Color'])
            else:
                emission.inputs['Color'].default_value = principled.inputs['Base Color'].default_value

            # Conectar Emission -> Output
            links.new(emission.outputs['Emission'], output_node.inputs['Surface'])
            
            # Nodo de imagen Target (CLEAN SELECTION)
            # Deseleccionar todos los nodos primero para evitar confusión en BAKE
            for n in nodes:
                n.select = False
                
            target_tex_node = nodes.new('ShaderNodeTexImage')
            target_tex_node.image = bake_image
            target_tex_node.select = True
            nodes.active = target_tex_node
            
            # EJECUTAR BAKE
            print(f"🔥 Bakeando EMIT: {material.name} ({resolution}px)...")
            try:
                bpy.ops.object.bake(type='EMIT')
                print("✅ Bake finalizado exitosamente.")
            except Exception as e:
                print(f"❌ Error crítico en bake: {e}")
                # Solo fallback si realmente falló el bake
                # Si falla, limpiamos y usamos fallback
                nodes.remove(emission)
                nodes.remove(target_tex_node)
                self._create_direct_bake(material)
                return False
            
            # === RESTAURACIÓN ===
            nodes.remove(emission)
            
            links.new(target_tex_node.outputs['Color'], principled.inputs['Base Color'])
            target_tex_node.location = (principled.location.x - 300, principled.location.y)
            target_tex_node.label = "Rasterized Diffuse"
            
            if original_alpha_link_node and original_alpha_link_socket:
                links.new(original_alpha_link_socket, principled.inputs['Alpha'])
            
            links.new(principled.outputs['BSDF'], output_node.inputs['Surface'])
            
            bake_image.pack()
            bake_image.use_fake_user = True
            
            return True
            
        except Exception as e:
            print(f"❌ Error general en Smart Bake: {e}")
            self._create_direct_bake(material)
            return False
    
    def _create_direct_bake(self, material):
        """Crea bake directo cuando el bake normal falla"""
        try:
            # Recuperar resolución (aunque sea fallback)
            settings = getattr(bpy.context.scene, 'universal_gta_settings', None)
            res_str = getattr(settings, 'bake_resolution', '512')
            resolution = int(res_str)

            bake_name = f"{material.name}_d_f"
            
            if bake_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[bake_name])
            
            # Crear imagen con color promedio del material
            bake_image = bpy.data.images.new(bake_name, width=resolution, height=resolution, alpha=True)
            
            # Color por defecto: gris GTA (#E7E7E7FF)
            default_color = [0.906, 0.906, 0.906, 1.0]  # #E7E7E7 en RGB
            
            pixel_count = resolution * resolution
            pixels = default_color * pixel_count
            bake_image.pixels = pixels
            
            bake_image.pack()
            bake_image.use_fake_user = True
            
            print(f"✅ Bake directo creado: {material.name} -> {bake_name} ({resolution}x{resolution})")
            return True
            
        except Exception as e:
            print(f"❌ Error en bake directo: {e}")
            return False

class UNIVERSALGTA_OT_pre_conversion_rasterization(Operator):
    """Alias para mantener compatibilidad con versión anterior"""
    bl_idname = "universalgta.pre_conversion_rasterization"
    bl_label = "🧠 Pre-Conversion Rasterization"
    bl_description = "Rasterización pre-conversión (redirige a versión avanzada)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Redirigir al operador avanzado
        return bpy.ops.universalgta.pre_conversion_rasterization_advanced()


# ========================================================================================
# REGISTRO DE CLASES
# ========================================================================================

classes = [
    TextureExporterProperties,
    UNIVERSALGTA_OT_pre_conversion_rasterization_advanced,
    UNIVERSALGTA_OT_pre_conversion_rasterization,  # Alias de compatibilidad
    UNIVERSALGTA_OT_quick_texture_export,
    UNIVERSALGTA_OT_export_textures_enhanced,
    UNIVERSALGTA_OT_export_textures_with_browser,  # AGREGADO
    UNIVERSALGTA_OT_quick_material_rgb_fix,        # AGREGADO
    UNIVERSALGTA_OT_manual_smart_baking,
]


def register():
    """Registrar operadores avanzados de texturas"""
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass  # Ya registrado
    if not hasattr(bpy.types.Scene, "texture_exporter_props"):
        bpy.types.Scene.texture_exporter_props = PointerProperty(
            type=TextureExporterProperties
        )
    print("[TEXTURE_EXPORT_ADVANCED] ✅ Todos los operadores avanzados registrados")


def unregister():
    """Desregistrar operadores avanzados de texturas"""
    if hasattr(bpy.types.Scene, "texture_exporter_props"):
        del bpy.types.Scene.texture_exporter_props
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except ValueError:
            pass  # No estaba registrado
    print("[TEXTURE_EXPORT_ADVANCED] ✅ Operadores avanzados desregistrados")
