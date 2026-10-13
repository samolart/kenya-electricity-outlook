"""Stage 3: electricity supply-security index (10-country panel), Kenya stress tests, 2035 capacity-gap scenarios.
Usage: python3 -I src/03_security_stress_scenarios.py
"""
import numpy as np, pandas as pd, json
rng = np.random.default_rng(20261012)
P = pd.read_csv("data/processed/regional_panel.csv").sort_values(["country","year"]).reset_index(drop=True)
F = pd.read_csv("outputs/tables/demand_forecast_statistical_2026_2035.csv").set_index("year")
out = {}

# ============ 1. SUPPLY-SECURITY INDEX ============
src = ["hydro","geothermal_other_ren","wind","solar","bioenergy","coal","gas","other_fossil","nuclear"]
for c in src: P[c] = P[c].fillna(0)
tot = P[src].sum(axis=1)
sh = P[src].div(tot, axis=0)
P["hhi"] = (sh**2).sum(axis=1)                                   # 1/9 (even) .. 1 (single source)
P["imp_dep"] = (P.net_imports/P.demand*100).clip(lower=0)         # % of demand met by net imports (exporters -> 0)
P["fossil_share"] = P.fossil/P.generation*100
P["hydro_share"] = P.hydro/P.generation*100
hy = P.groupby("country").hydro.transform(lambda s: s.pct_change())
P["hydro_vol"] = hy.groupby(P.country).transform(lambda s: s.rolling(8, min_periods=5).std())
P["hydro_risk"] = P.hydro_share*P.hydro_vol                       # % of generation at 1-sigma hydrology swing
comp = {"imp_dep":"Import dependence","hhi":"Source concentration (HHI)","fossil_share":"Fossil / fuel-price exposure","hydro_risk":"Hydrology risk exposure"}
Z = P[P.year>=2006].dropna(subset=list(comp)).copy()
for c in comp:                                                    # winsorise 5/95 pooled, min-max -> 0..100 (100 = most secure)
    lo, hi = Z[c].quantile([.05,.95]); v = Z[c].clip(lo, hi)
    Z["s_"+c] = 100*(1-(v-lo)/(hi-lo))
S = ["s_"+c for c in comp]
Z["SSI"] = Z[S].mean(axis=1)
Z["SSI_geo"] = np.exp(np.log(Z[S].clip(lower=1)).mean(axis=1))    # geometric aggregation (penalises weak pillars)
Z.to_csv("outputs/tables/security_index_panel.csv", index=False)
last = Z[Z.year==2024].set_index("country")
rank24 = last.SSI.rank(ascending=False).astype(int).sort_values()
print(last[["SSI","SSI_geo"]+S].round(1).sort_values("SSI",ascending=False))
# weight sensitivity: 10,000 Dirichlet weight vectors -> Kenya rank distribution in 2024
W = rng.dirichlet(np.ones(4), 10000); M = last[S].values
sc = M@W.T; ranks = (-sc).argsort(axis=0).argsort(axis=0)+1
kidx = list(last.index).index("Kenya"); kr = ranks[kidx]
out["ssi_2024"] = last.SSI.round(2).to_dict(); out["rank_2024"] = {k:int(v) for k,v in rank24.items()}
out["kenya_rank_dist_2024"] = {str(r): float((kr==r).mean()) for r in range(1,11) if (kr==r).any()}
out["kenya_rank_median"] = float(np.median(kr)); out["kenya_rank_p5_p95"] = [int(np.percentile(kr,5)), int(np.percentile(kr,95))]
# Kenya trajectory + pillar change 2015 -> 2025
kz = Z[Z.country=="Kenya"].set_index("year")
out["kenya_ssi_series"] = kz.SSI.round(2).to_dict()
out["kenya_pillars_2015_2025"] = {c: [round(float(kz.loc[2015,"s_"+c]),1), round(float(kz.loc[2025,"s_"+c]),1)] for c in comp}
out["kenya_raw_2015_2025"] = {c: [round(float(kz.loc[2015,c]),3), round(float(kz.loc[2025,c]),3)] for c in comp}
out["kenya_ssi_2025"] = float(kz.loc[2025,"SSI"]); out["kenya_ssi_2015"] = float(kz.loc[2015,"SSI"])
# rank stability across 2010-2024 (equal weights)
rk = Z[Z.year.between(2010,2024)].assign(r=lambda d: d.groupby("year").SSI.rank(ascending=False)).query("country=='Kenya'").set_index("year").r
out["kenya_rank_by_year"] = {int(k):int(v) for k,v in rk.items()}

