import plotly.graph_objects as go
from shift.data_model import GeoLocation


COLORS = [
    "#1f77b4",  # muted blue
    "#ff7f0e",  # safety orange
    "#2ca02c",  # cooked asparagus green
    "#d62728",  # brick red
    "#9467bd",  # muted purple
    "#8c564b",  # chestnut brown
    "#e377c2",  # raspberry yogurt pink
    "#7f7f7f",  # middle gray
    "#bcbd22",  # curry yellow-green
    "#17becf",  # blue-teal
]


class PlotManager:
    """Class for managing plotly plots.

    Parameters
    ----------

    center: GeoLocation
        Centre of the map. Optional defaults to GeoLocation(0,0)


    Examples
    --------

    Creating an instance of the plot manager.

    >>> plt_instance = PlotManager()

    Adding plot the plot manager.

    >>> plt_instance.add_plot([GeoLocation(0,0),
        GeoLocation(0.0001, 0.0001)], name="plot1")

    Displaying the plot in the browser.

    >>> plt.instance.show()
    """

    def __init__(self, center: GeoLocation | None = None):
        """Constructor for managing plots with plotly."""
        self._figure = go.Figure()
        self.center = GeoLocation(0, 0) if center is None else center
        self._color_index = 0

    def _get_color(self):
        """Internal method to retrive color for plot dynamically."""
        if self._color_index >= len(COLORS):
            self._color_index = 0
        self._color_index += 1
        return COLORS[self._color_index - 1]

    def add_plot(
        self,
        geometries: list[GeoLocation] | list[list[GeoLocation]],
        name: str,
        mode: str = "markers",
    ):
        """Method to add geometries.

        Parameters
        ----------

        geometries: list[GeoLocation]
            Points to be added to the plot.
        name: str
            Name of the plot
        scatter_mode: bool, optional
            Set to False if you want to plot lines. Defaults to True.

        Examples
        --------

        >>> plt_instance.add_plot([GeoLocation(0,0),
            GeoLocation(0.0001, 0.0001)], name="plot1")
        """

        if isinstance(geometries[0], GeoLocation):
            longitudes = [item.longitude for item in geometries]
            latitudes = [item.latitude for item in geometries]
        else:
            longitudes, latitudes = [], []
            for geometry in geometries:
                latitudes.extend([loc.latitude for loc in geometry] + [None])
                longitudes.extend([loc.longitude for loc in geometry] + [None])

        self._figure.add_trace(
            go.Scattermapbox(
                lon=longitudes,
                lat=latitudes,
                name=name,
                mode=mode,
                marker=dict(size=10, color=self._get_color()),
                line=dict(color=self._get_color(), width=2) if "lines" not in mode else None,
            )
        )

    def show(self):
        """Method to show the plot."""
        self._update_plot_layout(self._figure, self.center.latitude, self.center.longitude)
        self._figure.show()

    @staticmethod
    def _update_plot_layout(
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
        figure.update_layout(margin=margin, legend=dict(x=0, y=1))
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
