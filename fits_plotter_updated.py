
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, Angle
import astropy.units as u
from matplotlib.patches import Ellipse
from reproject import reproject_interp  ### PARA LA REPROYECCIÓN

# ==============================
#   FITSPlotter (versión extendida)
# ==============================
class FITSPlotter:
    def __init__(
        self,
        image_fits,
        contour_fits=None,
        sigma=3e-3,
        moment=None,
        region_label=None,
        use_delta_coords=False,   # Nuevo: usar ejes en ΔRA/ΔDec (arcsec) relativos a UC1
        show_uc1=True,            # Nuevo: mostrar estrellita de UC1
        show_pa_lines=True,       # Nuevo: mostrar líneas PA=126° y 216°
        ask=True                  # Nuevo: preguntar en tiempo de ejecución por estas opciones
    ):
        """
        Parámetros:
            image_fits (str): Archivo FITS de la imagen base.
            contour_fits (str, opcional): Archivo FITS de los contornos (puede ser None).
            sigma (float, opcional): Factor de escala para el mapa.
            moment (str, opcional): Tipo de momento ('m0', 'm1', 'm2', 'continuo').
            region_label (str, opcional): Nombre de la región para mostrar en la imagen.
            use_delta_coords (bool): Si True, los ejes se muestran en ΔRA/ΔDec (arcsec) relativos a UC1.
            show_uc1 (bool): Si True, dibuja la estrellita y etiqueta de UC1.
            show_pa_lines (bool): Si True, dibuja las líneas con PA=126° y 216° pasando por UC1.
            ask (bool): Si True, al llamar plot() se preguntan estas opciones en pantalla.
        """
        self.image_fits = image_fits
        self.contour_fits = contour_fits
        self.sigma = sigma
        self.moment = moment
        self.region_label = region_label
        self.use_delta_coords = use_delta_coords
        self.show_uc1 = show_uc1
        self.show_pa_lines = show_pa_lines
        self.ask = ask

        # Definir etiquetas del colorbar según el momento
        moment_labels = {
            "m0": "Flujo Integrado (Jy/beam km/s)",
            "m1": "Velocidad (km/s)",
            "m2": "Dispersión de Velocidad (km/s)",
            "continuo": "Intensidad (Jy/beam)"
        }
        self.colorbar_label = moment_labels.get(self.moment, "Intensidad (Jy/beam)")

        # Cargar la imagen base
        self.hdul_base = fits.open(self.image_fits)
        self.data_base = self.hdul_base[0].data.squeeze()
        self.wcs_base = WCS(self.hdul_base[0].header, naxis=2)

        # Calcular el pixel scale (arcsec/pixel) usando CDELT1
        # Nota: CDELT1 < 0 normalmente para RA; usamos el valor absoluto
        self.pixel_scale = abs(self.hdul_base[0].header.get("CDELT1", 1.0/3600.0)) * 3600.0  # arcsec/pixel

        # Extraer parámetros del beam de la imagen base
        self.beam_base = self.get_beam_params(self.hdul_base[0].header)

        # Cargar contornos si aplica y re-proyectar a la WCS base
        if self.contour_fits:
            self.hdul_contour = fits.open(self.contour_fits)
            self.data_contour = self.hdul_contour[0].data.squeeze()
            self.wcs_contour = WCS(self.hdul_contour[0].header, naxis=2)
            # Reproyección sobre la grilla base
            shape_out = (self.data_base.shape[-2], self.data_base.shape[-1])
            self.reprojected_contour, _ = reproject_interp(
                (self.data_contour, self.wcs_contour), self.wcs_base, shape_out=shape_out
            )
            self.beam_contour = self.get_beam_params(self.hdul_contour[0].header)
        else:
            self.reprojected_contour = None
            self.beam_contour = None

        # Coordenadas de referencia UC1 (ICRS)
        self.uc1_coord = SkyCoord(ra='18h20m24.821s', dec='-16d11m35.02s', frame='icrs')

    def get_beam_params(self, header):
        """
        Extrae los parámetros del beam (BMAJ, BMIN, BPA) de un header FITS.
        Retorna un dict con BMAJ/BMIN en arcsec y BPA en grados. Si faltan, retorna None.
        """
        try:
            bmaj = header['BMAJ'] * 3600.0  # deg -> arcsec
            bmin = header['BMIN'] * 3600.0
            bpa = header['BPA']            # deg
            return {'bmaj': bmaj, 'bmin': bmin, 'bpa': bpa}
        except KeyError:
            return None

    # -----------------------------
    # Utilidades para ΔRA/ΔDec
    # -----------------------------
    def _arcsec_offsets_extent(self):
        """
        Calcula el 'extent' en (ΔRA, ΔDec) [arcsec] relativo a UC1 para usar en imshow/contour
        asumiendo un campo pequeño (distorsiones despreciables).
        """
        ny, nx = self.data_base.shape[-2], self.data_base.shape[-1]

        # Posición de UC1 en píxeles (en el sistema de la imagen base)
        x_uc1, y_uc1 = self.wcs_base.world_to_pixel(self.uc1_coord)

        # Convertimos las posiciones de borde a coordenadas del cielo
        # Para eje X (fijo y = y_uc1)
        x0_world = self.wcs_base.pixel_to_world(0, y_uc1)
        x1_world = self.wcs_base.pixel_to_world(nx - 1, y_uc1)

        # Para eje Y (fijo x = x_uc1)
        y0_world = self.wcs_base.pixel_to_world(x_uc1, 0)
        y1_world = self.wcs_base.pixel_to_world(x_uc1, ny - 1)

        # ΔRA (este positivo): considerar compresión por cos(dec)
        dec_rad = np.deg2rad(self.uc1_coord.dec.deg)
        dra0 = (x0_world.ra.deg - self.uc1_coord.ra.deg) * np.cos(dec_rad) * 3600.0
        dra1 = (x1_world.ra.deg - self.uc1_coord.ra.deg) * np.cos(dec_rad) * 3600.0

        # ΔDec (norte positivo)
        ddec0 = (y0_world.dec.deg - self.uc1_coord.dec.deg) * 3600.0
        ddec1 = (y1_world.dec.deg - self.uc1_coord.dec.deg) * 3600.0

        # Extent = (xmin, xmax, ymin, ymax) en arcsec
        xmin, xmax = np.sort([dra0, dra1])
        ymin, ymax = np.sort([ddec0, ddec1])
        return xmin, xmax, ymin, ymax, (x_uc1, y_uc1)

    # -----------------------------
    # Dibujo de beams (dos modos)
    # -----------------------------
    def plot_beam_pixels(self, ax, beam_params, facecolor, edgecolor):
        """Dibuja el beam sobre ejes en PIXELES (proyección WCSAxes)."""
        if beam_params:
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            beam_x = xlim[0] + 0.05 * (xlim[1] - xlim[0])
            beam_y = ylim[0] + 0.05 * (ylim[1] - ylim[0])
            width_pix = beam_params['bmin'] / self.pixel_scale
            height_pix = beam_params['bmaj'] / self.pixel_scale
            beam_ellipse = Ellipse((beam_x, beam_y), width=width_pix, height=height_pix,
                                   angle=beam_params['bpa'], edgecolor=edgecolor, facecolor=facecolor,
                                   alpha=0.5, lw=1.5)
            ax.add_patch(beam_ellipse)

    def plot_beam_arcsec(self, ax, beam_params, facecolor, edgecolor, xmin, xmax, ymin, ymax):
        """Dibuja el beam sobre ejes en ARCSEC (ΔRA/ΔDec)."""
        if beam_params:
            # 5% de margen desde la esquina inferior izquierda (en unidades de los ejes: arcsec)
            bx = xmin + 0.05 * (xmax - xmin)
            by = ymin + 0.05 * (ymax - ymin)
            width = beam_params['bmin']  # arcsec
            height = beam_params['bmaj'] # arcsec
            beam_ellipse = Ellipse((bx, by), width=width, height=height,
                                   angle=beam_params['bpa'], edgecolor=edgecolor, facecolor=facecolor,
                                   alpha=0.5, lw=1.5)
            ax.add_patch(beam_ellipse)

    # -----------------------------
    # Lógica principal de plot
    # -----------------------------
    def plot(self, save_as=None, title=""):
        """Genera la visualización con opciones interactivas para ejes y overlays."""

        # ====== Preguntas interactivas (si aplica) ======
        if self.ask:
            try:
                resp = input("¿Mostrar ejes en ΔRA/ΔDec relativos a UC1? [s/N]: ").strip().lower()
                if resp == 's':
                    self.use_delta_coords = True
                elif resp == 'n' or resp == '':
                    self.use_delta_coords = False
            except Exception:
                pass

            try:
                resp = input("¿Mostrar la estrellita de UC1? [S/n]: ").strip().lower()
                if resp == 'n':
                    self.show_uc1 = False
                else:
                    self.show_uc1 = True
            except Exception:
                pass

            try:
                resp = input("¿Mostrar las líneas PA=126° y 216°? [S/n]: ").strip().lower()
                if resp == 'n':
                    self.show_pa_lines = False
                else:
                    self.show_pa_lines = True
            except Exception:
                pass

        # ====== Configuración de colores según momento ======
        if self.moment in ['m0', 'continuo']:
            cmap_base = 'gnuplot2'
            contour_color = 'white'
            star_color = 'lawngreen'
        elif self.moment in ['m1', 'm2']:
            cmap_base = 'jet'
            contour_color = 'black'
            star_color = 'fuchsia'
        else:
            cmap_base = 'gnuplot2'
            contour_color = 'white'
            star_color = 'yellow'

        # ====== Dos modos de render ======
        if not self.use_delta_coords:
            # ------------------
            #   MODO WCS NORMAL
            # ------------------
            fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': self.wcs_base})

            # Base
            im = ax.imshow(self.data_base, origin='lower', cmap=cmap_base)

            # Contornos si existen (ya reproyectados)
            if self.reprojected_contour is not None:
                vmin = np.nanmin(self.data_contour)
                vmax = np.nanmax(self.data_contour)
                if np.isfinite(vmin) and np.isfinite(vmax) and vmax > vmin:
                    levels = np.linspace(vmin, vmax, 7)
                    ax.contour(self.reprojected_contour, levels=levels, colors=contour_color,
                               linewidths=1, alpha=0.8)

            # Beams en pixeles
            self.plot_beam_pixels(ax, self.beam_base, facecolor='gray', edgecolor='black')
            if self.beam_contour:
                self.plot_beam_pixels(ax, self.beam_contour, facecolor='white', edgecolor='gray')

            # Label de la región
            if self.region_label:
                ax.text(0.95, 0.95, self.region_label, transform=ax.transAxes, fontsize=14,
                        color='white', ha='right', va='top',
                        bbox=dict(facecolor='black', alpha=0.5))

            # UC1 y líneas PA si aplica
            # Posición UC1 (píxeles)
            x_pix, y_pix = self.wcs_base.world_to_pixel(self.uc1_coord)

            if self.show_uc1:
                ax.scatter(x_pix, y_pix, facecolors='none', edgecolors=star_color, marker='*',
                           s=250, linewidths=1.5, zorder=10, transform=ax.get_transform('pixel'))
                ax.annotate("UC1", (x_pix + 5, y_pix + 5), color=star_color, fontsize=12,
                            weight='bold', zorder=11, transform=ax.get_transform('pixel'))

            if self.show_pa_lines:
                for pa in (126, 216):
                    length = 30  # en píxeles; ajusta si lo deseas
                    theta = np.deg2rad(pa)
                    dx = length * np.sin(theta)
                    dy = length * np.cos(theta)
                    x1, y1 = x_pix - dx, y_pix - dy
                    x2, y2 = x_pix + dx, y_pix + dy
                    ax.plot([x1, x2], [y1, y2],
                            transform=ax.get_transform('pixel'),
                            color='gray', linestyle='--', linewidth=1)
                    # Etiqueta
                    ax.text(x_pix - 0.8*dx, y_pix - 0.8*dy,
                            f"PA={pa}°",
                            transform=ax.get_transform('pixel'),
                            color='gray', fontsize=12, rotation_mode='anchor')

            ax.set_xlabel('Ascensión Recta (RA)')
            ax.set_ylabel('Declinación (Dec)')
            plt.colorbar(im, ax=ax, pad=0.05, label=self.colorbar_label)
            plt.title(title)

        else:
            # -------------------------------
            #   MODO ΔRA/ΔDec (arcsec)
            # -------------------------------
            fig, ax = plt.subplots(figsize=(10, 8))

            xmin, xmax, ymin, ymax, (x_uc1, y_uc1) = self._arcsec_offsets_extent()

            # Base con extent en arcsec (ΔRA, ΔDec)
            im = ax.imshow(self.data_base, origin='lower', cmap=cmap_base,
                           extent=(xmin, xmax, ymin, ymax), aspect='equal')

            # Contornos (ya reprojectados), mismo extent
            if self.reprojected_contour is not None:
                vmin = np.nanmin(self.data_contour)
                vmax = np.nanmax(self.data_contour)
                if np.isfinite(vmin) and np.isfinite(vmax) and vmax > vmin:
                    levels = np.linspace(vmin, vmax, 7)
                    ax.contour(self.reprojected_contour, levels=levels, colors=contour_color,
                               linewidths=1, alpha=0.8, extent=(xmin, xmax, ymin, ymax))

            # Beam en unidades de arcsec
            self.plot_beam_arcsec(ax, self.beam_base, facecolor='gray', edgecolor='black',
                                  xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
            if self.beam_contour:
                self.plot_beam_arcsec(ax, self.beam_contour, facecolor='white', edgecolor='gray',
                                      xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

            # Label de región
            if self.region_label:
                ax.text(0.95, 0.95, self.region_label, transform=ax.transAxes, fontsize=14,
                        color='white', ha='right', va='top',
                        bbox=dict(facecolor='black', alpha=0.5))

            # UC1 en el origen (0,0) y líneas PA si aplica
            if self.show_uc1:
                ax.scatter(0.0, 0.0, facecolors='none', edgecolors=star_color, marker='*',
                           s=250, linewidths=1.5, zorder=10)
                ax.annotate("UC1", (3.0, 3.0), color=star_color, fontsize=12, weight='bold', zorder=11)

            if self.show_pa_lines:
                for pa in (126, 216):
                    length_arcsec = 30.0  # longitud en arcsec; ajusta según escala de tu mapa
                    theta = np.deg2rad(pa)
                    dx = length_arcsec * np.sin(theta)  # ΔRA (este positivo)
                    dy = length_arcsec * np.cos(theta)  # ΔDec (norte positivo)
                    ax.plot([-dx, dx], [-dy, dy], color='gray', linestyle='--', linewidth=1)
                    ax.text(-0.8*dx, -0.8*dy, f"PA={pa}°", color='gray', fontsize=12, rotation_mode='anchor')

            ax.set_xlabel('ΔRA (arcsec)')
            ax.set_ylabel('ΔDec (arcsec)')
            plt.colorbar(im, ax=ax, pad=0.05, label=self.colorbar_label)
            plt.title(title)

        if save_as:
            plt.savefig(save_as, dpi=300, bbox_inches='tight')
            print(f"Imagen guardada como {save_as}")

        plt.show()


# -----------------------------
#   Ejemplo de uso rápido
# -----------------------------
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="FITSPlotter con ejes ΔRA/ΔDec y overlays opcionales.")
    p.add_argument("--image", required=True, help="FITS de imagen base")
    p.add_argument("--contours", default=None, help="FITS de contornos (opcional)")
    p.add_argument("--moment", default=None, help="m0, m1, m2 o continuo (opcional)")
    p.add_argument("--label", default=None, help="Etiqueta de región (opcional)")
    p.add_argument("--delta", action="store_true", help="Usar ejes en ΔRA/ΔDec relativos a UC1")
    p.add_argument("--no-ask", action="store_true", help="No preguntar en pantalla (usar flags)")
    p.add_argument("--hide-uc1", action="store_true", help="Oculta la estrellita de UC1")
    p.add_argument("--hide-pa", action="store_true", help="Oculta las líneas PA=126° y 216°")
    p.add_argument("--save", default=None, help="Ruta de salida para guardar la imagen (opcional)")
    args = p.parse_args()

    plotter = FITSPlotter(
        image_fits=args.image,
        contour_fits=args.contours,
        moment=args.moment,
        region_label=args.label,
        use_delta_coords=args.delta,
        show_uc1=(not args.hide_uc1),
        show_pa_lines=(not args.hide_pa),
        ask=(not args.no_ask)
    )
    plotter.plot(save_as=args.save, title=args.label or "")
