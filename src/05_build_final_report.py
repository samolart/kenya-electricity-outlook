"""Stage 5a: build the Final Report (DOCX). Run: python3 -I src/05_build_final_report.py   (repo root)"""
import json, pandas as pd, numpy as np
exec(open("src/docx_helpers.py").read())
T, FG = "outputs/tables/", "outputs/figures/"
k = pd.read_csv("data/processed/kenya_annual.csv").set_index("year"); P = pd.read_csv("data/processed/regional_panel.csv")
F = pd.read_csv(T+"demand_forecast_statistical_2026_2035.csv").set_index("year"); ff = json.load(open(T+"forecast_facts.json")); f3 = json.load(open(T+"stage3_facts.json"))
el = json.load(open(T+"elasticities.json")); bs = pd.read_csv(T+"backtest_summary.csv"); cap = pd.read_csv(T+"capacity_gap_scenarios.csv"); stt = pd.read_csv(T+"stress_scenarios_2025.csv", index_col=0)
bm = pd.read_csv(T+"regional_benchmark_2024.csv"); dq = json.load(open(T+"data_quality.json")); Z = pd.read_csv(T+"security_index_panel.csv")
E = "Ensemble (mean)"; si = f3["stress_inputs"]
d00, d25 = k.demand[2000], k.demand[2025]; pc00, pc25 = k.demand_per_capita_kwh[2000], k.demand_per_capita_kwh[2025]
sh = lambda c, y=2025: k[c][y]/k.generation[y]*100
imp15, imp25 = k.net_imports[2015]/k.demand[2015]*100, k.net_imports[2025]/k.demand[2025]*100
f30, f35 = F.loc[2030, E], F.loc[2035, E]; ci = lambda y, a, b: f"{F.loc[y,a]:.1f}–{F.loc[y,b]:.1f}"
m1 = lambda m, h: bs[(bs.model == m) & (bs.h == h)].MAPE.iloc[0]
mc_a, mc_o = f3["mc_imports_available"], f3["mc_imports_out"]
capv = lambda s, y, mix, col="new_gw_holdBAU": cap[(cap.scenario.str.startswith(s)) & (cap.year == y) & (cap.mix.str.startswith(mix))][col].iloc[0]
gapv = lambda s, y: cap[(cap.scenario.str.startswith(s)) & (cap.year == y)].gap_twh.iloc[0]
rk = f3["rank_2024"]; ssi24 = f3["ssi_2024"]
TITLE = "Kenya Electricity Demand Outlook and Supply-Security Assessment"

d = new_doc(f"{TITLE} | Portfolio analytical report")
# ---------------- cover ----------------
for _ in range(5): d.add_paragraph()
para(d, "ANALYTICAL REPORT", size=11, color=GREY, after=4)
p = para(d, TITLE, size=28, color=BLUE, after=6); p.runs[0].bold = True
para(d, "Forecasting demand, measuring supply security, stress-testing the grid and sizing the capacity gap, 2000–2035", size=14, color=INK, after=24)
para(d, "A data-driven policy analysis built on open electricity data for Kenya and nine regional peers", size=11, italic=True, color=GREY, after=60)
para(d, "Author: Samatar Ahmed", size=11, after=2); para(d, "Date: October 2026", size=11, after=2)
para(d, "Data: Ember yearly electricity data (generation, demand, emissions) and Our World in Data energy dataset (population, GDP)", size=10, color=GREY, after=2)
para(d, "Code and reproducible pipeline: see the accompanying GitHub repository and the Technical Methods Report.", size=10, color=GREY)

# ---------------- executive summary ----------------
h1(d, "Executive summary")
para(d, "Kenya's electricity system has been growing faster than almost any other part of its economy, and it is changing in character. This report uses open data to answer four questions that a national energy-planning team has to answer repeatedly: how fast will electricity demand grow, how secure is supply today, what happens if the grid is hit by drought or by loss of imported power, and how much new capacity is needed to keep pace.")
callout(d, "Headline findings", "")
bullets(d, [
  ("Demand has more than tripled and will keep climbing.", f"Annual electricity demand rose from {d00:.1f} TWh in 2000 to {d25:.1f} TWh in 2025, an average of {ff['cagr_2000_2025']*100:.1f}% a year. Our backtested ensemble forecast puts demand at {f30:.1f} TWh in 2030 (80% interval {ci(2030,'lo80','hi80')}) and {f35:.1f} TWh in 2035 (80% interval {ci(2035,'lo80','hi80')})."),
  ("Forecast accuracy is good but honest limits apply.", f"In rolling-origin backtests the ensemble missed next-year demand by {m1(E,1):.1f}% on average and three-year-ahead demand by {m1(E,3):.1f}%. Only 26 annual observations exist, so the intervals widen quickly and the model cannot see structural breaks."),
  ("Kenya is the most diversified power system in its region, which makes it structurally the most secure.", f"On a four-pillar supply-security index Kenya ranks first among ten countries in 2024 (score {ssi24['Kenya']:.0f}/100, next best Uganda {ssi24['Uganda']:.0f}). The result holds as the median under 10,000 random weightings, but Kenya is first in only {f3['kenya_rank_dist_2024']['1']*100:.0f}% of them, so the ranking is a strength, not a certainty."),
  ("The new weak spot is imported power.", f"Net imports supplied {imp15:.1f}% of demand in 2015 and {imp25:.1f}% in 2025, the one security pillar that deteriorated markedly (score {f3['kenya_pillars_2015_2025']['imp_dep'][0]:.0f} to {f3['kenya_pillars_2015_2025']['imp_dep'][1]:.0f})."),
  ("The grid survives drought or an import outage, but not both together.", f"On an annual-energy basis, existing thermal plant can replace a drought as severe as the 2000 event or the loss of all imports, one at a time. Combine the two and about {stt.iloc[5].unserved_pct_demand:.1f}% of demand goes unserved. In a Monte Carlo built on 25 years of hydrology, the chance of a shortfall is {mc_a['p_unserved']*100:.0f}% with imports available and {mc_o['p_unserved']*100:.0f}% if the import link is down."),
  ("Meeting base-case demand needs about twice the historical build pace.", f"Closing the gap to {f35:.1f} TWh by 2035 requires adding roughly {f3['req_pace_base_2035']:.2f} TWh of new supply per year, {f3['pace_multiple_base_2035']:.1f} times the {f3['hist_gen_addition_twh_per_yr_2015_2025']:.2f} TWh per year added in 2015–2025. That is about {capv('Base',2035,'Geothermal'):.1f}–{capv('Base',2035,'Solar'):.1f} GW of new capacity depending on the technology mix."),
])
para(d, "What this means for planners.", bold_lead=None).runs[0].bold = True
bullets(d, ["Treat the import share and the thermal reserve as the two numbers to watch monthly. Both are cheap to track and both drive the stress results.",
            "Keep geothermal at the centre of the build programme: it is the technology that adds the most secure energy per gigawatt and it keeps the mix diversified.",
            "Invest in higher-frequency data (monthly generation, peak demand, reservoir levels). Annual data answers the strategic questions in this report but cannot answer the operational ones."])
