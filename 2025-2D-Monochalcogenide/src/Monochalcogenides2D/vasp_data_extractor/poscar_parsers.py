# vasp_data_extractor/poscar_parsers.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
POSCAR - Parsing information from POSCAR file.

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""

import os

import numpy as np
from ase import Atom, Atoms


class ReadPOSCAR(object):
    """
    A parser for VASP POSCAR files that extracts structural information.

    This class reads and parses POSCAR files (VASP input structure files),
    extracting information about the crystal structure, atomic positions,
    and optional features like selective dynamics. It can create an ASE
    Atoms object for compatibility with atomic simulation environments.

    Args:
        poscar_path (str): Path to the POSCAR file to be parsed.

    Raises:
        FileNotFoundError: If the specified POSCAR file does not exist.
        TypeError: If the provided path is not a string.

    Attributes:
        get_ions_positions(): Returns parsed atomic positions.
        get_lattice_vectors(): Returns lattice vectors as 3x3 list.
        get_atoms(): Returns ASE Atoms object representation.
        get_total_species(): Returns total number of atoms.
        get_ions(): Returns ions per species count.
        get_species_ions_per_species(): Returns element composition details.

    Example:
        >>> parser = ReadPOSCAR('POSCAR')
        >>> parser.create_atoms()
        >>> atoms = parser.get_atoms()
        >>> print(atoms.get_positions())
    """
    def __init__(self, poscar_path=""):
        self._poscar_path = None
        # Mandatory
        self._system_description = None  # line 1 - to line 1
        self._scaling_factor = None  # line 2 - to line 2
        self._lattice_vectors = []  # line 3 - to line 5
        self._ions_per_species = []  # line (6,7) - to line (6,7)
        self._coordinates_mode = None  # line (7, 8, 9) - to line (7, 8,9)
        self._list_ions_positions = []  # line (8, 9, 10) - to line (8+n, 9+n, 10+n)
        # Optional
        self._list_ions_positions_flag = []
        self._species_name = []  # line 6 - to line 6
        self._selective_dynamics = False  # line (7,8) - to line (7,8)  after the "Ions per species"
        self._lattice_velocities = None
        self._ions_velocities = None
        self._md_extra = None

        # Control
        self._total_species = 0
        self._line_ions_per_species = 0
        self._type_coordinates_mode = [
            'cartesian', 'direct'
        ]
        self._atoms = Atoms()

        self._structure_file = {
            1: lambda number, content: self.__set_value('_system_description', number, content),
            2: lambda number, content: self.__set_value('_scaling_factor', number, content),
            3: lambda number, content: self.__set_lattice_vector(number, content),
            4: lambda number, content: self.__set_lattice_vector(number, content),
            5: lambda number, content: self.__set_lattice_vector(number, content),
            6: lambda number, content: self.__process_line_content_ions_information(number, content),
            7: lambda number, content: self.__process_line_content_ions_information(number, content),
        }

        if isinstance(poscar_path, str):
            if os.path.isfile(poscar_path):
                self._poscar_path = poscar_path
                self.read_file()
            else:
                raise FileNotFoundError(f"The file '{poscar_path}' does not exist.")
        else:
            raise TypeError("The 'poscar_path' must be a string.")

    def get_ions_positions(self):
        return self._list_ions_positions

    def get_lattice_vectors(self):
        return self._lattice_vectors

    def get_atoms(self):
        return self._atoms

    def get_total_species(self):
        return self._total_species

    def get_ions(self):
        return self._ions_per_species

    def get_species_ions_per_species(self):
        data = []
        for _ions in range(len(self._ions_per_species)):
            element_info = {
                'element': self._species_name[_ions],
                'ions_per_specie': self._ions_per_species[_ions]
            }
            data.append(element_info)
        return data

    def __process_line_content_modes_coordinates(self, line_number, value):
        if len(value) > 0 and (value[0] == 'S' or value[0] == 's'):
            self._selective_dynamics = True

    def __process_line_content_ions_information(self, line_number, value):
        parts = value.split()
        if len(parts) > 0:
            if line_number == 6:
                if parts[0].isalpha():
                    # print('The names of the chemical species have been provided')
                    for species in parts:
                        self._species_name.append(species)
                else:
                    # print('The names of the chemical species have not been provided.')
                    safe_element_name = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
                    j = 0
                    for species in parts:
                        self._total_species += int(species)
                        self._line_ions_per_species = line_number
                        self._ions_per_species.append(species)
                        self._species_name.append(safe_element_name[j])
                        j += 1
            elif line_number == 7:
                if parts[0].isdigit():
                    for species in parts:
                        self._total_species += int(species)
                        self._line_ions_per_species = line_number
                        self._ions_per_species.append(species)

    def __set_lattice_vector(self, line_number, value):
        parts = value.strip().split()
        axis_line = []
        for axis in parts:
            axis_line.append(self.__format_float_values(axis))
        self._lattice_vectors.append(axis_line)

    def __set_value(self, name, line_number, value):
        if hasattr(self, name):
            if name == '_scaling_factor':
                setattr(self, name, self.__format_float_values(value))
            else:
                setattr(self, name, value.strip())
        else:
            print(f"The variable '{name}' doesn't exist")

    @staticmethod
    def __format_float_values(value):
        try:
            return np.float64(np.format_float_positional(np.float64(value), precision=16, unique=True, min_digits=16))
        except Exception as e:
            print(f'Error: {e}')
            return value

    def __set_selective_dynamics(self, line_number, value):
        value = value.strip()
        if value[0] == 'S' or value[0] == 's':
            self._selective_dynamics = True
        else:
            self._coordinates_mode = value

    def __set_coordinates_mode(self, line_number, value):
        value = value.strip()
        self._coordinates_mode = value

    def __set_ions_positions(self, line_number, positions):
        formatted_positions = positions.split()
        positions = [
            self.__format_float_values(formatted_positions[0]),
            self.__format_float_values(formatted_positions[1]),
            self.__format_float_values(formatted_positions[2])
        ]
        self._list_ions_positions.append(positions)
        if self._selective_dynamics:
            positions_flag = [
                formatted_positions[3],
                formatted_positions[4],
                formatted_positions[5]
            ]
            self._list_ions_positions_flag.append(positions_flag)

    def read_file(self):
        try:
            with open(self._poscar_path, "r") as POSCAR:
                for line_number, line_content in enumerate(POSCAR, start=1):
                    if line_content.strip() == '':
                        break
                    else:
                        formatted_line_content = line_content.strip()
                        # print(f'Line {line_number}: {formatted_line_content}')
                        if self._line_ions_per_species == 0:
                            if line_number in self._structure_file:
                                self._structure_file[line_number](line_number, line_content)
                        else:
                            # The line containing 'selective dynamics' must necessarily come after the information about
                            # ions per species.
                            if line_number == (self._line_ions_per_species + 1):
                                self.__set_selective_dynamics(line_number, line_content)
                            else:
                                if formatted_line_content.lower() in self._type_coordinates_mode:
                                    self.__set_coordinates_mode(line_number, line_content)
                                else:
                                    self.__set_ions_positions(line_number, line_content)
        except Exception as e:
            print("An error occurred while reading the file:", e)

    def create_atoms(self):
        index_atom = 0
        for i in range(len(self._species_name)):
            symbol = self._species_name[i]
            for j in range(int(self._ions_per_species[i])):
                created_atom = Atom(
                    symbol,
                    self._list_ions_positions[index_atom]
                )
                self._atoms.append(created_atom)
                index_atom += 1

        self._atoms.set_cell(self._lattice_vectors)
