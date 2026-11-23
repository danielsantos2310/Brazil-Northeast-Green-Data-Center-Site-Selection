"""Clean and summarize ANEEL SIGA for Northeast Brazil.

The raw source remains unchanged. Public/processed output deliberately excludes
DscPropriRegimePariticipacao because the field can contain personal/company
identifiers that are not required for this site-selection project.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

NE_STATES = {"MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"}
REQUIRED_COLUMNS = {
    "DatGeracaoConjuntoDados",
    "NomEmpreendimento",
    "CodCEG",
    "SigUFPrincipal",
    "SigTipoGeracao",
    "DscFaseUsina",
    "MdaPotenciaOutorgadaKw",
    "MdaPotenciaFiscalizadaKw",
    "NumCoordNEmpreendimento",
    "NumCoordEEmpreendimento",
    "DscMuninicpios",
}
NUMERIC_COLUMNS = [
    "MdaPotenciaOutorgadaKw",
    "MdaPotenciaFiscalizadaKw",
    "MdaGarantiaFisicaKw",
    "NumCoordNEmpreendimento",
    "NumCoordEEmpreendimento",
]
TECHNOLOGY_LABELS = {
    "EOL": "Wind",
    "UFV": "Solar",
    "UHE": "Hydro",
    "PCH": "Hydro",
    "CGH": "Hydro",
    "UTE": "Thermal",
}
DROP_FROM_PUBLIC = {"DscPropriRegimePariticipacao"}


def parse_ptbr_numeric(series: pd.Series) -> pd.Series:
    """Convert ANEEL decimal-comma text to numeric values."""
    cleaned = (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA})
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def load_siga(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        keep_default_na=False,
    )
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required SIGA columns: {sorted(missing)}")
    return df


def clean_northeast(df: pd.DataFrame) -> pd.DataFrame:
    out = df.loc[df["SigUFPrincipal"].isin(NE_STATES)].copy()

    for col in NUMERIC_COLUMNS:
        if col in out.columns:
            out[col] = parse_ptbr_numeric(out[col])

    out["technology"] = out["SigTipoGeracao"].map(TECHNOLOGY_LABELS).fillna(
        out["SigTipoGeracao"]
    )
    out["capacity_granted_mw"] = out["MdaPotenciaOutorgadaKw"] / 1000
    out["capacity_fiscalized_mw"] = out["MdaPotenciaFiscalizadaKw"] / 1000
    out["latitude"] = out["NumCoordNEmpreendimento"]
    out["longitude"] = out["NumCoordEEmpreendimento"]
    out["is_operating"] = out["DscFaseUsina"].eq("Operação")
    out["is_wind_solar"] = out["SigTipoGeracao"].isin(["EOL", "UFV"])
    out["coordinate_valid"] = (
        out["latitude"].notna()
        & out["longitude"].notna()
        & out["latitude"].ne(0)
        & out["longitude"].ne(0)
        & out["latitude"].between(-35, 6)
        & out["longitude"].between(-75, -30)
    )

    out = out.drop(columns=[c for c in DROP_FROM_PUBLIC if c in out.columns])
    return out


def build_state_summary(df: pd.DataFrame) -> pd.DataFrame:
    states = []
    for state, g in df.groupby("SigUFPrincipal", sort=True):
        operating = g["is_operating"]
        wind = operating & g["SigTipoGeracao"].eq("EOL")
        solar = operating & g["SigTipoGeracao"].eq("UFV")
        pipeline_ws = (~operating) & g["is_wind_solar"]

        valid = int(g["coordinate_valid"].sum())
        total = len(g)
        states.append(
            {
                "state": state,
                "plant_records": total,
                "operating_all_mw": g.loc[operating, "capacity_fiscalized_mw"].sum(),
                "operating_wind_mw": g.loc[wind, "capacity_fiscalized_mw"].sum(),
                "operating_solar_mw": g.loc[solar, "capacity_fiscalized_mw"].sum(),
                "operating_wind_solar_mw": g.loc[
                    wind | solar, "capacity_fiscalized_mw"
                ].sum(),
                "wind_solar_pipeline_granted_mw": g.loc[
                    pipeline_ws, "capacity_granted_mw"
                ].sum(),
                "valid_coordinates": valid,
                "missing_coordinates": total - valid,
                "coordinate_completeness_pct": 100 * valid / total,
            }
        )
    result = pd.DataFrame(states)
    return result.sort_values("operating_wind_solar_mw", ascending=False)


def build_technology_phase_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(
            ["SigUFPrincipal", "SigTipoGeracao", "technology", "DscFaseUsina"],
            dropna=False,
            as_index=False,
        )
        .agg(
            plants=("CodCEG", "size"),
            fiscalized_mw=("capacity_fiscalized_mw", "sum"),
            granted_mw=("capacity_granted_mw", "sum"),
        )
        .rename(
            columns={
                "SigUFPrincipal": "state",
                "SigTipoGeracao": "technology_code",
                "DscFaseUsina": "phase",
            }
        )
        .sort_values(["state", "technology_code", "phase"])
    )


def validate(df_raw: pd.DataFrame, df_ne: pd.DataFrame) -> None:
    assert len(df_raw.columns) == 23, f"Expected 23 columns, got {len(df_raw.columns)}"
    assert set(df_ne["SigUFPrincipal"].dropna()) == NE_STATES
    assert not df_ne["CodCEG"].eq("").any()
    assert not df_ne["CodCEG"].duplicated().any()
    assert (df_ne["capacity_granted_mw"].dropna() >= 0).all()
    assert (df_ne["capacity_fiscalized_mw"].dropna() >= 0).all()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to raw SIGA CSV")
    parser.add_argument(
        "--output-dir", default="data/processed", help="Directory for derived outputs"
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw = load_siga(args.input)
    ne = clean_northeast(raw)
    validate(raw, ne)

    ne.to_parquet(output_dir / "aneel_siga_northeast_clean.parquet", index=False)
    build_state_summary(ne).to_csv(
        output_dir / "aneel_ne_state_summary.csv", index=False
    )
    build_technology_phase_summary(ne).to_csv(
        output_dir / "aneel_ne_technology_phase_summary.csv", index=False
    )

    print(f"Raw records: {len(raw):,}")
    print(f"Northeast records: {len(ne):,}")
    print(f"Snapshot date(s): {sorted(raw['DatGeracaoConjuntoDados'].unique())}")


if __name__ == "__main__":
    main()
