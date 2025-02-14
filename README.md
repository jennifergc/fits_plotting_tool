# FITSPlotter: Visualización de Imágenes FITS

**Autor:** MSc. Jennifer Grisales-Casadiegos\
**Institución:** Universidad de Guanajuato, México\
**Fecha de última actualización:** 14 Febrero 2025

## Descripción

**FITSPlotter** es una clase en Python diseñada para visualizar imágenes astronómicas en formato **FITS** con la opción de superponer contornos. La visualización está optimizada para gráficos de alta calidad.

## Requisitos

Para utilizar este script, asegúrate de tener instaladas las siguientes dependencias:

```bash
pip install matplotlib astropy numpy
```

## Uso

### 1️⃣ Importar la clase

```python
from fits_plotter import FITSPlotter
```

### 2️⃣ Cargar un archivo FITS sin contornos

```python
fits_file = "ruta/a/tu/imagen.fits"
plotter = FITSPlotter(image_fits=fits_file)
plotter.plot()
plotter.close()
```

### 3️⃣ Cargar una imagen con contornos

Si deseas superponer una imagen de contornos:

```python
fits_file = "ruta/a/tu/imagen.fits"
contour_file = "ruta/a/tu/contornos.fits"
plotter = FITSPlotter(image_fits=fits_file, contour_fits=contour_file)
plotter.plot(contour_levels=[3, 5, 10])
plotter.close()
```

### 4️⃣ Ajustar el valor de `sigma` para los contornos

Puedes modificar `sigma` para ajustar la escala de los niveles de contorno:

```python
plotter = FITSPlotter(image_fits=fits_file, contour_fits=contour_file, sigma=5e-3)
plotter.plot(contour_levels=[-3, 3, 5, 10, 20, 40, 80, 100, 150])
plotter.close()
```

### 5️⃣ Guardar la imagen generada

Si deseas guardar la imagen resultante en un archivo:

```python
plotter.plot(contour_levels=[3, 5, 10], save_as="resultado.png")
```

## Características

✅ Visualización de imágenes FITS con coordenadas astronómicas.\
✅ Superposición opcional de contornos desde otro archivo FITS.\
✅ Configuración de etiquetas, grillas y estilo para publicaciones científicas.\
✅ Opciones para personalizar el título, nombre del objeto y niveles de contorno.\
✅ Permite guardar las imágenes en formato PNG con alta resolución.

## Notas

Si tienes problemas con la importación del script, asegúrate de que el archivo `fits_plotter.py` se encuentra en el mismo directorio de tu script o en el `PYTHONPATH`.

```python
import sys
sys.path.append("ruta/a/tu/directorio")
```

**Desarrollado para análisis de imágenes FITS en astrofísica**. 🚀


