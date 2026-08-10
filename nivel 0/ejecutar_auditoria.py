#!/usr/bin/env python3
"""
Auditoria Nivel 0 — Python local.

Uso (desde la raiz miguel-gis):
  python "auditoria/nivel 0/ejecutar_auditoria.py"

Salida en auditoria/nivel 0/salida/  (PNG, HTML, PDF, CSV)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
SALIDA = HERE / "salida"


def find_miguel_gis_root() -> Path:
    env = os.environ.get("MIGUEL_GIS_ROOT")
    if env:
        p = Path(env)
        if (p / "analisis" / "nivel0").is_dir():
            return p
        raise SystemExit(f"MIGUEL_GIS_ROOT no tiene analisis/nivel0: {p}")
    for base in (HERE.parents[1], HERE.parents[2], HERE.parent):
        if (base / "analisis" / "nivel0").is_dir():
            return base
    raise SystemExit(
        "No se encontro analisis/nivel0. Clona miguel-gis o define MIGUEL_GIS_ROOT "
        "apuntando a la raiz del proyecto con los CSV."
    )


REPO = find_miguel_gis_root()

sys.path.insert(0, str(HERE))

import graficos as g
import metricas as m
from interpretaciones import (
    explicacion_ganador_2024,
    explicacion_tabla_numeros,
    guia_rapida,
    notas_figuras,
)
from reporte import build_html, build_pdf, narrativa


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    n0 = m.nivel0_dir(REPO)
    if not n0.is_dir():
        print(f"No existe {n0}. Genera N0 con scripts/electoral_nivel0.py")
        sys.exit(1)

    print("Auditoria Nivel 0")
    print("Repo:", REPO)
    print("Salida:", SALIDA)
    print()

    fuentes = m.resumen_fuentes(n0)
    for f in fuentes:
        st = "OK" if f["existe"] else "FALTA"
        print(f"  [{st}] {f['archivo']}: {f['filas']:,} filas")

    df_acta = m.load_seccion_anio(n0)
    df_interp = m.load_interpolada(n0)
    cargos = m.resumen_cargos(df_acta)

    d4_inst = m.filter_d4(df_acta, interpolada=False)
    d4_vig = m.filter_d4(df_interp, interpolada=True)
    agg = m.agg_historico_d4(d4_vig)
    flags = m.quality_flags(d4_vig)
    gan = m.ganador_2024(d4_vig)

    agg.to_csv(SALIDA / "tabla_agregada_d4_vigente.csv", index=False)
    flags.to_csv(SALIDA / "banderas_calidad.csv", index=False)

    titulo = "Auditoria Nivel 0 · Distrito Local 4 · Diputacion"
    g.save(
        g.fig_evolucion_pct(agg, titulo + " · % MC vs 4T"),
        SALIDA / "01_evolucion_pct_mc_4t.png",
        nota="Barras = % de votos del distrito; linea = secciones contadas.",
    )
    g.save(
        g.fig_votos_absolutos(agg, "Votos validos por bloque · D4 vigente"),
        SALIDA / "02_votos_absolutos.png",
        nota="Altura total = votos validos sumados; colores = cada partido/bloque.",
    )
    g.save(
        g.fig_ganador_2024(gan, "Ganador por seccion · 2024 · D4 vigente"),
        SALIDA / "03_ganador_2024.png",
        nota="Rebanadas = secciones ganadas (no % de votos del estado).",
    )
    g.save(
        g.fig_flags(flags, "Grafico 4 · Avisos de calidad (no es resultado electoral)", len(d4_vig)),
        SALIDA / "04_banderas_calidad.png",
        nota=f"No cuenta votos: revisa {len(d4_vig):,} filas sección-año. Ver nota amarilla en informe.",
    )
    g.save(
        g.fig_secciones_por_anio(d4_inst, d4_vig, "Secciones con dato · institucional vs vigente"),
        SALIDA / "05_secciones_inst_vs_vigente.png",
        nota="Azul = mapa D4 de hoy; gris = acta historica del año.",
    )

    notas = notas_figuras(agg, gan, flags, len(d4_inst), len(d4_vig))
    titulos = {
        "01_evolucion_pct_mc_4t.png": "Grafico 1 · Evolucion MC vs MORENA-4T (porcentajes)",
        "02_votos_absolutos.png": "Grafico 2 · Votos totales por bloque (numeros grandes)",
        "03_ganador_2024.png": "Grafico 3 · Quien gano cada seccion en 2024",
        "04_banderas_calidad.png": "Grafico 4 · Avisos de calidad (NO es quien gano)",
        "05_secciones_inst_vs_vigente.png": "Grafico 5 · Cuantas secciones entran por año",
    }
    imagenes = [
        (titulos["01_evolucion_pct_mc_4t.png"], SALIDA / "01_evolucion_pct_mc_4t.png", notas["01_evolucion_pct_mc_4t.png"]),
        (titulos["02_votos_absolutos.png"], SALIDA / "02_votos_absolutos.png", notas["02_votos_absolutos.png"]),
        (titulos["03_ganador_2024.png"], SALIDA / "03_ganador_2024.png", notas["03_ganador_2024.png"]),
        (titulos["04_banderas_calidad.png"], SALIDA / "04_banderas_calidad.png", notas["04_banderas_calidad.png"]),
        (
            titulos["05_secciones_inst_vs_vigente.png"],
            SALIDA / "05_secciones_inst_vs_vigente.png",
            notas["05_secciones_inst_vs_vigente.png"],
        ),
    ]

    guia = guia_rapida(agg, gan, flags)
    exp_tabla = explicacion_tabla_numeros()
    exp_gan = explicacion_ganador_2024(gan)

    secciones = narrativa(
        fuentes=fuentes,
        n_acta=len(df_acta),
        n_interp=len(df_interp),
        n_inst_d4=len(d4_inst),
        n_vig_d4=len(d4_vig),
        cargos=cargos,
    )

    html_path = SALIDA / "informe_auditoria_n0.html"
    build_html(
        html_path,
        titulo=titulo,
        secciones=secciones,
        guia=guia,
        explicacion_tabla=exp_tabla,
        explicacion_ganador=exp_gan,
        agg=agg,
        flags=flags,
        ganador=gan,
        imagenes=imagenes,
    )

    pdf_path = SALIDA / "informe_auditoria_n0.pdf"
    ok_pdf = build_pdf(
        pdf_path,
        titulo=titulo,
        secciones=secciones,
        guia=guia,
        explicacion_tabla=exp_tabla,
        explicacion_ganador=exp_gan,
        agg=agg,
        imagenes=imagenes,
    )

    print()
    print("=== Resumen D4 vigente (diputado) ===")
    show = agg[["anio", "secciones", "validos", "pct_mc", "pct_4t", "outliers"]].copy()
    show["validos"] = show["validos"].map(lambda x: f"{int(x):,}")
    print(show.to_string(index=False))
    print()
    print("Ganador 2024:")
    print(gan.to_string())
    print()
    print("Archivos generados:")
    for p in sorted(SALIDA.iterdir()):
        print(" ", p.name)
    if not ok_pdf:
        print()
        print("PDF no generado (instala reportlab): pip install reportlab")
    else:
        print()
        print("Abre informe_auditoria_n0.html o informe_auditoria_n0.pdf en salida/")


if __name__ == "__main__":
    main()
