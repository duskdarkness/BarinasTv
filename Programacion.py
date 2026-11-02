import os
import sys
import json
import random
import hashlib
import datetime
import threading
import subprocess
import urllib.request
import urllib.parse
import webbrowser
import shutil
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import xml.etree.ElementTree as ET

# ==============================================================================
# DETECCIÓN DE DIRECTORIO BASE (COMPATIBLE CON NUITKA / PYINSTALLER / .EXE)
# ==============================================================================
def obtener_directorio_base():
    """Retorna la carpeta real del ejecutable para no perder archivos de licencia ni configs."""
    if "__compiled__" in globals():
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    elif getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = obtener_directorio_base()

# ==============================================================================
# VERSIÓN DEL SOFTWARE Y CONFIGURACIÓN EN LA NUBE
# ==============================================================================
VERSION_LOCAL = "1.0.0"
URL_SERVIDOR_LICENCIAS = "https://script.google.com/macros/s/AKfycbwDM0c8Brh8sv0KA-QNSMr_yVxA0tUOYYBWXraVglLQ6FsxXo4C6CdDRq2UwKdH0rAI/exec"

ARCHIVO_LICENCIA_LOCAL = os.path.join(BASE_DIR, "licencia.dat")
ARCHIVO_SEGURIDAD_LOCAL = os.path.join(BASE_DIR, "seguridad.dat")
ARCHIVO_CONFIG_GLOBAL = os.path.join(BASE_DIR, "config_general.json")
ARCHIVO_CONFIG_PROGRAMAS = os.path.join(BASE_DIR, "programas_config.json")
ARCHIVO_REGISTRO_DIARIO = os.path.join(BASE_DIR, "registro_ejecuciones.json")

INTENTOS_MAXIMOS = 3

# Datos remotos cargados dinámicamente desde Google Sheets
datos_remotos = {
    "cliente": "",
    "vence": "",
    "dias_restantes": 365,
    "contacto": "+584120000000",
    "version_remota": VERSION_LOCAL,
    "url_descarga": "",
    "notas_actualizacion": ""
}

# ==============================================================================
# UTILIDADES DE RUTAS, HUELLA HARDWARE Y CRIPTOGRAFÍA
# ==============================================================================
def calcular_hash(texto):
    return hashlib.sha256(texto.strip().encode('utf-8')).hexdigest()

def limpiar_ruta(texto):
    """
    Elimina comillas, espacios y convierte TODAS las barras / a formato Windows \\.
    Garantiza que las rutas de red UNC siempre comiencen con \\\\ y nunca con //.
    """
    if not texto:
        return ""
    texto = str(texto).strip().strip('"').strip("'").strip()
    if not texto:
        return ""

    es_red = texto.startswith("//") or texto.startswith("\\\\")
    texto = texto.replace("/", "\\")

    partes = [p for p in texto.split("\\") if p]
    if not partes:
        return ""

    if es_red:
        return "\\\\" + "\\".join(partes)
    else:
        if ":" in partes[0]:
            return partes[0] + "\\" + "\\".join(partes[1:])
        return "\\".join(partes)

def obtener_hwid():
    """Genera la huella única de la computadora del cliente."""
    try:
        cmd = 'powershell -command "(Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"'
        uuid = subprocess.check_output(cmd, shell=True).decode().strip()
        if uuid: return uuid
    except Exception:
        pass
    import platform
    hw_cadena = f"{platform.node()}-{platform.processor()}-{os.environ.get('COMPUTERNAME', '')}"
    return hashlib.md5(hw_cadena.encode()).hexdigest()

def calcular_dias_desde_fecha(vence_str):
    """Calcula con exactitud los días restantes usando el reloj local."""
    try:
        vence_limpio = str(vence_str).split("T")[0].strip()
        if "/" in vence_limpio:
            partes = [int(p) for p in vence_limpio.split("/")]
            fecha_vence = datetime.date(partes[0], partes[1], partes[2]) if partes[0] > 31 else datetime.date(partes[2], partes[1], partes[0])
        elif "-" in vence_limpio:
            partes = [int(p) for p in vence_limpio.split("-")]
            fecha_vence = datetime.date(partes[0], partes[1], partes[2]) if partes[0] > 31 else datetime.date(partes[2], partes[1], partes[0])
        else:
            return 365

        hoy = datetime.date.today()
        dias = (fecha_vence - hoy).days
        return max(0, dias)
    except Exception:
        return 365

