import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
from matplotlib.patches import Ellipse
from reproject import reproject_interp ### PARA LA REPROYECCIÓN


class FITSPlotter:
    def __init__(self, image_fits, contour_fits, sigma=3e-3, moment=None, region_label=None):
        """
        Parámetros:
            image_fits (str): Archivo FITS de la imagen base.
            contour_fits (str): Archivo FITS de los contornos.
            sigma (float, opcional): Factor de escala para el mapa.
            moment (str, opcional): Tipo de momento ('m0', 'm1', 'm2', 'continuo').
            region_label (str, opcional): Nombre de la región para mostrar en la imagen.
        """
        self.image_fits = image_fits
        self.contour_fits = contour_fits
        self.sigma = sigma
        self.moment = moment  
        self.region_label = region_label  

        # Cargar la imagen base
        self.hdul_base = fits.open(self.image_fits)
        self.data_base = self.hdul_base[0].data.squeeze()
        self.wcs_base = WCS(self.hdul_base[0].header, naxis=2)
        #self.wcs_base = WCS(self.hdul_base[0].header).celestial #COMENTADO PARA LA REPROYECCIÓN
        
        # Cargar la imagen de contornos
        self.hdul_contour = fits.open(self.contour_fits)
        self.data_contour = self.hdul_contour[0].data.squeeze()
        self.wcs_contour = WCS(self.hdul_contour[0].header, naxis=2)## AGREGADO PARA LA REPROYECCIÓN
        #############################################################REPROYECCIÓN (ELIMINAR SI NO ME SIRVE)
        # Reproyectar la imagen de contornos para alinearla con la base
        shape_out = (self.data_base.shape[-2], self.data_base.shape[-1])
        self.reprojected_contour, _ = reproject_interp(
            (self.data_contour, self.wcs_contour), self.wcs_base, shape_out=shape_out
        )
        ###################################################################################################
        # Determinar la etiqueta de la barra de color según el momento
        moment_labels = {
            "m0": "Flujo Integrado (Jy/beam km/s)",
            "m1": "Velocidad (km/s)",
            "m2": "Dispersión de Velocidad (km/s)",
            "continuo": "Intensidad (Jy/beam)"
        }
        self.colorbar_label = moment_labels.get(self.moment, "Intensidad (Jy/beam)")

    def plot(self, save_as=None, title=""):
        """Genera la visualización de la imagen FITS con la superposición de contornos."""
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': self.wcs_base})
        # Seleccionar el cmap dependiendo del tipo de imagen
        if self.moment in ['continuo', 'm0']:
            cmap = 'inferno'
        elif self.moment in ['m1', 'm2']:
            cmap = 'rainbow'
        else:
            cmap = 'inferno'  # Valor por defecto en caso de que no haya momento definido
        im = ax.imshow(self.data_base, cmap=cmap, origin='lower', interpolation='nearest')

   
        # Dibujar los contornos
        levels = np.linspace(np.nanmin(self.data_contour), np.nanmax(self.data_contour), 7)  # Ajusta el número de niveles si es necesario
        #ax.contour(self.data_contour, levels=levels, colors='white', linewidths=1.5, alpha=0.8) #COMENTADO PARA LA REPROYECCIÓN
        ax.contour(self.reprojected_contour, levels=levels, colors='white', linewidths=1.5, alpha=0.8)

        

        # Dibujar el tamaño del beam en la esquina inferior izquierda dentro del mapa
        bmaj = self.hdul_base[0].header.get("BMAJ", None)
        bmin = self.hdul_base[0].header.get("BMIN", None)
        bpa = self.hdul_base[0].header.get("BPA", 0)  

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

        # Si ingresé un nombre para la región, mostrarlo en la imagen
        if self.region_label:
            ax.text(0.95, 0.95, self.region_label, transform=ax.transAxes, fontsize=14,
                    color='white', ha='right', va='top', bbox=dict(facecolor='black', alpha=0.5))
        
        ############ ESTRELLITA
        # Convertir coordenadas ecuatoriales a coordenadas de píxeles
        uc1_coords = SkyCoord(ra='18h20m24.82s', dec='-16d11m34.9s', frame='icrs')
        x_pix, y_pix = self.wcs_base.world_to_pixel(uc1_coords)
        
        # Agregar la estrellita en la ubicación de UC1 con solo el borde (vacía por dentro)
        ax.scatter(x_pix, y_pix, facecolors='none', edgecolors='cyan', marker='*', s=250, linewidths=1.5, zorder=10)
        
        # Agregar la etiqueta sin fondo y en letra negra
        ax.annotate("UC1", (x_pix + 5, y_pix + 5), color='cyan', fontsize=12, weight='bold', zorder=11)

        ############

        # Configuración de ejes
        ax.set_xlabel('Ascensión Recta (RA)')
        ax.set_ylabel('Declinación (Dec)')
        plt.colorbar(im, ax=ax, pad=0.05, label=self.colorbar_label)
        plt.title(title)

        if save_as:
            plt.savefig(save_as, dpi=300, bbox_inches='tight')
            print(f" Imagen guardada como {save_as}")

        plt.show()