from typing import Annotated, NamedTuple

from pydantic import BaseModel, Field


class GeoLocation(NamedTuple):
    """Inyerface for geo location."""

    longitude: Annotated[
        float,
        Field(..., ge=-180, le=180, description="Longitude coordinate of the parcel."),
    ]
    latitude: Annotated[
        float, Field(..., ge=-90, le=90, description="Latitude coordinate of the parcel.")
    ]


class ParcelModel(BaseModel):
    """Interface for parcel model."""

    name: Annotated[str, Field(..., description="Name of the parcel.")]
    geometry: Annotated[
        list[GeoLocation] | GeoLocation, Field(..., description="Geo location for the parcel.")
    ]