import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, EnumProperty

class UNIVERSALGTA_OT_load_animation(Operator):
    """Cargar animación desde archivo .blend único"""
    bl_idname = "universalgta.load_animation"
    bl_label = "Load Animation"
    bl_description = "Load animation from GTA animations blend file"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Animaciones disponibles en el archivo .blend
    animation_name: EnumProperty(
        name="Animation",
        description="Select animation to load",
        items=[
            ('IDLE', 'Idle', 'Pose de descanso estática'),
            ('WALK', 'Walk', 'Animación de caminar'),
            ('RUN', 'Run', 'Animación de correr'),
            ('JUMP', 'Jump', 'Animación de saltar'),
            ('CROUCH', 'Crouch', 'Pose agachado'),
            ('AIM', 'Aim', 'Pose apuntando'),
            ('SHOOT', 'Shoot', 'Animación de disparar'),
            ('DANCE', 'Dance', 'Animación de baile'),
            ('WAVE', 'Wave', 'Animación de saludo'),
            ('PUNCH', 'Punch', 'Animación de puñetazo'),
            ('KICK', 'Kick', 'Animación de patada'),
            ('FALLING', 'Falling', 'Animación de caída'),
            ('GETUP', 'Get Up', 'Animación de levantarse'),
            ('SIT', 'Sit', 'Pose sentado'),
            ('DRIVE', 'Drive', 'Pose de conducir'),
        ]
    )
    
    apply_immediately: BoolProperty(
        name="Apply Immediately",
        description="Apply animation immediately after loading",
        default=True
    )
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No target armature selected")
            return {'CANCELLED'}
        
        # Ruta del archivo de animaciones
        addon_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        animations_file = os.path.join(addon_dir, "animations", "gta_animations.blend")
        
        if not os.path.exists(animations_file):
            self.report({'ERROR'}, f"Animation file not found: {animations_file}")
            return {'CANCELLED'}
        
        try:
            # Cargar animación específica
            success = self.load_animation_from_blend(animations_file, self.animation_name, settings.target_armature)
            
            if success:
                self.report({'INFO'}, f"Animation '{self.animation_name}' loaded successfully")
                
                # Aplicar inmediatamente si está habilitado
                if self.apply_immediately:
                    bpy.ops.universalgta.apply_facial_expressiveness()
                
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, f"Failed to load animation '{self.animation_name}'")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error loading animation: {str(e)}")
            return {'CANCELLED'}
    
    def load_animation_from_blend(self, blend_file, anim_name, target_armature):
        """Carga una animación específica desde el archivo .blend"""
        
        # Mapeo de nombres de animaciones a nombres de actions en el .blend
        animation_mapping = {
            'IDLE': 'GTA_Idle',
            'WALK': 'GTA_Walk',
            'RUN': 'GTA_Run',
            'JUMP': 'GTA_Jump',
            'CROUCH': 'GTA_Crouch',
            'AIM': 'GTA_Aim',
            'SHOOT': 'GTA_Shoot',
            'DANCE': 'GTA_Dance',
            'WAVE': 'GTA_Wave',
            'PUNCH': 'GTA_Punch',
            'KICK': 'GTA_Kick',
            'FALLING': 'GTA_Falling',
            'GETUP': 'GTA_GetUp',
            'SIT': 'GTA_Sit',
            'DRIVE': 'GTA_Drive',
        }
        
        action_name = animation_mapping.get(anim_name, f"GTA_{anim_name}")
        
        # Hacer backup del contexto actual
        original_frame = bpy.context.scene.frame_current
        original_mode = bpy.context.mode
        
        try:
            # Cambiar a modo objeto
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Seleccionar el armature target
            bpy.context.view_layer.objects.active = target_armature
            target_armature.select_set(True)
            
            # Importar action desde el archivo .blend
            with bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
                if action_name in data_from.actions:
                    data_to.actions = [action_name]
                    print(f"[DEBUG] Importing action: {action_name}")
                else:
                    print(f"[DEBUG] Action '{action_name}' not found in {blend_file}")
                    print(f"[DEBUG] Available actions: {data_from.actions}")
                    return False
            
            # Verificar que se importó correctamente
            if action_name not in bpy.data.actions:
                print(f"[DEBUG] Failed to import action: {action_name}")
                return False
            
            # Obtener la action importada
            action = bpy.data.actions[action_name]
            
            # Aplicar la action al armature
            if target_armature.animation_data is None:
                target_armature.animation_data_create()
            
            # Asignar la action
            target_armature.animation_data.action = action
            
            # Configurar timeline
            if action.frame_range:
                bpy.context.scene.frame_start = int(action.frame_range[0])
                bpy.context.scene.frame_end = int(action.frame_range[1])
                bpy.context.scene.frame_current = int(action.frame_range[0])
            
            print(f"[DEBUG] Animation '{anim_name}' loaded successfully")
            print(f"[DEBUG] Frame range: {action.frame_range}")
            print(f"[DEBUG] Action assigned to: {target_armature.name}")
            
            return True
            
        except Exception as e:
            print(f"[DEBUG] Error loading animation: {e}")
            return False
        
        finally:
            # Restaurar contexto
            bpy.context.scene.frame_current = original_frame


