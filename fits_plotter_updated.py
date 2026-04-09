"""
fits_plotter_updated.py  [DEPRECADO]
=====================================
Este archivo ha sido fusionado en fits_plotter.py.
Importa directamente desde fits_plotter.py en su lugar.

    from fits_plotter import FITSPlotter
"""
import warnings
warnings.warn(
    "fits_plotter_updated.py está deprecado. Usa fits_plotter.py en su lugar:\n"
    "    from fits_plotter import FITSPlotter",
    DeprecationWarning,
    stacklevel=2,
)

from fits_plotter import FITSPlotter  # noqa: F401 — re-exportado por compatibilidad
