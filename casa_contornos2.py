#! /usr/bin/env casa

import os
import sys
import shutil
import numpy as np
from casatasks import importfits, exportfits, imstat, immath

# Leer argumentos de entrada
if len(sys.argv) < 6:
    print("Uso: casa --nologger --nogui -c script_contornos.py <fits_file> <moment> <sigma (opcional)> <multipliers> <output_fits>")
    sys.exit(1)

fits_file = sys.argv[1]
moment = int(sys.argv[2])  # Momento 0, 1 o 2
sigma_value_arg = sys.argv[3]  # Corresponde al valor de sigma
multipliers_arg = sys.argv[4]  # Corresponde a los valores de contorno
output_fits = sys.argv[5]  # Archivo de salida

print(f"Multipliers recibidos: {multipliers_arg}")
print(f"Argumentos recibidos: {sys.argv}")

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

# Determinar sigma si no se proporciona
sigma_value = None
if moment in [0, 2]:
    if sigma_value_arg.lower() == "auto":
        stats = imstat(imagename=casa_image)
        sigma_value = stats['rms'][0] if 'rms' in stats else 1.0  # Estimación por RMS si no se da sigma
        print(f"Sigma estimado: {sigma_value}")
    else:
        sigma_value = float(sigma_value_arg)  # Usa el valor ingresado por el usuario

# Calcular niveles de contorno según el momento
try:
    if moment == 0 or moment == 2:
        multipliers = list(map(float, multipliers_arg.split(',')))
        contour_levels = [sigma_value * m for m in multipliers]
    elif moment == 1:
        # Si el usuario no proporciona los valores de contorno, se genera un error
        if not multipliers_arg or multipliers_arg.lower() == "auto":
            print("Error: Para el momento 1, el usuario debe ingresar los niveles de contorno explícitamente.")
            sys.exit(1)
        else:
            multipliers = list(map(float, multipliers_arg.split(',')))
            contour_levels = multipliers
    else:
        print("Error: El momento debe ser 0, 1 o 2.")
        sys.exit(1)
except ValueError:
    print(f"Error: No se pudieron convertir los valores de contorno correctamente. Revisar entrada: {multipliers_arg}")
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