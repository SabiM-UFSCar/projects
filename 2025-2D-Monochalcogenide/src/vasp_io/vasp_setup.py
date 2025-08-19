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
from utils import get_mq_elements, logger, log_generate_inputs, progress_bar_show
from poscar_writer import run_write_poscar
from incar_writer import run_write_incar
from kpoints_writer import run_kpoints_writer
from config import LIST_SP, LIST_MQ


@log_generate_inputs
def run_generate_inputs(path_output_folder: str):
    """Orchestrates VASP input generation for multiple space groups and material systems.

    Creates nested directory structure and generates POSCAR/INCAR files
    for all combinations of space groups in LIST_SP and materials in LIST_MQ.
    Serves as the top-level workflow controller for input file generation.

    Args:
        path_output_folder: Root directory for output file hierarchy

    Returns:
        None (writes files to disk)

    Raises:
        OSError: If directory creation fails
        RuntimeError: Propagated from file generation functions

    Example:
        >>> run_generate_inputs('vasp_simulations')
        Generates input files for all material/space group combinations
    """
    # Initialize root output directory with safe creation
    # Critical: Ensures base path exists before nested generation
    path_output = Path(path_output_folder)
    path_output.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Output directory set to: {path_output.resolve()}")
    
    system_count = 0
    progress_bar_show(system_count)
    # Process each space group in predefined list
    # Why: Different crystal structures require distinct templates
    for sp in LIST_SP:
        # Initialize path placeholder for current space group
        path_output_sp = ""

        # Process each material system in predefined list
        # Note: Materials are represented as string identifiers (e.g., "NaCl")
        for mq in LIST_MQ:
            # Create material-specific subdirectory under space group
            # Structure: root/space_group/material_system/
            path_output_sp = path_output.joinpath(sp, mq)
            path_output_sp.mkdir(parents=True, exist_ok=True)
            logger.info(f"Processing space group: {sp} with material: {mq}")

            # Generate POSCAR file with space-group-appropriate template
            # Note: get_mq_elements() converts material ID to element list
            if run_write_poscar(path_output_sp, get_mq_elements(mq), sp):
                logger.info(f"POSCAR file created successfully for {mq} in space group {sp}.")
            else:
                logger.info(f"Failed to create POSCAR file for {mq} in space group {sp}.")
                raise RuntimeError(f"POSCAR generation failed for {mq} in space group {sp}.")
     
            # Generate matching INCAR file with material-specific parameters
            # Critical: Must run after POSCAR for folder structure consistency
            run_write_incar(path_output_sp, get_mq_elements(mq))

            # Generate matching KPOINTS file with material-specific parameters
            # Critical: Must run after POSCAR for folder structure consistency
            run_kpoints_writer(path_output_sp)

            system_count += 1
            progress_bar_show(system_count)
            logger.info(f"Completed input generation for {mq} in space group {sp}. Total systems: {system_count}")
            logger.info("#########################################################################################")


# Execute the script
# Entry point: Generates all inputs under './vasp_outputs' directory
# run_generate_inputs("./vasp_outputs")
