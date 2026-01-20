"""
Sistema de Consolidación Jerárquica de Bone Mappings v2.0
==========================================================
Algoritmo PURAMENTE JERÁRQUICO que NO depende de nombres de huesos.
Se basa en la estructura del árbol, relaciones padre-hijo, y análisis de chains.

Autor: YoshiMaincra + Cursor AI
Versión: 2.0 - Hierarchy-Based (no name-based)
"""
import bpy
from typing import Dict, List, Set, Optional, Tuple
from bpy.types import Operator, Armature
from bpy.props import BoolProperty, FloatProperty, IntProperty


class HierarchyNode:
    """Representa un nodo en el árbol de jerarquía con metadata"""
    
    def __init__(self, bone_name: str):
        self.bone_name = bone_name
        self.parent = None
        self.children = []
        self.depth = 0
        self.is_leaf = True
        self.chain_position = 0  # Posición en un chain lineal
        self.is_terminal = False  # Último hueso de un chain
        self.sibling_count = 0
        self.has_multiple_children = False
        
    def __repr__(self):
        return f"HierarchyNode({self.bone_name}, depth={self.depth}, children={len(self.children)})"


class BoneHierarchyAnalyzer:
    """Analiza la estructura jerárquica del armature sin depender de nombres"""
    
    def __init__(self, armature_obj):
        self.armature_obj = armature_obj
        self.nodes = {}  # bone_name -> HierarchyNode
        self.roots = []
        self._build_hierarchy()
        self._analyze_structure()
    
    def _build_hierarchy(self):
        """Construir árbol jerárquico"""
        if not self.armature_obj or self.armature_obj.type != 'ARMATURE':
            return
        
        armature = self.armature_obj.data
        
        # Crear nodos
        for bone in armature.bones:
            self.nodes[bone.name] = HierarchyNode(bone.name)
        
        # Establecer relaciones
        for bone in armature.bones:
            node = self.nodes[bone.name]
            
            if bone.parent:
                parent_node = self.nodes[bone.parent.name]
                node.parent = parent_node
                parent_node.children.append(node)
                parent_node.is_leaf = False
            else:
                self.roots.append(node)
    
    def _analyze_structure(self):
        """Analizar estructura del árbol"""
        # Calcular profundidades
        for root in self.roots:
            self._calculate_depth(root, 0)
        
        # Analizar chains
        for root in self.roots:
            self._analyze_chains(root)
        
        # Contar siblings
        for node in self.nodes.values():
            if node.parent:
                node.sibling_count = len(node.parent.children)
            node.has_multiple_children = len(node.children) > 1
    
    def _calculate_depth(self, node: HierarchyNode, depth: int):
        """Calcular profundidad de cada nodo"""
        node.depth = depth
        for child in node.children:
            self._calculate_depth(child, depth + 1)
    
    def _analyze_chains(self, node: HierarchyNode, chain_pos: int = 0):
        """
        Analizar chains lineales (secuencias padre->hijo único->nieto único)
        """
        node.chain_position = chain_pos
        
        if len(node.children) == 0:
            # Es leaf, terminal del chain
            node.is_terminal = True
        elif len(node.children) == 1:
            # Continúa el chain
            self._analyze_chains(node.children[0], chain_pos + 1)
        else:
            # Bifurcación, cada hijo inicia nuevo chain
            for child in node.children:
                self._analyze_chains(child, 0)
    
    def get_node(self, bone_name: str) -> Optional[HierarchyNode]:
        """Obtener nodo por nombre de hueso"""
        return self.nodes.get(bone_name)
    
    def get_ancestors(self, bone_name: str) -> List[HierarchyNode]:
        """Obtener ancestros de un hueso (cercano a lejano)"""
        node = self.get_node(bone_name)
        if not node:
            return []
        
        ancestors = []
        current = node.parent
        
        while current:
            ancestors.append(current)
            current = current.parent
        
        return ancestors
    
    def is_linear_descendant(self, bone_name: str, ancestor_name: str) -> bool:
        """
        Verificar si bone_name es descendiente LINEAL de ancestor_name
        (todos los nodos intermedios tienen un solo hijo)
        """
        node = self.get_node(bone_name)
        ancestor = self.get_node(ancestor_name)
        
        if not node or not ancestor:
            return False
        
        current = node.parent
        while current:
            if current == ancestor:
                return True
            # Si tiene múltiples hijos, no es lineal
            if len(current.children) > 1:
                return False
            current = current.parent
        
        return False
    
    def get_chain_siblings(self, bone_name: str) -> List[HierarchyNode]:
        """
        Obtener hermanos en el mismo chain (mismo padre, profundidad similar)
        """
        node = self.get_node(bone_name)
        if not node or not node.parent:
            return []
        
        return [child for child in node.parent.children if child != node]
    
    def classify_node_type(self, node: HierarchyNode) -> str:
        """
        Clasificar tipo de nodo BASÁNDOSE EN ESTRUCTURA JERÁRQUICA
        No usa nombres de huesos
        """
        # LEAF: Sin hijos
        if node.is_leaf:
            return 'LEAF'
        
        # BIFURCATION: Múltiples hijos (punto de ramificación importante)
        if node.has_multiple_children:
            return 'BIFURCATION'
        
        # CHAIN_START: Inicio de una secuencia lineal larga
        if node.chain_position == 0 and len(node.children) == 1:
            # Contar longitud del chain
            chain_length = self._get_chain_length(node)
            if chain_length > 3:
                return 'CHAIN_START'
        
        # CHAIN_MID: Medio de un chain lineal
        if node.chain_position > 0 and len(node.children) == 1:
            return 'CHAIN_MID'
        
        # CHAIN_END: Final de chain pero no es leaf
        if node.chain_position > 0 and node.is_terminal:
            return 'CHAIN_END'
        
        # BRIDGE: Conecta dos regiones (tiene 1 hijo, pero es importante)
        if len(node.children) == 1:
            return 'BRIDGE'
        
        return 'UNKNOWN'
    
    def _get_chain_length(self, node: HierarchyNode) -> int:
        """Calcular longitud de un chain lineal"""
        length = 1
        current = node
        
        while len(current.children) == 1:
            current = current.children[0]
            length += 1
        
        return length


