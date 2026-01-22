# Universal GTA SA Converter

## 📖 ¿Qué es este addon?

Este addon convierte personajes de diferentes sistemas de animación (como Mixamo, Source/SFM, ValveBiped, AvatarSDK, etc.) al formato de huesos que usa Grand Theft Auto: San Andreas. Básicamente, toma un personaje con su estructura de huesos y lo adapta para que funcione correctamente en GTA SA.

---

## 🎯 ¿Cómo funciona el addon?

### Flujo de trabajo básico:

1. **Configuración inicial**: Seleccionas tu armature (estructura de huesos) original y el armature objetivo de GTA SA.

2. **Detección inteligente**: El addon intenta detectar automáticamente qué tipo de personaje tienes (Mixamo, Source, etc.) y carga un mapeo predefinido.

3. **Mapeo de huesos**: El sistema crea una lista de "mapeos" que relacionan cada hueso de tu personaje original con un hueso del sistema GTA SA.

4. **Conversión**: El addon realiza una serie de pasos automáticos:
   - Limpia y optimiza texturas y materiales
   - Une las mallas del personaje
   - Aplica los mapeos de huesos
   - Crea "constraints" (restricciones) que copian las posiciones
   - Transfiere los pesos de los vértices (vertex weights)
   - Renombra grupos de vértices según los huesos de GTA SA
   - Limpia la escena final

5. **Resultado**: Obtienes un personaje compatible con GTA SA, listo para exportar.

---

## 🔗 Sistema de Mapping (Mapeo de Huesos)

### ¿Qué es un "mapping"?

Un mapping (mapeo) es una conexión entre dos huesos:
- **Source Bone (Hueso Fuente)**: El hueso de tu personaje original
- **Target Bone (Hueso Objetivo)**: El hueso correspondiente en el sistema GTA SA

**Ejemplo:**
- Si tu personaje tiene un hueso llamado "LeftArm" (brazo izquierdo)
- Y GTA SA necesita un hueso llamado " L UpperArm"
- El mapping conecta estos dos huesos

### Tipos de mappings:

1. **Mappings directos (1:1)**: Un hueso fuente se mapea a un hueso objetivo único
   - Ejemplo: `Hips` → ` Pelvis`

2. **Mappings duplicados (muchos:1)**: Varios huesos fuente se mapean al mismo hueso objetivo
   - Ejemplo: `LeftEye` y `RightEye` → ambos a ` Head`
   - Esto es útil cuando GTA SA tiene menos huesos que tu personaje original

### ¿Cómo se crean los mappings?

1. **Detección automática inteligente**: El addon analiza los nombres de tus huesos y compara con perfiles conocidos (Mixamo, Source, etc.).

2. **Mappings predefinidos**: El addon incluye archivos JSON con mapeos ya configurados para sistemas comunes.

3. **Edición manual**: Puedes editar cualquier mapping manualmente en el panel "Advanced Mapping".

---

## 📚 Mappings Predefinidos del Addon

El addon incluye **11 perfiles de mapping predefinidos** que cubren los sistemas de animación más comunes. Cuando usas la función "Smart Auto-Detect", el addon intenta reconocer automáticamente qué tipo de personaje tienes y carga el mapping más adecuado.

### 🎭 Perfiles Disponibles:

#### 1. **Mixamo** (`bone_mapping_mixamo.json`)
**¿Qué es Mixamo?** Mixamo es un servicio de Adobe que proporciona personajes y animaciones gratuitas. Los personajes de Mixamo usan nombres de huesos como `mixamorig:Hips`, `mixamorig:Spine`, etc.

**Características:**
- Prefijo `mixamorig:` en todos los huesos
- Sistema estándar de animación para personajes humanos
- Huesos comunes: `mixamorig:Hips`, `mixamorig:LeftArm`, `mixamorig:RightLeg`
- Muy popular para personajes de juegos y animaciones

**Cuándo usarlo:** Si importaste un personaje directamente desde Mixamo o usas personajes con el prefijo `mixamorig:` en los nombres de huesos.

---

