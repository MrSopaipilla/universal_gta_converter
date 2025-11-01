"""Módulo de utilidades."""

import bpy  # type: ignore

try:
    from .cleanup import *
    CLEANUP_UTILS_AVAILABLE = True
except ImportError as e:
    CLEANUP_UTILS_AVAILABLE = False

available_classes = []


def register():
    """Registra todas las utilidades disponibles"""
    for cls in available_classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"[UTILS] Error registrando {cls.__name__}: {e}")


def unregister():
    """Desregistra todas las utilidades disponibles"""
    for cls in reversed(available_classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"[UTILS] Error desregistrando {cls.__name__}: {e}")


if __name__ == "__main__":
    register()