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

# 🏺 Procesador de Imágenes Lítica

Aplicación de escritorio para clasificar, copiar, analizar y generar reportes de imágenes arqueológicas basadas en IDs de monumento y excavación.

---

## 🔎 Descripción General

Este programa permite **procesar grandes volúmenes de imágenes** que siguen un patrón específico en su nombre (por ejemplo: `T1_00003_114_0003057_1.jpg`).  
Su objetivo es reorganizarlas, clasificarlas automáticamente y generar reportes estructurados sobre los resultados.

Incluye una **interfaz gráfica (GUI) intuitiva en tema oscuro**, creada para que cualquier persona pueda usar la aplicación sin necesidad de conocimientos técnicos o de programación.

---

## 🧰 ¿Qué hace el programa?

La aplicación realiza las siguientes tareas:

1. **Escanea una carpeta completa** buscando imágenes válidas (`jpg`, `jpeg`, `png`, `tif`, `tiff`).
2. **Identifica automáticamente los IDs** presentes en el nombre de archivo:
   - **ID de monumento**: `T[1-7]_\d{5}`
   - **ID de excavación**: `XXX_XXXXXXX`
3. **Crea carpetas organizadas** para cada ID de monumento.
4. **Copia cada imagen a su carpeta correspondiente** dentro del directorio destino.
5. **Genera dos reportes automáticos**:
   - `reporte_copiado.csv`
   - `reporte_resumen.xlsx` (con tablas formateadas)
6. **Muestra una consola interna** con el progreso del procesamiento.
7. **Permite abrir la carpeta del reporte o el Excel con un solo clic**.

---

## ▶️ Cómo Usar

### 1. Ejecutar la aplicación

Abra el archivo `Procesador_Litica.exe`.

### 2. Seleccionar carpetas

- **Carpeta origen** → donde están las imágenes originales.
- **Carpeta destino** → donde se guardará la nueva organización y los reportes.

### 3. Vista previa

Permite saber cuántas imágenes se detectarán antes de procesar.

### 4. Ejecutar procesamiento

La barra de progreso comenzará a animarse y la consola mostrará:

- Imágenes copiadas
- IDs detectados
- Errores (si los hubiera)

### 5. Abrir resultados

Al finalizar:

- Botón **"Abrir carpeta del reporte"**
- Botón **"Abrir Excel generado"**

---

## 🧠 Lógica Interna

El programa tiene una arquitectura modular dividida en dos archivos:

### `procesador.py`

Contiene toda la lógica central:

- Búsqueda recursiva de imágenes
- Filtrado de extensiones válidas
- Regex para extraer IDs
- Clasificación y copia de archivos
- Generación del CSV
- Generación del Excel con estilos profesionales
- Función `ejecutar_proceso()` reutilizable para CLI o GUI

### `ui_tk.py`

Implementa la interfaz gráfica:

- Botones para seleccionar carpetas
- Vista previa de imágenes detectadas
- Barra de progreso animada
- Consola interna tipo terminal
- Botones para abrir resultados

---

## 🖥️ Características de la GUI

### ✔ Tema oscuro (Dark Mode)

Interfaz moderna, colores estilo Visual Studio Code.

### ✔ Barra de progreso animada

Indica que el procesamiento se está ejecutando.

### ✔ Consola de salida

Muestra logs en tiempo real:

- Estado de cada imagen
- IDs detectados
- Errores de copia
- Finalización del proceso

### ✔ Botones de acceso rápido

- Abrir carpeta del reporte
- Abrir Excel generado

### ✔ Ventana centrada y tamaño fijo

Facilita su uso en pantallas pequeñas o grandes.

---

## 📁 Salidas y Resultados

### **1. Carpeta organizada**

Dentro de la carpeta destino se creará:

```bash
├── T1_00001/
│   └── T1_00001_000_0000001_01.jpg
├── T1_00002/
│   └── T1_00002_000_0000001_01.jpg
├── T2_00005/
│   └── T1_00005_000_0000001_01.jpg
└── reportes_2025-11-16_18-22-40/
    ├── reporte_resumen.xlsx
    └── reporte_copiado.csv
```

### **2. CSV: `reporte_copiado.csv`**

Incluye:

- Nombre de archivo
- Ruta origen
- Ruta destino
- ID de monumento
- Estado (COPIADO, ERROR, IGNORADO)

### **3. Excel: `reporte_resumen.xlsx`**

Contiene dos hojas:

#### Hoja 1 → `reporte_copiado`

Copia del CSV con formato de tabla.

#### Hoja 2 → `resumen_ids`

Incluye:

- Total imágenes procesadas
- Total de IDs de monumento
- Conteo por ID
- Conteo por ID de excavación
- Detección de imágenes repetidas

---