#### 2. **Mixamo Clean** (`bone_mapping_mixamo_clean.json`)
**¿Qué es?** Una versión "limpia" del mapping de Mixamo, optimizada para personajes que ya fueron procesados o que no tienen el prefijo `mixamorig:`. Usa nombres simples como `Hips`, `Spine`, `LeftArm`.

**Características:**
- Nombres de huesos sin prefijo `mixamorig:`
- Huesos como: `Hips`, `Spine`, `Spine1`, `LeftArm`, `RightLeg`
- Incluye soporte para huesos twist (ej: `Twist_Hand_Left`, `Twist_ForeArm_Right`)
- Ideal para personajes ya procesados o exportados desde otros programas

**Cuándo usarlo:** Si tienes un personaje con estructura similar a Mixamo pero sin el prefijo, o si necesitas soporte para twist bones.

**Diferencia con Mixamo estándar:** Este mapping incluye específicamente los twist bones al inicio del mapeo, lo cual es útil para personajes con sistemas de deformación más avanzados.

---

#### 3. **Source Film Maker (SFM)** (`bone_mapping_SFM.json`)
**¿Qué es Source Film Maker?** Es un programa de Valve para crear animaciones usando modelos de Source Engine (Half-Life, Team Fortress, Portal, etc.). Los personajes usan nombres como `bip_collar_l`, `bip_index_0_l`, `Jaw`, etc.

**Características:**
- Prefijo `bip_` para muchos huesos (Bip = Biped)
- Huesos específicos de Source: `Jaw`, `Tongue`, `Ear_L`, `Ear_R`
- Sistema de dedos detallado: `bip_index_0_l`, `bip_thumb_0_l`, etc.
- Compatible con modelos de Team Fortress 2, Half-Life 2, Portal, etc.

**Cuándo usarlo:** Si trabajas con personajes de Source Film Maker, Source Engine, o modelos de juegos de Valve.

---

#### 4. **ValveBiped** (`valve_bone_mapping.json`)
**¿Qué es ValveBiped?** Es el sistema estándar de huesos usado por Valve en sus juegos. Los huesos tienen nombres como `ValveBiped.Bip01_Pelvis`, `ValveBiped.Bip01_L_UpperArm`, etc.

**Características:**
- Prefijo `ValveBiped.Bip01_` en todos los huesos principales
- Sistema jerárquico estándar de Valve
- Incluye soporte para twist bones de Valve: `ValveBiped.Bip01_L_UpperArm_Twist`
- Compatible con modelos de Counter-Strike, Half-Life, etc.

**Cuándo usarlo:** Si tienes personajes con estructura ValveBiped, especialmente de juegos más antiguos de Valve o modelos exportados desde Source SDK.

**Diferencia con SFM:** ValveBiped es el sistema base, mientras que SFM puede tener variaciones y huesos adicionales específicos para animación cinematográfica.

---

#### 5. **Rigify** (`rigify_mapping.json`)
**¿Qué es Rigify?** Es un addon de Blender que genera automáticamente estructuras de huesos (rigs) profesionales. Los huesos generados tienen nombres como `DEF-pelvis`, `DEF-spine.001`, `DEF-upper_arm.L`, etc.

**Características:**
- Prefijo `DEF-` en la mayoría de los huesos (DEF = Deform)
- Numeración con puntos: `DEF-spine.001`, `DEF-spine.002`, etc.
- Nomenclatura con puntos y guiones: `DEF-upper_arm.L`, `DEF-hand.L`
- Sistema profesional y flexible para animación

**Cuándo usarlo:** Si generaste tu rig usando el addon Rigify de Blender, o si tu personaje tiene nombres de huesos que empiezan con `DEF-`.

---

#### 6. **AccuRig** (`accurig_bone_mapping.json`)
**¿Qué es AccuRig?** Es un software de Reallusion para crear automáticamente estructuras de huesos desde una fotografía o modelo 3D. Los huesos tienen nombres como `CC_Base_Hip`, `CC_Base_Spine01`, `CC_Base_L_Upperarm`, etc.

