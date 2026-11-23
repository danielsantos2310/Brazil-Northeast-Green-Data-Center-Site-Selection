import pandas as pd

from src.clean.clean_aneel_siga import (
    NE_STATES,
    clean_northeast,
    parse_ptbr_numeric,
)


def test_parse_ptbr_numeric():
    s = pd.Series(["1.234,56", "652,50", ",00", ""])
    out = parse_ptbr_numeric(s)
    assert out.iloc[0] == 1234.56
    assert out.iloc[1] == 652.50
    assert out.iloc[2] == 0
    assert pd.isna(out.iloc[3])


def test_clean_northeast_filters_and_minimizes_fields():
    df = pd.DataFrame(
        {
            "DatGeracaoConjuntoDados": ["2026-10-01", "2026-10-01"],
            "NomEmpreendimento": ["A", "B"],
            "CodCEG": ["EOL.AA.CE.1", "EOL.AA.SP.2"],
            "SigUFPrincipal": ["CE", "SP"],
            "SigTipoGeracao": ["EOL", "EOL"],
            "DscFaseUsina": ["Operação", "Operação"],
            "MdaPotenciaOutorgadaKw": ["1000,00", "2000,00"],
            "MdaPotenciaFiscalizadaKw": ["900,00", "1800,00"],
            "MdaGarantiaFisicaKw": ["", ""],
            "NumCoordNEmpreendimento": ["-3,7", "-23,5"],
            "NumCoordEEmpreendimento": ["-38,5", "-46,6"],
            "DscMuninicpios": ["Fortaleza - CE", "São Paulo - SP"],
            "DscPropriRegimePariticipacao": ["identifier text", "identifier text"],
        }
    )
    out = clean_northeast(df)
    assert len(out) == 1
    assert set(out["SigUFPrincipal"]) <= NE_STATES
    assert out.iloc[0]["capacity_fiscalized_mw"] == 0.9
    assert bool(out.iloc[0]["coordinate_valid"])
    assert "DscPropriRegimePariticipacao" not in out.columns
