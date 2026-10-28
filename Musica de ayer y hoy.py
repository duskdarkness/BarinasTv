import os
import random
import datetime
import xml.etree.ElementTree as ET

# 1. Configuración de rutas (Todo centralizado en la red \\aire2)
RUTA_AYER_Y_HOY = r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\mUSICA DE aYER y hOY"
RUTA_FREECOVER = r"\\aire2\BASE DE DATOS 2022\PROGRAMACION\freecover"
CARPETA_DESTINO = r"D:\Luis\1 Programacion diaria\Programacion del dia"

# Rutas exactas de los elementos institucionales y cortinillas en \\aire2
PATH_AHORA_SIGUE = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\AHORA SIGUE 2020\MUSICA DE AYER Y HOY.mpg"
PATH_LOGO_MUSICALIZADO = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\BTV LOGO MUSICALIZADO 2020\BTV LOGO MUSICALIZADO 2020.mpg"
PATH_A_CONTINUACION = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\A CONTINUACION 2020\MUSICA DE AYER Y HOY.mpg"
PATH_HORARIO = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\TIPOS DE HORARIOS 2020\HORARIO SUPERVISADO 2020.mpg"
PATH_PROGRAMA_RECREATIVO = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA\TIPOS DE PROGRAMAS 2020\PROGRAMA RECREATIVO  2020.mpg"

# Elementos específicos del programa según la estructura de red
PATH_PRESENTA = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4"
PATH_YA_REGRESAMOS = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4"
PATH_REGRESAMOS_CON = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4"
PATH_PRESENTO = r"\\aire2\BASE DE DATOS 2022\ESCUDERIA 2022\ESCUDERIA PROGRAMAS 2017\Musica de Ayer y Hoy\MUSICA DE AYER Y HOY.mp4"

# Duraciones exactas en segundos de cada institucional
DURACIONES_FIJAS = {
    PATH_AHORA_SIGUE: 7.974633,
    PATH_LOGO_MUSICALIZADO: 15.1151,
    PATH_A_CONTINUACION: 8.008,
    PATH_HORARIO: 20.8208,
    PATH_PROGRAMA_RECREATIVO: 3.737067,
    PATH_PRESENTA: 7.7077,
    PATH_YA_REGRESAMOS: 7.7077,
    PATH_REGRESAMOS_CON: 7.7077,
    PATH_PRESENTO: 7.7077
}

# Obtener la fecha actual en formato Día-Mes-Año
FECHA_HOY = datetime.datetime.now().strftime("%d-%m-%Y")
NOMBRE_ARCHIVO = f"5.-musica de ayer y hoy {FECHA_HOY}.xml"
ARCHIVO_SALIDA = os.path.join(CARPETA_DESTINO, NOMBRE_ARCHIVO)

def recolectar_videos(ruta_carpeta):
    videos = []
    if os.path.exists(ruta_carpeta):
        for raiz, _, archivos in os.walk(ruta_carpeta):
            for archivo in archivos:
                if archivo.lower().endswith(('.mp4', '.mpg', '.avi', '.mkv', '.mov', '.mp3', '.wav', '.aac')):
                    videos.append(os.path.join(raiz, archivo))
    else:
        print(f"Advertencia: No se puede acceder a la ruta: {ruta_carpeta}")
    return videos