**Características:**
- Prefijo `CC_Base_` en todos los huesos (CC = Character Creator)
- Numeración en los nombres: `CC_Base_Spine01`, `CC_Base_Spine02`
- Sistema de twist bones numerado: `CC_Base_L_UpperarmTwist01`, `CC_Base_L_UpperarmTwist02`
- Muy detallado, con múltiples huesos twist para mejor deformación

**Cuándo usarlo:** Si creaste tu personaje con AccuRig, Character Creator de Reallusion, o personajes con el prefijo `CC_Base_`.

**Nota importante:** Los mappings de AccuRig incluyen muchos twist bones numerados que deben mapearse en el orden correcto (ver sección de orden de mappings).

---

#### 7. **AvatarSDK** (`avatarsdk_bone_mapping.json`)
**¿Qué es AvatarSDK?** Es un sistema para crear avatares y personajes, comúnmente usado para avatares virtuales y sistemas de captura de movimiento. Los huesos tienen nombres simples como `Hips`, `Spine`, `LeftArm`, `RightLeg`.

**Características:**
- Nomenclatura simple y directa (sin prefijos complejos)
- Huesos estándar: `Hips`, `Spine`, `Spine1`, `Spine2`, `Neck`, `Head`
- Sistema de dedos numerado: `LeftHandIndex1`, `LeftHandIndex2`, `LeftHandThumb1`, etc.
- Compatible con sistemas de avatares virtuales y VR

**Cuándo usarlo:** Si trabajas con avatares de sistemas VR, captura de movimiento, o personajes con nomenclatura simple sin prefijos.

---

#### 8. **GoldSrc (Half-Life 1 / Counter-Strike 1.6)** (`goldsrc_mapping.json`)
**¿Qué es GoldSrc?** Es el motor original de Valve usado para juegos clásicos como Half-Life 1 y CS 1.6. Sus modelos usan nombres como `Bip01 Pelvis`, `Bip01 L UpperArm`, etc.

**Características:**
- Estructura Bip01 de la vieja escuela
- Nombres de huesos con espacios o sufijos numéricos simples
- Jerarquía optimizada para motores de finales de los 90
- Compatible con modelos clásicos de GoldSrc

**Cuándo usarlo:** Si estás portando modelos de Half-Life 1, Day of Defeat o Counter-Strike 1.6.

---

#### 9. **MMD (MikuMikuDance)** (`mmd_bone_mapping.json`)
**¿Qué es MMD?** Un software de animación japonés extremadamente popular. Sus modelos utilizan nombres de huesos en **japonés** (ej: `腰`, `上半身`, `腕.L`).

**Características:**
- Soporte nativo para nombres de huesos en japonés
- Manejo de huesos "D" y huesos auxiliares típicos de modelos de anime
- Mapeo complejo de dedos y extremidades
- Ideal para convertir modelos descargados de comunidades de MMD (como BowlRoll)

**Cuándo usarlo:** Cuando tengas un modelo que use la nomenclatura estándar de MMD en japonés.

---

#### 10. **Valve Left 4 Dead (L4D)** (`valve_l4d_bone_mapping.json`)
**¿Qué es?** Una evolución del sistema ValveBiped específica para los juegos Left 4 Dead 1 y 2. Incluye huesos de ayuda ("helper bones") y una estructura ligeramente diferente al ValveBiped estándar.

**Características:**
- Soporte para `ValveBiped.hlp_` (huesos de ayuda)
- Mapeos optimizados para las deformaciones de los personajes de L4D
- Maneja nombres como `ValveBiped.Bip01_L_Bicep` y otros específicos
- Mayor fidelidad en la conversión de modelos de L4D

**Cuándo usarlo:** Si importas modelos directamente de Left 4 Dead 1 o 2.

---

#### 11. **Empty (Vacío)** (`empty_gta_sa_mapping.json`)
**¿Qué es?** Un mapping completamente vacío, sin ningún mapeo predefinido. Útil cuando quieres crear todos los mappings manualmente desde cero.

**Características:**
- Sin mappings predefinidos
- Lista vacía lista para agregar tus propios mappings
- Útil para personajes personalizados o sistemas no estándar

