"""
fits_plotter.py
===============
Re-exporta FITSPlotter desde myastroutilities.plotting.fits_plotter.

El código canónico vive en el paquete myastroutilities. Instálalo con:

    pip install -e /home/jennifer/myastroutilities

o bien:

    pip install git+https://github.com/jennifergc/myastroutilities.git

Uso en notebooks y scripts:

    from myastroutilities.plotting.fits_plotter import FITSPlotter
    # o, usando este archivo de compatibilidad:
    from fits_plotter import FITSPlotter
"""
from myastroutilities.plotting.fits_plotter import FITSPlotter  # noqa: F401

if __name__ == "__main__":
    # Permite ejecutar como CLI directamente
    from myastroutilities.plotting.fits_plotter import __name__ as _  # noqa: F401
    import runpy
    runpy.run_module("myastroutilities.plotting.fits_plotter", run_name="__main__")
