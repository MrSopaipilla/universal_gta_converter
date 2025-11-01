import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty, 
    PointerProperty, 
    BoolProperty, 
    CollectionProperty, 
    FloatProperty, 
    IntProperty, 
    EnumProperty
)

# Propiedades globales de la escena
bpy.types.Scene.gta_leg_roll_angle = FloatProperty(
    name="Leg Roll Angle",
    description="Ajustar ángulo de rotación para las piernas",
    default=0.0,
    min=-180.0,
    max=180.0,
    subtype='ANGLE'
)


def poll_armature_objects(self, object):
    """
    Poll function para filtrar solo armatures en los selectores
    Se ejecuta para cada objeto en la escena
    """
    return object.type == 'ARMATURE'


def validate_name_input(self, context):
    """Validador para nombres de skin y autor"""
    import re
    
    # Validar skin_name
    if hasattr(self, 'skin_name') and self.skin_name:
        # Solo permitir letras, numeros, guiones y guiones bajos
        pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(pattern, self.skin_name):
            self.name_validation_message = "Error: Skin name - Solo letras, numeros, _ y -"
            # Limpiar caracteres invalidos
            self.skin_name = re.sub(r'[^a-zA-Z0-9_-]', '', self.skin_name)
        else:
            self.name_validation_message = "Skin name valido"
    
    # Validar author_nickname
    if hasattr(self, 'author_nickname') and self.author_nickname:
        pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(pattern, self.author_nickname):
            if "Error:" not in getattr(self, 'name_validation_message', ''):
                self.name_validation_message = "Error: Author nickname - Solo letras, numeros, _ y -"
            # Limpiar caracteres invalidos
            self.author_nickname = re.sub(r'[^a-zA-Z0-9_-]', '', self.author_nickname)
        else:
            if "Error:" not in getattr(self, 'name_validation_message', ''):
                self.name_validation_message = "Nombres validos"


class BoneMappingItem(PropertyGroup):
    """Elemento de mapeo de huesos"""
    source_bone: StringProperty(name="Source Bone")
    target_bone: StringProperty(name="Target Bone")
    enabled: BoolProperty(name="Enabled", default=True)
    detection_method: StringProperty(name="Detection Method", default="Manual")
    confidence: FloatProperty(name="Confidence", default=0.0)


