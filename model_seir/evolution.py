import cupy as cp

from .parameters_control import param_to_index, fixed_params_to_index


def evolve(params, fixed_params, state):
    """SIED evolve algorithm"""
    eta = fixed_params[fixed_params_to_index['eta']]
    mu = fixed_params[fixed_params_to_index['mu']]
    lambda_ = params[param_to_index['lambda']]

    state[3] = mu * state[2]

    p_infected = lambda_ * state[2]

    state[2] = state[1]*eta + state[2]*(1-mu)

    state[1] = state[0] * p_infected + (1-eta)*state[1]

    state[0] *= (1 - p_infected)