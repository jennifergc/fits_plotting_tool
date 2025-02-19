#! /usr/bin/env casa

import os
import sys
import shutil
import numpy as np
from casatasks import importfits, exportfits, imstat, immath

# Leer argumentos de entrada
if len(sys.argv) < 5:
    print("Uso: casa --nologger --nogui -c script_contornos.py <fits_file> <moment> <sigma (opcional)> <multipliers> <output_fits>")
    sys.exit(1)

#leo los argumentos de entrada
fits_file = sys.argv[1]
moment = int(sys.argv[2])  # Momento 0, 1 o 2
multipliers = list(map(float, sys.argv[3].split(',')))
output_fits = sys.argv[4]

# Defino nombres de archivos intermedios
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

# Determinar sigma si no se proporciona
sigma_value = None
if moment in [0, 2]:
    stats = imstat(imagename=casa_image)
    sigma_value = stats['rms'][0] if 'rms' in stats else 1.0  # Estimación por RMS si no se da sigma
    print(f"Sigma estimado: {sigma_value}")
else:
    sigma_value = None  # No se usa sigma para momento 1

# Calcular niveles de contorno según el momento
if moment == 0 or moment == 2:
    contour_levels = [sigma_value * m for m in multipliers]
elif moment == 1:
    # Si el usuario no ha dado niveles, se estiman con un criterio estándar
    if not multipliers:
        stats = imstat(imagename=casa_image)
        v_min, v_max = stats['min'][0], stats['max'][0]
        n_levels = 5
        multipliers = np.linspace(v_min, v_max, n_levels).tolist()
        print(f"Niveles de contorno para momento 1 estimados: {multipliers}")
    contour_levels = multipliers
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

# Ejemplo de uso en una notebook de Python
# ----------------------------------------
# Este script se ejecuta en el entorno CASA, por lo que para llamarlo desde una notebook de Python,
# se puede usar el módulo subprocess para ejecutar comandos de sistema:

# ```python
# import subprocess
# 
# fits_file = "mi_imagen.fits"  # Ruta de la imagen FITS de entrada
# moment = 1  # Momento a calcular (0, 1 o 2)
# sigma = 0.001  # Valor de sigma si es aplicable (para momentos 0 y 2)
# multipliers = "3,5,10,20"  # Múltiplos de sigma o niveles absolutos para el momento 1
# output_fits = "contornos.fits"  # Nombre del archivo de salida
# 
# comando = ["casa", "--nologger", "--nogui", "-c", "script_contornos.py", 
#            fits_file, str(moment), str(sigma), multipliers, output_fits]
# 
# subprocess.run(comando)
# ```