import os
import sys
import shutil
import subprocess

# Asegurar la ruta de trabajo en la misma carpeta del script
CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
os.chdir(CARPETA_ACTUAL)

print("=" * 65)
print("     COMPILADOR COMERCIAL A UN SOLO ARCHIVO .EXE")
print("=" * 65)
print(f"Carpeta de trabajo: {CARPETA_ACTUAL}\n")

archivo_py = os.path.join(CARPETA_ACTUAL, "Programacion.py")

if not os.path.exists(archivo_py):
    print(f"[!] ERROR: No se encuentra 'Programacion.py' en:")
    print(f"    {archivo_py}")
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

# 1. Comprobar e instalar PyInstaller si falta
try:
    import PyInstaller
except ImportError:
    print("[+] Instalando herramienta de empaquetado (PyInstaller)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

# 2. Proceso de compilación
nombre_exe = "Panel_Playout"
print(f"[+] Compilando '{archivo_py}' en '{nombre_exe}.exe'...")
print("    Por favor espera un momento mientras se empaqueta todo...")

comando = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",               # Empaqueta TODO en un solo archivo ejecutable
    "--noconsole",             # Elimina la consola negra de Windows
    "--name", nombre_exe,      # Nombre final del programa
    "--clean",                 # Limpia caché previa
    archivo_py
]

resultado = subprocess.run(comando)

if resultado.returncode == 0:
    origen_exe = os.path.join(CARPETA_ACTUAL, "dist", f"{nombre_exe}.exe")
    destino_exe = os.path.join(CARPETA_ACTUAL, f"{nombre_exe}.exe")

    # Mover el .exe a la carpeta principal
    if os.path.exists(destino_exe):
        try:
            os.remove(destino_exe)
        except Exception:
            pass

    if os.path.exists(origen_exe):
        shutil.move(origen_exe, destino_exe)

    # Limpiar residuos y carpetas temporales
    shutil.rmtree(os.path.join(CARPETA_ACTUAL, "build"), ignore_errors=True)
    shutil.rmtree(os.path.join(CARPETA_ACTUAL, "dist"), ignore_errors=True)
    spec = os.path.join(CARPETA_ACTUAL, f"{nombre_exe}.spec")
    if os.path.exists(spec):
        try:
            os.remove(spec)
        except Exception:
            pass

    print("\n" + "=" * 65)
    print("  ¡COMPILACIÓN EXITOSA!")
    print(f"  Tu ejecutable comercial está listo en:")
    print(f"  -> {destino_exe}")
    print("=" * 65)
else:
    print("\n[!] Hubo un error durante la compilación con PyInstaller.")

input("\nPresiona la tecla ENTER para finalizar...")
