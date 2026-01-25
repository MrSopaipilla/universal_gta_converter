"""
Sistema de Backup/Restore de Materiales
Inspirado en SimpleBake addon para permitir baking sin dependencias circulares.
"""

import bpy

class MaterialBackup:
    """
    Guarda y restaura el estado completo de un material.
    Permite modificar temporalmente el material para baking y luego restaurarlo.
    """
    
    def __init__(self, material):
        self.material = material
        self.nodes_data = {}
        self.links_data = []
        
    def backup(self):
        """Guarda el estado completo del material"""
        if not self.material or not self.material.use_nodes:
            return False
            
        node_tree = self.material.node_tree
        
        # Guardar todos los nodos
        for node in node_tree.nodes:
            node_data = {
                'name': node.name,
                'type': node.type,
                'bl_idname': node.bl_idname,
                'location': tuple(node.location),
                'width': node.width,
                'height': node.height,
                'label': node.label,
                'hide': node.hide,
                'mute': node.mute,
                'inputs': {},
                'outputs': {},
                'properties': {}
            }
            
            # Guardar valores de inputs
            for inp in node.inputs:
                input_data = {
                    'name': inp.name,
                    'type': inp.type,
                }
                
                # Guardar default_value si existe
                if hasattr(inp, 'default_value'):
                    try:
                        val = inp.default_value
                        # Convertir a tuple si es vector/color
                        if hasattr(val, '__iter__') and not isinstance(val, str):
                            input_data['default_value'] = tuple(val)
                        else:
                            input_data['default_value'] = val
                    except:
                        pass
                
                node_data['inputs'][inp.name] = input_data
            
            # Guardar propiedades específicas del nodo
            if node.type == 'TEX_IMAGE':
                node_data['properties']['image'] = node.image.name if node.image else None
                node_data['properties']['interpolation'] = node.interpolation
                node_data['properties']['projection'] = node.projection
                node_data['properties']['extension'] = node.extension
            elif node.type == 'BSDF_PRINCIPLED':
                # Ya guardamos los inputs, no necesitamos más
                pass
            elif node.type == 'OUTPUT_MATERIAL':
                node_data['properties']['is_active_output'] = node.is_active_output
            elif node.type == 'EMISSION':
                # Inputs ya guardados
                pass
            elif node.type == 'RGB':
                # Inputs ya guardados
                pass
            
            self.nodes_data[node.name] = node_data
        
        # Guardar todos los links
        for link in node_tree.links:
            link_data = {
                'from_node': link.from_node.name,
                'from_socket': link.from_socket.name,
                'to_node': link.to_node.name,
                'to_socket': link.to_socket.name,
            }
            self.links_data.append(link_data)
        
        print(f"   💾 Backup: {len(self.nodes_data)} nodos, {len(self.links_data)} links")
        return True
    
    def restore(self):
        """Restaura el material a su estado guardado"""
        if not self.material or not self.material.use_nodes:
            return False
            
        node_tree = self.material.node_tree
        nodes = node_tree.nodes
        links = node_tree.links
        
        # Limpiar todo
        nodes.clear()
        
        # Recrear nodos
        nodes_map = {}
        for node_name, node_data in self.nodes_data.items():
            # Crear nodo
            new_node = nodes.new(node_data['bl_idname'])
            new_node.name = node_data['name']
            new_node.location = node_data['location']
            new_node.width = node_data['width']
            new_node.height = node_data['height']
            new_node.label = node_data['label']
            new_node.hide = node_data['hide']
            new_node.mute = node_data['mute']
            
            # Restaurar propiedades específicas
            if node_data['type'] == 'TEX_IMAGE':
                image_name = node_data['properties'].get('image')
                if image_name and image_name in bpy.data.images:
                    new_node.image = bpy.data.images[image_name]
                new_node.interpolation = node_data['properties'].get('interpolation', 'Linear')
                new_node.projection = node_data['properties'].get('projection', 'FLAT')
                new_node.extension = node_data['properties'].get('extension', 'REPEAT')
            elif node_data['type'] == 'OUTPUT_MATERIAL':
                new_node.is_active_output = node_data['properties'].get('is_active_output', True)
            
            # Restaurar valores de inputs
            for inp_name, inp_data in node_data['inputs'].items():
                if inp_name in new_node.inputs:
                    inp = new_node.inputs[inp_name]
                    if 'default_value' in inp_data and hasattr(inp, 'default_value'):
                        try:
                            inp.default_value = inp_data['default_value']
                        except:
                            pass
            
            nodes_map[node_name] = new_node
        
        # Recrear links
        for link_data in self.links_data:
            try:
                from_node = nodes_map.get(link_data['from_node'])
                to_node = nodes_map.get(link_data['to_node'])
                
                if from_node and to_node:
                    from_socket = from_node.outputs.get(link_data['from_socket'])
                    to_socket = to_node.inputs.get(link_data['to_socket'])
                    
                    if from_socket and to_socket:
                        links.new(from_socket, to_socket)
            except Exception as e:
                print(f"   ⚠️ Error recreando link: {e}")
        
        print(f"   ♻️ Restore: Material restaurado completamente")
        return True
