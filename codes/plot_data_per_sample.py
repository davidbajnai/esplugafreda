# Import libraries -------------------------------------------------------------
from _plot_style import *
from _helper_functions import *

import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
from reconstruct_water_Dp17O import reconstruct_water_Dp17O
from pathlib import Path


# Define relative file paths ---------------------------------------------------
figures_dir = Path(__file__).resolve().parent.parent / "figures"
data_dir = Path(__file__).resolve().parent.parent / "data"


# Load Data --------------------------------------------------------------------
def plot_calcite_equilibrium(
    water_dp17o: float, water_d18o: float, minimum_temperature: float,
    ax: Axes, color: str = "k"
) -> pd.DataFrame:
    water_d17o = d17O(water_d18o, water_dp17o)

    # Plot the equilibrium line
    equilibrium_temperatures = np.arange(minimum_temperature, 290, 1) + 273.15
    mineral_d18o = d18O_cc(equilibrium_temperatures, water_d18o)
    mineral_d17o = d17O_cc(equilibrium_temperatures, water_d17o)
    mineral_equilibrium = np.array(
        [mineral_d18o, Dp17O(mineral_d17o, mineral_d18o),
         equilibrium_temperatures]
    ).T
    ax.plot(prime(mineral_equilibrium[:, 0]), mineral_equilibrium[:, 1],
            c=color, ls=":", zorder=0)

    # Return equilibrium data as a dataframe
    equilibrium_df = pd.DataFrame(mineral_equilibrium)
    equilibrium_df[2] = equilibrium_df[2] - 273.15
    equilibrium_df = equilibrium_df.rename(
        columns={0: "d18O", 1: "Dp17O", 2: "temperature"}
    )
    return equilibrium_df


def sample_key(sample_name: str) -> str:
    # Match sample codes across metadata and replicate naming conventions.
    key = re.sub(r"[^a-z0-9]", "", str(sample_name).lower())
    key = re.sub(r"itseyssc(\d+).*", r"itseys\1", key)
    return re.sub(r"(itseys\d+)sc.*", r"\1", key)


def reconstructed_water_errors(row: pd.Series) -> pd.Series:
    # Use all uncertainty-range corners to retain the existing error propagation.
    corners = np.array([
        [
            (carbonate_d18o + 1000) / a18_cc(temperature + 273.15) - 1000,
            reconstruct_water_Dp17O(
                carbonate_d18o, carbonate_dp17o, temperature
            ),
        ]
        for carbonate_d18o in row["d18O"] + np.array([
            -row["δ18O_SE"], row["δ18O_SE"]
        ])
        for carbonate_dp17o in row["Dp17O_AC"] + np.array([
            -row["Dp17O_error"], row["Dp17O_error"]
        ])
        for temperature in row["temperature"] + np.array([
            -row["temperature_SE"], row["temperature_SE"]
        ])
    ])
    return pd.Series({
        "reconstructed_water_d18O_error": np.ptp(corners[:, 0]) / 2,
        "reconstructed_water_Dp17O_error": np.ptp(corners[:, 1]) / 2
    })


df_carbonates = pd.read_csv(data_dir / "output" / "csv" / "replicate_data_scaled_averaged.csv")
replicate_columns = df_carbonates.columns.tolist()
df_sample_info = pd.read_csv(data_dir / "input" / "sample_info.csv")
df_meteoric = pd.read_csv(data_dir / "input" / "water_data" / "Aron_2021.csv")

df_sample_info["sample_key"] = df_sample_info["Sample code"].map(sample_key)
df_sample_info["δ18O_SE"] = df_sample_info["δ18O_SD"] / np.sqrt(df_sample_info["N"])
df_sample_info = df_sample_info.groupby("sample_key", as_index=False).agg(
    d18O=("δ18O", "mean"),
    δ18O_SE=("δ18O_SE", lambda x: np.sqrt(np.sum(x**2)) / len(x)),
    temperature=("Temperature", "mean"),
    temperature_SE=("Temperature_SE", lambda x: np.sqrt(np.sum(x**2)) / len(x))
)
df_carbonates["sample_key"] = df_carbonates["SampleName"].map(sample_key)
df_carbonates = df_carbonates.merge(df_sample_info, on="sample_key", how="left")
df_carbonates["reconstructed_water_d18O"] = (df_carbonates["d18O"] + 1000) / a18_cc(df_carbonates["temperature"] + 273.15) - 1000
df_carbonates["reconstructed_water_Dp17O"] = reconstruct_water_Dp17O(
    df_carbonates["d18O"], df_carbonates["Dp17O_AC"], df_carbonates["temperature"]
)


df_carbonates[["reconstructed_water_d18O_error", "reconstructed_water_Dp17O_error"]] = (
    df_carbonates.apply(reconstructed_water_errors, axis=1)
)

export_table(
    df_carbonates[replicate_columns + ["d18O", "δ18O_SE", "temperature", "temperature_SE",
                                       "reconstructed_water_d18O", "reconstructed_water_d18O_error",
                                       "reconstructed_water_Dp17O", "reconstructed_water_Dp17O_error"]],
    "all_data",
    False
)

df_carbonates["period"] = np.where(
    df_carbonates["SampleName"].str.contains("ys", case=False, regex=False),
    "PETM", "latest Paleocene")

# Export individual reconstructions before calculating or plotting group means.
df_soil_water = df_carbonates[[
    "SampleName", "period", "d18O", "δ18O_SE", "Dp17O_AC", "Dp17O_error",
    "temperature", "temperature_SE",
    "reconstructed_water_d18O", "reconstructed_water_d18O_error",
    "reconstructed_water_Dp17O", "reconstructed_water_Dp17O_error",
]].copy()
df_soil_water.to_csv(
    data_dir / "output" / "csv" / "reconstructed_soil_water.csv", index=False
)

