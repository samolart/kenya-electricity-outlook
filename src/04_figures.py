"""Stage 4: publication figures (light surface, validated default categorical palette order)."""
import numpy as np, pandas as pd, json, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
C = ["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#008300","#6250d6","#e34948"]
INK, SUB, GRID, GRAY = "#0b0b0b", "#52514e", "#e6e5e1", "#a8a7a1"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"axes.edgecolor":GRID,"axes.labelcolor":SUB,"xtick.color":SUB,"ytick.color":SUB,
  "axes.spines.top":False,"axes.spines.right":False,"axes.grid":True,"grid.color":GRID,"grid.linewidth":.6,"axes.axisbelow":True,
  "figure.facecolor":"#fcfcfb","axes.facecolor":"#fcfcfb","savefig.facecolor":"#fcfcfb","axes.titlesize":10.5,"axes.titleweight":"bold","axes.titlecolor":INK})
D="outputs/figures/"; T="outputs/tables/"
k = pd.read_csv("data/processed/kenya_annual.csv").set_index("year"); P = pd.read_csv("data/processed/regional_panel.csv")
F = pd.read_csv(T+"demand_forecast_statistical_2026_2035.csv").set_index("year")
Z = pd.read_csv(T+"security_index_panel.csv"); f3 = json.load(open(T+"stage3_facts.json"))
def save(fig, n): fig.tight_layout(); fig.savefig(D+n, dpi=200); plt.close(fig)

# F1 generation mix (stacked) + demand line
fig, ax = plt.subplots(figsize=(7.2,4))
k["fossil_all"] = k.coal.fillna(0)+k.gas.fillna(0)+k.other_fossil.fillna(0)
st = [("Geothermal & other ren.","geothermal_other_ren"),("Hydro","hydro"),("Wind","wind"),("Solar","solar"),("Bioenergy","bioenergy"),("Fossil (thermal)","fossil_all"),("Net imports","net_imports")]
ax.stackplot(k.index, *[k[c].clip(lower=0) for _,c in st], colors=[C[0],C[1],C[2],C[3],C[4],"#6b6a64",C[6]], labels=[n for n,_ in st], edgecolor="#fcfcfb", linewidth=.8)
ax.plot(k.index, k.demand, color=INK, lw=1.4, ls="--", label="Electricity demand")
ax.set_ylabel("TWh per year"); ax.set_title("Kenya's electricity supply mix, 2000–2025"); ax.set_xlim(2000,2025)
ax.legend(ncol=2, frameon=False, fontsize=8, loc="upper left"); save(fig,"fig01_supply_mix.png")

# F2 forecast fan
fig, ax = plt.subplots(figsize=(7.2,4))
ax.plot(k.index, k.demand, color=C[0], lw=2, label="Observed demand")
ax.fill_between(F.index, F.lo95, F.hi95, color=C[0], alpha=.12, lw=0, label="95% interval"); ax.fill_between(F.index, F.lo80, F.hi80, color=C[0], alpha=.25, lw=0, label="80% interval")
ax.plot(F.index, F["Ensemble (mean)"], color=C[0], lw=2, ls="--", label="Ensemble forecast"); ax.axvline(2025.5, color=GRAY, lw=.8)
for yr in (2030,2035): ax.annotate(f'{F.loc[yr,"Ensemble (mean)"]:.1f} TWh', (yr,F.loc[yr,"Ensemble (mean)"]), xytext=(-8,12), textcoords="offset points", color=INK, fontsize=8.5, ha="right")
ax.set_ylabel("TWh per year"); ax.set_title("Kenya electricity demand: history and 2026–2035 forecast"); ax.legend(frameon=False, loc="upper left"); save(fig,"fig02_forecast_fan.png")

# F3 backtest accuracy
s = pd.read_csv(T+"backtest_summary.csv"); order = s[s.h==1].sort_values("MAPE").model.tolist()
fig, ax = plt.subplots(figsize=(7.2,3.8)); w=.27; x=np.arange(len(order))
for i,h in enumerate((1,2,3)):
    v=[s[(s.model==m)&(s.h==h)].MAPE.iloc[0] for m in order]; ax.barh(x+(1-i)*w, v, height=w-.03, color=C[i], label=f"{h}-year ahead")
ax.set_yticks(x); ax.set_yticklabels(order); ax.invert_yaxis(); ax.set_xlabel("Mean absolute % error (rolling-origin backtest)"); ax.set_title("Out-of-sample accuracy by model and horizon"); ax.legend(frameon=False); save(fig,"fig03_backtest.png")

