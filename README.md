# Supplementary material for</br> "Convergent Magnetic, Geochemical and Triple Oxygen Evidence for Increased Soil Moisture during the PETM, Southern Pyrenees"

## Graphical abstract

![Graphical abstract](figures/png/carbonates_averaged_water.png)

## Reference

> [!IMPORTANT]
> Újvári, G., Bajnai, D., Kelson, J., Bógalo, M. F., Bradák-Hayashi, B., Payros, A., Pesnin, M., & Kele, S. (under review). Convergent magnetic, geochemical and triple oxygen evidence for increased soil moisture during the PETM, southern Pyrenees.

## Codes

- [scale_data.py](codes/scale_data.py) scales and averages the carbonate triple oxygen isotope measurements. Input: [replicate_data.csv](data/input/replicate_data.csv). Output: [replicate_data_scaled.csv](data/output/csv/replicate_data_scaled.csv), [replicate_data_scaled.xlsx](data/output/xlsx/replicate_data_scaled.xlsx), [replicate_data_scaled_averaged.csv](data/output/csv/replicate_data_scaled_averaged.csv), [replicate_data_scaled_averaged.xlsx](data/output/xlsx/replicate_data_scaled_averaged.xlsx), [replicates_a.png](figures/png/replicates_a.png), [replicates_b.png](figures/png/replicates_b.png), and [replicates_d-e.png](figures/png/replicates_d-e.png).
- [plot_data_averaged_water.py](codes/plot_data_averaged_water.py) provides separate figures for the main carbonate and soil-water reconstruction and the comparison of Hayles, GuoZhou, and Wostbrock equilibrium relationships, with period-difference uncertainties calculated by combining the period sample SDs in quadrature. Input: [replicate_data_scaled_averaged.csv](data/output/csv/replicate_data_scaled_averaged.csv), [replicate_data_scaled_averaged_Wostbrock.csv](data/output/csv/replicate_data_scaled_averaged_Wostbrock.csv), [sample_info.csv](data/input/sample_info.csv), [Aron_2021.csv](data/input/water_data/Aron_2021.csv), [Kelson_2026_meteoric_water.csv](data/input/water_data/Kelson_2026_meteoric_water.csv), and [Kelson_2026_soil_water.csv](data/input/water_data/Kelson_2026_soil_water.csv). Output: [reconstructed_water_averaged.csv](data/output/csv/reconstructed_water_averaged.csv), [reconstructed_water_averaged.xlsx](data/output/xlsx/reconstructed_water_averaged.xlsx), [reconstructed_soil_water.csv](data/output/csv/reconstructed_soil_water.csv), [table_S4.xlsx](data/output/xlsx/table_S4.xlsx), [carbonates_averaged_water.png](figures/png/carbonates_averaged_water.png), and [theta_comparison.png](figures/png/theta_comparison.png).
- [reconstruct_water_Dp17O.py](codes/reconstruct_water_Dp17O.py) reconstructs water Δ’<sup>17</sup>O from carbonate isotope compositions and temperature using the selected Hayles, GuoZhou, or Wostbrock model. Input: carbonate δ<sup>18</sup>O, Δ’<sup>17</sup>O, and temperature values. Output: reconstructed water Δ’<sup>17</sup>O values.
- [_helper_functions.py](codes/_helper_functions.py) provides shared isotope calculations and table export.
- [_plot_style.py](codes/_plot_style.py) provides shared figure styling, default marker sizing, and export.

SVG versions of all included figures are available in the [SVG folder](figures/svg/).

## Data files

### Input data files

- [replicate_data.csv](data/input/replicate_data.csv) contains raw triple oxygen isotope measurements of Esplugafreda carbonates and reference materials. It is used by [scale_data.py](codes/scale_data.py).
- [sample_info.csv](data/input/sample_info.csv) contains carbonate δ<sup>18</sup>O measurements and clumped isotopes temperature estimates from Esplugafreda across the PETM. It is used by [plot_data_averaged_water.py](codes/plot_data_averaged_water.py).

### Exported data files

- [replicate_data_scaled.csv](data/output/csv/replicate_data_scaled.csv) contains scaled replicate triple oxygen isotope measurements of Esplugafreda carbonates. It is exported by [scale_data.py](codes/scale_data.py).
- [replicate_data_scaled_averaged.csv](data/output/csv/replicate_data_scaled_averaged.csv) contains sample-average triple oxygen isotope compositions of Esplugafreda carbonates. It is exported by [scale_data.py](codes/scale_data.py) and used by [plot_data_averaged_water.py](codes/plot_data_averaged_water.py).
- [replicate_data_scaled_averaged_Wostbrock.csv](data/output/csv/replicate_data_scaled_averaged_Wostbrock.csv) contains sample-average triple oxygen isotope compositions of Esplugafreda carbonates scaled using the Wostbrock reference values. It is used by [plot_data_averaged_water.py](codes/plot_data_averaged_water.py).
- [reconstructed_soil_water.csv](data/output/csv/reconstructed_soil_water.csv) contains individual Hayles-based soil-water isotope reconstructions from Esplugafreda before and during the PETM. It is exported by [plot_data_averaged_water.py](codes/plot_data_averaged_water.py).
- [reconstructed_water_averaged.csv](data/output/csv/reconstructed_water_averaged.csv) contains period-average Hayles-based reconstructed soil-water isotope compositions from Esplugafreda before and during the PETM. It is exported by [plot_data_averaged_water.py](codes/plot_data_averaged_water.py).

### Literature data used in the scripts

Sources for the modern water comparison datasets are listed below.

- [Aron_2021.csv](data/input/water_data/Aron_2021.csv) contains triple oxygen isotope compositions of modern waters from geographically diverse settings. Source: [Aron et al. (2021)](https://doi.org/10.1016/j.chemgeo.2020.120026).
- [Kelson_2026_meteoric_water.csv](data/input/water_data/Kelson_2026_meteoric_water.csv) contains meteoric-water isotope compositions from dryland and temperate forest sites in the United States. Source: [Kelson et al. (2026)](https://doi.org/10.1029/2026GC012921).
- [Kelson_2026_soil_water.csv](data/input/water_data/Kelson_2026_soil_water.csv) contains soil-water isotope compositions from dryland and temperate forest sites in the United States. Source: [Kelson et al. (2026)](https://doi.org/10.1029/2026GC012921).

## License

All files in this repository are available under CC0 1.0. No rights reserved.