para(d, "How to read this report. Chapters 2–3 describe the data and Kenya's system. Chapters 4–7 contain the four analyses. Chapter 8 draws recommendations, Chapter 9 sets out limitations, and the appendices give definitions, a data dictionary and full tables. The companion Technical Methods Report documents every step and every line of code.", size=10, italic=True, color=GREY)

# ---------------- contents ----------------
h1(d, "Contents")
for t in ["1  Introduction and policy context", "2  Data and quality assurance", "3  Kenya's electricity system, 2000–2025", "4  Demand forecasting", "5  Supply-security index",
          "6  Stress tests: drought and import interruption", "7  Capacity-gap analysis to 2035", "8  Recommendations for energy planners", "9  Limitations and threats to validity",
          "10 Conclusion", "Appendix A  Glossary", "Appendix B  Data dictionary", "Appendix C  Supporting tables", "Appendix D  Sources"]:
    para(d, t, after=3)

# ---------------- 1 introduction ----------------
h1(d, "1  Introduction and policy context")
h2(d, "1.1  Why electricity, and why now")
para(d, "Electricity is the part of the energy system where Kenya's recent story is most visible. The supply mix is dominated by geothermal, hydro and wind, the grid is increasingly interconnected with neighbours, and demand is growing steadily as incomes rise and more households and firms connect. For a planning ministry, three recurring questions follow: what will demand be, can supply meet it reliably, and what must be built.")
para(d, "These are the questions behind the day-to-day work of an energy economic analyst: compiling and updating consumption data, analysing programmes and projects, forecasting market trends, and monitoring supply chains and strategic reserves. This project applies exactly that toolkit to electricity, using only open data, so that every number can be reproduced by anyone.")
h2(d, "1.2  What this report does")
table(d, pd.DataFrame([
  ["Collect, compile and update consumption data", "Chapter 2: harmonised Kenya and 10-country panel built from two open datasets, with reconciliation checks"],
  ["Analyse data on programmes and projects", "Chapter 7: capacity-gap analysis converting forecast demand into GW of new plant under alternative technology mixes"],
  ["Forecast market trends", "Chapter 4: five forecasting methods, rolling-origin backtests, calibrated prediction intervals to 2035"],
  ["Monitor supply chains and strategic stocks", "Chapters 5–6: supply-security index and stress tests of thermal reserves and import dependence"]],
  columns=["Analyst duty", "Where this project demonstrates it"]), caption="Table 1. Mapping of the analysis to the core duties of an energy economic analyst", widths=[6.2, 10.0], align_right_from=9)
h2(d, "1.3  Scope and an important boundary")
para(d, "The analysis is about electricity, not fuels. It uses annual data from 2000 to 2025 for Kenya and annual data to 2024 for nine regional comparators (Uganda, Tanzania, Ethiopia, Rwanda, Burundi, Zambia, Mozambique, DR Congo and Sudan). Everything is measured in energy terms (terawatt-hours, TWh). The report does not model prices, tariffs, transmission constraints or hourly operations, because the open data used here cannot support them. Chapter 9 explains what that means for how results should be used.")

# ---------------- 2 data ----------------
h1(d, "2  Data and quality assurance")
h2(d, "2.1  Sources")
bullets(d, [("Ember yearly electricity data (global, long format).", f"Generation by source (TWh), electricity demand, net imports, emissions and installed capacity by country and year. The extract contains {104273:,} rows for 1985–2025; Kenya is covered 2000–2025."),
            ("Our World in Data (OWID) energy dataset.", "Population, GDP (2011 international dollars), primary energy and derived per-capita measures. OWID's electricity series is itself derived from Ember, so the two files are consistent by construction and the reconciliation below is a check on processing, not an independent validation.")])
h2(d, "2.2  Panel construction")
para(d, "The pipeline filters Ember to country-level records, reshapes generation by source into one row per country and year, merges population and GDP from OWID, and derives per-capita demand and GDP per capita. Geothermal is reported by Ember under 'Other renewables'; for Kenya this is overwhelmingly geothermal, and it is labelled 'Geothermal & other renewables' throughout. Fossil generation is the sum of coal, gas and other fossil.")
h2(d, "2.3  Quality checks")
table(d, pd.DataFrame([
  ["Generation by source sums to total generation", f"max gap {dq['max_abs_sources_vs_generation_pct']:.3f}%", "Pass"],
  ["Generation + net imports equals demand", f"max gap {dq['max_abs_gen_plus_imports_vs_demand_pct']:.3f}%", "Pass"],
  ["Ember vs OWID generation (Kenya, 26 years)", f"max gap {dq['max_abs_gen_diff_pct']:.2f}%", "Pass (not independent)"],
  ["Ember vs OWID demand (Kenya, 26 years)", f"max gap {dq['max_abs_demand_diff_pct']:.2f}%", "Pass (not independent)"],
  ["Kenya capacity for geothermal", "Reported as zero in Ember", "Not used (see 2.4)"]],
  columns=["Check", "Result", "Status"]), caption="Table 2. Data quality checks", widths=[7.4, 6.2, 3.0], align_right_from=9)
