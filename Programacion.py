import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import json
from datetime import datetime

# Rutas y nombres de tus programas
PROGRAMAS = [
    {
        "id": "barinas",
        "nombre": "Despertando con Barinas",
        "ruta": r"D:\Luis\1 Programacion diaria\Generador de contenido\Despertando con Barinas.py"
    },
    {
        "id": "cristiana",
        "nombre": "Música Cristiana",
        "ruta": r"D:\Luis\1 Programacion diaria\Generador de contenido\Musica Cristiana.py"
    },
    {
        "id": "llanero",
        "nombre": "Sentir Llanero",
        "ruta": r"D:\Luis\1 Programacion diaria\Generador de contenido\Sentir Llanero.py"
    },
    {
        "id": "juventud",
        "nombre": "Juventud Activa",
        "ruta": r"D:\Luis\1 Programacion diaria\Generador de contenido\Juventud Activa.py"
    },
    {
        "id": "ayer_hoy",
        "nombre": "Música de Ayer y Hoy",
        "ruta": r"D:\Luis\1 Programacion diaria\Generador de contenido\Musica de ayer y hoy.py"
    }
]

ARCHIVO_REGISTRO = "registro_ejecuciones.json"

# --- GESTIÓN DE REGISTRO DIARIO ---
def obtener_hoy():
    return datetime.now().strftime("%Y-%m-%d")

