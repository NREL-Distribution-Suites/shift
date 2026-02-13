"""Parcel clustering tools."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from shift.mcp_server.serializers import serialize_group


def register(mcp: FastMCP) -> None:
    """Register clustering tools on the FastMCP instance."""

    @mcp.tool()
    def cluster_parcels(
        points: list[dict[str, float]],
        num_clusters: int = 5,
    ) -> str:
        """Cluster geographic points into groups using K-means.

        Useful for grouping building parcels to determine transformer
        placement locations. Each cluster has a center (potential transformer
        site) and member points (loads served by that transformer).

        Args:
            points: List of {longitude, latitude} dicts representing parcel
                    centroids or load locations.
            num_clusters: Number of clusters to create (default 5). Must be
                          <= number of points.

        Returns:
            JSON array of cluster objects with center coordinates and member
            points for each cluster.
        """
        try:
            from shift.utils.get_cluster import get_kmeans_clusters
            from shift.data_model import GeoLocation

            if len(points) < num_clusters:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"num_clusters ({num_clusters}) must be <= number of points ({len(points)}).",
                    }
                )

            geo_points = [GeoLocation(p["longitude"], p["latitude"]) for p in points]
            clusters = get_kmeans_clusters(num_clusters, geo_points)
            result = [serialize_group(c) for c in clusters]

            return json.dumps(
                {
                    "success": True,
                    "clusters": result,
                    "num_clusters": len(result),
                }
            )

        except Exception as exc:
            return json.dumps({"success": False, "error": str(exc)})
