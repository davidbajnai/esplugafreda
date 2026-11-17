import numpy as np

from _helper_functions import a17_cc, a18_cc, theta_cc


def reconstruct_water_Dp17O(d18O_carbonate, Dp17O_carbonate, temperature_C):
    """Reconstruct water Delta'17O from carbonate d18O, Delta'17O, and temperature."""
    temperature_K = np.asarray(temperature_C) + 273.15
    a18 = a18_cc(temperature_K)
    theta = theta_cc(temperature_K)
    a17 = a17_cc(temperature_K)
    if not np.allclose(a17, a18**theta):
        raise ValueError("a17_cc(T) does not match a18_cc(T) ** theta_cc(T).")
    d18O_water = (np.asarray(d18O_carbonate) + 1000) / a18 - 1000
    d18O_carbonate_prime = 1000 * np.log(np.asarray(d18O_carbonate) / 1000 + 1)
    d17O_carbonate_prime = np.asarray(Dp17O_carbonate) / 1000 + 0.528 * d18O_carbonate_prime
    d17O_carbonate = (np.exp(d17O_carbonate_prime / 1000) - 1) * 1000
    d17O_water = (d17O_carbonate + 1000) / a17 - 1000
    return (1000 * np.log(d17O_water / 1000 + 1) - 0.528 * 1000 * np.log(d18O_water / 1000 + 1)) * 1000
