import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, PointerProperty, BoolProperty, CollectionProperty, FloatProperty, IntProperty, EnumProperty

def validate_name_input(self, context):
    """Validador para nombres de skin y autor - VERSIÓN CORREGIDA"""
    import re
    
    try:
        # Validar skin_name
        if hasattr(self, 'skin_name') and self.skin_name:
            if not re.match(r'^[a-zA-Z0-9_-]+$', self.skin_name):
                self.name_validation_message = "❌ Skin name: Solo se permiten letras, números, _ y -"
                # Limpiar caracteres inválidos
                self.skin_name = re.sub(r'[^a-zA-Z0-9_-]', '', self.skin_name)
            else:
                self.name_validation_message = "✅ Skin name válido"

        # Validar author_nickname
        if hasattr(self, 'author_nickname') and self.author_nickname:
            if not re.match(r'^[a-zA-Z0-9_-]+$', self.author_nickname):
                if "❌" not in self.name_validation_message:
                    self.name_validation_message = "❌ Author nickname: Solo se permiten letras, números, _ y -"
                # Limpiar caracteres inválidos
                self.author_nickname = re.sub(r'[^a-zA-Z0-9_-]', '', self.author_nickname)
            else:
                if "❌" not in self.name_validation_message:
                    self.name_validation_message = "✅ Nombres válidos"
    except Exception as e:
        print(f"[CONFIG] Error en validación de nombres: {e}")
        # No fallar, solo reportar


class BoneMappingItem(PropertyGroup):
    """Elemento de mapeo de huesos - VERSIÓN CORREGIDA"""
    source_bone: StringProperty(
        name="Source Bone",
        description="Nombre del hueso en el armature fuente",
        default=""
    )
    target_bone: StringProperty(
        name="Target Bone",
        description="Nombre del hueso en el armature destino",
        default=""
    )
    enabled: BoolProperty(
        name="Enabled", 
        description="Si este mapeo está habilitado para la conversión",
        default=True
    )
    detection_method: StringProperty(
        name="Detection Method", 
        description="Método usado para detectar este mapeo",
        default="Manual"
    )
    confidence: FloatProperty(
        name="Confidence", 
        description="Nivel de confianza en la detección automática",
        default=0.0,
        min=0.0,
        max=1.0
    )