class HierarchicalIntelligentConsolidator:
    """
    Consolidador inteligente basado SOLO en jerarquía.
    NO usa nombres de huesos para clasificación.
    """
    
    def __init__(self, source_armature, target_armature, base_mappings: Dict[str, str]):
        self.source_armature = source_armature
        self.target_armature = target_armature
        self.base_mappings = base_mappings.copy()
        
        self.hierarchy = BoneHierarchyAnalyzer(source_armature)
        
        self.consolidated_mappings = {}
        self.mapping_metadata = {}
        
        # Configuración
        self.inherit_leafs = True  # Hojas heredan del padre
        self.inherit_chain_siblings = True  # Hermanos en chain heredan
        self.inherit_linear_descendants = True  # Descendientes lineales heredan
        self.max_inheritance_depth = 10  # Máxima distancia para heredar
    
    def consolidate(self) -> Dict[str, str]:
        """
        Ejecutar consolidación PURAMENTE JERÁRQUICA
        """
        print("\n" + "="*60)
        print("🔄 CONSOLIDACIÓN JERÁRQUICA v2.0 (Hierarchy-Based)")
        print("="*60)
        
        # Inicializar con mappings base
        self.consolidated_mappings = self.base_mappings.copy()
        
        # Marcar mappings base en metadata
        for bone in self.base_mappings:
            self.mapping_metadata[bone] = {
                'method': 'base',
                'weight': 1.0,
                'depth': 0
            }
        
        # Estadísticas
        stats = {
            'linear_inherited': 0,
            'leaf_inherited': 0,
            'sibling_inherited': 0,
            'ancestor_inherited': 0,
            'bifurcation_kept': 0,
            'unmapped': 0
        }
        
        # Procesar todos los nodos
        for bone_name, node in self.hierarchy.nodes.items():
            if bone_name in self.consolidated_mappings:
                continue  # Ya tiene mapping
            
            result = self._process_unmapped_bone(node)
            if result:
                stats[result] += 1
        
        # Reportar
        self._print_statistics(stats, len(self.hierarchy.nodes))
        
        return self.consolidated_mappings
    
    def _process_unmapped_bone(self, node: HierarchyNode) -> Optional[str]:
        """
        Procesar hueso sin mapping usando SOLO análisis jerárquico
        """
        bone_name = node.bone_name
        
        # REGLA 1: LEAF BONES (sin hijos)
        if node.is_leaf and self.inherit_leafs:
            if node.parent:
                ancestor_mapping = self._find_mapped_ancestor(node)
                if ancestor_mapping:
                    target, ancestor, distance = ancestor_mapping
                    self.consolidated_mappings[bone_name] = target
                    self.mapping_metadata[bone_name] = {
                        'method': 'leaf_inherited',
                        'inherited_from': ancestor.bone_name,
                        'weight': self._calculate_weight('LEAF', distance),
                        'depth': distance
                    }
                    return 'leaf_inherited'
        
        # REGLA 2: DESCENDIENTES LINEALES
        # Si es parte de un chain lineal descendiente de un bone mapeado
        if self.inherit_linear_descendants:
            linear_ancestor = self._find_linear_mapped_ancestor(node)
            if linear_ancestor:
                target, ancestor, distance = linear_ancestor
                self.consolidated_mappings[bone_name] = target
                self.mapping_metadata[bone_name] = {
                    'method': 'linear_inherited',
                    'inherited_from': ancestor.bone_name,
                    'weight': self._calculate_weight('LINEAR', distance),
                    'depth': distance,
                    'chain_position': node.chain_position
                }
                return 'linear_inherited'
        
        # REGLA 3: HERMANOS EN CHAIN
        # Si tiene hermanos mapeados (mismo padre, estructura similar)
        if self.inherit_chain_siblings:
            sibling_mapping = self._find_sibling_mapping(node)
            if sibling_mapping:
                target, sibling = sibling_mapping
                self.consolidated_mappings[bone_name] = target
                self.mapping_metadata[bone_name] = {
                    'method': 'sibling_inherited',
                    'inherited_from': sibling.bone_name,
                    'weight': self._calculate_weight('SIBLING', 1),
                    'depth': 1
                }
                return 'sibling_inherited'
        
        # REGLA 4: ANCESTRO GENERAL
        # Heredar del ancestro mapeado más cercano
        ancestor_mapping = self._find_mapped_ancestor(node)
        if ancestor_mapping:
            target, ancestor, distance = ancestor_mapping
            
            if distance <= self.max_inheritance_depth:
                self.consolidated_mappings[bone_name] = target
                self.mapping_metadata[bone_name] = {
                    'method': 'ancestor_inherited',
                    'inherited_from': ancestor.bone_name,
                    'weight': self._calculate_weight('ANCESTOR', distance),
                    'depth': distance
                }
                return 'ancestor_inherited'
        
        # REGLA 5: BIFURCACIONES
        # Puntos de bifurcación importantes se mantienen sin mapear
        # (requieren mapping manual por ser estructuralmente importantes)
        node_type = self.hierarchy.classify_node_type(node)
        if node_type == 'BIFURCATION':
            self.mapping_metadata[bone_name] = {
                'method': 'bifurcation_unmapped',
                'weight': 0.0,
                'requires_manual': True
            }
            return 'bifurcation_kept'
        
        # Sin mapping
        self.mapping_metadata[bone_name] = {
            'method': 'unmapped',
            'weight': 0.0
        }
        return 'unmapped'
    
    def _find_mapped_ancestor(self, node: HierarchyNode) -> Optional[Tuple[str, HierarchyNode, int]]:
        """
        Encontrar ancestro más cercano con mapping.
        Returns: (target_bone, ancestor_node, distance)
        """
        ancestors = self.hierarchy.get_ancestors(node.bone_name)
        
        for i, ancestor in enumerate(ancestors):
            if ancestor.bone_name in self.consolidated_mappings:
                target = self.consolidated_mappings[ancestor.bone_name]
                distance = i + 1
                return (target, ancestor, distance)
        
        return None
    
    def _find_linear_mapped_ancestor(self, node: HierarchyNode) -> Optional[Tuple[str, HierarchyNode, int]]:
        """
        Encontrar ancestro mapeado en chain LINEAL (sin bifurcaciones).
        Solo retorna si NO hay bifurcaciones entre el nodo y el ancestro.
        """
        ancestors = self.hierarchy.get_ancestors(node.bone_name)
        
        for i, ancestor in enumerate(ancestors):
            # Verificar que no haya bifurcaciones en el camino
            if i > 0:
                previous = ancestors[i-1]
                if len(previous.children) > 1:
                    # Hay bifurcación, detener búsqueda
                    break
            
            if ancestor.bone_name in self.consolidated_mappings:
                target = self.consolidated_mappings[ancestor.bone_name]
                distance = i + 1
                return (target, ancestor, distance)
        
        return None
    
    def _find_sibling_mapping(self, node: HierarchyNode) -> Optional[Tuple[str, HierarchyNode]]:
        """
        Encontrar hermano mapeado (mismo padre).
        Útil para chains paralelos (ej: dedos de una mano)
        """
        if not node.parent:
            return None
        
        siblings = self.hierarchy.get_chain_siblings(node.bone_name)
        
        for sibling in siblings:
            if sibling.bone_name in self.consolidated_mappings:
                target = self.consolidated_mappings[sibling.bone_name]
                return (target, sibling)
        
        return None
    
    def _calculate_weight(self, inheritance_type: str, distance: int) -> float:
        """
        Calcular peso basándose en tipo de herencia y distancia.
        NO usa nombres de huesos, solo estructura.
        """
        base_weights = {
            'LEAF': 0.3,       # Hojas tienen bajo peso (usualmente end bones)
            'LINEAR': 0.8,     # Descendientes lineales tienen alto peso
            'SIBLING': 0.9,    # Hermanos tienen muy alto peso
            'ANCESTOR': 0.6,   # Ancestros generales tienen peso medio
        }
        
        base_weight = base_weights.get(inheritance_type, 0.5)
        
        # Aplicar decay por distancia
        decay_factor = 1.0 / (1.0 + distance * 0.15)
        
        return round(base_weight * decay_factor, 2)
    
    def _print_statistics(self, stats: Dict[str, int], total_bones: int):
        """Imprimir estadísticas del proceso"""
        print("\n📊 ESTADÍSTICAS DE CONSOLIDACIÓN:")
        print("-" * 60)
        print(f"  📌 Total de huesos:            {total_bones}")
        
        base_count = len(self.base_mappings)
        print(f"  ✅ Mappings base:              {base_count} ({base_count/total_bones*100:.1f}%)")
        print(f"  🔗 Heredados lineales:         {stats['linear_inherited']} ({stats['linear_inherited']/total_bones*100:.1f}%)")
        print(f"  🍃 Hojas heredadas:            {stats['leaf_inherited']} ({stats['leaf_inherited']/total_bones*100:.1f}%)")
        print(f"  👥 Hermanos heredados:         {stats['sibling_inherited']} ({stats['sibling_inherited']/total_bones*100:.1f}%)")
        print(f"  ⬆️  Ancestros heredados:        {stats['ancestor_inherited']} ({stats['ancestor_inherited']/total_bones*100:.1f}%)")
        print(f"  🔱 Bifurcaciones (no mapeadas): {stats['bifurcation_kept']} ({stats['bifurcation_kept']/total_bones*100:.1f}%)")
        print(f"  ❌ Sin mapeo:                  {stats['unmapped']} ({stats['unmapped']/total_bones*100:.1f}%)")
        print(f"  🎯 Total consolidado:          {len(self.consolidated_mappings)} ({len(self.consolidated_mappings)/total_bones*100:.1f}%)")
        print("=" * 60 + "\n")
    
    def export_mappings_with_metadata(self) -> List[dict]:
        """Exportar mappings en formato del addon"""
        mappings_list = []
        
        for idx, (source, target) in enumerate(self.consolidated_mappings.items()):
            metadata = self.mapping_metadata.get(source, {})
            
            # Generar descripción del método
            method = metadata.get('method', 'Unknown')
            inherited_from = metadata.get('inherited_from')
            
            if inherited_from:
                detection_method = f"Inherited from {inherited_from} ({method})"
            else:
                detection_method = method.replace('_', ' ').title()
            
            mapping_entry = {
                "index": idx,
                "source_bone": source,
                "target_bone": target,
                "enabled": True,
                "detection_method": detection_method,
                "confidence": metadata.get('weight', 1.0)
            }
            
            mappings_list.append(mapping_entry)
        
        return mappings_list


