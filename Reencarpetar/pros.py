import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

# -------------------------------
# LOG
# -------------------------------
LOG_FILE = f"organizador_pdfs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# -------------------------------
# LÓGICA PRINCIPAL
# -------------------------------
def organizar_pdfs(base_path, modo, progress):
    patron_pdf = re.compile(r'^(T[1-7]_\d{5})\.pdf$', re.IGNORECASE)

    encontrados = []

    # Primera pasada: detectar
    for raiz, _, archivos in os.walk(base_path):
        if os.path.basename(raiz) == "PROS":
            continue

        for archivo in archivos:
            if patron_pdf.match(archivo):
                encontrados.append((raiz, archivo))

    total = len(encontrados)
    progress["maximum"] = total
    progress["value"] = 0

    if total == 0:
        log("No se encontraron PDFs válidos.")
        return 0, 0

    # Segunda pasada: procesar
    for raiz, archivo in encontrados:
        id_monumento = archivo.replace(".pdf", "")
        origen = os.path.join(raiz, archivo)

        carpeta_id = os.path.join(raiz, id_monumento)
        carpeta_pros = os.path.join(carpeta_id, "PROS")
        destino = os.path.join(carpeta_pros, archivo)

        log(f"\n▶ PDF detectado: {origen}")

        # Evitar reprocesar
        if os.path.exists(destino):
            log("  ↪ Saltado (ya existe en PROS)")
            progress["value"] += 1
            continue

        if modo == "dry-run":
            log(f"  [DRY-RUN] CREAR: {carpeta_pros}")
            log(f"  [DRY-RUN] {modo.upper()}: {origen} → {destino}")
            progress["value"] += 1
            continue

        try:
            os.makedirs(carpeta_pros, exist_ok=True)

            if modo == "mover":
                shutil.move(origen, destino)
            elif modo == "copiar":
                shutil.copy2(origen, destino)

            log(f"  ✔ {modo.upper()} OK")

        except Exception as e:
            log(f"  ✖ ERROR: {e}")

        progress["value"] += 1
        progress.update_idletasks()

    return total, total


# -------------------------------
# GUI
# -------------------------------
def seleccionar_carpeta(entry):
    ruta = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, ruta)


def ejecutar():
    carpeta = entrada_carpeta.get()
    modo = opcion_modo.get()

    if not carpeta or not os.path.isdir(carpeta):
        messagebox.showerror("Error", "Carpeta inválida")
        return

    if modo == "mover":
        if not messagebox.askyesno(
            "Confirmar",
            "Se moverán archivos PDF.\n¿Desea continuar?"
        ):
            return

    log(f"\n=== INICIO ({modo.upper()}) ===")

    try:
        procesados, total = organizar_pdfs(carpeta, modo, progress)
        log("=== FIN ===")

        messagebox.showinfo(
            "Finalizado",
            f"PDFs procesados: {procesados}/{total}\n\nLog:\n{LOG_FILE}"
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))


# -------------------------------
# VENTANA
# -------------------------------
root = tk.Tk()
root.title("Organizador de PDFs por Monumento")
root.geometry("650x420")

tk.Label(root, text="Carpeta / Unidad a analizar").pack(pady=5)
entrada_carpeta = tk.Entry(root, width=60)
entrada_carpeta.pack()
tk.Button(
    root,
    text="Seleccionar",
    command=lambda: seleccionar_carpeta(entrada_carpeta)
).pack(pady=5)

opcion_modo = tk.StringVar(value="dry-run")

tk.Label(root, text="Modo de operación").pack(pady=10)
tk.Radiobutton(root, text="Simulación (dry-run)", variable=opcion_modo, value="dry-run").pack()
tk.Radiobutton(root, text="Mover PDFs", variable=opcion_modo, value="mover").pack()
tk.Radiobutton(root, text="Copiar PDFs", variable=opcion_modo, value="copiar").pack()

progress = ttk.Progressbar(root, length=500)
progress.pack(pady=20)

tk.Button(
    root,
    text="Ejecutar",
    font=("Arial", 12, "bold"),
    bg="#4CAF50",
    fg="white",
    command=ejecutar
).pack(pady=10)

root.mainloop()