# ==============================================================================
# CONFIGURACIÓN GENERAL (CARPETA DE SALIDA XML)
# ==============================================================================
def cargar_config_general():
    if os.path.exists(ARCHIVO_CONFIG_GLOBAL):
        try:
            with open(ARCHIVO_CONFIG_GLOBAL, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    default_dir = os.path.join(os.path.expanduser("~"), "Documents", "Playout_XML")
    return {"carpeta_salida": default_dir}

def guardar_config_general(cfg):
    with open(ARCHIVO_CONFIG_GLOBAL, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)

config_general = cargar_config_general()

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
                {"tipo": "musica", "nombre": "Bloque 1", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Musica Cristiana", "minutos": 21.0},
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\2.-VIDEOS CRISTIANOS. YA REGRESAMOS.mpg", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\3.-VIDEOS CRISTIANOS. REGRESAMOS CON.mpg", "duracion": 7.7077},
                {"tipo": "musica", "nombre": "Bloque 2", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Musica Cristiana", "minutos": 21.0},
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\2.-VIDEOS CRISTIANOS. YA REGRESAMOS.mpg", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\3.-VIDEOS CRISTIANOS. REGRESAMOS CON.mpg", "duracion": 7.7077},
                {"tipo": "musica", "nombre": "Bloque 3", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Musica Cristiana", "minutos": 21.0},
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\2.-VIDEOS CRISTIANOS. YA REGRESAMOS.mpg", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\VIDEOS CRISTIANOS\3.-VIDEOS CRISTIANOS. REGRESAMOS CON.mpg", "duracion": 7.7077},
                {"tipo": "musica", "nombre": "Bloque 4 Final", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Musica Cristiana", "minutos": 22.0},
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
                {"tipo": "musica", "nombre": "Bloque 1", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Sentir Llanero", "minutos": 21.0},
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                {"tipo": "musica", "nombre": "Bloque 2", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Sentir Llanero", "minutos": 21.0},
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                {"tipo": "musica", "nombre": "Bloque 3", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Sentir Llanero", "minutos": 21.0},
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Sentir Llanero\SENTIR LLANERO.mp4", "duracion": 7.6076},
                {"tipo": "musica", "nombre": "Bloque 4 Final", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Sentir Llanero", "minutos": 22.0},
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
                {"tipo": "musica", "nombre": "Bloque 1", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Juventud Activa", "minutos": 55.0},
                {"tipo": "fijo", "nombre": "Ya Regresa", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\JUVENTUD ACTIVA 2016\02_YA REGRESA JUVENTUD ACTIVA.mpg", "duracion": 15.048367},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Continúa", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\JUVENTUD ACTIVA 2016\03_CONTINUA  JUVENTUD ACTIVA.mpg", "duracion": 15.048367},
                {"tipo": "musica", "nombre": "Bloque 2 Final", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Juventud Activa", "minutos": 55.0},
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
                {"tipo": "musica", "nombre": "Bloque 1 (Ayer y Hoy)", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\mUSICA DE aYER y hOY", "minutos": 21.0},
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                {"tipo": "musica", "nombre": "Bloque 2 (Ayer y Hoy)", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\mUSICA DE aYER y hOY", "minutos": 21.0},
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                {"tipo": "musica", "nombre": "Bloque 3 (Freecover)", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\freecover", "minutos": 21.0},
                {"tipo": "fijo", "nombre": "Ya Regresamos", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151},
                {"tipo": "fijo", "nombre": "Regresamos Con", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                {"tipo": "musica", "nombre": "Bloque 4 (Freecover)", "carpeta": r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\freecover", "minutos": 22.0},
                {"tipo": "fijo", "nombre": "Presentó", "ruta": r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4", "duracion": 7.7077},
                {"tipo": "fijo", "nombre": "Logo Musicalizado", "ruta": logo, "duracion": 15.1151}
            ]
        }
    ]

# ==============================================================================
# CARGA Y GUARDADO CON AUTO-REPARACIÓN DE BARRAS
# ==============================================================================
def cargar_programas():
    if os.path.exists(ARCHIVO_CONFIG_PROGRAMAS):
        try:
            with open(ARCHIVO_CONFIG_PROGRAMAS, "r", encoding="utf-8") as f:
                programas = json.load(f)
                for prog in programas:
                    for paso in prog.get("escaleta", []):
                        if "ruta" in paso: paso["ruta"] = limpiar_ruta(paso["ruta"])
                        if "carpeta" in paso: paso["carpeta"] = limpiar_ruta(paso["carpeta"])
                if programas: return programas
        except Exception:
            pass
    programas = obtener_programas_por_defecto()
    guardar_programas(programas)
    return programas

def guardar_programas(programas):
    for prog in programas:
        for paso in prog.get("escaleta", []):
            if "ruta" in paso: paso["ruta"] = limpiar_ruta(paso["ruta"])
            if "carpeta" in paso: paso["carpeta"] = limpiar_ruta(paso["carpeta"])

    with open(ARCHIVO_CONFIG_PROGRAMAS, "w", encoding="utf-8") as f:
        json.dump(programas, f, indent=4, ensure_ascii=False)

def cargar_registro():
    hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(ARCHIVO_REGISTRO_DIARIO):
        try:
            with open(ARCHIVO_REGISTRO_DIARIO, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if datos.get("fecha") == hoy:
                    return datos.get("ejecutados", {})
        except Exception:
            pass
    return {}

def guardar_registro(ejecutados):
    try:
        with open(ARCHIVO_REGISTRO_DIARIO, "w", encoding="utf-8") as f:
            json.dump({"fecha": datetime.datetime.now().strftime("%Y-%m-%d"), "ejecutados": ejecutados}, f, indent=4)
    except Exception as e:
        print(f"Error al guardar registro: {e}")

# ==============================================================================
# SISTEMA DE ACTUALIZACIÓN REMOTA AUTOMÁTICA
# ==============================================================================
def comprobar_actualizacion_disponible(parent):
    v_remota = datos_remotos.get("version_remota", VERSION_LOCAL)
    url_descarga = datos_remotos.get("url_descarga", "")
    notas = datos_remotos.get("notas_actualizacion", "Mejoras generales de estabilidad.")

    if v_remota > VERSION_LOCAL and url_descarga.startswith("http"):
        msg = (
            f"¡Nueva versión disponible: v{v_remota}!\n"
            f"Versión actual: v{VERSION_LOCAL}\n\n"
            f"Novedades:\n{notas}\n\n"
            f"¿Deseas descargar y aplicar la actualización automáticamente ahora?"
        )
        if messagebox.askyesno("Actualización Encontrada", msg, parent=parent):
            ejecutar_actualizacion(url_descarga)

def ejecutar_actualizacion(url_descarga):
    win_upd = tk.Toplevel(ventana)
    win_upd.title("Actualizando Sistema")
    win_upd.geometry("380x150")
    win_upd.configure(bg="#2c3e50")
    tk.Label(win_upd, text="Descargando actualización...", font=("Segoe UI", 11, "bold"), fg="white", bg="#2c3e50").pack(pady=20)
    prog_bar = ttk.Progressbar(win_upd, mode="indeterminate")
    prog_bar.pack(fill="x", padx=40)
    prog_bar.start()

    def tarea_descarga():
        try:
            exe_actual = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
            carpeta_app = os.path.dirname(exe_actual)
            exe_nuevo = os.path.join(carpeta_app, "nuevo_update.exe")

            urllib.request.urlretrieve(url_descarga, exe_nuevo)

            bat_reemplazo = os.path.join(carpeta_app, "actualizar.bat")
            with open(bat_reemplazo, "w") as f:
                f.write(f"""@echo off
timeout /t 2 /nobreak >nul
move /y "{exe_nuevo}" "{exe_actual}"
start "" "{exe_actual}"
del "%~f0"
""")
            subprocess.Popen([bat_reemplazo], shell=True)
            os._exit(0)
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al actualizar:\n{e}")
            win_upd.destroy()

    threading.Thread(target=tarea_descarga, daemon=True).start()

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
                    archivos.append(limpiar_ruta(os.path.join(raiz, file)))
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
    carpeta_salida = limpiar_ruta(config_general.get("carpeta_salida", ""))
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    fecha_hoy = datetime.datetime.now().strftime("%d-%m-%Y")
    archivo_salida = limpiar_ruta(os.path.join(carpeta_salida, f"{prog['prefijo']} {fecha_hoy}.xml"))
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
# EDITOR DE ESCALETAS (BUSCADOR WINDOWS + EDICIÓN MANUAL)
# ==============================================================================
class VentanaEditorEscaleta(tk.Toplevel):
    def __init__(self, parent, prog, callback_guardar):
        super().__init__(parent)
        self.title(f"Editor de Escaleta - {prog['nombre']}")
        self.geometry("980x580")
        self.configure(bg="#2c3e50")
        self.prog = prog
        self.callback_guardar = callback_guardar
        self.escaleta = list(prog.get("escaleta", []))

        self.reparar_rutas(silencioso=True)

        lbl = tk.Label(self, text=f"Escaleta de: {prog['nombre']}", font=("Segoe UI", 13, "bold"), fg="#ecf0f1", bg="#2c3e50")
        lbl.pack(pady=10)

        frame_list = tk.Frame(self)
        frame_list.pack(fill="both", expand=True, padx=15, pady=5)

        self.tree = ttk.Treeview(frame_list, columns=("tipo", "nombre", "detalle"), show="headings", selectmode="browse")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("nombre", text="Elemento")
        self.tree.heading("detalle", text="Duración / Carpeta")
        self.tree.column("tipo", width=120, anchor="center")
        self.tree.column("nombre", width=180)
        self.tree.column("detalle", width=620)
        
        self.tree.bind("<Double-1>", lambda event: self.editar_manual())

        scroll = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        frame_btns = tk.Frame(self, bg="#2c3e50")
        frame_btns.pack(fill="x", padx=15, pady=10)

        tk.Button(frame_btns, text="⬆ Subir", bg="#34495e", fg="white", relief="flat", command=self.subir).pack(side="left", padx=2)
        tk.Button(frame_btns, text="⬇ Bajar", bg="#34495e", fg="white", relief="flat", command=self.bajar).pack(side="left", padx=2)
        tk.Button(frame_btns, text="📋 Duplicar", bg="#d35400", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.duplicar).pack(side="left", padx=3)
        
        tk.Button(frame_btns, text="✏ Editar Fila", bg="#1f3a52", fg="#f1c40f", font=("Segoe UI", 9, "bold"), relief="groove", command=self.editar_manual).pack(side="left", padx=3)
        tk.Button(frame_btns, text="➕ Cortinilla (Archivo)", bg="#2980b9", fg="white", relief="flat", command=self.agregar_fijo).pack(side="left", padx=2)
        tk.Button(frame_btns, text="🎲 1 Video Azar", bg="#16a085", fg="white", relief="flat", command=self.agregar_azar).pack(side="left", padx=2)
        tk.Button(frame_btns, text="🎵 Bloque Música", bg="#8e44ad", fg="white", relief="flat", command=self.agregar_musica).pack(side="left", padx=2)
        tk.Button(frame_btns, text="🗑 Quitar", bg="#c0392b", fg="white", relief="flat", command=self.eliminar).pack(side="left", padx=2)
        tk.Button(frame_btns, text="🛠 Corregir // a \\\\", bg="#7f8c8d", fg="white", relief="flat", command=lambda: self.reparar_rutas(silencioso=False)).pack(side="left", padx=4)

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

    def agregar_fijo(self):
        nom = simpledialog.askstring("Cortinilla", "Nombre (ej: Ya Regresamos):", parent=self)
        if not nom: return
        ruta = filedialog.askopenfilename(
            title="Seleccionar Archivo de Cortinilla (Red o Local)",
            filetypes=[("Archivos de video", "*.mp4 *.mpg *.avi *.mkv *.mov *.mp3 *.wav *.wmv"), ("Todos los archivos", "*.*")],
            parent=self
        )
        if not ruta:
            ruta = simpledialog.askstring("Ruta Manual", "No seleccionaste archivo. ¿Deseas escribirla o pegarla?:", parent=self)
        if not ruta: return

        dur = simpledialog.askfloat("Duración", "Duración exacta en segundos:", initialvalue=10.0, parent=self)
        if dur is None: return

        self.escaleta.append({"tipo": "fijo", "nombre": nom, "ruta": limpiar_ruta(ruta), "duracion": dur})
        self.recargar_tabla()

    def agregar_azar(self):
        nom = simpledialog.askstring("Video al Azar", "Nombre (ej: Documental del Día):", parent=self)
        if not nom: return
        carpeta = filedialog.askdirectory(title="Seleccionar Carpeta con Videos al Azar", parent=self)
        if not carpeta:
            carpeta = simpledialog.askstring("Carpeta Manual", "No seleccionaste carpeta. ¿Deseas escribirla o pegarla?:", parent=self)
        if not carpeta: return

        self.escaleta.append({"tipo": "azar", "nombre": nom, "carpeta": limpiar_ruta(carpeta), "duracion": 1800.0})
        self.recargar_tabla()

    def agregar_musica(self):
        nom = simpledialog.askstring("Bloque", "Nombre (ej: Bloque 1):", parent=self)
        if not nom: return
        carpeta = filedialog.askdirectory(title="Seleccionar Carpeta para Bloque Musical", parent=self)
        if not carpeta:
            carpeta = simpledialog.askstring("Carpeta Manual", "No seleccionaste carpeta. ¿Deseas escribirla o pegarla?:", parent=self)
        if not carpeta: return

        minutos = simpledialog.askfloat("Minutos", "Minutos a rellenar (ej: 21):", initialvalue=21.0, parent=self)
        if minutos is None: return

        self.escaleta.append({"tipo": "musica", "nombre": nom, "carpeta": limpiar_ruta(carpeta), "minutos": minutos})
        self.recargar_tabla()

    def editar_manual(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona una fila para editar.\n(O haz doble clic sobre ella).", parent=self)
            return

        idx = int(sel[0])
        paso = self.escaleta[idx]
        tipo = paso.get("tipo")

        metodo = messagebox.askyesnocancel(
            "Método de Edición",
            f"¿Cómo deseas modificar '{paso['nombre']}'?\n\n"
            f"[SÍ] = Buscar con ventana de Windows (Examinar)\n"
            f"[NO] = Escribir / Corregir texto manualmente\n"
            f"[CANCELAR] = Dejar sin cambios",
            parent=self
        )
        if metodo is None: return

        if tipo == "fijo":
            nueva_ruta = None
            if metodo:
                dir_inicial = os.path.dirname(paso.get("ruta", ""))
                nueva_ruta = filedialog.askopenfilename(
                    title=f"Seleccionar nuevo archivo para '{paso['nombre']}'",
                    filetypes=[("Archivos de video", "*.mp4 *.mpg *.avi *.mkv *.mov *.mp3 *.wav *.wmv"), ("Todos los archivos", "*.*")],
                    initialdir=dir_inicial if os.path.exists(dir_inicial) else None,
                    parent=self
                )
            else:
                nueva_ruta = simpledialog.askstring("Editar Ruta", f"Modifica la ruta para '{paso['nombre']}':", initialvalue=paso.get("ruta", ""), parent=self)

            if nueva_ruta: paso["ruta"] = limpiar_ruta(nueva_ruta)

            nueva_dur = simpledialog.askfloat("Editar Duración", "Duración en segundos:", initialvalue=float(paso.get("duracion", 0.0)), parent=self)
            if nueva_dur is not None: paso["duracion"] = nueva_dur

        elif tipo in ("musica", "azar"):
            nueva_carpeta = None
            if metodo:
                dir_inicial = paso.get("carpeta", "")
                nueva_carpeta = filedialog.askdirectory(
                    title=f"Seleccionar nueva carpeta para '{paso['nombre']}'",
                    initialdir=dir_inicial if os.path.exists(dir_inicial) else None,
                    parent=self
                )
            else:
                nueva_carpeta = simpledialog.askstring(
                    "Editar Carpeta", 
                    f"Modifica la carpeta para '{paso['nombre']}':\n(Cualquier '/' será convertido a '\\' automáticamente)", 
                    initialvalue=paso.get("carpeta", ""), 
                    parent=self
                )

            if nueva_carpeta: paso["carpeta"] = limpiar_ruta(nueva_carpeta)

            if tipo == "musica":
                nuevos_min = simpledialog.askfloat("Editar Minutos", "Minutos a rellenar:", initialvalue=float(paso.get("minutos", 0.0)), parent=self)
                if nuevos_min is not None: paso["minutos"] = nuevos_min

        self.recargar_tabla()
        self.tree.selection_set(str(idx))

    def reparar_rutas(self, silencioso=False):
        cambios = 0
        for paso in self.escaleta:
            if "ruta" in paso:
                orig = paso["ruta"]
                limpia = limpiar_ruta(orig)
                if orig != limpia:
                    paso["ruta"] = limpia
                    cambios += 1
            if "carpeta" in paso:
                orig = paso["carpeta"]
                limpia = limpiar_ruta(orig)
                if orig != limpia:
                    paso["carpeta"] = limpia
                    cambios += 1

        if not silencioso:
            self.recargar_tabla()
            if cambios > 0:
                messagebox.showinfo("Listo", f"Se corrigieron {cambios} rutas con formato de red Windows (\\\\).\nHaz clic en GUARDAR para confirmar.", parent=self)
            else:
                messagebox.showinfo("Correcto", "Todas las rutas ya tienen el formato correcto (\\\\).", parent=self)

    def duplicar(self):
        sel = self.tree.selection()
        if not sel: return
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

    def guardar(self):
        self.reparar_rutas(silencioso=True)
        self.prog["escaleta"] = self.escaleta
        self.callback_guardar()
        messagebox.showinfo("Éxito", "Escaleta guardada con todas las rutas normalizadas (\\\\).", parent=self)
        self.destroy()

# ==============================================================================
# ADMINISTRADOR GENERAL (PROGRAMAS, RESPALDOS Y DIAGNÓSTICO)
# ==============================================================================
class VentanaAdminProgramas(tk.Toplevel):
    def __init__(self, parent, lista_programas, callback_actualizar_ui):
        super().__init__(parent)
        self.title("Administrador de Categorías y Sistema")
        self.geometry("680x520")
        self.configure(bg="#2c3e50")
        self.programas = lista_programas
        self.callback_actualizar_ui = callback_actualizar_ui

        tk.Label(self, text="⚙ Panel de Configuración y Escaletas", font=("Segoe UI", 13, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=10)

        frame_list = tk.Frame(self)
        frame_list.pack(fill="both", expand=True, padx=20, pady=5)

        self.listbox = tk.Listbox(frame_list, font=("Segoe UI", 11), bg="#34495e", fg="white", selectbackground="#2980b9")
        self.listbox.pack(side="left", fill="both", expand=True)
        
        scroll = tk.Scrollbar(frame_list, command=self.listbox.yview)
        scroll.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scroll.set)

        # Fila 1 de acciones
        frame_acciones = tk.Frame(self, bg="#2c3e50")
        frame_acciones.pack(fill="x", padx=20, pady=6)

        tk.Button(frame_acciones, text="➕ Nuevo Programa", bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.nuevo_programa).pack(side="left", padx=3)
        tk.Button(frame_acciones, text="✏ Editar Escaleta", bg="#2980b9", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.abrir_escaleta).pack(side="left", padx=3)
        tk.Button(frame_acciones, text="🗑 Eliminar", bg="#c0392b", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.eliminar_programa).pack(side="left", padx=3)
        tk.Button(frame_acciones, text="🔍 Diagnóstico de Rutas", bg="#16a085", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.diagnostico_rutas).pack(side="right", padx=3)

        # Fila 2 de acciones (Respaldos y Seguridad)
        frame_acciones2 = tk.Frame(self, bg="#2c3e50")
        frame_acciones2.pack(fill="x", padx=20, pady=6)

        tk.Button(frame_acciones2, text="💾 Exportar a USB", bg="#d35400", fg="white", relief="flat", command=self.exportar_respaldo).pack(side="left", padx=3)
        tk.Button(frame_acciones2, text="📂 Importar Respaldo", bg="#d35400", fg="white", relief="flat", command=self.importar_respaldo).pack(side="left", padx=3)
        tk.Button(frame_acciones2, text="↺ Restaurar Fábrica", bg="#e67e22", fg="white", relief="flat", command=self.restaurar_fabrica).pack(side="left", padx=3)
        tk.Button(frame_acciones2, text="🔑 Cambiar Contraseña", bg="#8e44ad", fg="white", relief="flat", command=self.cambiar_clave_cliente).pack(side="right", padx=3)

        self.refrescar_lista()

    def refrescar_lista(self):
        self.listbox.delete(0, tk.END)
        for p in self.programas:
            self.listbox.insert(tk.END, f"  {p['nombre']} ({len(p.get('escaleta', []))} pasos)")

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

    def cambiar_clave_cliente(self):
        nueva = simpledialog.askstring("Seguridad", "Nueva contraseña de operador:", show="•", parent=self)
        if not nueva: return
        conf = simpledialog.askstring("Confirmar", "Repite la nueva contraseña:", show="•", parent=self)
        if nueva != conf:
            messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=self)
            return

        usr_guardado = "admin"
        if os.path.exists(ARCHIVO_SEGURIDAD_LOCAL):
            try:
                with open(ARCHIVO_SEGURIDAD_LOCAL, "r", encoding="utf-8") as f:
                    usr_guardado = json.load(f).get("usuario_hash", "")
            except Exception: pass

        with open(ARCHIVO_SEGURIDAD_LOCAL, "w", encoding="utf-8") as f:
            json.dump({"usuario_hash": usr_guardado, "clave_hash": calcular_hash(nueva)}, f)
        messagebox.showinfo("Éxito", "Contraseña cambiada correctamente.", parent=self)

    def exportar_respaldo(self):
        ruta_archivo = filedialog.asksaveasfilename(
            title="Guardar Respaldo de Programas",
            defaultextension=".json",
            filetypes=[("Archivo JSON de Respaldo", "*.json")],
            initialfile=f"Respaldo_Playout_{datetime.datetime.now().strftime('%Y%m%d')}.json",
            parent=self
        )
        if ruta_archivo:
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                json.dump(self.programas, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Respaldo Guardado", "Todas las escaletas se guardaron con éxito.", parent=self)

    def importar_respaldo(self):
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar Respaldo",
            filetypes=[("Archivo JSON", "*.json")],
            parent=self
        )
        if ruta_archivo:
            try:
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                if isinstance(datos, list):
                    self.programas.clear()
                    self.programas.extend(datos)
                    guardar_programas(self.programas)
                    self.refrescar_lista()
                    self.callback_actualizar_ui()
                    messagebox.showinfo("Éxito", "Respaldo importado correctamente.", parent=self)
                else:
                    messagebox.showerror("Error", "El archivo de respaldo no es válido.", parent=self)
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al importar:\n{e}", parent=self)

    def diagnostico_rutas(self):
        salida = limpiar_ruta(config_general.get("carpeta_salida", ""))
        errores = []

        if not os.path.exists(salida):
            errores.append(f"❌ Carpeta de salida inaccesible:\n   {salida}")
        else:
            errores.append(f"✔ Carpeta de Salida XML conectada.")

        carpetas_revisadas = set()
        for p in self.programas:
            for paso in p.get("escaleta", []):
                t = paso.get("tipo")
                ruta_revisar = paso.get("ruta") if t == "fijo" else paso.get("carpeta")
                if ruta_revisar and ruta_revisar not in carpetas_revisadas:
                    carpetas_revisadas.add(ruta_revisar)
                    if not os.path.exists(limpiar_ruta(ruta_revisar)):
                        errores.append(f"❌ Inaccesible ({p['nombre']}):\n   {ruta_revisar}")

        info_final = "\n\n".join(errores)
        messagebox.showinfo("Diagnóstico de Red y Discos", f"Estado de los medios:\n\n{info_final}", parent=self)

# ==============================================================================
# VENTANA DE SOPORTE TÉCNICO
# ==============================================================================
def abrir_soporte_tecnico():
    win_sop = tk.Toplevel(ventana)
    win_sop.title("Centro de Soporte Técnico y Licencia")
    win_sop.geometry("460x420")
    win_sop.resizable(False, False)
    win_sop.configure(bg="#2c3e50")

    tk.Label(win_sop, text="🛠 SOPORTE TÉCNICO OFICIAL", font=("Segoe UI", 13, "bold"), fg="#f1c40f", bg="#2c3e50").pack(pady=(15, 5))
    tk.Label(win_sop, text=f"Playout Generator Suite v{VERSION_LOCAL}", font=("Segoe UI", 9), fg="#bdc3c7", bg="#2c3e50").pack(pady=(0, 10))

    frame_box = tk.Frame(win_sop, bg="#34495e", padx=15, pady=10)
    frame_box.pack(fill="x", padx=25, pady=5)

    hwid = obtener_hwid()
    tk.Label(frame_box, text=f"Estación: {datos_remotos.get('cliente', 'No Registrado')}", font=("Segoe UI", 9, "bold"), fg="white", bg="#34495e").pack(anchor="w")
    tk.Label(frame_box, text=f"Vigencia: {datos_remotos.get('vence', 'N/A')} ({datos_remotos.get('dias_restantes', 0)} días restantes)", font=("Segoe UI", 9), fg="#2ecc71", bg="#34495e").pack(anchor="w")
    tk.Label(frame_box, text=f"ID de Equipo (HWID): {hwid[:18]}...", font=("Segoe UI", 8), fg="#bdc3c7", bg="#34495e").pack(anchor="w", pady=(5, 0))

    def copiar_hwid():
        ventana.clipboard_clear()
        ventana.clipboard_append(hwid)
        messagebox.showinfo("Copiado", "Tu ID de Equipo (HWID) se ha copiado al portapapeles.", parent=win_sop)

    tk.Button(frame_box, text="📋 Copiar ID de Equipo Completo", font=("Segoe UI", 8), bg="#2980b9", fg="white", relief="flat", command=copiar_hwid).pack(fill="x", pady=6)

    def contactar():
        contacto = datos_remotos.get("contacto", "")
        if "@" in contacto:
            webbrowser.open(f"mailto:{contacto}?subject=Soporte Playout - {datos_remotos.get('cliente')}")
        else:
            numero = contacto.replace("+", "").replace(" ", "").replace("-", "")
            msg = urllib.parse.quote(f"Hola, necesito soporte con mi licencia de Playout (Cliente: {datos_remotos.get('cliente')}, HWID: {hwid})")
            webbrowser.open(f"https://wa.me/{numero}?text={msg}")

    tk.Button(win_sop, text="💬 Contactar a Soporte Directo", font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white", relief="flat", cursor="hand2", command=contactar).pack(fill="x", padx=25, pady=12)

    frame_guia = tk.Frame(win_sop, bg="#2c3e50")
    frame_guia.pack(fill="both", expand=True, padx=25)
    tk.Label(frame_guia, text="Guía Rápida de Uso:", font=("Segoe UI", 9, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(anchor="w")
    tk.Label(frame_guia, text="1. Selecciona la carpeta donde tu Playout lee los XML arriba.", font=("Segoe UI", 8), fg="#bdc3c7", bg="#2c3e50").pack(anchor="w")
    tk.Label(frame_guia, text="2. Entra a 'Administrar' para armar las tandas y bloques.", font=("Segoe UI", 8), fg="#bdc3c7", bg="#2c3e50").pack(anchor="w")
    tk.Label(frame_guia, text="3. Presiona el botón del programa y cárgalo en Insta Playout.", font=("Segoe UI", 8), fg="#bdc3c7", bg="#2c3e50").pack(anchor="w")

# ==============================================================================
# PANEL PRINCIPAL (GUI)
# ==============================================================================
programas_activos = cargar_programas()
registro_hoy = cargar_registro()
botones_app = {}

def cambiar_carpeta_salida():
    nueva = filedialog.askdirectory(title="Selecciona la carpeta donde guardar los XML", initialdir=config_general.get("carpeta_salida"))
    if nueva:
        nueva_limpia = limpiar_ruta(nueva)
        config_general["carpeta_salida"] = nueva_limpia
        guardar_config_general(config_general)
        lbl_salida_path.config(text=nueva_limpia)
        messagebox.showinfo("Guardado", f"Carpeta de salida configurada en:\n{nueva_limpia}")

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
        if not messagebox.askyesno("Aviso", f"'{prog['nombre']}' YA SE GENERÓ HOY a las {hora}.\n\n¿Volver a generar?"):
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

    if not programas_activos:
        tk.Label(frame_scroll, text="No hay programas creados.\nEntra en '⚙ Administrar' para crear tu primer programa.", 
                 font=("Segoe UI", 10, "italic"), fg="#7f8c8d", bg="#f4f6f9").pack(pady=40)
        return

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
# SEGURIDAD Y LOGIN LOCAL
# ==============================================================================
intentos_restantes = INTENTOS_MAXIMOS

def validar_login(event=None):
    global intentos_restantes
    usr_ingresado = entry_usuario.get()
    pwd_ingresado = entry_clave.get()

    try:
        with open(ARCHIVO_SEGURIDAD_LOCAL, "r", encoding="utf-8") as f:
            cred = json.load(f)
        u_ok = cred.get("usuario_hash")
        p_ok = cred.get("clave_hash")
    except Exception:
        u_ok = calcular_hash("admin")
        p_ok = calcular_hash("1234")

    if calcular_hash(usr_ingresado) == u_ok and calcular_hash(pwd_ingresado) == p_ok:
        win_login.destroy()
        ventana.deiconify()
        comprobar_actualizacion_disponible(ventana)
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
# GESTIÓN DE LICENCIAMIENTO EN LA NUBE
# ==============================================================================
def iniciar_flujo_licenciamiento():
    hwid = obtener_hwid()
    clave_guardada = ""

    if os.path.exists(ARCHIVO_LICENCIA_LOCAL):
        try:
            with open(ARCHIVO_LICENCIA_LOCAL, "r", encoding="utf-8") as f:
                clave_guardada = f.read().strip()
        except Exception: pass

    if clave_guardada:
        try:
            params = urllib.parse.urlencode({"clave": clave_guardada, "hwid": hwid})
            url = f"{URL_SERVIDOR_LICENCIAS}?{params}"
            req = urllib.request.Request(url, headers={'User-Agent': 'PlayoutLicense/1.0'})
            with urllib.request.urlopen(req, timeout=12) as response:
                resp = json.loads(response.read().decode('utf-8'))

            if resp.get("valido"):
                datos_remotos["cliente"] = resp.get("cliente", "")
                datos_remotos["vence"] = resp.get("vence", "")
                
                # Cargar ajustes remotos desde Google Sheets
                ajustes = resp.get("ajustes", {})
                datos_remotos["contacto"] = ajustes.get("contacto", "+584120000000")
                datos_remotos["version_remota"] = ajustes.get("version", VERSION_LOCAL)
                datos_remotos["url_descarga"] = ajustes.get("url_descarga", "")
                datos_remotos["notas_actualizacion"] = ajustes.get("notas", "")

                actualizar_insignia_licencia()
                mostrar_login()
                return
            else:
                messagebox.showerror("Licencia Inválida", f"Acceso Denegado:\n\n{resp.get('mensaje')}")
                try: os.remove(ARCHIVO_LICENCIA_LOCAL)
                except Exception: pass
                pedir_activacion_licencia(hwid)
        except Exception:
            messagebox.showwarning("Sin Conexión", "No se pudo verificar la licencia con el servidor central.\nVerifica tu conexión a internet.")
            ventana.destroy()
    else:
        pedir_activacion_licencia(hwid)

def actualizar_insignia_licencia():
    vence = datos_remotos.get("vence", "")
    dias = calcular_dias_desde_fecha(vence)
    datos_remotos["dias_restantes"] = dias
    cli = datos_remotos.get("cliente", "Autorizado")
    
    if dias > 15:
        color = "#27ae60"  # Verde
        texto = f"✔ Licencia Activa ({cli}) | Vence en {dias} días ({vence})"
    elif dias > 3:
        color = "#e67e22"  # Naranja
        texto = f"⚠ Atención: Tu licencia vence en {dias} días ({cli})"
    else:
        color = "#c0392b"  # Rojo
        texto = f"🚨 URGENTE: Tu licencia vence en {dias} días. Contacta a soporte."

    lbl_licencia_info.config(text=texto, fg=color)

def pedir_activacion_licencia(hwid):
    win_act = tk.Toplevel(ventana)
    win_act.title("Activación de Licencia Playout")
    win_act.geometry("440x320")
    win_act.resizable(False, False)
    win_act.configure(bg="#1a252f")
    win_act.protocol("WM_DELETE_WINDOW", ventana.destroy)

    tk.Label(win_act, text="🔑 ACTIVACIÓN DE PRODUCTO", font=("Segoe UI", 13, "bold"), fg="#f1c40f", bg="#1a252f").pack(pady=(20, 10))
    tk.Label(win_act, text="Introduce la clave de licencia provista para tu estación:", font=("Segoe UI", 9), fg="#bdc3c7", bg="#1a252f").pack()

    entry_lic = tk.Entry(win_act, font=("Segoe UI", 12, "bold"), justify="center")
    entry_lic.pack(fill="x", padx=40, pady=(15, 5))
    entry_lic.focus()

    lbl_estado_act = tk.Label(win_act, text="", font=("Segoe UI", 8, "bold"), fg="#e74c3c", bg="#1a252f")
    lbl_estado_act.pack(pady=4)

    def ejecutar_activacion():
        clave = entry_lic.get().strip()
        if not clave:
            lbl_estado_act.config(text="Por favor escribe una clave.")
            return

        lbl_estado_act.config(text="Validando con Google Cloud...", fg="#3498db")
        win_act.update()

        try:
            params = urllib.parse.urlencode({"clave": clave, "hwid": hwid})
            url = f"{URL_SERVIDOR_LICENCIAS}?{params}"
            req = urllib.request.Request(url, headers={'User-Agent': 'PlayoutLicense/1.0'})
            with urllib.request.urlopen(req, timeout=12) as response:
                resp = json.loads(response.read().decode('utf-8'))

            if resp.get("valido"):
                with open(ARCHIVO_LICENCIA_LOCAL, "w", encoding="utf-8") as f:
                    f.write(clave)
                
                datos_remotos["cliente"] = resp.get("cliente", "")
                datos_remotos["vence"] = resp.get("vence", "")

                messagebox.showinfo("¡Licencia Activada!", f"Estación: {datos_remotos['cliente']}\nVigencia: {datos_remotos['vence']}\n\nAhora crea tu Usuario y Contraseña de operador local.", parent=win_act)
                win_act.destroy()
                pedir_creacion_cuenta_local()
            else:
                lbl_estado_act.config(text=resp.get("mensaje", "Clave no válida."), fg="#e74c3c")
        except Exception:
            lbl_estado_act.config(text="Error de conexión con el servidor central.", fg="#e74c3c")

    tk.Button(win_act, text="Activar Playout", font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white", relief="flat", cursor="hand2", command=ejecutar_activacion).pack(fill="x", padx=40, pady=15)

def pedir_creacion_cuenta_local():
    win_usr = tk.Toplevel(ventana)
    win_usr.title("Crear Cuenta Local")
    win_usr.geometry("380x300")
    win_usr.resizable(False, False)
    win_usr.configure(bg="#2c3e50")
    win_usr.protocol("WM_DELETE_WINDOW", ventana.destroy)

    tk.Label(win_usr, text="👤 CREA TU CUENTA LOCAL", font=("Segoe UI", 12, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=(20, 10))

    tk.Label(win_usr, text="Usuario:", font=("Segoe UI", 9), fg="#bdc3c7", bg="#2c3e50").pack(anchor="w", padx=45)
    e_u = tk.Entry(win_usr, font=("Segoe UI", 11))
    e_u.pack(padx=45, fill="x", pady=2)
    e_u.insert(0, "admin")

    tk.Label(win_usr, text="Contraseña:", font=("Segoe UI", 9), fg="#bdc3c7", bg="#2c3e50").pack(anchor="w", padx=45, pady=(8, 0))
    e_p = tk.Entry(win_usr, show="•", font=("Segoe UI", 11))
    e_p.pack(padx=45, fill="x", pady=2)

    def guardar_cuenta():
        u = e_u.get().strip()
        p = e_p.get().strip()
        if not u or not p:
            messagebox.showwarning("Atención", "Usuario y Contraseña no pueden estar vacíos.", parent=win_usr)
            return

        with open(ARCHIVO_SEGURIDAD_LOCAL, "w", encoding="utf-8") as f:
            json.dump({"usuario_hash": calcular_hash(u), "clave_hash": calcular_hash(p)}, f)

        messagebox.showinfo("Configuración Completa", "¡Cuenta creada con éxito!\nAhora inicia sesión.", parent=win_usr)
        win_usr.destroy()
        actualizar_insignia_licencia()
        mostrar_login()

    tk.Button(win_usr, text="Guardar y Continuar", font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white", relief="flat", cursor="hand2", command=guardar_cuenta).pack(fill="x", padx=45, pady=20)

# ==============================================================================
# VENTANA PRINCIPAL (INICIALIZACIÓN)
# ==============================================================================
ventana = tk.Tk()
ventana.title(f"Panel Playout Generator Suite v{VERSION_LOCAL}")
ventana.geometry("580x740")
ventana.resizable(False, False)
ventana.configure(bg="#f4f6f9")
ventana.withdraw()

# Barra Superior
frame_top = tk.Frame(ventana, bg="#f4f6f9")
frame_top.pack(fill="x", padx=20, pady=(12, 0))

tk.Label(frame_top, text="Generador de Contenido", font=("Segoe UI", 14, "bold"), bg="#f4f6f9", fg="#2c3e50").pack(side="left")

btn_lock = tk.Button(frame_top, text="🔒 Bloquear", font=("Segoe UI", 8, "bold"), bg="#e67e22", fg="white", relief="flat", cursor="hand2", command=bloquear_pantalla)
btn_lock.pack(side="right", padx=2)

btn_admin = tk.Button(frame_top, text="⚙ Administrar", font=("Segoe UI", 8, "bold"), bg="#34495e", fg="white", relief="flat", cursor="hand2", 
                      command=lambda: VentanaAdminProgramas(ventana, programas_activos, reconstruir_interfaz_botones))
btn_admin.pack(side="right", padx=2)

btn_sop = tk.Button(frame_top, text="🛠 Soporte", font=("Segoe UI", 8, "bold"), bg="#2980b9", fg="white", relief="flat", cursor="hand2", command=abrir_soporte_tecnico)
btn_sop.pack(side="right", padx=2)

# Insignia de Licencia Dinámica
lbl_licencia_info = tk.Label(ventana, text="Licencia: Verificando...", font=("Segoe UI", 8, "bold"), bg="#f4f6f9", fg="#27ae60")
lbl_licencia_info.pack(pady=(2, 4))

# Selector de Carpeta de Salida XML
frame_salida = tk.Frame(ventana, bg="#ecf0f1", padx=10, pady=5)
frame_salida.pack(fill="x", padx=20, pady=(0, 10))

tk.Label(frame_salida, text="📁 Salida XML:", font=("Segoe UI", 8, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(side="left")
lbl_salida_path = tk.Label(frame_salida, text=limpiar_ruta(config_general.get("carpeta_salida")), font=("Segoe UI", 8), bg="#ecf0f1", fg="#7f8c8d", anchor="w")
lbl_salida_path.pack(side="left", padx=5, fill="x", expand=True)

tk.Button(frame_salida, text="Cambiar", font=("Segoe UI", 7, "bold"), bg="#bdc3c7", relief="flat", command=cambiar_carpeta_salida).pack(side="right")

btn_all = tk.Button(ventana, text="⚡ EJECUTAR TODOS LOS PROGRAMAS", font=("Segoe UI", 11, "bold"), bg="#8e44ad", fg="white", relief="flat", cursor="hand2", height=2, command=ejecutar_todos)
btn_all.pack(fill="x", padx=20, pady=(0, 8))

tk.Frame(ventana, height=2, bg="#dcdde1").pack(fill="x", padx=20, pady=(0, 8))

canvas = tk.Canvas(ventana, bg="#f4f6f9", highlightthickness=0)
scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
frame_scroll = tk.Frame(canvas, bg="#f4f6f9")

frame_scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas_window = canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
canvas.bind('<Configure>', lambda event: canvas.itemconfig(canvas_window, width=event.width))
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="top", fill="both", expand=True, padx=(20, 5))
scrollbar.pack(side="right", fill="y", before=canvas)

lbl_estado = tk.Label(ventana, text="Listo para ejecutar", font=("Segoe UI", 9, "italic"), bg="#f4f6f9", fg="#7f8c8d")
lbl_estado.pack(side="bottom", pady=4)

tk.Button(ventana, text="Cerrar Aplicación", font=("Segoe UI", 9), bg="#bdc3c7", fg="#2c3e50", relief="flat", cursor="hand2", command=ventana.destroy).pack(side="bottom", pady=2)

reconstruir_interfaz_botones()

# Iniciar validación con el servidor de licencias en la nube
iniciar_flujo_licenciamiento()
ventana.mainloop()
