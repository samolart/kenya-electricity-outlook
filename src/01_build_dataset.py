"""Stage 1: build analysis-ready Kenya and regional panels from Ember + OWID raw files.
Usage: python3 -I src/01_build_dataset.py   (run from repo root)
"""
import pandas as pd, numpy as np, json

RAW = "data/raw"; OUT = "data/processed"
PEERS = {  # Ember name -> short name used in the project
    "Kenya": "Kenya", "Uganda": "Uganda", "Tanzania (the United Republic of)": "Tanzania",
    "Ethiopia": "Ethiopia", "Rwanda": "Rwanda", "Burundi": "Burundi", "Zambia": "Zambia",
    "Mozambique": "Mozambique", "Congo (DRC)": "DR Congo", "Sudan": "Sudan",
}
OWID_NAME = {"Tanzania": "Tanzania", "DR Congo": "Democratic Republic of Congo"}

e = pd.read_csv(f"{RAW}/ember_generation_yearly.csv", low_memory=False)
e = e[(e["Area type"] == "Country or economy") & e.Area.isin(PEERS)].copy()
e["country"] = e.Area.map(PEERS)
gen = e.pivot_table(index=["country", "Year"], columns="Electricity source",
                    values="Generation (TWh)", aggfunc="first")
inten = e[e["Electricity source"] == "Total generation"].set_index(["country", "Year"])[
    "Emissions intensity (gCO2e/kWh)"]
emis = e[e["Electricity source"] == "Total generation"].set_index(["country", "Year"])["Emissions (MtCO2e)"]

main = ["Hydro", "Other renewables", "Wind", "Solar", "Bioenergy", "Coal", "Gas", "Other fossil",
        "Nuclear", "Net imports", "Total generation", "Demand", "Fossil", "Clean", "Renewables"]
panel = gen[[c for c in main if c in gen.columns]].copy().fillna({"Coal":0,"Gas":0,"Nuclear":0})
panel.columns = [c.lower().replace(" ", "_") for c in panel.columns]
panel = panel.rename(columns={"other_renewables": "geothermal_other_ren", "total_generation": "generation",
                              "net_imports": "net_imports", "demand": "demand"})
panel["emissions_mtco2e"] = emis
panel["emissions_intensity_g_kwh"] = inten
panel = panel.reset_index().rename(columns={"Year": "year"})

o = pd.read_csv(f"{RAW}/owid-energy-data.csv")
o["country"] = o.country.replace({"Democratic Republic of Congo": "DR Congo"})
oc = o[o.country.isin(PEERS.values())][["country", "year", "population", "gdp",
       "electricity_demand_per_capita", "primary_energy_consumption", "energy_per_capita"]]
panel = panel.merge(oc, on=["country", "year"], how="left")
panel["demand_per_capita_kwh"] = panel.demand * 1e9 / panel.population
panel["gdp_per_capita"] = panel.gdp / panel.population
panel = panel.sort_values(["country", "year"]).reset_index(drop=True)
panel.to_csv(f"{OUT}/regional_panel.csv", index=False)

k = panel[panel.country == "Kenya"].drop(columns="country").reset_index(drop=True)
k.to_csv(f"{OUT}/kenya_annual.csv", index=False)

# --- data quality checks ---
q = {}
q["kenya_years"] = [int(k.year.min()), int(k.year.max()), int(len(k))]
q["countries"] = sorted(panel.country.unique().tolist())
# Ember generation vs OWID generation reconciliation (Kenya)
ok = o[o.country == "Kenya"].set_index("year")
kk = k.set_index("year")
rec = pd.DataFrame({"ember_gen": kk.generation, "owid_gen": ok.electricity_generation,
                    "ember_demand": kk.demand, "owid_demand": ok.electricity_demand}).dropna()
rec["gen_diff_pct"] = (rec.ember_gen / rec.owid_gen - 1) * 100
rec["dem_diff_pct"] = (rec.ember_demand / rec.owid_demand - 1) * 100
rec.to_csv("outputs/tables/data_reconciliation_kenya.csv")
q["max_abs_gen_diff_pct"] = float(rec.gen_diff_pct.abs().max())
q["max_abs_demand_diff_pct"] = float(rec.dem_diff_pct.abs().max())
# identity check: sum of sources + imports ~ demand
src = ["hydro", "geothermal_other_ren", "wind", "solar", "bioenergy", "coal", "gas", "other_fossil"]
k2 = k.copy(); k2["sum_src"] = k2[src].sum(axis=1)
q["max_abs_sources_vs_generation_pct"] = float(((k2.sum_src / k2.generation - 1) * 100).abs().max())
q["max_abs_gen_plus_imports_vs_demand_pct"] = float((((k2.generation + k2.net_imports) / k2.demand - 1) * 100).abs().max())
q["missing_by_col_kenya"] = {c: int(v) for c, v in k.isna().sum().items() if v}
q["gdp_last_year_kenya"] = int(k.year[k.gdp.notna()].max())
json.dump(q, open("outputs/tables/data_quality.json", "w"), indent=2)
print(json.dumps(q, indent=2)); print(rec.round(2).tail(6)); print(panel.shape)
