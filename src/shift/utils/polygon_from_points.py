from infrasys.quantities import Distance
from shapely import Polygon, MultiPoint, Point

from shift.data_model import GeoLocation


def get_polygon_from_points(points: list[GeoLocation], buffer: Distance) -> Polygon:
    """Method to return bounding box polygon for a given set of points.

    Parameters
    ----------

    points: list[GeoLocation]
        List of geo location points
    buffer: Distance
        Buffer distance to include for getting road network.

    Returns
    -------

    Polygon
        Bounding box polygon

    Examples
    --------

    >>> get_polygon_from_points([[-97.32, 43.22], [-98.33, 45.35]], buffer=Distance(20, "m"))
    <POLYGON ((-98.33 43.22, -97.32 43.22, -97.32 45.35, -98.33 45.35, -98.33 43...>
    """

    multipoints = MultiPoint([Point(*point) for point in points])
    minx, miny, maxx, maxy = multipoints.buffer((buffer.to("m") / 111139).magnitude).bounds
    return Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)])