**Cuándo usarlo:** 
- Si tu personaje usa un sistema de nombres completamente personalizado
- Si quieres control total sobre cada mapping
- Si el addon no detecta correctamente tu tipo de personaje (mejor usar esto y mapear manualmente)

---

### 🔍 ¿Cómo elige el addon qué mapping usar?

Cuando haces clic en **"🧠 Smart Auto-Detect"**, el addon:

1. **Analiza los nombres de tus huesos** en el armature fuente
2. **Compara con cada perfil predefinido** y calcula un porcentaje de coincidencia
3. **Selecciona el perfil con mayor coincidencia** (si supera el 20% de similitud)
4. **Carga automáticamente** todos los mappings de ese perfil

**Ejemplo:**
- Si detecta huesos como `mixamorig:Hips`, `mixamorig:Spine` → Carga **Mixamo**
- Si detecta huesos como `DEF-pelvis`, `DEF-spine` → Carga **Rigify**
- Si detecta huesos como `CC_Base_Hip`, `CC_Base_Spine01` → Carga **AccuRig**
- Si no encuentra coincidencias claras → Carga **Empty** para mapeo manual

### 💡 Tips sobre los mappings predefinidos:

1. **Revisa siempre el resultado**: Aunque el addon detecte automáticamente, siempre revisa los mappings en "Advanced Mapping" para asegurarte de que sean correctos.

2. **Puedes mezclar mappings**: No estás limitado a un solo perfil. Puedes cargar un mapping predefinido y luego agregar o modificar mappings manualmente.

3. **Guarda tus mappings personalizados**: Si modificas un mapping predefinido, puedes guardarlo usando "Save Mapping" para usarlo después.

4. **Orden importa**: Incluso los mappings predefinidos respetan el orden correcto mencionado en la sección de "Orden del Mapeo", especialmente para twist bones.

---

## 🔝 Consolidación Jerárquica (Consolidate by Hierarchy)

### 🧠 ¿Qué es la Consolidación Jerárquica?

Es una de las funciones más potentes del addon. A diferencia del "Smart Auto-Detect" que busca nombres de huesos, la **Consolidación Jerárquica** analiza la **forma y estructura del esqueleto**, no los nombres.

### 🎯 ¿Para qué sirve?

Sirve para completar automáticamente los mappings que faltan, **mapeando huesos twist, jingle bones y huesos extra** de forma automática. Es especialmente útil en modelos que usan idiomas extraños, nombres aleatorios o estructuras que no encajan en los perfiles estándar.

### 🛠️ ¿Cómo funciona?

El algoritmo usa reglas de herencia basadas en la posición del hueso en el árbol jerárquico:

1.  **Huesos de Cadenas Lineales (Linear Chains):** Si tienes un hueso mapeado (ej: `Brazo`) seguido de una cadena lineal (`Brazo.001`, `Brazo.002`), el extra hereda automáticamente el mapping del padre.
2.  **Huesos Hermanos (Siblings):** Útil para manos y pies. Si mapeas un dedo, los dedos hermanos pueden heredar ese mapping si están en la misma posición relativa.
3.  **Huesos Hoja (Leaf Bones):** Los huesos finales que no tienen hijos suelen ser huesos de punta o accesorios; estos heredan del padre más cercano.
4.  **Independencia de Nombres:** Funciona perfectamente con modelos chinos, japoneses, rusos o con nombres de huesos sin sentido, siempre que la estructura del rig sea humana.

### 💡 Tips de Consolidación:

- **Ejecútalo DESPUÉS del Smart Auto-Detect**: Primero carga los mappings principales y luego usa la consolidación para "rellenar los huecos".
- **Nuevos mappings arriba**: El addon coloca los mappings consolidados **al principio de la lista** (arriba del todo). Esto es porque suelen ser huesos auxiliares que, según nuestra "Regla de Oro", deben procesarse antes que los huesos principales.
- **Validación visual**: Al terminar, verás en la lista de mappings que el método de detección dice "Inherited from..." con un nivel de confianza basado en la distancia jerárquica.

---

## ⚠️ IMPORTANTE: Orden del Mapeo

### 🔄 ¿Cómo funcionan los Constraints?