# ============ 2. KENYA STRESS TESTS ============
K = P[P.country=="Kenya"].set_index("year")
b = K.loc[2025]; dem = b.demand
THERM_GW, CF_THERM = 0.57, 0.65                                    # Ember fossil capacity (GW); assumed max thermal availability
therm_ceiling = THERM_GW*8.76*CF_THERM
therm_now = b.coal+b.gas+b.other_fossil
headroom_th = therm_ceiling - therm_now
IMP_MAX = K.net_imports.max()                                      # historical max annual net imports (2025)
out["stress_inputs"] = dict(demand_2025=float(dem), thermal_2025=float(therm_now), thermal_ceiling=float(therm_ceiling),
                            thermal_headroom=float(headroom_th), imports_2025=float(b.net_imports), thermal_cf_assumed=CF_THERM,
                            thermal_capacity_gw=THERM_GW)
hyd_yoy = K.hydro.pct_change().dropna(); out["hydro_yoy_min"] = float(hyd_yoy.min()); out["hydro_yoy_max"] = float(hyd_yoy.max())
out["hydro_yoy_sd"] = float(hyd_yoy.std()); out["hydro_cv_detrended"] = float((K.hydro/K.hydro.rolling(5,center=True,min_periods=3).mean()).std())
def scenario(hydro_shock=0, imports_mult=1.0, wind_shock=0, geo_shock=0, th_cf=CF_THERM):
    ceil = THERM_GW*8.76*th_cf
    lost = -b.hydro*hydro_shock - b.wind*wind_shock - b.geothermal_other_ren*geo_shock + b.net_imports*(1-imports_mult)
    head = max(0, ceil-therm_now); thermal_add = min(max(lost,0), head); unserved = max(0, lost-head)
    return dict(lost_twh=float(lost), thermal_add_twh=float(thermal_add), unserved_twh=float(unserved),
                unserved_pct_demand=float(unserved/dem*100), extra_co2_mt=float(thermal_add*0.658))  # 0.658 MtCO2/TWh = 658 g/kWh (Ember 'Other fossil')
sc_def = {"S0 Baseline 2025": dict(),
          "S1 Moderate drought (hydro -25%)": dict(hydro_shock=-.25),
          "S2 2000-type drought (hydro -42%)": dict(hydro_shock=-.42),
          "S3 Import interruption (Ethiopia link out)": dict(imports_mult=0.0),
          "S4 Drought -25% + imports -50%": dict(hydro_shock=-.25, imports_mult=.5),
          "S5 2000-type drought + imports out": dict(hydro_shock=-.42, imports_mult=0.0),
          "S6 Compound: S5 + wind -20% + geothermal -10%": dict(hydro_shock=-.42, imports_mult=0.0, wind_shock=-.2, geo_shock=-.1)}
st = pd.DataFrame({k: scenario(**v) for k,v in sc_def.items()}).T; st.to_csv("outputs/tables/stress_scenarios_2025.csv"); print(st.round(2))
# thermal CF sensitivity for S5
sens = {cf: scenario(hydro_shock=-.42, imports_mult=0.0, th_cf=cf)["unserved_pct_demand"] for cf in (0.5,0.65,0.8)}
out["stress_s5_thermal_cf_sensitivity"] = {str(k):float(v) for k,v in sens.items()}
# Monte-Carlo: resample HISTORICAL deviations of hydro and geothermal/other-renewable output from their centred 5-yr mean
# (joint, same year => preserves co-movement) and apply them to the 2025 supply stack. Two states for imports.
dev = pd.DataFrame({"h": K.hydro/K.hydro.rolling(5,center=True,min_periods=3).mean()-1,
                    "g": K.geothermal_other_ren/K.geothermal_other_ren.rolling(5,center=True,min_periods=3).mean()-1}).dropna()
