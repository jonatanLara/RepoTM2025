import os
import re
import json
import shutil
import queue
import threading
import platform
import subprocess
from pathlib import Path
from datetime import datetime

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd


CONFIG_FILE = "config.json"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Respaldo y Estructura de Informes - 2025")

        # ---- Estado / variables ----
        self.source_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="respaldo")  # "respaldo" | "informes"
        self.generate_report = tk.BooleanVar(value=True)
        self.dark_mode = tk.BooleanVar(value=False)

        self.not_copied = []
        self.ui_queue = queue.Queue()

        # Cargar configuración (si existe)
        self.load_config()

        # Construir UI
        self.setup_ui()

        # Aplicar tema inicial
        if self.dark_mode.get():
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

        # Procesar cola de UI (para comunicación hilo->UI)
        self.root.after(100, self.process_ui_queue)

        # Guardar config al cerrar
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Trazas para guardar config en caliente
        self.source_var.trace_add("write", lambda *_: self.save_config())
        self.dest_var.trace_add("write", lambda *_: self.save_config())
        self.mode_var.trace_add("write", lambda *_: self.save_config())
        self.generate_report.trace_add("write", lambda *_: self.save_config())
        self.dark_mode.trace_add("write", lambda *_: self.save_config())

    # ------------------------------------------------------------------
    # Configuración persistente
    # ------------------------------------------------------------------
    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.source_var.set(data.get("source", ""))
                self.dest_var.set(data.get("dest", ""))
                self.mode_var.set(data.get("mode", "respaldo"))
                self.generate_report.set(bool(data.get("generate_report", True)))
                self.dark_mode.set(bool(data.get("dark_mode", False)))
        except Exception as e:
            print("No se pudo cargar config.json:", e)

    def save_config(self):
        data = {
            "source": self.source_var.get(),
            "dest": self.dest_var.get(),
            "mode": self.mode_var.get(),
            "generate_report": self.generate_report.get(),
            "dark_mode": self.dark_mode.get(),
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("No se pudo guardar config.json:", e)

    def on_close(self):
        self.save_config()
        self.root.destroy()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def setup_ui(self):
        # Menú superior (navbar)
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        menu_opciones = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opciones", menu=menu_opciones)
        menu_opciones.add_checkbutton(
            label="Modo Oscuro 🌙", onvalue=True, offvalue=False,
            variable=self.dark_mode, command=self.toggle_dark_mode
        )

        menu_tools = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=menu_tools)
        menu_tools.add_command(label="(CLI - próximamente)", state="disabled")

        menu_help = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_help)
        menu_help.add_command(
            label="Acerca de",
            command=lambda: messagebox.showinfo("Acerca de", "Sistema de Respaldo 2025\nINAH")
        )

        # Contenedor principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Layout expandible
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Origen / destino
        ttk.Label(main_frame, text="Carpeta Origen:").grid(row=0, column=0, sticky="w")
        ttk.Entry(main_frame, textvariable=self.source_var, width=60).grid(row=0, column=1, sticky="ew")
        ttk.Button(main_frame, text="Buscar", command=self.choose_source).grid(row=0, column=2, padx=(6, 0))

        ttk.Label(main_frame, text="Carpeta Destino:").grid(row=1, column=0, sticky="w")
        ttk.Entry(main_frame, textvariable=self.dest_var, width=60).grid(row=1, column=1, sticky="ew")
        ttk.Button(main_frame, text="Buscar", command=self.choose_dest).grid(row=1, column=2, padx=(6, 0))

        # Modo
        ttk.Label(main_frame, text="Modo de Operación:").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(main_frame, text="Respaldo 2025", variable=self.mode_var, value="respaldo").grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(main_frame, text="Estructura de Informes", variable=self.mode_var, value="informes").grid(row=3, column=1, sticky="w")

        # Acciones
        ttk.Button(main_frame, text="Analizar Carpeta", command=self.analyze_folder).grid(row=4, column=1, pady=8, sticky="w")
        ttk.Button(main_frame, text="Limpiar Consola", command=self.clear_log).grid(row=4, column=2, pady=8, sticky="w")

        ttk.Button(main_frame, text="Ejecutar", command=self.run).grid(row=5, column=1, pady=8, sticky="w")

        ttk.Checkbutton(
            main_frame,
            text="Generar reporte Excel de archivos no copiados",
            variable=self.generate_report
        ).grid(row=6, column=1, sticky="w", pady=(0, 10))

        # Log
        self.log = tk.Text(main_frame, width=60, height=15)
        self.log.grid(row=7, column=0, columnspan=3, sticky="nsew")
        main_frame.rowconfigure(7, weight=1)

        # Progreso
        self.progress = ttk.Progressbar(main_frame, length=300, mode="determinate")
        self.progress.grid(row=8, column=0, columnspan=3, pady=5, sticky="ew")

        self.progress_label = ttk.Label(main_frame, text="Progreso: 0%")
        self.progress_label.grid(row=9, column=0, columnspan=3, sticky="w")

    # ------------------------------------------------------------------
    # Temas (Claro / Oscuro)
    # ------------------------------------------------------------------
    def apply_dark_theme(self):
        style = ttk.Style()
        style.theme_use("clam")

        bg = "#1e1e1e"
        fg = "#ffffff"
        widget_bg = "#2b2b2b"

        # Ventana
        self.root.configure(bg=bg)

        # Estilos ttk
        style.configure(".", background=bg, foreground=fg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TFrame", background=bg)
        style.configure("TButton", background=widget_bg, foreground=fg)
        style.map("TButton", background=[("active", "#3a3a3a")])
        style.configure("TRadiobutton", background=bg, foreground=fg)
        style.configure("TCheckbutton", background=bg, foreground=fg)
        style.configure("TEntry", fieldbackground=widget_bg, foreground=fg)
        style.configure("Horizontal.TProgressbar", background="#4CAF50")

        # Text (no ttk)
        self.log.configure(bg=widget_bg, fg=fg, insertbackground=fg)

        self.dark_mode.set(True)

    def apply_light_theme(self):
        style = ttk.Style()
        style.theme_use("clam")

        bg = "#f0f0f0"
        fg = "#000000"

        self.root.configure(bg=bg)

        style.configure(".", background=bg, foreground=fg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TFrame", background=bg)
        style.configure("TButton", background="#e6e6e6", foreground=fg)
        style.map("TButton", background=[("active", "#d5d5d5")])
        style.configure("TRadiobutton", background=bg, foreground=fg)
        style.configure("TCheckbutton", background=bg, foreground=fg)
        style.configure("TEntry", fieldbackground="#ffffff", foreground=fg)
        style.configure("Horizontal.TProgressbar", background="#4CAF50")

        self.log.configure(bg="white", fg="black", insertbackground="black")

        self.dark_mode.set(False)

    def toggle_dark_mode(self):
        if self.dark_mode.get():
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
        self.save_config()

    # ------------------------------------------------------------------
    # Utilidades UI
    # ------------------------------------------------------------------
    def clear_log(self):
        self.log.delete("1.0", tk.END)

    def safe_log(self, msg):
        """Encolar mensaje para escribir en log desde el hilo de UI."""
        self.ui_queue.put(("log", msg))

    def safe_progress(self, current, total):
        self.ui_queue.put(("progress", (current, total)))

    def process_ui_queue(self):
        """Procesa mensajes encolados por el hilo de trabajo."""
        try:
            while True:
                kind, payload = self.ui_queue.get_nowait()
                if kind == "log":
                    self.log.insert(tk.END, payload + "\n")
                    self.log.see(tk.END)
                elif kind == "progress":
                    current, total = payload
                    percent = int((current / total) * 100) if total > 0 else 0
                    self.progress["value"] = percent
                    self.progress_label.config(text=f"Progreso: {percent}%")
                elif kind == "open_folder":
                    self._open_folder_impl(payload)
                elif kind == "done":
                    # Nada especial aquí, ya se habrá logueado al final
                    pass
        except queue.Empty:
            pass
        # reprogramar
        self.root.after(100, self.process_ui_queue)

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def choose_source(self):
        path = filedialog.askdirectory()
        if path:
            self.source_var.set(path)

    def choose_dest(self):
        path = filedialog.askdirectory()
        if path:
            self.dest_var.set(path)

    def analyze_folder(self):
        self.clear_log()
        source = self.source_var.get()
        pattern = re.compile(r"^[T][1-7]_\d{5}", re.IGNORECASE)
        try:
            monuments = [
                d.name for d in Path(source).iterdir()
                if d.is_dir() and pattern.match(d.name)
            ]
            self.safe_log(f"📂 Monumentos detectados: {len(monuments)}")
            for m in monuments:
                self.safe_log(f" - {m}")
        except Exception as e:
            self.safe_log(f"❌ Error analizando carpeta: {e}")

    def run(self):
        # Ejecutar en segundo hilo para no congelar la UI
        t = threading.Thread(target=self.process_run, daemon=True)
        t.start()

    def process_run(self):
        self.not_copied = []
        src = self.source_var.get()
        dst = self.dest_var.get()

        if not src or not dst:
            self.safe_log("⚠️ Selecciona carpetas primero.")
            return

        try:
            if self.mode_var.get() == "respaldo":
                self.reorganize_respaldo(src, dst)
            else:
                self.reorganize_informes(src, dst)

            if self.generate_report.get() and self.not_copied:
                self.generate_excel_report(dst)

            # Abrir carpeta destino al terminar (desde hilo UI)
            self.ui_queue.put(("open_folder", dst))
            self.safe_log("✅ Proceso Finalizado")
        except Exception as e:
            self.safe_log(f"❌ Error en la ejecución: {e}")
        finally:
            self.ui_queue.put(("done", None))

    # ------------------------------------------------------------------
    # Núcleo de negocio
    # ------------------------------------------------------------------
    def reorganize_respaldo(self, source, destination):
        """
        RESPALDO 2025:
        - Copiar TODA la estructura de cada carpeta de monumento T[1-7]_#####
        - Omitir COMPLETAMENTE la carpeta 'PROYECTO AGISOFT'
        - 'PRODUCTOS GENERADOS' se copia tal cual (sin filtros)
        - No se filtran extensiones: se copia todo lo permitido por las exclusiones
        """
        pattern = re.compile(r"^[T][1-7]_\d{5}", re.IGNORECASE)
        exclude = {"PROYECTO AGISOFT"}

        monuments = [d for d in Path(source).iterdir() if d.is_dir() and pattern.match(d.name)]
        total = len(monuments)

        if total == 0:
            self.safe_log("❌ No se encontraron monumentos.")
            self.safe_progress(1, 1)
            return

        for i, monument in enumerate(monuments, start=1):
            dest_root = Path(destination) / monument.name
            self.safe_log(f"📦 Respaldando: {monument.name}")

            for root, dirs, files in os.walk(monument):
                current = Path(root)

                # Omitir carpetas excluidas
                if any(part.upper() in exclude for part in current.parts):
                    continue

                relative = current.relative_to(monument)
                dest_folder = dest_root / relative
                dest_folder.mkdir(parents=True, exist_ok=True)

                for f in files:
                    src = current / f
                    dst_file = dest_folder / f
                    try:
                        shutil.copy2(src, dst_file)
                    except Exception as e:
                        self.not_copied.append((f, str(src), str(e), datetime.now()))
                        self.safe_log(f"❌ Error copiando {f}: {e}")

            self.safe_progress(i, total)

        self.safe_log("✅ Respaldo 2025 realizado exitosamente.")

    def reorganize_informes(self, source, destination):
        """
        ESTRUCTURA DE INFORMES:
        - Copiar TODA la estructura de cada carpeta de monumento T[1-7]_#####
        - Omitir COMPLETAMENTE: 'PRODUCTOS GENERADOS' y 'PROYECTO AGISOFT'
        - No se filtran extensiones: se copia todo lo permitido por las exclusiones
        """
        pattern = re.compile(r"^[T][1-7]_\d{5}", re.IGNORECASE)
        exclude = {"PRODUCTOS GENERADOS", "PROYECTO AGISOFT"}

        monuments = [d for d in Path(source).iterdir() if d.is_dir() and pattern.match(d.name)]
        total = len(monuments)

        if total == 0:
            self.safe_log("❌ No se encontraron monumentos.")
            self.safe_progress(1, 1)
            return

        for i, monument in enumerate(monuments, start=1):
            dest_root = Path(destination) / monument.name
            self.safe_log(f"📄 Copiando estructura: {monument.name}")

            for root, dirs, files in os.walk(monument):
                current = Path(root)

                if any(part.upper() in exclude for part in current.parts):
                    continue

                relative = current.relative_to(monument)
                dest_folder = dest_root / relative
                dest_folder.mkdir(parents=True, exist_ok=True)

                for f in files:
                    src = current / f
                    dst_file = dest_folder / f
                    try:
                        shutil.copy2(src, dst_file)
                    except Exception as e:
                        self.not_copied.append((f, str(src), str(e), datetime.now()))
                        self.safe_log(f"❌ Error copiando {f}: {e}")

            self.safe_progress(i, total)

        self.safe_log("✅ Estructura de Informes copiada correctamente.")

    # ------------------------------------------------------------------
    # Reporte y utilidades del sistema
    # ------------------------------------------------------------------
    def generate_excel_report(self, destination):
        
        try:
            df = pd.DataFrame(self.not_copied, columns=["Archivo", "Ubicación Origen", "Motivo/Error", "Fecha"])
            output = Path(destination) / f"reporte_no_copiados_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            df.to_excel(output, index=False)
            self.safe_log(f"📊 Reporte generado: {output}")
        except Exception as e:
            self.safe_log(f"❌ No se pudo generar el reporte: {e}")

    def _open_folder_impl(self, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            self.safe_log(f"⚠️ No se pudo abrir la carpeta destino: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
