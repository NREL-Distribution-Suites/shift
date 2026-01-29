from sklearn.neighbors import KDTree
import numpy as np


def get_nearest_points(
    source_points: list[list[float]], target_points: list[list[float]]
) -> np.ndarray:
    """Find the nearest source point for each target point using KD-Tree.

    This function efficiently finds the closest point in source_points for each
    point in target_points using a K-D tree spatial index. This is useful for
    connecting loads to nearby network nodes or mapping parcels to road intersections.

    The algorithm has O(n log n) build time for the KD-tree and O(m log n) query time,
    where n is the number of source points and m is the number of target points.

    Parameters
    ----------
    source_points : list[list[float]]
        List of candidate points, where each point is [x, y] or [longitude, latitude].
        These are the points that will be searched to find nearest neighbors.
    target_points : list[list[float]]
        List of query points, where each point is [x, y] or [longitude, latitude].
        For each of these points, the nearest point in source_points is found.

    Returns
    -------
    np.ndarray
        Array of nearest points from source_points, one for each target_point.
        Shape is (len(target_points), 2).

    Notes
    -----
    - Uses Euclidean distance metric
    - For geographic coordinates, consider using haversine distance for large areas
    - Returns the actual coordinate values, not indices
    - If multiple source points are equidistant, returns the first one found

    Examples
    --------
    >>> from shift import get_nearest_points
    >>> source = [[1, 2], [2, 3], [3, 4]]
    >>> target = [[4, 5]]
    >>> result = get_nearest_points(source, target)
    >>> result
    array([[3, 4]])

    """

    tree = KDTree(source_points)
    _, idx = tree.query(target_points, k=1)
    first_indexes = [el[0] for el in idx]
    return np.array(source_points)[first_indexes]
