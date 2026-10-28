import os
import random
import datetime
import xml.etree.ElementTree as ET

# 1. Configuración de rutas (Todo centralizado en la red \\aire2)
RUTA_JUVENTUD_ACTIVA = r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\Juventud Activa"
CARPETA_DESTINO = r"D:\Luis\1 Programacion diaria\Programacion del dia"

# Rutas exactas de los elementos institucionales y cortinillas en \\aire2
PATH_AHORA_SIGUE = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\AHORA SIGUE 2020\JUVENTUD ACTIVA.mpg"
PATH_LOGO_MUSICALIZADO = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\BTV LOGO MUSICALIZADO 2020\BTV LOGO MUSICALIZADO 2020.mpg"
PATH_A_CONTINUACION = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\A CONTINUACION 2020\JUVENTUD ACTIVA.mpg"
PATH_HORARIO = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\TIPOS DE HORARIOS 2020\HORARIO TODOUSUARIO 2020.mpg"
PATH_PROGRAMA_RECREATIVO = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\TIPOS DE PROGRAMAS 2020\PROGRAMA RECREATIVO  2020.mpg"

# Elementos específicos de Juventud Activa según la estructura de red
PATH_PRESENTA = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\JUVENTUD ACTIVA 2016\01_BTV PRESENTA JUVENTUD ACTIVA.mpg"
PATH_YA_REGRESAMOS = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\JUVENTUD ACTIVA 2016\02_YA REGRESA JUVENTUD ACTIVA.mpg"
PATH_REGRESAMOS_CON = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\JUVENTUD ACTIVA 2016\03_CONTINUA  JUVENTUD ACTIVA.mpg"
PATH_PRESENTO = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\JUVENTUD ACTIVA 2016\04_BTV PRESENTO JUVENTUD ACTIVA.mpg"

# Duraciones exactas en segundos de cada institucional
DURACIONES_FIJAS = {
    PATH_AHORA_SIGUE: 7.974633,
    PATH_LOGO_MUSICALIZADO: 15.1151,
    PATH_A_CONTINUACION: 8.008,
    PATH_HORARIO: 20.8208,
    PATH_PROGRAMA_RECREATIVO: 3.737067,
    PATH_PRESENTA: 16.549867,
    PATH_YA_REGRESAMOS: 15.048367,
    PATH_REGRESAMOS_CON: 15.048367,
    PATH_PRESENTO: 16.549867
}

# Obtener la fecha actual en formato Día-Mes-Año
FECHA_HOY = datetime.datetime.now().strftime("%d-%m-%Y")
NOMBRE_ARCHIVO = f"4.-juventud activa {FECHA_HOY}.xml"
ARCHIVO_SALIDA = os.path.join(CARPETA_DESTINO, NOMBRE_ARCHIVO)

def generar_xml_juventud_activa():
    if not os.path.exists(CARPETA_DESTINO):
        os.makedirs(CARPETA_DESTINO)

    # 2. Recolectar archivos multimedia en la red de Juventud Activa
    videos_musica = []
    if os.path.exists(RUTA_JUVENTUD_ACTIVA):
        for raiz, _, archivos in os.walk(RUTA_JUVENTUD_ACTIVA):
            for archivo in archivos:
                if archivo.lower().endswith(('.mp4', '.mpg', '.avi', '.mkv', '.mov', '.mp3', '.wav', '.aac')):
                    ruta_completa = os.path.join(raiz, archivo)
                    videos_musica.append(ruta_completa)
    else:
        print(f"Error: No se puede acceder a la ruta de red: {RUTA_JUVENTUD_ACTIVA}")
        return

    if not videos_musica:
        print("No se encontraron archivos en la ruta de red de Juventud Activa.")
        return

    # Mezclar aleatoriamente para garantizar variedad diaria
    random.shuffle(videos_musica)
    iter_musica = iter(videos_musica)

    # 3. Estructurar el XML para Insta Playout (IPO)
    root = ET.Element('m_config', path=ARCHIVO_SALIDA)
    ET.SubElement(root, 'video')
    ET.SubElement(root, 'audio', track_split='')

    playlist_items = []

    def agregar_item(path_archivo):
        duracion = DURACIONES_FIJAS.get(path_archivo, 10.0)
        playlist_items.append((path_archivo, duracion))

    def agregar_bloque_musica(duracion_objetivo_minutos):
        nonlocal iter_musica
        segundos_objetivo = duracion_objetivo_minutos * 60
        acumulado = 0
        duracion_estimada_video = 210.0  # 3.5 minutos promedio por video musical

        while acumulado < segundos_objetivo:
            try:
                video_path = next(iter_musica)
            except StopIteration:
                random.shuffle(videos_musica)
                iter_musica = iter(videos_musica)
                video_path = next(iter_musica)
            
            playlist_items.append((video_path, duracion_estimada_video))
            acumulado += duracion_estimada_video

    # --- ESTRUCTURA EXACTA CON LOS 2 BLOQUES MUSICALES ---
    
    # 1. Secuencia de inicio exacta
    agregar_item(PATH_AHORA_SIGUE)
    agregar_item(PATH_LOGO_MUSICALIZADO)
    agregar_item(PATH_A_CONTINUACION)
    agregar_item(PATH_HORARIO)
    agregar_item(PATH_PROGRAMA_RECREATIVO)
    agregar_item(PATH_PRESENTA)

    # 2. Bloque Musical 1 (aprox. 55 min - la mitad del programa)
    agregar_bloque_musica(55)

    # 3. Pausa intermedia única (Ya regresamos + Doble Logo + Regresamos con)
    agregar_item(PATH_YA_REGRESAMOS)
    agregar_item(PATH_LOGO_MUSICALIZADO)
    agregar_item(PATH_LOGO_MUSICALIZADO)
    agregar_item(PATH_REGRESAMOS_CON)

    # 4. Bloque Musical 2 final (para completar la otra mitad de la hora/programa)
    agregar_bloque_musica(55)

    # 5. Cierre definitivo del programa (Presentó + Logo institucional final)
    agregar_item(PATH_PRESENTO)
    agregar_item(PATH_LOGO_MUSICALIZADO)

    # 4. Escribir todos los elementos en el XML
    for path_archivo, duracion in playlist_items:
        nodo_file = ET.SubElement(root, 'file', {
            'in': '0.0',
            'path': path_archivo,
            'duration': str(duracion),
            'loop': 'false'
        })
        
        ET.SubElement(nodo_file, 'video', width='1280', height='720', rate='29.97003', aspect_ratio='16:9')
        ET.SubElement(nodo_file, 'audio', channels='2', rate='48000', bits='16')

    # 5. Guardar el archivo XML utilizando cp1252 para conservar acentos y eñes correctamente
    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    tree.write(ARCHIVO_SALIDA, encoding='cp1252', xml_declaration=False)
    
    print(f"¡Programación de Juventud Activa con 2 bloques generada con éxito!")
    print(f"Archivo guardado en: {ARCHIVO_SALIDA}")

if __name__ == "__main__":
    generar_xml_juventud_activa()
