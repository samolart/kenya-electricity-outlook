# Data dictionary

## data/processed/regional_panel.csv (252 rows) and kenya_annual.csv (26 rows)

| Field | Unit | Description |
|---|---|---|
| country, year | | Panel keys (kenya_annual.csv has year only) |
| hydro, geothermal_other_ren, wind, solar, bioenergy, coal, gas, other_fossil, nuclear | TWh | Generation by source (Ember). `geothermal_other_ren` is Ember's "Other renewables", which for Kenya is predominantly geothermal |
| net_imports | TWh | Imports minus exports |
| generation | TWh | Total generation |
| demand | TWh | Electricity demand = generation + net imports |
| fossil, clean, renewables | TWh | Ember aggregates |
| emissions_mtco2e | Mt CO2e | Power-sector emissions |
| emissions_intensity_g_kwh | g CO2e/kWh | Emissions per kWh generated |
| population | persons | OWID |
| gdp | 2011 int-$ | OWID; Kenya ends 2022 |
| demand_per_capita_kwh | kWh | demand x 1e9 / population |
| gdp_per_capita | 2011 int-$ | gdp / population |

## outputs/tables/security_index_panel.csv

| Field | Description |
|---|---|
| hhi | Herfindahl index of generation shares over nine sources (0.11 even to 1.0 single source) |
| imp_dep | max(0, net imports / demand) x 100 |
| fossil_share, hydro_share | % of generation |
| hydro_vol | Rolling 8-year (min 5) std dev of hydro growth |
| hydro_risk | hydro_share x hydro_vol |
| s_imp_dep, s_hhi, s_fossil_share, s_hydro_risk | Pillar scores 0-100 (100 = most secure), winsorised at pooled 5th/95th percentiles |
| SSI, SSI_geo | Equal-weight arithmetic and geometric index |

## Other output tables

| File | Contents |
|---|---|
| backtest_all_forecasts.csv | Every out-of-sample forecast: model, origin, horizon, actual, prediction, log error |
| backtest_summary.csv | MAPE, RMSE, bias, error relative to drift, by model and horizon |
| demand_forecast_statistical_2026_2035.csv | Model paths, ensemble, 80% and 95% bounds |
| stress_scenarios_2025.csv | Deterministic scenario results |
| capacity_gap_scenarios.csv | Gap (TWh) and new GW by demand path, year and technology mix |
| regional_benchmark_2024.csv | Peer comparison |
| data_quality.json, data_reconciliation_kenya.csv | Quality checks |
| elasticities.json, forecast_facts.json, stage3_facts.json | Key numeric results used in the reports |
