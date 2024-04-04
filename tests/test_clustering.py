from shift.cluster import get_kmeans_clusters, ClusterModel
from shift.data_model import GeoLocation


def test_point_clustering():
    """Test point clustering function."""
    points = [
        GeoLocation(*el)
        for el in [
            (-73.935242, 40.730610),
            (-73.934657, 40.731008),
            (-73.934952, 40.730456),
            (-73.935751, 40.730240),
            (-73.935302, 40.729913),
            (-73.935860, 40.730362),
            (-73.935479, 40.730812),
            (-73.935071, 40.730628),
            (-73.935530, 40.730160),
            (-73.935171, 40.730527),
        ]
    ]
    clusters = get_kmeans_clusters(2, points)
    assert len(clusters) == 2
    assert isinstance(clusters[0], ClusterModel)
