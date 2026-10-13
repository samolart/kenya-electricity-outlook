# CV entry and interview notes

## One-line description (CV)
**Kenya Electricity Demand Outlook & Supply-Security Assessment** | Python, pandas, scipy, time-series forecasting, Monte Carlo | GitHub: https://github.com/samolart/kenya-electricity-outlook | Live dashboard: https://samolart.github.io/kenya-electricity-outlook/

## CV bullets (pick 3-4)
- Built an end-to-end analytics pipeline on open Ember and Our World in Data electricity datasets (10 countries, 2000-2025), with automated quality checks reconciling sources to within 0.06%.
- Forecast Kenya's electricity demand to 2035 using five models (ARIMA, ETS, trend, drift) implemented from scratch; 42 rolling-origin backtests per model gave 2.9% one-year-ahead error and calibrated 80%/95% intervals.
- Designed a four-pillar supply-security index benchmarking Kenya against nine regional peers, with 10,000-draw weight-sensitivity analysis; identified import dependence (0.1% to 9.8% of demand, 2015-2025) as the main emerging vulnerability.
- Stress-tested the supply system with drought and import-loss scenarios and a 20,000-draw Monte Carlo on observed hydrology, quantifying shortfall risk (27% with imports out, 0% with imports available).
- Built a self-contained interactive HTML dashboard (hand-coded SVG charts, no BI tool) with live stress-test and capacity simulators.
- Sized the 2035 capacity gap (about 2.2-3.1 GW under base demand; 2.2x the historical build pace) and produced a 25-page policy report and a 22-page reproducible methods report.

## How it maps to the vacancy
| Duty | Evidence in the project |
|---|---|
| Collect, compile, update consumption data | Stage 1 harmonised panel, data dictionary, quality checks, one-command refresh |
| Analyse data on petroleum projects and programmes | Capacity-gap analysis converts demand forecasts into plant requirements (applies equally to any energy programme) |
| Forecast market trends | Backtested forecasts with intervals; honest accuracy reporting |
| Monitor supply chains and strategic stocks | Security index; thermal-reserve and import-share stress tests; monitoring dashboard proposal |

Be upfront that this is an electricity project; the transferable point is the method (compile, forecast, stress-test, monitor), which carries straight over to refined products and strategic stocks.

## Questions you should be ready for
1. **Why not statsmodels?** The workspace could not install it. Implementing ARIMA/ETS by hand forced understanding of the estimators; formulas are in the technical report.
2. **Only 26 data points: can you forecast with that?** Yes for simple models, and the backtests show 3-4% errors at 1-3 years. Intervals beyond 3 years rest on a sqrt(h) assumption, stated openly.
3. **Why did you drop the ETS model?** Backtests showed it was weakest (9% error at 3 years) because it slows growth too early. The selection was made on the same data, so reported ensemble accuracy is a little optimistic. This is disclosed.
4. **What is the weakest part?** Annual energy balance cannot see peak or seasonal shortfalls, so stress results are a lower bound on risk. No price or cost data.
5. **Why does Kenya rank first when it has outages?** The index measures structural exposure (diversification, imports, hydrology, fuel), not network reliability.
6. **What would you do next?** Monthly data for seasonal adequacy; cost data to turn the capacity gap into investment needs.
7. **First Monte Carlo gave 0% risk. What happened?** It resampled year-on-year hydro changes including growth years, understating tail risk. Redesigned on deviations from the five-year mean and conditioned on import state.

## Be able to explain without notes
MAPE and rolling-origin backtesting; why log demand; what an elasticity is and why Kenya's is not significant; HHI; winsorising; what a capacity factor is; the three assumptions that drive the stress results (thermal availability, thermal capacity, annual basis).
