from gdm import (
    DistributionTransformer,
    MatrixImpedanceBranchEquipment,
    MatrixImpedanceBranch,
    SequenceImpedanceBranchEquipment,
    SequenceImpedanceBranch,
    GeometryBranchEquipment,
    GeometryBranch,
    MatrixImpedanceFuseEquipment,
    MatrixImpedanceFuse,
    MatrixImpedanceSwitch,
    MatrixImpedanceRecloser,
    MatrixImpedanceRecloserEquipment,
    MatrixImpedanceSwitchEquipment,
    DistributionTransformerEquipment,
)

EQUIPMENT_TO_CLASS_TYPE = {
    MatrixImpedanceBranch: MatrixImpedanceBranchEquipment,
    MatrixImpedanceFuse: MatrixImpedanceFuseEquipment,
    MatrixImpedanceRecloser: MatrixImpedanceRecloserEquipment,
    MatrixImpedanceSwitch: MatrixImpedanceSwitchEquipment,
    SequenceImpedanceBranch: SequenceImpedanceBranchEquipment,
    GeometryBranch: GeometryBranchEquipment,
    DistributionTransformer: DistributionTransformerEquipment,
}
