import os
import shutil
import re
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from datetime import datetime
import pandas as pd
import platform
import subprocess

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Respaldo y Estructura de Informes - 2025")

        self.source_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="respaldo")

        self.not_copied = []
        self.generate_report = tk.BooleanVar(value=True)

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(main_frame, text="Carpeta Origen:").grid(row=0, column=0, sticky="w")
        ttk.Entry(main_frame, textvariable=self.source_var, width=60).grid(row=0, column=1)
        ttk.Button(main_frame, text="Buscar", command=self.choose_source).grid(row=0, column=2)

        ttk.Label(main_frame, text="Carpeta Destino:").grid(row=1, column=0, sticky="w")
        ttk.Entry(main_frame, textvariable=self.dest_var, width=60).grid(row=1, column=1)
        ttk.Button(main_frame, text="Buscar", command=self.choose_dest).grid(row=1, column=2)

        ttk.Label(main_frame, text="Modo de Operación:").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(main_frame, text="Respaldo 2025", variable=self.mode_var, value="respaldo").grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(main_frame, text="Estructura de Informes", variable=self.mode_var, value="informes").grid(row=3, column=1, sticky="w")

        ttk.Button(main_frame, text="Analizar Carpeta", command=self.analyze_folder).grid(row=4, column=1, pady=8)
        ttk.Button(main_frame, text="Limpiar Consola", command=self.clear_log).grid(row=4, column=2)

        ttk.Button(main_frame, text="Ejecutar", command=self.run).grid(row=5, column=1, pady=8)

        ttk.Checkbutton(
            main_frame,
            text="Generar reporte Excel de archivos no copiados",
            variable=self.generate_report
        ).grid(row=6, column=1, sticky="w", pady=(0,10))

        self.log = tk.Text(main_frame, width=60, height=15)
        self.log.grid(row=7, column=0, columnspan=3)

        # ✅ Barra de progreso
        self.progress = ttk.Progressbar(main_frame, length=300, mode="determinate")
        self.progress.grid(row=8, column=0, columnspan=3, pady=5)

        self.progress_label = ttk.Label(main_frame, text="Progreso: 0%")
        self.progress_label.grid(row=9, column=0, columnspan=3)

    def clear_log(self):
        self.log.delete("1.0", tk.END)

    def update_progress(self, current, total):
        percent = int((current / total) * 100)
        self.progress["value"] = percent
        self.progress_label.config(text=f"Progreso: {percent}%")
        self.root.update_idletasks()

    def choose_source(self):
        self.source_var.set(filedialog.askdirectory())

    def choose_dest(self):
        self.dest_var.set(filedialog.askdirectory())

    def log_message(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def analyze_folder(self):
        self.clear_log()
        source = self.source_var.get()
        pattern = re.compile(r"^[T][1-7]_\d{5}", re.IGNORECASE)
        try:
            monuments = [d.name for d in Path(source).iterdir() if d.is_dir() and pattern.match(d.name)]
            self.log_message(f"📂 Monumentos detectados: {len(monuments)}")
            for m in monuments:
                self.log_message(f" - {m}")
        except:
            self.log_message("❌ Error analizando carpeta.")

    def run(self):
        self.not_copied = []
        src = self.source_var.get()
        dst = self.dest_var.get()

        if not src or not dst:
            self.log_message("⚠️ Selecciona carpetas primero.")
            return

        if self.mode_var.get() == "respaldo":
            self.reorganize_respaldo(src, dst)
        else:
            self.reorganize_informes(src, dst)

        if self.generate_report.get() and self.not_copied:
            self.generate_excel_report(dst)

        self.open_folder(dst)
        self.log_message("✅ Proceso Finalizado")

    # RESPALDO 2025
    def reorganize_respaldo(self, source, destination):
        pattern = re.compile(r"^[T][1-7]_\d{5}", re.IGNORECASE)
        exclude = {"PROYECTO AGISOFT","FOTOS DE PROCESAMIENTO","FOTOS DE REGISTRO","FOTOS PROCESAMIENTO", "FOTOS REGISTRO", "PUNTOS DE CONTROL"}

        monuments = [d for d in Path(source).iterdir() if d.is_dir() and pattern.match(d.name)]
        total = len(monuments)

        for i, monument in enumerate(monuments, start=1):
            dest_root = Path(destination) / monument.name

            for root, dirs, files in os.walk(monument):
                current = Path(root)

                if any(part.upper() in exclude for part in current.parts):
                    continue

                relative = current.relative_to(monument)
                dest_folder = dest_root / relative
                dest_folder.mkdir(parents=True, exist_ok=True)

                for f in files:
                    try:
                        shutil.copy2(current / f, dest_folder / f)
                    except Exception as e:
                        self.not_copied.append((f, str(current / f), str(e), datetime.now()))

            self.update_progress(i, total)

        self.log_message("✅ Respaldo 2025 realizado exitosamente.")

    # INFORMES
    def reorganize_informes(self, source, destination):
        pattern = re.compile(r"^[T][1-7]_\d{5}", re.IGNORECASE)
        exclude = {"PRODUCTOS GENERADOS", "PROYECTO AGISOFT"}

        monuments = [d for d in Path(source).iterdir() if d.is_dir() and pattern.match(d.name)]
        total = len(monuments)

        for i, monument in enumerate(monuments, start=1):
            dest_root = Path(destination) / monument.name

            for root, dirs, files in os.walk(monument):
                current = Path(root)
                if any(part.upper() in exclude for part in current.parts):
                    continue

                relative = current.relative_to(monument)
                dest_folder = dest_root / relative
                dest_folder.mkdir(parents=True, exist_ok=True)

                for f in files:
                    try:
                        shutil.copy2(current / f, dest_folder / f)
                    except Exception as e:
                        self.not_copied.append((f, str(current / f), str(e), datetime.now()))

            self.update_progress(i, total)

        self.log_message("✅ Estructura de Informes copiada correctamente.")

    def generate_excel_report(self, destination):
        df = pd.DataFrame(self.not_copied, columns=["Archivo", "Ubicación Origen", "Motivo", "Fecha"])
        output = Path(destination) / f"reporte_no_copiados_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        df.to_excel(output, index=False)
        self.log_message(f"📊 Reporte generado: {output}")

    def open_folder(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