h2(d, "2.4  Known data limitations that shape the analysis")
bullets(d, [("Short series.", "Kenya has 26 annual observations. That is enough to estimate trends and test forecasts out of sample, but too few for rich models. The report therefore favours simple, transparent methods and reports uncertainty explicitly."),
            ("No geothermal capacity.", "Ember reports zero installed capacity for Kenya's 'Other renewables', although the category generated 6.4 TWh in 2025. Capacity-based adequacy metrics (such as reserve margins) would be misleading, so the report works in energy terms and uses capacity only for thermal plant, where it is reported."),
            ("GDP ends in 2022; 2025 may be provisional.", "GDP is used for elasticity estimation and a conditional cross-check only. Latest-year values can be revised, so results should be refreshed with each Ember release; the pipeline reruns in one command.")])

# ---------------- 3 system ----------------
h1(d, "3  Kenya's electricity system, 2000–2025")
h2(d, "3.1  Growth")
para(d, f"Annual electricity demand grew from {d00:.1f} TWh in 2000 to {k.demand[2015]:.1f} TWh in 2015 and {d25:.1f} TWh in 2025: an average of {ff['cagr_2000_2025']*100:.1f}% a year over the whole period, {ff['cagr_2015_2025']*100:.1f}% over the last decade and {ff['cagr_2020_2025']*100:.1f}% over the last five years. Per-capita demand rose from {pc00:.0f} kWh to {pc25:.0f} kWh, so growth is mainly a story of more people and more use per person together. Demand fell in four years: sharply in 2007 and 2008 (−11% and −8%) and marginally in 2013 and 2016 (about −1% each).")
figure(d, FG+"fig01_supply_mix.png", "Kenya's electricity supply mix by source, with demand shown as the dashed line. Net imports appear at the top from 2022.")
h2(d, "3.2  The mix")
para(d, f"In 2025 geothermal and other renewables supplied {sh('geothermal_other_ren'):.0f}% of Kenya's generation, hydro {sh('hydro'):.0f}%, wind {sh('wind'):.0f}%, solar {sh('solar'):.0f}%, bioenergy {sh('bioenergy'):.0f}% and fossil plant {sh('other_fossil'):.0f}%. The grid emits about {k.emissions_intensity_g_kwh[2025]:.0f} grams of CO2 per kWh generated, among the lowest in the world, and broadly unchanged from a decade earlier ({k.emissions_intensity_g_kwh[2015]:.0f} g/kWh in 2015): the intensity moves year to year with hydrology and with how much thermal plant is called.")
para(d, f"Two changes stand out. First, wind went from a negligible 0.06 TWh in 2015 to {k.wind[2025]:.1f} TWh in 2025, and solar from 0.05 to {k.solar[2025]:.1f} TWh. Second, hydro's share fell from {sh('hydro',2015):.0f}% in 2015 to {sh('hydro'):.0f}% in 2025: hydro output has been flat-to-down while demand grew, so new supply came from other sources.")
figure(d, FG+"fig07_imports_shares.png", "Left: net imports as a share of demand, last 14 years. Right: share of generation from geothermal and other renewables, hydro and wind.")
h2(d, "3.3  The rise of imported power")
para(d, f"Net imports were negligible ({k.net_imports[2015]:.2f} TWh, {imp15:.1f}% of demand) in 2015, stayed at or below 0.3 TWh through 2022, then reached {k.net_imports[2023]:.2f} TWh in 2023, {k.net_imports[2024]:.2f} TWh in 2024 and {k.net_imports[2025]:.2f} TWh ({imp25:.1f}% of demand) in 2025. The data do not identify the supplying country; the timing is consistent with the commissioning of the high-capacity interconnector with Ethiopia, but that attribution is an inference and not something the dataset shows. What matters for security analysis is that roughly one unit in ten now crosses a border.")
h2(d, "3.4  Regional benchmarking")
para(d, f"Kenya's per-capita demand of {bm[bm.country=='Kenya'].demand_per_capita_kwh.iloc[0]:.0f} kWh in 2024 sits in the middle of the East African pack. It is well above Tanzania, Uganda, Rwanda, Ethiopia, Burundi and DR Congo, and below Sudan, Mozambique and Zambia, the last two of which combine large hydro supply with heavy industrial demand. Kenya's ten-year demand growth of {bm[bm.country=='Kenya'].cagr_2014_2024.iloc[0]:.1f}% a year is slower than Ethiopia (10.4%), Rwanda (9.3%) and Burundi (7.8%), which are growing from much smaller bases.")
b2 = bm.copy(); b2 = b2.sort_values("demand_per_capita_kwh", ascending=False)
tb = pd.DataFrame({"Country": b2.country, "Demand (TWh)": b2.demand.round(1), "Per capita (kWh)": b2.demand_per_capita_kwh.round(0).astype(int), "Hydro share (%)": b2.hydro_share.round(0).astype(int),
                   "Fossil share (%)": b2.fossil_share.round(0).astype(int), "Net imports (% demand)": b2.imp_dep.round(1), "g CO2/kWh": b2.emissions_intensity_g_kwh.round(0).astype(int), "Demand CAGR 2014–24 (%)": b2.cagr_2014_2024.round(1)})
table(d, tb, caption="Table 3. Regional benchmark, 2024", fs=8.5, widths=[2.4, 1.9, 2.1, 1.9, 1.9, 2.3, 1.7, 2.3])
figure(d, FG+"fig04_percapita_vs_gdp.png", "Electricity demand per capita against GDP per capita in 2022 (log scales). Kenya, in blue, lies close to the regional income-demand relationship.", width=12.5)
para(d, f"Across the panel, a one per cent difference in income per head is associated with about {el['fe_loglog_levels']['elasticity']:.2f}% more electricity per head within a country over time (country fixed-effects estimate, {el['fe_loglog_levels']['n']} observations). This long-run relation is close to one-for-one, and it explains why demand keeps pace with the economy even when year-to-year growth rates are noisy.")

