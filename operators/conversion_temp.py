import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
import re
from typing import List, Tuple, Optional, Dict
from mathutils import Vector, Matrix
from ..gta_conversion_utils import GTAConversionUtils  # Importación corregida

class UNIVERSALGTA_OT_execute_conversion(Operator):
    """Convertidor GTA SA Definitivo - Basado en flujo probado + mejoras desarrolladas"""
    bl_idname = "universalgta.execute_conversion"
    bl_label = "Convert to GTA SA (Ultimate)"
    bl_description = "Conversión definitiva a GTA SA con flujo probado"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            settings = context.scene.universal_gta_settings
            utils = GTAConversionUtils(debug=True)
            
            # Proceso de conversión...
            
            # Limpieza final
            if settings.target_armature:
                utils.cleanup_target_armature_parent(settings.target_armature)
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en conversión: {str(e)}")
            return {'CANCELLED'}
