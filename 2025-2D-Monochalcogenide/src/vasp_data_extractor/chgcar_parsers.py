# vasp_data_extractor/chgcar_parsers.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
CHGCAR - Parsing information from CHGCAR file.

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""

import os
import sys
import numpy as np


def read_chgcar(chgcar_file):
    """
    Parse a VASP CHGCAR file to extract charge density data and structural information.
    
    Reads a CHGCAR file containing electron charge density data from VASP calculations
    along with crystal structure information. Returns the charge density grid and
    structural parameters including atomic coordinates and lattice vectors.

    Args:
        chgcar_file (str): Path to the CHGCAR file to be read.

    Returns:
        tuple: A tuple containing:
            - chg (numpy.ndarray): 3D array of charge density values with shape (x_points, y_points, z_points)
            - coord_elements (list): List of dictionaries with atomic coordinates and element information
            - grid (numpy.ndarray): Grid dimensions [nx, ny, nz]
            - vec_a (numpy.ndarray): First lattice vector
            - vec_b (numpy.ndarray): Second lattice vector
            - vec_c (numpy.ndarray): Third lattice vector

    Raises:
        SystemExit: If the file doesn't exist or is not a valid file.
    """
    # Validate file existence and type before processing
    if not os.path.exists(chgcar_file):
        print('File not found')
        sys.exit(1)
    if not os.path.isfile(chgcar_file):
        print('Not a file')
        sys.exit(1)

    # Open file for reading
    chgcar = open(chgcar_file, 'r')
    
    # Read header information (system description and scaling factor)
    system = chgcar.readline().strip()
    scale_factor = chgcar.readline().strip().split()
    
    # Read lattice vectors from next three lines
    vec_a = chgcar.readline().strip().split()
    vec_b = chgcar.readline().strip().split()
    vec_c = chgcar.readline().strip().split()

    # Convert lattice vectors to numpy arrays with high precision
    vec_a = np.array([np.float64(vec_a[0]), np.float64(vec_a[1]), np.float64(vec_a[2])])
    vec_b = np.array([np.float64(vec_b[0]), np.float64(vec_b[1]), np.float64(vec_b[2])])
    vec_c = np.array([np.float64(vec_c[0]), np.float64(vec_c[1]), np.float64(vec_c[2])])

    # Read element symbols and their counts
    elements = chgcar.readline().strip().split()
    qtd_elements = chgcar.readline().strip().split()
    
    # Check for selective dynamics line (optional in CHGCAR)
    selective_dynamics = chgcar.readline().strip().split()
    
    # Calculate total number of atoms
    qtd_sum = 0
    for qtd in qtd_elements:
        qtd_sum += int(qtd)

    # Read atomic coordinates for all atoms
    coord_elements = []
    for count, element in enumerate(elements):
        # Read coordinates for each atom of current element type
        for i in range(1, int(qtd_elements[count]) + 1):
            coord_ = chgcar.readline().strip().split()
            element_i = {
                'Element': element,
                'x': coord_[0],
                'y': coord_[1],
                'z': coord_[2],
            }
            coord_elements.append(element_i)

    # Skip empty line (separator between structure and charge data)
    _ = chgcar.readline().strip().split()
    
    # Read grid dimensions for charge density data
    grid_string = chgcar.readline().strip().split()

    # Parse grid dimensions and prepare array for charge density
    grid = np.array([int(grid_string[0]), int(grid_string[1]), int(grid_string[2])])
    z_points = int(grid_string[2])
    y_points = int(grid_string[1])
    x_points = int(grid_string[0])
    
    # Initialize empty array for charge density values
    chg = np.empty((x_points, y_points, z_points))
    
    # Read charge density values in nested loops (z then y then x)
    for zz in range(z_points):
        for yy in range(y_points):
            # Read one line of x-points for current y and z coordinates
            chg[:, yy, zz] = np.fromfile(chgcar, count=x_points, sep=' ')

    return chg, coord_elements, grid, vec_a, vec_b, vec_c
