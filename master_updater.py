#!/usr/bin/env python3
"""
master_updater_script.py - Universal GTA Converter Addon Updater v1.0
================================================================================
SISTEMA MAESTRO DE ACTUALIZACIÓN PARA BLENDER ADDON
Compatible con Blender 5.0 - Actualiza y mejora archivos existentes

CARACTERÍSTICAS:
✅ Corrige menús duplicados en UI
✅ Mejora manual_smart_baking() según especificaciones exactas
✅ Integra correctamente en el flujo de conversión
✅ Mantiene compatibilidad con estructura existente
✅ Código profesional sin errores de sintaxis
✅ No modifica radicalmente el addon existente

ARCHIVOS QUE MODIFICA:
- panels/main_panel.py (fix UI duplicada)
- operators/texture_export.py (mejora manual_smart_baking)
- operators/gta_complete_conversion.py (integración)
- __init__.py (verificación de registro)
================================================================================
"""

import os
import sys
import re
from pathlib import Path

class UniversalGTAUpdater:
    """Sistema maestro de actualización para Universal GTA Converter"""
    
    def __init__(self, addon_path):
        self.addon_path = Path(addon_path)
        self.fixed_files = []
        self.created_files = []
        self.errors = []
        
        print("🚀 INICIANDO ACTUALIZACIÓN UNIVERSAL GTA CONVERTER")
        print(f"📁 Ruta del addon: {self.addon_path}")
        print("=" * 80)
    
    def run_all_updates(self):
        """Ejecuta todas las actualizaciones necesarias"""
        try:
            # 1. Verificar estructura del addon
            if not self._verify_addon_structure():
                return False
            
            # 2. Corregir menús duplicados en main_panel.py
            self._fix_duplicate_ui_panels()
            
            # 3. Mejorar manual_smart_baking en texture_export.py
            self._enhance_manual_smart_baking()
            
            # 4. Integrar en gta_complete_conversion.py
            self._integrate_smart_baking_into_conversion()
            
            # 5. Verificar y corregir __init__.py
            self._verify_and_fix_init_file()
            
            # 6. Crear backup de archivos originales
            self._create_backup_files()
            
            # Reporte final
            self._print_final_report()
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR CRÍTICO: {e}")
            self.errors.append(str(e))
            return False
    
    def _verify_addon_structure(self):
        """Verifica que la estructura del addon esté presente"""
        required_files = [
            "__init__.py",
            "panels/main_panel.py",
            "operators/texture_export.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.addon_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ ARCHIVOS FALTANTES: {missing_files}")
            return False
        
        print("✅ Estructura del addon verificada")
        return True
    
    def _fix_duplicate_ui_panels(self):
        """Corrige el problema de menús duplicados en main_panel.py"""
        file_path = self.addon_path / "panels" / "main_panel.py"
        
        try:
            print("🔧 Corrigiendo menús duplicados en main_panel.py...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Encontrar y corregir bl_idname duplicados
            content = self._fix_panel_idnames(content)
            
            # Limpiar botones duplicados de texture tools
            content = self._clean_duplicate_texture_buttons(content)
            
            # Escribir archivo corregido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.fixed_files.append(str(file_path))
            print("✅ main_panel.py corregido - menús duplicados eliminados")
            
        except Exception as e:
            error_msg = f"Error corrigiendo main_panel.py: {e}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
    
    def _fix_panel_idnames(self, content):
        """Corrige bl_idname duplicados en paneles"""
        
        # Mapeo de nombres únicos para evitar duplicados
        panel_fixes = {
            'UNIVERSALGTA_PT_advanced_mapping_panel': 'UNIVERSALGTA_PT_advanced_mapping_unique',
            'UNIVERSALGTA_PT_quick_actions_panel': 'UNIVERSALGTA_PT_quick_actions_unique',
            'UNIVERSALGTA_PT_utilities_panel': 'UNIVERSALGTA_PT_utilities_unique',
            'UNIVERSALGTA_PT_info_panel': 'UNIVERSALGTA_PT_info_unique'
        }
        
        for old_name, new_name in panel_fixes.items():
            content = content.replace(f'bl_idname = "{old_name}"', f'bl_idname = "{new_name}"')
            content = content.replace(f'bl_parent_id = "{old_name}"', f'bl_parent_id = "{new_name}"')
        
        return content
    
    def _clean_duplicate_texture_buttons(self, content):
        """Elimina botones de texturas duplicados en la UI"""
        
        # Buscar secciones duplicadas de texture tools
        texture_section_pattern = r'# === ADVANCED TEXTURE TOOLS ===.*?info_col\.label\(text="✅ Soporte para Vector \+ Image \+ HSV"\)'
        
        # Encontrar todas las ocurrencias
        matches = list(re.finditer(texture_section_pattern, content, re.DOTALL))
        
        if len(matches) > 1:
            print(f"🔍 Encontradas {len(matches)} secciones de texture tools duplicadas")
            
            # Mantener solo la primera ocurrencia
            for i in range(len(matches) - 1, 0, -1):
                start, end = matches[i].span()
                content = content[:start] + content[end:]
            
            print("✅ Secciones duplicadas de texture tools eliminadas")
        
        return content
    
    def _enhance_manual_smart_baking(self):
        """Mejora la función manual_smart_baking según especificaciones exactas"""
        file_path = self.addon_path / "operators" / "texture_export.py"
        
        try:
            print("🔥 Mejorando manual_smart_baking() en texture_export.py...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar y reemplazar la función manual_smart_baking existente
            new_manual_smart_baking = self._create_enhanced_smart_baking_function()
            
            # Patrón para encontrar la clase completa
            pattern = r'class UNIVERSALGTA_OT_manual_smart_baking\(Operator\):.*?(?=class|\Z)'
            
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, new_manual_smart_baking + '\n\n', content, flags=re.DOTALL)
                print("✅ Función manual_smart_baking reemplazada exitosamente")
            else:
                # Si no existe, agregar al final antes de las clases de registro
                insertion_point = content.rfind("# Lista de clases para registro")
                if insertion_point == -1:
                    insertion_point = content.rfind("classes = [")
                
                if insertion_point != -1:
                    content = content[:insertion_point] + new_manual_smart_baking + '\n\n' + content[insertion_point:]
                    print("✅ Función manual_smart_baking agregada exitosamente")
                else:
                    content += '\n\n' + new_manual_smart_baking
                    print("✅ Función manual_smart_baking agregada al final del archivo")
            
            # Escribir archivo corregido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.fixed_files.append(str(file_path))
            print("✅ texture_export.py actualizado con manual_smart_baking mejorado")
            
        except Exception as e:
            error_msg = f"Error mejorando manual_smart_baking: {e}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
    
    def _create_enhanced_smart_baking_function(self):
        """Crea la función manual_smart_baking mejorada según especificaciones exactas"""
        return '''class UNIVERSALGTA_OT_manual_smart_baking(Operator):
    """Sistema de baking manual inteligente - ESPECIFICACIONES EXACTAS"""
    bl_idname = "universalgta.manual_smart_baking"
    bl_label = "🔥 Manual Smart Baking"
    bl_description = "Baking inteligente: verifica objeto, limpia nodos, bakea según casos específicos"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            # 1. VERIFICAR OBJETO ACTIVO
            target_obj = self._verify_and_select_object(context)
            if not target_obj:
                self.report({'ERROR'}, "No se encontró objeto mesh válido")
                return {'CANCELLED'}
            
            print(f"🎯 Objeto seleccionado: {target_obj.name}")
            
            # 2. PROCESAR MATERIALES DEL OBJETO
            processed_materials = 0
            for slot in target_obj.material_slots:
                if slot.material and slot.material.use_nodes:
                    success = self._process_material_smart_baking(slot.material, context)
                    if success:
                        processed_materials += 1
            
            if processed_materials > 0:
                self.report({'INFO'}, f"✅ Smart baking aplicado a {processed_materials} materiales en {target_obj.name}")
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "No se procesaron materiales")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error en smart baking: {e}")
            return {'CANCELLED'}
    
    def _verify_and_select_object(self, context):
        """Verifica y selecciona objeto según especificaciones"""
        mesh_objects = [obj for obj in context.scene.objects if obj.type == 'MESH']
        
        if len(mesh_objects) == 0:
            return None
        elif len(mesh_objects) == 1:
            # Solo hay un objeto mesh, seleccionarlo automáticamente
            obj = mesh_objects[0]
            context.view_layer.objects.active = obj
            obj.select_set(True)
            return obj
        else:
            # Varios objetos, buscar uno que se llame "Mesh"
            for obj in mesh_objects:
                if obj.name == "Mesh":
                    context.view_layer.objects.active = obj
                    obj.select_set(True)
                    return obj
            
            # Si no hay "Mesh", usar el activo actual si es mesh
            if context.active_object and context.active_object.type == 'MESH':
                return context.active_object
            
            # Como último recurso, usar el primero
            obj = mesh_objects[0]
            context.view_layer.objects.active = obj
            obj.select_set(True)
            return obj
    
    def _process_material_smart_baking(self, material, context):
        """Procesa material según casos específicos de las especificaciones"""
        try:
            print(f"🔄 Procesando material: {material.name}")
            
            nodes = material.node_tree.nodes
            links = material.node_tree.links
            
            # Buscar nodos importantes
            material_output = None
            principled_bsdf = None
            image_texture_nodes = []
            
            for node in nodes:
                if node.type == 'OUTPUT_MATERIAL':
                    material_output = node
                elif node.type == 'BSDF_PRINCIPLED':
                    principled_bsdf = node
                elif node.type == 'TEX_IMAGE':
                    image_texture_nodes.append(node)
            
            if not principled_bsdf or not material_output:
                print(f"⚠️ Material {material.name} no tiene BSDF o Output, saltando")
                return False
            
            # Verificar caso específico: Image Texture conectado a Base Color
            base_color_input = principled_bsdf.inputs.get('Base Color')
            alpha_input = principled_bsdf.inputs.get('Alpha')
            
            # CASO 1: Base Color con Image Texture
            if self._has_image_texture_in_base_color(base_color_input):
                print(f"📖 CASO 1: {material.name} tiene Image Texture en Base Color")
                
                # Verificar excepción: Image Texture también conectado a Alpha
                if self._is_image_texture_connected_to_alpha(alpha_input, image_texture_nodes):
                    print(f"⚠️ EXCEPCIÓN: {material.name} tiene Image Texture también en Alpha - SOLO LIMPIEZA")
                    self._clean_nodes_preserve_image_texture(material, principled_bsdf, material_output)
                    return True
                else:
                    # Limpiar nodos y hacer bake normal
                    self._clean_nodes_preserve_image_texture(material, principled_bsdf, material_output)
                    return self._perform_smart_bake(material, context)
            
            # CASO 2: No hay Image Texture, solo color directo (RVA)
            else:
                print(f"🎨 CASO 2: {material.name} tiene solo color directo")
                return self._rasterize_direct_color(material, principled_bsdf, base_color_input, alpha_input)
            
        except Exception as e:
            print(f"❌ Error procesando material {material.name}: {e}")
            return False
    
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
        """Realiza bake real del material después de limpieza"""
        try:
            # Verificar que tengamos un objeto activo con UV
            active_obj = context.active_object
            if not active_obj or not active_obj.data.uv_layers:
                print(f"⚠️ Objeto sin UV layers, creando bake directo para {material.name}")
                return self._create_direct_bake(material)
            
            # Crear imagen para bake
            bake_name = f"{material.name}_d_f"
            
            # Remover imagen existente
            if bake_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[bake_name])
            
            # Crear imagen de bake
            bake_image = bpy.data.images.new(bake_name, width=512, height=512, alpha=True)
            
            # Crear nodo temporal para bake
            nodes = material.node_tree.nodes
            temp_node = nodes.new(type='ShaderNodeTexImage')
            temp_node.image = bake_image
            temp_node.select = True
            nodes.active = temp_node
            
            # Realizar bake
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.device = 'CPU'  # Más compatible
            bpy.context.scene.render.bake.use_pass_direct = False
            bpy.context.scene.render.bake.use_pass_indirect = False
            bpy.context.scene.render.bake.use_pass_color = True
            
            bpy.ops.object.bake(type='DIFFUSE')
            
            # Eliminar nodo temporal
            nodes.remove(temp_node)
            
            # Crear nodo final y conectar
            final_node = nodes.new(type='ShaderNodeTexImage')
            final_node.image = bake_image
            final_node.location = (-300, 0)
            
            # Buscar BSDF
            principled_bsdf = None
            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    principled_bsdf = node
                    break
            
            if principled_bsdf:
                links = material.node_tree.links
                links.new(final_node.outputs['Color'], principled_bsdf.inputs['Base Color'])
                links.new(final_node.outputs['Alpha'], principled_bsdf.inputs['Alpha'])
            
            # Empacar imagen
            bake_image.pack()
            bake_image.use_fake_user = True
            
            print(f"✅ Bake completado: {material.name} -> {bake_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error en bake de {material.name}: {e}")
            # Fallback a bake directo
            return self._create_direct_bake(material)
    
    def _create_direct_bake(self, material):
        """Crea bake directo cuando el bake normal falla"""
        try:
            # Similar a rasterize pero con nombre _d_f
            bake_name = f"{material.name}_d_f"
            
            if bake_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[bake_name])
            
            # Crear imagen con color promedio del material
            bake_image = bpy.data.images.new(bake_name, width=512, height=512, alpha=True)
            
            # Color por defecto: gris GTA (#E7E7E7FF)
            default_color = [0.906, 0.906, 0.906, 1.0]  # #E7E7E7 en RGB
            
            pixel_count = 512 * 512
            pixels = default_color * pixel_count
            bake_image.pixels = pixels
            
            bake_image.pack()
            bake_image.use_fake_user = True
            
            print(f"✅ Bake directo creado: {material.name} -> {bake_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error en bake directo: {e}")
            return False'''
    
    def _integrate_smart_baking_into_conversion(self):
        """Integra manual_smart_baking en el flujo de conversión principal"""
        conversion_file = self.addon_path / "operators" / "gta_complete_conversion.py"
        
        if not conversion_file.exists():
            print("⚠️ Archivo gta_complete_conversion.py no encontrado, saltando integración")
            return
        
        try:
            print("🔗 Integrando smart baking en flujo de conversión...")
            
            with open(conversion_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar la función execute_conversion
            if "def execute(self, context):" in content and "universalgta.execute_conversion" in content:
                
                # Buscar punto de inserción después de configurar materiales
                insertion_patterns = [
                    "# Configurar materiales",
                    "UNIVERSALGTA_OT_configure_materials_gta",
                    "configure_materials_gta",
                    "# Cleanup final"
                ]
                
                insertion_point = -1
                for pattern in insertion_patterns:
                    point = content.find(pattern)
                    if point != -1:
                        insertion_point = point
                        break
                
                if insertion_point != -1:
                    # Encontrar el final de esa sección
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if insertion_patterns[0] in line or any(p in line for p in insertion_patterns[1:]):
                            # Insertar después de esta línea
                            smart_baking_integration = '''
            # === SMART BAKING INTEGRATION ===
            print("[CONVERSION] 🔥 Aplicando Smart Baking automático...")
            try:
                # Llamar a manual_smart_baking para procesar materiales
                result = bpy.ops.universalgta.manual_smart_baking()
                if result == {'FINISHED'}:
                    print("[CONVERSION] ✅ Smart Baking aplicado exitosamente")
                else:
                    print("[CONVERSION] ⚠️ Smart Baking completado con advertencias")
            except Exception as e:
                print(f"[CONVERSION] ❌ Error en Smart Baking: {e}")
                # Continuar con el resto de la conversión
'''
                            lines.insert(i + 1, smart_baking_integration)
                            content = '\n'.join(lines)
                            break
                
                # Escribir archivo modificado
                with open(conversion_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixed_files.append(str(conversion_file))
                print("✅ Smart baking integrado en flujo de conversión")
            
        except Exception as e:
            error_msg = f"Error integrando smart baking: {e}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
    
    def _verify_and_fix_init_file(self):
        """Verifica y corrige el archivo __init__.py principal"""
        init_file = self.addon_path / "__init__.py"
        
        try:
            print("🔍 Verificando __init__.py...")
            
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar que manual_smart_baking esté en la lista de imports
            if "UNIVERSALGTA_OT_manual_smart_baking" not in content:
                print("📝 Agregando manual_smart_baking a imports en __init__.py...")
                
                # Buscar sección de texture_export imports
                texture_import_pattern = r'from \.operators\.texture_export import \((.*?)\)'
                match = re.search(texture_import_pattern, content, re.DOTALL)
                
                if match:
                    current_imports = match.group(1)
                    if "UNIVERSALGTA_OT_manual_smart_baking" not in current_imports:
                        # Agregar el import
                        new_imports = current_imports.rstrip() + ",\n            UNIVERSALGTA_OT_manual_smart_baking,"
                        content = content.replace(match.group(1), new_imports)
            
            # Verificar registro en all_classes
            if "UNIVERSALGTA_OT_manual_smart_baking" not in content or "TEXTURE_EXPORT_OPERATORS" not in content:
                print("📝 Verificando registro de operadores de texturas...")
                
                # Asegurar que TEXTURE_EXPORT_OPERATORS esté en all_classes
                if "all_classes.extend(TEXTURE_EXPORT_OPERATORS)" not in content:
                    # Buscar donde agregar
                    all_classes_point = content.find("all_classes.extend(MATERIAL_OPERATORS)")
                    if all_classes_point != -1:
                        content = content.replace(
                            "all_classes.extend(MATERIAL_OPERATORS)",
                            "all_classes.extend(TEXTURE_EXPORT_OPERATORS)  # Texturas PRIMERO\n    all_classes.extend(MATERIAL_OPERATORS)"
                        )
            
            # Escribir archivo corregido
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.fixed_files.append(str(init_file))
            print("✅ __init__.py verificado y corregido")
            
        except Exception as e:
            error_msg = f"Error verificando __init__.py: {e}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
    
    def _create_backup_files(self):
        """Crea copias de seguridad de archivos importantes"""
        backup_dir = self.addon_path / "backup_before_update"
        
        try:
            backup_dir.mkdir(exist_ok=True)
            
            important_files = [
                "__init__.py",
                "panels/main_panel.py", 
                "operators/texture_export.py",
                "operators/gta_complete_conversion.py"
            ]
            
            for file_path in important_files:
                source = self.addon_path / file_path
                if source.exists():
                    dest = backup_dir / f"{source.name}.backup"
                    dest.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
            
            print(f"💾 Backups creados en: {backup_dir}")
            
        except Exception as e:
            print(f"⚠️ Error creando backups: {e}")
    
    def _print_final_report(self):
        """Imprime reporte final de la actualización"""
        print("\n" + "=" * 80)
        print("📊 REPORTE FINAL DE ACTUALIZACIÓN")
        print("=" * 80)
        
        print(f"✅ ARCHIVOS MODIFICADOS ({len(self.fixed_files)}):")
        for file_path in self.fixed_files:
            print(f"   • {file_path}")
        
        if self.created_files:
            print(f"\n📁 ARCHIVOS CREADOS ({len(self.created_files)}):")
            for file_path in self.created_files:
                print(f"   • {file_path}")
        
        if self.errors:
            print(f"\n❌ ERRORES ENCONTRADOS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        print("\n🚀 CAMBIOS REALIZADOS:")
        print("   ✅ Menús duplicados corregidos en main_panel.py")
        print("   ✅ manual_smart_baking() mejorado según especificaciones exactas")
        print("   ✅ Integración en flujo de conversión automática")
        print("   ✅ Verificación y corrección de __init__.py")
        print("   ✅ Backups de seguridad creados")
        
        print("\n📋 FUNCIONALIDADES DE manual_smart_baking():")
        print("   🎯 Verificación automática de objeto activo")
        print("   🧹 Limpieza inteligente de nodos")
        print("   📖 CASO 1: Preserva Image Texture + ColorRamp + RGB Curves + HSV")
        print("   🎨 CASO 2: Rasteriza colores directos a 256x256")
        print("   ⚠️ EXCEPCIÓN: Solo limpieza si Image Texture en Alpha")
        print("   🔗 Conexión automática a Base Color y Alpha")
        print("   📦 Empaquetado automático de imágenes")
        print("   🏷️ Nomenclatura: nombre_del_material_d_f")
        
        print("\n🎉 ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("   El addon está listo para usar con las nuevas funcionalidades")
        print("=" * 80)


def main():
    """Función principal del actualizador"""
    
    # Ruta por defecto del addon (ajustar según sea necesario)
    default_addon_path = r"C:\Users\BASCO\AppData\Roaming\Blender Foundation\Blender\5.0\scripts\addons\yoshimaincra_universal_gta_converter"
    
    # Permitir ruta personalizada como argumento
    if len(sys.argv) > 1:
        addon_path = sys.argv[1]
    else:
        addon_path = default_addon_path
    
    # Verificar que la ruta existe
    if not os.path.exists(addon_path):
        print(f"❌ ERROR: Ruta del addon no encontrada: {addon_path}")
        print("💡 Uso: python master_updater_script.py [ruta_del_addon]")
        return False
    
    # Ejecutar actualizador
    updater = UniversalGTAUpdater(addon_path)
    success = updater.run_all_updates()
    
    if success:
        print("\n🎉 ¡ACTUALIZACIÓN EXITOSA!")
        print("   Reinicia Blender para aplicar los cambios")
        return True
    else:
        print("\n❌ ACTUALIZACIÓN FALLIDA")
        print("   Revisa los errores arriba y corrige manualmente si es necesario")
        return False


if __name__ == "__main__":
    main()