# ---------------- 4 forecasting ----------------
h1(d, "4  Demand forecasting")
h2(d, "4.1  Approach in plain language")
para(d, "Forecasting a short annual series calls for restraint. Rather than fit one elaborate model, we compare several simple ones, test each by repeatedly pretending it is an earlier year, and combine the ones that perform well. All models work on the logarithm of demand, so growth is proportional.")
bullets(d, [("Random walk with drift:", "demand continues to grow at the historical average rate."),
            ("Recent drift:", "the same, but using only the last eight years."),
            ("Log-linear trend:", "a straight line through log demand, i.e. constant percentage growth around a fitted path."),
            ("ARIMA(1,1,0) with drift:", "growth rates are allowed to persist from year to year."),
            ("Damped-trend exponential smoothing (ETS):", "growth that slows gradually; standard in demand forecasting."),
            ("GDP-driver model:", "demand growth explained by GDP growth. It needs future GDP, so it is tested only where GDP is known, and used as a cross-check.")])
h2(d, "4.2  How we test: rolling-origin backtesting")
para(d, "A model's fit to history says little about its forecasting skill. We therefore fit each model on the first 11 years, forecast 1, 2 and 3 years ahead, then add one year and repeat until the data end. This produces 42 genuine out-of-sample forecasts per model, each compared with what actually happened. The score is the mean absolute percentage error (MAPE).")
rows = []
for m in ["Ensemble (mean)", "Drift (RW+drift)", "Log-linear trend", "GDP-driver (conditional)", "ARIMA(1,1,0)+drift", "Recent drift (8y)", "ETS damped trend"]:
    rows.append([m] + [f"{m1(m,h):.1f}%" for h in (1,2,3)] + [f"{bs[(bs.model==m)&(bs.h==1)].rel_MAE_vs_drift.iloc[0]:.2f}"])
table(d, pd.DataFrame(rows, columns=["Model", "1 year ahead", "2 years ahead", "3 years ahead", "Error vs drift (1-yr)"]), caption="Table 4. Out-of-sample accuracy (MAPE) from rolling-origin backtests, 2011–2025 targets", widths=[5.4, 2.4, 2.6, 2.6, 3.2])
figure(d, FG+"fig03_backtest.png", "Mean absolute percentage error by model and forecast horizon.")
h2(d, "4.3  What the backtests say")
bullets(d, [f"The damped-trend ETS model was the least accurate ({m1('ETS damped trend',1):.1f}% at one year and {m1('ETS damped trend',3):.1f}% at three). It slows growth too soon: Kenya's demand growth has not decelerated.",
            "Simple trend models were hard to beat. Random walk with drift and the log-linear trend both beat more elaborate alternatives at most horizons, which is typical when a series is short and smooth.",
            f"The GDP-driver model was competitive at one year ({m1('GDP-driver (conditional)',1):.1f}%) but it is given actual GDP growth in the test, so it is not a fair like-for-like forecast. It is shown for context only.",
            f"The equal-weight ensemble of drift, ARIMA and log-linear trend achieved {m1(E,1):.1f}%, {m1(E,2):.1f}% and {m1(E,3):.1f}% at one, two and three years. It is the headline forecast."])
callout(d, "An honesty note on the ensemble", "The ensemble members were chosen after a first backtest showed ETS and recent-drift were weakest. That is a selection step on a small sample, so the ensemble's backtest accuracy is probably somewhat optimistic. The forecast itself does not depend on this choice much: all retained models give 2035 demand between 24.0 and 25.6 TWh.")
h2(d, "4.4  The forecast")
fc = pd.DataFrame({"Year": [2026, 2028, 2030, 2032, 2035]}); fc["Ensemble (TWh)"] = [f"{F.loc[y,E]:.1f}" for y in fc.Year]; fc["80% interval"] = [ci(y,'lo80','hi80') for y in fc.Year]; fc["95% interval"] = [ci(y,'lo95','hi95') for y in fc.Year]
fc["Implied growth vs 2025"] = [f"{((F.loc[y,E]/d25)**(1/(y-2025))-1)*100:.1f}% p.a." for y in fc.Year]
table(d, fc, caption="Table 5. Kenya electricity demand forecast (TWh)", widths=[2.0, 3.2, 3.6, 3.6, 4.0])
figure(d, FG+"fig02_forecast_fan.png", "Observed demand and ensemble forecast with 80% and 95% prediction intervals.")
para(d, f"The central forecast implies demand of {f30:.1f} TWh in 2030 and {f35:.1f} TWh in 2035, an increase of {(f35/d25-1)*100:.0f}% on 2025. Growth of about {((f35/d25)**(1/10)-1)*100:.1f}% a year is slightly below the {ff['cagr_2020_2025']*100:.1f}% of the last five years and in line with the long-run average.")
h2(d, "4.5  How reliable are the intervals?")
cv = ff["interval_coverage"]
para(d, f"Prediction intervals are built from the ensemble's backtest errors, scaled by the square root of the horizon, the standard result for a random-walk-type process. Checking them against the backtests: the 80% interval contained {cv['1']['cover80']*100:.0f}% of one-year-ahead outcomes (n = {cv['1']['n']}), {cv['2']['cover80']*100:.0f}% of two-year and {cv['3']['cover80']*100:.0f}% of three-year outcomes. Coverage at one year is close to nominal and at longer horizons the intervals are conservative. With 13 to 15 test points per horizon, these coverage figures are themselves imprecise, so they are best read as 'no sign of overconfidence' and not as proof of calibration.")
para(d, "Beyond three years there is no out-of-sample evidence at all, and the intervals for 2030–2035 rest on an assumption. They also cannot capture structural events such as a new large industrial customer, a step change in electrification policy or a prolonged economic shock. For that reason the capacity analysis in Chapter 7 uses the lower and upper 80% bounds as explicit low and high scenarios.")
h2(d, "4.6  Income elasticity of electricity demand")
para(d, f"A common planning question is how much demand grows for each per cent of GDP growth. In growth-rate form the answer is imprecise: pooling nine countries gives an elasticity of {el['pooled_all_10']['elasticity']:.2f} (standard error {el['pooled_all_10']['se']:.2f}, clustered by country), and Kenya alone gives {el['kenya_only_ols']['elasticity']:.2f} with a standard error of {el['kenya_only_ols']['se']:.2f} (p = {el['kenya_only_ols']['p']:.2f}), which is not distinguishable from zero. Year-to-year demand growth in Kenya is driven by factors that annual GDP growth does not capture, such as connections and weather. The long-run levels relationship in Chapter 3 ({el['fe_loglog_levels']['elasticity']:.2f}) is much more informative. The practical conclusion is that GDP growth rates should not be used as a short-term demand predictor for Kenya, but the long-run link between income and demand is strong.")

