""" " Test for getting parcels."""

from unittest import mock

import pytest
from infrasys.quantities import Distance
import geopandas as gpd
from shapely import Point, Polygon

from shift import GeoLocation, ParcelModel, parcels_from_location

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


@pytest.fixture
def mock_ox():
    """Fixture for mocking osmnx package."""
    with mock.patch("shift.parcel.ox") as mock_ox:
        yield mock_ox


def get_sample_geo_dataframe():
    """Function to return sample geo dataframe."""
    return gpd.GeoDataFrame(
        geometry=[Point(1, 1), Polygon([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])]
    )


def test_get_parcels_with_address(mock_ox):
    """Test get parcel with address."""
    mock_ox.features_from_address.return_value = get_sample_geo_dataframe()
    result = parcels_from_location("Fort Worth, Texas", Distance(100, "m"))

    mock_ox.features_from_address.assert_called_once_with(
        "Fort Worth, Texas", {"building": True}, dist=100
    )

    assert len(result) == 2
    assert isinstance(result[0], ParcelModel)


def test_get_parcels_with_point(mock_ox):
    """Test function to test get parcels from point."""
    mock_ox.features_from_point.return_value = gpd.GeoDataFrame(
        geometry=[Point(1, 1), Polygon([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])]
    )

    result = parcels_from_location(
        GeoLocation(longitude=-97.3, latitude=32.75), Distance(300, "m")
    )
    mock_ox.features_from_point.assert_called_once_with(
        [32.75, -97.3], {"building": True}, dist=300
    )

    assert len(result) == 2
    assert isinstance(result[0], ParcelModel)


def test_get_parcels_with_polygon(mock_ox):
    """Test function to test get parcels from polygon."""
    mock_ox.features_from_polygon.return_value = gpd.GeoDataFrame(
        geometry=[Point(1, 1), Polygon([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])]
    )

    polygon = [
        GeoLocation(-122.29262, 37.83639),
        GeoLocation(-122.28095, 37.82972),
        GeoLocation(-122.29213, 37.82768),
        GeoLocation(-122.29262, 37.83639),
    ]
    result = parcels_from_location(polygon)
    mock_ox.features_from_polygon.assert_called_once_with(Polygon(polygon), {"building": True})

    assert len(result) == 2
    assert isinstance(result[0], ParcelModel)