class UNIVERSALGTA_OT_preview_animation(Operator):
    """Preview de animación en tiempo real"""
    bl_idname = "universalgta.preview_animation"
    bl_label = "Preview Animation"
    bl_description = "Preview animation without applying permanently"
    bl_options = {'REGISTER'}
    
    animation_name: StringProperty(
        name="Animation Name",
        description="Name of animation to preview",
        default="IDLE"
    )
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No target armature selected")
            return {'CANCELLED'}
        
        # Aplicar animación temporalmente
        self.apply_temporary_animation(settings.target_armature, self.animation_name)
        
        # Iniciar playback
        bpy.ops.screen.animation_play()
        
        self.report({'INFO'}, f"Previewing animation: {self.animation_name}")
        return {'FINISHED'}
    
    def apply_temporary_animation(self, armature, anim_name):
        """Aplica animación temporalmente para preview"""
        
        # Cambiar a modo pose
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Aplicar poses específicas basadas en el nombre
        if anim_name == "IDLE":
            self.apply_idle_pose(armature)
        elif anim_name == "WALK":
            self.apply_walk_pose(armature)
        elif anim_name == "RUN":
            self.apply_run_pose(armature)
        # ... más poses
        
        bpy.ops.object.mode_set(mode='OBJECT')
    
    def apply_idle_pose(self, armature):
        """Aplica pose de idle"""
        bpy.ops.object.mode_set(mode='POSE')
        
        # Ejemplo de pose idle
        if "Spine" in armature.pose.bones:
            armature.pose.bones["Spine"].rotation_euler = (0, 0, 0)
        
        if "Head" in armature.pose.bones:
            armature.pose.bones["Head"].rotation_euler = (0, 0, 0)
        
        # Brazos relajados
        if "L UpperArm" in armature.pose.bones:
            armature.pose.bones["L UpperArm"].rotation_euler = (0, 0, -0.2)
        
        if "R UpperArm" in armature.pose.bones:
            armature.pose.bones["R UpperArm"].rotation_euler = (0, 0, 0.2)
    
    def apply_walk_pose(self, armature):
        """Aplica pose de caminar"""
        bpy.ops.object.mode_set(mode='POSE')
        
        # Ejemplo de pose walk
        if "L Thigh" in armature.pose.bones:
            armature.pose.bones["L Thigh"].rotation_euler = (0.3, 0, 0)
        
        if "R Thigh" in armature.pose.bones:
            armature.pose.bones["R Thigh"].rotation_euler = (-0.3, 0, 0)


class UNIVERSALGTA_OT_batch_load_animations(Operator):
    """Cargar múltiples animaciones de una vez"""
    bl_idname = "universalgta.batch_load_animations"
    bl_label = "Batch Load Animations"
    bl_description = "Load multiple animations at once"
    bl_options = {'REGISTER', 'UNDO'}
    
    load_basic: BoolProperty(
        name="Basic Animations",
        description="Load basic animations (Idle, Walk, Run)",
        default=True
    )
    
    load_combat: BoolProperty(
        name="Combat Animations",
        description="Load combat animations (Punch, Kick, Aim, Shoot)",
        default=False
    )
    
    load_special: BoolProperty(
        name="Special Animations",
        description="Load special animations (Dance, Wave, Sit)",
        default=False
    )
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No target armature selected")
            return {'CANCELLED'}
        
        animations_to_load = []
        
        if self.load_basic:
            animations_to_load.extend(['IDLE', 'WALK', 'RUN', 'JUMP'])
        
        if self.load_combat:
            animations_to_load.extend(['AIM', 'SHOOT', 'PUNCH', 'KICK'])
        
        if self.load_special:
            animations_to_load.extend(['DANCE', 'WAVE', 'SIT', 'DRIVE'])
        
        loaded_count = 0
        
        for anim_name in animations_to_load:
            # Usar el operador de carga individual
            try:
                bpy.ops.universalgta.load_animation(animation_name=anim_name, apply_immediately=False)
                loaded_count += 1
            except Exception as e:
                print(f"[DEBUG] Failed to load {anim_name}: {e}")
        
        self.report({'INFO'}, f"Loaded {loaded_count} animations")
        return {'FINISHED'}


