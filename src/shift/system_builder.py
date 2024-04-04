from abc import ABC

from gdm import DistributionSystem


class DistributionSystemBuilder(ABC):
    """Abstract class interface for building distribution system.

    Subclasses must implement these methods.
    * `build_system_graph`: Custom implementation for returning
        an instance `SystemGraph` class.
    * `build_phase_mapper`: Custom implementation for returning
        an instance of `PhaseMapper` class.
    * `build_voltage_mapper`: Custom implementation for returning
        an instance of  `VoltageMapper` class.
    * `build_equipment_mapper`: Custom implementation for
        returning an instance of `EquipmentMapper` class.

    """

    def __init__(self, name: str, base_freq: int):
        """Constructor for distribution system builder.

        Parameters
        ----------
        base_freq : int
            Base frequency for the system.
        name : str
            Name of the distribution system.
        """
        self.base_frequency = base_freq
        self.sys = DistributionSystem(name=name)

    # @abstractmethod
    # def build_system_graph(self) ->  ''

    # @abstractmethod
    # def build_phase_mapper(self) -> ''

    # @abstractmethod
    # def build_voltage_mapper(self) -> ''

    # @abstractmethod
    # def build_equipment_mapper(self) -> ''

    def build_system(
        self,
    ) -> DistributionSystem:
        """Builds distribution system from

        Returns
        -------
        DistributionSystem
            _description_
        """
