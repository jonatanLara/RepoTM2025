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
OUTPUT_DIR = r"D:\Documentos\Github\RepoTM2025_litica\litica3"

EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".JPG", ".JPEG")

ID_REGEX = re.compile(r"(T[1-7]_\d{5})")

os.makedirs(OUTPUT_DIR, exist_ok=True)

fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

REPORT_DIR = os.path.join(OUTPUT_DIR, f"reportes_{fecha_hoy}")
os.makedirs(REPORT_DIR, exist_ok=True)

CSV_PATH = os.path.join(REPORT_DIR, "reporte_copiado.csv")


# =========================
# FUNCIÓN: detectar basura de Mac
# =========================
def es_archivo_macos(nombre_archivo):
    return nombre_archivo.startswith("._")


# =========================
# FUNCIÓN: procesar una imagen
# =========================
def procesar_imagen(file_path):

    file_name = os.path.basename(file_path)

    if es_archivo_macos(file_name):
        return (file_name, file_path, "", "", "IGNORADO_MACOS")

    if not file_name.endswith(EXTS):
        return (file_name, file_path, "", "", "EXTENSIÓN_NO_VÁLIDA")

    match = ID_REGEX.search(file_name)
    if not match:
        return (file_name, file_path, "", "", "ID_NO_ENCONTRADO")

    id_monumento = match.group(1)

    carpeta_destino = os.path.join(OUTPUT_DIR, id_monumento)
    os.makedirs(carpeta_destino, exist_ok=True)

    destino = os.path.join(carpeta_destino, file_name)

    try:
        shutil.copy2(file_path, destino)
        return (file_name, file_path, destino, id_monumento, "COPIADO")
    except Exception as e:
        return (file_name, file_path, "", id_monumento, f"ERROR: {str(e)}")


# =========================
# FUNCIÓN: recolectar imágenes
# =========================
def recolectar_imagenes():
    rutas = []
    for current_path, dirs, files in os.walk(ROOT_DIR):
        for file in files:

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

    with ThreadPoolExecutor(max_workers=8) as executor:
        futuros = {executor.submit(procesar_imagen, ruta): ruta for ruta in todas_las_imagenes}

        for future in as_completed(futuros):
            resultado = future.result()
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

    print("\n📄 Reporte CSV generado.")

    # =======================================================
    # GENERAR EXCEL DE RESUMEN (NUEVO)
    # =======================================================
    from openpyxl import Workbook
    import collections

    print("📘 Generando archivo Excel con resumen...")

    wb = Workbook()

    # ------------------------------
    # Hoja 1: Copia del reporte CSV
    # ------------------------------
    ws1 = wb.active
    ws1.title = "reporte_copiado"

    ws1.append(["Archivo", "Ruta Origen", "Ruta Destino", "ID Monumento", "Estado"])
    for row in resultados:
        ws1.append(list(row))

    # ------------------------------
    # Hoja 2: Resumen
    # ------------------------------
    ws2 = wb.create_sheet("resumen_ids")

    # Regex excavación
    regex_exc = re.compile(r"T[1-7]_\d{5}_(\d{3}_\d{7})")

    # Totales
    total_imagenes = len([r for r in resultados if r[4] == "COPIADO"])
    ids_monumento = [r[3] for r in resultados if r[3] != ""]
    contador_monumento = collections.Counter(ids_monumento)

    # Conteo por excavación
    ids_excav = []
    for nombre, origen, destino, id_m, estado in resultados:
        match = regex_exc.search(nombre)
        if match:
            ids_excav.append((id_m, match.group(1)))

    contador_excav = collections.Counter(ids_excav)

    # ------------------------------
    # Escribir resumen
    # ------------------------------
    ws2.append(["Resumen general"])
    ws2.append(["Total de imágenes procesadas", total_imagenes])
    ws2.append(["Total de IDs de monumento únicos", len(contador_monumento)])
    ws2.append([])
    ws2.append(["ID Monumento", "Cantidad de Imágenes"])

    for id_m, count in contador_monumento.items():
        ws2.append([id_m, count])

    ws2.append([])
    ws2.append(["ID Monumento", "ID Excavación", "Cantidad de Imágenes"])

    for (id_m, id_exc), count in contador_excav.items():
        ws2.append([id_m, id_exc, count])

    # Guardar Excel
    excel_path = os.path.join(REPORT_DIR, "reporte_resumen.xlsx")
    wb.save(excel_path)

    print(f"📘 Archivo Excel generado en: {excel_path}")

    print("\n========== PROCESO FINALIZADO ==========")
    print(f"📄 Reporte CSV: {CSV_PATH}")
    print(f"📘 Excel: {excel_path}")
    print(f"📂 Carpeta reorganizada en: {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()