class UNIVERSALGTA_OT_create_animation_files(Operator):
    """Crear archivo base de animaciones"""
    bl_idname = "universalgta.create_animation_files"
    bl_label = "Create Animation Files"
    bl_description = "Create base animation files structure"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        addon_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        animations_dir = os.path.join(addon_dir, "animations")
        
        # Crear directorio si no existe
        if not os.path.exists(animations_dir):
            os.makedirs(animations_dir)
        
        # Crear archivo base de animaciones
        blend_file = os.path.join(animations_dir, "gta_animations.blend")
        
        if not os.path.exists(blend_file):
            # Crear archivo .blend con animaciones base
            self.create_base_animations_file(blend_file)
            self.report({'INFO'}, f"Animation file created: {blend_file}")
        else:
            self.report({'WARNING'}, f"Animation file already exists: {blend_file}")
        
        return {'FINISHED'}
    
    def create_base_animations_file(self, filepath):
        """Crea archivo base con animaciones"""
        
        # Crear nuevo archivo
        bpy.ops.wm.read_homefile(use_empty=True)
        
        # Crear armature base para las animaciones
        bpy.ops.object.armature_add()
        armature = bpy.context.active_object
        armature.name = "GTA_AnimationRig"
        
        # Crear actions básicas
        self.create_idle_action(armature)
        self.create_walk_action(armature)
        self.create_run_action(armature)
        
        # Guardar archivo
        bpy.ops.wm.save_as_mainfile(filepath=filepath)
        
        print(f"[DEBUG] Created animation file: {filepath}")
    
    def create_idle_action(self, armature):
        """Crea action de idle"""
        action = bpy.data.actions.new(name="GTA_Idle")
        
        if armature.animation_data is None:
            armature.animation_data_create()
        
        armature.animation_data.action = action
        
        # Configurar keyframes básicos
        bpy.context.scene.frame_set(1)
        bpy.ops.object.mode_set(mode='POSE')
        
        # Keyframes para pose idle
        for bone in armature.pose.bones:
            bone.keyframe_insert(data_path="rotation_euler", frame=1)
            bone.keyframe_insert(data_path="rotation_euler", frame=60)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print("[DEBUG] Created GTA_Idle action")
    
    def create_walk_action(self, armature):
        """Crea action de walk"""
        action = bpy.data.actions.new(name="GTA_Walk")
        
        if armature.animation_data is None:
            armature.animation_data_create()
        
        armature.animation_data.action = action
        
        # Configurar keyframes para walk cycle
        bpy.context.scene.frame_set(1)
        bpy.ops.object.mode_set(mode='POSE')
        
        # Keyframes para walk cycle (24 frames)
        for frame in [1, 12, 24]:
            bpy.context.scene.frame_set(frame)
            for bone in armature.pose.bones:
                bone.keyframe_insert(data_path="rotation_euler", frame=frame)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print("[DEBUG] Created GTA_Walk action")
    
    def create_run_action(self, armature):
        """Crea action de run"""
        action = bpy.data.actions.new(name="GTA_Run")
        
        if armature.animation_data is None:
            armature.animation_data_create()
        
        armature.animation_data.action = action
        
        # Configurar keyframes para run cycle
        bpy.context.scene.frame_set(1)
        bpy.ops.object.mode_set(mode='POSE')
        
        # Keyframes para run cycle (16 frames, más rápido)
        for frame in [1, 8, 16]:
            bpy.context.scene.frame_set(frame)
            for bone in armature.pose.bones:
                bone.keyframe_insert(data_path="rotation_euler", frame=frame)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print("[DEBUG] Created GTA_Run action")


