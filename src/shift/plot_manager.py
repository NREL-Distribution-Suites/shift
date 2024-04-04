import plotly.graph_objects as go
from shift.update_plot_layout import update_plot_layout
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
    """Class for managing plotly plots."""

    def __init__(self, centre: GeoLocation | None = None):
        """Constructor for managing plots with plotly."""
        self.figure = go.Figure()
        self.centre = centre
        self.color_index = 0

    def _get_color(self):
        """Internal method to retrive color for plot dynamically."""
        if self.color_index >= len(COLORS):
            self.color_index = 0
        self.color_index += 1
        return COLORS[self.color_index - 1]

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
        """

        if isinstance(geometries[0], GeoLocation):
            longitudes = [item.longitude for item in geometries]
            latitudes = [item.latitude for item in geometries]
        else:
            longitudes, latitudes = [], []
            for geometry in geometries:
                latitudes.extend([loc.latitude for loc in geometry] + [None])
                longitudes.extend([loc.longitude for loc in geometry] + [None])

        self.figure.add_trace(
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
        """Method to show the graph."""
        update_plot_layout(self.figure, self.centre.latitude, self.centre.longitude)
        self.figure.show()
