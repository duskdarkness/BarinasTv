import os
import shutil
import random
import threading
import re
import unicodedata
from datetime import date, timedelta, datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# ================= RUTAS PRINCIPALES =================
RUTA_NO_CATEGORIZADO = r"D:\Respaldo Insert\respaldo disco programas\PROGRAMACION\peliculas\No CATEGORIZADO"
RUTA_POR_ANO = r"D:\Respaldo Insert\respaldo disco programas\PROGRAMACION\peliculas\No CATEGORIZADO\Por Año"
RUTA_REPORTE_TXT = os.path.join(RUTA_POR_ANO, "Registro_Programacion.txt")

EXTENSIONES_VIDEO = ('.mp4', '.mkv', '.avi', '.mov', '.mpg', '.wmv', '.m4v')

# Patrón para omitir carpetas de fechas ya trabajadas (ej: "2026-10-28", "05-30")
PATRON_FECHA_TRABAJADA = re.compile(r"^(\d{4}-\d{2}-\d{2}|\d{2}-\d{2})$")
PATRON_DIA_ORDEN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def normalizar_texto(texto):
    """Elimina tildes y pasa a minúsculas para comparar texto de forma segura."""
    return unicodedata.normalize('NFKD', texto.lower()).encode('ASCII', 'ignore').decode('utf-8')

class GestorPeliculasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor y Programador de Películas")
        self.root.geometry("700x680")
        self.root.minsize(650, 600)

        # Variables internas
        self.diccionario_peliculas = {"animada": [], "no animada": [], "navideña": []}
        self.tipo_seleccionado = tk.StringVar(value="animada")
        self.opcion_fecha = tk.StringVar(value="Hoy")
        self.fecha_final = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.cantidad_mover = tk.IntVar(value=1)

        self._crear_interfaz()
        self.iniciar_escaneo()

    def _crear_interfaz(self):
        style = ttk.Style()
        style.theme_use("clam")

        # --- SECCIÓN 1: Inventario Disponible ---
        frame_inventario = ttk.LabelFrame(self.root, text=" 📁 Inventario Disponible ", padding=10)
        frame_inventario.pack(fill="x", padx=12, pady=6)

        self.lbl_animadas = ttk.Label(frame_inventario, text="Animadas: 0", font=("Segoe UI", 9, "bold"))
        self.lbl_animadas.grid(row=0, column=0, padx=15, sticky="w")

        self.lbl_no_animadas = ttk.Label(frame_inventario, text="No Animadas: 0", font=("Segoe UI", 9, "bold"))
        self.lbl_no_animadas.grid(row=0, column=1, padx=15, sticky="w")

        self.lbl_navidenas = ttk.Label(frame_inventario, text="Navideñas: 0", font=("Segoe UI", 9, "bold"))
        self.lbl_navidenas.grid(row=0, column=2, padx=15, sticky="w")

        btn_rescan = ttk.Button(frame_inventario, text="↻ Re-escanear", command=self.iniciar_escaneo)
        btn_rescan.grid(row=0, column=3, padx=10, sticky="e")

        # --- SECCIÓN 2: Categoría y Cantidad ---
        frame_opciones = ttk.LabelFrame(self.root, text=" 🎬 Categoría y Cantidad a Mover ", padding=10)
        frame_opciones.pack(fill="x", padx=12, pady=6)

        ttk.Label(frame_opciones, text="Tipo:").grid(row=0, column=0, sticky="w", pady=4)
        cbo_tipo = ttk.Combobox(
            frame_opciones, 
            textvariable=self.tipo_seleccionado, 
            values=["animada", "no animada", "navideña"], 
            state="readonly", 
            width=16
        )
        cbo_tipo.grid(row=0, column=1, sticky="w", padx=8, pady=4)
        cbo_tipo.bind("<<ComboboxSelected>>", self._actualizar_limite_cantidad)

        ttk.Label(frame_opciones, text="Cantidad:").grid(row=0, column=2, sticky="w", padx=(20, 0), pady=4)
        self.spn_cantidad = ttk.Spinbox(frame_opciones, from_=1, to=999, textvariable=self.cantidad_mover, width=8)
        self.spn_cantidad.grid(row=0, column=3, sticky="w", padx=8, pady=4)

        # --- SECCIÓN 3: Programación de Fecha ---
        frame_fecha = ttk.LabelFrame(self.root, text=" 📅 Programar Fecha Destino ", padding=10)
        frame_fecha.pack(fill="x", padx=12, pady=6)

        opciones_dias = [
            ("Hoy", "Hoy"),
            ("Mañana", "Mañana"),
            ("Pasado mañana (+2d)", "Pasado"),
            ("En 1 semana (+7d)", "Semana"),
            ("Personalizada", "Manual")
        ]

        f_radios = ttk.Frame(frame_fecha)
        f_radios.pack(anchor="w", pady=2)

        for texto, valor in opciones_dias:
            r = ttk.Radiobutton(
                f_radios, 
                text=texto, 
                value=valor, 
                variable=self.opcion_fecha, 
                command=self._actualizar_campo_fecha
            )
            r.pack(side="left", padx=5)

        f_custom = ttk.Frame(frame_fecha)
        f_custom.pack(anchor="w", pady=6)
        ttk.Label(f_custom, text="Carpeta de fecha (AAAA-MM-DD):").pack(side="left")
        self.ent_fecha = ttk.Entry(f_custom, textvariable=self.fecha_final, width=14, state="disabled")
        self.ent_fecha.pack(side="left", padx=8)

        # --- SECCIÓN 4: Botones de Acción ---
        f_botones = ttk.Frame(self.root)
        f_botones.pack(fill="x", padx=12, pady=6)

        self.btn_mover = ttk.Button(f_botones, text="🚀 Mover Películas Seleccionadas", command=self.iniciar_traslado)
        self.btn_mover.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_txt = ttk.Button(f_botones, text="📄 Abrir Reporte TXT", command=self.abrir_reporte_txt)
        self.btn_txt.pack(side="right", padx=(6, 0))

        # --- SECCIÓN 5: Consola / Logs ---
        frame_log = ttk.LabelFrame(self.root, text=" 📋 Registro de Actividad ", padding=8)
        frame_log.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.txt_log = scrolledtext.ScrolledText(frame_log, height=10, state="disabled", font=("Consolas", 9))
        self.txt_log.pack(fill="both", expand=True)

    def log(self, mensaje):
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, mensaje + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    def _actualizar_campo_fecha(self):
        opcion = self.opcion_fecha.get()
        hoy = date.today()

        if opcion == "Hoy":
            self.fecha_final.set(hoy.strftime("%Y-%m-%d"))
            self.ent_fecha.config(state="disabled")
        elif opcion == "Mañana":
            self.fecha_final.set((hoy + timedelta(days=1)).strftime("%Y-%m-%d"))
            self.ent_fecha.config(state="disabled")
        elif opcion == "Pasado":
            self.fecha_final.set((hoy + timedelta(days=2)).strftime("%Y-%m-%d"))
            self.ent_fecha.config(state="disabled")
        elif opcion == "Semana":
            self.fecha_final.set((hoy + timedelta(days=7)).strftime("%Y-%m-%d"))
            self.ent_fecha.config(state="disabled")
        elif opcion == "Manual":
            self.ent_fecha.config(state="normal")
            self.ent_fecha.focus_set()

    def _actualizar_limite_cantidad(self, event=None):
        cat = self.tipo_seleccionado.get()
        max_disponible = len(self.diccionario_peliculas.get(cat, []))
        if max_disponible > 0:
            self.spn_cantidad.config(to=max_disponible)
            if self.cantidad_mover.get() > max_disponible:
                self.cantidad_mover.set(max_disponible)
        else:
            self.spn_cantidad.config(to=1)
            self.cantidad_mover.set(1)

    def iniciar_escaneo(self):
        threading.Thread(target=self._escanear_archivos, daemon=True).start()

    def _escanear_archivos(self):
        self.log("🔍 Escaneando catálogo de audiovisuales...")

        if not os.path.exists(RUTA_NO_CATEGORIZADO):
            self.log(f"❌ Error: No existe la ruta principal: {RUTA_NO_CATEGORIZADO}")
            return

        animadas = []
        no_animadas = []
        navidenas = []

        for raiz, directorios, archivos in os.walk(RUTA_NO_CATEGORIZADO):
            # Omitir días ya trabajados
            directorios[:] = [d for d in directorios if not PATRON_FECHA_TRABAJADA.match(d)]

            for archivo in archivos:
                if archivo.lower().endswith(EXTENSIONES_VIDEO):
                    ruta_completa = os.path.join(raiz, archivo)

                    # MEJORA CLAVE: Evaluamos tanto la carpeta como el nombre del archivo
                    texto_a_evaluar = normalizar_texto(f"{raiz} {archivo}")

                    # 1. Prioridad: Navideña (en carpeta o en el título)
                    if any(k in texto_a_evaluar for k in ["navidad", "naviden", "christmas"]):
                        navidenas.append(ruta_completa)
                    # 2. No Animada
                    elif any(k in texto_a_evaluar for k in ["no animad", "no_animad", "noanimad"]):
                        no_animadas.append(ruta_completa)
                    # 3. Animada
                    elif any(k in texto_a_evaluar for k in ["animad", "anime", "cartoon"]):
                        animadas.append(ruta_completa)
                    # 4. Resto por defecto a No Animada
                    else:
                        no_animadas.append(ruta_completa)

        self.diccionario_peliculas = {
            "animada": animadas,
            "no animada": no_animadas,
            "navideña": navidenas
        }

        self.root.after(0, self._actualizar_contadores_ui)

    def _actualizar_contadores_ui(self):
        self.lbl_animadas.config(text=f"Animadas: {len(self.diccionario_peliculas['animada'])}")
        self.lbl_no_animadas.config(text=f"No Animadas: {len(self.diccionario_peliculas['no animada'])}")
        self.lbl_navidenas.config(text=f"Navideñas: {len(self.diccionario_peliculas['navideña'])}")
        self._actualizar_limite_cantidad()
        total = sum(len(v) for v in self.diccionario_peliculas.values())
        self.log(f"✔ Escaneo completo: {total} películas listas para programar.")

    def generar_reporte_txt(self):
        if not os.path.exists(RUTA_POR_ANO):
            return

        dias_encontrados = []
        for entrada in os.listdir(RUTA_POR_ANO):
            ruta_entrada = os.path.join(RUTA_POR_ANO, entrada)
            if os.path.isdir(ruta_entrada) and PATRON_DIA_ORDEN.match(entrada):
                dias_encontrados.append(entrada)

        dias_encontrados.sort()

        if not dias_encontrados:
            return

        lineas = []
        lineas.append("================================================================================")
        lineas.append("           HISTORIAL DE PELÍCULAS PROGRAMADAS POR DÍA                          ")
        lineas.append(f"           Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lineas.append("================================================================================\n")

        for dia in dias_encontrados:
            ruta_dia = os.path.join(RUTA_POR_ANO, dia)
            lineas.append(f"--------------------------------------------------------------------------------")
            lineas.append(f"📅 DÍA: {dia}")
            lineas.append(f"--------------------------------------------------------------------------------")

            categorias = ["animada", "no animada", "navideña"]
            tiene_peliculas = False

            for cat in categorias:
                ruta_cat = os.path.join(ruta_dia, cat)
                archivos_cat = []

                if os.path.exists(ruta_cat) and os.path.isdir(ruta_cat):
                    for arch in os.listdir(ruta_cat):
                        if arch.lower().endswith(EXTENSIONES_VIDEO):
                            archivos_cat.append(arch)

                lineas.append(f"  [{cat.upper()}]:")
                if archivos_cat:
                    tiene_peliculas = True
                    for pelicula in sorted(archivos_cat):
                        lineas.append(f"    • {pelicula}")
                else:
                    lineas.append("    (Sin películas asignadas)")
                lineas.append("")

            if not tiene_peliculas:
                lineas.append("  (Este día no contiene archivos de video)\n")

            lineas.append("\n")

        try:
            with open(RUTA_REPORTE_TXT, "w", encoding="utf-8") as f:
                f.write("\n".join(lineas))
            self.log("📝 Reporte 'Registro_Programacion.txt' actualizado con éxito.")
        except Exception as e:
            self.log(f"⚠ No se pudo escribir el archivo TXT: {e}")

    def abrir_reporte_txt(self):
        self.generar_reporte_txt()
        if os.path.exists(RUTA_REPORTE_TXT):
            try:
                os.startfile(RUTA_REPORTE_TXT)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo TXT: {e}")
        else:
            messagebox.showinfo("Sin Datos", "Aún no hay carpetas de días trabajados para generar el reporte.")

    def iniciar_traslado(self):
        tipo = self.tipo_seleccionado.get()
        disponibles = self.diccionario_peliculas.get(tipo, [])

        if not disponibles:
            messagebox.showwarning("Sin archivos", f"No hay películas disponibles en '{tipo}'.")
            return

        try:
            cantidad = int(self.cantidad_mover.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Cantidad Inválida", "Ingresa un número mayor a 0.")
            return

        fecha = self.fecha_final.get().strip()
        if not fecha:
            messagebox.showerror("Fecha vacía", "Debes ingresar una fecha válida.")
            return

        self.btn_mover.config(state="disabled")
        threading.Thread(target=self._mover_archivos_worker, args=(tipo, cantidad, fecha), daemon=True).start()

    def _mover_archivos_worker(self, tipo, cantidad, fecha):
        lista = list(self.diccionario_peliculas[tipo])
        cantidad_real = min(cantidad, len(lista))

        random.shuffle(lista)
        seleccionadas = lista[:cantidad_real]

        carpeta_destino = os.path.join(RUTA_POR_ANO, fecha, tipo)
        os.makedirs(carpeta_destino, exist_ok=True)

        self.log(f"\n📦 Moviendo {cantidad_real} película(s) a: {carpeta_destino}")

        movidas_con_exito = 0
        for ruta_origen in seleccionadas:
            nombre = os.path.basename(ruta_origen)
            destino_archivo = os.path.join(carpeta_destino, nombre)

            if os.path.exists(destino_archivo):
                base, ext = os.path.splitext(nombre)
                c = 1
                while os.path.exists(os.path.join(carpeta_destino, f"{base}_{c}{ext}")):
                    c += 1
                destino_archivo = os.path.join(carpeta_destino, f"{base}_{c}{ext}")

            try:
                shutil.move(ruta_origen, destino_archivo)
                self.log(f" [OK] {nombre}")
                movidas_con_exito += 1
            except Exception as e:
                self.log(f" [ERROR] No se pudo mover {nombre}: {e}")

        self.log(f"🎉 Traslado finalizado: {movidas_con_exito}/{cantidad_real} películas movidas.")

        self.generar_reporte_txt()
        self._escanear_archivos()
        self.root.after(0, lambda: self.btn_mover.config(state="normal"))

if __name__ == "__main__":
    ventana = tk.Tk()
    app = GestorPeliculasApp(ventana)
    ventana.mainloop()