class UNIVERSALGTA_OT_clear_animations(Operator):
    """Limpiar animaciones cargadas"""
    bl_idname = "universalgta.clear_animations"
    bl_label = "Clear Animations"
    bl_description = "Clear all loaded animations"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No target armature selected")
            return {'CANCELLED'}
        
        # Limpiar action del armature
        if settings.target_armature.animation_data:
            settings.target_armature.animation_data.action = None
        
        # Eliminar actions GTA
        actions_to_remove = []
        for action in bpy.data.actions:
            if action.name.startswith("GTA_"):
                actions_to_remove.append(action)
        
        for action in actions_to_remove:
            bpy.data.actions.remove(action)
        
        self.report({'INFO'}, f"Cleared {len(actions_to_remove)} GTA animations")
        return {'FINISHED'}


class UNIVERSALGTA_OT_apply_facial_expressiveness(Operator):
    """Aplicar expresividad facial"""
    bl_idname = "universalgta.apply_facial_expressiveness"
    bl_label = "Apply Facial Expressiveness"
    bl_description = "Apply facial expressiveness to current animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No target armature selected")
            return {'CANCELLED'}
        
        # Aplicar expresividad facial
        self.apply_facial_animation(settings.target_armature)
        
        self.report({'INFO'}, "Facial expressiveness applied")
        return {'FINISHED'}
    
    def apply_facial_animation(self, armature):
        """Aplica animación facial básica"""
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Parpadeo básico
        if "Head" in armature.pose.bones:
            head_bone = armature.pose.bones["Head"]
            
            # Keyframes para parpadeo
            for frame in [1, 30, 60, 90, 120]:
                bpy.context.scene.frame_set(frame)
                
                # Variación sutil en rotación de cabeza
                if frame == 30:
                    head_bone.rotation_euler.z = 0.05
                elif frame == 90:
                    head_bone.rotation_euler.z = -0.05
                else:
                    head_bone.rotation_euler.z = 0
                
                head_bone.keyframe_insert(data_path="rotation_euler")
        
        bpy.ops.object.mode_set(mode='OBJECT')


class UNIVERSALGTA_OT_refresh_animations_on_spacing_change(Operator):
    """Refrescar animaciones cuando cambia el espaciado"""
    bl_idname = "universalgta.refresh_animations_on_spacing_change"
    bl_label = "Refresh Animations"
    bl_description = "Refresh animations after spacing changes"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.universal_gta_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No target armature selected")
            return {'CANCELLED'}
        
        # Refrescar animaciones
        if settings.target_armature.animation_data and settings.target_armature.animation_data.action:
            action = settings.target_armature.animation_data.action
            
            # Recalcular keyframes basados en nuevo espaciado
            self.recalculate_keyframes(action, settings)
            
            self.report({'INFO'}, "Animations refreshed")
        else:
            self.report({'WARNING'}, "No animation to refresh")
        
        return {'FINISHED'}
    
    def recalculate_keyframes(self, action, settings):
        """Recalcula keyframes basado en nuevo espaciado"""
        
        # Ajustar keyframes basados en arm_spacing y leg_spacing
        for fcurve in action.fcurves:
            if "UpperArm" in fcurve.data_path or "ForeArm" in fcurve.data_path:
                # Aplicar factor de espaciado de brazos
                for keyframe in fcurve.keyframe_points:
                    keyframe.co.y *= settings.arm_spacing
            
            elif "Thigh" in fcurve.data_path or "Calf" in fcurve.data_path:
                # Aplicar factor de espaciado de piernas
                for keyframe in fcurve.keyframe_points:
                    keyframe.co.y *= settings.leg_spacing
        
        # Actualizar action
        action.update()


# Lista de clases para registrar
classes = [
    UNIVERSALGTA_OT_load_animation,
    UNIVERSALGTA_OT_preview_animation,
    UNIVERSALGTA_OT_batch_load_animations,
    UNIVERSALGTA_OT_create_animation_files,
    UNIVERSALGTA_OT_clear_animations,
    UNIVERSALGTA_OT_apply_facial_expressiveness,
    UNIVERSALGTA_OT_refresh_animations_on_spacing_change,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)