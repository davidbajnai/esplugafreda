# The following code is used to:
# Compare carbonate and reconstructed soil-water isotope compositions
#
# INPUT:    replicate_data_scaled_averaged.csv
#           sample_info.csv
#           Aron_2021.csv
#           Kelson_2026_meteoric_water.csv
#           Kelson_2026_soil_water.csv
#
# OUTPUT:   carbonates_averaged_water.png
#           carbonates_averaged_water.svg
#           carbonates_averaged_water_theta_comparison.png
#           carbonates_averaged_water_theta_comparison.svg
#           reconstructed_soil_water.csv
#           reconstructed_water_averaged.csv
#           reconstructed_water_averaged.xlsx
#           table_S4.xlsx

"""Period-average waters with unweighted means and sample SD (ddof=1).
Reported uncertainties describe between-sample variability within each period.
"""
# Import libraries -------------------------------------------------------------
from _plot_style import *
from _helper_functions import *

from matplotlib.ticker import MultipleLocator
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
from reconstruct_water_Dp17O import reconstruct_water_Dp17O
from pathlib import Path


# Define relative file paths -------------------------------------------------
figures_dir = Path(__file__).resolve().parent.parent / "figures"
data_dir = Path(__file__).resolve().parent.parent / "data"


# Load Data ------------------------------------------------------------------
def plot_calcite_equilibrium(
    water_dp17o: float, water_d18o: float, minimum_temperature: float,
    ax: Axes, color: str = "k", model: str = "Hayles"
) -> pd.DataFrame:
    water_d17o = d17O(water_d18o, water_dp17o)

    # Plot the equilibrium line
    equilibrium_temperatures = np.arange(minimum_temperature, 290, 1) + 273.15
    mineral_d18o = d18O_cc(equilibrium_temperatures, water_d18o)
    mineral_d17o = d17O_cc(equilibrium_temperatures, water_d17o, model)
    mineral_equilibrium = np.array(
        [mineral_d18o, Dp17O(mineral_d17o, mineral_d18o),
         equilibrium_temperatures]
    ).T
    ax.plot(prime(mineral_equilibrium[:, 0]), mineral_equilibrium[:, 1],
            c = color, ls=":", zorder=0)

    # Return equilibrium data as a dataframe
    equilibrium_df = pd.DataFrame(mineral_equilibrium)
    equilibrium_df[2] = equilibrium_df[2] - 273.15
    equilibrium_df = equilibrium_df.rename(
        columns = {0: "d18O", 1: "Dp17O", 2: "temperature"}
    )
    return equilibrium_df


def sample_key(sample_name: str) -> str:
    # Match sample codes across metadata and replicate naming conventions.
    key = re.sub(r"[^a-z0-9]", "", str(sample_name).lower())
    key = re.sub(r"itseyssc(\d+).*", r"itseys\1", key)
    return re.sub(r"(itseys\d+)sc.*", r"\1", key)