**Explicación simple:** El addon crea constraints (restricciones) que copian las posiciones de los huesos. Estos constraints se procesan **de arriba hacia abajo**, uno por uno, en el orden exacto que aparece en la lista de mappings.

**¿Qué significa esto?**
- Si tienes varios huesos que mapean al mismo target (objetivo), el sistema los procesa en orden
- Cada constraint mueve el target a la posición del hueso source
- **El último constraint en la lista es el que "gana"** - es decir, el hueso target se quedará en la última posición que fue aplicada

**Ejemplo práctico:**
```
Si mapeas así (orden incorrecto):
1. Pelvis → Pelvis
2. Spine2 → Spine1
3. Spine → Spine1    ← Este se aplica último, Spine1 se queda aquí
4. Spine1 → Spine1
```
En este caso, `Spine1` terminará en la posición de `Spine` (el último), no en su posición correcta.

Por eso el orden es crítico: **los huesos auxiliares (twist y jinglebones) deben ir primero**, para que cuando se apliquen los huesos principales, estos ya estén correctamente posicionados.

---

### ✅ Ejemplo de Mapping Correcto (Rig Valve + Anime)

Tomando como referencia un rig de Valve (`valve_bone_mapping.json`) y añadiendo huesos típicos de un modelo de anime (pechos, falda, twist), así debería verse el orden para que el personaje se vea perfecto:

1.  **Huesos Twist (AL INICIO):**
    *   `ValveBiped.Bip01_L_UpperArm_Twist` → ` L UpperArm`
    *   `ValveBiped.Bip01_R_UpperArm_Twist` → ` R UpperArm`
    *   *¿Por qué?* Queremos que el brazo principal sobreescriba cualquier rotación extra del twist al final.

2.  **Jingle Bones (Anime/Accesorios):**
    *   `Breast_L` → ` Spine1` (Hueso del pecho izquierdo)
    *   `Breast_R` → ` Spine1` (Hueso del pecho derecho)
    *   `Side_Hair_L` → ` Head` (Hueso de pelo lateral)
    *   `Skirt_01_Front` → ` Pelvis` (Hueso de falda delantera)
    *   *¿Por qué?* Estos huesos deben procesarse antes que el tronco o la cabeza para que no "tiren" del modelo de forma incorrecta si el hueso principal se aplica después.

3.  **Huesos Duplicados (Secundarios):**
    *   `ValveBiped.Bip01_Spine` → ` Spine1`
    *   `ValveBiped.Bip01_Spine4` → ` Spine1`
    *   *¿Por qué?* Estos huesos ayudan a mover el torso, pero no son el punto central del pecho.

4.  **Huesos Principales (AL FINAL - ¡LOS QUE GANAN!):**
    *   `ValveBiped.Bip01_Pelvis` → ` Pelvis` (**GANA** sobre la falda)
    *   `ValveBiped.Bip01_Spine2` → ` Spine1` (**GANA** sobre pechos y otros spine - El Spine2 es el pecho real en Valve)
    *   `ValveBiped.Bip01_L_UpperArm` → ` L UpperArm` (**GANA** sobre el twist)
    *   `ValveBiped.Bip01_Head1` → ` Head` (**GANA** sobre el pelo)

**Regla de oro:** Lo que pongas más abajo en la lista es lo que el motor de Blender usará como posición final para ese hueso de GTA.

---

### 📐 Orden Correcto para los Mappings

#### 1. **Huesos Twist** (AL INICIO)

Los **twist bones** son huesos auxiliares que ayudan a crear deformaciones más suaves en las articulaciones (brazos, piernas, etc.).

**Ejemplos:**
- `Twist_Hand_Left` / `Twist_Hand_Right`
- `Twist_ForeArm_Left` / `Twist_ForeArm_Right`
- `Twist_UpperArm_Left` / `Twist_UpperArm_Right`
- `CC_Base_L_UpperarmTwist01` / `CC_Base_R_UpperarmTwist01`
- `bip01_l_upperarm_twist` / `bip01_r_upperarm_twist`

**Todos los twist bones deben ir primero**, antes que cualquier otro mapping.

---

#### 2. **Jinglebones** (DESPUÉS de twist bones, pero también al inicio)


