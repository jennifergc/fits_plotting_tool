#%%writefile fits_plotter.py
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np
import matplotlib as mpl
from reproject import reproject_interp

class FITSPlotter:
    """
    Clase para visualizar imágenes FITS y superponer contornos desde otra imagen FITS.
    
    Atributos:
        image_fits (str): Ruta del archivo FITS de la imagen base.
        contour_fits (str): Ruta del archivo FITS de los contornos.
    
    Métodos:
        - plot(): Grafica la imagen base con los contornos superpuestos.
        - close(): Cierra los archivos FITS abiertos.
    """
    def __init__(self, image_fits, contour_fits):
        """
        Inicializa la clase cargando los archivos FITS de imagen base y contornos.

        Parámetros:
            image_fits (str): Ruta al archivo FITS de la imagen base.
            contour_fits (str): Ruta al archivo FITS de los contornos.
        """
        self.image_fits = image_fits
        self.contour_fits = contour_fits

        # Abrimos los archivos FITS
        self.hdul_base = fits.open(self.image_fits)
        self.hdul_contour = fits.open(self.contour_fits)
        
        # Extraemos los datos de la imagen base y contornos
        self.data_base = np.squeeze(self.hdul_base[0].data)  # Aseguramos que sea 2D
        self.data_contour = np.squeeze(self.hdul_contour[0].data)  # Aseguramos que sea 2D
        
        # Extraemos la información de coordenadas espaciales (WCS)
        self.wcs_base = WCS(self.hdul_base[0].header).celestial  
        self.wcs_contour = WCS(self.hdul_contour[0].header).celestial  
        
        # Verificar si las dimensiones coinciden
        if self.data_contour.shape != self.data_base.shape:
            print("⚠️ Reproyectando contornos para que coincidan con la imagen base...")
            try:
                self.data_contour, _ = reproject_interp((self.data_contour, self.hdul_contour[0].header), 
                                                        self.hdul_base[0].header, shape_out=self.data_base.shape)
            except ValueError as e:
                print(f"🚨 Error al reproyectar los contornos: {e}")
                self.data_contour = None
        
    def plot(self, save_as=None, title="Imagen con Contornos", object_name="Objeto Astronómico"):
        """
        Genera una imagen mostrando la imagen base con los contornos superpuestos.

        Parámetros:
        - save_as (str, opcional): Nombre del archivo para guardar la imagen.
        - title (str, opcional): Título de la imagen.
        - object_name (str, opcional): Nombre del objeto astronómico.
        """
        # Configuración de estilo para publicaciones científicas
        mpl.rcParams.update({
            "font.family": "serif",
            "text.usetex": False,
            "axes.labelsize": 16,
            "axes.titlesize": 18,
            "xtick.labelsize": 14,
            "ytick.labelsize": 14,
            "legend.fontsize": 14,
            "figure.dpi": 300
        })

        # Crear la figura y ajustar tamaño
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': self.wcs_base})

        # Mostrar la imagen base
        im = ax.imshow(self.data_base, cmap='inferno', origin='lower', interpolation='nearest')
        
        # Agregar contornos si la reproyección fue exitosa
        if self.data_contour is not None:
            ax.contour(self.data_contour, levels=np.linspace(np.min(self.data_contour), np.max(self.data_contour), 10), 
                       colors='white', linewidths=1, transform=ax.get_transform(self.wcs_base))
        else:
            print("🚨 No se pudieron superponer los contornos debido a un error en la reproyección.")

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
        self.hdul_contour.close()
        print("Archivos FITS cerrados.")