out["hydro_dev_worst"] = {int(y):float(v) for y,v in dev.h.nsmallest(3).items()}
N = 20000; dr = dev.iloc[rng.integers(0, len(dev), N)].values
res_lost = np.clip(-(b.hydro*dr[:,0] + b.geothermal_other_ren*dr[:,1]), 0, None)
def mc(extra_lost):
    lost = res_lost + extra_lost; un = np.clip(lost-max(0, headroom_th), 0, None)
    return dict(p_any_loss=float((lost>0).mean()), p_unserved=float((un>0).mean()), mean_unserved_twh=float(un.mean()),
                p95_unserved_pct_demand=float(np.percentile(un,95)/dem*100), p99_unserved_pct_demand=float(np.percentile(un,99)/dem*100),
                p95_thermal_twh=float(np.percentile(np.minimum(lost, max(0,headroom_th)),95)))
out["mc_imports_available"] = mc(0.0); out["mc_imports_out"] = mc(float(b.net_imports)); out["mc_n"] = N
# ============ 3. CAPACITY-GAP SCENARIOS TO 2035 ============
CF = {"Geothermal":0.85, "Wind":0.45, "Solar":0.25}; MIXES = {"Geothermal-led (50/30/20)":{"Geothermal":.5,"Wind":.3,"Solar":.2},
                                                           "Balanced (34/33/33)":{"Geothermal":.34,"Wind":.33,"Solar":.33},
                                                           "Solar-heavy (20/30/50)":{"Geothermal":.2,"Wind":.3,"Solar":.5}}
def blended_gw(twh, mix_energy): # mix given as shares of ENERGY; capacity = sum(twh*share/(8.76*CF))
    return sum(twh*s/(8.76*CF[t]) for t,s in mix_energy.items())
scn = {"Low (80% lower bound)":"lo80", "Base (ensemble)":"Ensemble (mean)", "High (80% upper bound)":"hi80"}
rows = []; base_supply = float(dem)   # 2025 supply incl. imports (1.52) and thermal (1.40) held constant
for sname, col in scn.items():
    for yr in (2030, 2035):
        d = float(F.loc[yr, col]); gap = d-base_supply
        # variant B: also phase imports down to 5% of demand and thermal down to 5% of demand -> extra requirement
        extra_B = max(0, b.net_imports-0.05*d) + max(0, therm_now-0.05*d)
        for mname, mix in MIXES.items():
            rows.append(dict(scenario=sname, year=yr, demand_twh=d, gap_twh=gap, gap_pct_2025=gap/dem*100,
                             req_new_gen_twh_per_yr=gap/(yr-2025), mix=mname,
                             new_gw_holdBAU=blended_gw(gap, mix), new_gw_phasedown=blended_gw(gap+extra_B, mix)))
cap = pd.DataFrame(rows); cap.to_csv("outputs/tables/capacity_gap_scenarios.csv", index=False)
hist_add = (K.generation[2025]-K.generation[2015])/10
out["hist_gen_addition_twh_per_yr_2015_2025"] = float(hist_add)
out["hist_gen_addition_twh_per_yr_2020_2025"] = float((K.generation[2025]-K.generation[2020])/5)
out["req_pace_base_2035"] = float((F.loc[2035,"Ensemble (mean)"]-dem)/10)
out["pace_multiple_base_2035"] = out["req_pace_base_2035"]/hist_add
print(cap[cap.mix.str.startswith("Balanced")].round(2).to_string())
# regional benchmarking table (2024)
bm = P[P.year==2024].set_index("country")[["demand","population","demand_per_capita_kwh","hydro_share","fossil_share","imp_dep","emissions_intensity_g_kwh","hhi"]]
g20 = P.pivot(index="year", columns="country", values="demand"); bm["cagr_2014_2024"] = ((g20.loc[2024]/g20.loc[2014])**(1/10)-1)*100
bm.round(2).to_csv("outputs/tables/regional_benchmark_2024.csv"); print(bm.round(2))
json.dump(out, open("outputs/tables/stage3_facts.json","w"), indent=2, default=float); print(json.dumps({k:out[k] for k in out if k not in ('kenya_ssi_series',)}, indent=1, default=float))
