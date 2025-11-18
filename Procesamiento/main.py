# main.py  - Parte 1/3
# Importaciones y configuración inicial
import os
import sys
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

# -------------------------
# Utilidades para entorno
# -------------------------
def get_base_path():
    """
    Devuelve la carpeta base del exe o script.
    Funciona tanto en script .py como en .exe creado con PyInstaller.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent

# -------------------------
# Clase principal App
# -------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("ProcesamientoREPO - 2025")

        # Variables UI
        self.source_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="respaldo")  # 'respaldo' o 'informes'
        self.generate_report = tk.BooleanVar(value=True)
        self.dark_mode = tk.BooleanVar(value=False)

        # Report path: por defecto ./reporte relativo al exe
        self.report_path_absolute = False
        self.report_path = Path(get_base_path() / "reporte")

        # Cola para comunicacion hilo->UI y lista de no copiados
        self.ui_queue = queue.Queue()
        self.not_copied = []

        # Cargar configuración si existe
        self.load_config()

        # Construir UI
        self.setup_ui()

        # Aplicar tema actual
        if self.dark_mode.get():
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

        # Procesar cola periódicamente
        self.root.after(100, self.process_ui_queue)

        # Guardar config al cerrar
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # -------------------------
    # Config persistente
    # -------------------------
    def load_config(self):
        if not Path(CONFIG_FILE).exists():
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.source_var.set(data.get("source", ""))
            self.dest_var.set(data.get("dest", ""))
            self.mode_var.set(data.get("mode", "respaldo"))
            self.generate_report.set(data.get("generate_report", True))
            self.dark_mode.set(data.get("dark_mode", False))
            self.report_path_absolute = data.get("report_path_absolute", False)
            rp = data.get("report_path", "")
            if rp:
                if self.report_path_absolute:
                    self.report_path = Path(rp)
                else:
                    self.report_path = Path(get_base_path()) / rp
        except Exception as e:
            print("Error cargando config:", e)

    def save_config(self):
        # Guardar report_path relativo si no es absoluta
        rp_to_save = str(self.report_path) if self.report_path_absolute else "reporte"
        data = {
            "source": self.source_var.get(),
            "dest": self.dest_var.get(),
            "mode": self.mode_var.get(),
            "generate_report": self.generate_report.get(),
            "dark_mode": self.dark_mode.get(),
            "report_path": rp_to_save,
            "report_path_absolute": self.report_path_absolute,
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Error guardando config:", e)

    def on_close(self):
        self.save_config()
        self.root.destroy()

    # -------------------------
    # Construcción UI
    # -------------------------
    def setup_ui(self):
        # Menu / navbar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        menu_opciones = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opciones", menu=menu_opciones)
        menu_opciones.add_checkbutton(label="Modo Oscuro 🌙", variable=self.dark_mode, command=self.toggle_dark_mode)
        menu_opciones.add_command(label="Configuración de reportes…", command=self.open_config_window)
        menu_opciones.add_command(label="Abrir carpeta de reportes", command=self.open_report_folder)

        menu_tools = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=menu_tools)
        menu_tools.add_command(label="CLI (ver readme)", state="disabled")

        menu_help = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_help)
        menu_help.add_command(label="Acerca de", command=lambda: messagebox.showinfo("Acerca de", "ProcesamientoREPO - 2025"))

        # Main frame
        main = ttk.Frame(self.root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        # Origen
        ttk.Label(main, text="Carpeta Origen:").grid(row=0, column=0, sticky="w")
        ttk.Entry(main, textvariable=self.source_var).grid(row=0, column=1, sticky="ew")
        ttk.Button(main, text="Buscar", command=self.choose_source).grid(row=0, column=2, padx=6)

        # Destino
        ttk.Label(main, text="Carpeta Destino:").grid(row=1, column=0, sticky="w")
        ttk.Entry(main, textvariable=self.dest_var).grid(row=1, column=1, sticky="ew")
        ttk.Button(main, text="Buscar", command=self.choose_dest).grid(row=1, column=2, padx=6)

        # Modo
        ttk.Label(main, text="Modo de operación:").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(main, text="Respaldo 2025", variable=self.mode_var, value="respaldo").grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(main, text="Estructura de Informes", variable=self.mode_var, value="informes").grid(row=3, column=1, sticky="w")

        # Botones
        ttk.Button(main, text="Analizar Carpeta", command=self.analyze_folder).grid(row=4, column=1, sticky="w", pady=6)
        ttk.Button(main, text="Limpiar Consola", command=self.clear_log).grid(row=4, column=2, sticky="w", pady=6)

        ttk.Button(main, text="Ejecutar", command=self.run).grid(row=5, column=1, sticky="w", pady=6)

        ttk.Checkbutton(main, text="Generar reporte Excel de no copiados", variable=self.generate_report).grid(row=6, column=1, sticky="w", pady=(0,8))

        # Log
        self.log = tk.Text(main, height=14)
        self.log.grid(row=7, column=0, columnspan=3, sticky="nsew")
        main.rowconfigure(7, weight=1)

        # Progreso
        self.progress = ttk.Progressbar(main, mode="determinate")
        self.progress.grid(row=8, column=0, columnspan=3, sticky="ew", pady=6)
        self.progress_label = ttk.Label(main, text="Progreso: 0%")
        self.progress_label.grid(row=9, column=0, columnspan=3, sticky="w")

    # -------------------------
    # Ventana de configuracion (menu)
    # -------------------------
    def open_config_window(self):
        win = tk.Toplevel(self.root)
        win.title("Configuración de reportes")
        win.geometry("480x160")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text="Ruta donde se guardarán los reportes:").pack(pady=(10,4))
        rp_label = ttk.Label(win, text=str(self.report_path))
        rp_label.pack()

        def change_folder():
            new = filedialog.askdirectory()
            if not new:
                return
            # Guardamos como absoluta y la mostramos
            self.report_path = Path(new)
            self.report_path_absolute = True
            rp_label.config(text=str(self.report_path))
            self.save_config()

        def reset_default():
            self.report_path_absolute = False
            self.report_path = Path(get_base_path() / "reporte")
            rp_label.config(text=str(self.report_path))
            self.save_config()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Cambiar carpeta…", command=change_folder).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="Restablecer a carpeta por defecto", command=reset_default).grid(row=0, column=1, padx=6)
        ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=(6,10))

    # -------------------------
    # Temas: claro / oscuro
    # -------------------------
    def apply_dark_theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        bg = "#1e1e1e"
        fg = "#ffffff"
        widget_bg = "#2b2b2b"
        self.root.configure(bg=bg)
        style.configure(".", background=bg, foreground=fg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=widget_bg, foreground=fg)
        style.configure("TEntry", fieldbackground=widget_bg, foreground=fg)
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
        style.configure("TButton", background="#e6e6e6", foreground=fg)
        style.configure("TEntry", fieldbackground="#ffffff", foreground=fg)
        self.log.configure(bg="white", fg="black", insertbackground="black")
        self.dark_mode.set(False)

    def toggle_dark_mode(self):
        if self.dark_mode.get():
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
        self.save_config()

# main.py  - Parte 2/3
# Cola UI-safe helpers, contar archivos y control UI (disable/enable)

    # -------------------------
    # Utilidades UI-safe (hilos)
    # -------------------------
    def safe_log(self, msg):
        """Encolar mensaje para ser mostrado en el thread principal"""
        self.ui_queue.put(("log", msg))

    def safe_progress(self, current, total):
        """Encolar progreso (current, total)"""
        self.ui_queue.put(("progress", (current, total)))

    def process_ui_queue(self):
        """Procesa la cola y actualiza UI (run en mainloop)"""
        try:
            while True:
                kind, payload = self.ui_queue.get_nowait()
                if kind == "log":
                    self.log.insert(tk.END, payload + "\n")
                    self.log.see(tk.END)
                elif kind == "progress":
                    current, total = payload
                    pct = int((current / total) * 100) if total > 0 else 0
                    self.progress["value"] = pct
                    self.progress_label.config(text=f"Progreso: {pct}%")
                elif kind == "restore_ui":
                    # Reactivar widgets (habilitar)
                    self._set_ui_enabled(True)
                    self.progress_label.config(text="Progreso: 0%")
                    self.progress["value"] = 0
                elif kind == "open_reports":
                    # Abrir carpeta de reportes
                    self._open_folder_impl(payload)
        except queue.Empty:
            pass
        self.root.after(100, self.process_ui_queue)

    def _set_ui_enabled(self, enabled: bool):
        """Habilita o deshabilita widgets principales para evitar interacción mientras corre"""
        state = "normal" if enabled else "disabled"
        # iterar sobre children del main frame (index 0)
        for widget in self.root.winfo_children():
            try:
                widget.configure(state=state)
            except Exception:
                # algunos contenedores no tienen state, lo ignoramos
                pass
        # Además forzar que barra de menú siga activa (no se puede desactivar facilmente)
        # No hacemos nada con el menu para evitar bloquear acceso a configuración.

    # -------------------------
    # Conteo de archivos (para barra real)
    # -------------------------
    def count_files(self, source_path: Path, mode: str) -> int:
        """
        Cuenta archivos que se van a copiar según el modo:
        - 'respaldo': copia toda la estructura de cada monumento, omitiendo 'PROYECTO AGISOFT'
        - 'informes': copia toda la estructura de cada monumento, omitiendo 'PRODUCTOS GENERADOS' y 'PROYECTO AGISOFT'
        """
        source = Path(source_path)
        if not source.exists():
            return 0

        pattern = re.compile(r"^[T][1-7]_\d{5}", re.IGNORECASE)
        exclude_folders = {"PROYECTO AGISOFT"} if mode == "respaldo" else {"PROYECTO AGISOFT", "PRODUCTOS GENERADOS"}

        total = 0
        monuments = [d for d in source.iterdir() if d.is_dir() and pattern.match(d.name)]
        for monument in monuments:
            for root, dirs, files in os.walk(monument):
                current = Path(root)
                if any(p.upper() in exclude_folders for p in current.parts):
                    continue
                total += len(files)
        return total

    # -------------------------
    # Analizar carpeta (muestra en log)
    # -------------------------
    def analyze_folder(self):
        self.clear_log()
        src = self.source_var.get()
        if not src:
            self.safe_log("⚠️ Selecciona una carpeta origen antes de analizar.")
            return
        try:
            source = Path(src)
            pattern = re.compile(r"^[T][1-7]_\d{5}", re.IGNORECASE)
            monuments = [d.name for d in source.iterdir() if d.is_dir() and pattern.match(d.name)]
            self.safe_log(f"📂 Monumentos detectados: {len(monuments)}")
            for m in monuments:
                self.safe_log(f" - {m}")
            # además mostrar conteo estimado de archivos (según modo)
            total_files = self.count_files(source, self.mode_var.get())
            self.safe_log(f"📊 Archivos aproximados a copiar: {total_files}")
        except Exception as e:
            self.safe_log(f"❌ Error analizando carpeta: {e}")

    # -------------------------
    # Run -> inicia hilo de trabajo
    # -------------------------
    def run(self):
        # bloquear UI
        self._set_ui_enabled(False)
        # preparar barra en 0
        self.progress.config(mode="determinate", value=0)
        self.progress_label.config(text="Calculando archivos...")
        # iniciar hilo
        t = threading.Thread(target=self._run_thread, daemon=True)
        t.start()

    def _run_thread(self):
        try:
            self.not_copied = []
            src = self.source_var.get()
            dst = self.dest_var.get()
            mode = self.mode_var.get()

            if not src or not dst:
                self.safe_log("⚠️ Selecciona carpeta origen y destino.")
                return

            src_path = Path(src)
            dst_path = Path(dst)
            if not src_path.exists() or not dst_path.exists():
                self.safe_log("⚠️ Las rutas seleccionadas no existen.")
                return

            # 1) Contar archivos totales para barra real
            total_files = self.count_files(src_path, mode)
            if total_files == 0:
                self.safe_log("⚠️ No se encontraron archivos para copiar.")
                return

            # 2) Ejecutar proceso según modo, actualizando progreso por cada archivo copiado
            files_processed = 0

            if mode == "respaldo":
                # recorrer monumentos y copiar
                pattern = re.compile(r"^[T][1-7]_\d{5}", re.IGNORECASE)
                exclude = {"PROYECTO AGISOFT","FOTOS DE PROCESAMIENTO","FOTOS DE REGISTRO","FOTOS PROCESAMIENTO", "FOTOS REGISTRO", "PUNTOS DE CONTROL"}
                monuments = [d for d in src_path.iterdir() if d.is_dir() and pattern.match(d.name)]
                for monument in monuments:
                    self.safe_log(f"📦 Respaldando: {monument.name}")
                    for root, dirs, files in os.walk(monument):
                        current = Path(root)
                        if any(p.upper() in exclude for p in current.parts):
                            continue
                        rel = current.relative_to(monument)
                        target_dir = dst_path / monument.name / rel
                        target_dir.mkdir(parents=True, exist_ok=True)
                        for f in files:
                            src_file = current / f
                            dst_file = target_dir / f
                            try:
                                # Modo A: sobrescribir automáticamente
                                shutil.copy2(src_file, dst_file)
                            except Exception as e:
                                self.not_copied.append((str(src_file), str(dst_file), str(e), datetime.now()))
                                self.safe_log(f"❌ Error copiando {src_file}: {e}")
                            files_processed += 1
                            self.safe_progress(files_processed, total_files)

            else:  # informes
                pattern = re.compile(r"^[T][1-7]_\d{5}", re.IGNORECASE)
                exclude = {"PRODUCTOS GENERADOS", "PROYECTO AGISOFT"}
                monuments = [d for d in src_path.iterdir() if d.is_dir() and pattern.match(d.name)]
                for monument in monuments:
                    self.safe_log(f"📄 Copiando estructura: {monument.name}")
                    for root, dirs, files in os.walk(monument):
                        current = Path(root)
                        if any(p.upper() in exclude for p in current.parts):
                            continue
                        rel = current.relative_to(monument)
                        target_dir = dst_path / monument.name / rel
                        target_dir.mkdir(parents=True, exist_ok=True)
                        for f in files:
                            src_file = current / f
                            dst_file = target_dir / f
                            try:
                                shutil.copy2(src_file, dst_file)
                            except Exception as e:
                                self.not_copied.append((str(src_file), str(dst_file), str(e), datetime.now()))
                                self.safe_log(f"❌ Error copiando {src_file}: {e}")
                            files_processed += 1
                            self.safe_progress(files_processed, total_files)

            # 3) Generar reporte si aplica
            if self.generate_report.get() and self.not_copied:
                self.generate_excel_report()

            self.safe_log("✅ Proceso finalizado.")
            # Abrir carpeta de reportes en UI thread
            self.ui_queue.put(("open_reports", str(self.report_path)))

        except Exception as e:
            self.safe_log(f"❌ Error inesperado: {e}")
        finally:
            # restaurar UI (en cola para que corra en main thread)
            self.ui_queue.put(("restore_ui", None))

# main.py  - Parte 3/3
# Reporte Excel, abrir carpeta y launch

    # -------------------------
    # Generar reporte Excel y abrir carpeta
    # -------------------------
    def generate_excel_report(self):
        """
        Guarda el reporte en la carpeta configurada (relativa o absoluta).
        Si la carpeta no existe, la crea.
        Luego intenta abrir la carpeta para que el usuario vea el archivo.
        """
        try:
            # Determinar carpeta de reportes final
            if self.report_path_absolute:
                rp = Path(self.report_path)
            else:
                rp = Path(get_base_path()) / (Path(self.report_path).name if Path(self.report_path).name != "" else "reporte")
            rp.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            report_file = rp / f"reporte_no_copiados_{timestamp}.xlsx"
            df = pd.DataFrame(self.not_copied, columns=["Origen", "Destino", "Motivo/Error", "Fecha"])
            df.to_excel(report_file, index=False)
            self.safe_log(f"📊 Reporte guardado en: {report_file}")

            # Intentar abrir carpeta de reportes (en thread UI)
            self.ui_queue.put(("open_reports", str(rp)))
        except Exception as e:
            self.safe_log(f"❌ Error generando reporte: {e}")

    # -------------------------
    # Abrir carpeta (implementacion portable)
    # -------------------------
    def open_report_folder(self):
        # Abre la carpeta configurada de reportes
        if self.report_path_absolute:
            path = str(self.report_path)
        else:
            path = str(Path(get_base_path()) / (Path(self.report_path).name if Path(self.report_path).name != "" else "reporte"))
        self._open_folder_impl(path)

    def _open_folder_impl(self, path_str):
        try:
            p = Path(path_str)
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)
            if platform.system() == "Windows":
                os.startfile(str(p))
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", str(p)])
            else:
                subprocess.Popen(["xdg-open", str(p)])
        except Exception as e:
            self.safe_log(f"⚠️ No se pudo abrir la carpeta: {e}")

    # -------------------------
    # Otros helpers
    # -------------------------
    def clear_log(self):
        self.log.delete("1.0", tk.END)
    
    def choose_source(self):
        p = filedialog.askdirectory()
        if p:
            self.source_var.set(p)

    def choose_dest(self):
        p = filedialog.askdirectory()
        if p:
            self.dest_var.set(p)

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
