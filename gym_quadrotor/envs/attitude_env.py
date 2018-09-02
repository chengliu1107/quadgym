import numpy as np
from gym import spaces
from gym_quadrotor.envs.base import QuadRotorEnvBase, clip_attitude, ensure_fixed_position
from gym_quadrotor.dynamics.coordinates import angvel_to_euler, angle_difference


# TODO fix observation space
class CopterStabilizeAttitudeEnv(QuadRotorEnvBase):
    observation_space = spaces.Box(0, 1, (6,), dtype=np.float32)

    def __init__(self):
        super().__init__()
        self._error_target = 1 * np.pi / 180
        self._velocity_factor = 1e-2
        self._in_target_reward = 0.1

    def _step_copter(self, action: np.ndarray):
        attitude = self._state.attitude

        velocity_error = np.sum(self._state.angular_velocity ** 2)
        reward = self._calculate_reward(attitude, velocity_error)
        if clip_attitude(self._state, np.pi/4):
            reward -= 1
        ensure_fixed_position(self._state, 1.0)

        return reward, False, {}

    def _calculate_reward(self, attitude, velocity_error):
        angle_error = attitude.roll ** 2 + attitude.pitch ** 2 + angle_difference(attitude.yaw, 0) ** 2
        reward = -angle_error - self._velocity_factor * velocity_error
        # check whether error is below bound in any of the angle coordinates
        if abs(attitude.roll) < self._error_target:
            reward += self._in_target_reward / 3
        if abs(attitude.pitch) < self._error_target:
            reward += self._in_target_reward / 3
        if abs(angle_difference(attitude.yaw, 0)) < self._error_target:
            reward += self._in_target_reward / 3
        return reward

    def _get_state(self):
        s = self._state
        rate = angvel_to_euler(s.attitude, s.angular_velocity)
        state = [s.attitude.roll, s.attitude.pitch, angle_difference(s.attitude.yaw, 0.0),
                 rate[0], rate[1], rate[2]]
        return np.array(state)

    def _reset_copter(self):
        self.randomize_angle(20)
        self.randomize_angular_velocity(2.0)
        self._state.attitude.yaw = self.random_state.uniform(low=-0.3, high=0.3)
        self._state.position[2] = 1

