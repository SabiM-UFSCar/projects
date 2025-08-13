import numpy as np


def vector_cross(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Calculate the cross product of two vectors.

    :param a: First vector.
    :param b: Second vector.

    :return: Cross product of vectors a and b.

    Note:
    When defining functions that use NumPy's cross() function internally, it may trigger a warning message stating
    "This code is unreachable" for the subsequent code. This behavior occurs because certain static analysis tools
    cannot accurately determine the reachability of code following the cross() function call.
    Defining the cross() function within another function is an attempt to resolve this behavior.
    """
    return np.cross(a, b)


def rkmesh(rk, lattice_vectors, correction_factor):
    """
    Calculate reciprocal space grid points.

    :param rk: Reciprocal space factor.
    :param lattice_vectors: Reciprocal lattice vectors.
    :param correction_factor: Factor correction.

    :return: 3D reciprocal space grid points.
    """
    ngrid = np.zeros(3, dtype=np.int64)
    pi = np.pi

    # Factor correction:
    lattice_vectors *= correction_factor

    blat = calc_reciprocal_lattice_vectors(lattice_vectors)

    vsize = np.array([vector_size(blat[i]) for i in range(3)])
    vsize /= (2.0 * pi)

    ngrid[0] = int(max(1.0, (rk * vsize[0]) + 0.5))
    ngrid[1] = int(max(1.0, (rk * vsize[1]) + 0.5))
    ngrid[2] = int(max(1.0, (rk * vsize[2]) + 0.5))

    return ngrid


def rkmesh2d(rk, lattice_vectors, correction_factor):
    """
    Calculate 2D reciprocal space grid points.

    :param rk: Reciprocal space factor.
    :param lattice_vectors: Reciprocal lattice vectors.
    :param correction_factor: Factor correction.

    :return: 2D reciprocal space grid points as a numpy.ndarray.
    """

    ngrid = np.zeros(3, dtype=np.int64)
    pi = np.pi

    # Factor correction:
    lattice_vectors *= correction_factor

    blat = calc_reciprocal_lattice_vectors(lattice_vectors)

    vsize = np.array([vector_size(blat[i]) for i in range(3)])
    vsize /= (2.0 * pi)

    ngrid[0] = int(max(1.0, (rk * vsize[0]) + 0.5))
    ngrid[1] = int(max(1.0, (rk * vsize[1]) + 0.5))
    ngrid[2] = 1

    return ngrid


def calc_reciprocal_lattice_vectors(lattice_vectors):
    """
    Calculate the reciprocal lattice vectors.

    :param lattice_vectors: Reciprocal lattice vectors.

    :return: Tuple containing the reciprocal lattice vectors.
    """
    lat23 = vector_cross(lattice_vectors[1], lattice_vectors[2])
    lat31 = vector_cross(lattice_vectors[0], lattice_vectors[2])
    lat12 = vector_cross(lattice_vectors[0], lattice_vectors[1])

    vol = abs(
        (lattice_vectors[0][0] * lat23[0]) + (lattice_vectors[0][1] * lat23[1]) + (lattice_vectors[0][2] * lat23[2]))

    rec_lat_1 = ((2.0 * np.pi) / vol) * lat23
    rec_lat_2 = ((2.0 * np.pi) / vol) * lat31
    rec_lat_3 = ((2.0 * np.pi) / vol) * lat12

    return rec_lat_1, rec_lat_2, rec_lat_3


def vector_size(vec):
    """
    Calculate the size of a vector.

    :param vec: Input vector.

    :return: Size of the input vector.
    """
    vsize = np.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)
    return vsize