class UNIVERSALGTA_OT_consolidate_bone_mappings(Operator):
    """Mapea automáticamente huesos faltantes usando la jerarquía del esqueleto"""
    bl_idname = "universalgta.consolidate_bone_mappings"
    bl_label = "🔄 Consolidate by Hierarchy"
    bl_description = "Completa automáticamente los mapeos que faltan. Analiza la estructura del esqueleto, no los nombres de los huesos. Funciona con cualquier idioma/nomenclatura"
    bl_options = {'REGISTER', 'UNDO'}
    
    inherit_leafs: BoolProperty(
        name="Inherit Leaf Bones",
        description="Huesos finales (sin hijos) heredan del hueso padre",
        default=True
    )
    
    inherit_linear: BoolProperty(
        name="Inherit Linear Chains",
        description="Cadenas lineales (ej: Brazo → Brazo.001 → Brazo.002) heredan del primero",
        default=True
    )
    
    inherit_siblings: BoolProperty(
        name="Inherit Siblings",
        description="Huesos hermanos (mismo padre) heredan entre sí (ej: dedos de una mano)",
        default=True
    )
    
    max_depth: IntProperty(
        name="Max Depth",
        description="Qué tan 'lejos' puede buscar un hueso padre. Aumenta si tienes cadenas muy largas",
        default=10,
        min=1,
        max=50
    )
    
    min_confidence: FloatProperty(
        name="Min Confidence",
        description="Solo incluye mapeos con confianza mayor a este valor. Aumenta para ser más selectivo",
        default=0.2,
        min=0.0,
        max=1.0
    )
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        # Validaciones
        if not settings.source_armature:
            self.report({'ERROR'}, "No hay source armature seleccionado")
            return {'CANCELLED'}
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No hay target armature seleccionado")
            return {'CANCELLED'}
        
        # Construir diccionario de mappings base
        base_mappings = {}
        for mapping in settings.bone_mappings:
            if mapping.enabled and mapping.source_bone and mapping.target_bone:
                base_mappings[mapping.source_bone] = mapping.target_bone
        
        if len(base_mappings) == 0:
            self.report({'ERROR'}, "No hay mappings base para consolidar. Ejecuta Smart Auto-Detect primero.")
            return {'CANCELLED'}
        
        # Crear consolidador
        consolidator = HierarchicalIntelligentConsolidator(
            settings.source_armature,
            settings.target_armature,
            base_mappings
        )
        
        # Configurar opciones
        consolidator.inherit_leafs = self.inherit_leafs
        consolidator.inherit_linear_descendants = self.inherit_linear
        consolidator.inherit_chain_siblings = self.inherit_siblings
        consolidator.max_inheritance_depth = self.max_depth
        
        # Consolidar
        consolidated = consolidator.consolidate()
        
        # Aplicar al settings
        new_count = self._apply_to_settings(settings, consolidator, self.min_confidence)
        
        self.report({'INFO'}, f"✅ Consolidación completada: {len(consolidated)} mappings totales ({new_count} nuevos)")
        return {'FINISHED'}
    
    def _apply_to_settings(self, settings, consolidator, min_confidence):
        """Aplicar mappings consolidados a los settings"""
        new_mappings_to_add = []
        updated_count = 0
        
        export_mappings = consolidator.export_mappings_with_metadata()
        
        # Primero, recopilar todos los nuevos mappings
        for mapping_data in export_mappings:
            # Filtrar por confianza mínima
            if mapping_data['confidence'] < min_confidence:
                continue
            
            # Verificar si ya existe
            existing = None
            for m in settings.bone_mappings:
                if m.source_bone == mapping_data['source_bone']:
                    existing = m
                    break
            
            if existing:
                # Actualizar si tiene mayor confianza
                if mapping_data['confidence'] > existing.confidence:
                    existing.target_bone = mapping_data['target_bone']
                    existing.confidence = mapping_data['confidence']
                    existing.detection_method = mapping_data['detection_method']
                    updated_count += 1
            else:
                # Guardar para agregar después (al inicio)
                new_mappings_to_add.append(mapping_data)
        
        # Agregar nuevos mappings AL INICIO de la lista (arriba del todo)
        # Los agregamos en orden inverso para que queden en el orden correcto
        for mapping_data in reversed(new_mappings_to_add):
            # Crear nuevo mapping al final primero
            new_mapping = settings.bone_mappings.add()
            new_mapping.source_bone = mapping_data['source_bone']
            new_mapping.target_bone = mapping_data['target_bone']
            new_mapping.confidence = mapping_data['confidence']
            new_mapping.detection_method = mapping_data['detection_method']
            new_mapping.enabled = True
            
            # Moverlo al inicio (índice 0)
            # Obtenemos el índice actual (último)
            current_index = len(settings.bone_mappings) - 1
            
            # Moverlo al principio
            while current_index > 0:
                settings.bone_mappings.move(current_index, current_index - 1)
                current_index -= 1
        
        new_count = len(new_mappings_to_add)
        
        if new_count > 0:
            print(f"\n✨ NUEVOS MAPPINGS CONSOLIDADOS:")
            print(f"   📍 {new_count} nuevos mappings agregados ARRIBA DEL TODO")
            print(f"   🔄 {updated_count} mappings actualizados")
            print(f"   📜 Desplázate hacia arriba para verlos\n")
        
        return new_count



def register():
    bpy.utils.register_class(UNIVERSALGTA_OT_consolidate_bone_mappings)

def unregister():
    bpy.utils.unregister_class(UNIVERSALGTA_OT_consolidate_bone_mappings)
