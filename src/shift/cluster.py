from typing import Annotated

from pydantic import BaseModel, Field
from sklearn.cluster import KMeans
import numpy as np

from shift.parcel.model import GeoLocation


class ClusterModel(BaseModel):
    """Interface for cluster model."""

    center: Annotated[GeoLocation, Field(..., description="Centre of the cluster.")]
    points: Annotated[
        list[GeoLocation], Field(..., description="List of points that belong to this cluster.")
    ]


def get_kmeans_clusters(num_cluster: int, points: list[GeoLocation]) -> list[ClusterModel]:
    """Function to return kmeans clusters for given set of points.

    Parameters
    ----------
    num_cluster : int
        Number of cluster to group given set of points.
    points : list[GeoLocation]
        List of points for clustering.

    Returns
    -------
    list[ClusterModel]
        Generated cluster.

    Examples
    --------
    >>> from shift.cluster import get_kmeans_clusters
    >>> points = [GeoLocation(2, 3), GeoLocation(3, 4), GeoLocation(4, 5)]
    >>> clusters = get_kmeans_clusters(2, points)

    """

    clusters = KMeans(n_clusters=num_cluster, random_state=0).fit(points)

    return [
        ClusterModel(
            center=GeoLocation(*center),
            points=[GeoLocation(*el) for el in np.array(points)[clusters.labels_ == idx]],
        )
        for idx, center in enumerate(clusters.cluster_centers_)
    ]
