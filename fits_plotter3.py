import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
from matplotlib.patches import Ellipse

class FITSPlotter:
    def __init__(self, image_fits, sigma=3e-3, moment=None, region_label=None):
        """
        Parámetros:
            image_fits (str): Archivo FITS de la imagen base.
            sigma (float, opcional): Factor de escala para el mapa.
            moment (str, opcional): Tipo de momento ('m0', 'm1', 'm2', 'continuo').
            region_label (str, opcional): Nombre de la región para mostrar en la imagen.
        """
        self.image_fits = image_fits
        self.sigma = sigma
        self.moment = moment  # Tipo de momento
        self.region_label = region_label  # Nombre de la región

        # Cargar la imagen base
        self.hdul_base = fits.open(self.image_fits)
        self.data_base = self.hdul_base[0].data.squeeze()
        self.wcs_base = WCS(self.hdul_base[0].header).celestial

        # Determinar la etiqueta de la barra de color según el momento
        moment_labels = {
            "m0": "Flujo Integrado (Jy/beam km/s)",
            "m1": "Velocidad (km/s)",
            "m2": "Dispersión de Velocidad (km/s)",
            "continuo": "Intensidad (Jy/beam)"
        }
        self.colorbar_label = moment_labels.get(self.moment, "Intensidad (Jy/beam)")

    def plot(self, save_as=None, title=""):
        """Genera la visualización de la imagen FITS con tamaño del beam correctamente ubicado y nombre de la región."""
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': self.wcs_base})
        im = ax.imshow(self.data_base, cmap='inferno', origin='lower', interpolation='nearest')

        # Dibujar el tamaño del beam en la esquina inferior izquierda dentro del mapa
        bmaj = self.hdul_base[0].header.get("BMAJ", None)
        bmin = self.hdul_base[0].header.get("BMIN", None)
        bpa = self.hdul_base[0].header.get("BPA", 0)  # Ángulo de posición

        if bmaj and bmin:
            bmaj_pix = bmaj / abs(self.hdul_base[0].header["CDELT1"])  # Convertir a píxeles
            bmin_pix = bmin / abs(self.hdul_base[0].header["CDELT2"])
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            beam_x = xlim[0] + 0.1 * (xlim[1] - xlim[0])  # Posición en la esquina inferior izquierda
            beam_y = ylim[0] + 0.1 * (ylim[1] - ylim[0])
            beam_ellipse = Ellipse((beam_x, beam_y), width=bmin_pix, height=bmaj_pix, angle=bpa,
                                   edgecolor='white', facecolor='gray', alpha=0.5, lw=1.5)
            ax.add_patch(beam_ellipse)

        # Si el usuario ingresó un nombre para la región, mostrarlo en la imagen
        if self.region_label:
            ax.text(0.95, 0.95, self.region_label, transform=ax.transAxes, fontsize=14,
                    color='white', ha='right', va='top', bbox=dict(facecolor='black', alpha=0.5))

        # Configuración de ejes
        ax.set_xlabel('Ascensión Recta (RA)')
        ax.set_ylabel('Declinación (Dec)')
        plt.colorbar(im, ax=ax, pad=0.05, label=self.colorbar_label)
        plt.title(title)

        # Guardar la imagen si se especifica
        if save_as:
            plt.savefig(save_as, dpi=300, bbox_inches='tight')
            print(f" Imagen guardada como {save_as}")

        plt.show()
