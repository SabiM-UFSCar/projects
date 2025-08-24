# vasp_data_viz/soc_dos_plotter.py
"""
Simulações Ab-initio de Materiais - SAbiM
==============================================================================================
Density of States with Spin-Orbit Coupling (SOC) Plotter
----------------------------------------------------------------------------------------------
This module provides functionality to plot the Density of States (DOS) for VASP calculations
that include Spin-Orbit Coupling (SOC)

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""

from pathlib import Path

from vasp_data_extractor import doscar_parsers


def plot_dos_soc(path_simulation_folder: Path, filename: str) -> None:
    path_doscar = path_simulation_folder.joinpath('DOSCAR')

    if not path_doscar.exists():
        raise FileNotFoundError(f"DOSCAR file not found in {path_simulation_folder}")
    if not path_doscar.is_file():
        raise ValueError(f"The path {path_doscar} is not a file.")
    
    # Extract DOS data from DOSCAR file
    energy, fermi_energy_delta, dos, integrated_dos, tables_orbitals_dos, index_table, list_qdt_per_ions = (
            doscar_parsers.read_doscar(path_doscar))

    print(f"Energy range: {energy[0]} to {energy[-1]} eV")


path_sim = Path('/home/murbach/Documents/UResearch/Projects/2024_2D_Monochalcogenides/Simulations/Results/Raw_Outputs/DensityOfStatesStudy/SOCMQLowestEnergy/AlS/P6m2')
plot_dos_soc(path_sim, 'dos_soc_plot.png')