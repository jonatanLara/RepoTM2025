import os
import re
import csv
import shutil
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# =========================
# CONFIGURACIÓN
# =========================
ROOT_DIR = r"E:\Respaldo general Laboratorio de Lítica 15 Noviembre 2025"
# Carpeta donde se guardará la copia reorganizada
OUTPUT_DIR = r"D:\Documentos\Github\RepoTM2025_litica\litica2"

# Extensiones válidas (mayúsculas y minúsculas)
EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".JPG", ".JPEG")

# Regex para ID de monumento
ID_REGEX = re.compile(r"(T[1-7]_\d{5})")

# Crear carpeta de salida
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fecha para reportes
fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Carpeta para reportes
REPORT_DIR = os.path.join(OUTPUT_DIR, f"reportes_{fecha_hoy}")
os.makedirs(REPORT_DIR, exist_ok=True)

# Archivo CSV del reporte
CSV_PATH = os.path.join(REPORT_DIR, "reporte_copiado.csv")

# =========================
# FUNCIÓN PARA PROCESAR UNA SOLA IMAGEN
# =========================
def procesar_imagen(file_path):

    file_name = os.path.basename(file_path)
    
    # Omitir archivos basura generados por MacOS
    if es_archivo_macos(file_name):
        return (file_name, file_path, "", "", "IGNORADO_MACOS")
    
    # Validar extensión
    if not file_name.endswith(EXTS):
        return (file_name, file_path, "", "", "EXTENSIÓN_NO_VÁLIDA")

    # Buscar ID de monumento
    match = ID_REGEX.search(file_name)
    if not match:
        return (file_name, file_path, "", "", "ID_NO_ENCONTRADO")

    id_monumento = match.group(1)

    # Crear carpeta destino para este ID
    carpeta_destino = os.path.join(OUTPUT_DIR, id_monumento)
    os.makedirs(carpeta_destino, exist_ok=True)

    destino = os.path.join(carpeta_destino, file_name)

    # Copiar archivo
    try:
        shutil.copy2(file_path, destino)
        return (file_name, file_path, destino, id_monumento, "COPIADO")
    except Exception as e:
        return (file_name, file_path, "", id_monumento, f"ERROR: {str(e)}")

# =========================
# DETECTOR DE ARCHIVOS MACOS
# =========================
def es_archivo_macos(nombre_archivo):
    """
    Devuelve True si el archivo es un duplicado creado por MacOS.
    Ejemplo: ._IMG_00123.JPG   (tamaño típico: 4 KB)
    """
    return nombre_archivo.startswith("._")

# =========================
# ESCANEAR TODAS LAS RUTAS
# =========================
def recolectar_imagenes():
    rutas = []
    for current_path, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            #  Saltar archivos basura MacOS
            if es_archivo_macos(file):
                continue
            
            if file.endswith(EXTS):
                rutas.append(os.path.join(current_path, file))
    return rutas


# =========================
# PROCESO PRINCIPAL
# =========================
def main():
    print("\n========== INICIANDO PROCESO ==========\n")

    todas_las_imagenes = recolectar_imagenes()
    total = len(todas_las_imagenes)

    print(f"📸 Imágenes encontradas: {total}")
    print("Procesando con múltiples hilos...\n")

    resultados = []

    # Pool de hilos
    with ThreadPoolExecutor(max_workers=8) as executor:
        futuros = {executor.submit(procesar_imagen, ruta): ruta for ruta in todas_las_imagenes}

        for future in as_completed(futuros):
            resultado = future.result()

            # Registrar
            resultados.append(resultado)

            nombre, origen, destino, id_m, estado = resultado
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {estado} → {nombre}")

    # =========================
    # GENERAR CSV
    # =========================
    with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Archivo", "Ruta Origen", "Ruta Destino", "ID Monumento", "Estado"])
        writer.writerows(resultados)

    print("\n========== PROCESO FINALIZADO ==========")
    print(f"📄 Reporte generado en: {CSV_PATH}")
    print(f"📂 Carpeta reorganizada en: {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()
