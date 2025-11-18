import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import os
import webbrowser
from procesador import ejecutar_proceso, recolectar_imagenes


# ============================
# CONFIGURACIÓN DEL TEMA OSCURO
# ============================
BG = "#424242"       # Fondo oscuro VSCode
FG = "#d4d4d4"       # Texto gris claro
BTN_BG = "#3c3c3c"   # Fondo botones
BTN_FG = "white"
ACCENT = "#5874ee"   # Azul VSCode
CONSOLE_BG = "#3A3A3A"
CONSOLE_FG = "#5874ee"


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # -----------------------------
        # CONFIGURACIÓN DE VENTANA
        # -----------------------------
        self.title("Reencarpetado de Imágenes por ID de monumento")
        self.geometry("900x650")
        self.configure(bg=BG)
        self.resizable(False, False)

        # Centrar ventana
        self.update_idletasks()
        width = 900
        height = 650
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Variables
        self.folder_origen = ""
        self.folder_destino = ""
        self.path_reporte = ""
        self.path_excel = ""

        # =====================================
        # TITULO
        # =====================================
        titulo = tk.Label(
            self,
            text="Reencarpetado de Imágenes por ID de monumento",
            font=("Arial", 22, "bold"),
            bg=BG,
            fg=FG
        )
        titulo.pack(pady=15)

        # =====================================
        # FRAME PRINCIPAL
        # =====================================
        frame = tk.Frame(self, bg=BG)
        frame.pack(pady=5)

        # ---- ORIGEN ----
        self.lbl_origen = tk.Label(frame, text="Carpeta origen: (no seleccionada)", bg=BG, fg=FG)
        self.lbl_origen.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        tk.Button(frame, text="Seleccionar carpeta origen",
                  command=self.seleccionar_origen,
                  bg=BTN_BG, fg=BTN_FG, width=25).grid(row=0, column=1, padx=10, pady=5)

        # ---- DESTINO ----
        self.lbl_destino = tk.Label(frame, text="Carpeta destino: (no seleccionada)", bg=BG, fg=FG)
        self.lbl_destino.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        tk.Button(frame, text="Seleccionar carpeta destino",
                  command=self.seleccionar_destino,
                  bg=BTN_BG, fg=BTN_FG, width=25).grid(row=1, column=1, padx=10, pady=5)

        # ---- VISTA PREVIA ----
        tk.Button(frame, text="Vista previa",
                  command=self.vista_previa,
                  bg=ACCENT, fg="white", width=25).grid(row=2, column=0, columnspan=2, pady=10)

        # ---- EJECUTAR ----
        tk.Button(frame, text="Ejecutar procesamiento",
                  command=self.ejecutar,
                  bg="#5874ee", fg="white", width=32).grid(row=3, column=0, columnspan=2, pady=10)

        # =====================================
        # BARRA DE PROGRESO
        # =====================================
        self.progress = ttk.Progressbar(self, length=700, mode="indeterminate")
        self.progress.pack(pady=10)

        # =====================================
        # CONSOLA
        # =====================================
        self.consola = scrolledtext.ScrolledText(
            self, width=110, height=18,
            bg=CONSOLE_BG, fg=CONSOLE_FG,
            insertbackground="white",
            font=("Consolas", 10)
        )
        self.consola.pack(padx=20, pady=10)

        # =====================================
        # BOTONES: abrir carpeta / abrir excel
        # =====================================
        frame2 = tk.Frame(self, bg=BG)
        frame2.pack(pady=5)

        tk.Button(frame2, text="Abrir carpeta del reporte",
                  command=self.abrir_carpeta_reporte,
                  bg=BTN_BG, fg=BTN_FG, width=25).grid(row=0, column=0, padx=10)

        tk.Button(frame2, text="Abrir Excel generado",
                  command=self.abrir_excel,
                  bg=BTN_BG, fg=BTN_FG, width=25).grid(row=0, column=1, padx=10)

    # =============================================
    # SELECCIÓN DE CARPETAS
    # =============================================
    def seleccionar_origen(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.folder_origen = ruta
            self.lbl_origen.configure(text=f"Carpeta origen: {ruta}")

    def seleccionar_destino(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.folder_destino = ruta
            self.lbl_destino.configure(text=f"Carpeta destino: {ruta}")

    # =============================================
    # VISTA PREVIA
    # =============================================
    def vista_previa(self):
        if not self.folder_origen:
            messagebox.showerror("Error", "Selecciona la carpeta origen.")
            return

        imágenes = recolectar_imagenes(self.folder_origen)
        self.log(f"Vista previa: {len(imágenes)} imágenes encontradas.")

    # =============================================
    # EJECUCIÓN PRINCIPAL
    # =============================================
    def ejecutar(self):
        if not self.folder_origen or not self.folder_destino:
            messagebox.showerror("Error", "Debes seleccionar ambas carpetas.")
            return

        self.log("Procesando imágenes...")
        self.progress.start(10)  # velocidad animada

        # Llamar al proceso real
        csv_path, excel_path = ejecutar_proceso(
            self.folder_origen,
            self.folder_destino,
            callback=self.log
        )

        self.progress.stop()

        self.path_reporte = os.path.dirname(csv_path)
        self.path_excel = excel_path

        self.log("\n✔ PROCESO COMPLETO ✔")
        self.log(f"CSV creado en: {csv_path}")
        self.log(f"Excel creado en: {excel_path}")

        messagebox.showinfo("Finalizado", "El procesamiento ha terminado correctamente.")

    # =============================================
    # FUNCIONES PARA ABRIR ARCHIVOS
    # =============================================
    def abrir_carpeta_reporte(self):
        if self.path_reporte:
            os.startfile(self.path_reporte)
        else:
            messagebox.showerror("Error", "Aún no se ha generado ningún reporte.")

    def abrir_excel(self):
        if self.path_excel and os.path.exists(self.path_excel):
            os.startfile(self.path_excel)
        else:
            messagebox.showerror("Error", "Aún no se ha generado un archivo Excel.")

    # =============================================
    # LOG EN CONSOLA
    # =============================================
    def log(self, texto):
        self.consola.insert("end", texto + "\n")
        self.consola.see("end")


if __name__ == "__main__":
    app = App()
    app.mainloop()
