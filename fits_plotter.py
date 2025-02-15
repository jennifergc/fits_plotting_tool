#%%writefile fits_plotter.py
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np
import matplotlib as mpl
from matplotlib.ticker import MaxNLocator

class FITSPlotter:
    """
    Clase para visualizar imágenes FITS y superponer contornos opcionalmente.
    
    Atributos:
        image_fits (str): Ruta del archivo FITS de la imagen base.
        contour_fits (str, opcional): Ruta del archivo FITS de los contornos (si se desea).
        sigma (float): Escalado de los niveles de contorno (valor por defecto 3e-3).
    
    Métodos:
        - plot(): Grafica la imagen y los contornos si están disponibles.
        - close(): Cierra los archivos FITS abiertos.
    """
    def __init__(self, image_fits, contour_fits=None, sigma=3e-3):
        """
        Inicializa la clase cargando los archivos FITS.

        Parámetros:
            image_fits (str): Ruta al archivo FITS de la imagen base.
            contour_fits (str, opcional): Ruta al archivo FITS de los contornos.
            sigma (float, opcional): Factor de escala para los contornos.
        """
        self.image_fits = image_fits  # Guarda la ruta del archivo de imagen
        self.contour_fits = contour_fits  # Guarda la ruta del archivo de contornos (si se proporciona)
        self.sigma = sigma  # Define el nivel de escala para los contornos

        # Abrimos el archivo FITS de la imagen principal
        self.hdul_base = fits.open(self.image_fits)
        # Extraemos los datos de la imagen principal (se asume un formato de 4 dimensiones)
        self.data_base = self.hdul_base[0].data[0, 0, :, :]
        # Extraemos la información de coordenadas espaciales (WCS)
        self.wcs_base = WCS(self.hdul_base[0].header).celestial  

        # Si se proporciona un archivo de contorno, también lo abrimos
        if self.contour_fits:
            self.hdul_contour = fits.open(self.contour_fits)
            self.data_contour = self.hdul_contour[0].data[0, 0, :, :]
            self.wcs_contour = WCS(self.hdul_contour[0].header).celestial
        else:
            self.data_contour = None  # Si no hay contorno, asignamos None

    def plot(self, contour_levels=None, save_as=None, title="Mapa de Intensidad", object_name="M17"):
        """
        Genera una imagen FITS hermosa y con estilo :D

        Parámetros:
        - contour_levels (list, opcional): Lista de niveles de contorno en unidades de sigma.
        - save_as (str, opcional): Nombre del archivo para guardar la imagen.
        - title (str, opcional): Título de la imagen.
        - object_name (str, opcional): Nombre del objeto astronómico.
        """

        # Configuración de estilo para publicaciones científicas
        mpl.rcParams.update({
            "font.family": "serif",  # Fuente tipo serif
            "text.usetex": False,  # Usa LaTeX si es necesario
            "axes.labelsize": 16,  # Tamaño de etiqueta de ejes
            "axes.titlesize": 18,  # Tamaño de título
            "xtick.labelsize": 14,  # Tamaño de ticks en X
            "ytick.labelsize": 14,  # Tamaño de ticks en Y
            "legend.fontsize": 14,  # Tamaño de fuente en leyenda
            "figure.dpi": 300  # Alta resolución
        })
 
        # Crear la figura y ajustar tamaño
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': self.wcs_base})

        # Ajustar colores
        im = ax.imshow(self.data_base, cmap='inferno', origin='lower', interpolation='nearest')

        # Agregar contornos si están disponibles
        if self.data_contour is not None and contour_levels:
            contour_levels = np.array(contour_levels) * self.sigma
            ax.contour(self.data_contour, levels=contour_levels, colors='white', linewidths=1,
                       transform=ax.get_transform(self.wcs_contour))

        # Configuración de ejes y escalas
        ax.set_xlabel('Ascensión Recta (RA)', fontsize=16)
        ax.set_ylabel('Declinación (Dec)', fontsize=16)
        ax.tick_params(axis="both", direction="in", which="both", length=6, width=1.5)

        # Agregar barra de color con etiquetas
        cbar = plt.colorbar(im, ax=ax, pad=0.05)
        cbar.set_label('Intensidad (Jy/beam)', fontsize=14)

        # Agregar anotaciones con el nombre del objeto (OPCIONAL)
        ax.text(0.05, 0.95, f"{object_name}", transform=ax.transAxes, fontsize=16, fontweight='bold',
                color='white', bbox=dict(facecolor='black', alpha=0.5, edgecolor='none'))

        # Agregar título y configurar límites de ejes
        plt.title(title, fontsize=18)

        # Guardar la imagen si se especifica un archivo
        if save_as:
            plt.savefig(save_as, dpi=300, bbox_inches='tight')
            print(f"Imagen guardada como {save_as}")

        # Mostrar la imagen
        plt.show()

    def close(self):
        """Cierra los archivos FITS abiertos."""
        self.hdul_base.close()
        if self.contour_fits:
            self.hdul_contour.close()
        print("Archivos FITS cerrados.")