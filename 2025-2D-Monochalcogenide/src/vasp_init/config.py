# vasp_init/config.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
VASP Input Configuration File

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024

This module contains all constant variables and default parameters used by vasp_io scripts
for generating VASP simulation input files (INCAR, POSCAR, KPOINTS, POTCAR).

All production scripts should import these settings rather than hard-coding parameters.
"""

from pathlib import Path

# VASP SETUP Parameters
LIST_SP = [
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

LIST_MQ = [
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

TOTAL_MQ_SYSTEMS = len(LIST_MQ) * len(LIST_SP)

# VASP INCAR Generation Parameters
PATH_FOLDER_POTPAW = Path("/PotPaw_Folder_Path")  # Path to the folder containing POTPAW files
LIST_POTCAR_D_GW = ['Sn', 'In']
RATIO_FACTOR = 2.0
INCAR_FILE_TEMPLATE = Path("./vasp_templates/INCAR_PATTERN")

# VASP POSCAR Generation Parameters
POSCAR_FILE_TEMPLATE = "POSCAR_PATTERN"
PATH_FOLDER_TEMPLATE = Path("./vasp_templates/POSCAR")
LINES_TO_MODIFY = {1, 6}

# VASP KPOINTS Generation Parameters
RKFACTOR = 30
