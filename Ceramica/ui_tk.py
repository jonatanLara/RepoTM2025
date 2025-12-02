import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from procesador import ProcesadorLaminasFS


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Reencarpetado de Láminas Finales")
        self.geometry("900x600")

        self.source_dir = ""
        self.dest_dir = ""
        self.procesador: ProcesadorLaminasFS | None = None
        self.total_imagenes = 0

        self.var_detectadas = tk.StringVar(value="Imágenes detectadas: 0")
        self.var_ids = tk.StringVar(value="IDs de monumento detectados: 0")

        self._construir_ui()

    # -------------------------------------------------
    #                 CONSTRUCCIÓN UI
    # -------------------------------------------------
    def _construir_ui(self):
        frame_paths = ttk.LabelFrame(self, text="Rutas")
        frame_paths.pack(fill="x", padx=10, pady=10)

        # ORIGEN
        ttk.Label(frame_paths, text="Carpeta origen:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_origen = ttk.Entry(frame_paths)
        self.entry_origen.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(frame_paths, text="Seleccionar...", command=self.seleccionar_origen).grid(row=0, column=2, padx=5, pady=5)

        # DESTINO
        ttk.Label(frame_paths, text="Carpeta destino:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_destino = ttk.Entry(frame_paths)
        self.entry_destino.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(frame_paths, text="Seleccionar...", command=self.seleccionar_destino).grid(row=1, column=2, padx=5, pady=5)

        frame_paths.columnconfigure(1, weight=1)

        # CONTROLES
        frame_ctrl = ttk.LabelFrame(self, text="Control")
        frame_ctrl.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Button(frame_ctrl, text="Analizar carpeta", command=self.analizar_carpeta).grid(row=0, column=0, padx=5, pady=5)

        self.btn_procesar = ttk.Button(frame_ctrl, text="Procesar y copiar", command=self.procesar_copia, state="disabled")
        self.btn_procesar.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_ctrl, textvariable=self.var_detectadas).grid(row=1, column=0, sticky="w", padx=5)
        ttk.Label(frame_ctrl, textvariable=self.var_ids).grid(row=1, column=1, sticky="w", padx=5)

        # BARRA DE PROGRESO
        self.progress = ttk.Progressbar(frame_ctrl, mode="indeterminate")
        self.progress.grid(row=2, column=0, columnspan=3, sticky="we", padx=5, pady=5)

        # CONSOLA
        frame_console = ttk.LabelFrame(self, text="Consola")
        frame_console.pack(fill="both", expand=True, padx=10, pady=10)

        self.text_console = tk.Text(frame_console, wrap="word", state="disabled")
        self.text_console.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(frame_console, orient="vertical", command=self.text_console.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_console.config(yscrollcommand=scrollbar.set)

    # -------------------------------------------------
    #                SELECCIÓN DE RUTAS
    # -------------------------------------------------
    def seleccionar_origen(self):
        carpeta = filedialog.askdirectory(title="Selecciona carpeta origen")
        if carpeta:
            self.entry_origen.delete(0, tk.END)
            self.entry_origen.insert(0, carpeta)
            self.source_dir = carpeta

    def seleccionar_destino(self):
        carpeta = filedialog.askdirectory(title="Selecciona carpeta destino")
        if carpeta:
            self.entry_destino.delete(0, tk.END)
            self.entry_destino.insert(0, carpeta)
            self.dest_dir = carpeta

    # -------------------------------------------------
    #                  LOG A CONSOLA
    # -------------------------------------------------
    def log(self, mensaje: str):
        def append():
            self.text_console.config(state="normal")
            self.text_console.insert(tk.END, mensaje + "\n")
            self.text_console.see(tk.END)
            self.text_console.config(state="disabled")

        self.text_console.after(0, append)

    # -------------------------------------------------
    #           VALIDAR RUTAS DE LA UI
    # -------------------------------------------------
    def _validar_rutas(self) -> bool:
        self.source_dir = self.entry_origen.get().strip()
        self.dest_dir = self.entry_destino.get().strip()

        if not self.source_dir or not os.path.isdir(self.source_dir):
            messagebox.showerror("Error", "Selecciona una carpeta origen válida.")
            return False

        if not self.dest_dir or not os.path.isdir(self.dest_dir):
            messagebox.showerror("Error", "Selecciona una carpeta destino válida.")
            return False

        return True

    # -------------------------------------------------
    #                ANÁLISIS DE CARPETA
    # -------------------------------------------------
    def analizar_carpeta(self):
        if not self._validar_rutas():
            return

        self.procesador = ProcesadorLaminasFS(
            source_root=self.source_dir,
            dest_root=self.dest_dir,
            log_fn=self.log
        )

        self.log("==============================================")
        self.log("INICIANDO ANÁLISIS")
        self.log("==============================================")

        try:
            laminas = self.procesador.analizar()
        except Exception as e:
            self.log(f"[ERROR] {e}")
            messagebox.showerror("Error", str(e))
            return

        total = len(laminas)
        ids_unicos = {l.monument_id for l in laminas}

        self.var_detectadas.set(f"Imágenes detectadas: {total}")
        self.var_ids.set(f"IDs de monumento detectados: {len(ids_unicos)}")

        self.log(f"\nSe detectarán {total} imágenes antes de procesar.")

        if total > 0:
            self.btn_procesar.config(state="normal")
        else:
            self.btn_procesar.config(state="disabled")

    # -------------------------------------------------
    #                  COPIAR ARCHIVOS
    # -------------------------------------------------
    def procesar_copia(self):
        if not self.procesador:
            messagebox.showwarning("Advertencia", "Primero analiza la carpeta.")
            return

        self.btn_procesar.config(state="disabled")
        self.progress.start(10)

        self.log("\n==============================================")
        self.log("INICIO DEL PROCESO DE COPIA")
        self.log("==============================================")

        def tarea():
            try:
                self.procesador.copiar()
                self.after(0, self._fin_copia_ok)
            except Exception as e:
                self.after(0, self._fin_copia_error, e)

        threading.Thread(target=tarea, daemon=True).start()

    def _fin_copia_ok(self):
        self.progress.stop()
        self.btn_procesar.config(state="normal")
        self.log("Proceso completado correctamente.")
        messagebox.showinfo("Finalizado", "Proceso de copia terminado.")

    def _fin_copia_error(self, error):
        self.progress.stop()
        self.btn_procesar.config(state="normal")
        self.log(f"[ERROR] {error}")
        messagebox.showerror("Error durante la copia", str(error))


if __name__ == "__main__":
    app = App()
    app.mainloop()
