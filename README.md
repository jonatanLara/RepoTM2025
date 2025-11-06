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

# 📁 Gestor de Respaldo y Estructura de Informes - 2025

## 📋 Descripción General

Este proyecto proporciona **dos interfaces** para gestionar la copia y organización de carpetas de monumentos siguiendo patrones específicos:

- **Interfaz Gráfica (GUI)**: Aplicación desktop con tkinter
- **Interfaz de Línea de Comandos (CLI)**: Script para automatización

Ambas versiones permiten realizar dos tipos de operaciones:
- **Respaldo 2025**: Copia completa excluyendo ciertas carpetas
- **Estructura de Informes**: Copia selectiva para documentación

## 🎯 ¿Qué hace el programa?

### Funcionalidades Principales

1. **Detección Automática de Monumentos**
   - Identifica carpetas que siguen el patrón: `T[1-7]_#####` (ej: `T1_12345`, `T3_67890`)

2. **Dos Modos de Operación**
   - **Modo Respaldo**: Copia toda la estructura excluyendo carpetas de procesamiento
   - **Modo Informes**: Copia estructura excluyendo productos generados

3. **Exclusiones Inteligentes**
   - **Respaldo**: Excluye `PROYECTO AGISOFT`, `FOTOS DE PROCESAMIENTO`, `FOTOS DE REGISTRO`, `FOTOS PROCESAMIENTO`, `FOTOS REGISTRO`, `PUNTOS DE CONTROL`
   - **Informes**: Excluye `PRODUCTOS GENERADOS` y `PROYECTO AGISOFT`

4. **Reportes de Errores**
   - Genera archivos Excel con los archivos que no pudieron copiarse y el motivo

5. **Interfaz Amigable**
   - Barra de progreso en tiempo real
   - Consola de logs integrada
   - Temas claro/oscuro
   - Configuración persistente

## 🚀 Cómo Usar

### Interfaz Gráfica (GUI)

1. **Ejecutar la aplicación:**
    ProcesamientoREPO.exe
2. **Configurar las rutas:**

    - Carpeta Origen: Donde están las carpetas de monumentos
    - Carpeta Destino: Donde se guardarán los archivos copiados

3. **Seleccionar el modo:**

    -    Respaldo 2025: Para backup completo
    -    Estructura de Informes: Para documentación

4. **Opciones adicionales:**

    -   ✅ Analizar Carpeta: Ver qué monumentos se detectarán
    -   📊 Generar reporte Excel: Crear lista de archivos no copiados
    -   🌙 Modo Oscuro: Alternar entre tema claro/oscuro
    -   🧹 Limpiar Consola: Borrar los logs de la pantalla

5. **Ejecutar: Click en "Ejecutar" y monitorear el progreso**

Interfaz de Línea de Comandos (CLI)
```bash
    # Modo Respaldo con reporte
    python cli.py --source "C:\\Origen" --dest "D:\\Destino" --mode respaldo --report

    # Modo Respaldo simplificado
    python cli.py -s "C:\\Origen" -d "D:\\Destino" -m respaldo -r

    # Modo Informes sin reporte
    python cli.py --source "/ruta/origen" --dest "/ruta/destino" --mode informes

    # Parámetros disponibles:
    # --source, -s    Ruta origen (requerido)
    # --dest, -d      Ruta destino (requerido)  
    # --mode, -m      Modo: respaldo/informes (default: respaldo)
    # --report, -r    Generar reporte Excel
```

## 🔧 Lógica Interna
### Flujo de Procesamiento

1. **Detección de Monumentos**
```python
    pattern = re.compile(r"^[T][1-7]_\d{5}", re.IGNORECASE)
    monuments = [d for d in Path(source).iterdir() if d.is_dir() and pattern.match(d.name)]
```

2. Recorrido y Filtrado

    * Recorre recursivamente cada carpeta de monumento usando os.walk()
    * Omite carpetas según las exclusiones del modo seleccionado
    * Mantiene la estructura de directorios original

3. Copia Segura

    * Usa shutil.copy2() que preserva metadatos y timestamps
    * Manejo de excepciones para errores de archivo individuales
    * Progreso en tiempo real con actualización de UI

4. Generación de Reportes

    * Crea DataFrame con pandas
    * Exporta a Excel con timestamp en el nombre
    * Incluye: archivo, ubicación origen, error y fecha

```bash
    Carpeta_Origen/
    ├── T1_12345/
    │   ├── DOCUMENTOS/
    │   ├── FOTOS/
    │   ├── PROYECTO AGISOFT/          # ← Excluido en ambos modos
    │   └── PRODUCTOS GENERADOS/       # ← Excluido solo en Informes
    ├── T2_67890/
    ├── T3_54321/
    └── ...
```

## Características Técnicas
* Multiplataforma: Funciona en Windows, macOS, Linux
* Threading: Interfaz responsive durante operaciones largas
* Persistencia: Guarda configuración en config.json
* Temas: Soporte para modo claro/oscuro
* Logging: Consola integrada con mensajes descriptivos
* Manejo de Errores: Continuación después de errores individuales

## ⚙️ Requisitos e Instalación
### Dependencias Python
```bash
    pip install pandas openpyxl
```

```bash
    pandas>=1.5.0
    openpyxl>=3.0.0
```

### Compatibilidad

* Python: 3.7+
* Sistemas Operativos: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
## 🎨 Características de la GUI
### Elementos de la Interfaz

* Selector de carpetas con botones "Buscar"
* Radio buttons para selección de modo
* Barra de progreso visual con porcentaje
* Consola de texto con scroll automático
* Checkbox para generación de reportes
* Menú superior con opciones y ayuda
### Funcionalidades de UI

* Tema Oscuro/Claro: Persistente entre sesiones
* Logs en Tiempo Real: Mensajes durante la ejecución
* Progreso Visual: Barra y porcentaje actualizados
* Auto-apertura: Carpeta destino al finalizar
* Configuración Persistente: Recuerda rutas y preferencias
## 📊 Salidas y Resultados
```bash
Carpeta_Destino/
├── T1_12345/
│   ├── DOCUMENTOS/
│   │   ├── informe.pdf
│   │   └── planos.dwg
│   └── FOTOS/
│       ├── foto1.jpg
│       └── foto2.jpg
├── T2_67890/
└── ...
```

Reportes Generados
* Nombre: ``reporte_no_copiados_YYYYMMDD_HHMM.xlsx``
* Columnas:
    * Archivo: Nombre del archivo problemático
    * Ubicación Origen: Ruta completa de origen
    * Motivo/Error: Descripción del error
    * Fecha: Timestamp del error

## Logs de Consola
```bash
📂 Monumentos detectados: 5
 - T1_12345
 - T2_67890
 - T3_54321
📦 Respaldando: T1_12345
❌ Error copiando archivo_corrupto.jpg: [Errno 13] Permission denied
✅ Respaldo 2025 realizado exitosamente.
📊 Reporte generado: D:\Destino\reporte_no_copiados_20250115_1430.xlsx
```

## 📝 Notas de Versión
### v1.0 Características
* Interfaz gráfica y CLI
* Dos modos de operación
* Reportes Excel automáticos
* Temas claro/oscuro
* Configuración persistente
* Progreso en tiempo real
* Manejo robusto de errores
