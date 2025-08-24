# vasp_init/kpoints_write.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
KPOINTS - Handles creation and writing of VASP KPOINTS files.

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""
from pathlib import Path

import numpy as np
from Monochalcogenides2D.common.config import RK_FACTOR

from poscar_writer import read_poscar_vectors
from Monochalcogenides2D.common.utils import init_logger, task_generate_log


@task_generate_log
def run_kpoints_writer(path_output: Path):
    """Generates and writes a VASP KPOINTS file for 2D system calculations.

    Reads lattice vectors from a POSCAR file, computes an appropriate k-point mesh
    for 2D systems, and writes the results in VASP KPOINTS format. The mesh is
    Gamma-centered and automatically sized based on reciprocal lattice dimensions.

    Args:
        path_output (Path): Output directory for KPOINTS file

    Returns:
        None: Writes file to disk and logs location

    Note:
        Depends on:
        - read_poscar_vectors() for lattice extraction
        - rkmesh2d() for k-point grid calculation
        - Global RK_FACTOR for mesh density control
        - logger for status reporting
    """

    path_poscar = path_output.joinpath('POSCAR')

    # Extract lattice parameters from POSCAR: flat cell flag, scaling factor, and vectors
    _, scale, a1, a2, a3 = read_poscar_vectors(path_poscar)

    # Construct 3x3 real-space lattice matrix for reciprocal space calculations
    rlattice = np.array([a1.tolist(), a2.tolist(), a3.tolist()])

    # Compute optimal k-point grid dimensions for 2D system
    # RK_FACTOR controls density, scale adjusts lattice dimensions
    ngrid = rkmesh2d(RK_FACTOR, rlattice, scale)

    # Build KPOINTS file content following VASP format specifications:
    # Line 1: Comment
    # Line 2: 0 = automatic generation mode
    # Line 3: Gamma-centered grid
    # Line 4: Mesh dimensions (2D with z=1)
    # Line 5: Grid offset (none)
    kpoints_content = [
        "Regular k-point mesh (auto generated KPOINTS)",
        "0",  # Automatic generation scheme
        "Gamma",  # Gamma-centered grid type
        f"{str(ngrid[0])} {str(ngrid[1])} {str(ngrid[2])}",  # Grid dimensions
        "0  0  0",  # Zero offset for grid
    ]

    # Resolve output path and write file
    path_kpoints_file = Path(path_output).joinpath("KPOINTS")
    path_kpoints_file.write_text('\n'.join(kpoints_content), encoding='utf-8')

    # Confirm file creation in logs
    logger.info(f"KPOINTS file written to {path_kpoints_file.resolve()}")


def rkmesh2d(rk, rlat, ifactor):
    """Computes a 2D k-point mesh grid for Brillouin zone sampling.

    Given real-space lattice vectors, this function calculates an appropriate
    k-point sampling grid for 2D systems. The grid density is determined by the
    rk parameter and reciprocal vector magnitudes. The third dimension is always
    set to 1 for 2D systems.

    Args:
        rk (float): k-point density parameter (larger = denser mesh).
        rlat (list[array]): Three real-space lattice vectors [v1, v2, v3].
        ifactor (int): Scaling factor for lattice vectors.

    Returns:
        np.ndarray: Integer array [n1, n2, 1] specifying k-point grid dimensions.

    Note:
        Assumes recvec and vecsize functions are defined. The third lattice vector
        should be perpendicular to the 2D plane (typically [0,0,c]).
    """
    # Initialize output arrays for grid dimensions, reciprocal vectors, and magnitudes
    ngrid = np.zeros(3, dtype=np.int64)
    blat = np.zeros((3, 3), dtype=np.float64)
    vsize = np.zeros(3, dtype=np.float64)
    pi = np.arccos(-1.0)

    # Scale real-space lattice vectors by input factor
    # This adjusts unit cell dimensions before reciprocal space calculation
    for vec in rlat:
        vec *= ifactor

    # Compute reciprocal lattice vectors from scaled real-space vectors
    blat = recvec(rlat[0], rlat[1], rlat[2])

    # Calculate magnitudes of reciprocal lattice vectors
    # These relate to real-space lattice periods
    for i in range(3):
        vsize[i] = vecsize(blat[i])

    # Convert reciprocal magnitudes to real-space periods
    # Reciprocal vector magnitude = 2π / real-space period
    vsize = vsize / (2.0 * pi)

    # Determine grid points: round(rk * period) with minimum 1
    # Ensures at least 1 k-point in each 2D direction
    ngrid[0] = int(max(1.0, (rk * vsize[0]) + 0.5))
    ngrid[1] = int(max(1.0, (rk * vsize[1]) + 0.5))
    ngrid[2] = 1  # Fixed 1-point grid for non-periodic (z) direction

    return ngrid


