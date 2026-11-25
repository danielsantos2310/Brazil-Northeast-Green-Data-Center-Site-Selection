from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

def read(path, **kwargs):
    return pd.read_csv(ROOT / path, **kwargs)

def test_step16_gate_matrix_has_all_tier_a_candidates():
    df=read("data/processed/step16_tierA_diligence_gate_matrix_v2_climate_risk_2026-11-25.csv",dtype={"ibge_code":str})
    assert len(df)==11
    assert df["ibge_code"].nunique()==11
    assert df["municipality"].nunique()==11

def test_adaptabrasil_baseline_is_complete_and_versioned():
    df=read("data/processed/step16_adaptabrasil_tierA_risk_v1.csv",dtype={"ibge_code":str})
    assert len(df)==22
    assert df["matched"].astype(str).str.lower().eq("true").all()
    assert set(df["indicator_key"])=={"water_stress_risk","flood_risk"}
    years=dict(df.groupby("indicator_key")["year"].first())
    assert years["water_stress_risk"]==2020
    assert years["flood_risk"]==2015
    assert df.groupby("indicator_key")["ibge_code"].nunique().eq(11).all()

def test_external_diligence_queue_is_exactly_five():
    df=read("data/processed/step16_external_diligence_shortlist_v1_2026-11-25.csv")
    active=df[df["candidate_priority"]<=5]
    assert len(active)==5
    assert active["municipality"].nunique()==5
    expected={
        "Bom Jesus da Lapa","Brumado","Juazeiro",
        "São Gonçalo do Amarante","Urandi",
    }
    assert set(active["municipality"])==expected

def test_no_external_gate_is_accidentally_marked_verified():
    df=read("data/processed/step16_tierA_diligence_gate_matrix_v2_climate_risk_2026-11-25.csv")
    cols=[
        "utility_headroom_gate","water_supply_rights_gate",
        "carrier_route_independence_gate","parcel_feasibility_gate",
    ]
    for col in cols:
        assert df[col].eq("UNVERIFIED_EXTERNAL_DILIGENCE").all()
