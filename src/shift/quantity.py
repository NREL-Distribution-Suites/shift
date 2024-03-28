from infrasys.base_quantity import BaseQuantity, ureg


ureg.define("var = ampere * volt")
ureg.define("va = ampere * volt")


class PositiveArea(BaseQuantity):
    """Quantity representing area."""

    __compatible_unit__ = "m*m"

    def __init__(self, value, units, **kwargs):
        assert value >= 0, f"Area ({value}, {units}) must be positive."
