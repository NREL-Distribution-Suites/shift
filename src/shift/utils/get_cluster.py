from sklearn.cluster import KMeans
import numpy as np

from shift.data_model import GeoLocation, GroupModel


def get_kmeans_clusters(num_cluster: int, points: list[GeoLocation]) -> list[GroupModel]:
    """Cluster geographic points using K-means algorithm.

    This function groups a set of geographic locations into clusters using the
    K-means clustering algorithm. Each cluster contains a center point and all
    points assigned to that cluster.

    The algorithm minimizes the sum of squared distances between points and their
    assigned cluster centers. This is useful for grouping nearby loads or parcels
    in distribution system modeling.

    Parameters
    ----------
    num_cluster : int
        Number of clusters to create. Must be less than or equal to the number
        of input points.
    points : list[GeoLocation]
        List of geographic locations to cluster. Each point should be a GeoLocation
        namedtuple with longitude and latitude.

    Returns
    -------
    list[GroupModel]
        List of cluster models, where each model contains:
        - center: GeoLocation of the cluster centroid
        - points: List of GeoLocation objects assigned to this cluster

    Notes
    -----
    - Uses scikit-learn's KMeans implementation with random_state=0 for reproducibility
    - Points are treated as Euclidean coordinates; consider projection for large areas
    - Empty clusters are possible if num_cluster is too large relative to point distribution

    Examples
    --------
    >>> from shift import get_kmeans_clusters, GeoLocation
    >>> points = [
    ...     GeoLocation(-97.33, 32.75),
    ...     GeoLocation(-97.32, 32.76),
    ...     GeoLocation(-97.35, 32.77),
    ... ]
    >>> clusters = get_kmeans_clusters(2, points)
    >>> len(clusters)
    2

    """

    clusters = KMeans(n_clusters=num_cluster, random_state=0).fit(points)

    return [
        GroupModel(
            center=GeoLocation(*center),
            points=[GeoLocation(*el) for el in np.array(points)[clusters.labels_ == idx]],
        )
        for idx, center in enumerate(clusters.cluster_centers_)
    ]
