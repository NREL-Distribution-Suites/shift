from infrasys.quantities import Distance
from geopandas import GeoDataFrame
import osmnx as ox
import shapely
from loguru import logger

from shift.data_model import ParcelModel, GeoLocation


def convert_buildings_to_parcel(geo_df: GeoDataFrame) -> list[ParcelModel]:
    """Function to convert geopandas dataframe to list of parcel models.

    Args:
        geo_df (GeoDataFrame): Geo dataframe.

    Returns:
        list[ParcelModel]
    """
    logger.info(f"Length of geodataframe: {len(geo_df)}, CRS: {geo_df.crs}")
    parcels: list[ParcelModel] = []
    for idx, geometry in enumerate(geo_df.to_dict(orient="records")):
        name = f"parcel_{idx}"
        geometry_obj = geometry["geometry"]

        match geometry_obj.geom_type:
            case "Point":
                parcels.append(
                    ParcelModel(
                        name=name,
                        geometry=GeoLocation(*list(geometry_obj.coords)[0]),
                    )
                )
            case "Polygon":
                parcels.append(
                    ParcelModel(
                        name=name,
                        geometry=[GeoLocation(*coord) for coord in geometry_obj.exterior.coords],
                    )
                )
    logger.info(f"Number of parcels: {len(parcels)}")
    return parcels


def get_parcels(
    location: str | GeoLocation | list[GeoLocation], max_distance: Distance = Distance(500, "m")
) -> list[ParcelModel] | None:
    """Function to return parcels for a given location.

    Note max_distance is not used if location type is Polygon.
    For a location of type str and GeoLocation, a polygon
    is created by forming a sqaure bounding box using max distance.
    We use osmnx package to fetch these buildings.

    Parameters
    ----------
        location : str | GeoLocation | Polygon
            Location for which openstreet parcels
            are to be fetched.
        max_distance : Distance
            Maximum distance to form a bounding box
            within which buildings are fetched.

    Returns
    -------
        list[ParcelModel]
            List of `ParcelModel`.

    Examples
    --------
    >>> from shift.parcel.openstreet import get_parcels
    >>> from infrasys.quantities import Distance
    >>> get_parcels("Fort Worth, Texas", Distance(100, "m"))
    """
    logger.info(f"Attempting to fecth parcels for {location}")
    tags = {"building": True}
    if isinstance(location, str):
        return convert_buildings_to_parcel(
            ox.features_from_address(location, tags, dist=max_distance.to("m").magnitude)
        )
    elif isinstance(location, GeoLocation):
        return convert_buildings_to_parcel(
            ox.features_from_point(
                list(reversed(location)), tags, dist=max_distance.to("m").magnitude
            )
        )
    elif isinstance(location, list):
        return convert_buildings_to_parcel(
            ox.features_from_polygon(shapely.Polygon(location), tags)
        )