def cargar_registro():
    """Carga el registro. Si es un día nuevo, lo reinicia."""
    hoy = obtener_hoy()
    if os.path.exists(ARCHIVO_REGISTRO):
        try:
            with open(ARCHIVO_REGISTRO, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if datos.get("fecha") == hoy:
                    return datos.get("ejecutados", {})
        except Exception:
            pass
    # Si no existe o es de otro día, empieza limpio
    return {}

def guardar_registro(ejecutados):
    try:
        with open(ARCHIVO_REGISTRO, "w", encoding="utf-8") as f:
            json.dump({"fecha": obtener_hoy(), "ejecutados": ejecutados}, f, indent=4)
    except Exception as e:
        print(f"Error al guardar registro: {e}")

registro_hoy = cargar_registro()
botones_app = {}

# --- ACCIONES ---
def lanzar_proceso(ruta):
    """Ejecuta el script de manera independiente."""
    subprocess.Popen([sys.executable, ruta])

def ejecutar_script(prog, forzar=False):
    """Ejecuta un script individual validando si ya se usó hoy."""
    prog_id = prog["id"]
    nombre = prog["nombre"]
    ruta = prog["ruta"]

    if not os.path.exists(ruta):
        messagebox.showerror("Error", f"No se encontró el archivo:\n\n{ruta}")
        return False

    # Verificar si ya se corrió hoy
    if prog_id in registro_hoy and not forzar:
        hora_ejecucion = registro_hoy[prog_id]
        respuesta = messagebox.askyesno(
            "Aviso: Programa ya ejecutado",
            f"El programa '{nombre}' YA SE EJECUTÓ HOY a las {hora_ejecucion}.\n\n"
            "¿Estás seguro de que deseas volver a ejecutarlo?"
        )
        if not respuesta:
            return False  # El usuario canceló la ejecución

    # Ejecutar
    try:
        lanzar_proceso(ruta)
        hora_actual = datetime.now().strftime("%I:%M %p")
        registro_hoy[prog_id] = hora_actual
        guardar_registro(registro_hoy)
        actualizar_botones()
        lbl_estado.config(text=f"Última acción: Ejecutado '{nombre}' ({hora_actual})", fg="#27ae60")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al ejecutar {nombre}:\n{e}")
        return False

def ejecutar_todo():
    """Ejecuta todos los scripts de la lista."""
    pendientes = [p for p in PROGRAMAS if p["id"] not in registro_hoy]
    
    if len(pendientes) < len(PROGRAMAS):
        msg = (
            "Algunos programas ya se ejecutaron hoy.\n\n"
            "• Presiona [SÍ] para ejecutar ÚNICAMENTE los que faltan.\n"
            "• Presiona [NO] para forzar la ejecución de TODOS."
        )
        resp = messagebox.askyesnocancel("Ejecutar Todo", msg)
        if resp is None:
            return  # Cancelar operación
        lista_a_ejecutar = pendientes if resp else PROGRAMAS
    else:
        if not messagebox.askyesno("Confirmar", "¿Deseas iniciar TODOS los programas en cola?"):
            return
        lista_a_ejecutar = PROGRAMAS

    for prog in lista_a_ejecutar:
        ejecutar_script(prog, forzar=True)

def actualizar_botones():
    """Actualiza la apariencia de los botones si ya fueron ejecutados."""
    for prog in PROGRAMAS:
        btn = botones_app.get(prog["id"])
        if not btn:
            continue
        if prog["id"] in registro_hoy:
            hora = registro_hoy[prog["id"]]
            btn.config(
                text=f"✔  {prog['nombre']}   (Ejecutado: {hora})",
                bg="#27ae60",
                activebackground="#2ecc71"
            )
        else:
            btn.config(
                text=f"▶  {prog['nombre']}",
                bg="#2980b9",
                activebackground="#3498db"
            )

# --- INTERFAZ GRÁFICA ---
ventana = tk.Tk()
ventana.title("Panel de Control - Programación Diaria")
ventana.geometry("540x630")
ventana.resizable(False, False)
ventana.configure(bg="#f4f6f9")

# Encabezado
lbl_titulo = tk.Label(
    ventana, 
    text="Generador de Contenido", 
    font=("Segoe UI", 16, "bold"), 
    bg="#f4f6f9", 
    fg="#2c3e50"
)
lbl_titulo.pack(pady=(15, 2))

lbl_subtitulo = tk.Label(
    ventana, 
    text=f"Registro de hoy: {datetime.now().strftime('%d/%m/%Y')}", 
    font=("Segoe UI", 9), 
    bg="#f4f6f9", 
    fg="#7f8c8d"
)
lbl_subtitulo.pack(pady=(0, 12))

# Botón Especial: Ejecutar Todo
btn_todos = tk.Button(
    ventana,
    text="⚡ EJECUTAR TODOS LOS PROGRAMAS",
    font=("Segoe UI", 11, "bold"),
    bg="#8e44ad",
    fg="white",
    activebackground="#9b59b6",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    height=2,
    command=ejecutar_todo
)
btn_todos.pack(fill="x", padx=25, pady=(0, 15))

# Separador visual
tk.Frame(ventana, height=2, bg="#dcdde1").pack(fill="x", padx=25, pady=(0, 15))

# Frame de los programas individuales
frame_botones = tk.Frame(ventana, bg="#f4f6f9")
frame_botones.pack(padx=25, fill="both", expand=True)

for prog in PROGRAMAS:
    btn = tk.Button(
        frame_botones,
        text=f"▶  {prog['nombre']}",
        font=("Segoe UI", 10, "bold"),
        bg="#2980b9",
        fg="white",
        relief="flat",
        cursor="hand2",
        height=2,
        command=lambda p=prog: ejecutar_script(p)
    )
    btn.pack(fill="x", pady=4)
    botones_app[prog["id"]] = btn

# Actualizar el aspecto de los botones si ya se habían corrido hoy
actualizar_botones()

# Barra de estado inferior
lbl_estado = tk.Label(
    ventana, 
    text="Listo para ejecutar", 
    font=("Segoe UI", 9, "italic"), 
    bg="#f4f6f9", 
    fg="#7f8c8d"
)
lbl_estado.pack(side="bottom", pady=8)

# Botón para cerrar
btn_salir = tk.Button(
    ventana,
    text="Cerrar Aplicación",
    font=("Segoe UI", 9),
    bg="#bdc3c7",
    fg="#2c3e50",
    relief="flat",
    cursor="hand2",
    command=ventana.destroy
)
btn_salir.pack(side="bottom", pady=4)

# Mantiene abierta la app
ventana.mainloop()
