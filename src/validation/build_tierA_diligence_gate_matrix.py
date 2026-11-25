"""Build the Step-16 Tier-A due-diligence gate matrix.

This script intentionally does NOT create another attractiveness score.
It converts the final v4 Tier-A shortlist into explicit diligence gates and
study-priority bands using only evidence already present in the release.

The output is a triage tool. It does not verify utility headroom, water rights,
carrier-route independence, parcel feasibility or investment readiness.
"""

from pathlib import Path
import pandas as pd

INPUT = Path("data/processed/step12_tierA_candidate_archetypes_and_gates_v4_water_integrated_2026-11-25.csv")
OUTPUT = Path("data/processed/step16_tierA_diligence_gate_matrix_v1_2026-11-25.csv")

def env_gate(x):
    if x >= 20:
        return "HIGH_MUNICIPAL_OVERLAP"
    if x >= 5:
        return "MATERIAL_MUNICIPAL_OVERLAP"
    return "CLEAN_MUNICIPAL_SCREEN"

def climate_gate(x):
    if x >= 0.70:
        return "FAVOURABLE_SCREEN"
    if x >= 0.45:
        return "MODERATE_SCREEN"
    return "CHALLENGING_SCREEN"

def water_gate(x):
    if x >= 0.65:
        return "STRONG_HYDROLOGICAL_EVIDENCE"
    if x >= 0.40:
        return "MODERATE_HYDROLOGICAL_EVIDENCE"
    return "WEAK_HYDROLOGICAL_EVIDENCE"

def fibre_gate(n):
    if n >= 8:
        return "STRONG_PROVIDER_DEPTH"
    if n >= 5:
        return "MODERATE_PROVIDER_DEPTH"
    return "LIMITED_PROVIDER_DEPTH"

def study_band(r):
    # Priority 1 = strongest candidates to spend diligence effort on first,
    # NOT an investment recommendation.
    if (
        not bool(r["epe_known_near_term_access_constraint_flag"])
        and r["cnuc_overlap_pct"] < 10
        and r["fiber_provider_count"] >= 5
        and r["water_score"] >= 0.40
        and r["climate_score"] >= 0.45
    ):
        return "P1_ADVANCE_FIRST"
    if bool(r["epe_known_near_term_access_constraint_flag"]):
        return "P2_STRATEGIC_CONDITIONAL"
    return "P3_TARGETED_RISK_RESOLUTION"

def next_gate(r):
    gates = []
    if bool(r["epe_known_near_term_access_constraint_flag"]):
        gates.append("utility connection/headroom")
    if r["water_score"] < 0.40:
        gates.append("water supply/rights")
    else:
        gates.append("permitted water supply")
    if r["fiber_provider_count"] < 8:
        gates.append("independent fibre routes")
    if r["cnuc_overlap_pct"] >= 5:
        gates.append("parcel environmental screen")
    if r["climate_score"] < 0.45:
        gates.append("extreme-heat/cooling resilience")
    if not gates:
        gates.append("utility headroom")
    return "; ".join(dict.fromkeys(gates))

df = pd.read_csv(INPUT)

out = df[[
    "ibge_code","municipality","state","sensitivity_median_rank_across_scenarios",
    "energy_score","grid_strength_score","connectivity_score","climate_score",
    "environment_score","water_score","fiber_provider_count",
    "nearest_ons_operating_230kv_substation_distance_km","cnuc_overlap_pct",
    "epe_known_near_term_access_constraint_flag","water_supply_verified"
]].copy()

out["utility_headroom_gate"] = "UNVERIFIED_EXTERNAL_DILIGENCE"
out["water_supply_rights_gate"] = "UNVERIFIED_EXTERNAL_DILIGENCE"
out["carrier_route_independence_gate"] = "UNVERIFIED_EXTERNAL_DILIGENCE"
out["parcel_feasibility_gate"] = "UNVERIFIED_EXTERNAL_DILIGENCE"
out["environment_triage"] = out["cnuc_overlap_pct"].map(env_gate)
out["climate_triage"] = out["climate_score"].map(climate_gate)
out["hydrology_triage"] = out["water_score"].map(water_gate)
out["provider_depth_triage"] = out["fiber_provider_count"].map(fibre_gate)
out["study_priority_band"] = df.apply(study_band, axis=1)
out["next_blocking_gate"] = df.apply(next_gate, axis=1)

out = out.sort_values(
    ["study_priority_band","sensitivity_median_rank_across_scenarios"],
    ascending=[True, True],
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(OUTPUT, index=False)

print(out[["municipality","state","study_priority_band","next_blocking_gate"]].to_string(index=False))
print(f"\nWrote {OUTPUT}")