# F4 per-capita demand vs GDP per capita (2022)
d = P[(P.year==2022)].dropna(subset=["gdp_per_capita","demand_per_capita_kwh"])
fig, ax = plt.subplots(figsize=(6.4,4.2))
for r in d.itertuples():
    kn = r.country=="Kenya"; ax.scatter(r.gdp_per_capita, r.demand_per_capita_kwh, s=70 if kn else 40, color=C[0] if kn else GRAY, zorder=3, edgecolor="#fcfcfb")
    ax.annotate(r.country, (r.gdp_per_capita, r.demand_per_capita_kwh), xytext=(5,4), textcoords="offset points", fontsize=8, color=INK if kn else SUB)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("GDP per capita (2011 int-$, log scale)"); ax.set_ylabel("Electricity demand per capita (kWh, log scale)")
ax.set_title("Electricity demand per capita vs income, 2022"); ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:,.0f}")); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:,.0f}")); save(fig,"fig04_percapita_vs_gdp.png")

# F5 security index 2024 + Kenya trajectory
z24 = Z[Z.year==2024].sort_values("SSI"); fig, (a,b) = plt.subplots(1,2,figsize=(8.4,3.8), gridspec_kw={"width_ratios":[1,1.1]})
a.barh(z24.country, z24.SSI, color=[C[0] if c=="Kenya" else GRAY for c in z24.country], height=.65)
for i,v in enumerate(z24.SSI): a.text(v+1, i, f"{v:.0f}", va="center", fontsize=8, color=INK)
a.set_xlim(0,100); a.set_title("Supply-security index, 2024"); a.set_xlabel("0 = least secure, 100 = most secure")
for c in Z.country.unique():
    z = Z[Z.country==c]; b.plot(z.year, z.SSI, color=C[0] if c=="Kenya" else GRAY, lw=2.4 if c=="Kenya" else 1, zorder=3 if c=="Kenya" else 1)
b.text(2025.3, Z[(Z.country=="Kenya")&(Z.year==2025)].SSI.iloc[0], "Kenya", color=C[0], fontsize=9, va="center", fontweight="bold")
b.set_title("Index trajectory 2006–2025 (grey = peers)"); b.set_ylabel("Index"); b.set_xlim(2006,2027); save(fig,"fig05_security_index.png")

# F6 Kenya pillars 2015 vs 2025
pil = f3["kenya_pillars_2015_2025"]; nm = {"imp_dep":"Import dependence","hhi":"Source concentration","fossil_share":"Fossil / fuel-price exposure","hydro_risk":"Hydrology risk exposure"}
fig, ax = plt.subplots(figsize=(6.8,3.2))
for i,(c,(a0,a1)) in enumerate(pil.items()):
    ax.plot([a0,a1],[i,i], color=GRAY, lw=2, zorder=1); ax.scatter(a0,i,color=GRAY,s=60,zorder=3,label="2015" if i==0 else None); ax.scatter(a1,i,color=C[0],s=60,zorder=3,label="2025" if i==0 else None)
    ax.text(max(a0,a1)+2, i, f"{a0:.0f} → {a1:.0f}", va="center", fontsize=8.5, color=INK)
ax.set_yticks(range(4)); ax.set_yticklabels([nm[c] for c in pil]); ax.invert_yaxis(); ax.set_xlim(40,115); ax.set_xlabel("Pillar score (100 = most secure)"); ax.set_title("Kenya: what moved in the security index, 2015 → 2025"); ax.legend(frameon=False, loc="lower left"); save(fig,"fig06_pillars.png")

# F7 import dependence + hydro/geothermal shares (Kenya)
fig, (a,b) = plt.subplots(1,2,figsize=(8.4,3.6))
a.bar(k.index[-14:], (k.net_imports/k.demand*100)[-14:], color=C[1], width=.7); a.set_title("Net imports as % of demand"); a.set_ylabel("%")
sh = lambda c: k[c]/k.generation*100
for nme,c,i in [("Geothermal & other","geothermal_other_ren",0),("Hydro","hydro",1),("Wind","wind",2)]:
    b.plot(k.index, sh(c), color=C[i], lw=2, label=nme)
b.set_title("Share of generation (%)"); b.legend(frameon=False, fontsize=8); save(fig,"fig07_imports_shares.png")

