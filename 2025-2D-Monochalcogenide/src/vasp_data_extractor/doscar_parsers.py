# vasp_data_extractor/doscar_parsers.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
DOSCAR - Parsing information from DOSCAR file.

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""

import os
import numpy as np
from poscar_parsers  import ReadPOSCAR as read_poscar


def read_doscar(doscar_file):
    """
    Parses a VASP DOSCAR file to extract density of states (DOS) information.
    
    This function reads a VASP DOSCAR file and extracts total DOS, integrated DOS,
    and orbital-projected DOS data. It also retrieves structural information from
    the associated POSCAR file to properly interpret atomic contributions.

    Args:
        doscar_file (str): Path to the DOSCAR file to be read.

    Returns:
        tuple: A tuple containing:
            - energy (list): Energy values for DOS points
            - fermi_energy_delta (list): Energy values relative to Fermi level
            - dos (list): Total density of states values
            - integrated_DOS (list): Integrated density of states values
            - orbitals_table (list): Orbital-resolved DOS for each atom
            - index_table (int): Number of orbital tables processed
            - POSCAR_IONS_PER_SPECIES (list): Ion counts per species from POSCAR

    Raises:
        FileNotFoundError: If the DOSCAR file doesn't exist.
        ValueError: If file format is unexpected or inconsistent.
    """
    # Get directory containing DOSCAR file for POSCAR lookup
    _SIM_FOLDER_PATH = os.path.dirname(doscar_file)

    # Verify file exists before attempting to read
    if os.path.isfile(doscar_file):
        doscar = open(doscar_file, 'r')

        # Parse header information from first five lines
        IONS_EMPTY_SPHERES, IONS, PDOS, NCDIJ = doscar.readline().strip().split()
        VOL_UNIT_CELL, BASIC_VECTORS_A, BASIC_VECTORS_B, BASIC_VECTORS_C, POTIM = doscar.readline().strip().split()
        INITIAL_TEMPERATURE = doscar.readline().strip()
        COORDINATES_MODE = doscar.readline().strip()
        SYSTEM_INCAR = doscar.readline().strip()
        # Extract DOS-specific parameters including Fermi energy
        EMAX, EMIN, NEDOS, EFERMI, WEIGHT = doscar.readline().strip().split()

        # Process total DOS data (energy, DOS, integrated DOS)
        _NUM_DOS_LINES = int(NEDOS) + 1
        energy = []
        fermi_energy_delta = []
        dos = []
        integrated_DOS = []
        # Read and convert each line of DOS data
        for i in range(1, _NUM_DOS_LINES):
            content = doscar.readline().strip().split()
            energy.append(np.float64(content[0]))
            fermi_energy_delta.append(np.float64(content[0]) - np.float64(EFERMI))
            dos.append(np.float64(content[1]))
            integrated_DOS.append(np.float64(content[2]))

        # Read POSCAR to get ion counts for parsing atom-resolved DOS
        poscar = os.path.join(_SIM_FOLDER_PATH, 'POSCAR')
        poscar_obj = read_poscar(poscar)
        POSCAR_IONS_PER_SPECIES = poscar_obj.get_ions()
        POSCAR_TOTAL_IONS = poscar_obj.get_total_species()

        # Process orbital-projected DOS for each atom
        index_table = 0
        tables_orbitals_dos = [[] for _ in range(int(POSCAR_TOTAL_IONS))]
        # Iterate through each atom type and each atom
        for quantity in POSCAR_IONS_PER_SPECIES:
            for j in range(int(quantity)):
                # Skip header line for each atom's DOS section
                doscar.readline().strip()  # N/A EMAX, EMIN, NEDOS, EFERMI, WEIGHT
                tables_orbitals_dos[index_table] = []
                # Read all DOS points for current atom
                for i in range(1, _NUM_DOS_LINES):
                    line = doscar.readline().strip()
                    tables_orbitals_dos[index_table].append(line)
                index_table += 1

        doscar.close()

        # Convert string data to numerical values for orbital tables
        converted_orbitals_table = [[] for _ in range(index_table)]
        for i in range(index_table):
            converted_orbitals_table[i] = [[np.float64(num) for num in line.split()] for line in tables_orbitals_dos[i]]

        # Extract orbital data (excluding energy column)
        orbitals_table = [[] for _ in range(index_table)]
        for i in range(index_table):
            orbitals_table[i] = [line[1:] for line in converted_orbitals_table[i]]

        return (energy, fermi_energy_delta, dos, integrated_DOS, orbitals_table, index_table,
                POSCAR_IONS_PER_SPECIES)


def sum_orbitals_dos(*tables):
    """
    Sums orbital-projected DOS data across multiple tables.
    
    This function combines DOS data from multiple orbital tables (typically from different atoms)
    by summing corresponding orbital contributions. It handles the specific VASP format where
    each orbital has 4 columns of data (s, p, d, f components).

    Args:
        *tables: Variable number of orbital DOS tables to be summed.

    Returns:
        list: A list of lists where each sublist contains summed DOS values for each energy point,
              with the total DOS inserted as the first element.

    Example:
        >>> table1 = [[1, 2, 3, 4], [5, 6, 7, 8]]
        >>> table2 = [[2, 3, 4, 5], [6, 7, 8, 9]]
        >>> sum_orbitals_dos(table1, table2)
        [[12, 5, 7, 9], [30, 11, 15, 19]]
    """
    # Determine orbital structure from first table
    t_1number_col = len(tables[0][0])
    qtd_orbitals = int(t_1number_col / 4)  # Each orbital has 4 columns in VASP
    first_col_dos_orbital = 0

    # Identify which columns to sum (first column of each orbital group)
    list_col_sum = []
    for i in range(qtd_orbitals):
        list_col_sum.append(first_col_dos_orbital + (i * 4))

    # Reorganize data by orbital type across all tables
    result_orbitals_dos = []
    for lines in zip(*tables):
        new_lines = [[line[i] for i in list_col_sum] for line in lines]
        result_orbitals_dos.append(new_lines)

    # Sum orbital contributions across all tables
    result_sum_orbitals = []
    for lines in result_orbitals_dos:
        sum_cols = [sum(cols) for cols in zip(*lines)]
        result_sum_orbitals.append(sum_cols)

    # Calculate total DOS for each energy point
    sum_cols_orbitals = []
    for lines in result_sum_orbitals:
        sum_cols = sum(lines)
        sum_cols_orbitals.append(sum_cols)

    # Insert total DOS as first element in each result line
    for line_result, compound_dos_sum in zip(result_sum_orbitals, sum_cols_orbitals):
        line_result.insert(0, compound_dos_sum)

    return result_sum_orbitals