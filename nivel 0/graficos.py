"""Graficos matplotlib para auditoria N0."""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

COLORS = {
    "MC": "#EA580C",
    "MORENA_4T": "#9F2241",
    "PAN": "#2563EB",
    "PRI": "#DC2626",
    "OTROS": "#6B7280",
    "mc": "#EA580C",
    "m4t": "#9F2241",
    "pan": "#2563EB",
    "pri": "#DC2626",
    "otros": "#6B7280",
}


def fig_evolucion_pct(agg: pd.DataFrame, title: str) -> plt.Figure:
    fig, ax1 = plt.subplots(figsize=(10, 5))
    years = agg["anio"]
    w = 0.35
    ax1.bar(years - w / 2, agg["pct_mc"], width=w, label="MC %", color=COLORS["MC"])
    ax1.bar(years + w / 2, agg["pct_4t"], width=w, label="MORENA 4T %", color=COLORS["MORENA_4T"])
    ax1.set_ylabel("% sobre votos validos")
    ax1.set_xlabel("Anio")
    ax1.set_title(title)
    ax1.legend(loc="upper left")
    ax2 = ax1.twinx()
    ax2.plot(years, agg["secciones"], "o-", color="#334155", label="Secciones")
    ax2.set_ylabel("Secciones con dato")
    fig.tight_layout()
    return fig


def fig_votos_absolutos(agg: pd.DataFrame, title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = None
    for col, label in [
        ("mc", "MC"),
        ("m4t", "MORENA 4T"),
        ("pan", "PAN"),
        ("pri", "PRI"),
        ("otros", "Otros"),
    ]:
        vals = agg[col].values
        ax.bar(agg["anio"], vals, bottom=bottom, label=label, color=COLORS[col])
        bottom = vals if bottom is None else bottom + vals
    ax.set_title(title)
    ax.set_xlabel("Anio")
    ax.set_ylabel("Votos validos (suma distrito)")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    return fig


def fig_votos_porcentaje(agg: pd.DataFrame, title: str) -> plt.Figure:
    """Barras apiladas al 100%: composición de votos válidos por bloque (eje desde 0%)."""
    fig, ax = plt.subplots(figsize=(10, 5))
    tot = agg["validos"].replace(0, pd.NA)
    bottom = None
    for col, label in [
        ("mc", "MC"),
        ("m4t", "MORENA 4T"),
        ("pan", "PAN"),
        ("pri", "PRI"),
        ("otros", "Otros"),
    ]:
        pct = (agg[col] / tot * 100).fillna(0).values
        ax.bar(
            agg["anio"],
            pct,
            bottom=bottom,
            label=label,
            color=COLORS[col],
            edgecolor="white",
            linewidth=0.4,
        )
        bottom = pct if bottom is None else bottom + pct
    ax.set_title(title)
    ax.set_xlabel("Anio")
    ax.set_ylabel("% de votos validos (cada barra = 100%)")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    return fig


def fig_ganador_2024(counts: pd.Series, title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 6))
    labels = counts.index.tolist()
    colors = [COLORS.get(l, "#94A3B8") for l in labels]
    ax.pie(counts.values, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
    ax.set_title(title)
    fig.tight_layout()
    return fig


LABELS_FLAG = {
    "flag_outlier": "Dato raro (revisar acta)",
    "flag_datos_incompletos": "Sin votos validos",
    "flag_coalicion_compleja": "Boleta/coalicion dificil de leer",
    "flag_lista_nominal_faltante": "No venia padron (lista nominal)",
}


def fig_flags(flags: pd.DataFrame, title: str, total_filas: int) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    df = flags.copy()
    df["etiqueta"] = df["flag"].map(lambda f: LABELS_FLAG.get(f, f.replace("flag_", "")))
    df = df.sort_values("n", ascending=True)
    bars = ax.barh(df["etiqueta"], df["n"], color="#DC2626", alpha=0.75)
    ax.set_xlabel(f"Cuantas veces aparece (de {total_filas:,} filas sección-año en total)")
    ax.set_title(title + "\n(No es 'votos mal'; son recordatorios en el archivo)", fontsize=11)
    xmax = max(df["n"].max(), 1)
    ax.set_xlim(0, xmax * 1.35)
    for bar, n in zip(bars, df["n"]):
        pct = 100 * n / total_filas if total_filas else 0
        ax.text(
            bar.get_width() + xmax * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{int(n):,}  ({pct:.0f}%)",
            va="center",
            fontsize=9,
            color="#334155",
        )
    fig.tight_layout()
    return fig


def fig_secciones_por_anio(inst: pd.DataFrame, vig: pd.DataFrame, title: str) -> plt.Figure:
    a = inst.groupby("anio")["seccion"].nunique()
    b = vig.groupby("anio")["seccion"].nunique()
    anios = sorted(set(a.index) | set(b.index))
    fig, ax = plt.subplots(figsize=(10, 4))
    x = range(len(anios))
    w = 0.35
    ax.bar([i - w / 2 for i in x], [a.get(y, 0) for y in anios], width=w, label="Institucional (acta)", color="#64748B")
    ax.bar([i + w / 2 for i in x], [b.get(y, 0) for y in anios], width=w, label="Vigente (interpolada)", color="#1090D0")
    ax.set_xticks(list(x))
    ax.set_xticklabels([str(int(y)) for y in anios])
    ax.set_ylabel("Secciones unicas")
    ax.set_xlabel("Anio")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig


def save(fig: plt.Figure, path, *, nota: str | None = None) -> None:
    if nota:
        fig.text(0.5, 0.02, nota, ha="center", va="bottom", fontsize=8, color="#475569", wrap=True)
        fig.subplots_adjust(bottom=0.14)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