# Apply plot style -------------------------------------------------------------
apply_plot_style()


# Create figure ----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.5, 3.5))


# Plot data --------------------------------------------------------------------
water_rows = []
for _, row in df_carbonates.iterrows():
    is_ys = "ys" in str(row["SampleName"])
    color = C["yellow"] if is_ys else C["yellow8"]
    water_d18o = row["reconstructed_water_d18O"]
    water_dp17o = row["reconstructed_water_Dp17O"]
    water_rows.append({"is_ys": is_ys, "water_d18o": water_d18o, "water_dp17o": water_dp17o, "temperature": row["temperature"]})
    xs = prime(water_d18o + np.array([-row["reconstructed_water_d18O_error"], row["reconstructed_water_d18O_error"]]))
    ys = water_dp17o + np.array([-row["reconstructed_water_Dp17O_error"], row["reconstructed_water_Dp17O_error"]])
    ax.add_patch(Rectangle((xs.min(), ys.min()), np.ptp(xs), np.ptp(ys),
                           fc=color, ec=color, alpha=0.2, lw=0.6, zorder=1))
    ax.errorbar(prime(row["d18O"]), row["Dp17O_AC"],
                xerr=row["δ18O_SE"], yerr=row["Dp17O_error"],
                fmt='none', ecolor=color)
    ax.scatter(prime(row["d18O"]), row["Dp17O_AC"],
            marker='o', fc=color, ec="k", zorder = 2)
    # Equilibrium curve for this sample, starting at its own temperature
    plot_calcite_equilibrium(
        water_dp17o, water_d18o,
        row["temperature"], ax, color=color)

df_water = pd.DataFrame(water_rows)
range_label_positions = {
    True: (1, 10),    # PETM (yellow)
    False: (-22, -60),  # latest Paleocene (red)
}
for is_ys, color in [(True, C["yellow"]), (False, C["yellow8"])]:
    group = df_water[df_water["is_ys"] == is_ys]
    water_d18o_min, water_d18o_max = group["water_d18o"].min(), group["water_d18o"].max()
    water_dp17o_min, water_dp17o_max = group["water_dp17o"].min(), group["water_dp17o"].max()
    temperature_min, temperature_max = group["temperature"].min(), group["temperature"].max()
    period = "PETM" if is_ys else "latest Paleocene"
    ax.annotate(
        f"{period}:\n$\\delta^{{18}}O_{{water}}$: {water_d18o_min:.1f} ‰ to {water_d18o_max:.1f} ‰\n"
        f"$\\Delta\\prime^{{17}}O_{{water}}$: {water_dp17o_min:.0f} ppm to {water_dp17o_max:.0f} ppm\n"
        f"$\\it{{T}}$: {temperature_min:.0f} °C to {temperature_max:.0f} °C",
        xy=(prime(group["water_d18o"].mean()), group["water_dp17o"].mean()),
        xytext=range_label_positions[is_ys],
        arrowprops=dict(
            arrowstyle="->", color="k", lw=0.8,
            connectionstyle="arc3,rad=-0.15", shrinkB=8,
        ),
        fontsize=7, ha="left", va="center", color="k",
    )

# Modern meteoric waters
ax.scatter(prime(df_meteoric["δ18O"]), df_meteoric["Dp17O"],
           marker='.', fc=C["wgray"], ec="none", alpha=0.5, s=30)
ax.text(-3, 40, "modern\nevaporative waters",
        fontsize=7, ha="left", va="top", color=C["wgray"])


# Add legend -------------------------------------------------------------------
# Period annotations identify the plotted groups.


# Setup axes -------------------------------------------------------------------
setup_axes(fig)
ax.set_xlim(-25, 35)
ax.set_ylim(-115, 45)
# Add axis labels --------------------------------------------------------------
ax.set_xlabel(r"$\delta\prime^{18}\mathrm{O}$ (‰ VSMOW)")
ax.set_ylabel(r"$\Delta\prime^{17}\mathrm{O}$ (ppm)")

# Save figure
save_figure(fig, figures_dir, "carbonates_per_sample")



# Create figure ----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.5, 3.5))


# Plot data --------------------------------------------------------------------
for _, row in df_carbonates.iterrows():
    color = C["yellow"] if "ys" in str(row["SampleName"]) else C["yellow8"]
    ax.errorbar(row["d18O_AC"], row["d18O"],
                xerr=row["d18O_error"], yerr=row["δ18O_SE"],
                fmt="none", ecolor=color, alpha=0.8, zorder=1)
    ax.scatter(row["d18O_AC"], row["d18O"],
               marker="o", fc=color, ec="k", zorder=2)
lims = [
    min(df_carbonates["d18O_AC"].min(), df_carbonates["d18O"].min()),
    max(df_carbonates["d18O_AC"].max(), df_carbonates["d18O"].max())
]
ax.plot(lims, lims, c="k", ls=":", zorder=1)

# Add legend -------------------------------------------------------------------
# Colors use the same period mapping as the water figure.


# Setup axes -------------------------------------------------------------------
setup_axes(fig)
# ax.set_xlim(lims)
# ax.set_ylim(lims)
# Add axis labels --------------------------------------------------------------
ax.set_xlabel(r"$\delta^{18}\mathrm{O}$ this study (‰)")
ax.set_ylabel(r"$\delta^{18}\mathrm{O}$ Ujvari et al. 2025 (‰)")
save_figure(fig, figures_dir, "d18O_AC_vs_d18O")