# ---------------- 5 security index ----------------
h1(d, "5  Supply-security index")
h2(d, "5.1  Why an index")
para(d, "Supply security has many dimensions and no single number captures it. An index makes a transparent, comparable summary possible: it lets planners track Kenya over time and against its neighbours, and it shows which dimension is moving. The index here measures structural exposure using four pillars that can be computed consistently for all ten countries from the data in hand.")
table(d, pd.DataFrame([
  ["Import dependence", "Net imports as % of demand (exporters scored as zero dependence)", "Reliance on neighbours' systems and interconnectors"],
  ["Source concentration", "Herfindahl–Hirschman index of generation shares across nine sources", "A grid reliant on one source is fragile to that source failing"],
  ["Fuel-price exposure", "Fossil share of generation (%)", "Exposure to imported-fuel price and availability"],
  ["Hydrology risk", "Hydro share × rolling 8-year volatility of hydro output", "Share of generation exposed to a one-standard-deviation hydrology swing"]],
  columns=["Pillar", "Measure", "Why it matters"]), caption="Table 6. The four pillars of the supply-security index", widths=[3.4, 6.6, 6.4], align_right_from=9)
para(d, "Each measure is winsorised at the 5th and 95th percentiles of the pooled 2006–2025 sample, rescaled to 0–100 with 100 meaning most secure, and the four scores are averaged with equal weights. The index starts in 2006 because the volatility pillar needs history. A geometric-mean variant, which penalises a country with one very weak pillar, is reported as a robustness check.")
h2(d, "5.2  Results")
figure(d, FG+"fig05_security_index.png", "Left: supply-security index in 2024. Right: index trajectories 2006–2025; Kenya in blue.", width=16)
para(d, f"Kenya scores {ssi24['Kenya']:.0f} in 2024, ahead of Uganda ({ssi24['Uganda']:.0f}), Mozambique ({ssi24['Mozambique']:.0f}) and DR Congo ({ssi24['DR Congo']:.0f}); Burundi ({ssi24['Burundi']:.0f}) and Ethiopia ({ssi24['Ethiopia']:.0f}) are the lowest. Kenya has ranked first in every year from 2010 to 2024. The reason is diversification: Kenya's HHI of {Z[(Z.country=='Kenya')&(Z.year==2025)].hhi.iloc[0]:.2f} compares with 0.5 to 0.9 for every neighbour except Rwanda (0.31), most of which rely on one or two sources, typically hydro.")
para(d, "Two cautions apply. The index measures structural exposure, not operational reliability, so a country can score well and still suffer outages from transmission or distribution failures. It also treats fossil share as a pure negative on security grounds, which penalises Kenya's thermal reserve, the very asset that makes the drought stress test in Chapter 6 survivable. Readers should treat the fossil pillar as a fuel-exposure measure only.")
h2(d, "5.3  What moved inside Kenya's score, 2015 to 2025")
pl = f3["kenya_pillars_2015_2025"]; rw = f3["kenya_raw_2015_2025"]
table(d, pd.DataFrame([
  ["Import dependence", f"{rw['imp_dep'][0]:.1f}%", f"{rw['imp_dep'][1]:.1f}%", f"{pl['imp_dep'][0]:.0f}", f"{pl['imp_dep'][1]:.0f}"],
  ["Source concentration (HHI)", f"{rw['hhi'][0]:.2f}", f"{rw['hhi'][1]:.2f}", f"{pl['hhi'][0]:.0f}", f"{pl['hhi'][1]:.0f}"],
  ["Fossil share", f"{rw['fossil_share'][0]:.1f}%", f"{rw['fossil_share'][1]:.1f}%", f"{pl['fossil_share'][0]:.0f}", f"{pl['fossil_share'][1]:.0f}"],
  ["Hydrology risk exposure", f"{rw['hydro_risk'][0]:.1f}", f"{rw['hydro_risk'][1]:.1f}", f"{pl['hydro_risk'][0]:.0f}", f"{pl['hydro_risk'][1]:.0f}"]],
  columns=["Pillar", "Raw 2015", "Raw 2025", "Score 2015", "Score 2025"]), caption="Table 7. Kenya's pillar values and scores", widths=[5.6, 2.4, 2.4, 2.8, 2.8])
figure(d, FG+"fig06_pillars.png", "Change in Kenya's four pillar scores between 2015 and 2025.", width=13.5)
para(d, f"Three pillars improved or held steady, and one deteriorated. Diversification improved as wind and solar grew; hydrology risk exposure fell sharply (score {pl['hydro_risk'][0]:.0f} to {pl['hydro_risk'][1]:.0f}) because hydro's share of generation fell and its recent volatility is lower than in the drought-affected 2000s. The big loser is import dependence, from near-total security to {pl['imp_dep'][1]:.0f}. The overall index in 2025 ({f3['kenya_ssi_2025']:.0f}) is above 2015 ({f3['kenya_ssi_2015']:.0f}) only because the gains elsewhere outweigh the imports loss, which is a good reason to keep that pillar in view.")
h2(d, "5.4  Is the ranking robust?")
para(d, f"The equal-weight choice is a judgement. To test it, we drew 10,000 random weightings of the four pillars and recomputed Kenya's 2024 rank each time. Kenya's median rank is {f3['kenya_rank_median']:.0f}, it is first in {f3['kenya_rank_dist_2024']['1']*100:.0f}% of draws and its 5th–95th percentile range is {f3['kenya_rank_p5_p95'][0]}–{f3['kenya_rank_p5_p95'][1]}. The leading position is therefore robust on balance but not unconditional. Putting 70% of the weight on a single pillar (10% on each of the others) leaves Kenya first if that pillar is source concentration or hydrology risk, third if it is fuel exposure, and seventh if it is import dependence, where hydro-based neighbours that import little (Uganda, Mozambique, Zambia, Ethiopia) score higher.")
figure(d, FG+"fig11_rank_sensitivity.png", "Distribution of Kenya's 2024 rank across 10,000 random pillar weightings.", width=11)

