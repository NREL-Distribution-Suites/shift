from sklearn.neighbors import KDTree
import numpy as np


def get_nearest_points(source_points: list[list[float]], target_points: list[list[float]]):
    """Function to find nearest point in graph nodes for all points.

    Parameters
    ----------

    source_points: list[list[float]]
        List of list of floats representing points among which
        to compute nearest points.
    target_points: list[list[float]]
        List of list of floats representing points for which
        closest point is to be computed in `source_points`.

    Examples
    --------

    >>> from shift import get_nearest_points
    >>> get_nearest_points([[1, 2], [2, 3]], [[4, 5]])
    array([[2,3]])

    """

    tree = KDTree(source_points)
    _, idx = tree.query(target_points, k=1)
    first_indexes = [el[0] for el in idx]
    return np.array(source_points)[first_indexes]
