import casadi as ca

from fabrics.planner.default_maps import ParameterizedGoalMap
from fabrics.diffGeometry.geometry import Geometry
from fabrics.diffGeometry.energy import Lagrangian
from fabrics.leaves.leaf import Leaf
from fabrics.helpers.variables import Variables


class GenericAttractor(Leaf):
    """
    The GenericAttractor is a leaf to the tree of fabrics.

    The attractor's potential and metric are defined through the corresponding
    functions to which the symbolic expression is passed as a string.
    """

    def __init__(
        self, root_variables: Variables, fk_goal: ca.SX, attractor_name: str
    ):
        goal_dimension = fk_goal.size()[0]
        super().__init__(
            root_variables,
            f"{attractor_name}_leaf",
            fk_goal,
            dim=goal_dimension,
        )
        self.set_forward_map(attractor_name)

    def set_forward_map(self, goal_name):
        reference_name = f"x_{goal_name}"
        goal_dimension = self._forward_kinematics.size()[0]
        if reference_name in self._parent_variables.parameters():
            reference_variable = self._parent_variables.parameters()[
                reference_name
            ]
        else:
            reference_variable = ca.SX.sym(reference_name, goal_dimension)
        geo_parameters = {
            reference_name: reference_variable,
        }
        self._parent_variables.add_parameters(geo_parameters)
        self._forward_map = ParameterizedGoalMap(
            self._parent_variables, self._forward_kinematics, reference_variable
        )

    def set_potential(self, potential: str) -> None:
        x = self._leaf_variables.position_variable()
        xdot = self._leaf_variables.velocity_variable()
        psi = eval(potential)
        h_psi = ca.gradient(psi, x)
        self._geo = Geometry(h=h_psi, var=self._leaf_variables)

    def set_metric(self, attractor_metric: str) -> None:
        x = self._leaf_variables.position_variable()
        xdot = self._leaf_variables.velocity_variable()
        attractor_metric = eval(attractor_metric)
        lagrangian_psi = ca.dot(xdot, ca.mtimes(attractor_metric, xdot))
        self._lag = Lagrangian(lagrangian_psi, var=self._leaf_variables)

    def map(self):
        return self._forward_map
