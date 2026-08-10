"""Enlace entre informe auditoria/salida y PDF Nivel 0 (§0.6–0.8, §0.7 entregables)."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import pandas as pd

from metricas import count_csv_rows

# Todos los artefactos N0/N0.5 en analisis/nivel0/ (copia a salida/entregables_n0/)
ARCHIVOS_ENTREGABLES: list[tuple[str, str]] = [
    ("README.md", "Guía de entregables N0"),
    ("base_maestra_largo.csv", "Base maestra formato largo"),
    ("base_seccion_anio.csv", "Resumen sección×año×cargo"),
    ("historial_partidos.csv", "Registro largo por partido (limpieza)"),
    ("base_seccion_anio_interpolada.csv", "Serie remapeada N0.5"),
    ("interpolacion_proporciones.csv", "Proporciones interpolación (auditable)"),
    ("catalogo_secciones.csv", "Catálogo territorial"),
    ("catalogo_elecciones.csv", "Elecciones comparables"),
    ("catalogo_coalicion.csv", "Catálogo de coaliciones"),
    ("homologacion_partidos_bloques.csv", "Homologación partido→bloque"),
    ("voto_combinado_coalicion.csv", "Voto combinado coalición"),
    ("registro_satelites.csv", "Partidos satélite"),
    ("resumen_partidos_estatal.csv", "Resumen estatal por partido"),
    ("inventario_fuentes.csv", "Inventario de fuentes"),
    ("reporte_anomalias.csv", "Anomalías y outliers (detalle)"),
    ("reporte_calidad.md", "Control calidad §0.6 + checklist §0.8"),
    ("diccionario_datos.md", "Diccionario de variables"),
    ("bitacora_metodologica.md", "Bitácora metodológica"),
    (
        "vistas_demarcacion/vw_resultados_institucionales_distrito.csv",
        "Vista demarcación · resultados institucionales",
    ),
    (
        "vistas_demarcacion/vw_nivel1_demarcacion.csv",
        "Vista demarcación · nivel 1",
    ),
]

CARPETA_ENTREGABLES = "entregables_n0"

# PDF Nivel 0 §0.7 → agrupación para tabla del informe
ENTREGABLES_PDF: list[tuple[str, list[str]]] = [
    ("Base maestra electoral limpia", ["base_maestra_largo.csv", "base_seccion_anio.csv"]),
    ("Historial y limpieza", ["historial_partidos.csv"]),
    ("Diccionario de datos", ["diccionario_datos.md"]),
    ("Catálogo de elecciones comparables", ["catalogo_elecciones.csv"]),
    ("Catálogo territorial y coaliciones", ["catalogo_secciones.csv", "catalogo_coalicion.csv"]),
    ("Tabla de homologación partidaria", ["homologacion_partidos_bloques.csv", "voto_combinado_coalicion.csv"]),
    ("Reporte de calidad de datos", ["reporte_calidad.md", "reporte_anomalias.csv"]),
    ("Inventario de fuentes", ["inventario_fuentes.csv"]),
    ("Bitácora metodológica", ["bitacora_metodologica.md"]),
    ("Serie remapeada (N0.5)", ["base_seccion_anio_interpolada.csv", "interpolacion_proporciones.csv"]),
    ("Auxiliares pipeline", ["registro_satelites.csv", "resumen_partidos_estatal.csv"]),
    ("Vistas demarcación", ["vistas_demarcacion/vw_resultados_institucionales_distrito.csv", "vistas_demarcacion/vw_nivel1_demarcacion.csv"]),
]

PDF_INSTRUCCIONES = (
    "analisis/Instrucciones v1/Instrucciones v1/Nivel 0.pdf"
)


def _filas_o_tamano(path: Path) -> str:
    if path.suffix.lower() == ".csv":
        n = count_csv_rows(path)
        return f"{n:,} filas" if n >= 0 else "?"
    kb = path.stat().st_size / 1024
    return f"{kb:.1f} KB"


def copiar_entregables_n0(n0: Path, salida: Path) -> pd.DataFrame:
    """Copia todos los entregables N0 a salida/entregables_n0/ y devuelve manifiesto."""
    dest_root = salida / CARPETA_ENTREGABLES
    dest_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []

    for rel, descripcion in ARCHIVOS_ENTREGABLES:
        src = n0 / rel
        dst = dest_root / rel
        if not src.is_file():
            rows.append(
                {
                    "archivo": rel,
                    "descripcion": descripcion,
                    "copia_local": "",
                    "detalle": "FALTA en analisis/nivel0",
                    "estado": "Falta",
                }
            )
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        link = f"{CARPETA_ENTREGABLES}/{rel.replace(chr(92), '/')}"
        rows.append(
            {
                "archivo": rel,
                "descripcion": descripcion,
                "copia_local": link,
                "detalle": _filas_o_tamano(src),
                "estado": "Copiado",
            }
        )

    manifest = pd.DataFrame(rows)
    manifest.to_csv(salida / "entregables_n0_manifest.csv", index=False, encoding="utf-8-sig")
    return manifest


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
    """Copia reporte_calidad.md también en raíz de salida (atajo) si existe en N0."""
    src = n0 / "reporte_calidad.md"
    if not src.exists():
        return None
    dst = salida / "control_calidad_jalisco_n0.md"
    shutil.copy2(src, dst)
    return dst


def texto_marco_pdf() -> str:
    return (
        "Este informe combina narrativa del Distrito Local 4 (diputado) con el cumplimiento del PDF "
        f"«Nivel 0» ({PDF_INSTRUCCIONES}). Todos los entregables del pipeline "
        "(base maestra, catálogos, reportes, bitácora, N0.5) se copian a "
        f"salida/{CARPETA_ENTREGABLES}/ al ejecutar la auditoría. "
        "Los colores estratégicos del PDF §0.1 corresponden al Nivel 1+."
    )