# ---------------- 6 stress tests ----------------
h1(d, "6  Stress tests: drought and import interruption")
h2(d, "6.1  Design")
para(d, f"The index describes structure. The stress tests ask what would actually happen if supply were disrupted. We take Kenya's actual 2025 supply stack and remove energy from it, then ask whether the remaining sources can fill the hole. The fallback resources are (i) thermal generation up to a ceiling of {si['thermal_ceiling']:.2f} TWh a year (Ember's {si['thermal_capacity_gw']:.2f} GW of fossil capacity at an assumed {si['thermal_cf_assumed']*100:.0f}% availability), of which {si['thermal_2025']:.2f} TWh was already used in 2025, leaving {si['thermal_headroom']:.2f} TWh of headroom; and (ii) imports, which are the thing being tested in some scenarios.")
para(d, f"The drought scenarios are calibrated to history. Kenya's hydro output was 42% below its five-year centred average in 2000 and 29% below in 2009; the single largest year-on-year fall in the data is {abs(f3['hydro_yoy_min'])*100:.0f}%. We therefore use a 25% hydro loss as a moderate drought and a 42% loss as a 2000-type event.")
h2(d, "6.2  Deterministic scenarios")
tbl = pd.DataFrame({"Scenario": [s.split(" (")[0] if len(s) > 44 else s for s in stt.index[1:]], "Supply lost (TWh)": stt.lost_twh[1:].round(2).values, "Replaced by thermal (TWh)": stt.thermal_add_twh[1:].round(2).values,
                    "Unserved (TWh)": stt.unserved_twh[1:].round(2).values, "Unserved (% demand)": stt.unserved_pct_demand[1:].round(1).values, "Extra CO2 (Mt)": stt.extra_co2_mt[1:].round(2).values})
table(d, tbl, caption="Table 8. Stress-test results on the 2025 supply stack", fs=8.5, widths=[5.8, 1.9, 2.3, 2.0, 2.2, 1.8])
figure(d, FG+"fig08_stress.png", "Lost supply in each scenario, split into what thermal plant can replace and what goes unserved.", width=14.6)
bullets(d, [("Each shock alone is manageable.", f"A 2000-type drought (1.2 TWh) or losing all imports (1.5 TWh) falls within thermal headroom ({si['thermal_headroom']:.2f} TWh). The cost is running thermal plant at up to about {si['thermal_cf_assumed']*100:.0f}% availability, about 2.3 times its 2025 output, and adding roughly 0.8 to 1.0 Mt of CO2."),
            ("The combination is not.", f"A 2000-type drought with imports lost leaves {stt.iloc[5].unserved_twh:.2f} TWh ({stt.iloc[5].unserved_pct_demand:.1f}% of demand) unserved. Adding modest wind and geothermal shortfalls raises that to {stt.iloc[6].unserved_pct_demand:.1f}%."),
            ("The result is sensitive to thermal availability.", f"For the combined drought-plus-import-loss scenario, unserved energy is {f3['stress_s5_thermal_cf_sensitivity']['0.8']:.1f}% of demand if thermal plant can run at 80% availability, {f3['stress_s5_thermal_cf_sensitivity']['0.65']:.1f}% at 65% and {f3['stress_s5_thermal_cf_sensitivity']['0.5']:.1f}% at 50%. Maintenance and fuel logistics for thermal plant are therefore a strategic-reserve issue, not a detail.")])
h2(d, "6.3  Monte Carlo on observed hydrology")
para(d, f"The deterministic scenarios are chosen by us. To let the history speak, we resampled the 25 observed years of hydro and geothermal deviations from their five-year averages 20,000 times and applied them to the 2025 stack, in two states: imports available, and imports interrupted. The probabilities below are conditional on the import state; the analysis does not attempt to estimate how likely an interconnector outage is.")
table(d, pd.DataFrame([["Imports available", f"{mc_a['p_any_loss']*100:.0f}%", f"{mc_a['p_unserved']*100:.0f}%", f"{mc_a['p95_unserved_pct_demand']:.1f}%", f"{mc_a['p95_thermal_twh']:.2f}"],
                       ["Imports interrupted", f"{mc_o['p_any_loss']*100:.0f}%", f"{mc_o['p_unserved']*100:.0f}%", f"{mc_o['p95_unserved_pct_demand']:.1f}%", f"{mc_o['p95_thermal_twh']:.2f}"]],
                      columns=["State", "P(supply loss)", "P(energy shortfall)", "95th pct shortfall (% demand)", "95th pct thermal call (TWh)"]),
      caption="Table 9. Monte Carlo results (20,000 draws of historical hydrology and geothermal deviations)", widths=[3.6, 2.6, 3.0, 3.8, 3.6])
figure(d, FG+"fig09_monte_carlo.png", "Probability of an annual energy shortfall and the 95th-percentile shortfall, by import state.", width=14)
para(d, f"With imports available, thermal plant covers every simulated hydrology year: the 95th-percentile thermal call is {mc_a['p95_thermal_twh']:.2f} TWh against {si['thermal_headroom']:.2f} TWh of headroom. With imports out, the same hydrology produces a shortfall in {mc_o['p_unserved']*100:.0f}% of draws, and in the worst 5% it reaches {mc_o['p95_unserved_pct_demand']:.1f}% of demand. Imports are therefore currently a shock absorber for the system and a vulnerability at the same time: they cover the deficit when hydrology is bad, but their loss in the same year is the scenario that matters.")
callout(d, "How to read these results", "The tests are on an annual-energy basis. They show whether the year's energy can in principle be found, not whether it can be delivered at the hour of peak demand, through the transmission network or at an acceptable cost. In practice shortfalls would appear earlier and be concentrated in dry-season peaks. Treat the figures as a lower bound on risk.", fill="FDF3E1")

