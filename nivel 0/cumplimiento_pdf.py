"""Enlace entre informe auditoria/salida y PDF Nivel 0 (§0.6–0.8, §0.7 entregables)."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import pandas as pd

from metricas import count_csv_rows

# PDF Nivel 0 §0.7 → archivos en analisis/nivel0/ (generados por electoral_nivel0.py)
ENTREGABLES_PDF: list[tuple[str, list[str]]] = [
    ("Base maestra electoral limpia", ["base_maestra_largo.csv", "base_seccion_anio.csv"]),
    ("Diccionario de datos", ["diccionario_datos.md"]),
    ("Catálogo de elecciones comparables", ["catalogo_elecciones.csv"]),
    ("Tabla de homologación partidaria", ["homologacion_partidos_bloques.csv"]),
    ("Reporte de calidad de datos", ["reporte_calidad.md", "reporte_anomalias.csv"]),
    ("Inventario de fuentes", ["inventario_fuentes.csv"]),
    ("Catálogo territorial", ["catalogo_secciones.csv"]),
    ("Bitácora metodológica", ["bitacora_metodologica.md"]),
    ("Serie remapeada (N0.5)", ["base_seccion_anio_interpolada.csv"]),
]

PDF_INSTRUCCIONES = (
    "analisis/Instrucciones v1/Instrucciones v1/Nivel 0.pdf"
)


def _parse_md_table(lines: list[str]) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in lines:
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---"):
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 3 and parts[0].lower() != "prueba":
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def leer_control_calidad(n0: Path) -> dict:
    """Lee reporte_calidad.md del pipeline N0 (tabla §0.6 y checklist §0.8)."""
    path = n0 / "reporte_calidad.md"
    out: dict = {
        "existe": path.exists(),
        "qa": [],
        "checklist": [],
        "nota": "",
    }
    if not path.exists():
        out["nota"] = "No hay reporte_calidad.md. Ejecuta scripts/electoral_nivel0.py."
        return out

    text = path.read_text(encoding="utf-8")
    if "## Pruebas de control de calidad" in text:
        block = text.split("## Pruebas de control de calidad", 1)[1]
        block = block.split("## Cobertura", 1)[0]
        out["qa"] = _parse_md_table(block.splitlines())

    if "## Checklist ejecutivo" in text:
        block = text.split("## Checklist ejecutivo", 1)[1]
        block = block.split("##", 1)[0]
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("- **"):
                out["checklist"].append(re.sub(r"^-\s*", "", line))

    m = re.search(r"_Generado:\s*(.+?)_", text)
    if m:
        out["nota"] = f"Reporte pipeline generado: {m.group(1).strip()}"
    return out


def tabla_entregables(n0: Path) -> pd.DataFrame:
    rows = []
    for nombre, archivos in ENTREGABLES_PDF:
        detalle = []
        ok = True
        for name in archivos:
            p = n0 / name
            if p.exists():
                if name.endswith(".csv"):
                    detalle.append(f"{name} ({count_csv_rows(p):,} filas)")
                else:
                    detalle.append(name)
            else:
                ok = False
                detalle.append(f"{name} (FALTA)")
        rows.append(
            {
                "entregable_pdf_0_7": nombre,
                "archivos_en_repo": "; ".join(detalle),
                "estado": "Presente" if ok else "Incompleto",
            }
        )
    return pd.DataFrame(rows)


def control_d4_vigente(df: pd.DataFrame) -> pd.DataFrame:
    """Pruebas §0.6 aplicadas al corte D4 vigente (diputado) usado en gráficos."""
    dup = df.duplicated(subset=["seccion", "anio"], keep=False).sum()
    n = len(df)
    outlier = int(df.get("flag_outlier", pd.Series(0)).fillna(0).astype(float).sum())
    incompletos = int(df.get("flag_datos_incompletos", pd.Series(0)).fillna(0).astype(float).sum())
    rows = [
        (
            "Secciones únicas (D4 vigente)",
            "Una fila por sección+año (diputado)",
            "OK" if dup == 0 else f"REVISAR ({dup} duplicados)",
        ),
        (
            "Filas D4 vigente",
            "Serie usada en gráficos 1–5",
            f"{n:,} filas",
        ),
        (
            "Outliers marcados",
            "flag_outlier = 1 (PDF §0.10)",
            f"{outlier} fila(s)",
        ),
        (
            "Datos incompletos",
            "flag_datos_incompletos = 1",
            f"{incompletos} fila(s)",
        ),
        (
            "Secciones 2024",
            "Cartografía D4 completa (167)",
            f"{df.loc[df['anio'] == 2024, 'seccion'].nunique()} secciones",
        ),
    ]
    return pd.DataFrame(rows, columns=["prueba", "criterio", "resultado"])


def copiar_reporte_calidad(n0: Path, salida: Path) -> Path | None:
    src = n0 / "reporte_calidad.md"
    if not src.exists():
        return None
    dst = salida / "control_calidad_jalisco_n0.md"
    shutil.copy2(src, dst)
    return dst


def texto_marco_pdf() -> str:
    return (
        "Este informe en salida/ combina tres capas: (1) gráficos y narrativa del Distrito Local 4 "
        "(diputado) para campaña; (2) entregables y pruebas del PDF "
        f"«Nivel 0» ({PDF_INSTRUCCIONES}) ya materializados en analisis/nivel0/ por electoral_nivel0.py; "
        "(3) pruebas adicionales solo sobre el subconjunto D4 vigente que alimenta los gráficos. "
        "Los colores estratégicos (azul/dorado/naranja…) del PDF §0.1 corresponden al Nivel 1+, no a esta auditoría."
    )
