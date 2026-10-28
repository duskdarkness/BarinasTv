import os
import random
import datetime
import xml.etree.ElementTree as ET

# 1. Configuración de rutas
RUTA_SENTIR_LLANERO = r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Sentir Llanero"
CARPETA_DESTINO = r"D:\Luis\1 Programacion diaria\Programacion del dia"

# Archivo fijo de cierre institucional con la ruta correcta
CIERRE_LOGO_MUSICALIZADO = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\BTV LOGO MUSICALIZADO 2020\BTV LOGO MUSICALIZADO 2020.mpg"
DURACION_CIERRE = 15.1151  # Duración exacta en segundos

# Obtener la fecha actual en formato Día-Mes-Año
FECHA_HOY = datetime.datetime.now().strftime("%d-%m-%Y")
NOMBRE_ARCHIVO = f"1.-despertando con barinas {FECHA_HOY}.xml"
ARCHIVO_SALIDA = os.path.join(CARPETA_DESTINO, NOMBRE_ARCHIVO)

# 115 minutos totales, restando el cierre para clavar el tiempo exacto
DURACION_OBJETIVO_SEGUNDOS = (115 * 60) - DURACION_CIERRE  

def generar_xml_playout():
    if not os.path.exists(CARPETA_DESTINO):
        os.makedirs(CARPETA_DESTINO)

    # 2. Recolectar audios/videos en la carpeta de red y subcarpetas
    canciones = []
    if os.path.exists(RUTA_SENTIR_LLANERO):
        for raiz, _, archivos in os.walk(RUTA_SENTIR_LLANERO):
            for archivo in archivos:
                if archivo.lower().endswith(('.mp3', '.wav', '.mpg', '.mp4', '.aac')):
                    ruta_completa = os.path.join(raiz, archivo)
                    canciones.append(ruta_completa)
    else:
        print(f"Error: No se puede acceder a la ruta de red: {RUTA_SENTIR_LLANERO}")
        return

    if not canciones:
        print("No se encontraron archivos de audio en la ruta de red especificada.")
        return

    # 3. Mezclar aleatoriamente las canciones
    random.shuffle(canciones)

    # 4. Estructurar el XML para Insta Playout (IPO)
    root = ET.Element('m_config', path=ARCHIVO_SALIDA)
    ET.SubElement(root, 'video')
    ET.SubElement(root, 'audio', track_split='')

    tiempo_acumulado = 0
    duracion_estimada = 210.0  # 3.5 minutos en promedio por tema musical

    playlist_items = []

    # Seleccionar canciones hasta llenar el bloque principal
    for item in canciones:
        if tiempo_acumulado + duracion_estimada > DURACION_OBJETIVO_SEGUNDOS:
            break
        playlist_items.append((item, duracion_estimada))
        tiempo_acumulado += duracion_estimada

    # AGREGAR EL LOGO DE CIERRE OBLIGATORIAMENTE AL FINAL
    playlist_items.append((CIERRE_LOGO_MUSICALIZADO, DURACION_CIERRE))

    # Escribir todos los elementos en el XML
    for path_archivo, duracion in playlist_items:
        nodo_file = ET.SubElement(root, 'file', {
            'in': '0.0',
            'path': path_archivo,
            'duration': str(duracion),
            'loop': 'false'
        })
        
        ET.SubElement(nodo_file, 'video', width='1280', height='720', rate='29.97003', aspect_ratio='16:9')
        ET.SubElement(nodo_file, 'audio', channels='2', rate='48000', bits='16')

    # 5. Guardar el archivo XML utilizando la codificación nativa cp1252 de Windows
    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    tree.write(ARCHIVO_SALIDA, encoding='cp1252', xml_declaration=False)
    
    print(f"¡Programación de Despertando con Barinas lista con la ruta correcta!")
    print(f"Archivo generado: {NOMBRE_ARCHIVO}")

if __name__ == "__main__":
    generar_xml_playout()
