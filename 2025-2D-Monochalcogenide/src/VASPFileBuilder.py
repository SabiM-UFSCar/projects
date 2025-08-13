import os
import re
import sys

from CORE import CONST as C
from VASPStructuresFile import KPOINTSCalculator
from VASPStructuresFile.POTCARSearch import POTCARScanner


class VASPFileCreator:
    """
    Class responsible for creating simulation files for pyVASP, such as POSCAR, INCAR, and POTCAR.
    """

    def __init__(self, path_folder, incar_pattern, poscar_pattern):
        """
        Initializer of the class.
        :param path_folder: Directory path where the files will be generated.
        :param incar_pattern: INCAR file pattern.
        :param poscar_pattern: POSCAR file pattern.
        """

        # Configuration attributes
        self._elem_m = None
        self._elem_q = None
        self._ratio_factor = 0.0
        self._incar_encut = 0.0
        self._elem_m_enmax = 0.0
        self._elem_q_enmax = 0.0
        self._structure = None
        self._pattern_potpaw = '_GW'
        self._list_potcar_pattern_for_elements = []

        # Paths of file patterns
        self._file_incar_pattern = os.path.join(C.PATH_FOLDER_INCAR_PATTERN, incar_pattern)
        self._file_poscar_pattern = os.path.join(C.PATH_FOLDER_POSCAR_PATTERN, poscar_pattern)

        # Check the existence of files
        # if not os.path.isfile(self._file_incar_pattern) or not os.path.isfile(self._file_poscar_pattern) or not os.path.isdir(path_folder):
        #             sys.exit(1)
        if not os.path.isfile(self._file_incar_pattern):
            sys.exit(1)
        if not os.path.isfile(self._file_poscar_pattern):
            sys.exit(1)
        if os.path.isdir(path_folder):
            self._path_folder = path_folder
        else:
            sys.exit(1)

    def set_elements(self, elements):
        """
        Sets the elements to be used in the simulation.
        :param elements: List of elements.
        """
        self._elem_m = elements[0]
        self._elem_q = elements[1]

    def set_structure(self, structure):
        """
        Sets the structure of the simulation.
        :param structure: Name of the structure.
        """
        self._structure = structure

    def set_ratio_factor(self, ratio_factor):
        """
        Sets the proportion factor.
        :param ratio_factor: Proportion factor.
        """
        self._ratio_factor = ratio_factor

    def _get_ratio_factor(self):
        """
        Gets the proportion factor.
        :return: Proportion factor.
        """
        return self._ratio_factor

    def _set_incar_encut(self, incar_encut):
        """
        Sets the ENCUT value for the INCAR file.
        :param incar_encut: ENCUT value.
        """
        self._incar_encut = incar_encut

    def _get_incar_encut(self):
        """
        Gets the ENCUT value for the INCAR file.
        :return: ENCUT value.
        """
        return self._incar_encut

    def _set_elem_m_enmax(self, elem_m_enmax):
        """
        Sets the ENMAX value for element M.
        :param elem_m_enmax: ENMAX value for element M.
        """
        self._elem_m_enmax = elem_m_enmax

    def _get_elem_m_enmax(self):
        """
        Gets the ENMAX value for element M.
        :return: ENMAX value for element M.
        """
        return self._elem_m_enmax

    def _set_elem_q_enmax(self, elem_q_enmax):
        """
        Sets the ENMAX value for element Q.
        :param elem_q_enmax: ENMAX value for element Q.
        """
        self._elem_q_enmax = elem_q_enmax

    def _get_elem_q_enmax(self):
        """
        Gets the ENMAX value for element Q.
        :return: ENMAX value for element Q.
        """
        return self._elem_q_enmax

    def set_list_potcar_extra_folder(self, list_elements, name_potcar):
        """
        Sets the POTCAR pattern list for specific elements.
        :param list_elements: List of elements.
        :param name_potcar: POTCAR pattern.
        """
        for element in list_elements:
            result = {
                'element': element,
                'potcar_pattern': name_potcar
            }
            self._list_potcar_pattern_for_elements.append(result)

    def get_set_list_potcar_extra_folder(self):
        """
        Gets the POTCAR pattern list for specific elements.
        :return: List of POTCAR patterns.
        """
        return self._list_potcar_pattern_for_elements

    def _search_elements_potpaw(self, element_search):
        """
        Searches the POTCAR pattern for a specific element.
        :param element_search: Element to search.
        :return: POTCAR pattern.
        """
        for element_pattern in self._list_potcar_pattern_for_elements:
            if element_pattern['element'] == element_search:
                return element_search + element_pattern['potcar_pattern']

        return element_search + self._pattern_potpaw

    def build_simulation_files(self):
        """Generates the simulation files."""
        self._create_poscar_file()
        self._create_kpoints_file()
        self._create_potcar_file()
        self._create_incar_file()

    def _create_potcar_file(self):
        """Creates the POTCAR file."""
        path_potcar_generate = os.path.join(self._path_folder, 'POTCAR')
        search_elem_m = POTCARScanner()
        search_elem_m.generate_potcar_mapping(self._search_elements_potpaw(self._elem_m))
        self._elem_m_enmax = search_elem_m.search_enmax()
        potcar_elem_m = search_elem_m.get_content_potcar_file()

        search_elem_q = POTCARScanner()
        search_elem_q.generate_potcar_mapping(self._search_elements_potpaw(self._elem_q))
        self._elem_q_enmax = search_elem_q.search_enmax()
        potcar_elem_q = search_elem_q.get_content_potcar_file()

        if self._elem_m_enmax > self._elem_q_enmax:
            self._incar_encut = self._elem_m_enmax * self._ratio_factor
        elif self._elem_q_enmax > self._elem_m_enmax:
            self._incar_encut = self._elem_q_enmax * self._ratio_factor
        else:
            self._incar_encut = self._elem_q_enmax * self._ratio_factor

        # CREATE POTCAR FILE FOR ELEMENTS FIRST ELEMENT M , SECOND ELEMENT Q
        content_potcar = potcar_elem_m + potcar_elem_q

        with open(path_potcar_generate, 'wb') as potcar_q_m:
            potcar_q_m.write(content_potcar)

    def _create_incar_file(self):
        """Creates the INCAR file."""
        _path_incar_generate = os.path.join(self._path_folder, 'INCAR')
        with open(self._file_incar_pattern, 'r') as incar_read:
            lines_incar_pattern = incar_read.readlines()

        with open(_path_incar_generate, 'w') as incar_generate:
            for line_number, lines in enumerate(lines_incar_pattern, start=1):
                if line_number == 1:
                    new_line = "#SYSTEM " + self._elem_m + " " + self._elem_q + " - (auto generated INCAR)\n"
                    incar_generate.writelines(new_line)
                elif line_number == 4:
                    new_line = "ENCUT = " + str(self._incar_encut) + "\n"
                    incar_generate.writelines(new_line)
                else:
                    corrected_line = lines.strip()
                    corrected_line = corrected_line + "\n"
                    corrected_line = re.sub(r'\s{2,}', ' ', corrected_line)
                    incar_generate.writelines(corrected_line)

    def _create_kpoints_file(self):
        """Creates the KPOINTS file."""
        path_poscar = os.path.join(self._path_folder, 'POSCAR')
        _path_kpoints_generate = os.path.join(self._path_folder, 'KPOINTS')

        if os.path.exists(path_poscar):
            with open(path_poscar, 'r') as poscar_read:
                poscar_read.readline().strip()
                ifactor = int(float(poscar_read.readline().strip()))
                str_vec1 = poscar_read.readline().strip()
                str_vec2 = poscar_read.readline().strip()
                str_vec3 = poscar_read.readline().strip()

            a_vec = str_vec1.split()
            b_vec = str_vec2.split()
            c_vec = str_vec3.split()

            lattice_vectors = [
                [float(a_vec[0]), float(a_vec[1]), float(a_vec[2])],
                [float(b_vec[0]), float(b_vec[1]), float(b_vec[2])],
                [float(c_vec[0]), float(c_vec[1]), float(c_vec[2])]
            ]

            ngrid = KPOINTSCalculator.rkmesh2d(C.RKFACTOR, lattice_vectors, ifactor)

            with open(_path_kpoints_generate, 'w') as kpoints_file:
                kpoints_file.writelines("Regular k-point mesh (auto generated KPOINTS)\n")
                kpoints_file.writelines("0\n")
                kpoints_file.writelines("Gamma\n")
                kpoints_file.writelines(f"{str(ngrid[0])} {str(ngrid[1])} {str(ngrid[2])}\n")
                kpoints_file.writelines("0 0 0\n")

    def _create_poscar_file(self):
        """Creates the POSCAR file."""
        _path_poscar_generate = os.path.join(self._path_folder, 'POSCAR')
        if os.path.isfile(self._file_poscar_pattern):
            with open(self._file_poscar_pattern, 'r') as POSCAR_READ:
                lines_poscar = POSCAR_READ.readlines()

            list_line_changes = [1, 6]
            pattern_numbers_retrieve = re.compile(r"(\d+)")

            with open(_path_poscar_generate, 'w') as POSCAR_GENERATE:
                for line_number, lines in enumerate(lines_poscar, start=1):
                    if line_number in list_line_changes:
                        if line_number == 1:
                            numbers = pattern_numbers_retrieve.findall(lines)
                            new_line = self._elem_m + str(numbers[0]) + self._elem_q + str(
                                numbers[1]) + " [SpaceGroup: " + self._structure + "] - (auto generated POSCAR)\n"
                            POSCAR_GENERATE.writelines(new_line)
                        if line_number == 6:
                            new_line = self._elem_m + " " + self._elem_q + "\n"
                            POSCAR_GENERATE.writelines(new_line)
                    else:
                        corrected_line = lines.strip()
                        corrected_line = corrected_line + "\n"
                        corrected_line = re.sub(r'\s{2,}', ' ', corrected_line)
                        POSCAR_GENERATE.writelines(corrected_line)
