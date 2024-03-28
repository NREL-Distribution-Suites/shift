from typing import Annotated, NamedTuple

from pydantic import BaseModel, Field
from shapely import Polygon
from infrastructure_systems.src.infrasys.quantities import Distance

from shift.quantity import PositiveArea


class GeoLocation(NamedTuple):
    latitude: float
    longitude: float


class OpenStreetParcelModel(BaseModel):
    """Interface for parcel model."""

    name: Annotated[str, Field(..., description="Name of the parcel.")]
    longitude: Annotated[
        float,
        Field(..., ge=-180, le=180, description="Longitude coordinate of the parcel."),
    ]
    latitude: Annotated[
        float, Field(..., ge=-90, le=90, description="Latitude coordinate of the parcel.")
    ]
    area: Annotated[PositiveArea, Field(..., description="Area of the parcel.")]


def get_openstreet_parcels(
    location: str | GeoLocation | Polygon, max_distance: Distance
) -> list[OpenStreetParcelModel]:
    """Function to return parcels for a given location.

    Note max_distance is not used if location type is Polygon.
    For a location of type str and GeoLocation, a polygon
    is created by forming a sqaure bounding box using max distance.
    We use osmnx package to fetch these buildings.

    Args
        location (str | GeoLocation | Polygon): Location for which
            openstreet parcels are to be fetched.
        max_distance (Distance): Maximum distance to form a bounding box
            within which buildings are fetched.

    Return:
        list[OpenStreetParcelModel]: List of `OpenStreetParcelModel`.

    Examples:
        >>> from shift.parcels.openstreet_parcel_model import get_openstreet_parcels
        >>> from infrasys.quantities import Distance
        >>> get_openstreet_parcels("Fort Worth, Texas", Distance(100, "m*m"))
    """
