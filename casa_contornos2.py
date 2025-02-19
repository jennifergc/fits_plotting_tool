#! /usr/bin/env casa

import os
import sys
import shutil
from casatasks import importfits, exportfits, immath

# Leer argumentos de entrada
if len(sys.argv) != 6:
    print("Uso: casa --nologger --nogui -c script_contornos.py <fits_file> <moment> <sigma> <multipliers> <output_fits>")
    sys.exit(1)

fits_file = sys.argv[1]
moment = int(sys.argv[2])  # Momento 0, 1 o 2
sigma_value = float(sys.argv[3])
multipliers = list(map(float, sys.argv[4].split(',')))
output_fits = sys.argv[5]

# Definir nombres de archivos intermedios
casa_image = 'imagen_casa.im'
contour_image = 'contornos.im'

# Eliminar directorios temporales si existen
for directory in [casa_image, contour_image]:
    if os.path.exists(directory):
        shutil.rmtree(directory)
        print(f"Directorio {directory} eliminado para evitar conflictos de sobrescritura.")

# Eliminar archivo de salida si existe
if os.path.exists(output_fits):
    os.remove(output_fits)
    print(f"Archivo {output_fits} eliminado para evitar conflictos de sobrescritura.")

# Importar la imagen FITS a un formato de CASA
importfits(fits_file, imagename=casa_image, overwrite=True)

# Calcular niveles de contorno según el momento
if moment == 0 or moment == 2:
    # Momento 0 o 2: Basado en sigma dado por el usuario
    contour_levels = [sigma_value * m for m in multipliers]
elif moment == 1:
    # Momento 1: Basado en valores absolutos de velocidad
    contour_levels = multipliers  # Usamos los valores directamente
else:
    print("Error: El momento debe ser 0, 1 o 2.")
    sys.exit(1)

# Generar contornos con immath
contour_expr = f"iif({casa_image} > {contour_levels[0]}, 1, 0)"
for level in contour_levels[1:]:
    contour_expr += f" + iif({casa_image} > {level}, 1, 0)"

immath(imagename=casa_image, expr=contour_expr, outfile=contour_image)

# Exportar la imagen de contornos a FITS con el nombre especificado
exportfits(imagename=contour_image, fitsimage=output_fits, overwrite=True)

print(f"Proceso completado: Contornos generados para momento {moment} con sigma={sigma_value} y múltiplos {multipliers} <3")

# Para ejecutar este script en CASA, usa el siguiente comando en la terminal:
# casa --nologger --nogui -c script_contornos.py imagen.fits 0 0.001 "3,5,10,20" salida_contornos.fits