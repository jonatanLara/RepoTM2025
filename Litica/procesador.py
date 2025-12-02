import os
import re
import csv
import time
import shutil
from datetime import datetime
from openpyxl import Workbook

# ==============================
# CONFIGURACIÓN
# ==============================

EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".JPG", ".JPEG")
ID_REGEX = re.compile(r"(T[1-7]_\d{5})")
REGEX_EXC = re.compile(r"T[1-7]_\d{5}_(\d{3}_\d{7})")


# ==============================
# UTILIDADES
# ==============================

def es_archivo_macos(nombre):
    return nombre.startswith("._")


def recolectar_imagenes(root_dir):
    rutas = []
    for current_path, dirs, files in os.walk(root_dir):
        for file in files:
            if es_archivo_macos(file):
                continue
            if file.endswith(EXTS):
                rutas.append(os.path.join(current_path, file))
    return rutas


def copiar_con_reintentos(src, dst, intentos=5, espera=0.7):
    for intento in range(1, intentos + 1):
        try:
            shutil.copy2(src, dst)
            return "OK"
        except Exception as e:
            if intento < intentos:
                time.sleep(espera)
            else:
                return f"ERROR: {str(e)}"


def procesar_en_batches(rutas, tam_batch=1000):
    for i in range(0, len(rutas), tam_batch):
        yield rutas[i:i + tam_batch]


# ==============================
# PROCESAR UNA SOLA IMAGEN
# ==============================

def procesar_imagen_mejorado(file_path, output_dir, log_path):

    file_name = os.path.basename(file_path)

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\nProcesando: {file_name}\n")

    if es_archivo_macos(file_name):
        estado = "IGNORADO_MACOS"
        destino = ""
        id_monumento = ""

    else:
        match = ID_REGEX.search(file_name)
        if not match:
            estado = "ID_NO_ENCONTRADO"
            destino = ""
            id_monumento = ""

        else:
            id_monumento = match.group(1)

            carpeta_destino = os.path.join(output_dir, id_monumento)
            os.makedirs(carpeta_destino, exist_ok=True)

            destino = os.path.join(carpeta_destino, file_name)

            estado = copiar_con_reintentos(file_path, destino)

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"Estado: {estado}\n")

    return (file_name, file_path, destino, id_monumento, estado)


# ==============================
# PROCESAMIENTO GENERAL + CSV
# ==============================

def procesar_imagenes_batch(root_dir, output_dir, reporte_path, callback=None, tam_batch=1000):

    rutas = recolectar_imagenes(root_dir)
    total = len(rutas)

    # LOG
    log_path = os.path.join(os.path.dirname(reporte_path), "log_procesamiento.txt")
    with open(log_path, "a", encoding="utf-8") as log:
        log.write("\n\n" + ("=" * 60) + "\n")
        log.write(f"INICIO DEL PROCESAMIENTO: {datetime.now()}\n")
        log.write(f"Total de imágenes encontradas: {total}\n")
        log.write(("=" * 60) + "\n")

    if callback:
        callback(f"Total de imágenes encontradas: {total}")

    resultados = []
    batch_num = 1

    for batch in procesar_en_batches(rutas, tam_batch=tam_batch):
        if callback:
            callback(f"Procesando batch {batch_num} ({len(batch)} imágenes)...")

        for file_path in batch:
            resultado = procesar_imagen_mejorado(file_path, output_dir, log_path)
            resultados.append(resultado)

        time.sleep(0.5)
        batch_num += 1

    # Guardar reporte CSV
    with open(reporte_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Archivo", "Origen", "Destino", "ID", "Estado"])
        writer.writerows(resultados)

    return resultados, log_path


# ==============================
# GENERAR EXCEL
# ==============================

def generar_excel(resultados, excel_path):

    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"

    ws.append(["Archivo", "Origen", "Destino", "ID", "Estado"])

    for fila in resultados:
        ws.append(list(fila))

    wb.save(excel_path)
    return excel_path


# ==============================
# FUNCIÓN QUE ESPERA TU UI
# ==============================

def ejecutar_proceso(folder_origen, folder_destino, callback=None):

    # Rutas del reporte
    reporte_csv = os.path.join(folder_destino, "reporte_copiado.csv")
    reporte_excel = os.path.join(folder_destino, "reporte_copiado.xlsx")

    if callback:
        callback("Iniciando procesamiento...")

    resultados, log_path = procesar_imagenes_batch(
        folder_origen,
        folder_destino,
        reporte_csv,
        callback=callback,
        tam_batch=1000
    )

    if callback:
        callback("Generando Excel...")

    generar_excel(resultados, reporte_excel)

    if callback:
        callback(f"Reporte generado:\nCSV → {reporte_csv}\nExcel → {reporte_excel}")
        callback("Proceso finalizado correctamente.")

    return reporte_csv, reporte_excel
