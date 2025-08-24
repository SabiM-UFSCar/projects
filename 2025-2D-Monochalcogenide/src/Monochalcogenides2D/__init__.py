"""
Simulações Ab-initio de Materiais - SAbiM
=======================
Monochalcogenides2D

Computational tools for VASP-based simulations and analysis of 2D monochalcogenides,
developed by SAbiM for materials science research.

Modules:
--------
- common: configuration and utility functions
- vasp_io: parsers and I/O tools for VASP data
"""

from importlib.metadata import version, PackageNotFoundError

try:
    from importlib.metadata import version, PackageNotFoundError
    __version__ = version("Monochalcogenides2D")
except PackageNotFoundError:
    # fallback local dev
    __version__ = "0.0.0.dev"

__all__ = ["__version__"]
