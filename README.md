# FITS Plotting Tool

**Autora:** J. Grisales Casadiegos  
**Git:** jennifergc  
**ORCID:** [0000-0003-0830-2778](https://orcid.org/0000-0003-0830-2778)  
**Institución:** Universidad de Guanajuato, Doctorado en Ciencias Astrofísica  
**Fecha de última actualización:** 14 Febrero 2025

---

## Requisitos

Para utilizar las herramientas de este repositorio, asegúrate de tener instaladas las siguientes dependencias:

- **Python (>=3.6)**
- **Matplotlib**
- **Astropy**
- **Numpy**
- **Reproject** (para la reproyección de contornos en la imagen base)

Puedes instalar todas las dependencias necesarias ejecutando:

```bash
pip install matplotlib astropy numpy reproject
```

---

## Descripción General

**FITS Plotting Tool** es un repositorio destinado al análisis y visualización de imágenes astronómicas en formato **FITS**. Permite, entre otras cosas, visualizar imágenes con información de coordenadas astronómicas, superponer contornos significativos y beams (representación de la respuesta instrumental), y realizar análisis interactivos mediante notebooks.

El repositorio ofrece dos scripts principales y un notebook interactivo, cada uno orientado a distintos aspectos del procesamiento y análisis de datos:

- **contcal.py:** Genera mapas de contornos en imágenes FITS utilizando el entorno CASA.
- **fits_plotter.py:** Proporciona la clase `FITSPlotter` para visualizar imágenes FITS y superponer contornos, beams y anotaciones.
- **Fits_visualizer.ipynb:** Notebook interactivo que ejemplifica el uso de la herramienta y permite explorar y ajustar parámetros visuales en tiempo real.

---

## Detalle de Componentes

### 1. Script: **contcal.py**

- **Propósito:**  
  Generar mapas de contornos a partir de imágenes FITS utilizando CASA. Este script calcula los niveles de contorno basados en dos métodos:
  - **sigma:** Usa la desviación estándar (RMS) y multiplicadores definidos por el usuario.
  - **imax:** Utiliza el valor máximo de la imagen y factores predefinidos.

- **Contenido e Instrucciones de Uso:**  
  - **Argumentos de entrada:**  
    - `<fits_file>`: Ruta del archivo FITS de entrada.
    - `<moment>`: Momento de la imagen (0, 1 o 2).
    - `<method>`: Método para calcular los niveles de contorno ("sigma" o "imax").
    - `<sigma>`: Valor de sigma o "auto" para calcularlo automáticamente (válido para momentos 0 y 2).
    - `<multipliers>`: Valores de contorno separados por comas. Obligatorio en el método "sigma"; en "imax" es opcional.
    - `<output_fits>`: Nombre del archivo de salida con los contornos generados.

  - **Uso General:**  
    Este script se ejecuta desde la línea de comandos en el entorno CASA.  
    Ejemplo de uso:
    ```bash
    casa --nologger --nogui -c contcal.py imagen.fits 0 sigma 0.005 "3,5,10,20" salida_contornos.fits
    ```
    También se muestran ejemplos en los comentarios internos del script para diversos casos de uso (como el uso del método "imax" o la especificación de contornos directos para el momento 1).

- **Uso en Notebooks o Scripts Locales:**  
  Aunque **contcal.py** está diseñado para ejecutarse en CASA, se puede invocar de manera similar desde un script o notebook si se tiene configurado el entorno adecuado o se utiliza un sistema de automatización que invoque comandos externos.

---

### 2. Script: **fits_plotter.py**

- **Propósito:**  
  Visualizar imágenes FITS y superponer información adicional (como contornos y beams) en la imagen de base.

- **Contenido e Instrucciones de Uso:**  
  - Este script define la clase `FITSPlotter`, la cual:
    - Carga la imagen FITS base.
    - Lee opcionalmente un archivo FITS que contenga contornos.
    - Extrae automáticamente parámetros importantes desde la cabecera (como la escala de píxeles y los parámetros del beam).
    - Realiza la reproyección del archivo de contornos para que se alinee con la imagen base.
    - Genera una visualización utilizando Matplotlib, en la que se dibujan la imagen, los contornos (si se han proporcionado), los beams en la esquina inferior izquierda, y anotaciones como el nombre de la región o marcas sobre estrellas de referencia.
  
  - **Ejemplo de Uso en un Script Python:**
    ```python
    from fits_plotter import FITSPlotter
    #Definir la ruta a la imagen FITS y opcionalmente al archivo de contornos
    fits_file = "ruta/a/tu/imagen.fits"
    contour_file = "ruta/a/tu/contornos.fits"
    #Crear una instancia de FITSPlotter, ajustando parámetros como sigma, tipo de momento y etiqueta de región
    plotter = FITSPlotter(
        image_fits=fits_file,
        contour_fits=contour_file,
        sigma=3e-3,
        moment='m0',
        region_label="Región A"
    )
    #Generar y mostrar la visualización (se puede guardar la imagen utilizando el parámetro save_as)
    plotter.plot(save_as="resultado.png") 
    ```
  
  - **Uso en Notebooks o desde un Directorio Local:**  
    Si el script se encuentra en un directorio distinto al del notebook o script principal, añade la ruta al `PYTHONPATH` para poder importarlo sin inconvenientes:
    ```python
    import sys
    sys.path.append("ruta/al/directorio/de/tu/script")
    from fits_plotter import FITSPlotter
    ```
    Esto te permitirá utilizar la clase de forma interactiva o en otros entornos sin necesidad de mover los archivos.

---

### 3. Notebook: **Fits_visualizer.ipynb**

- **Propósito:**  
  Ofrecer una interfaz interactiva que permita visualizar y analizar imágenes FITS, aplicando contornos y mostrando beams de forma dinámica (testeando el uso de contcal y fits_plotter).

- **Qué se Puede Ver y Hacer en el Notebook:**  
  - **Carga Interactiva de Imágenes:** Permite cargar imágenes FITS directamente en el entorno de Jupyter.
  - **Aplicación de Contornos:** Se muestran ejemplos prácticos de cómo generar y superponer contornos utilizando los scripts disponibles (especialmente la clase `FITSPlotter`).
  - **Ajuste de Parámetros en Tiempo Real:** Puedes modificar parámetros como sigma, momento y etiquetas de regiones, y observar inmediatamente cómo estos cambios afectan la visualización.
  - **Demostración Completa del Flujo de Trabajo:** El notebook integra el uso de la clase `FITSPlotter` junto con explicaciones paso a paso, facilitando la comprensión del proceso de análisis de datos astronómicos.


## Licencia

Este repositorio se distribuye bajo la Licencia Pública General GNU (GPL) versión 3. Esto significa que se garantiza el derecho a usar, estudiar, modificar y redistribuir este software, siempre que cualquier distribución o modificación se mantenga bajo los mismos términos y se incluya el código fuente correspondiente.

Para más información, consulta el texto completo de la licencia en:  
[https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html)
