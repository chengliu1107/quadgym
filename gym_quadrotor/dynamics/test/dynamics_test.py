import numpy as np
import pytest

from gym_quadrotor.dynamics.coordinates import Euler
from gym_quadrotor.dynamics.dynamics import *


@pytest.fixture()
def params():
    return CopterParams()

@pytest.fixture()
def state():
    return DynamicsState()


# linear dynamics
def test_gravity_only(params, state):
    # velocity and rotorspeeds need to be zero.
    state._attitude = Euler.from_numpy_array(np.random.rand(3))
    state._angular_velocity = np.random.rand(3)
    acceleration = linear_dynamics(params, state)

    assert acceleration == pytest.approx([0.0, 0.0, -9.81])


def test_drag_only(params, state):
    params._gravity = np.zeros(3)
    params._translational_drag = np.array([0.1, 0.2, 0.3])

    state._velocity = np.array([1.0, 1.0, 1.0])
    state._angular_velocity = np.random.rand(3)
    acceleration = linear_dynamics(params, state)

    assert acceleration == pytest.approx([-0.1, -0.2, -0.3])

    # check consistency in rotation
    state._attitude = Euler.from_numpy_array(np.random.rand(3))
    state._velocity = body_to_world(state._attitude, [1.0, 1.0, 1.0])
    acceleration = linear_dynamics(params, state)

    assert acceleration == pytest.approx(body_to_world(state._attitude, [-0.1, -0.2, -0.3]))


def test_rotor_thrust(params, state):
    state._attitude = Euler.from_numpy_array(np.random.rand(3))
    state._rotorspeeds = np.array([2.0, 2.0, 2.0, 2.0])
    params._gravity = [0.0, 0.0, 0.0]

    acceleration = linear_dynamics(params, state)

    assert acceleration == pytest.approx(body_to_world(state._attitude, [0, 0, 4*2.0**2]))
