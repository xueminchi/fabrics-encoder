import casadi as ca
import numpy as np

from optFabrics.diffGeometry.variables import Jdot_sign


class DifferentialMap:
    """description"""

    def __init__(self, phi: ca.SX, **kwargs):
        if len(kwargs) == 2:
            q = kwargs.get('q')
            qdot = kwargs.get('qdot')
        elif len(kwargs) == 1:
            q, qdot = kwargs.get('var')
        assert isinstance(q, ca.SX)
        assert isinstance(qdot, ca.SX)
        assert isinstance(phi, ca.SX)
        self._vars = [q, qdot]
        self._phi = phi
        self._J = ca.jacobian(phi, q)
        self._Jdot = Jdot_sign * ca.jacobian(ca.mtimes(self._J, qdot), q)

    def Jdotqdot(self):
        return ca.mtimes(self._Jdot, self.qdot())

    def phidot(self):
        return ca.mtimes(self._J, self.qdot())

    def concretize(self):
        self._fun = ca.Function(
            "forward", self._vars, [self._phi, self._J, self._Jdot]
        )

    def forward(self, q: np.ndarray, qdot: np.ndarray):
        assert isinstance(q, np.ndarray)
        assert isinstance(qdot, np.ndarray)
        funs = self._fun(q, qdot)
        x = np.array(funs[0])[:, 0]
        J = np.array(funs[1])
        Jdot = np.array(funs[2])
        return x, J, Jdot

    def q(self):
        return self._vars[0]

    def qdot(self):
        return self._vars[1]


class VariableDifferentialMap(DifferentialMap):
    def __init__(self, phi: ca.SX, **kwargs):
        if len(kwargs) == 5:
            q = kwargs.get('q')
            qdot = kwargs.get('qdot')
            q_p = kwargs.get('q_p')
            qdot_p = kwargs.get('qdot_p')
            qddot_p = kwargs.get('qddot_p')
        elif len(kwargs) == 1:
            q, qdot, q_p, qdot_p, qddot_p = kwargs.get('var')
        assert isinstance(q_p, ca.SX)
        assert isinstance(qdot_p, ca.SX)
        assert isinstance(qddot_p, ca.SX)
        super().__init__(phi, q=q, qdot=qdot)
        self._vars += [q_p, qdot_p, qddot_p]
        self._J_p = ca.jacobian(phi, q_p)
        self._Jdot_p = Jdot_sign * ca.jacobian(ca.mtimes(self._J_p, qdot_p), q_p)

    def concretize(self):
        self._fun = ca.Function(
            "forward", self._vars, [self._phi, self._J, self._Jdot, self._J_p, self._Jdot_p]
        )

    def forward(self, q: np.ndarray, qdot: np.ndarray, q_p: np.ndarray, qdot_p: np.ndarray, qddot_p: np.ndarray):
        assert isinstance(q, np.ndarray)
        assert isinstance(qdot, np.ndarray)
        assert isinstance(q_p, np.ndarray)
        assert isinstance(qdot_p, np.ndarray)
        assert isinstance(qddot_p, np.ndarray)
        funs = self._fun(q, qdot, q_p, qdot_p, qddot_p)
        x = np.array(funs[0])[:, 0]
        J = np.array(funs[1])
        Jdot = np.array(funs[2])
        J_p = np.array(funs[3])
        Jdot_p = np.array(funs[4])
        return x, J, Jdot, J_p, Jdot_p

    def Jdotqdot(self):
        return ca.mtimes(self._Jdot, self.qdot()) + ca.mtimes(self._J_p, self.qddot_p())

    def phidot(self):
        return ca.mtimes(self._J, self.qdot()) + ca.mtimes(self._J_p, self.qdot_p())

    def q_p(self):
        return self._vars[2]

    def qdot_p(self):
        return self._vars[3]

    def qddot_p(self):
        return self._vars[4]


class RelativeDifferentialMap(DifferentialMap):
    def __init__(self, **kwargs):
        if len(kwargs) == 5:
            q = kwargs.get('q')
            qdot = kwargs.get('qdot')
            q_p = kwargs.get('q_p')
            qdot_p = kwargs.get('qdot_p')
            qddot_p = kwargs.get('qddot_p')
        elif len(kwargs) == 1:
            q, qdot, q_p, qdot_p, qddot_p = kwargs.get('var')
        assert isinstance(q_p, ca.SX)
        assert isinstance(qdot_p, ca.SX)
        assert isinstance(qddot_p, ca.SX)
        phi = q - q_p
        super().__init__(phi, q=q, qdot=qdot)
        self._vars += [q_p, qdot_p, qddot_p]

    def forward(self, q: np.ndarray, qdot: np.ndarray, q_p: np.ndarray, qdot_p: np.ndarray, qddot_p: np.ndarray):
        assert isinstance(q, np.ndarray)
        assert isinstance(qdot, np.ndarray)
        assert isinstance(q_p, np.ndarray)
        assert isinstance(qdot_p, np.ndarray)
        assert isinstance(qddot_p, np.ndarray)
        funs = self._fun(q, qdot, q_p, qdot_p, qddot_p)
        x = np.array(funs[0])[:, 0]
        xdot = qdot - qdot_p
        return x, xdot

    def Jdotqdot(self):
        return -1 * self.qddot_p()

    def phidot(self):
        return self.qdot() - self.qdot_p()

    def q_p(self):
        return self._vars[2]

    def qdot_p(self):
        return self._vars[3]

    def qddot_p(self):
        return self._vars[4]
