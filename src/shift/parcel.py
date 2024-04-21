from infrasys.quantities import Distance
from geopandas import GeoDataFrame
import osmnx as ox
import shapely
from loguru import logger

from shift.data_model import ParcelModel, GeoLocation

from pathlib import Path

import pandas as pd
from shapely import wkt


def parcels_from_geodataframe(geo_df: GeoDataFrame) -> list[ParcelModel]:
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
            case "MultiPolygon":
                parcels.append(
                    ParcelModel(
                        name=name,
                        geometry=[
                            GeoLocation(*coord)
                            for coord in geometry_obj.convex_hull.exterior.coords
                        ],
                    )
                )
            case _:
                logger.warning(f"{geometry_obj.geom_type} is not supported.")
    logger.info(f"Number of parcels: {len(parcels)}")
    return parcels


def parcels_from_csv(file_path: Path):
    """Function to load parcels from csv.

    Note, this function uses geopandas to construct geo dataframe
    which requires that you have at least a column named `geometry` in your file.

    Parameters
    ----------
    file_path: Path to csv file with geometries.
    """

    df = pd.read_csv(file_path)
    if "geometry" not in df.columns:
        msg = f"geometry column missing csv file {file_path=}"
        raise ValueError(msg)
    df["geometry"] = df["geometry"].apply(wkt.loads)
    return parcels_from_geodataframe(GeoDataFrame(df))


def parcels_from_location(
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
        return parcels_from_geodataframe(
            ox.features_from_address(location, tags, dist=max_distance.to("m").magnitude)
        )
    elif isinstance(location, GeoLocation):
        return parcels_from_geodataframe(
            ox.features_from_point(
                list(reversed(location)), tags, dist=max_distance.to("m").magnitude
            )
        )
    elif isinstance(location, list):
        return parcels_from_geodataframe(ox.features_from_polygon(shapely.Polygon(location), tags))
