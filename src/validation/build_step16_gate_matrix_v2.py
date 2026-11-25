"""Build Step-16 v2 diligence bands with official AdaptaBrasil baseline risks.

Inputs:
- v1 Tier-A gate matrix (final v4 evidence)
- live AdaptaBrasil municipal risk extract:
    water-stress risk baseline = 2020
    flood / flash-flood / urban-flood risk baseline = 2015

The output remains a study-priority matrix, not an investment ranking.
"""

from pathlib import Path
import pandas as pd

BASE = Path("data/processed/step16_tierA_diligence_gate_matrix_v1_2026-11-25.csv")
RISK = Path("data/processed/step16_adaptabrasil_tierA_risk_v1.csv")
OUT = Path("data/processed/step16_tierA_diligence_gate_matrix_v2_climate_risk_2026-11-25.csv")

HIGH = {"Alto", "Muito alto", "Muito Alto"}
VERY_HIGH = {"Muito alto", "Muito Alto"}

def risk_value(pivot, code, indicator, field):
    try:
        return pivot.loc[(code, indicator), field]
    except KeyError:
        return None

def classify(row):
    original = row["study_priority_band"]
    ws = str(row.get("adaptabrasil_water_stress_label") or "")
    fl = str(row.get("adaptabrasil_flood_risk_label") or "")

    if original == "P2_STRATEGIC_CONDITIONAL":
        return "P2_STRATEGIC_CONDITIONAL_GRID"

    if original == "P3_TARGETED_RISK_RESOLUTION":
        return "P3_TARGETED_RISK_RESOLUTION"

    if ws not in VERY_HIGH and fl not in HIGH:
        return "P1A_EXTERNAL_DILIGENCE_FRONT_RUNNER"

    return "P1B_ADVANCE_WITH_CLIMATE_WATER_CONDITIONS"

def climate_gate(row):
    issues=[]
    ws=str(row.get("adaptabrasil_water_stress_label") or "")
    fl=str(row.get("adaptabrasil_flood_risk_label") or "")
    if ws in VERY_HIGH:
        issues.append("very-high baseline water-stress risk")
    elif ws in HIGH:
        issues.append("high baseline water-stress risk")
    if fl in HIGH:
        issues.append("high baseline flood/flash-flood/urban-flood risk")
    return "; ".join(issues) if issues else "no high/very-high baseline AdaptaBrasil flag"

def next_actions(row):
    actions=["formal utility headroom study", "permitted industrial-water study",
             "physical carrier-route validation", "parcel screen"]
    if str(row.get("adaptabrasil_water_stress_label") or "") in HIGH | VERY_HIGH:
        actions.insert(1,"water-demand/climate-stress assessment")
    if str(row.get("adaptabrasil_flood_risk_label") or "") in HIGH:
        actions.append("parcel flood/hydraulic assessment")
    if bool(row.get("epe_access_risk_flag")):
        actions.insert(0,"resolve EPE grid-access constraint/timing")
    return "; ".join(dict.fromkeys(actions))

base=pd.read_csv(BASE,dtype={"ibge_code":str})
risk=pd.read_csv(RISK,dtype={"ibge_code":str})
risk["ibge_code"]=risk["ibge_code"].str[:7]

p=risk.set_index(["ibge_code","indicator_key"])

base["adaptabrasil_water_stress_value"]=[
    risk_value(p,c,"water_stress_risk","value") for c in base["ibge_code"]
]
base["adaptabrasil_water_stress_label"]=[
    risk_value(p,c,"water_stress_risk","range_label") for c in base["ibge_code"]
]
base["adaptabrasil_water_stress_year"]=[
    risk_value(p,c,"water_stress_risk","year") for c in base["ibge_code"]
]
base["adaptabrasil_flood_risk_value"]=[
    risk_value(p,c,"flood_risk","value") for c in base["ibge_code"]
]
base["adaptabrasil_flood_risk_label"]=[
    risk_value(p,c,"flood_risk","range_label") for c in base["ibge_code"]
]
base["adaptabrasil_flood_risk_year"]=[
    risk_value(p,c,"flood_risk","year") for c in base["ibge_code"]
]

if base[["adaptabrasil_water_stress_value","adaptabrasil_flood_risk_value"]].isna().any().any():
    missing=base.loc[
        base[["adaptabrasil_water_stress_value","adaptabrasil_flood_risk_value"]].isna().any(axis=1),
        ["ibge_code","municipality","state"]
    ]
    raise RuntimeError(f"Missing AdaptaBrasil matches:\n{missing.to_string(index=False)}")

base["step16_v2_band"]=base.apply(classify,axis=1)
base["adaptabrasil_risk_gate"]=base.apply(climate_gate,axis=1)
base["step16_next_actions"]=base.apply(next_actions,axis=1)

order={
    "P1A_EXTERNAL_DILIGENCE_FRONT_RUNNER":0,
    "P1B_ADVANCE_WITH_CLIMATE_WATER_CONDITIONS":1,
    "P2_STRATEGIC_CONDITIONAL_GRID":2,
    "P3_TARGETED_RISK_RESOLUTION":3,
}
base["_order"]=base["step16_v2_band"].map(order)
base=base.sort_values(["_order","median_rank"]).drop(columns="_order")

OUT.parent.mkdir(parents=True,exist_ok=True)
base.to_csv(OUT,index=False)

cols=["municipality","state","step16_v2_band",
      "adaptabrasil_water_stress_value","adaptabrasil_water_stress_label",
      "adaptabrasil_flood_risk_value","adaptabrasil_flood_risk_label",
      "step16_next_actions"]
print(base[cols].to_string(index=False))
print(f"\nWrote {OUT}")
