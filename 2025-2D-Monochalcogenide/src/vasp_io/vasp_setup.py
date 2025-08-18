# vasp_io/vasp_setup.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
VASP - This script is designed to generate input files for VASP calculations.

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""

from pathlib import Path
from utils import get_mq_elements, logger, log_generate_inputs
from poscar_writer import run_write_poscar
from incar_writer import run_write_incar


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

@log_generate_inputs
def run_generate_inputs(path_output_folder: str):
    """
    Run the VASP input generation script.
    This function is a wrapper for the main function in the vasp_setup module.
    """
    path_output = Path(path_output_folder)
    path_output.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Output directory set to: {path_output.resolve()}")
    for sp in LIST_SP:
        path_output_sp = ""
        for mq in LIST_MQ:
            path_output_sp = path_output.joinpath(sp, mq)
            path_output_sp.mkdir(parents=True, exist_ok=True)
            logger.info(f"Processing space group: {sp} with material: {mq}")
            if run_write_poscar(path_output_sp, get_mq_elements(mq), sp):
                print(f"POSCAR file created successfully for {mq} in space group {sp}.")
            else:
                print(f"Failed to create POSCAR file for {mq} in space group {sp}.")
            # Here you would call the function to write the INCAR file
            run_write_incar(path_output_sp, get_mq_elements(mq))

# Execute the script
run_generate_inputs("./vasp_outputs")
