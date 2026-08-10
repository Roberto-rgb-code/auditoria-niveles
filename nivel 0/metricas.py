"""Metricas Nivel 0 — solo pandas, datos en analisis/nivel0/."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

CARGO_DIP = "Diputacion local de mayoria relativa"
D4_INST = 4

ARCHIVOS_N0 = {
    "historial_partidos.csv": "Registro largo por partido (limpieza N0)",
    "base_maestra_largo.csv": "Maestra homologada a bloques",
    "base_seccion_anio.csv": "Acta agregada seccion x anio x cargo",
    "base_seccion_anio_interpolada.csv": "Serie remapeada a demarcacion vigente (N0.5)",
    "catalogo_secciones.csv": "Catalogo territorial 2024",
}


def nivel0_dir(repo_root: Path) -> Path:
    return repo_root / "analisis" / "nivel0"


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return -1
    with path.open(encoding="utf-8-sig") as fh:
        return sum(1 for _ in fh) - 1


def load_seccion_anio(n0: Path) -> pd.DataFrame:
    return pd.read_csv(n0 / "base_seccion_anio.csv", encoding="utf-8-sig", low_memory=False)


def load_interpolada(n0: Path) -> pd.DataFrame:
    return pd.read_csv(
        n0 / "base_seccion_anio_interpolada.csv", encoding="utf-8-sig", low_memory=False
    )


def filter_d4(df: pd.DataFrame, *, interpolada: bool = False) -> pd.DataFrame:
    out = df[df["cargo"] == CARGO_DIP].copy()
    if interpolada and "distrito_local_vigente" in out.columns:
        d = out["distrito_local_vigente"].astype(str).str.replace(".0", "", regex=False)
        return out[d == "4"]
    col = "distrito_local_del_anio" if "distrito_local_del_anio" in out.columns else "distrito_local"
    if col in out.columns:
        return out[out[col].astype(float).astype(int) == D4_INST]
    return out


def agg_historico_d4(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("anio", as_index=False)
        .agg(
            secciones=("seccion", "nunique"),
            validos=("votos_validos", "sum"),
            mc=("votos_MC", "sum"),
            m4t=("votos_MORENA_4T", "sum"),
            pan=("votos_PAN", "sum"),
            pri=("votos_PRI", "sum"),
            otros=("votos_OTROS", "sum"),
            outliers=("flag_outlier", "sum"),
        )
        .sort_values("anio")
    )
    tot = g["validos"].replace(0, pd.NA)
    g["pct_mc"] = (g["mc"] / tot * 100).round(2)
    g["pct_4t"] = (g["m4t"] / tot * 100).round(2)
    return g


def ganador_2024(df: pd.DataFrame) -> pd.Series:
    return df.loc[df["anio"] == 2024, "ganador_bloque"].value_counts()


def quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    names = [
        "flag_outlier",
        "flag_datos_incompletos",
        "flag_coalicion_compleja",
        "flag_lista_nominal_faltante",
    ]
    present = [c for c in names if c in df.columns]
    return pd.DataFrame(
        [{"flag": c, "n": int(df[c].fillna(0).astype(float).sum())} for c in present]
    )


def resumen_fuentes(n0: Path) -> list[dict]:
    rows = []
    for name, desc in ARCHIVOS_N0.items():
        p = n0 / name
        rows.append(
            {
                "archivo": name,
                "descripcion": desc,
                "filas": count_csv_rows(p),
                "existe": p.exists(),
            }
        )
    return rows


def resumen_cargos(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("cargo", as_index=False)
        .agg(filas=("seccion", "count"), anios=("anio", "nunique"))
        .sort_values("filas", ascending=False)
    )
