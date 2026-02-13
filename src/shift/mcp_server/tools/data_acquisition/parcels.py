"""Parcel fetching tools."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from shift.mcp_server.serializers import serialize_parcel


def _parse_location(location: str):
    """Parse a location string into a GeoLocation or return the string."""
    from shift.data_model import GeoLocation

    if "," in location:
        parts = location.split(",")
        if len(parts) == 2:
            try:
                lon, lat = float(parts[0].strip()), float(parts[1].strip())
                return GeoLocation(lon, lat)
            except ValueError:
                pass
    return location


def register(mcp: FastMCP) -> None:
    """Register parcel tools on the FastMCP instance."""

    @mcp.tool()
    def fetch_parcels(
        location: str,
        distance_meters: float = 500.0,
    ) -> str:
        """Fetch building parcels from OpenStreetMap for a given location.

        Retrieves building footprints and metadata (building type, address)
        within the specified radius of a location.

        Args:
            location: Address string (e.g. "Fort Worth, TX") or coordinates
                      as "longitude,latitude" (e.g. "-97.33,32.75").
            distance_meters: Search radius in meters (default 500, max 5000).

        Returns:
            JSON array of parcel objects with name, building_type, city,
            state, postal_address, and geometry.
        """
        try:
            from shift.parcel import parcels_from_location
            from gdm.quantities import Distance

            distance_meters = min(distance_meters, 5000.0)
            loc = _parse_location(location)
            parcels = parcels_from_location(loc, Distance(distance_meters, "m"))

            if parcels is None:
                return json.dumps({"success": True, "parcels": [], "count": 0})

            result = [serialize_parcel(p) for p in parcels]
            return json.dumps({"success": True, "parcels": result, "count": len(result)})

        except Exception as exc:
            return json.dumps({"success": False, "error": str(exc)})

    @mcp.tool()
    def fetch_parcels_in_polygon(
        coordinates: list[dict[str, float]],
    ) -> str:
        """Fetch building parcels within a polygon boundary.

        Args:
            coordinates: List of {longitude, latitude} dicts defining the
                         polygon vertices. At least 3 points required.

        Returns:
            JSON array of parcel objects found within the polygon.
        """
        try:
            from shift.parcel import parcels_from_location
            from shift.data_model import GeoLocation

            if len(coordinates) < 3:
                return json.dumps(
                    {"success": False, "error": "At least 3 coordinate points required."}
                )

            geo_points = [GeoLocation(c["longitude"], c["latitude"]) for c in coordinates]
            parcels = parcels_from_location(geo_points)

            if parcels is None:
                return json.dumps({"success": True, "parcels": [], "count": 0})

            result = [serialize_parcel(p) for p in parcels]
            return json.dumps({"success": True, "parcels": result, "count": len(result)})

        except Exception as exc:
            return json.dumps({"success": False, "error": str(exc)})
