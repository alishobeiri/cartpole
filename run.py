from custom_cartpole_delay import CartPoleEnv

import gym

import numpy as np
import scipy.linalg as linalg
lqr = linalg.solve_continuous_are

env = CartPoleEnv()
env.buffer_size = 5
gravity = 9.8
masscart = 1.0
masspole = 0.1
total_mass = (masspole + masscart)
length = 0.5  # actually half the pole's length
polemass_length = (masspole * length)
force_mag = 10.0
tau = 0.02


def E(x):
	return 1/2 * masspole * (2 * length)**2 / 3 * x[3]**2 + np.cos(x[2]) * polemass_length * gravity


def u(x):
	# print(E(x)-Ed)
	return 1.0 * (E(x)-Ed) * x[3] * np.cos(x[2])


H = np.array([
	[1, 0, 0, 0],
	[0, total_mass, 0, - polemass_length],
	[0, 0, 1, 0],
	[0, - polemass_length, 0, (2 * length)**2 * masspole / 3]
	])

Hinv = np.linalg.inv(H)

A = Hinv @ np.array([
    [0, 1, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 1],
    [0, 0, - polemass_length * gravity, 0]
	])
B = Hinv @ np.array([0, 1.0, 0, 0]).reshape((4, 1))
Q = np.diag([0.01, 0.1, 100.0, 0.5])
R = np.array([[0.1]])

P = lqr(A, B, Q, R)
Rinv = np.linalg.inv(R)
K = Rinv @ B.T @ P


def ulqr(x):
	x1 = np.copy(x)
	x1[2] = np.sin(x1[2])
	return np.dot(K, x1)


Ed = E([0, 0, 0, 0])

observation = env._reset()
for _ in range(100000):
    observation = np.copy(observation)
    env._render()
    observation[0] += observation[1] * tau * env.buffer_size
    observation[2] += observation[3] * tau * env.buffer_size
    observation[3] += np.sin(observation[2]) * tau * \
                            env.buffer_size * gravity / (length * 2) / 2
    # action = env.action_space.sample() # your agent here (this takes random actions)
    a = u(observation) - 0.3 * observation[0] - 0.1 * observation[1]
    # abs(E(observation)-Ed) < 0.1 and
    if abs(E(observation)-Ed) < 0.1 and np.cos(observation[2]) > 0.6:

        a = ulqr(observation)
        env.force_mag = min(abs(a[0]), 10)
        print(a[0])
    else:
        env.force_mag = 10.0
    if a < 0:
        action = 0
    else:
        action = 1



    observation, reward, done, info = env._step(action)