# Calculates the vector resulting from the cross product of two vectors v1 × v2
def prodvec(v1, v2):
    """Computes the cross product of two 3D vectors.

    Standard vector cross product implementation for 3-dimensional vectors.
    Follows right-hand rule convention: i(v1×v2) = v1.y*v2.z - v1.z*v2.y.

    Args:
        v1 (array-like): First 3D vector [x1, y1, z1]
        v2 (array-like): Second 3D vector [x2, y2, z2]

    Returns:
        np.ndarray: Resulting cross product vector [vx, vy, vz]
    """
    # Initialize output vector
    vx = np.zeros(3, dtype=np.float64)

    # Cross product components (right-hand rule)
    vx[0] = (v1[1] * v2[2]) - (v1[2] * v2[1])  # x-component: y1z2 - z1y2
    vx[1] = (v1[2] * v2[0]) - (v1[0] * v2[2])  # y-component: z1x2 - x1z2
    vx[2] = (v1[0] * v2[1]) - (v1[1] * v2[0])  # z-component: x1y2 - y1x2

    return vx


def recvec(rlat1, rlat2, rlat3):
    """Computes reciprocal lattice vectors from three real-space lattice vectors.

    Given three real-space lattice vectors (rlat1, rlat2, rlat3) forming a unit cell,
    this function calculates the corresponding reciprocal lattice vectors using
    standard solid-state physics conventions. The reciprocal vectors are computed
    using cross products and volume normalization with a 2π factor.

    Args:
        rlat1 (array-like): First real-space lattice vector (3D).
        rlat2 (array-like): Second real-space lattice vector (3D).
        rlat3 (array-like): Third real-space lattice vector (3D).

    Returns:
        tuple: Three reciprocal lattice vectors (blat1, blat2, blat3) as NumPy arrays.

    Note:
        Assumes `prodvec` computes the vector cross product. Volume calculation relies
        on the scalar triple product rlat1 · (rlat2 × rlat3).
    """
    pi = np.pi

    # Initialize empty vectors for cross product results
    v23 = np.empty(3, dtype=np.float64)
    v31 = np.empty(3, dtype=np.float64)
    v12 = np.empty(3, dtype=np.float64)

    # Initialize output vectors for reciprocal lattice
    blat1 = np.empty(3, dtype=np.float64)
    blat2 = np.empty(3, dtype=np.float64)
    blat3 = np.empty(3, dtype=np.float64)

    # Compute cross products between lattice vectors
    v23 = prodvec(rlat2, rlat3)  # rlat2 × rlat3
    v31 = prodvec(rlat3, rlat1)  # rlat3 × rlat1
    v12 = prodvec(rlat1, rlat2)  # rlat1 × rlat2

    # Calculate unit cell volume using scalar triple product
    vol = abs((rlat1[0] * v23[0]) + (rlat1[1] * v23[1]) + (rlat1[2] * v23[2]))

    # Compute reciprocal lattice vectors with 2π normalization
    blat1 = ((2.0 * pi) / vol) * v23  # Reciprocal vector corresponding to rlat1
    blat2 = ((2.0 * pi) / vol) * v31  # Reciprocal vector corresponding to rlat2
    blat3 = ((2.0 * pi) / vol) * v12  # Reciprocal vector corresponding to rlat3

    return blat1, blat2, blat3


def vecsize(vec):
    """Computes the Euclidean norm (magnitude) of a 3D vector.

    Args:
        vec (array-like): Input vector with 3 components (x, y, z).

    Returns:
        float: Magnitude of the input vector.
    """
    # Calculate vector magnitude using Euclidean norm formula
    vsize = np.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)
    return vsize


if __name__ == "__main__":
    logger = init_logger(task_name="KPOINTS_INIT_WRITE", level="INFO")
else:
    from loguru import logger