- **Jinglebones:** Son huesos especiales que tienen una función específica en la animación (normalmente relacionados con movimiento secundario, como colgantes, accesorios, o partes que se mueven independientemente)
- **Huesos duplicados normales:** Son simplemente múltiples huesos que mapean al mismo target porque tu personaje tiene más huesos que GTA SA (ej: Spine2, Spine3 → todos a Spine1)

**Ejemplos de jinglebones (huesos especiales):**
- Huesos de accesorios que deben estar disponibles temprano
- Huesos de movimiento secundario
- Huesos que otros elementos necesitan referenciar

**Los jinglebones van DESPUÉS de los twist bones, pero ANTES de los huesos principales.**

---

#### 3. **Huesos Duplicados Normales** (Pueden ir mezclados con jinglebones o después)

Estos son huesos que simplemente mapean al mismo target porque tu personaje tiene más huesos que GTA SA necesita.

**Ejemplos:**
- `Spine2`, `Spine3` → todos a ` Spine1`
- `Neck1`, `Neck2` → todos a ` Neck`
- `LeftEye`, `RightEye` → ambos a ` Head`

**Diferencia clave con jinglebones:** Los jinglebones tienen una función especial, mientras que los huesos duplicados normales solo necesitan mapearse al mismo target porque hay más huesos de los que GTA SA soporta.

Estos pueden ir junto con los jinglebones al inicio, o pueden ir después. Lo importante es que estén antes de los huesos principales.

---

#### 4. **Huesos Principales** (AL FINAL, después de twist bones, jinglebones y duplicados)

Estos son los huesos principales del personaje que definen la estructura básica.
```
Root
  └─> Pelvis (Hips)
       └─> Spine
            └─> Spine1
                 └─> Neck
                      └─> Head
```

**Recordatorio:** Como los constraints se aplican de arriba hacia abajo, el último mapping que afecta a un target es el que "gana". Por eso los huesos principales van al final: queremos que el target termine en la posición del hueso principal, no en la de un twist bone o jinglebone.

---

## 🔧 Cómo verificar el orden en el addon:

1. Abre el panel **"Advanced Mapping"** en el addon
2. Revisa la lista de mappings en orden (de arriba hacia abajo)
3. Usa los botones **↑ (subir)** y **↓ (bajar)** para reordenar si es necesario
4. **Regla general**: 
   - Twist bones PRIMERO (al inicio absoluto)
   - Jinglebones DESPUÉS de twist bones (pero antes de principales)
   - Huesos duplicados normales (pueden ir con jinglebones o después)
   - Huesos principales AL FINAL (con padres antes que hijos)
   
   **Por qué:** Los constraints se aplican secuencialmente de arriba hacia abajo. El último mapping "gana", así que queremos que los huesos principales estén al final para que sus posiciones sean las finales.

---

## 💡 Tips importantes:

1. **Twist bones PRIMERO**: Todos los twist bones deben estar al inicio absoluto de la lista, antes que cualquier otro mapping.

2. **Jinglebones después de twist**: Los jinglebones (huesos especiales, no confundir con duplicados normales) van después de los twist bones, pero también al inicio, antes de los huesos principales.

3. **Huesos principales al final**: Los huesos principales van al final porque queremos que los targets terminen en sus posiciones (no en las de twist bones o jinglebones). Mantén el orden padre-hijo: Pelvis → Spine → Spine1 → Neck → Head.

4. **No confundir jinglebones con duplicados**: Los jinglebones son huesos especiales con función específica. Los huesos duplicados normales (como Spine2 → Spine1) simplemente mapean al mismo target porque hay más huesos que targets disponibles.

5. **Por qué importa el orden**: Los constraints se procesan de arriba hacia abajo. Si múltiples mappings afectan al mismo target, el último en la lista es el que queda. Por eso los principales van al final.

6. **Validación**: Usa el botón **"Validate Mappings"** para verificar que todos tus mappings sean válidos antes de convertir.

---

## 🚀 Uso básico:

1. **Seleccionar armatures**: En el panel principal, selecciona tu armature fuente y el armature objetivo de GTA SA.