class UniversalGTASettings(PropertyGroup):
    preserve_vertex_data: BoolProperty(
        name="Preservar Vertex Colors / Atributos",
        description="No eliminar vertex colors y atributos de geometría durante la conversión",
        default=False
    )
    """Configuracion principal del addon"""
    
    # Espaciado
    arm_spacing: FloatProperty(name="Arm Spacing", default=0.0, min=-1.0, max=1.0)
    leg_spacing: FloatProperty(name="Leg Spacing", default=0.0, min=-1.0, max=1.0)

    # ARMATURES CON FILTROS ESTRICTOS (MEJORADO)
    source_armature: PointerProperty(
        name="Source Armature",
        description="Armature fuente que sera convertido (SOLO ARMATURES)",
        type=bpy.types.Object,
        poll=poll_armature_objects  # FILTRO: Solo armatures
    )
    
    target_armature: PointerProperty(
        name="Target Armature", 
        description="Armature destino con estructura GTA SA (SOLO ARMATURES)",
        type=bpy.types.Object,
        poll=poll_armature_objects  # FILTRO: Solo armatures
    )
    
    # Opciones de conversion
    keep_vertex_colors: BoolProperty(name="Mantener Vertex Colors", default=False)
    rasterize_textures: BoolProperty(
        name="Rasterizar texturas",
        description="Si está activado, hornea/rasteriza materiales complejos durante la conversión; si no, solo limpia/simplifica sin crear nuevas texturas",
        default=False
    )
    clean_materials: BoolProperty(
        name="Limpiar materiales",
        description="Si está activado, simplifica materiales. No bakea; solo rasteriza colores directos a 256x256 y deja intactos los que tengan Image Texture directa en Base Color",
        default=False
    )
    debug_mode: BoolProperty(name="Debug Mode", default=False)
    auto_detect_mode: BoolProperty(name="Auto Detect", default=True)
    detection_threshold: FloatProperty(name="Detection Threshold", default=0.5)
    
    # Mapeos de huesos
    bone_mappings: CollectionProperty(type=BoneMappingItem)
    bone_mappings_index: IntProperty(name="Index", default=0)
    
    # Auto-aplicar pose personalizada
    auto_apply_custom_pose: BoolProperty(
        name="Auto Apply Custom Pose", 
        description="Aplica automaticamente la pose personalizada despues de la conversion",
        default=True
    )

    # Propiedades para el nombre de la skin y autor
    skin_name: StringProperty(
        name="Skin Name",
        description="Nombre del personaje o skin (solo letras, números, guiones y guiones bajos)",
        default="",
        update=validate_name_input
    )
    
    author_nickname: StringProperty(
        name="Author",
        description="Nombre del autor (solo letras, números, guiones y guiones bajos)",
        default="",
        update=validate_name_input
    )
    
    name_validation_message: StringProperty(
        name="Validation Message",
        description="Mensaje de validación para el nombre y autor",
        default=""
    )
    
    # NUEVAS PROPIEDADES PARA CORRECCION DE NORMALES
    auto_fix_normals: BoolProperty(
        name="Auto Fix Normals",
        description="Recalcula automaticamente las normales hacia afuera despues de la conversion",
        default=True
    )
    
    duplicate_inverted_normals: BoolProperty(
        name="Duplicate with Inverted Normals",
        description="Crea una copia duplicada con normales invertidas para asegurar visibilidad de todas las caras",
        default=False
    )
    
    # NUEVAS PROPIEDADES PARA NOMBRES PERSONALIZADOS CON VALIDACION
    skin_name: StringProperty(
        name="Skin Name",
        description="Nombre del skin (solo caracteres alfanumericos, guiones y guiones bajos)",
        default="MySkin",
        maxlen=32,
        update=validate_name_input
    )
    
    author_nickname: StringProperty(
        name="Author Nickname", 
        description="Nickname del autor (solo caracteres alfanumericos, guiones y guiones bajos)",
        default="Author",
        maxlen=32,
        update=validate_name_input
    )
    
    # NUEVAS PROPIEDADES PARA ANIMACIONES PREDEFINIDAS
    predefined_animation: EnumProperty(
        name="Predefined Animation",
        description="Selecciona una animacion predefinida para cargar",
        items=[
            ('NONE', 'None', 'Sin animacion'),
            ('IDLE', 'Idle', 'Pose de espera'),
            ('WALK', 'Walk', 'Caminata'),
            ('RUNNING', 'Running', 'Corriendo'),
            ('JUMP', 'Jump', 'Salto'),
            ('CHAT', 'Chat', 'Hablando'),
            ('FACIAL', 'Facial', 'Expresion facial'),
        ],
        default='NONE'
    )
    
    # NUEVAS PROPIEDADES PARA EXPRESIVIDAD FACIAL
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
        description="Expresion de la mandibula",
        default=0.0,
        min=-0.3,
        max=0.3
    )
    
    # PROPIEDADES PARA VALIDACION DE NOMBRES
    name_validation_message: StringProperty(
        name="Name Validation",
        description="Mensaje de validacion de nombres",
        default=""
    )
    
    # === NUEVAS PROPIEDADES MEJORADAS ===
    
    # Control de limpieza automática
    auto_cleanup_enabled: BoolProperty(
        name="Limpieza Automática",
        description="Ejecutar limpieza automática al final de la conversión",
        default=True
    )
    
    # Configuración de autodetección mejorada
    autodetect_duplicates_enabled: BoolProperty(
        name="Autodetección de Duplicados",
        description="Permitir autodetección repetida para mejorar mapeos",
        default=True
    )
    
    autodetect_confidence_threshold: FloatProperty(
        name="Umbral de Confianza",
        description="Umbral mínimo de confianza para autodetección",
        default=0.7,
        min=0.0,
        max=1.0
    )


def register_validation():
    """
    Funcion para registrar validadores adicionales si es necesario.
    Por ahora solo es un placeholder para compatibilidad.
    """
    print("[CONFIG] Validadores de nombres registrados")
    pass

