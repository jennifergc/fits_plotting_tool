#! /usr/bin/env casa

import os
import sys
import shutil
import numpy as np
from casatasks import importfits, exportfits, imstat, immath

"""
Script para generar contornos en imágenes FITS utilizando CASA.

Uso:
    casa --nologger --nogui -c script_contornos.py <fits_file> <moment> <method> <sigma (opcional)> <multipliers> <output_fits>

Argumentos:
    <fits_file>:     Ruta del archivo FITS de entrada.
    <moment>:        Momento de la imagen (0, 1 o 2).
    <method>:        Método para calcular los niveles de contorno:
                     - "sigma": Usa la desviación estándar (RMS) y multipliers ingresados por el usuario.
                     - "imax": Usa el valor máximo de la imagen y factores predefinidos.
    <sigma>:         Valor de sigma o "auto" para calcularlo a partir del RMS (solo en momentos 0 y 2).
    <multipliers>:   Valores de contorno separados por comas (obligatorio en método "sigma", opcional en "imax").
    <output_fits>:   Nombre del archivo de salida con los contornos generados.

Ejemplos de uso:
    1. Usando sigma en momento 0:
       casa --nologger --nogui -c script_contornos.py imagen.fits 0 sigma 0.005 "3,5,10,20" salida_sigma_m0.fits
    
    2. Usando I_max en momento 2:
       casa --nologger --nogui -c script_contornos.py imagen.fits 2 imax auto "" salida_imax_m2.fits
    
    3. Usando multipliers directos en momento 1:
       casa --nologger --nogui -c script_contornos.py imagen.fits 1 direct auto "5,10,15,20" salida_multipliers_m1.fits

    4. Mostrar esta ayuda:
       casa --nologger --nogui -c script_contornos.py --help
"""

# Leer argumentos de entrada
if len(sys.argv) < 7:
    print("Uso: casa --nologger --nogui -c script_contornos.py <fits_file> <moment> <method> <sigma (opcional)> <multipliers> <output_fits>")
    sys.exit(1)

fits_file = sys.argv[1]
moment = int(sys.argv[2])  # Momento 0, 1 o 2
method = sys.argv[3].lower()  # Método: "sigma" o "imax"
sigma_value_arg = sys.argv[4]  # Corresponde al valor de sigma
multipliers_arg = sys.argv[5]  # Corresponde a los valores de contorno si se usa sigma
output_fits = sys.argv[6]  # Archivo de salida

print(f"Método seleccionado: {method}", '\n')
print(f"Multipliers recibidos: {multipliers_arg}", '\n')
print(f"Argumentos recibidos: {sys.argv}", '\n')

# Definir nombres de archivos intermedios
casa_image = 'imagen_casa.im'
contour_image = 'contornos.im'

# Eliminar directorios temporales si existen
for directory in [casa_image, contour_image]:
    if os.path.exists(directory):
        shutil.rmtree(directory)
        print(f"Directorio {directory} eliminado para evitar conflictos de sobrescritura.", '\n')

# Eliminar archivo de salida si existe
if os.path.exists(output_fits):
    os.remove(output_fits)
    print(f"Archivo {output_fits} eliminado para evitar conflictos de sobrescritura.", '\n')

# Importar la imagen FITS a un formato de CASA
importfits(fits_file, imagename=casa_image, overwrite=True)

# Obtener estadísticas de la imagen
stats = imstat(imagename=casa_image)

# Determinar sigma o I_max según el método
sigma_value = None
contour_levels = []

if method == "sigma":
    if moment in [0, 2]:
        if sigma_value_arg.lower() == "auto":
            sigma_value = stats['rms'][0] if 'rms' in stats else 1.0  # Estimación por RMS si no se da sigma
            print(f"Sigma estimado: {sigma_value}", '\n')
        else:
            sigma_value = float(sigma_value_arg)  # Usa el valor ingresado por el usuario
        
        # Calcular niveles de contorno con multipliers
        try:
            multipliers = list(map(float, multipliers_arg.split(',')))
            contour_levels = [sigma_value * m for m in multipliers]
        except ValueError:
            print(f"Error: No se pudieron convertir los valores de contorno correctamente. Revisar entrada: {multipliers_arg}", '\n')
            sys.exit(1)
    else:
        print("Error: El método 'sigma' solo es válido para momentos 0 y 2.", '\n')
        sys.exit(1)

elif method == "imax":
    i_max = stats['max'][0]
    factors = [0.1, 0.2, 0.4, 0.5, 0.7, 0.9]
    contour_levels = [f * i_max for f in factors]
    print(f"Niveles de contorno basados en I_max={i_max}: {contour_levels}", '\n')

elif moment == 1:
    # Usar los multipliers ingresados directamente
    try:
        contour_levels = list(map(float, multipliers_arg.split(',')))
        print(f"Niveles de contorno ingresados por el usuario: {contour_levels}")
    except ValueError:
        print(f"Error: No se pudieron convertir los valores de contorno correctamente. Revisar entrada: {multipliers_arg}", '\n')
        sys.exit(1)

else:
    print("Error: Método desconocido. Use 'sigma' o 'imax'.", '\n')
    sys.exit(1)



# Generar contornos con immath
contour_expr = f"iif({casa_image} > {contour_levels[0]}, 1, 0)"
for level in contour_levels[1:]:
    contour_expr += f" + iif({casa_image} > {level}, 1, 0)"

immath(imagename=casa_image, expr=contour_expr, outfile=contour_image)

# Exportar la imagen de contornos a FITS con el nombre especificado
exportfits(imagename=contour_image, fitsimage=output_fits, overwrite=True)

print(f"Proceso completado: Contornos generados para momento {moment} con método {method} y niveles {contour_levels} <3", '\n')

#EJEMPLOS DE USO
#casa --nologger --nogui -c script_contornos.py imagen.fits 0 sigma 0.001 "3,5,10,20" salida.fits
#casa --nologger --nogui -c script_contornos.py imagen.fits 0 imax auto "" salida.fits