# F8 stress scenarios
st = pd.read_csv(T+"stress_scenarios_2025.csv", index_col=0).iloc[1:]
fig, ax = plt.subplots(figsize=(7.4,3.9)); y=np.arange(len(st))
ax.barh(y, st.thermal_add_twh, color=C[3], height=.62, label="Covered by extra thermal generation")
ax.barh(y, st.unserved_twh, left=st.thermal_add_twh, color=C[7], height=.62, label="Unserved energy", edgecolor="#fcfcfb", linewidth=1.5)
ax.axvline(f3["stress_inputs"]["thermal_headroom"], color=INK, lw=1, ls="--", label="Thermal headroom limit (1.85 TWh)")
for i,r in enumerate(st.itertuples()): ax.text(r.lost_twh+.05, i, f"{r.unserved_pct_demand:.1f}% unserved" if r.unserved_pct_demand>0 else "fully covered", va="center", fontsize=8, color=INK, bbox=dict(facecolor="#fcfcfb", edgecolor="none", pad=1.2), zorder=5)
ax.set_yticks(y); ax.set_yticklabels([s_.split(" (")[0] if len(s_)>40 else s_ for s_ in st.index], fontsize=8); ax.invert_yaxis(); ax.set_xlim(0,5); ax.set_xlabel("Lost supply to be replaced (TWh per year)")
ax.set_title("Stress tests on the 2025 supply stack"); ax.legend(frameon=False, loc="upper center", fontsize=8, bbox_to_anchor=(0.2,-0.2), ncol=2); save(fig,"fig08_stress.png")

# F9 Monte Carlo summary
a_, b_ = f3["mc_imports_available"], f3["mc_imports_out"]
fig, (a,b) = plt.subplots(1,2,figsize=(7.6,3.3))
a.bar(["Imports\navailable","Imports\ninterrupted"], [a_["p_unserved"]*100, b_["p_unserved"]*100], color=[C[0],C[1]], width=.55); a.set_title("Probability of an annual energy shortfall"); a.set_ylabel("%")
for i,v in enumerate([a_["p_unserved"]*100,b_["p_unserved"]*100]): a.text(i, v+.8, f"{v:.0f}%", ha="center", fontsize=9, color=INK)
b.bar(["Imports\navailable","Imports\ninterrupted"], [a_["p95_unserved_pct_demand"], b_["p95_unserved_pct_demand"]], color=[C[0],C[1]], width=.55); b.set_title("95th-percentile shortfall (% of demand)")
for i,v in enumerate([a_["p95_unserved_pct_demand"], b_["p95_unserved_pct_demand"]]): b.text(i, v+.15, f"{v:.1f}%", ha="center", fontsize=9, color=INK)
save(fig,"fig09_monte_carlo.png")

# F10 capacity gap
cp = pd.read_csv(T+"capacity_gap_scenarios.csv"); cp = cp[cp.year==2035]; fig, ax = plt.subplots(figsize=(7.2,3.8)); sc=["Low (80% lower bound)","Base (ensemble)","High (80% upper bound)"]; mx=cp.mix.unique(); w=.26
for i,m in enumerate(mx):
    v=[cp[(cp.scenario==s_)&(cp.mix==m)].new_gw_holdBAU.iloc[0] for s_ in sc]; ax.bar(np.arange(3)+(i-1)*w, v, width=w-.03, color=C[i], label=m)
    for j,vv in enumerate(v): ax.text(j+(i-1)*w, vv+.06, f"{vv:.1f}", ha="center", fontsize=8, color=INK)
ax.set_xticks(range(3)); ax.set_xticklabels(["Low demand","Base demand","High demand"]); ax.set_ylabel("New capacity needed by 2035 (GW)"); ax.set_title("New generation capacity needed by 2035 under three build mixes"); ax.legend(frameon=False, fontsize=8, title="Energy mix (geo/wind/solar)", title_fontsize=8); save(fig,"fig10_capacity_gap.png")

# F11 rank distribution under random weights
rd = f3["kenya_rank_dist_2024"]; fig, ax = plt.subplots(figsize=(5.6,3.2)); ax.bar([int(r) for r in rd], [v*100 for v in rd.values()], color=C[0], width=.65)
ax.set_xlabel("Kenya's rank among 10 countries (1 = most secure)"); ax.set_ylabel("% of 10,000 random weightings"); ax.set_title("Is Kenya's rank an artefact of the weights?"); ax.set_xticks(range(1,10)); save(fig,"fig11_rank_sensitivity.png")
print("figures done")