# ---------------- 7 capacity gap ----------------
h1(d, "7  Capacity-gap analysis to 2035")
h2(d, "7.1  Method")
para(d, f"The question is how much new generation Kenya must add so that supply keeps pace with demand without relying on more imports or more thermal output than in 2025. The 2025 supply stack (generation plus imports, {d25:.1f} TWh) is held constant; the gap is demand in the target year minus {d25:.1f} TWh. The three demand paths are the forecast's lower 80% bound, central path and upper 80% bound. The gap is converted to gigawatts using assumed capacity factors for new plant: geothermal 85%, wind 45%, solar 25%, under three technology mixes expressed as shares of new energy.")
para(d, "A second variant also phases imports and thermal output down to 5% of demand each, which raises the requirement.")
h2(d, "7.2  Results")
rows = []
for s, nm in (("Low", "Low demand"), ("Base", "Base demand"), ("High", "High demand")):
    for y in (2030, 2035):
        rows.append([nm, y, f"{cap[(cap.scenario.str.startswith(s))&(cap.year==y)].demand_twh.iloc[0]:.1f}", f"{gapv(s,y):.1f}", f"{capv(s,y,'Geo'):.1f}", f"{capv(s,y,'Bal'):.1f}", f"{capv(s,y,'Sol'):.1f}"])
table(d, pd.DataFrame(rows, columns=["Demand path", "Year", "Demand (TWh)", "Gap vs 2025 (TWh)", "New GW: geothermal-led", "New GW: balanced", "New GW: solar-heavy"]),
      caption="Table 10. New generation required to meet demand while holding imports and thermal at 2025 levels", fs=8.5, widths=[2.9, 1.3, 2.2, 2.5, 2.7, 2.4, 2.4])
figure(d, FG+"fig10_capacity_gap.png", "New capacity needed by 2035 under three technology mixes and three demand paths (imports and thermal held at 2025 levels).")
h2(d, "7.3  Interpretation")
bullets(d, [f"In the base case, Kenya needs an additional {gapv('Base',2030):.1f} TWh of supply by 2030 and {gapv('Base',2035):.1f} TWh by 2035. That is {f3['req_pace_base_2035']:.2f} TWh a year, {f3['pace_multiple_base_2035']:.1f} times the {f3['hist_gen_addition_twh_per_yr_2015_2025']:.2f} TWh a year added in 2015–2025 and {f3['req_pace_base_2035']/f3['hist_gen_addition_twh_per_yr_2020_2025']:.1f} times the {f3['hist_gen_addition_twh_per_yr_2020_2025']:.2f} TWh a year of the last five years.",
            f"The technology mix matters for the gigawatts needed. Because geothermal runs at a far higher capacity factor, a geothermal-led programme needs {capv('Base',2035,'Geo'):.1f} GW against {capv('Base',2035,'Sol'):.1f} GW for a solar-heavy one to deliver the same energy. Lower-capacity-factor technologies need more physical plant, more land and more transmission for the same TWh, and they bring more variability.",
            f"The 80% demand band alone spans {capv('Low',2035,'Bal'):.1f} to {capv('High',2035,'Bal'):.1f} GW (balanced mix): planning uncertainty in demand is as large as the choice of technology. A programme that is robust across the band needs staged commitments that can be accelerated if demand tracks the upper path.",
            "Phasing imports and thermal down to 5% each adds comparatively little in the base case by 2035, because the system is already growing so fast that fixed 2025 import and thermal volumes become a small share of demand."])
callout(d, "A caution on the gigawatt figures", "These are indicative. They convert annual energy to capacity with assumed capacity factors, and ignore reserve margins, transmission losses, curtailment, retirements, storage and the need for firm capacity at peak. The energy gap in TWh is the more reliable number; the GW figures show relative scale and the effect of the technology mix.")

# ---------------- 8 recommendations ----------------
h1(d, "8  Recommendations for energy planners")
h2(d, "8.1  Monitoring: what to track and how often")
table(d, pd.DataFrame([
  ["Net imports as % of demand", "Monthly", "Early signal of dependence on interconnectors; our 2025 value is 9.8%. Set an alert threshold and review the stress test when it is crossed."],
  ["Thermal availability and fuel stocks", "Monthly", "Thermal plant is the system's main buffer. Its available energy, not its nameplate, determines whether a drought plus import loss is survivable."],
  ["Hydro output vs five-year average", "Monthly during rains", "A hydro deviation worse than -15% triggers a review; 2000 and 2009 were -42% and -29%."],
  ["Demand vs forecast band", "Quarterly", "Re-run the model each release; flag if demand leaves the 80% band two quarters running."],
  ["Share of the largest source", "Annual", "Keeps the diversification advantage visible."]],
  columns=["Indicator", "Frequency", "Why"]), caption="Table 11. Proposed monitoring dashboard", widths=[4.6, 2.8, 9.0], align_right_from=9)
h2(d, "8.2  Supply planning")
bullets(d, ["Plan on the central demand path but pre-position options for the upper band; the cost of being late is higher than the cost of options.",
            "Prefer firm, high-capacity-factor additions (geothermal, where resource and finance allow) for the energy backbone, and use wind and solar for volume and speed, rather than treating the choice as either-or.",
            "Treat imports as a complement to domestic supply and not a substitute for it. Pair any growth in contracted imports with matching thermal or storage reserve.",
            "Test thermal fuel supply and maintenance schedules as part of strategic-stock planning, since the combined-shock result depends heavily on thermal availability."])
h2(d, "8.3  Data improvements")
bullets(d, ["Publish monthly generation, peak demand and reservoir levels in open formats. These would allow seasonal models and peak-adequacy analysis that annual data cannot support.",
            "Report installed capacity for geothermal and other renewables; the zero values in international datasets undermine reserve-margin analysis.",
            "Record the origin of imports, so that dependence on a single interconnector can be measured directly."])

