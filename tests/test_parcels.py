"""" Test for getting parcels."""

import pytest
from infrasys.quantities import Distance

from shift.parcel.openstreet import get_parcels
from shift.parcel.model import GeoLocation, ParcelModel

GET_PARCEL_INPUTS = [
    ["Fort Worth, TX", Distance(300, "m")],
    [GeoLocation(longitude=-97.3, latitude=32.75), Distance(300, "m")],
    [
        [
            GeoLocation(-122.29262, 37.83639),
            GeoLocation(-122.28095, 37.82972),
            GeoLocation(-122.29213, 37.82768),
            GeoLocation(-122.29262, 37.83639),
        ]
    ],
]


@pytest.mark.parametrize("location", GET_PARCEL_INPUTS)
def test_get_parcels(location):
    """Test function for getting parcels."""
    parcels = get_parcels(*location)
    assert parcels
    assert isinstance(parcels[0], ParcelModel)
