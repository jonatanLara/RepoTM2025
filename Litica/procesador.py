import os
import re
import csv
import shutil
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
import collections


EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".JPG", ".JPEG")
ID_REGEX = re.compile(r"(T[1-7]_\d{5})")
REGEX_EXC = re.compile(r"T[1-7]_\d{5}_(\d{3}_\d{7})")


def es_archivo_macos(nombre_archivo):
    return nombre_archivo.startswith("._")


def recolectar_imagenes(root_dir):
    rutas = []
    for current_path, dirs, files in os.walk(root_dir):
        for file in files:
            if es_archivo_macos(file):
                continue

            if file.endswith(EXTS):
                rutas.append(os.path.join(current_path, file))
    return rutas


def procesar_imagen(file_path, output_dir):
    file_name = os.path.basename(file_path)

    if es_archivo_macos(file_name):
        return (file_name, file_path, "", "", "IGNORADO_MACOS")

    if not file_name.endswith(EXTS):
        return (file_name, file_path, "", "", "EXT_NO_VALIDO")

    match = ID_REGEX.search(file_name)
    if not match:
        return (file_name, file_path, "", "", "ID_NO_ENCONTRADO")

    id_monumento = match.group(1)
    carpeta_destino = os.path.join(output_dir, id_monumento)
    os.makedirs(carpeta_destino, exist_ok=True)

    destino = os.path.join(carpeta_destino, file_name)

    try:
        shutil.copy2(file_path, destino)
        return (file_name, file_path, destino, id_monumento, "COPIADO")
    except Exception as e:
        return (file_name, file_path, "", id_monumento, f"ERROR: {str(e)}")


def generar_excel(resultados, report_dir):
    excel_path = os.path.join(report_dir, "reporte_resumen.xlsx")
    wb = Workbook()

    # =================================================
    # Hoja 1
    # =================================================
    ws1 = wb.active
    ws1.title = "reporte_copiado"

    headers = ["Archivo", "Ruta Origen", "Ruta Destino", "ID Monumento", "Estado"]
    ws1.append(headers)

    for row in resultados:
        ws1.append(list(row))

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="4F81BD")

    for col in range(1, len(headers) + 1):
        cell = ws1.cell(row=1, column=col)
        cell.font = header_font
        cell.fill = header_fill

    tabla = Table(displayName="ReporteCopiado", ref=f"A1:E{len(resultados)+1}")
    estilo_tabla = TableStyleInfo(
        name="TableStyleMedium9",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    tabla.tableStyleInfo = estilo_tabla
    ws1.add_table(tabla)

    for col in ws1.columns:
        max_len = max(len(str(c.value)) for c in col if c.value)
        ws1.column_dimensions[col[0].column_letter].width = max_len + 2

    # =================================================
    # Resumen (Hoja 2)
    # =================================================
    ws2 = wb.create_sheet("resumen_ids")

    total_imagenes = len([r for r in resultados if r[4] == "COPIADO"])
    ids_monumento = [r[3] for r in resultados if r[3] != ""]
    contador_monumento = collections.Counter(ids_monumento)

    ids_excav = []
    for nombre, origen, destino, id_m, estado in resultados:
        match = REGEX_EXC.search(nombre)
        if match:
            ids_excav.append((id_m, match.group(1)))

    contador_excav = collections.Counter(ids_excav)

    ws2.append(["Resumen"])
    ws2.append(["Total imágenes procesadas", total_imagenes])
    ws2.append(["Total IDs monumento", len(contador_monumento)])
    ws2.append([])

    ws2.append(["ID Monumento", "Cantidad"])
    for id_m, count in contador_monumento.items():
        ws2.append([id_m, count])

    ws2.append([])
    ws2.append(["ID Monumento", "ID Excavación", "Cantidad"])
    for (id_m, id_exc), count in contador_excav.items():
        ws2.append([id_m, id_exc, count])

    wb.save(excel_path)
    return excel_path


def ejecutar_proceso(root_dir, output_dir, callback=None):
    """Callback = función para mandar mensajes a la UI."""
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_dir = os.path.join(output_dir, f"reportes_{fecha_hoy}")
    os.makedirs(report_dir, exist_ok=True)

    if callback:
        callback("Escaneando imágenes...")

    imagenes = recolectar_imagenes(root_dir)

    if callback:
        callback(f"{len(imagenes)} imágenes encontradas.")

    resultados = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futuros = {executor.submit(procesar_imagen, ruta, output_dir): ruta for ruta in imagenes}
        for future in as_completed(futuros):
            r = future.result()
            resultados.append(r)
            if callback:
                callback(f"{r[4]} → {r[0]}")

    # CSV
    csv_path = os.path.join(report_dir, "reporte_copiado.csv")
    with open(csv_path, "w", newline="", encoding="utf8") as f:
        w = csv.writer(f)
        w.writerow(["Archivo", "Ruta Origen", "Ruta Destino", "ID Monumento", "Estado"])
        w.writerows(resultados)

    excel_path = generar_excel(resultados, report_dir)

    return csv_path, excel_path