def generar_xml_ayer_y_hoy():
    if not os.path.exists(CARPETA_DESTINO):
        os.makedirs(CARPETA_DESTINO)

    # 2. Recolectar videos de ambas carpetas por separado
    lista_ayer_hoy = recolectar_videos(RUTA_AYER_Y_HOY)
    lista_freecover = recolectar_videos(RUTA_FREECOVER)

    if not lista_ayer_hoy:
        print(f"Error: No se encontraron archivos en la carpeta de Ayer y Hoy.")
        return
    if not lista_freecover:
        print(f"Error: No se encontraron archivos en la carpeta de Freecover.")
        return

    # Mezclar ambas listas de forma independiente
    random.shuffle(lista_ayer_hoy)
    random.shuffle(lista_freecover)

    iter_ayer_hoy = iter(lista_ayer_hoy)
    iter_freecover = iter(lista_freecover)

    # 3. Estructurar el XML para Insta Playout (IPO)
    root = ET.Element('m_config', path=ARCHIVO_SALIDA)
    ET.SubElement(root, 'video')
    ET.SubElement(root, 'audio', track_split='')

    playlist_items = []

    def agregar_item(path_archivo):
        duracion = DURACIONES_FIJAS.get(path_archivo, 10.0)
        playlist_items.append((path_archivo, duracion))

    def agregar_bloque_desde_iterador(iterador_fuente, lista_fuente, duracion_objetivo_minutos):
        segundos_objetivo = duracion_objetivo_minutos * 60
        acumulado = 0
        duracion_estimada_video = 210.0  # 3.5 minutos promedio por video musical

        while acumulado < segundos_objetivo:
            try:
                video_path = next(iterador_fuente)
            except StopIteration:
                random.shuffle(lista_fuente)
                # Creamos un nuevo iterador si se agota
                nonlocal iter_ayer_hoy, iter_freecover
                if iterador_fuente is iter_ayer_hoy:
                    iter_ayer_hoy = iter(lista_fuente)
                    video_path = next(iter_ayer_hoy)
                else:
                    iter_freecover = iter(lista_fuente)
                    video_path = next(iter_freecover)
            
            playlist_items.append((video_path, duracion_estimada_video))
            acumulado += duracion_estimada_video

    # --- ESTRUCTURA EXACTA CON LOS 4 BLOQUES MUSICALES ---
    
    # 1. Secuencia de inicio exacta
    agregar_item(PATH_AHORA_SIGUE)
    agregar_item(PATH_LOGO_MUSICALIZADO)
    agregar_item(PATH_A_CONTINUACION)
    agregar_item(PATH_HORARIO)
    agregar_item(PATH_PROGRAMA_RECREATIVO)
    agregar_item(PATH_PRESENTA)

    # 2. Bloque Musical 1 (Usa carpeta Música de Ayer y Hoy)
    agregar_bloque_desde_iterador(iter_ayer_hoy, lista_ayer_hoy, 21)

    # 3. Primera tanda intermedia (Ya regresamos + Doble Logo + Regresamos con)
    agregar_item(PATH_YA_REGRESAMOS)
    agregar_item(PATH_LOGO_MUSICALIZADO)
    agregar_item(PATH_LOGO_MUSICALIZADO)
    agregar_item(PATH_REGRESAMOS_CON)

    # 4. Bloque Musical 2 (Usa carpeta Música de Ayer y Hoy)
    agregar_bloque_desde_iterador(iter_ayer_hoy, lista_ayer_hoy, 21)

    # 5. Segunda tanda intermedia (Ya regresamos + Doble Logo + Regresamos con)
    agregar_item(PATH_YA_REGRESAMOS)
    agregar_item(PATH_LOGO_MUSICALIZADO)
    agregar_item(PATH_LOGO_MUSICALIZADO)
    agregar_item(PATH_REGRESAMOS_CON)

    # 6. Bloque Musical 3 (Usa carpeta Freecover)
    agregar_bloque_desde_iterador(iter_freecover, lista_freecover, 21)

    # 7. Tercera tanda intermedia (Ya regresamos + Doble Logo + Regresamos con)
    agregar_item(PATH_YA_REGRESAMOS)
    agregar_item(PATH_LOGO_MUSICALIZADO)
    agregar_item(PATH_LOGO_MUSICALIZADO)
    agregar_item(PATH_REGRESAMOS_CON)

    # 8. Bloque Musical 4 final (Usa carpeta Freecover para completar las 2 horas)
    agregar_bloque_desde_iterador(iter_freecover, lista_freecover, 22)

    # 9. Cierre definitivo del programa (Presentó + Logo institucional final)
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
    
    print(f"¡Programación de Música de Ayer y Hoy generada con éxito!")
    print(f"Archivo guardado en: {ARCHIVO_SALIDA}")

if __name__ == "__main__":
    generar_xml_ayer_y_hoy()
