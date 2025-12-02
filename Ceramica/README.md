<p align="center">
  <img 
    src="https://github.com/jonatanLara/jonatanLara/blob/main/src/header_3_t.png?raw=true" 
    alt="Hoja Calendario"
    width="73%"
  />
</p>

<p align="center">
  <a href="https://github.com/jonatanLara">🐙 GitHub</a> |
  <a href="https://www.youtube.com/@jonatanlara">📺 YouTube</a> |
  <a href="https://www.instagram.com/jonatanlaraortiz/">📸 Instagram</a>
</p>
<br>

# 🗂️ Reencarpetador de Láminas Finales

Organiza automáticamente imágenes arqueológicas en una estructura estandarizada por _ID de monumento_ y _categoría_ (COMPLETAS, MISCELANEAS, NO COMPLETAS).

---

# 🔎 Descripción General

Este programa permite **analizar una carpeta completa de fotografías arqueológicas**, localizar aquellas dentro de carpetas llamadas **LAMINA FINAL**, extraer su categoría (COMPLETA, MISCELANEA, NO COMPLETA), interpretar el **ID de monumento** desde el nombre del archivo y finalmente **copiar las imágenes** a una nueva carpeta organizada y normalizada.

La herramienta incluye una **interfaz gráfica en Tkinter** y un **procesador inteligente** que corrige errores comunes en los nombres de las carpetas.

---

# 🧰 ¿Qué hace el programa?

✔ Recorre automáticamente toda la carpeta de origen.  
✔ Busca únicamente imágenes dentro de **LAMINA FINAL**.  
✔ Extrae el _ID de monumento_ desde el nombre del archivo.  
✔ Detecta la _categoría_ según la carpeta superior:

- COMPLETA / COMPLETAS
- MISCELANEA / MISCELANEAS
- NO COMPLETA / NO COMPLETAS
- Soporta variaciones con acentos (misceláneo, completás, etc.)  
  ✔ Normaliza todas las categorías a su forma estándar en plural:

| Encontrado  | Convertido a |
| ----------- | ------------ |
| completa    | COMPLETAS    |
| misceláneos | MISCELANEAS  |
| no completa | NO COMPLETAS |

✔ Copia las imágenes a una estructura organizada:

```bash
DESTINO/
└── T1_00044/
├── COMPLETAS/
├── MISCELANEAS/
└── NO COMPLETAS/
```

✔ Mantiene nombres originales.  
✔ Genera logs en tiempo real.  
✔ Muestra un resumen final de errores e imágenes copiadas.

---

# ▶️ Cómo Usar

## 1️⃣ Ejecutar el programa

Puedes iniciar la aplicación corriendo:

```bash
python ui_tk.py
```

(O bien usar el archivo .exe generado con PyInstaller).

## 2️⃣ Seleccionar Carpeta Origen

Debe ser una carpeta con estructura similar a:

```bash

TRAMO 1/
 ├── COMPLETA/
 ├── MISCELANEA/
 └── NO COMPLETA/
Cada una contiene carpetas con IDs completos como:

```

```bash

Copiar código
T1_00044_118_0001406/
    LAMINA FINAL/
        T1_00044_118_0001406.jpg

```

## 3️⃣ Seleccionar Carpeta Destino

Será donde se genere la nueva estructura final organizada.

## 4️⃣ Analizar Carpeta

El programa mostrará:

Imágenes encontradas

IDs detectados

Categorías detectadas

Problemas comunes de nombre

## 5️⃣ Procesar y Copiar

La barra de progreso se animará y comenzará el reencarpetado.

## 🧠 Lógica Interna

La lógica utiliza estos pasos:

1. Recorrido del sistema de archivos

Utiliza os.walk para encontrar carpetas llamadas LAMINA FINAL.

2. Detección de categorías

Se toma el abuelo de la carpeta:

```bash
CATEGORIA → ID COMPLETO → LAMINA FINAL → archivo.jpg
```

3. Normalización inteligente

Se limpia acentos, espacios, guiones, mayúsculas, plurales/singulares:

Entrada → “misceláneo”, “Miscelaneas”, “MIS-CELÁNEA”
Salida normalizada → MISCELANEAS

4. Extracción del ID de monumento

Usa el patrón:

```bash
T{1-7}_{00000}
```

Ejemplo:

```bash
T1_00044_118_0001406.jpg
││  └─ ID excavación (ignoramos)
└└──── ID monumento = T1_00044

```

5. Reencarpetado

Genera la estructura:

```bash
DESTINO/
  └── ID_MONUMENTO/
         └── CATEGORIA_NORMALIZADA/
                └── imagen.jpg
```

📁 Salidas y Resultados
📌 Carpeta destino generada:

Estructura completamente reorganizada:

```bash
T1_00003/
 └── MISCELANEAS/
      └── T1_00003_114_0003058.jpg

T1_00044/
 ├── COMPLETAS/
 │     └── T1_00044_118_0001406.jpg
 └── NO COMPLETAS/
       └── T1_00044_118_0001458.jpg

```
