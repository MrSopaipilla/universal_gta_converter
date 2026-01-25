
def _rasterize_direct_color(material, principled, base_socket, alpha_socket=None):
    """
    Crea una textura sólida 256x256 del color base y la conecta.
    Simplifica el material a Imagen -> Principled -> Output.
    """
    try:
        # Obtener color base
        color = (1.0, 1.0, 1.0, 1.0)
        if base_socket:
            # Si hay un nodo conectado (RGB, Value), intentar obtener su valor
            if base_socket.is_linked:
                node = base_socket.links[0].from_node
                if node.type == 'RGB':
                    color = tuple(node.outputs[0].default_value)
                elif node.type == 'VALUE':
                    val = node.outputs[0].default_value
                    color = (val, val, val, 1.0)
            else:
                color = tuple(base_socket.default_value)
        
        # Crear imagen solida
        img_name = f"{material.name}_diffuse_solid"
        if img_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[img_name])
            
        # Generar imagen
        size = 256
        image = bpy.data.images.new(img_name, width=size, height=size, alpha=True)
        
        # Llenar píxeles
        pixels = [color[0], color[1], color[2], color[3]] * (size * size)
        image.pixels = pixels
        image.pack()
        
        # Limpiar nodos y conectar
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Crear nodo imagen
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.image = image
        tex_node.label = img_name
        tex_node.location = (principled.location.x - 300, principled.location.y)
        
        # Conectar a Base Color
        if base_socket:
            links.new(tex_node.outputs['Color'], base_socket)
            
        # Conectar Alpha si es necesario
        if alpha_socket:
            links.new(tex_node.outputs['Alpha'], alpha_socket)
            
        # Limpieza de nodos desconectados/inutiles podría ir aquí si se desea
        # Pero por seguridad solo conectamos la imagen y dejamos que 'clean_materials' limpie después
        
        return True
    except Exception as e:
        print(f"❌ Error rasterizando color sólido: {e}")
        return False
