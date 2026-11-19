# The following code is used to:
# Reconstruct water isotope compositions with a selected theta model
#
# INPUT:    carbonate isotope compositions, temperature, and theta model
#
# OUTPUT:   reconstructed water Δ’17O values

import numpy as np

from _helper_functions import a17_cc, a18_cc, theta_cc


def reconstruct_water_Dp17O(
    carbonate_d18o: float | np.ndarray,
    carbonate_dp17o: float | np.ndarray,
    temperature_c: float | np.ndarray,
    model: str = "GuoZhou",
) -> float | np.ndarray:
    """Reconstruct water Delta'17O from carbonate d18O, Delta'17O, and temperature."""
    temperature_k = np.asarray(temperature_c) + 273.15
    a18 = a18_cc(temperature_k)
    theta = theta_cc(temperature_k, model)
    a17 = a17_cc(temperature_k, model)
    if not np.allclose(a17, a18**theta):
        raise ValueError("a17_cc(T) does not match a18_cc(T) ** theta_cc(T).")
    water_d18o = (np.asarray(carbonate_d18o) + 1000) / a18 - 1000
    carbonate_d18o_prime = 1000 * np.log(np.asarray(carbonate_d18o) / 1000 + 1)
    carbonate_d17o_prime = np.asarray(carbonate_dp17o) / 1000 + 0.528 * carbonate_d18o_prime
    carbonate_d17o = (np.exp(carbonate_d17o_prime / 1000) - 1) * 1000
    water_d17o = (carbonate_d17o + 1000) / a17 - 1000
    return (1000 * np.log(water_d17o / 1000 + 1) - 0.528 * 1000 * np.log(water_d18o / 1000 + 1)) * 1000
