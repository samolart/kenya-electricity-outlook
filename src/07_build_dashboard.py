"""Stage 6: package project outputs into a single self-contained HTML dashboard.
Reads src/dashboard_template.html, injects data as JSON, writes index.html at the repo root (GitHub Pages entry point).
Usage: python3 -I src/07_build_dashboard.py   (repo root)"""
import json, numpy as np, pandas as pd
T = "outputs/tables/"
k = pd.read_csv("data/processed/kenya_annual.csv").set_index("year")
P = pd.read_csv("data/processed/regional_panel.csv")
F = pd.read_csv(T+"demand_forecast_statistical_2026_2035.csv").set_index("year")
bs = pd.read_csv(T+"backtest_summary.csv"); Z = pd.read_csv(T+"security_index_panel.csv")
bm = pd.read_csv(T+"regional_benchmark_2024.csv"); f3 = json.load(open(T+"stage3_facts.json")); ff = json.load(open(T+"forecast_facts.json"))
r = lambda a, n=3: [None if pd.isna(x) else round(float(x), n) for x in a]
fossil = (k.coal.fillna(0)+k.gas.fillna(0)+k.other_fossil.fillna(0))
D = {"years": [int(y) for y in k.index],
 "kenya": {"demand": r(k.demand), "generation": r(k.generation), "geo": r(k.geothermal_other_ren), "hydro": r(k.hydro), "wind": r(k.wind), "solar": r(k.solar),
           "bio": r(k.bioenergy), "fossil": r(fossil), "imports": r(k.net_imports), "intensity": r(k.emissions_intensity_g_kwh, 1), "perCapita": r(k.demand_per_capita_kwh, 1)},
 "forecast": {"years": [int(y) for y in F.index], "ens": r(F["Ensemble (mean)"]), "lo80": r(F.lo80), "hi80": r(F.hi80), "lo95": r(F.lo95), "hi95": r(F.hi95),
              "models": {"Random walk + drift": r(F["Drift (RW+drift)"]), "Log-linear trend": r(F["Log-linear trend"]), "ARIMA(1,1,0) + drift": r(F["ARIMA(1,1,0)+drift"]), "ETS damped trend": r(F["ETS damped trend"]), "Recent drift (8y)": r(F["Recent drift (8y)"])}},
 "backtest": [{"model": m, "h": [round(float(bs[(bs.model == m) & (bs.h == h)].MAPE.iloc[0]), 2) for h in (1, 2, 3)]} for m in bs.model.unique()],
 "cagr": ff["cagr_2000_2025"], "cagr1525": ff["cagr_2015_2025"], "cagr2025": ff["cagr_2020_2025"], "coverage": ff["interval_coverage"],
 "benchmark": [{"country": a.country, "demand": round(a.demand, 1), "perCapita": round(a.demand_per_capita_kwh, 0), "hydro": round(a.hydro_share, 0), "fossil": round(a.fossil_share, 0),
                "imports": round(a.imp_dep, 1), "intensity": round(a.emissions_intensity_g_kwh, 0), "cagr": round(a.cagr_2014_2024, 1)} for a in bm.itertuples()],
 "scatter": [{"country": a.country, "gdp": round(a.gdp_per_capita, 0), "dem": round(a.demand_per_capita_kwh, 0)} for a in P[P.year == 2022].dropna(subset=["gdp_per_capita", "demand_per_capita_kwh"]).itertuples()]}
yrs = list(range(2006, 2026)); sec = {}
for c in sorted(Z.country.unique()):
    z = Z[Z.country == c].set_index("year")
    sc = ["s_imp_dep", "s_hhi", "s_fossil_share", "s_hydro_risk"]; rw = ["imp_dep", "hhi", "fossil_share", "hydro_risk"]
    sec[c] = {"s": [[round(float(z.loc[y, q]), 2) for q in sc] if y in z.index else None for y in yrs], "raw": [[round(float(z.loc[y, q]), 3) for q in rw] if y in z.index else None for y in yrs]}
D["security"] = {"years": yrs, "data": sec, "rankDist": f3["kenya_rank_dist_2024"], "pillarNames": ["Import dependence", "Source concentration", "Fuel-price exposure", "Hydrology risk"]}
K = P[P.country == "Kenya"].set_index("year")
dev = pd.DataFrame({"h": K.hydro/K.hydro.rolling(5, center=True, min_periods=3).mean()-1, "g": K.geothermal_other_ren/K.geothermal_other_ren.rolling(5, center=True, min_periods=3).mean()-1}).dropna()
si = f3["stress_inputs"]
D["stress"] = {"demand": float(k.demand[2025]), "hydro": float(k.hydro[2025]), "wind": float(k.wind[2025]), "geo": float(k.geothermal_other_ren[2025]), "imports": float(k.net_imports[2025]),
               "thermal": si["thermal_2025"], "thermalGW": si["thermal_capacity_gw"], "thermalCF": si["thermal_cf_assumed"], "co2PerTWh": 0.658,
               "devH": [round(float(v), 4) for v in dev.h], "devG": [round(float(v), 4) for v in dev.g], "devYears": [int(y) for y in dev.index]}
D["capacity"] = {"base": float(k.demand[2025]), "imports": float(k.net_imports[2025]), "thermal": si["thermal_2025"], "paths": {"Low": r(F.lo80), "Base": r(F["Ensemble (mean)"]), "High": r(F.hi80)}, "years": [int(y) for y in F.index],
                 "histPace1525": f3["hist_gen_addition_twh_per_yr_2015_2025"], "histPace2025": f3["hist_gen_addition_twh_per_yr_2020_2025"], "genAdds": r(k.generation.diff().loc[2016:2025])}
D["facts"] = {"ssi2024": f3["ssi_2024"], "rank2024": f3["rank_2024"], "rankMedian": f3["kenya_rank_median"], "ssiKenya2025": f3["kenya_ssi_2025"], "mape": [round(float(bs[(bs.model == "Ensemble (mean)") & (bs.h == h)].MAPE.iloc[0]), 1) for h in (1, 2, 3)]}
tpl = open("src/dashboard_template.html", encoding="utf-8").read()
frag = tpl.replace("/*__DATA__*/null", json.dumps(D, separators=(",", ":")))
FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230d1113'/%3E%3Cpath d='M18 5 9 18h6l-1 9 9-13h-6z' fill='%23ff7a3d'/%3E%3C/svg%3E"
doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       '<meta name="description" content="Interactive dashboard for Kenya\'s electricity outlook: demand forecast to 2035, supply-security index, drought and import stress test, and capacity-gap calculator.">\n'
       '<meta name="theme-color" content="#0d1113">\n<link rel="icon" href="' + FAVICON + '">\n'
       '<style>:root{color-scheme:dark}html,body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n</head>\n<body>\n' + frag + "\n</body>\n</html>\n")
# index.html at the repository root so GitHub Pages serves it at https://<user>.github.io/<repo>/
open("index.html", "w", encoding="utf-8").write(doc)
open(".nojekyll", "w").write("")
print("index.html", round(len(doc)/1024), "KB")
