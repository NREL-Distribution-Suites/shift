import plotly.graph_objects as go


def update_plot_layout(
    figure: go.Figure,
    centre_latitude: float,
    centre_longitude: float,
    style: str = "carto-positron",
    zoom: int = 15,
    access_token: str | None = None,
    margin: dict | None = None,
):
    """Function to update plot layout.

    Parameters
    ----------

    figure: go.Figure
        Instance of plotly graph objects figure.
    centre_latitude: float
        Longitude location of map center.
    centre_longitude: float
        Longitude location of map center.
    style: str
        Valid mapbox style https://plotly.com/python/mapbox-layers/,
        defaults to `carto-positron`.
    zoom: int
        Zoom level for map, defaults to 15.
    access_token: str | None, optional
        Mapbox access token.
    margin: dict | None, optional
        Map margin


    Examples
    --------

    >>> fig = go.Figure()
    >>> update_plot_layout(fig, 0, 0)

    """
    if margin is None:
        margin = {"r": 0, "t": 0, "l": 0, "b": 0}
    figure.update_layout(margin=margin)
    figure.update_mapboxes(
        {
            "accesstoken": access_token,
            "style": style,
            "center": {
                "lon": centre_longitude,
                "lat": centre_latitude,
            },
            "zoom": zoom,
        }
    )
