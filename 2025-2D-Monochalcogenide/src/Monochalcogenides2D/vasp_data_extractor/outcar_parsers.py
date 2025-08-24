# vasp_data_extractor/outcar_parsers.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
OUTCAR - Parsing information from OUTCAR file.

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""

import mmap
import os
import re

def read_outcar_map(path_outcar):
    """
    Creates a memory-mapped view of an OUTCAR file for efficient large file reading.
    
    Memory mapping allows efficient random access to large OUTCAR files without
    loading the entire file into memory. This is particularly useful for VASP
    output files which can be several gigabytes in size.

    Args:
        path_outcar (str): Path to the OUTCAR file to memory map.

    Returns:
        mmap.mmap: Memory-mapped file object for efficient reading.

    Example:
        >>> outcar_map = read_outcar_map('OUTCAR')
        >>> print(outcar_map.size())
        10485760  # File size in bytes
    """
    # Open file in binary mode for memory mapping
    with open(path_outcar, 'rb') as OUTCAR_M:
        # Read entire file content (optional, not used later)
        content_file_m = OUTCAR_M.read()
        # Create memory map for efficient large file access
        file_map_m = mmap.mmap(OUTCAR_M.fileno(), 0, access=mmap.ACCESS_READ)
    return file_map_m


def get_number_grid(path_outcar):
    """
    Extracts grid dimensions (NGXF, NGYF, NGZF) from a VASP OUTCAR file.
    
    Parses the OUTCAR file to find the FFT grid dimensions used in the VASP
    calculation. These values are important for understanding the resolution
    of charge density and potential grids.

    Args:
        path_outcar (str): Path to the OUTCAR file to parse.

    Returns:
        tuple: A tuple containing three strings representing NGXF, NGYF, and NGZF values.

    Raises:
        FileNotFoundError: If the OUTCAR file does not exist.
        AttributeError: If the grid dimension patterns are not found in the file.

    Example:
        >>> get_number_grid('OUTCAR')
        ('64', '64', '128')  # Typical grid dimensions
    """
    # Verify file existence before attempting to read
    if os.path.exists(path_outcar):
        # Create memory-mapped view of OUTCAR file for efficient searching
        outcar_file_map = read_outcar_map(path_outcar)
        
        # Compile pattern to locate grid dimension information in file
        pattern_search = re.compile(b' {3}dimension x,y,z NGXF')
        
        # Search for pattern in memory-mapped file
        for result in pattern_search.finditer(outcar_file_map):
            start_r = result.start()
            end_r = result.end()

            # Extract the complete line containing the grid dimension information
            line_start = outcar_file_map.rfind(b'\n', 0, start_r) + 1
            line_end = outcar_file_map.find(b'\n', end_r)
            line_string = outcar_file_map[line_start:line_end].decode('utf-8')
            
            # Compile patterns to extract individual grid dimension values
            ngxf_line_fetch = re.compile(r'(NGXF=)([\r\n\t\f\v ]+)(\d{1,3})')
            ngyf_line_fetch = re.compile(r'(NGYF=)([\r\n\t\f\v ]+)(\d{1,3})')
            ngzf_line_fetch = re.compile(r'(NGZF=)([\r\n\t\f\v ]+)(\d{1,3})')
            
            # Extract each grid dimension value using regex patterns
            ngxf_string = re.search(ngxf_line_fetch, line_string)
            ngyf_string = re.search(ngyf_line_fetch, line_string)
            ngzf_string = re.search(ngzf_line_fetch, line_string)
            
            # Return the three grid dimension values
            return ngxf_string.group(3), ngyf_string.group(3), ngzf_string.group(3)