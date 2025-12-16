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
# Re-encarpetador de Monumentos PRO

Herramienta en **Python + Tkinter** para reorganizar de forma **segura, controlada y auditable** la estructura interna de carpetas de monumentos arqueológicos.

Está pensada para trabajar con carpetas cuyo nombre sigue el patrón:

```
T[1-7]_#####
Ejemplo: T3_01234
```

---

## 📌 ¿Qué problema resuelve?

En muchos proyectos arqueológicos, los archivos de un monumento están sueltos dentro de su carpeta principal:

```
T3_01234/
 ├── foto1.jpg
 ├── plano.pdf
 ├── ceramica.xlsx
 └── prospeccion.docx
```

Esta herramienta permite **encarpetar automáticamente** todo el contenido dentro de subcarpetas temáticas como:

- `LITI`
- `CERA`
- `PROS`

Sin riesgo de pérdida de datos y con opciones de simulación, copia o movimiento real.

---

## 🧠 Modos de operación

La aplicación ofrece **tres modos**, seleccionables desde la interfaz:

### 🧪 1. Dry-run (Simulación)

- **No realiza cambios reales** en el sistema de archivos
- Muestra exactamente qué se movería o copiaría
- Ideal para validar antes de ejecutar

📄 Todas las acciones se registran en el archivo de log

---

### 🔁 2. Mover (modo seguro)

- Reorganiza el contenido **dentro de la carpeta original**
- Usa una carpeta temporal para evitar pérdidas
- Incluye rollback automático si ocurre un error

⚠️ Requiere confirmación del usuario

---

### 📄 3. Copiar

- Crea una **nueva estructura completa** en otra ubicación
- No modifica los archivos originales
- Evita sobrescrituras silenciosas

---

## 🗂️ Flujo general de funcionamiento

1. El usuario selecciona la carpeta base
2. El sistema detecta carpetas válidas (`T1_00001`, `T2_12345`, etc.)
3. Se crea la subcarpeta indicada (`LITI`, `CERA`, `PROS`, etc.)
4. El contenido se mueve, copia o simula
5. Se actualiza la barra de progreso
6. Se genera un archivo de log con todo el proceso

---

## 📁 Ejemplos de uso

### Ejemplo 1: Subcarpeta `LITI`

**Antes**

```
T3_01234/
 ├── lasca1.jpg
 ├── lasca2.jpg
 └── analisis_litico.pdf
```

**Después (modo mover)**

```
T3_01234/
 └── LITI/
     ├── lasca1.jpg
     ├── lasca2.jpg
     └── analisis_litico.pdf
```

---

### Ejemplo 2: Subcarpeta `CERA`

**Antes**

```
T5_04567/
 ├── ceramica_001.jpg
 ├── ceramica_002.jpg
 └── inventario_ceramica.xlsx
```

**Después (modo mover)**

```
T5_04567/
 └── CERA/
     ├── ceramica_001.jpg
     ├── ceramica_002.jpg
     └── inventario_ceramica.xlsx
```

---

### Ejemplo 3: Subcarpeta `PROS` (modo copiar)

**Origen**

```
T1_00089/
 ├── prospeccion.kml
 └── notas_pros.txt
```

**Destino**

```
DESTINO/
 └── T1_00089/
     └── PROS/
         ├── prospeccion.kml
         └── notas_pros.txt
```

---

## 📊 Barra de progreso

- Avanza **por carpeta de monumento**
- Permite saber cuánto falta
- Evita la sensación de bloqueo en procesos largos

---

## 📄 Archivo de log

En cada ejecución se genera un archivo como:

```
reencarpetado_20251215_142233.log
```

### Contiene:

- Modo de ejecución (DRY-RUN / MOVER / COPIAR)
- Carpetas procesadas
- Archivos movidos o copiados
- Errores
- Acciones simuladas

### Ejemplo de log

```
▶ Procesando T3_01234
[DRY-RUN] MOVER: lasca1.jpg -> LITI/lasca1.jpg
[DRY-RUN] MOVER: analisis_litico.pdf -> LITI/analisis_litico.pdf
```

---

## 🔐 Seguridad y prevención de errores

✔ Evita doble ejecución
✔ Rollback automático
✔ Confirmación antes de mover
✔ No sobrescribe carpetas destino
✔ Simulación previa disponible

---

## 🧩 Casos de uso ideales

- Proyectos arqueológicos
- Inventarios de campo
- Normalización de estructuras
- Preparación de datos para análisis
- Digitalización institucional

---

## 🚀 Recomendaciones finales

1. Ejecuta primero en **dry-run**
2. Revisa el archivo de log
3. Ejecuta en modo mover o copiar
4. Guarda los logs junto al proyecto

---

**Desarrollado para flujos arqueológicos reales, con énfasis en seguridad, trazabilidad y control.**
