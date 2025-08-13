import math

import ase.io
import numpy as np
from ase import Atoms


class StructureHandler:
    def __init__(self, atoms: ase.atoms.Atoms):
        if not isinstance(atoms, ase.atoms.Atoms):
            raise TypeError("Invalid input: Expected an Atoms object.")
        self.atoms = Atoms(atoms)

    def rotate_atoms_index_stable(self, angle: int, vector: tuple,
                                  center: tuple, index_atoms_rotate, rotate_cell: bool):
        """
        Rotate atoms in the structure while preserving the indices of selected atoms.

        :param angle: The angle of rotation in degrees.
        :param vector: A tuple representing the rotation vector.
        :param center: A tuple representing the center of rotation.
        :param index_atoms_rotate: A list of indices of atoms to be rotated.
        :param rotate_cell: A boolean indicating whether to rotate the cell along with the atoms.

        :return: Atoms - The modified structure with rotated atoms.

        Raises:
        - TypeError: If the provided atoms are not in the correct format or type.

        This function rotates atoms in the atomic structure while keeping the indices of selected atoms unchanged.
        It copies the atoms that are not meant to be rotated, rotates the selected atoms, and updates the positions
        of the selected atoms in the original structure.

        Note:
        The rotation is applied only to the selected atoms while the rest of the structure remains stationary.
        """

        # Create a list of indices for atoms not to be rotated
        list_not_rotate = []
        for atoms in self.atoms:
            if atoms.index not in index_atoms_rotate:
                list_not_rotate.append(atoms.index)

        # Create a copy of the atoms to be rotated and delete atoms that are not meant to be rotated
        atoms_rotate = Atoms(self.atoms.copy())
        del atoms_rotate[[atom.index for atom in atoms_rotate if atom.index in list_not_rotate]]
        #
        # # Rotate the selected atoms
        atoms_rotate.rotate(angle, vector, center, rotate_cell)
        #
        # # Update positions of selected atoms in the original structure
        i = 0
        for atom in self.atoms:
            if atom.index in index_atoms_rotate:
                atom.position = atoms_rotate[i].position
                i = i + 1
        return self.atoms

    def rotate_atoms_index(self, angle, axis_vector, center, atom_rotate_list):
        angle_rad = math.radians(angle)
        axis_vector = np.array(axis_vector)
        axis_vector = axis_vector / np.linalg.norm(axis_vector)

        center_p = np.array(center)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        ux, uy, uz = axis_vector

        rotation_matrix = np.array(
            [
                [cos_angle + ux ** 2 * (1 - cos_angle), ux * uy * (1 - cos_angle) - uz * sin_angle,
                 ux * uz * (1 - cos_angle) + uy * sin_angle],
                [uy * ux * (1 - cos_angle) + uz * sin_angle, cos_angle + uy ** 2 * (1 - cos_angle),
                 uy * uz * (1 - cos_angle) - ux * sin_angle],
                [uz * ux * (1 - cos_angle) - uy * sin_angle, uz * uy * (1 - cos_angle) + ux * sin_angle,
                 cos_angle + uz ** 2 * (1 - cos_angle)]
            ]
        )

        # Create a list of indices for atoms not to be rotated
        list_not_rotate = []
        for atoms in self.atoms:
            if atoms.index not in atom_rotate_list:
                list_not_rotate.append(atoms.index)

        # Create a copy of the atoms to be rotated and delete atoms that are not meant to be rotated
        atoms_rotate = Atoms(self.atoms.copy())
        del atoms_rotate[[atom.index for atom in atoms_rotate if atom.index in list_not_rotate]]

        rotated_atoms = []
        for atom in atoms_rotate:
            point = np.array(atom.position)
            relative_point = point - center_p
            rotated_relative_point = np.dot(rotation_matrix, relative_point)
            rotated_point = rotated_relative_point + center_p
            rotated_atoms.append(rotated_point.tolist())

        i = 0
        for atom in self.atoms:
            if atom.index in atom_rotate_list:
                atom.position = rotated_atoms[i]
                i = i + 1

        return self.atoms
