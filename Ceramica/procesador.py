import os
import re
import shutil
import unicodedata
from dataclasses import dataclass
from typing import List, Callable, Optional

IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".tif", ".tiff",
    ".bmp", ".gif", ".heic", ".nef", ".raw", ".webp"
}

# Diccionario de equivalencias aceptadas
NORMALIZAR_CATEGORIAS = {
    "completa": "COMPLETAS",
    "completas": "COMPLETAS",
    "completo": "COMPLETAS",

    "miscelanea": "MISCELANEOS",
    "miscelaneas": "MISCELANEOS",
    "miscelaneo": "MISCELANEOS",
    "miscelaneos": "MISCELANEOS",

    "no completa": "NO COMPLETAS",
    "nocompleta": "NO COMPLETAS",
    "no completas": "NO COMPLETAS",
    "nocompletas": "NO COMPLETAS",
}

FILENAME_PATTERN = re.compile(
    r"^(T[1-7]_\d{5})_([A-Za-z0-9]{3}_\d{7}.*)$"
)


@dataclass
class LaminaInfo:
    monument_id: str
    category: str
    src_path: str
    filename: str


# ------------------------------------------------------------
# FUNCIÓN PARA NORMALIZAR STRINGS (acentos, símbolos, etc.)
# ------------------------------------------------------------
def limpiar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = texto.replace("_", "").replace("-", "").replace(" ", "")
    return texto


def normalizar_categoria(nombre: str) -> str:
    limpio = limpiar_texto(nombre)

    # Buscar coincidencia exacta en equivalencias
    if limpio in NORMALIZAR_CATEGORIAS:
        return NORMALIZAR_CATEGORIAS[limpio]

    # Intento extra: detectar “no completa” partidas en dos
    if "nocomplet" in limpio:
        return "NO COMPLETAS"

    return "SIN_CATEGORIA"


# ============================================================
#                   PROCESADOR PRINCIPAL
# ============================================================
class ProcesadorLaminasFS:
    def __init__(self, source_root: str, dest_root: str, log_fn: Optional[Callable[[str], None]] = None):
        self.source_root = source_root
        self.dest_root = dest_root
        self.log = log_fn or (lambda msg: None)
        self.laminas: List[LaminaInfo] = []
        self.errors: List[str] = []

    def analizar(self) -> List[LaminaInfo]:
        self.log("Iniciando análisis...\n")
        self.laminas.clear()
        self.errors.clear()

        for root, dirs, files in os.walk(self.source_root):
            if os.path.basename(root).upper() == "LAMINA FINAL":

                id_folder = os.path.basename(os.path.dirname(root))
                categoria_raw = os.path.basename(os.path.dirname(os.path.dirname(root)))

                categoria = normalizar_categoria(categoria_raw)

                self.log(f"[CAT] {categoria_raw} → {categoria}")

                for filename in files:
                    _, ext = os.path.splitext(filename)
                    ext = ext.lower()

                    if ext not in IMAGE_EXTS:
                        continue

                    stem, _ = os.path.splitext(filename)
                    match = FILENAME_PATTERN.match(stem)

                    if not match:
                        self.log(f"[Nombre inválido] {filename}")
                        continue

                    monument_id = match.group(1)
                    src_path = os.path.join(root, filename)

                    self.laminas.append(
                        LaminaInfo(
                            monument_id=monument_id,
                            category=categoria,
                            src_path=src_path,
                            filename=filename
                        )
                    )

                    self.log(f"[OK] {filename} → {monument_id}/{categoria}")

        self.log(f"\nTotal detectadas: {len(self.laminas)}")
        return self.laminas

    # ------------------------------------------------------------
    #                        COPIAR
    # ------------------------------------------------------------
    def copiar(self):
        if not self.laminas:
            self.analizar()

        total = len(self.laminas)
        self.log(f"\n--- INICIO COPIA ({total} imágenes) ---\n")

        copiadas = 0

        for idx, lam in enumerate(self.laminas, start=1):

            dest_folder = os.path.join(
                self.dest_root,
                lam.monument_id,
                lam.category
            )

            os.makedirs(dest_folder, exist_ok=True)

            dest_path = os.path.join(dest_folder, lam.filename)

            try:
                shutil.copy2(lam.src_path, dest_path)
                copiadas += 1
                self.log(f"[{idx}/{total}] {lam.filename} → {dest_folder}")
            except Exception as e:
                msg = f"[ERROR] {lam.src_path} → {dest_path} | {e}"
                self.errors.append(msg)
                self.log(msg)

        self.log("\n--- RESUMEN ---")
        self.log(f"Copiadas: {copiadas}/{total}")
        self.log(f"Errores: {len(self.errors)}")
        self.log("--- FIN ---\n")