class UniversalGTASettings(PropertyGroup):

    # Colección de huesos fuente para UI doble lista
    source_bones_collection: CollectionProperty(
        type=BoneMappingItem,
        name="Source Bones",
        description="Lista de huesos del armature fuente para drag & drop"
    )
    source_bones_index: IntProperty(
        name="Source Bone Index",
        default=0,
        min=0
    )
    # Colección de huesos destino para UI doble lista
    target_bones_collection: CollectionProperty(
        type=BoneMappingItem,
        name="Target Bones",
        description="Lista de huesos del armature destino para drag & drop"
    )
    target_bones_index: IntProperty(
        name="Target Bone Index",
        default=0,
        min=0
    )
    """Configuración principal del addon - VERSIÓN CORREGIDA Y COMPLETA"""
    
    # Espaciado
    arm_spacing: FloatProperty(
        name="Arm Spacing", 
        description="Espaciado horizontal de los brazos",
        default=0.0, 
        min=-1.0, 
        max=1.0
    )
    leg_spacing: FloatProperty(
        name="Leg Spacing", 
        description="Espaciado horizontal de las piernas",
        default=0.0, 
        min=-1.0, 
        max=1.0
    )

    # Armatures
    source_armature: PointerProperty(
        type=bpy.types.Object,
        name="Source Armature",
        description="Armature fuente a convertir",
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )
    target_armature: PointerProperty(
        type=bpy.types.Object,
        name="Target Armature", 
        description="Armature destino con estructura GTA SA",
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )
    
    # Opciones de conversión básicas
    keep_vertex_colors: BoolProperty(
        name="Mantener Vertex Colors", 
        description="Preservar vertex colors durante la conversión",
        default=False
    )
    debug_mode: BoolProperty(
        name="Debug Mode", 
        description="Activar modo debug con información detallada",
        default=False
    )
    auto_detect_mode: BoolProperty(
        name="Auto Detect", 
        description="Detectar automáticamente mapeos de huesos",
        default=True
    )
    detection_threshold: FloatProperty(
        name="Detection Threshold", 
        description="Umbral mínimo para detección automática",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    # Mapeos de huesos
    bone_mappings: CollectionProperty(
        type=BoneMappingItem,
        name="Bone Mappings",
        description="Lista de mapeos entre huesos fuente y destino"
    )
    bone_mappings_index: IntProperty(
        name="Index", 
        description="Índice del mapeo seleccionado",
        default=0,
        min=0
    )
    
    # Auto-aplicar pose personalizada
    auto_apply_custom_pose: BoolProperty(
        name="Auto Apply Custom Pose", 
        description="Aplica automáticamente la pose personalizada después de la conversión",
        default=True
    )
    
    # CORRECCIÓN DE NORMALES
    auto_fix_normals: BoolProperty(
        name="Auto Fix Normals",
        description="Recalcula automáticamente las normales hacia afuera después de la conversión",
        default=True
    )
    
    duplicate_inverted_normals: BoolProperty(
        name="Duplicate with Inverted Normals",
        description="Crea una copia duplicada con normales invertidas para asegurar visibilidad de todas las caras",
        default=False
    )
    
    # NOMBRES PERSONALIZADOS CON VALIDACIÓN
    skin_name: StringProperty(
        name="Skin Name",
        description="Nombre del skin (solo caracteres alfanuméricos, guiones y guiones bajos)",
        default="MySkin",
        maxlen=32,
        update=validate_name_input
    )
    
    author_nickname: StringProperty(
        name="Author Nickname", 
        description="Nickname del autor (solo caracteres alfanuméricos, guiones y guiones bajos)",
        default="Author",
        maxlen=32,
        update=validate_name_input
    )
    
    # ANIMACIONES PREDEFINIDAS
    predefined_animation: EnumProperty(
        name="Predefined Animation",
        description="Selecciona una animación predefinida para cargar",
        items=[
            ('NONE', 'None', 'Sin animación'),
            ('IDLE', 'Idle', 'Pose de espera'),
            ('WALK', 'Walk', 'Caminata'),
            ('RUNNING', 'Running', 'Corriendo'),
            ('JUMP', 'Jump', 'Salto'),
            ('CHAT', 'Chat', 'Hablando'),
            ('FACIAL', 'Facial', 'Expresión facial'),
        ],
        default='NONE'
    )
    
    # EXPRESIVIDAD FACIAL
    facial_expressiveness: FloatProperty(
        name="Facial Expressiveness",
        description="Ajusta la expresividad facial modificando el roll de huesos faciales",
        default=0.0,
        min=-1.0,
        max=1.0
    )
    
    eyebrow_intensity: FloatProperty(
        name="Eyebrow Intensity",
        description="Intensidad de las cejas",
        default=0.0,
        min=-0.5,
        max=0.5
    )
    
    jaw_expression: FloatProperty(
        name="Jaw Expression", 
        description="Expresión de la mandíbula",
        default=0.0,
        min=-0.3,
        max=0.3
    )
    
    # VALIDACIÓN DE NOMBRES
    name_validation_message: StringProperty(
        name="Name Validation",
        description="Mensaje de validación de nombres",
        default=""
    )
    
    # SHAPE KEYS - TODAS LAS PROPIEDADES CORREGIDAS
    auto_apply_shape_keys: BoolProperty(
        name="Auto Apply Shape Keys",
        description="Aplica automáticamente todas las shape keys durante la conversión (incluso las de valor 0)",
        default=True
    )

    preserve_basis_shape_key: BoolProperty(
        name="Preserve Basis Shape Key",
        description="Mantiene la shape key 'Basis' sin aplicar durante el proceso",
        default=False  # No preservar Basis por defecto para GTA SA
    )

    create_shape_keys_backup: BoolProperty(
        name="Create Shape Keys Backup",
        description="Crea automáticamente un backup de todos los meshes con shape keys antes de aplicarlas",
        default=True
    )

    apply_shape_keys_with_modifier: BoolProperty(
        name="Apply Shape Keys with Armature Modifier",
        description="Aplica las shape keys junto con los modificadores armature para mejor resultado",
        default=False
    )

    apply_final_shape_keys: BoolProperty(
        name="Apply Final Shape Keys",
        description="Aplica shape keys finales en el objeto unificado después de la conversión",
        default=True
    )

    shape_key_threshold: FloatProperty(
        name="Shape Key Threshold",
        description="Valor mínimo para aplicar una shape key (shape keys con valor menor se eliminan)",
        default=0.001,
        min=0.0,
        max=1.0
    )

    # Mensaje de estado para shape keys
    shape_keys_status_message: StringProperty(
        name="Shape Keys Status",
        description="Mensaje de estado del procesamiento de shape keys",
        default=""
    )
    
    # DEBUG PARA POSE DETECTION
    debug_pose_detection: BoolProperty(
        name="Debug Pose Detection",
        description="Activa debug detallado para detección de poses",
        default=False
    )
    
    # CONFIGURACIONES AVANZADAS DE CONVERSIÓN
    cleanup_materials: BoolProperty(
        name="Cleanup Materials",
        description="Limpia automáticamente materiales (metallic=0, specular=0)",
        default=True
    )
    
    unify_duplicate_materials: BoolProperty(
        name="Unify Duplicate Materials", 
        description="Unifica materiales que comparten la misma textura",
        default=True
    )
    
    remove_texture_suffixes: BoolProperty(
        name="Remove Texture Suffixes",
        description="Elimina sufijos .001, .002 de nombres de texturas",
        default=True
    )
    
    final_modifier_name: StringProperty(
        name="Final Modifier Name",
        description="Nombre del modificador armature final",
        default="GTA_SKIN"
    )
    
    final_armature_name: StringProperty(
        name="Final Armature Name", 
        description="Nombre final del armature después de conversión",
        default="Root"
    )
    
    # CONFIGURACIONES DE LIMPIEZA
    purge_orphan_data: BoolProperty(
        name="Purge Orphan Data",
        description="Elimina automáticamente datos huérfanos después de conversión",
        default=True
    )
    
    show_armature_in_front: BoolProperty(
        name="Show Armature In Front",
        description="Configura el armature final para mostrarse al frente",
        default=True
    )


def register_validation():
    """
    Función para registrar validadores adicionales si es necesario.
    VERSIÓN CORREGIDA: Manejo de errores mejorado
    """
    try:
        print("[CONFIG] Validadores de nombres registrados")
        # Aquí se pueden agregar validadores adicionales en el futuro
        return True
    except Exception as e:
        print(f"[CONFIG] Error registrando validadores: {e}")
        return False


# Funciones de utilidad para validación
def validate_armature_object(obj):
    """Valida que un objeto sea un armature válido"""
    if not obj:
        return False, "No se ha seleccionado objeto"
    
    if obj.type != 'ARMATURE':
        return False, f"El objeto '{obj.name}' no es un armature"
    
    if len(obj.data.bones) == 0:
        return False, f"El armature '{obj.name}' no tiene huesos"
    
    return True, "Armature válido"


def validate_bone_mappings(mappings, source_armature, target_armature):
    """Valida una lista de mapeos de huesos"""
    if not mappings:
        return False, "No hay mapeos definidos"
    
    if not source_armature or not target_armature:
        return False, "Armatures fuente y destino requeridos"
    
    enabled_mappings = [m for m in mappings if m.enabled]
    if not enabled_mappings:
        return False, "No hay mapeos habilitados"
    
    # Verificar que los huesos existen
    source_bones = {bone.name for bone in source_armature.pose.bones}
    target_bones = {bone.name for bone in target_armature.pose.bones}
    
    invalid_mappings = []
    for mapping in enabled_mappings:
        if mapping.source_bone not in source_bones:
            invalid_mappings.append(f"Hueso fuente '{mapping.source_bone}' no existe")
        if mapping.target_bone not in target_bones:
            invalid_mappings.append(f"Hueso destino '{mapping.target_bone}' no existe")
    
    if invalid_mappings:
        return False, "; ".join(invalid_mappings)
    
    return True, f"{len(enabled_mappings)} mapeos válidos"


def get_addon_version():
    """Obtiene la versión del addon"""
    return (3, 2, 3)


def get_addon_info():
    """Obtiene información del addon"""
    return {
        'name': 'Universal to GTA SA Converter',
        'version': get_addon_version(),
        'authors': ['YoshiMaincra', 'Claude (Anthropic)', 'ChatGPT (OpenAI)'],
        'description': 'Convierte armatures personalizados al formato GTA San Andreas',
        'status': 'In Development'
    }