def reconstructed_water_errors(row: pd.Series, model: str = "Hayles") -> pd.Series:
    # Use all uncertainty-range corners to retain the existing error propagation.
    corners = np.array([
        [
            (carbonate_d18o + 1000) / a18_cc(temperature + 273.15) - 1000,
            reconstruct_water_Dp17O(
                carbonate_d18o, carbonate_dp17o, temperature, model
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
df_sample_info = pd.read_csv(data_dir / "input" / "sample_info.csv")
df_meteoric = pd.read_csv(data_dir / "input" / "water_data" / "Aron_2021.csv")
df_kelson_meteoric = pd.read_csv(
    data_dir / "input" / "water_data" / "Kelson_2026_meteoric_water.csv"
)
df_kelson_soil = pd.read_csv(
    data_dir / "input" / "water_data" / "Kelson_2026_soil_water.csv"
)

# Combine comparison waters with matching isotope column names.
df_meteoric = pd.concat([
    df_meteoric[["δ18O", "Dp17O"]],
    df_kelson_meteoric[["d18O.mean", "D17O_pmg"]].rename(
        columns = {"d18O.mean": "δ18O", "D17O_pmg": "Dp17O"}
    ),
], ignore_index=True)

df_sample_info["sample_key"] = df_sample_info["Sample code"].map(sample_key)
df_sample_info["δ18O_SE"] = df_sample_info["δ18O_SD"] / np.sqrt(df_sample_info["N"])
df_sample_info = df_sample_info.groupby("sample_key", as_index=False).agg(
    d18O=("δ18O", "mean"),
    δ18O_SE=("δ18O_SE", lambda x: np.sqrt(np.sum(x**2)) / len(x)),
    temperature = ("Temperature", "mean"),
    temperature_SE=("Temperature_SE", lambda x: np.sqrt(np.sum(x**2)) / len(x))
)
df_carbonates["sample_key"] = df_carbonates["SampleName"].map(sample_key)
df_carbonates = df_carbonates.merge(df_sample_info, on="sample_key", how="left")

# Keep measured clumped isotopes temperatures separate from reconstruction inputs.
df_carbonates["clumped_temperature"] = df_carbonates["temperature"]

df_carbonates["reconstructed_water_d18O"] = (df_carbonates["d18O"] + 1000) / a18_cc(df_carbonates["temperature"] + 273.15) - 1000
df_carbonates["reconstructed_water_Dp17O"] = reconstruct_water_Dp17O(
    df_carbonates["d18O"], df_carbonates["Dp17O_AC"], df_carbonates["temperature"],
    model = "Hayles",
)


df_carbonates[["reconstructed_water_d18O_error", "reconstructed_water_Dp17O_error"]] = (
    df_carbonates.apply(reconstructed_water_errors, axis=1)
)

# Unweighted period means and sample SD describe between-sample variability.
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


df_carbonate_means = df_carbonates.groupby("period", sort=False).agg(
    samples = ("SampleName", "size"),
    d18o=("d18O", "mean"),
    d18o_sd=("d18O", "std"),
    dp17o=("Dp17O_AC", "mean"),
    dp17o_sd=("Dp17O_AC", "std"),
    temperature_min = ("clumped_temperature", "min"),
    temperature_max = ("clumped_temperature", "max"),
    temperature_mean = ("clumped_temperature", "mean"),
    temperature_sd = ("clumped_temperature", "std"),
).reset_index()
print("\nPeriod-average carbonate compositions")
print("Uncertainties: sample SD within each period (ddof=1); all ± values are 1 SD.")
for _, row in df_carbonate_means.iterrows():
    print(
        f"\nFor {row['period']} (n={int(row['samples'])}), "
        f"the mean carbonate δ18O is {row['d18o']:.1f} ± {row['d18o_sd']:.1f} ‰ VSMOW "
        f"and Δ′17O is {row['dp17o']:.2f} ± {row['dp17o_sd']:.2f} ppm "
        "(mean ± SD). "
        f"Clumped isotopes T: min {row['temperature_min']:.2f} °C, "
        f"max {row['temperature_max']:.2f} °C, "
        f"mean {row['temperature_mean']:.2f} ± {row['temperature_sd']:.2f} °C "
        "(mean ± SD)."
    )


df_water = df_carbonates.groupby("period", sort=False).agg(
    samples = ("SampleName", "size"),
    d18Ow=("reconstructed_water_d18O", "mean"),
    d18Ow_SD=("reconstructed_water_d18O", "std"),
    Dp17Ow=("reconstructed_water_Dp17O", "mean"),
    Dp17Ow_SD=("reconstructed_water_Dp17O", "std"),
    temperature = ("temperature", "mean"),
    temperature_SD=("temperature", "std"),
).reset_index()
print("\nPeriod-average reconstructed waters")
print("Uncertainties: sample SD within each period (ddof=1); all ± values are 1 SD.")
for _, row in df_water.iterrows():
    print(
        f"\nFor {row['period']} (n={int(row['samples'])}), "
        f"the mean reconstructed water δ18O is {row['d18Ow']:.1f} ± {row['d18Ow_SD']:.1f} ‰ "
        f"and Δ'17O is {row['Dp17Ow']:.2f} ± {row['Dp17Ow_SD']:.2f} ppm. "
        f"The mean temperature is {row['temperature']:.2f} ± {row['temperature_SD']:.2f} °C "
        "(mean ± SD)."
    )
export_table(df_water, "reconstructed_water_averaged", False)

# Calculate the alternative period means without replacing the Hayles exports.
df_guozhou = df_carbonates.copy()
df_guozhou["reconstructed_water_Dp17O"] = reconstruct_water_Dp17O(
    df_guozhou["d18O"], df_guozhou["Dp17O_AC"], df_guozhou["temperature"],
    model = "GuoZhou",
)
df_water_guozhou = df_water.copy()
guozhou_groups = df_guozhou.groupby("period")["reconstructed_water_Dp17O"]
df_water_guozhou["Dp17Ow"] = df_water_guozhou["period"].map(guozhou_groups.mean())
df_water_guozhou["Dp17Ow_SD"] = df_water_guozhou["period"].map(guozhou_groups.std())
water_models = {"Hayles": df_water, "GuoZhou": df_water_guozhou}

# Apply plot style ------------------------------------------------------------
apply_plot_style()


for figure_name, models in (
    ("carbonates_averaged_water", ("Hayles",)),
    ("carbonates_averaged_water_theta_comparison", ("Hayles", "GuoZhou")),
):
    comparison = len(models) > 1
    # Create figure ------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(3.5, 3.5))


    # Setup axes -------------------------------------------------------------
    setup_axes(fig)
    ax.set_xlim(-23, 31)
    ax.set_ylim(-160, 60)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_minor_locator(MultipleLocator(5))


    ax.set_xlabel(r"$\delta\prime^{18}\mathrm{O}$ (‰ VSMOW)")
    ax.set_ylabel(r"$\Delta\prime^{17}\mathrm{O}$ (ppm)")


    # Plot data --------------------------------------------------------------
    colors = {"PETM": C["cie_body"], "latest Paleocene": C["pre_petm"]}
    markers = {"PETM": "D", "latest Paleocene": "o"}
    period_labels = {"PETM": "CIE body", "latest Paleocene": "pre-PETM"}
    carbonate_handles = {}
    for _, row in df_carbonates.iterrows():
        color = colors[row["period"]]
        x = prime(row["d18O"])
        bounds = prime(row["d18O"] + np.array([-row["δ18O_SE"], row["δ18O_SE"]]))
        ax.errorbar(x, row["Dp17O_AC"], xerr=[[x-bounds[0]], [bounds[1]-x]],
                    yerr = row["Dp17O_error"], fmt="none", ecolor=color, capsize=1.5, zorder=1)
        period = row["period"]
        carbonate_handles[period] = ax.scatter(
            x, row["Dp17O_AC"], marker=markers[period], fc=color, ec="k", zorder=2, s=20,
            label = f"carbonate, {period_labels[period]}",
        )

    # Plot the unweighted group means of the individual water reconstructions.
    water_handles = {}
    for model in models:
        for _, row in water_models[model].iterrows():
            period = row["period"]
            color = colors[period]
            xs = prime(row["d18Ow"] + np.array([-row["d18Ow_SD"], row["d18Ow_SD"]]))
            ys = row["Dp17Ow"] + np.array([-row["Dp17Ow_SD"], row["Dp17Ow_SD"]])
            ax.add_patch(Rectangle((xs.min(), ys.min()), np.ptp(xs), np.ptp(ys),
                                   fc = color, ec=color, alpha=0.2, lw=0.6, zorder=1))
            water_handles[(model, period)] = ax.scatter(
                prime(row["d18Ow"]), row["Dp17Ow"],
                marker = "*", fc=color, ec=C["red"] if model == "GuoZhou" else "k", zorder=3, s=50,
                label = f"soil water, {period_labels[period]}" + (f" ({model})" if comparison else ""),
            )
            plot_calcite_equilibrium(row["Dp17Ow"], row["d18Ow"],
                                    row["temperature"], ax, color=color, model=model)


    meteoric_handle = ax.scatter(prime(df_meteoric["δ18O"]), df_meteoric["Dp17O"],
               marker = "o", fc=C["modern_meteoric"], ec="none", s=10,
               label = "modern meteoric waters")
    soil_handle = ax.scatter(prime(df_kelson_soil["d18O.mean"]), df_kelson_soil["D17O_pmg"],
               marker = "s", fc=C["modern_soil"], ec="none", s=10,
               label = "modern soil waters")


    # Add legend -------------------------------------------------------------
    legend_handles = [meteoric_handle, soil_handle]
    legend_handles.extend(carbonate_handles[period] for period in ("latest Paleocene", "PETM"))
    for model in models:
        legend_handles.extend(water_handles[(model, period)] for period in ("latest Paleocene", "PETM"))
    add_standard_legend(
        ax, handles=legend_handles, loc="lower left", fontsize=5 if comparison else 6, markerscale=1,
    )


    save_figure(fig, figures_dir, figure_name)



# Create table --------------------------------------------------------------
# Average repeated metadata records using the existing sample matching.
df_table_metadata = pd.read_csv(data_dir / "input" / "sample_info.csv")
df_table_metadata["sample_key"] = df_table_metadata["Sample code"].map(sample_key)
df_table_metadata = df_table_metadata.groupby("sample_key", as_index=False).agg(
    composite_depth = ("Composite depth (m)", "mean"),
    d18o_irms=("δ18O", "mean"),
    d18o_irms_sd=("δ18O_SD", "mean"),
    temperature_irms = ("Temperature", "mean"),
    temperature_irms_se = ("Temperature_SE", "mean"),
)
df_table_s4 = df_carbonates.merge(df_table_metadata, on="sample_key", how="left")
df_table_s4 = df_table_s4.sort_values("composite_depth").reset_index(drop=True)
df_table_s4["interval"] = df_table_s4["period"].map({
    "latest Paleocene": "pre-PETM", "PETM": "CIE body",
})

# Use the existing two-sided 68% Student's t CI half-widths without rescaling.
df_table_s4["d18o_ci68"] = df_table_s4["d18O_error"]
df_table_s4["d17o_ci68"] = df_table_s4["d17O_error"]
df_table_s4["dp17o_ci68"] = df_table_s4["Dp17O_error"]

table_s4_columns=[
    "SampleName", "composite_depth", "interval", "Replicates",
    "d18O_CO2", "d18o_ci68", "d17O_CO2", "d17o_ci68",
    "Dp17O_CO2", "dp17o_ci68", "d18O_AC", "d17O_AC", "Dp17O_AC",
    "d18o_irms", "d18o_irms_sd", "temperature_irms", "temperature_irms_se",
    "reconstructed_water_d18O", "reconstructed_water_d18O_error",
    "reconstructed_water_Dp17O", "reconstructed_water_Dp17O_error",
]
table_s4_headers=[
    "Sample", "Composite depth (m)", "Interval", "Replicates",
    "δ18O_CO2 (‰)", "68% CI half-width (‰)",
    "δ17O_CO2 (‰)", "68% CI half-width (‰)",
    "Δ′17O_CO2 (ppm)", "68% CI half-width (ppm)",
    "δ18O_carb (‰, V-SMOW)", "δ17O_carb (‰, V-SMOW)",
    "Δ′17O_carb (ppm, V-SMOW)", "δ18O_carb_IRMS (‰, V-SMOW)",
    "1σ (‰)", "T(Δ47) (°C)", "1SE (°C)",
    "δ18Owater (‰, V-SMOW)", "δ18Owater, uncertainty envelope (± ‰)",
    "Δ′17Owater (ppm)", "Δ′17Owater, uncertainty envelope (± ppm)",
]
table_s4_formats=[
    "General", "0.00", "General", "0",
    "0.00", "0.00", "0.00", "0.00", "0", "0",
    "0.00", "0.00", "0", "0.00", "0.00", "0.0", "0.0",
    "0.00", "0.00", "0", "0",
]
workbook = Workbook()
worksheet = workbook.active
worksheet.title = "Table_S4"
worksheet.sheet_view.showGridLines=False
worksheet.freeze_panes="B2"
worksheet.append(table_s4_headers)
for values in df_table_s4[table_s4_columns].itertuples(index=False, name=None):
    worksheet.append(values)

for column, number_format in zip(worksheet.columns, table_s4_formats):
    header = column[0]
    header.font = Font(name="Arial", size=10, bold=True)
    header.fill = PatternFill(fill_type="solid", fgColor="D9EAF7")
    header.alignment = Alignment(horizontal="center", vertical="center")
    display_lengths = [len(str(header.value))]
    for cell in column[1:]:
        cell.font = Font(name="Arial", size=10)
        cell.number_format = number_format
        cell.alignment = Alignment(
            horizontal = "left" if number_format == "General" else "right",
            vertical = "center",
        )
        if number_format == "General":
            display_lengths.append(len(str(cell.value)))
        else:
            decimals = len(number_format.partition(".")[2])
            display_lengths.append(len(f"{cell.value:.{decimals}f}"))
    worksheet.column_dimensions[header.column_letter].width = (
        max(display_lengths) * 1.15 + 3
    )
worksheet.row_dimensions[1].height = 22
workbook.save(data_dir / "output" / "xlsx" / "table_S4.xlsx")
