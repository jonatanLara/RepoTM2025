import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime


# -------------------------------
# LOG
# -------------------------------
LOG_FILE = f"reencarpetado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# -------------------------------
# LÓGICA PRINCIPAL
# -------------------------------
def procesar_carpetas(base_path, subcarpeta, modo, carpeta_destino, progress):
    patron = re.compile(r'^T[1-7]_\d{5}$')
    carpetas = [
        c for c in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, c)) and patron.match(c)
    ]

    total = len(carpetas)
    procesadas = 0

    progress["maximum"] = total
    progress["value"] = 0

    for carpeta in carpetas:
        ruta_monumento = os.path.join(base_path, carpeta)
        log(f"\n▶ Procesando {carpeta}")

        # Evitar doble ejecución
        if modo == "mover":
            if subcarpeta in os.listdir(ruta_monumento) and \
               len(os.listdir(ruta_monumento)) == 1:
                log("  ↪ Saltada (ya procesada)")
                progress["value"] += 1
                continue

        if modo == "mover":
            ruta_final = os.path.join(ruta_monumento, subcarpeta)
            ruta_tmp = os.path.join(ruta_monumento, "__tmp_reencarpetado__")
        else:
            ruta_final = os.path.join(carpeta_destino, carpeta, subcarpeta)

        try:
            if modo == "copiar" and os.path.exists(ruta_final):
                raise Exception(f"Destino ya existe: {ruta_final}")

            if modo == "mover" and modo != "dry-run":
                os.makedirs(ruta_tmp, exist_ok=True)

            if modo != "dry-run":
                os.makedirs(ruta_final, exist_ok=True)

            for item in os.listdir(ruta_monumento):
                if item in (subcarpeta, "__tmp_reencarpetado__"):
                    continue

                origen = os.path.join(ruta_monumento, item)

                if modo == "mover":
                    destino = os.path.join(ruta_tmp, item)
                    accion = "MOVER"
                else:
                    destino = os.path.join(ruta_final, item)
                    accion = "COPIAR"

                if modo == "dry-run":
                    log(f"  [DRY-RUN] {accion}: {origen} -> {destino}")
                    continue

                if modo == "mover":
                    shutil.move(origen, destino)
                else:
                    if os.path.isdir(origen):
                        shutil.copytree(origen, destino)
                    else:
                        shutil.copy2(origen, destino)

                log(f"  ✔ {accion}: {item}")

            if modo == "mover" and modo != "dry-run":
                for item in os.listdir(ruta_tmp):
                    shutil.move(
                        os.path.join(ruta_tmp, item),
                        os.path.join(ruta_final, item)
                    )
                os.rmdir(ruta_tmp)

            procesadas += 1

        except Exception as e:
            log(f"  ✖ ERROR: {e}")
            if modo == "mover" and os.path.exists(ruta_tmp):
                for item in os.listdir(ruta_tmp):
                    shutil.move(
                        os.path.join(ruta_tmp, item),
                        os.path.join(ruta_monumento, item)
                    )
                shutil.rmtree(ruta_tmp, ignore_errors=True)
            raise

        progress["value"] += 1
        progress.update_idletasks()

    return procesadas, total


# -------------------------------
# GUI
# -------------------------------
def seleccionar_carpeta(entry):
    ruta = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, ruta)


def ejecutar():
    carpeta = entrada_carpeta.get()
    subcarpeta = entrada_subcarpeta.get()
    modo = opcion_modo.get()
    destino = entrada_destino.get()

    if not carpeta or not os.path.isdir(carpeta):
        messagebox.showerror("Error", "Carpeta base inválida")
        return

    if not subcarpeta.strip():
        messagebox.showerror("Error", "Indique subcarpeta")
        return

    if modo == "copiar" and not os.path.isdir(destino):
        messagebox.showerror("Error", "Destino inválido")
        return

    if modo == "mover":
        if not messagebox.askyesno("Confirmar", "Se modificarán carpetas originales. ¿Continuar?"):
            return

    log(f"\n=== INICIO ({modo.upper()}) ===")

    try:
        procesadas, total = procesar_carpetas(
            carpeta, subcarpeta, modo, destino, progress
        )
        log("=== FIN ===")
        messagebox.showinfo(
            "Finalizado",
            f"Carpetas procesadas: {procesadas}/{total}\n\nLog:\n{LOG_FILE}"
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))


# -------------------------------
# VENTANA
# -------------------------------
root = tk.Tk()
root.title("Re-encarpetador de Monumentos PRO")
root.geometry("650x480")

tk.Label(root, text="Carpeta a analizar").pack()
entrada_carpeta = tk.Entry(root, width=60)
entrada_carpeta.pack()
tk.Button(root, text="Seleccionar",
          command=lambda: seleccionar_carpeta(entrada_carpeta)).pack()

tk.Label(root, text="Nombre subcarpeta").pack(pady=5)
entrada_subcarpeta = tk.Entry(root, width=40)
entrada_subcarpeta.pack()

opcion_modo = tk.StringVar(value="dry-run")

tk.Label(root, text="Modo").pack(pady=10)
tk.Radiobutton(root, text="Simulación (dry-run)", variable=opcion_modo, value="dry-run").pack()
tk.Radiobutton(root, text="Mover", variable=opcion_modo, value="mover").pack()
tk.Radiobutton(root, text="Copiar", variable=opcion_modo, value="copiar").pack()

tk.Label(root, text="Destino (solo copiar)").pack()
entrada_destino = tk.Entry(root, width=60)
entrada_destino.pack()
tk.Button(root, text="Seleccionar",
          command=lambda: seleccionar_carpeta(entrada_destino)).pack()

progress = ttk.Progressbar(root, length=500)
progress.pack(pady=20)

tk.Button(
    root,
    text="Ejecutar",
    font=("Arial", 12, "bold"),
    bg="#4CAF50",
    fg="white",
    command=ejecutar
).pack()

root.mainloop()
