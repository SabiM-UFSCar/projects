# common/config.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
VASP Input Configuration File

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024

This module contains all constant variables and default parameters used by the project

All production scripts should import these settings rather than hard-coding parameters.
"""

from pathlib import Path
from typing import Final, List, Set

# ============================================================
# Configuration of materials (monochalcogenides) and
# space groups to be studied in the simulations
# ============================================================
LIST_ELEMENTS: Final[List[str]] = [
    'Al', 'As', 'Ga', 'Ge', 'In', 'P', 'S', 'Sb', 'Se', 'Si', 'Sn', 'Te'
]

LIST_SP: Final[List[str]]  = [
    'P3m1_alpha',
    'P3m1_beta',
    'P6m2',
    'P_1_alpha',
    'P_1_beta',
    'P2_1c',
    'P4_nmm',
    'Pbcm',
    'Ph_like',
    'Pmmn',
    'Pmna',
    'Aem2',
    'C2_m'
]

LIST_MQ: Final[List[str]] = [
    # Group 1: Al, Ga, In compounds
    "AlS", "AlSe", "AlTe",
    "GaS", "GaSe", "GaTe",
    "InS", "InSe", "InTe",
    
    # Group 2: Ge, Si, Sn compounds
    "GeS", "GeSe", "GeTe",
    "SiS", "SiSe", "SiTe",
    "SnS", "SnSe", "SnTe",
    
    # Group 3: As, P, Sb compounds
    "AsS", "AsSe", "AsTe",
    "PS", "PSe", "PTe",
    "SbS", "SbSe", "SbTe"
]

TOTAL_MQ_SYSTEMS: Final[int] = len(LIST_MQ) * len(LIST_SP)

LIST_ORDERED_BC_TAGS: Final[List[str]] = [
    "SYSTEM",
    "ENCUT",
    "ALGO",
    "NELMIN",
    "NELM",
    "NELMDL",
    "EDIFF",
    "AMIX",
    "BMIX",
    "PREC",
    "ISPIN",
    "LASPH",
    "LREAL",
    "NSW",
    "#EDIFFG",
    "IBRION",
    "ISMEAR",
    "SIGMA",
    "LORBIT",
    "NWRITE",
    "LWAVE",
    "LCHARG",
    "LAECHG",
    "NGXF",
    "NGYF",
    "NGZF",
    "NCORE",
    "LPLANE"
]


# ============================================================
# Configuration of input file parameters (INCAR, POTCAR,
# POSCAR, KPOINTS, and related variables)
# ============================================================
LIST_ELEMENT_POTCAR_D_GW: Final[List[str]] = ['Sn', 'In']
RATIO_FACTOR: Final[float] = 2.0
POSCAR_LINES_TO_MODIFY: Final[Set[int]] = {1, 6}
RK_FACTOR: Final[int] = 30

# ============================================================
# Configuration of project directory paths (e.g., logs,
# templates, POTCAR libraries, output directories, etc.)
# ============================================================
PACKAGE_ROOT: Final[Path] = Path(__file__).parent.parent

PATH_FOLDER_LOG: Final[Path] = PACKAGE_ROOT.joinpath("logs")
PATH_FOLDER_OUTPUT: Final[Path] = PACKAGE_ROOT.joinpath("output")
PATH_FOLDER_TEMPLATE: Final[Path] = PACKAGE_ROOT.joinpath("templates")

PATH_FOLDER_POTPAW: Final[Path] = Path("potpaw_PBE_5_4_2020_01_15")  # Path to the folder containing POT PAW files
PATH_FILE_INCAR_PATTERN: Final[Path] = PATH_FOLDER_TEMPLATE.joinpath("relaxation/INCAR_PATTERN")
PATH_FOLDER_POSCAR_PATTERN: Final[Path] = PATH_FOLDER_TEMPLATE.joinpath("relaxation/POSCAR")
NAME_FILE_POSCAR_PATTERN: Final[str] = "POSCAR_PATTERN"