2. **Detección automática**: Haz clic en **"🧠 1. Smart Auto-Detect"** para que el addon intente detectar y mapear automáticamente.

3. **Revisar mappings**: Ve al panel **"Advanced Mapping"** y revisa que todos los mappings sean correctos. Ajusta el orden si es necesario.

4. **Convertir**: Haz clic en **"🚀 2. Convert to GTA SA"** para iniciar la conversión.

5. **Resultado**: El addon te dejará un personaje convertido listo para usar en GTA SA.

---

## 📝 Notas técnicas:

- Los constraints que se crean son de tipo **COPY_LOCATION**, que copian la posición de un hueso source a un hueso target.
- **El orden importa críticamente** porque los constraints se procesan secuencialmente de arriba hacia abajo en la lista.
- **Regla clave:** Si varios mappings afectan al mismo target, el último en la lista es el que "gana" - el target se queda en esa última posición.
- Por eso los twist bones y jinglebones van AL INICIO: para que estén disponibles, pero no determinen la posición final.
- Los huesos principales van AL FINAL: para que sus posiciones sean las que queden al final del proceso.
- Dentro de los principales, los padres deben ir antes que los hijos para calcular correctamente las posiciones relativas.

---

## 🎓 Glosario de términos:

- **Armature**: La estructura de huesos que controla la animación del personaje
- **Bone Mapping**: La conexión entre un hueso fuente y un hueso objetivo
- **Constraint**: Una restricción que controla cómo un hueso se comporta respecto a otro
- **COPY_LOCATION**: Tipo de constraint que copia la posición de un hueso a otro
- **Source Bone**: El hueso original de tu personaje
- **Target Bone**: El hueso correspondiente en el sistema GTA SA
- **Twist Bone**: Hueso auxiliar que ayuda a crear deformaciones suaves en articulaciones
- **Jinglebone**: Hueso especial con función específica (normalmente movimiento secundario o accesorios). NO es lo mismo que un hueso duplicado normal.
- **Hueso Duplicado**: Hueso que mapea al mismo target que otro simplemente porque hay más huesos que targets disponibles (ej: Spine2 → Spine1 porque GTA SA solo tiene Spine1)
- **Vertex Groups**: Grupos de vértices de la malla que están asociados a un hueso específico
- **Weight**: El "peso" de influencia que un hueso tiene sobre un vértice de la malla

---

## 🆘 Solución de problemas:

**Problema**: Los huesos no se posicionan correctamente después de la conversión.

**Solución**: Verifica el orden de los mappings. Recuerda que los constraints se aplican de arriba hacia abajo, y el último mapping que afecta a un target es el que queda. Asegúrate de que:
- Twist bones estén PRIMERO (al inicio absoluto)
- Jinglebones estén después de twist bones (pero antes de principales)
- Huesos duplicados normales estén antes de principales
- Huesos principales estén AL FINAL (para que sus posiciones sean las finales)
- Dentro de los principales, los padres antes que los hijos (Pelvis → Spine → Spine1 → Neck → Head)

**Problema**: Los constraints no se aplican.

**Solución**: 
- Verifica que ambos huesos (source y target) existan en sus respectivos armatures
- Asegúrate de que los mappings estén habilitados (checkbox "Enabled")
- Usa el botón "Validate Mappings" para encontrar problemas

**Problema**: Algunos huesos no se detectan automáticamente.

**Solución**: 
- Edita manualmente el mapping en "Advanced Mapping"
- Puedes agregar nuevos mappings con el botón "Add Custom"
- Guarda tus mappings personalizados para usarlos después

---

## 📚 Créditos:

- **Desarrollador principal**: Yoshi Maincra
- **Herramienta de desarrollo**: Cursor AI
- **Beta testers**: LenX, NyxxyGirl

---

## 📄 Licencia y uso:

Este addon está hecho con ❤️ para la comunidad de modding de GTA SA.

Para más información, sugerencias o reportar bugs, contacta a través del canal de YouTube Yoshi Maincra.

---

**Versión**: 1.2  
**Compatibilidad**: Blender 4.5+ y 5.0+  

