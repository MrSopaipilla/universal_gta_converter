import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, PointerProperty, BoolProperty, CollectionProperty, FloatProperty, IntProperty, EnumProperty

def validate_name_input(self, context):
    """Validador para nombres de skin y autor"""
    import re
    
    # Validar skin_name
    if self.skin_name:
        if not re.match(r'^[a-zA-Z0-9_-]+$', self.skin_name):
            self.name_validation_message = "❌ Skin name: Solo se permiten letras, números, _ y -"
            # Limpiar caracteres inválidos
            self.skin_name = re.sub(r'[^a-zA-Z0-9_-]', '', self.skin_name)
        else:
            self.name_validation_message = "✅ Skin name válido"

    # Validar author_nickname
    if self.author_nickname:
        if not re.match(r'^[a-zA-Z0-9_-]+$', self.author_nickname):
            if "❌" not in self.name_validation_message:
                self.name_validation_message = "❌ Author nickname: Solo se permiten letras, números, _ y -"
            # Limpiar caracteres inválidos
            self.author_nickname = re.sub(r'[^a-zA-Z0-9_-]', '', self.author_nickname)
        else:
            if "❌" not in self.name_validation_message:
                self.name_validation_message = "✅ Nombres válidos"

class BoneMappingItem(PropertyGroup):
    """Elemento de mapeo de huesos"""
    source_bone: StringProperty(name="Source Bone")
    target_bone: StringProperty(name="Target Bone")
    enabled: BoolProperty(name="Enabled", default=True)
    detection_method: StringProperty(name="Detection Method", default="Manual")
    confidence: FloatProperty(name="Confidence", default=0.0)

class UniversalGTASettings(PropertyGroup):
    """Configuración principal del addon"""
    
    # Espaciado
    arm_spacing: FloatProperty(name="Arm Spacing", default=0.0, min=-1.0, max=1.0)
    leg_spacing: FloatProperty(name="Leg Spacing", default=0.0, min=-1.0, max=1.0)

    # Armatures
    source_armature: PointerProperty(type=bpy.types.Object)
    target_armature: PointerProperty(type=bpy.types.Object)
    
    # Opciones de conversión
    keep_vertex_colors: BoolProperty(name="Mantener Vertex Colors", default=False)
    debug_mode: BoolProperty(name="Debug Mode", default=False)
    auto_detect_mode: BoolProperty(name="Auto Detect", default=True)
    detection_threshold: FloatProperty(name="Detection Threshold", default=0.5)
    
    # Mapeos de huesos
    bone_mappings: CollectionProperty(type=BoneMappingItem)
    bone_mappings_index: IntProperty(name="Index", default=0)
    
    # Auto-aplicar pose personalizada
    auto_apply_custom_pose: BoolProperty(
        name="Auto Apply Custom Pose", 
        description="Aplica automáticamente la pose personalizada después de la conversión",
        default=True
    )
    
    # PROPIEDADES PARA CORRECCIÓN DE NORMALES
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
    
    # PROPIEDADES PARA NOMBRES PERSONALIZADOS CON VALIDACIÓN
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
    
    # PROPIEDADES PARA ANIMACIONES PREDEFINIDAS
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
    
    # PROPIEDADES PARA EXPRESIVIDAD FACIAL
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
    
    # PROPIEDADES PARA VALIDACIÓN DE NOMBRES
    name_validation_message: StringProperty(
        name="Name Validation",
        description="Mensaje de validación de nombres",
        default=""
    )
    
    # PROPIEDADES PARA SHAPE KEYS (CORREGIDO - DENTRO DE LA CLASE)
    auto_apply_shape_keys: BoolProperty(
        name="Auto Apply Shape Keys",
        description="Aplica automáticamente todas las shape keys durante la conversión",
        default=True
    )

    preserve_basis_shape_key: BoolProperty(
        name="Preserve Basis Shape Key",
        description="Mantiene la shape key 'Basis' sin aplicar durante el proceso",
        default=True
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
        default=False
    )

    shape_key_threshold: FloatProperty(
        name="Shape Key Threshold",
        description="Valor mínimo para aplicar una shape key (shape keys con valor menor se eliminan)",
        default=0.01,
        min=0.0,
        max=1.0
    )

    # Mensaje de estado para shape keys
    shape_keys_status_message: StringProperty(
        name="Shape Keys Status",
        description="Mensaje de estado del procesamiento de shape keys",
        default=""
    )

def register_validation():
    """
    Función para registrar validadores adicionales si es necesario.
    Por ahora solo es un placeholder para compatibilidad.
    """
    print("[CONFIG] Validadores de nombres registrados")
    pass