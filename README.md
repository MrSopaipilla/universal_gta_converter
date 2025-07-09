# Universal GTA SA Converter v3.2.3 In-Dev

**⚠️ ESTADO: EN DESARROLLO ACTIVO - CONTIENE ERRORES CONOCIDOS**

Un addon avanzado para Blender que convierte armatures personalizados al formato exacto de GTA San Andreas con mapeo inteligente de huesos, procesamiento automático de Shape Keys y herramientas completas de optimización.

## 🚨 Advertencia Importante

Este addon está actualmente **en desarrollo** y contiene errores conocidos. No se recomienda para uso en producción. Use bajo su propio riesgo y siempre haga backups de sus proyectos.

## 📋 Información General

- **Versión**: 3.2.3 In-Dev
- **Autores**: YoshiMaincra (Lead), Claude (AI), ChatGPT (AI)
- **Compatibilidad**: Blender 4.0+
- **Licencia**: GPL v3
- **Categoría**: Rigging

## ✨ Características Principales

### 🦴 Mapeo Inteligente de Huesos
- **Detección automática** con nomenclatura exacta de GTA SA
- **Soporte completo** para espacios en nombres (`" L Hand"`, `" R Thigh"`)
- **Exclusión automática** del hueso Root
- **Inclusión garantizada** del hueso Pelvis
- **Validación en tiempo real** de mapeos

### 🎭 Procesamiento Avanzado de Shape Keys
- **Aplicación automática** durante conversión
- **Sistema de backup** antes de aplicar
- **Preservación opcional** de Basis shape key
- **Aplicación con modificadores** armature
- **Listado y gestión** de shape keys existentes

### 🎨 Corrección de Normales
- **Recálculo automático** hacia afuera
- **Detección de inconsistencias** en normales
- **Duplicación con normales invertidas** (opcional)
- **Verificación de consistencia** con análisis detallado

### 🎯 Animaciones Predefinidas
- **6 tipos de animación**: Idle, Walk, Running, Jump, Chat, Facial
- **Carga desde archivos .blend** con fallbacks automáticos
- **Expresividad facial** ajustable (cejas, mandíbula)
- **Sincronización con espaciado** de huesos

### 🧹 Herramientas de Limpieza
- **Limpieza de vertex groups** vacíos
- **Purga de datos** no utilizados
- **Optimización de materiales** (metallic=0, specular=0)
- **Unificación de materiales** duplicados
- **Eliminación de armatures** temporales

### 📝 Sistema de Nombres Personalizados
- **Validación de caracteres** (solo alfanuméricos, _, -)
- **Aplicación automática** a mesh y armature
- **Generación automática** basada en contenido
- **Límite de 32 caracteres** por nombre

## 🔧 Flujo de Conversión Detallado

### Fase 1: Preparación
1. Aplicar transformaciones al Source armature
2. Aplicar transformaciones a objetos hijos

### Fase 2: Procesamiento de Materiales
3. Configurar materiales (metallic=0, specular=0)
4. Unir todas las mallas en una sola
5. Limpiar nombres de texturas (.001, .002)
6. Fusionar materiales duplicados

### Fase 3: Shape Keys
7. Aplicar todas las Shape Keys activas
8. Eliminar shape keys restantes

### Fase 4: Modificadores
9. Aplicar modificador Armature del Source
10. Hornear pose actual del Source

### Fase 5: Reasignación
11. Crear constraints Copy Location en Target
12. Aplicar pose copiada
13. Eliminar constraints temporales

### Fase 6: Limpieza Final
14. Eliminar mallas no deseadas del Target
15. Eliminar Source armature completamente

### Fase 7: Configuración Final
16. Establecer Target como padre del mesh
17. Crear modificador "GTA_SKIN"
18. Aplicar nombres personalizados

## 🎛️ Paneles de Interfaz

### Panel Principal
- Configuración Source/Target armatures
- Botones "Auto Setup" y "Convert"

### Bone Mapping
- Lista drag & drop de mapeos
- Editor en línea de mapeos individuales
- Validación y estadísticas

### Shape Keys Manager
- Listado de shape keys detectadas
- Herramientas de backup y restauración
- Configuración de aplicación

### Advanced Options
- Configuración de conversión automática
- Espaciado de brazos y piernas
- Herramientas de testing

### Status & Reference
- **Herramientas de referencia GTA SA**
- **Verificación de configuración**
- **Estado de Shape Keys y backups**

## 📚 Nomenclatura Exacta GTA SA

### Con Espacios al Inicio:
```
" Spine", " Spine1", " Neck", " Head"
" L UpperArm", " L ForeArm", " L Hand"
" R UpperArm", " R ForeArm", " R Hand"
" L Thigh", " L Calf", " L Foot", " L Toe0"
" R Thigh", " R Calf", " R Foot", " R Toe0"
```

### Sin Espacios al Inicio:
```
"Pelvis", "Jaw", "L Brow", "R Brow"
"Bip01 L Clavicle", "Bip01 R Clavicle"
"L breast", "R breast", "Belly"
```

### Siempre Excluido:
```
"Root" - Se excluye automáticamente
```

## 🐛 Problemas Conocidos

- **Errores de importación** en algunos módulos
- **Inconsistencias** en mapeo automático
- **Fallos ocasionales** en aplicación de pose
- **Problemas de compatibilidad** con ciertos armatures
- **Shape Keys** pueden no aplicarse correctamente en todos los casos

## 📦 Instalación

1. Descargar el addon como .zip
2. En Blender: Edit > Preferences > Add-ons > Install
3. Seleccionar el archivo .zip
4. Activar "Universal to GTA SA Converter"
5. Guardar preferencias

## 🚀 Uso Básico

1. **Configurar armatures** (Source y Target)
2. **Click "Auto Setup"** para detectar mapeos
3. **Verificar en Status** que Pelvis esté incluido
4. **Backup Shape Keys** si existen
5. **Click "Convert"** para ejecutar conversión

## 🔍 Herramientas de Diagnóstico

- **Test Bone Mappings**: Prueba mapeos con constraints temporales
- **Preview Conversion**: Vista previa sin ejecutar
- **Validate Mappings**: Verifica configuración actual
- **Show Bone Names**: Referencia completa de huesos GTA SA

## 🛠️ Desarrollo

Este addon está en desarrollo activo. Los principales desarrolladores son:

- **YoshiMaincra**: Concepto, ensamblaje, testing
- **Claude (Anthropic)**: Programación Python, arquitectura
- **ChatGPT (OpenAI)**: Consultoría, completado de código

## 📞 Soporte

Para reportar bugs o sugerencias:
- Canal de YouTube: [Yoshi Maincra](https://www.youtube.com/@YoshiMaincra)
- Los bugs y problemas se reportan a través del canal

## ⚖️ Licencia

GPL v3 - Ver archivo LICENSE para detalles completos.

---

**Recuerda**: Este addon está en desarrollo activo. Siempre haz backup de tus proyectos antes de usar cualquier funcionalidad de conversión.
