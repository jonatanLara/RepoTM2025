import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

# -------------------------------
# LOG
# -------------------------------
LOG_FILE = f"organizador_pdfs_copia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# -------------------------------
# LÓGICA PRINCIPAL
# -------------------------------
def organizar_pdfs_copia(origen_base, destino_base, modo, progress):
    patron_pdf = re.compile(r'^(T[1-7]_\d{5})\.pdf$', re.IGNORECASE)
    encontrados = []

    # Detectar PDFs
    for raiz, _, archivos in os.walk(origen_base):
        if os.path.basename(raiz) == "PROS":
            continue

        for archivo in archivos:
            if patron_pdf.match(archivo):
                encontrados.append(os.path.join(raiz, archivo))

    total = len(encontrados)
    progress["maximum"] = total
    progress["value"] = 0

    if total == 0:
        log("No se encontraron PDFs válidos.")
        return 0, 0

    for origen_pdf in encontrados:
        archivo = os.path.basename(origen_pdf)
        id_monumento = archivo.replace(".pdf", "")

        carpeta_destino = os.path.join(destino_base, id_monumento, "PROS")
        destino_pdf = os.path.join(carpeta_destino, archivo)

        log(f"\n▶ PDF: {origen_pdf}")

        if modo == "dry-run":
            log(f"  [DRY-RUN] CREAR: {carpeta_destino}")
            log(f"  [DRY-RUN] COPIAR: {origen_pdf} → {destino_pdf}")
            progress["value"] += 1
            continue

        try:
            os.makedirs(carpeta_destino, exist_ok=True)

            if not os.path.exists(destino_pdf):
                shutil.copy2(origen_pdf, destino_pdf)
                log("  ✔ COPIADO OK")
            else:
                log("  ↪ Saltado (ya existe)")

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
    origen = entrada_origen.get()
    destino = entrada_destino.get()
    modo = opcion_modo.get()

    if not origen or not os.path.isdir(origen):
        messagebox.showerror("Error", "Carpeta de origen inválida")
        return

    if not destino or not os.path.isdir(destino):
        messagebox.showerror("Error", "Carpeta destino inválida")
        return

    log(f"\n=== INICIO ({modo.upper()}) ===")

    try:
        procesados, total = organizar_pdfs_copia(
            origen, destino, modo, progress
        )
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
root.title("Organizador de PDFs (Copia segura)")
root.geometry("700x460")

tk.Label(root, text="Carpeta ORIGEN (no se modifica)").pack(pady=5)
entrada_origen = tk.Entry(root, width=65)
entrada_origen.pack()
tk.Button(
    root,
    text="Seleccionar",
    command=lambda: seleccionar_carpeta(entrada_origen)
).pack(pady=5)

tk.Label(root, text="Carpeta DESTINO (estructura nueva)").pack(pady=5)
entrada_destino = tk.Entry(root, width=65)
entrada_destino.pack()
tk.Button(
    root,
    text="Seleccionar",
    command=lambda: seleccionar_carpeta(entrada_destino)
).pack(pady=5)

opcion_modo = tk.StringVar(value="dry-run")

tk.Label(root, text="Modo").pack(pady=10)
tk.Radiobutton(root, text="Simulación (dry-run)", variable=opcion_modo, value="dry-run").pack()
tk.Radiobutton(root, text="Copiar y re-encarpetar", variable=opcion_modo, value="copiar").pack()

progress = ttk.Progressbar(root, length=550)
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
