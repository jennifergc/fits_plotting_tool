import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
from matplotlib.patches import Ellipse
from reproject import reproject_interp ### PARA LA REPROYECCIÓN


class FITSPlotter:
    def __init__(self, image_fits, contour_fits=None, sigma=3e-3, moment=None, region_label=None):
        """
        Parámetros:
            image_fits (str): Archivo FITS de la imagen base.
            contour_fits (str, opcional): Archivo FITS de los contornos (puede ser None).
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
        
        # Extraer parámetros del beam de la imagen base
        self.beam_base = self.get_beam_params(self.hdul_base[0].header)
        
        # Cargar la imagen de contornos solo si se proporciona
        if self.contour_fits:
            self.hdul_contour = fits.open(self.contour_fits)
            self.data_contour = self.hdul_contour[0].data.squeeze()
            self.wcs_contour = WCS(self.hdul_contour[0].header, naxis=2)

            # Reproyección de los contornos a la imagen base
            shape_out = (self.data_base.shape[-2], self.data_base.shape[-1])
            self.reprojected_contour, _ = reproject_interp(
                (self.data_contour, self.wcs_contour), self.wcs_base, shape_out=shape_out
            )

            # Extraer parámetros del beam de los contornos
            self.beam_contour = self.get_beam_params(self.hdul_contour[0].header)
        else:
            self.reprojected_contour = None  # No hay contornos
            self.beam_contour = None  # No hay beam de contornos

    def get_beam_params(self, header):
        """
        Extrae los parámetros del beam (BMAJ, BMIN, BPA) de un header FITS.
        Retorna un diccionario con los valores si existen, de lo contrario, None.
        """
        try:
            bmaj = header['BMAJ'] * 3600  # Convertir de grados a arcsec
            bmin = header['BMIN'] * 3600
            bpa = header['BPA']
            return {'bmaj': bmaj, 'bmin': bmin, 'bpa': bpa}
        except KeyError:
            return None  # No hay información del beam

    def plot(self, save_as=None, title=""):
        """Genera la visualización de la imagen FITS con la superposición de contornos (si existen) y beams."""
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': self.wcs_base})

        # Determinar colores según el tipo de momento
        if self.moment in ['m0', 'continuo']:
            cmap_base = 'gnuplot2'
            contour_color = 'white'  # Contornos blancos
            star_color = 'lawngreen'  # Estrellita y label amarillo oscuro
        elif self.moment in ['m1', 'm2']:
            cmap_base = 'jet'
            contour_color = 'black'  # Contornos negros
            star_color = 'fuchsia'  # Estrellita y label amarillo oscuro
        else:
            cmap_base = 'gnuplot2'
            contour_color = 'white'  # Por defecto, contornos blancos
            star_color = 'yellow'  # Por defecto, amarillo normal

        # Mostrar la imagen base
        im = ax.imshow(self.data_base, origin='lower', cmap=cmap_base)

        # Dibujar contornos solo si hay datos de contornos
        if self.reprojected_contour is not None:
            levels = np.linspace(np.nanmin(self.data_contour), np.nanmax(self.data_contour), 7)
            ax.contour(self.reprojected_contour, levels=levels, colors=contour_color, linewidths=1.5, alpha=0.8)

        # Dibujar el beam de la imagen base en la esquina inferior izquierda
        self.plot_beam(ax, self.beam_base, 'white', position_factor=0.1)

        # Dibujar el beam de los contornos en la esquina inferior derecha si existen
        if self.beam_contour:
            self.plot_beam(ax, self.beam_contour, 'blue', position_factor=0.2)

        # Si ingresé un nombre para la región, mostrarlo en la imagen
        if self.region_label:
            ax.text(0.95, 0.95, self.region_label, transform=ax.transAxes, fontsize=14,
                    color='white', ha='right', va='top', bbox=dict(facecolor='black', alpha=0.5))

        ############ ESTRELLITA
        # Convertir coordenadas ecuatoriales a coordenadas de píxeles
        uc1_coords = SkyCoord(ra='18h20m24.82s', dec='-16d11m34.9s', frame='icrs')
        x_pix, y_pix = self.wcs_base.world_to_pixel(uc1_coords)
        
        # Agregar la estrellita en la ubicación de UC1 con solo el borde (vacía por dentro)
        ax.scatter(x_pix, y_pix, facecolors='none', edgecolors=star_color, marker='*', s=250, linewidths=1.5, zorder=10)
        
        # Agregar la etiqueta sin fondo y en letra negra
        ax.annotate("UC1", (x_pix + 5, y_pix + 5), color=star_color, fontsize=12, weight='bold', zorder=11)

        # Configuración de ejes
        ax.set_xlabel('Ascensión Recta (RA)')
        ax.set_ylabel('Declinación (Dec)')
        plt.colorbar(im, ax=ax, pad=0.05, label="Intensidad (Jy/beam)")
        plt.title(title)

        if save_as:
            plt.savefig(save_as, dpi=300, bbox_inches='tight')
            print(f" Imagen guardada como {save_as}")

        plt.show()

    def plot_beam(self, ax, beam_params, color, position_factor=0.1):
        """Dibuja el beam en la posición especificada dentro del mapa."""
        if beam_params:
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            beam_x = xlim[0] + position_factor * (xlim[1] - xlim[0])
            beam_y = ylim[0] + position_factor * (ylim[1] - ylim[0])
            beam_ellipse = Ellipse((beam_x, beam_y), width=beam_params['bmin'], height=beam_params['bmaj'],
                                   angle=beam_params['bpa'], edgecolor=color, facecolor='none', lw=2)
            ax.add_patch(beam_ellipse)