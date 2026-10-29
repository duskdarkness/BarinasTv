import os
import sys
import json
import random
import hashlib
import datetime
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import xml.etree.ElementTree as ET

# ==============================================================================
# SEGURIDAD Y ACCESO (SHA-256)
# ==============================================================================
USUARIO_HASH = "c5ff177a86e82441f93e3772da700d5f6838157fa1bfdc0bb689d7f7e55e7aba"  # admin
CLAVE_HASH = "6a175db84aeefddbe58bf92a5d67b372c78505c75b079912b89a0e599fe91317"  # 1234
INTENTOS_MAXIMOS = 3

def calcular_hash(texto):
    return hashlib.sha256(texto.strip().encode('utf-8')).hexdigest()

def limpiar_ruta(texto):
    """Elimina comillas accidentales, espacios y caracteres extra."""
    if not texto:
        return ""
    return texto.strip().strip('"').strip("'").strip()

# ==============================================================================
# RUTAS GLOBALES Y ARCHIVOS
# ==============================================================================
CARPETA_DESTINO = r"D:\Luis\1 Programacion diaria\Programacion del dia"
ARCHIVO_CONFIG = "programas_config.json"
ARCHIVO_REGISTRO = "registro_ejecuciones.json"

def obtener_fecha_hoy():
    return datetime.datetime.now().strftime("%d-%m-%Y")

