import bpy
import os
from bpy.types import Panel

class UNIVERSALGTA_PT_AnimationsPanel(Panel):
    """Panel para gestión de animaciones"""
    bl_label = "Animations"
    bl_idname = "UNIVERSALGTA_PT_AnimationsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_parent_id = "UNIVERSALGTA_PT_MainPanel"
    bl_order = 4

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_gta_settings
        
        # Verificar si existe el archivo de animaciones
        addon_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        animations_file = os.path.join(addon_dir, "animations", "gta_animations.blend")
        file_exists = os.path.exists(animations_file)
        
        # Header
        row = layout.row()
        if file_exists:
            row.label(text="GTA Animations", icon='ANIM')
        else:
            row.label(text="GTA Animations (Setup Required)", icon='ERROR')
        
        # Setup section
        if not file_exists:
            box = layout.box()
            box.label(text="First Time Setup:", icon='TOOL_SETTINGS')
            box.operator("universalgta.create_animation_files", 
                        text="Create Animation Files", 
                        icon='FILE_NEW')
            box.label(text="This will create the base animation file", icon='INFO')
            return
        
        # Animaciones individuales
        box = layout.box()
        box.label(text="Individual Animations:", icon='ANIM_DATA')
        
        # Selector de animación
        row = box.row()
        row.label(text="Animation:")
        
        # Botón de carga con selector
        op = box.operator("universalgta.load_animation", text="Load Animation", icon='IMPORT')
        
        # Grid de animaciones comunes
        col = box.column(align=True)
        
        # Fila 1: Básicas
        row = col.row(align=True)
        op1 = row.operator("universalgta.load_animation", text="Idle", icon='ARMATURE_DATA')
        op1.animation_name = 'IDLE'
        op2 = row.operator("universalgta.load_animation", text="Walk", icon='OUTLINER_OB_ARMATURE')
        op2.animation_name = 'WALK'
        op3 = row.operator("universalgta.load_animation", text="Run", icon='FORWARD')
        op3.animation_name = 'RUN'
        
        # Fila 2: Tipos de caminata
        row = col.row(align=True)
        op_fat = row.operator("universalgta.load_animation", text="Fat Walk", icon='COMMUNITY')
        op_fat.animation_name = 'FAT_WALK'
        op_muscle = row.operator("universalgta.load_animation", text="Muscle Walk", icon='MODIFIER_DATA')
        op_muscle.animation_name = 'MUSCLE_WALK'
        op4 = row.operator("universalgta.load_animation", text="Jump", icon='TRIA_UP')
        op4.animation_name = 'JUMP'
        
        # Fila 3: Acciones
        row = col.row(align=True)
        op5 = row.operator("universalgta.load_animation", text="Crouch", icon='TRIA_DOWN')
        op5.animation_name = 'CROUCH'
        op6 = row.operator("universalgta.load_animation", text="Aim", icon='CROSSHAIRS')
        op6.animation_name = 'AIM'
        op_talk = row.operator("universalgta.load_animation", text="Talk", icon='SPEAKER')
        op_talk.animation_name = 'TALK'
        
        # Fila 4: Combate
        row = col.row(align=True)
        op7 = row.operator("universalgta.load_animation", text="Punch", icon='HAND')
        op7.animation_name = 'PUNCH'
        op8 = row.operator("universalgta.load_animation", text="Kick", icon='PROP_OFF')
        op8.animation_name = 'KICK'
        op9 = row.operator("universalgta.load_animation", text="Shoot", icon='OUTLINER_OB_LIGHT')
        op9.animation_name = 'SHOOT'
        
        # Fila 5: Especiales y facial
        row = col.row(align=True)
        op10 = row.operator("universalgta.load_animation", text="Dance", icon='POSE_HLT')
        op10.animation_name = 'DANCE'
        op11 = row.operator("universalgta.load_animation", text="Wave", icon='HAND')
        op11.animation_name = 'WAVE'
        op12 = row.operator("universalgta.load_animation", text="Sit", icon='MESH_PLANE')
        op12.animation_name = 'SIT'
        
        # Fila 6: Facial expressions
        row = col.row(align=True)
        op_facial = row.operator("universalgta.load_animation", text="Facial", icon='FACE_MAPS')
        op_facial.animation_name = 'FACIAL'
        
        # Sección separada para animaciones de tipos de personaje
        layout.separator()
        character_box = layout.box()
        character_box.label(text="Character Type Animations:", icon='COMMUNITY')
        
        col = character_box.column(align=True)
        
        # Fila de tipos de caminata especiales
        row = col.row(align=True)
        op_fat_special = row.operator("universalgta.load_animation", text="Fat Walk Cycle", icon='COMMUNITY')
        op_fat_special.animation_name = 'FAT_WALK_CYCLE'
        op_muscle_special = row.operator("universalgta.load_animation", text="Muscle Walk Cycle", icon='MODIFIER_DATA')
        op_muscle_special.animation_name = 'MUSCLE_WALK_CYCLE'
        
        # Fila de expresiones y gestos
        row = col.row(align=True)
        op_talk_gesture = row.operator("universalgta.load_animation", text="Talk Gesture", icon='SPEAKER')
        op_talk_gesture.animation_name = 'TALK_GESTURE'
        op_facial_expr = row.operator("universalgta.load_animation", text="Facial Expression", icon='FACE_MAPS')
        op_facial_expr.animation_name = 'FACIAL_EXPRESSION'
        
        # Batch loading
        layout.separator()
        box = layout.box()
        box.label(text="Batch Loading:", icon='PACKAGE')
        
        col = box.column(align=True)
        
        # Batch básico
        row = col.row(align=True)
        op_basic = row.operator("universalgta.batch_load_animations", text="Basic Set", icon='ANIM')
        op_basic.load_basic = True
        op_basic.load_combat = False
        op_basic.load_special = False
        
        # Batch combate
        op_combat = row.operator("universalgta.batch_load_animations", text="Combat Set", icon='MODIFIER')
        op_combat.load_basic = False
        op_combat.load_combat = True
        op_combat.load_special = False
        
        # Batch personaje
        row = col.row(align=True)
        op_character = row.operator("universalgta.batch_load_animations", text="Character Set", icon='COMMUNITY')
        op_character.load_basic = False
        op_character.load_combat = False
        op_character.load_special = True
        op_character.load_character = True
        
        # Batch completo
        row = col.row()
        op_all = row.operator("universalgta.batch_load_animations", text="Load All Animations", icon='ANIM_DATA')
        op_all.load_basic = True
        op_all.load_combat = True
        op_all.load_special = True
        op_all.load_character = True
        
        # Preview y utilidades
        layout.separator()
        box = layout.box()
        box.label(text="Animation Tools:", icon='TOOL_SETTINGS')
        
        col = box.column(align=True)
        
        # Preview
        row = col.row(align=True)
        row.operator("universalgta.preview_animation", text="Preview", icon='PLAY')
        row.operator("universalgta.apply_facial_expressiveness", text="Add Facial", icon='FACE_MAPS')
        
        # Utilidades
        row = col.row(align=True)
        row.operator("universalgta.refresh_animations_on_spacing_change", text="Refresh", icon='FILE_REFRESH')
        row.operator("universalgta.clear_animations", text="Clear All", icon='TRASH')
        
        # Estado actual
        if settings.target_armature and settings.target_armature.animation_data:
            action = settings.target_armature.animation_data.action
            if action:
                layout.separator()
                box = layout.box()
                box.label(text="Current Animation:", icon='ANIM')
                
                row = box.row()
                row.label(text=f"Name: {action.name}")
                
                if action.frame_range:
                    row = box.row()
                    row.label(text=f"Frames: {int(action.frame_range[0])}-{int(action.frame_range[1])}")
                
                # Controles de playback
                row = box.row(align=True)
                row.operator("screen.animation_play", text="Play", icon='PLAY')
                row.operator("screen.animation_cancel", text="Stop", icon='PAUSE')
                
                # Frame controls
                row = box.row(align=True)
                row.operator("screen.frame_jump", text="", icon='REW').end = False
                row.operator("screen.keyframe_jump", text="", icon='PREV_KEYFRAME').next = False
                row.operator("screen.keyframe_jump", text="", icon='NEXT_KEYFRAME').next = True
                row.operator("screen.frame_jump", text="", icon='FF').end = True