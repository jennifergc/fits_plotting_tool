#%%writefile fits_plotter.py
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np

class FITSPlotter:
    def __init__(self, image_fits, contour_fits=None, sigma=3e-3):
        self.image_fits = image_fits
        self.contour_fits = contour_fits
        self.sigma = sigma
        
        self.hdul_base = fits.open(self.image_fits)
        self.data_base = self.hdul_base[0].data[0, 0, :, :]
        self.wcs_base = WCS(self.hdul_base[0].header).celestial

        if self.contour_fits:
            self.hdul_contour = fits.open(self.contour_fits)
            self.data_contour = self.hdul_contour[0].data[0, 0, :, :]
            self.wcs_contour = WCS(self.hdul_contour[0].header).celestial
        else:
            self.data_contour = None

    def plot(self, contour_levels=None, save_as=None):
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': self.wcs_base})
        im = ax.imshow(self.data_base, cmap='plasma', origin='lower')

        if self.data_contour is not None and contour_levels:
            contour_levels = np.array(contour_levels) * self.sigma
            contornos = ax.contour(self.data_contour, levels=contour_levels, colors='white', linewidths=0.8,
                                   transform=ax.get_transform(self.wcs_contour))

        plt.colorbar(im, ax=ax, pad=0.05, label='Intensidad (Jy/beam)')
        ax.set_xlabel('Ascensión Recta (RA)')
        ax.set_ylabel('Declinación (Dec)')
        plt.title(f'Imagen con contornos de {self.contour_fits if self.contour_fits else "ninguno"}')

        if save_as:
            plt.savefig(save_as, dpi=300, bbox_inches='tight')
            print(f"Imagen guardada como {save_as}")
        
        plt.show()

    def close(self):
        self.hdul_base.close()
        if self.contour_fits:
            self.hdul_contour.close()
        print("Archivos FITS cerrados.")
