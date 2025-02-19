#! /usr/bin/env casa

import os
import sys
from casatasks import importfits, imstat, exportfits, immath

# Leer argumentos de entrada
if len(sys.argv) != 5:
    print("Uso: casa --nologger --nogui -c script_contornos.py <fits_file> <sigma> <multipliers> <output_fits>")
    sys.exit(1)

fits_file = sys.argv[1]
sigma_value = float(sys.argv[2])
multipliers = list(map(float, sys.argv[3].split(',')))
output_fits = sys.argv[4]

# Definir nombres de archivos intermedios
casa_image = 'imagen_casa.im'
contour_image = 'contornos.im'

# Eliminar archivos temporales si existen
for file in [casa_image, contour_image, output_fits]:
    if os.path.exists(file):
        os.remove(file)
        print(f"Archivo {file} eliminado para evitar conflictos de sobrescritura. :D")

# Importar la imagen FITS a un formato de CASA
importfits(fitsimage=casa_image, infile=fits_file, overwrite=True)

# Calcular niveles de contorno basados en sigma y sus múltiplos
contour_levels = [sigma_value * m for m in multipliers]

# Generar contornos con immath
contour_expr = f"iif({casa_image} > {sigma_value * multipliers[0]}, 1, 0)"
for m in multipliers[1:]:
    contour_expr += f" + iif({casa_image} > {sigma_value * m}, 1, 0)"

immath(imagename=casa_image, expr=contour_expr, outfile=contour_image)

# Exportar la imagen de contornos a FITS con el nombre especificado
exportfits(imagename=contour_image, fitsimage=output_fits, overwrite=True)

print(f"Proceso completado: Contornos generados con sigma={sigma_value} y múltiplos {multipliers} <3 ")

# Para ejecutar este script en CASA, usa el siguiente comando en la terminal:
# casa --nologger --nogui -c script_contornos.py imagen.fits 0.001 "3,5,10,20" salida_contornos.fits