# ---------------- 9 limitations ----------------
h1(d, "9  Limitations and threats to validity")
bullets(d, [("Small sample.", "Twenty-six annual observations limit model complexity, and prediction intervals beyond three years rest on an assumption that cannot be verified."),
            ("Selection step in the ensemble.", "Members were chosen after a first backtest; backtest accuracy is mildly optimistic."),
            ("Annual energy, not power.", "No peak, seasonal or hourly analysis; the stress tests are a lower bound on risk."),
            ("Index design is a judgement.", "Four pillars, equal weights and winsorisation choices shape the ranking. Robustness checks show Kenya's lead is typical but not guaranteed."),
            ("Thermal capacity assumption.", f"Thermal ceiling uses an assumed {si['thermal_cf_assumed']*100:.0f}% availability and Ember's reported fossil capacity of {si['thermal_capacity_gw']:.2f} GW; Section 6.2 shows how sensitive the combined-shock result is to it."),
            ("Capacity factors for new plant", "are assumptions, not forecasts of project performance."),
            ("No economics.", "The open datasets contain no tariffs, fuel prices or investment costs. The analysis says what is needed and how risky the system is, not what it costs."),
            ("Peer comparability.", "Differences in metering, definitions and data quality across countries (especially for small systems such as Burundi) affect the benchmarking."),
            ("Data revisions.", "The latest year can change; results should be refreshed with each release.")])

# ---------------- 10 conclusion ----------------
h1(d, "10  Conclusion")
para(d, f"Kenya's electricity system is large, fast-growing and unusually diversified. Demand is likely to reach about {f30:.0f} TWh by 2030 and {f35:.0f} TWh by 2035, with a plausible range of {ci(2035,'lo80','hi80')} TWh in 2035. The system's structural security is the best among ten regional peers, and its low-carbon mix is a genuine asset. Its main emerging vulnerability is dependence on imported electricity, and its main buffer is a small fleet of thermal plant whose availability matters more than its size.")
para(d, f"Meeting base-case demand means building at roughly twice the pace of the last decade. The analysis suggests where to focus: firm domestic supply, a monitored thermal reserve, a watched import share, and better data. Every figure in this report can be regenerated from the open datasets and the accompanying code, and the method is general: the same pipeline can be pointed at any country in the Ember data.")

# ---------------- appendices ----------------
h1(d, "Appendix A  Glossary")
for a, b in [("TWh / GW", "Terawatt-hour (a billion kWh) of energy; gigawatt of power capacity."), ("Capacity factor", "Actual annual output as a fraction of what the plant would produce running at full power all year."),
             ("MAPE", "Mean absolute percentage error: the average size of forecast misses as a percent of the actual value."), ("Rolling-origin backtest", "Repeatedly fitting a model on data up to a year, forecasting ahead, and scoring against what happened."),
             ("ARIMA / ETS", "Standard time-series model families: autoregressive integrated moving average and exponential smoothing."), ("HHI", "Herfindahl–Hirschman index: sum of squared shares; higher means more concentrated."),
             ("Winsorise", "Cap extreme values at chosen percentiles so outliers do not dominate scaling."), ("Net imports", "Imports minus exports of electricity."),
             ("Interval (80% / 95%)", "Range expected to contain the outcome with that probability, given the model's historical errors.")]:
    para(d, b, bold_lead=a, after=3)
h1(d, "Appendix B  Data dictionary (analysis tables)")
dd = [["country, year", "Panel keys"], ["hydro, geothermal_other_ren, wind, solar, bioenergy, coal, gas, other_fossil, nuclear", "Generation by source (TWh), Ember"], ["generation", "Total generation (TWh)"], ["net_imports", "Imports minus exports (TWh)"],
      ["demand", "Electricity demand = generation + net imports (TWh)"], ["fossil, clean, renewables", "Ember aggregates (TWh)"], ["emissions_mtco2e, emissions_intensity_g_kwh", "Power-sector emissions (Mt CO2e) and intensity (g/kWh)"],
      ["population, gdp", "OWID; GDP in 2011 international dollars"], ["demand_per_capita_kwh, gdp_per_capita", "Derived"], ["hhi, imp_dep, fossil_share, hydro_share, hydro_vol, hydro_risk", "Security-index inputs"],
      ["s_*, SSI, SSI_geo", "Pillar scores (0–100), equal-weight and geometric indices"]]
table(d, pd.DataFrame(dd, columns=["Field", "Description"]), widths=[7.4, 9.0], align_right_from=9)
h1(d, "Appendix C  Supporting tables")
fa = F[["Drift (RW+drift)", "Log-linear trend", "ARIMA(1,1,0)+drift", "Ensemble (mean)", "lo80", "hi80", "lo95", "hi95"]].round(1).reset_index()
fa.columns = ["Year", "Drift", "Log-trend", "ARIMA", "Ensemble", "Lo 80%", "Hi 80%", "Lo 95%", "Hi 95%"]
table(d, fa, caption="Table C1. Forecast paths and prediction intervals, 2026–2035 (TWh)", fs=8.5)
kk = k[["demand", "generation", "net_imports", "hydro", "geothermal_other_ren", "wind", "solar", "emissions_intensity_g_kwh"]].loc[[2000, 2005, 2010, 2015, 2020, 2022, 2023, 2024, 2025]].round(2).reset_index()
kk.columns = ["Year", "Demand", "Generation", "Net imports", "Hydro", "Geoth./other", "Wind", "Solar", "g CO2/kWh"]
table(d, kk, caption="Table C2. Selected Kenya series (TWh unless stated)", fs=8.5)
h1(d, "Appendix D  Sources", newpage=False)
bullets(d, ["Ember. Yearly electricity data. Licensed CC BY 4.0. https://ember-energy.org/data/yearly-electricity-data/",
            "Our World in Data. Energy dataset (compiled from Ember, the Energy Institute Statistical Review and other sources). Licensed CC BY 4.0. https://github.com/owid/energy-data",
            "All code, derived data and figures: project GitHub repository (see README). Method detail: Technical Methods Report."])
d.save("reports/Final_Report_Kenya_Electricity_Outlook_and_Supply_Security.docx"); print("saved")