# ==============================================================================
# PLANTILLAS POR DEFECTO
# ==============================================================================
def obtener_programas_por_defecto():
    logo = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\BTV LOGO MUSICALIZADO 2020\BTV LOGO MUSICALIZADO 2020.mpg"
    recreativo = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\TIPOS DE PROGRAMAS 2020\PROGRAMA RECREATIVO  2020.mpg"
    horario_todo = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\TIPOS DE HORARIOS 2020\HORARIO TODOUSUARIO 2020.mpg"
    horario_sup = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\TIPOS DE HORARIOS 2020\HORARIO SUPERVISADO 2020.mpg"

    return [
        {
            "id": "barinas",
            "nombre": "Despertando con Barinas",
            "prefijo": "1.-despertando con barinas",
            "escaleta": [
                {"tipo": "musica", "nombre": "Música Llanera", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Sentir Llanero", "minutos": 114.75},
                {"tipo": "fijo", "nombre": "Logo Cierre", "ruta": logo, "duracion": 15.1151}
            ]
        },
        {
            "id": "cristiana",
            "nombre": "Música Cristiana",
            "prefijo": "2.-videos cristianos",
            "escaleta": [
                {"tipo": "fijo", "nombre": "Ahora Sigue", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\AHORA SIGUE 2020\VIDEOS CRISTIANOS.mpg", "duracion": 7.974633},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "A Continuación", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\A CONTINUACION 2020\VIDEOS CRISTIANOS.mpg", "duracion": 8.008},
                {"tipo": "fijo", "nombre": "Horario Todo Usuario", "ruta": horario_todo, "duracion": 20.8208},
                {"tipo": "fijo", "nombre": "Programa Recreativo", "ruta": recreativo, "duracion": 3.737067},
                {"tipo": "fijo", "nombre": "Presenta", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\1.-VIDEOS CRISTIANOS. PRESENTA.mpg", "duracion": 27.060367},
                
                {"tipo": "musica", "nombre": "Bloque 1", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Musica Cristiana", "minutos": 21},
                
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\2.-VIDEOS CRISTIANOS. YA REGRESAMOS.mpg", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\3.-VIDEOS CRISTIANOS. REGRESAMOS CON.mpg", "duracion": 7.7077},
                
                {"tipo": "musica", "nombre": "Bloque 2", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Musica Cristiana", "minutos": 21},
                
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\2.-VIDEOS CRISTIANOS. YA REGRESAMOS.mpg", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\3.-VIDEOS CRISTIANOS. REGRESAMOS CON.mpg", "duracion": 7.7077},
                
                {"tipo": "musica", "nombre": "Bloque 3", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Musica Cristiana", "minutos": 21},
                
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\2.-VIDEOS CRISTIANOS. YA REGRESAMOS.mpg", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\3.-VIDEOS CRISTIANOS. REGRESAMOS CON.mpg", "duracion": 7.7077},
                
                {"tipo": "musica", "nombre": "Bloque 4 Final", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Musica Cristiana", "minutos": 22},
                
                {"tipo": "fijo", "nombre": "Presentó", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\4.-VIDEOS CRISTIANOS. PRESENTÓ.mpg", "duracion": 27.060367},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151}
            ]
        },
        {
            "id": "llanero",
            "nombre": "Sentir Llanero",
            "prefijo": "3.-sentir llanero",
            "escaleta": [
                {"tipo": "fijo", "nombre": "Ahora Sigue", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\AHORA SIGUE 2020\SENTIR LLANERO.mpg", "duracion": 7.974633},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "A Continuación", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\A CONTINUACION 2020\SENTIR LLANERO.mpg", "duracion": 8.008},
                {"tipo": "fijo", "nombre": "Horario Todo Usuario", "ruta": horario_todo, "duracion": 20.8208},
                {"tipo": "fijo", "nombre": "Programa Recreativo", "ruta": recreativo, "duracion": 3.737067},
                {"tipo": "fijo", "nombre": "Presenta", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                
                {"tipo": "musica", "nombre": "Bloque 1", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Sentir Llanero", "minutos": 21},
                
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                
                {"tipo": "musica", "nombre": "Bloque 2", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Sentir Llanero", "minutos": 21},
                
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                
                {"tipo": "musica", "nombre": "Bloque 3", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Sentir Llanero", "minutos": 21},
                
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                
                {"tipo": "musica", "nombre": "Bloque 4 Final", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Sentir Llanero", "minutos": 22},
                
                {"tipo": "fijo", "nombre": "Presentó", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151}
            ]
        },
        {
            "id": "juventud",
            "nombre": "Juventud Activa",
            "prefijo": "4.-juventud activa",
            "escaleta": [
                {"tipo": "fijo", "nombre": "Ahora Sigue", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\AHORA SIGUE 2020\JUVENTUD ACTIVA.mpg", "duracion": 7.974633},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "A Continuación", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\A CONTINUACION 2020\JUVENTUD ACTIVA.mpg", "duracion": 8.008},
                {"tipo": "fijo", "nombre": "Horario Todo Usuario", "ruta": horario_todo, "duracion": 20.8208},
                {"tipo": "fijo", "nombre": "Programa Recreativo", "ruta": recreativo, "duracion": 3.737067},
                {"tipo": "fijo", "nombre": "Presenta", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\JUVENTUD ACTIVA 2016\01_BTV PRESENTA JUVENTUD ACTIVA.mpg", "duracion": 16.549867},
                
                {"tipo": "musica", "nombre": "Bloque 1", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Juventud Activa", "minutos": 55},
                
                {"tipo": "fijo", "nombre": "Ya Regresa", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\JUVENTUD ACTIVA 2016\02_YA REGRESA JUVENTUD ACTIVA.mpg", "duracion": 15.048367},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Continúa", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\JUVENTUD ACTIVA 2016\03_CONTINUA  JUVENTUD ACTIVA.mpg", "duracion": 15.048367},
                
                {"tipo": "musica", "nombre": "Bloque 2 Final", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Juventud Activa", "minutos": 55},
                
                {"tipo": "fijo", "nombre": "Presentó", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\JUVENTUD ACTIVA 2016\04_BTV PRESENTO JUVENTUD ACTIVA.mpg", "duracion": 16.549867},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151}
            ]
        },
        {
            "id": "ayer_hoy",
            "nombre": "Música de Ayer y Hoy",
            "prefijo": "5.-musica de ayer y hoy",
            "escaleta": [
                {"tipo": "fijo", "nombre": "Ahora Sigue", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\AHORA SIGUE 2020\MUSICA DE AYER Y HOY.mpg", "duracion": 7.974633},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "A Continuación", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\A CONTINUACION 2020\MUSICA DE AYER Y HOY.mpg", "duracion": 8.008},
                {"tipo": "fijo", "nombre": "Horario Supervisado", "ruta": horario_sup, "duracion": 20.8208},
                {"tipo": "fijo", "nombre": "Programa Recreativo", "ruta": recreativo, "duracion": 3.737067},
                {"tipo": "fijo", "nombre": "Presenta", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                
                {"tipo": "musica", "nombre": "Bloque 1 (Ayer y Hoy)", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\mUSICA DE aYER y hOY", "minutos": 21},
                
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                
                {"tipo": "musica", "nombre": "Bloque 2 (Ayer y Hoy)", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\mUSICA DE aYER y hOY", "minutos": 21},
                
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                
                {"tipo": "musica", "nombre": "Bloque 3 (Freecover)", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\freecover", "minutos": 21},
                
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                
                {"tipo": "musica", "nombre": "Bloque 4 (Freecover)", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\freecover", "minutos": 22},
                
                {"tipo": "fijo", "nombre": "Presentó", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151}
            ]
        }
    ]

# ==============================================================================
# CARGA Y GUARDADO
# ==============================================================================
def cargar_programas():
    if os.path.exists(ARCHIVO_CONFIG):
        try:
            with open(ARCHIVO_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    programas = obtener_programas_por_defecto()
    guardar_programas(programas)
    return programas

def guardar_programas(programas):
    with open(ARCHIVO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(programas, f, indent=4, ensure_ascii=False)

def cargar_registro():
    hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(ARCHIVO_REGISTRO):
        try:
            with open(ARCHIVO_REGISTRO, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if datos.get("fecha") == hoy:
                    return datos.get("ejecutados", {})
        except Exception:
            pass
    return {}

def guardar_registro(ejecutados):
    try:
        with open(ARCHIVO_REGISTRO, "w", encoding="utf-8") as f:
            json.dump({"fecha": datetime.datetime.now().strftime("%Y-%m-%d"), "ejecutados": ejecutados}, f, indent=4)
    except Exception as e:
        print(f"Error al guardar registro: {e}")

# ==============================================================================
# MOTOR UNIVERSAL XML (IPO)
# ==============================================================================
def recolectar_archivos(ruta_carpeta):
    ruta_limpia = limpiar_ruta(ruta_carpeta)
    exts = ('.mp4', '.mpg', '.avi', '.mkv', '.mov', '.mp3', '.wav', '.aac')
    archivos = []
    if os.path.exists(ruta_limpia):
        for raiz, _, files in os.walk(ruta_limpia):
            for file in files:
                if file.lower().endswith(exts):
                    archivos.append(os.path.join(raiz, file))
    return archivos

def crear_nodo_file(root, path_archivo, duracion):
    ruta_real = limpiar_ruta(path_archivo)
    nodo = ET.SubElement(root, 'file', {
        'in': '0.0',
        'path': ruta_real,
        'duration': str(duracion),
        'loop': 'false'
    })
    ET.SubElement(nodo, 'video', width='1280', height='720', rate='29.97003', aspect_ratio='16:9')
    ET.SubElement(nodo, 'audio', channels='2', rate='48000', bits='16')

def ejecutar_motor_universal(prog):
    if not os.path.exists(CARPETA_DESTINO):
        os.makedirs(CARPETA_DESTINO)

    archivo_salida = os.path.join(CARPETA_DESTINO, f"{prog['prefijo']} {obtener_fecha_hoy()}.xml")
    root = ET.Element('m_config', path=archivo_salida)
    ET.SubElement(root, 'video')
    ET.SubElement(root, 'audio', track_split='')

    cache_carpetas = {}

    for paso in prog["escaleta"]:
        tipo = paso.get("tipo")

        if tipo == "fijo":
            crear_nodo_file(root, paso["ruta"], paso["duracion"])

        elif tipo == "azar":
            carpeta = limpiar_ruta(paso["carpeta"])
            if carpeta not in cache_carpetas:
                encontrados = recolectar_archivos(carpeta)
                if not encontrados:
                    raise Exception(f"No hay archivos en la carpeta:\n{carpeta}")
                random.shuffle(encontrados)
                cache_carpetas[carpeta] = {"lista": encontrados, "iter": iter(encontrados)}
            
            paquete = cache_carpetas[carpeta]
            try:
                archivo_azar = next(paquete["iter"])
            except StopIteration:
                random.shuffle(paquete["lista"])
                paquete["iter"] = iter(paquete["lista"])
                archivo_azar = next(paquete["iter"])

            duracion_estimada = paso.get("duracion", 1800.0)
            crear_nodo_file(root, archivo_azar, duracion_estimada)

        elif tipo == "musica":
            carpeta = limpiar_ruta(paso["carpeta"])
            minutos = paso["minutos"]
            segundos_objetivo = minutos * 60

            if carpeta not in cache_carpetas:
                canciones = recolectar_archivos(carpeta)
                if not canciones:
                    raise Exception(f"No hay archivos multimedia en:\n{carpeta}")
                random.shuffle(canciones)
                cache_carpetas[carpeta] = {"lista": canciones, "iter": iter(canciones)}

            paquete = cache_carpetas[carpeta]
            acumulado = 0
            duracion_cancion = 210.0

            while acumulado < segundos_objetivo:
                try:
                    archivo = next(paquete["iter"])
                except StopIteration:
                    random.shuffle(paquete["lista"])
                    paquete["iter"] = iter(paquete["lista"])
                    archivo = next(paquete["iter"])

                crear_nodo_file(root, archivo, duracion_cancion)
                acumulado += duracion_cancion

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    tree.write(archivo_salida, encoding='cp1252', xml_declaration=False)

# ==============================================================================
# EDITOR DE ESCALETAS (CON DUPLICADOR)
# ==============================================================================
class VentanaEditorEscaleta(tk.Toplevel):
    def __init__(self, parent, prog, callback_guardar):
        super().__init__(parent)
        self.title(f"Editor de Escaleta - {prog['nombre']}")
        self.geometry("860x560")
        self.configure(bg="#2c3e50")
        self.prog = prog
        self.callback_guardar = callback_guardar
        self.escaleta = list(prog["escaleta"])

        lbl = tk.Label(self, text=f"Escaleta de: {prog['nombre']}", font=("Segoe UI", 13, "bold"), fg="#ecf0f1", bg="#2c3e50")
        lbl.pack(pady=10)

        frame_list = tk.Frame(self)
        frame_list.pack(fill="both", expand=True, padx=15, pady=5)

        self.tree = ttk.Treeview(frame_list, columns=("tipo", "nombre", "detalle"), show="headings", selectmode="browse")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("nombre", text="Elemento")
        self.tree.heading("detalle", text="Duración / Carpeta")
        self.tree.column("tipo", width=110, anchor="center")
        self.tree.column("nombre", width=200)
        self.tree.column("detalle", width=500)
        
        scroll = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        frame_btns = tk.Frame(self, bg="#2c3e50")
        frame_btns.pack(fill="x", padx=15, pady=10)

        tk.Button(frame_btns, text="⬆ Subir", bg="#34495e", fg="white", relief="flat", command=self.subir).pack(side="left", padx=2)
        tk.Button(frame_btns, text="⬇ Bajar", bg="#34495e", fg="white", relief="flat", command=self.bajar).pack(side="left", padx=2)
        tk.Button(frame_btns, text="📋 Duplicar", bg="#d35400", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.duplicar).pack(side="left", padx=5)
        tk.Button(frame_btns, text="➕ Cortinilla", bg="#2980b9", fg="white", relief="flat", command=self.agregar_fijo).pack(side="left", padx=3)
        tk.Button(frame_btns, text="🎲 1 Video al Azar", bg="#16a085", fg="white", relief="flat", command=self.agregar_azar).pack(side="left", padx=3)
        tk.Button(frame_btns, text="🎵 Bloque Musical", bg="#8e44ad", fg="white", relief="flat", command=self.agregar_musica).pack(side="left", padx=3)
        tk.Button(frame_btns, text="🗑 Quitar", bg="#c0392b", fg="white", relief="flat", command=self.eliminar).pack(side="left", padx=3)
        
        tk.Button(frame_btns, text="💾 GUARDAR", bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.guardar).pack(side="right", padx=2)

        self.recargar_tabla()

    def recargar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, paso in enumerate(self.escaleta):
            t = paso.get("tipo")
            if t == "fijo":
                tipo_str = "Cortinilla"
                detalle = f"{paso['duracion']} seg | {limpiar_ruta(paso['ruta'])}"
            elif t == "azar":
                tipo_str = "1 Video Azar"
                detalle = f"Carpeta: {limpiar_ruta(paso['carpeta'])}"
            else:
                tipo_str = "Bloque Música"
                detalle = f"{paso['minutos']} min | {limpiar_ruta(paso['carpeta'])}"

            self.tree.insert("", "end", iid=str(i), values=(tipo_str, paso["nombre"], detalle))

    def duplicar(self):
        """Clona el elemento seleccionado exactamente debajo."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un elemento para duplicar.", parent=self)
            return
        idx = int(sel[0])
        elemento_copiado = dict(self.escaleta[idx])
        self.escaleta.insert(idx + 1, elemento_copiado)
        self.recargar_tabla()
        self.tree.selection_set(str(idx + 1))
        self.tree.see(str(idx + 1))

    def subir(self):
        sel = self.tree.selection()
        if not sel: return
        idx = int(sel[0])
        if idx > 0:
            self.escaleta[idx - 1], self.escaleta[idx] = self.escaleta[idx], self.escaleta[idx - 1]
            self.recargar_tabla()
            self.tree.selection_set(str(idx - 1))

    def bajar(self):
        sel = self.tree.selection()
        if not sel: return
        idx = int(sel[0])
        if idx < len(self.escaleta) - 1:
            self.escaleta[idx + 1], self.escaleta[idx] = self.escaleta[idx], self.escaleta[idx + 1]
            self.recargar_tabla()
            self.tree.selection_set(str(idx + 1))

    def eliminar(self):
        sel = self.tree.selection()
        if not sel: return
        idx = int(sel[0])
        del self.escaleta[idx]
        self.recargar_tabla()

    def agregar_fijo(self):
        nom = simpledialog.askstring("Cortinilla", "Nombre (ej: Ya Regresamos):", parent=self)
        if not nom: return
        ruta = simpledialog.askstring("Ruta", "Ruta de red del archivo:", parent=self)
        if not ruta: return
        dur = simpledialog.askfloat("Duración", "Duración exacta en segundos:", parent=self)
        if dur is None: return
        self.escaleta.append({"tipo": "fijo", "nombre": nom, "ruta": limpiar_ruta(ruta), "duracion": dur})
        self.recargar_tabla()

    def agregar_azar(self):
        nom = simpledialog.askstring("Video al Azar", "Nombre (ej: Documental del Día):", parent=self)
        if not nom: return
        carpeta = simpledialog.askstring("Carpeta", "Carpeta de donde tomará 1 video al azar:", parent=self)
        if not carpeta: return
        self.escaleta.append({"tipo": "azar", "nombre": nom, "carpeta": limpiar_ruta(carpeta), "duracion": 1800.0})
        self.recargar_tabla()

    def agregar_musica(self):
        nom = simpledialog.askstring("Bloque", "Nombre (ej: Bloque 1):", parent=self)
        if not nom: return
        carpeta = simpledialog.askstring("Carpeta", "Carpeta con las canciones:", parent=self)
        if not carpeta: return
        minutos = simpledialog.askfloat("Minutos", "Minutos a rellenar (ej: 21):", parent=self)
        if minutos is None: return
        self.escaleta.append({"tipo": "musica", "nombre": nom, "carpeta": limpiar_ruta(carpeta), "minutos": minutos})
        self.recargar_tabla()

    def guardar(self):
        self.prog["escaleta"] = self.escaleta
        self.callback_guardar()
        messagebox.showinfo("Éxito", "Escaleta guardada.", parent=self)
        self.destroy()

# ==============================================================================
# ADMINISTRADOR GENERAL
# ==============================================================================
class VentanaAdminProgramas(tk.Toplevel):
    def __init__(self, parent, lista_programas, callback_actualizar_ui):
        super().__init__(parent)
        self.title("Administrador de Categorías")
        self.geometry("600x480")
        self.configure(bg="#2c3e50")
        self.programas = lista_programas
        self.callback_actualizar_ui = callback_actualizar_ui

        tk.Label(self, text="⚙ Gestión de Programas Playout", font=("Segoe UI", 13, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=12)

        frame_list = tk.Frame(self)
        frame_list.pack(fill="both", expand=True, padx=25, pady=5)

        self.listbox = tk.Listbox(frame_list, font=("Segoe UI", 11), bg="#34495e", fg="white", selectbackground="#2980b9")
        self.listbox.pack(side="left", fill="both", expand=True)
        
        scroll = tk.Scrollbar(frame_list, command=self.listbox.yview)
        scroll.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scroll.set)

        frame_acciones = tk.Frame(self, bg="#2c3e50")
        frame_acciones.pack(fill="x", padx=25, pady=12)

        tk.Button(frame_acciones, text="➕ Nuevo Programa", bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.nuevo_programa).pack(side="left", padx=4)
        tk.Button(frame_acciones, text="✏ Editar Escaleta", bg="#2980b9", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.abrir_escaleta).pack(side="left", padx=4)
        tk.Button(frame_acciones, text="🗑 Eliminar", bg="#c0392b", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.eliminar_programa).pack(side="left", padx=4)
        tk.Button(frame_acciones, text="↺ Restaurar Fábrica", bg="#e67e22", fg="white", relief="flat", command=self.restaurar_fabrica).pack(side="right", padx=4)

        self.refrescar_lista()

    def refrescar_lista(self):
        self.listbox.delete(0, tk.END)
        for p in self.programas:
            self.listbox.insert(tk.END, f"  {p['nombre']} ({len(p['escaleta'])} pasos)")

    def nuevo_programa(self):
        nom = simpledialog.askstring("Nuevo", "Nombre del Programa (ej: Documentales):", parent=self)
        if not nom: return
        prefijo = simpledialog.askstring("Prefijo", "Prefijo del archivo XML (ej: 6.-documentales):", parent=self)
        if not prefijo: return

        nuevo_id = f"prog_{len(self.programas) + 1}"
        nuevo_item = {"id": nuevo_id, "nombre": nom, "prefijo": prefijo, "escaleta": []}
        self.programas.append(nuevo_item)
        guardar_programas(self.programas)
        self.refrescar_lista()
        self.callback_actualizar_ui()
        VentanaEditorEscaleta(self, nuevo_item, lambda: guardar_programas(self.programas))

    def abrir_escaleta(self):
        sel = self.listbox.curselection()
        if not sel: return
        prog = self.programas[sel[0]]
        VentanaEditorEscaleta(self, prog, lambda: guardar_programas(self.programas))

    def eliminar_programa(self):
        sel = self.listbox.curselection()
        if not sel: return
        idx = sel[0]
        prog = self.programas[idx]
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{prog['nombre']}'?", parent=self):
            del self.programas[idx]
            guardar_programas(self.programas)
            self.refrescar_lista()
            self.callback_actualizar_ui()

    def restaurar_fabrica(self):
        if messagebox.askyesno("Restaurar", "¿Restaurar los 5 programas de fábrica?", parent=self):
            self.programas.clear()
            self.programas.extend(obtener_programas_por_defecto())
            guardar_programas(self.programas)
            self.refrescar_lista()
            self.callback_actualizar_ui()

# ==============================================================================
# PANEL PRINCIPAL
# ==============================================================================
programas_activos = cargar_programas()
registro_hoy = cargar_registro()
botones_app = {}

def ejecutar_proceso_hilo(prog):
    lbl_estado.config(text=f"Procesando '{prog['nombre']}'...", fg="#e67e22")
    ventana.update_idletasks()
    try:
        ejecutar_motor_universal(prog)
        hora = datetime.datetime.now().strftime("%I:%M %p")
        registro_hoy[prog["id"]] = hora
        guardar_registro(registro_hoy)
        actualizar_botones()
        lbl_estado.config(text=f"✔ Generado con éxito: '{prog['nombre']}' ({hora})", fg="#27ae60")
    except Exception as e:
        lbl_estado.config(text=f"Error en: '{prog['nombre']}'", fg="#c0392b")
        messagebox.showerror("Error", f"Error generando '{prog['nombre']}':\n\n{e}")

def solicitar_ejecucion(prog, forzar=False):
    if prog["id"] in registro_hoy and not forzar:
        hora = registro_hoy[prog["id"]]
        if not messagebox.askyesno("Aviso", f"'{prog['nombre']}' YA SE EJECUTÓ HOY a las {hora}.\n\n¿Volver a generar?"):
            return
    threading.Thread(target=ejecutar_proceso_hilo, args=(prog,), daemon=True).start()

def ejecutar_todos():
    pendientes = [p for p in programas_activos if p["id"] not in registro_hoy]
    if len(pendientes) < len(programas_activos):
        resp = messagebox.askyesnocancel("Ejecutar Todo", "¿Deseas ejecutar SOLO los programas pendientes?\n\n[SÍ] = Solo pendientes\n[NO] = Todos")
        if resp is None: return
        lista = pendientes if resp else programas_activos
    else:
        if not messagebox.askyesno("Confirmar", "¿Iniciar la generación de TODOS?"): return
        lista = programas_activos

    def serie():
        for p in lista:
            ejecutar_proceso_hilo(p)
    threading.Thread(target=serie, daemon=True).start()

def actualizar_botones():
    for p in programas_activos:
        btn = botones_app.get(p["id"])
        if not btn: continue
        if p["id"] in registro_hoy:
            hora = registro_hoy[p["id"]]
            btn.config(text=f"✔  {p['nombre']}   (Generado: {hora})", bg="#27ae60", activebackground="#2ecc71")
        else:
            btn.config(text=f"▶  {p['nombre']}", bg="#2980b9", activebackground="#3498db")

def reconstruir_interfaz_botones():
    for widget in frame_scroll.winfo_children():
        widget.destroy()
    botones_app.clear()

    for prog in programas_activos:
        btn = tk.Button(
            frame_scroll,
            text=f"▶  {prog['nombre']}",
            font=("Segoe UI", 10, "bold"),
            bg="#2980b9",
            fg="white",
            relief="flat",
            cursor="hand2",
            height=2,
            command=lambda p=prog: solicitar_ejecucion(p)
        )
        btn.pack(fill="x", pady=4, padx=5)
        botones_app[prog["id"]] = btn

    actualizar_botones()

# ==============================================================================
# SEGURIDAD Y LOGIN
# ==============================================================================
intentos_restantes = INTENTOS_MAXIMOS

def validar_login(event=None):
    global intentos_restantes
    if calcular_hash(entry_usuario.get()) == USUARIO_HASH and calcular_hash(entry_clave.get()) == CLAVE_HASH:
        win_login.destroy()
        ventana.deiconify()
    else:
        intentos_restantes -= 1
        entry_clave.delete(0, tk.END)
        if intentos_restantes > 0:
            lbl_error_login.config(text=f"Credenciales incorrectas. Quedan {intentos_restantes} intentos.")
        else:
            messagebox.showerror("Bloqueo", "Demasiados intentos fallidos. Cerrando aplicación.")
            ventana.destroy()

def bloquear_pantalla():
    ventana.withdraw()
    mostrar_login()

def mostrar_login():
    global win_login, entry_usuario, entry_clave, lbl_error_login, intentos_restantes
    intentos_restantes = INTENTOS_MAXIMOS

    win_login = tk.Toplevel(ventana)
    win_login.title("Acceso Protegido")
    win_login.geometry("360x320")
    win_login.resizable(False, False)
    win_login.configure(bg="#2c3e50")
    win_login.protocol("WM_DELETE_WINDOW", ventana.destroy)

    tk.Label(win_login, text="🔒 ACCESO REQUERIDO", font=("Segoe UI", 13, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=(20, 15))

    tk.Label(win_login, text="Usuario:", font=("Segoe UI", 9, "bold"), fg="#bdc3c7", bg="#2c3e50").pack(anchor="w", padx=45)
    entry_usuario = tk.Entry(win_login, font=("Segoe UI", 11))
    entry_usuario.pack(padx=45, fill="x", pady=(2, 10))
    entry_usuario.focus()

    tk.Label(win_login, text="Contraseña:", font=("Segoe UI", 9, "bold"), fg="#bdc3c7", bg="#2c3e50").pack(anchor="w", padx=45)
    entry_clave = tk.Entry(win_login, show="•", font=("Segoe UI", 11))
    entry_clave.pack(padx=45, fill="x", pady=(2, 5))
    entry_clave.bind("<Return>", validar_login)

    lbl_error_login = tk.Label(win_login, text="", font=("Segoe UI", 8, "bold"), fg="#e74c3c", bg="#2c3e50")
    lbl_error_login.pack(pady=4)

    tk.Button(win_login, text="Ingresar", font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white", relief="flat", cursor="hand2", command=validar_login).pack(fill="x", padx=45, pady=10)

# ==============================================================================
# VENTANA PRINCIPAL
# ==============================================================================
ventana = tk.Tk()
ventana.title("Panel Playout - Generador de Contenido")
ventana.geometry("560x700")
ventana.resizable(False, False)
ventana.configure(bg="#f4f6f9")
ventana.withdraw()

frame_top = tk.Frame(ventana, bg="#f4f6f9")
frame_top.pack(fill="x", padx=20, pady=(15, 0))

tk.Label(frame_top, text="Generador de Contenido", font=("Segoe UI", 15, "bold"), bg="#f4f6f9", fg="#2c3e50").pack(side="left")

btn_lock = tk.Button(frame_top, text="🔒 Bloquear", font=("Segoe UI", 8, "bold"), bg="#e67e22", fg="white", relief="flat", cursor="hand2", command=bloquear_pantalla)
btn_lock.pack(side="right", padx=2)

btn_admin = tk.Button(frame_top, text="⚙ Administrar", font=("Segoe UI", 8, "bold"), bg="#34495e", fg="white", relief="flat", cursor="hand2", 
                      command=lambda: VentanaAdminProgramas(ventana, programas_activos, reconstruir_interfaz_botones))
btn_admin.pack(side="right", padx=4)

lbl_sub = tk.Label(ventana, text=f"Fecha de emisión: {datetime.datetime.now().strftime('%d/%m/%Y')}", font=("Segoe UI", 9), bg="#f4f6f9", fg="#7f8c8d")
lbl_sub.pack(pady=(2, 10))

btn_all = tk.Button(ventana, text="⚡ EJECUTAR TODOS LOS PROGRAMAS", font=("Segoe UI", 11, "bold"), bg="#8e44ad", fg="white", relief="flat", cursor="hand2", height=2, command=ejecutar_todos)
btn_all.pack(fill="x", padx=25, pady=(0, 10))

tk.Frame(ventana, height=2, bg="#dcdde1").pack(fill="x", padx=25, pady=(0, 10))

canvas = tk.Canvas(ventana, bg="#f4f6f9", highlightthickness=0)
scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
frame_scroll = tk.Frame(canvas, bg="#f4f6f9")

frame_scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas_window = canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
canvas.bind('<Configure>', lambda event: canvas.itemconfig(canvas_window, width=event.width))
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="top", fill="both", expand=True, padx=(25, 5))
scrollbar.pack(side="right", fill="y", before=canvas)

lbl_estado = tk.Label(ventana, text="Listo para ejecutar", font=("Segoe UI", 9, "italic"), bg="#f4f6f9", fg="#7f8c8d")
lbl_estado.pack(side="bottom", pady=6)

tk.Button(ventana, text="Cerrar Aplicación", font=("Segoe UI", 9), bg="#bdc3c7", fg="#2c3e50", relief="flat", cursor="hand2", command=ventana.destroy).pack(side="bottom", pady=4)

reconstruir_interfaz_botones()
mostrar_login()
ventana.mainloop()
