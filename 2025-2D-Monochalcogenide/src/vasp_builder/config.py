# vasp_builder/config.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
VASP Input Configuration File

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024

This module contains all constant variables and default parameters used by vasp_builder scripts
for generating VASP simulation input files (INCAR, POSCAR, KPOINTS, POTCAR).

All production scripts should import these settings rather than hard-coding parameters.
"""

LIST_ELEMENTS = [
    'Al', 'As', 'Ga', 'Ge', 'In', 'P', 'S', 'Sb', 'Se', 'Si', 'Sn', 'Te'
]

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

LIST_ORDERED_BC_TAGS = [
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