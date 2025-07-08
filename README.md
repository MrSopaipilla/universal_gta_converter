# Universal GTA Converter v3.2.3 In-Dev - Instrucciones de Actualización

## 🚀 Versión 3.2.3 In-Dev - Nomenclatura Exacta GTA SA

### ✅ Cambios Principales Realizados:

#### 1. **Nomenclatura EXACTA de GTA SA**
- **CON espacios al inicio**: `" Spine"`, `" L UpperArm"`, `" R Thigh"`, etc.
- **SIN espacios al inicio**: `"Pelvis"`, `"Bip01 L Clavicle"`, `"Jaw"`, etc.
- **Corrección importante**: `" L ForeArm"` (con A mayúscula, no forearm)
- **Pelvis incluido** correctamente (solo Root excluido)

#### 2. **Nuevas Herramientas de Referencia GTA SA**
- **"Show Bone Names"** - Muestra nombres exactos en consola
- **"Create Template"** - Crea armature con estructura GTA SA completa
- **Panel "Status & Reference"** - Verificación de configuración y herramientas

#### 3. **Detección Inteligente Mejorada**
- Reconoce espacios al inicio de nombres de huesos
- Patrones específicos para `Bip01 L/R Clavicle`
- Prioridad correcta para nomenclatura GTA SA
- Validación específica para Pelvis

## 📁 Archivos a Actualizar:

### 1. **__init__.py** (REEMPLAZAR COMPLETO)
✅ **Reemplazar** con el contenido del artefacto `__init__.py - Versión 3.2.3 In-Dev`
- Versión actualizada a 3.2.3 In-Dev
- Importaciones de gta_reference agregadas
- Nuevos operadores incluidos en la lista de clases

### 2. **panels/main_panel.py**
✅ **Reemplazar** con el contenido del artefacto de paneles simplificados

### 3. **operators/mapping.py**
✅ **Reemplazar** con el contenido del artefacto con nomenclatura exacta

### 4. **operators/gta_reference.py** (NUEVO ARCHIVO)
📁 **Crear** este archivo nuevo con el contenido del artefacto de referencia

### 5. **converter.py**
✅ **Reemplazar** con el contenido del artefacto corregido (del mensaje anterior)

## 🎯 Estructura de Nombres GTA SA Exacta:

### **Columna Vertebral:**
```
"Pelvis"     # Sin espacio
" Spine"     # Con espacio al inicio
" Spine1"    # Con espacio al inicio
" Neck"      # Con espacio al inicio
" Head"      # Con espacio al inicio
```

### **Brazos:**
```
"Bip01 L Clavicle"  # Sin espacio al inicio
" L UpperArm"       # Con espacio al inicio
" L ForeArm"        # Con espacio al inicio (ForeArm con A mayúscula)
" L Hand"           # Con espacio al inicio
" L Finger"         # Con espacio al inicio
"L Finger01"        # Sin espacio al inicio

"Bip01 R Clavicle"  # Sin espacio al inicio
" R UpperArm"       # Con espacio al inicio
" R ForeArm"        # Con espacio al inicio
" R Hand"           # Con espacio al inicio
" R Finger"         # Con espacio al inicio
"R Finger01"        # Sin espacio al inicio
```

### **Piernas:**
```
" L Thigh"    # Con espacio al inicio
" L Calf"     # Con espacio al inicio
" L Foot"     # Con espacio al inicio
" L Toe0"     # Con espacio al inicio

" R Thigh"    # Con espacio al inicio
" R Calf"     # Con espacio al inicio
" R Foot"     # Con espacio al inicio
" R Toe0"     # Con espacio al inicio
```

### **Faciales y Especiales:**
```
"Jaw"         # Sin espacio al inicio
"L Brow"      # Sin espacio al inicio
"R Brow"      # Sin espacio al inicio
"L breast"    # Sin espacio al inicio
"R breast"    # Sin espacio al inicio
"Belly"       # Sin espacio al inicio
```

### **Siempre Excluido:**
```
"Root"        # NUNCA se mapea
```

## 🔧 Nuevas Características:

### **Panel "Status & Reference":**
- **Show Bone Names**: Lista completa de huesos GTA SA en consola
- **Create Template**: Crea armature con estructura exacta
- **Verificación de Pelvis**: Confirma que está mapeado
- **Estado de configuración**: Visual feedback del setup

### **Auto-Detección Mejorada:**
- Reconoce espacios al inicio de nombres
- Patrones específicos para cada hueso
- Confianza mejorada para nomenclatura GTA SA
- Pelvis incluido automáticamente

## ⚠️ Puntos Críticos:

1. **Los espacios al inicio SON parte del nombre** - no son errores
2. **ForeArm** tiene A mayúscula (no forearm)
3. **Pelvis** es crucial y ahora se incluye automáticamente
4. **Root** siempre se excluye automáticamente
5. **Bip01** es formato especial solo para clavículas

## 🚀 Flujo de Trabajo Actualizado:

1. **Instalar addon v3.2.3 In-Dev**
2. **Usar "Create Template"** para tener referencia (opcional)
3. **Asignar Source y Target armatures**
4. **Click "Auto Setup"** - detecta con nomenclatura exacta
5. **Verificar en "Status & Reference"** que Pelvis esté incluido
6. **Click "Convert"** - conversión con nombres exactos

## 🧪 Testing:

- **"Show Bone Names"** muestra lista con espacios exactos
- **Auto-detección** mapea a nombres con espacios correctos
- **Template creator** genera estructura exacta GTA SA
- **Panel Status** confirma que Pelvis está mapeado

## 📊 Cambios de Versión:

**v3.2.2 → v3.2.3 In-Dev:**
- ✅ Nomenclatura exacta GTA SA implementada
- ✅ Herramientas de referencia agregadas
- ✅ Pelvis incluido correctamente
- ✅ Espacios al inicio reconocidos
- ✅ Template creator con estructura real
- ✅ Interfaz simplificada y amigable

¡El addon ahora mapea con la nomenclatura EXACTA de GTA SA incluyendo todos los espacios y formatos especiales!
