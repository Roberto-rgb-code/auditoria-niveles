"""Cumplimiento auditoría N0 vs Instrucciones v3 (00 Marco + 01 Cimientos N0-N0.5)."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import pandas as pd

from metricas import count_csv_rows

INSTRUCCIONES_V3_SUBDIR = Path("analisis") / "Instrucciones v3" / "Instrucciones v3"
CARPETA_ENTREGABLES = "entregables_n0"
CARPETA_NORMATIVA = "instrucciones_v3"

ARCHIVOS_ENTREGABLES: list[tuple[str, str]] = [
    ("README.md", "Guía de entregables N0"),
    ("base_maestra_largo.csv", "Base maestra / hecho (pre o post re-ingesta D7)"),
    ("base_seccion_anio.csv", "Agregado sección×año×cargo (bloques, banderas)"),
    ("historial_partidos.csv", "Registro largo por partido"),
    ("catalogo_coalicion.csv", "Catálogo coalición → bloque (capa interpretación)"),
    ("registro_satelites.csv", "Satélites PVEM, PT, etc. (v3)"),
    ("homologacion_partidos_bloques.csv", "Homologación partido→bloque"),
    ("voto_combinado_coalicion.csv", "Voto combinado coalición"),
    ("catalogo_secciones.csv", "Territorio + distrito_local_vigente (Adenda A)"),
    ("catalogo_elecciones.csv", "Elecciones comparables"),
    ("inventario_fuentes.csv", "Inventario de fuentes"),
    ("reporte_anomalias.csv", "Anomalías detalladas"),
    ("reporte_calidad.md", "Control calidad pipeline (complemento)"),
    ("diccionario_datos.md", "Diccionario de variables"),
    ("bitacora_metodologica.md", "Bitácora metodológica"),
    ("base_seccion_anio_interpolada.csv", "N0.5 · base interpolada cartografía 2024"),
    ("interpolacion_proporciones.csv", "N0.5 · proporciones dasimétricas auditables"),
    (
        "vistas_demarcacion/vw_resultados_institucionales_distrito.csv",
        "Vista demarcación institucional",
    ),
    (
        "vistas_demarcacion/vw_nivel1_demarcacion.csv",
        "Vista demarcación N1",
    ),
]

# Instrucciones v3 §2.3 — entregables de cimientos
ENTREGABLES_V3: list[tuple[str, list[str]]] = [
    ("Hecho atómico / bases", ["base_maestra_largo.csv", "base_seccion_anio.csv"]),
    ("Interpretación coalición y satélites", ["catalogo_coalicion.csv", "registro_satelites.csv"]),
    ("Homologación y voto combinado", ["homologacion_partidos_bloques.csv", "voto_combinado_coalicion.csv"]),
    ("Catálogos territorio y elecciones", ["catalogo_secciones.csv", "catalogo_elecciones.csv"]),
    ("N0.5 interpolación + proporciones", ["base_seccion_anio_interpolada.csv", "interpolacion_proporciones.csv"]),
    ("Calidad, anomalías, fuentes", ["reporte_calidad.md", "reporte_anomalias.csv", "inventario_fuentes.csv"]),
    ("Documentación", ["diccionario_datos.md", "bitacora_metodologica.md"]),
]


def instrucciones_v3_dir(repo: Path) -> Path:
    return repo / INSTRUCCIONES_V3_SUBDIR


def rutas_normativas_v3(repo: Path) -> tuple[Path | None, Path | None]:
    base = instrucciones_v3_dir(repo)
    if not base.is_dir():
        return None, None
    marco = next(iter(sorted(base.glob("00*Marco*v3.md"))), None)
    cimientos = next(iter(sorted(base.glob("01*Cimientos*v3.md"))), None)
    return marco, cimientos


def rutas_normativas_texto(repo: Path) -> tuple[str, str]:
    marco, cim = rutas_normativas_v3(repo)
    rel = INSTRUCCIONES_V3_SUBDIR.as_posix()
    return (
        f"{rel}/{marco.name}" if marco else f"{rel}/00 — Marco general v3.md (no encontrado)",
        f"{rel}/{cim.name}" if cim else f"{rel}/01 — Cimientos N0-N0.5 v3.md (no encontrado)",
    )


def _filas_o_tamano(path: Path) -> str:
    if path.suffix.lower() == ".csv":
        n = count_csv_rows(path)
        return f"{n:,} filas" if n >= 0 else "?"
    kb = path.stat().st_size / 1024
    return f"{kb:.1f} KB"


def copiar_instrucciones_v3(repo: Path, salida: Path) -> list[str]:
    marco, cim = rutas_normativas_v3(repo)
    dest = salida / CARPETA_NORMATIVA
    dest.mkdir(parents=True, exist_ok=True)
    links: list[str] = []
    for src in (marco, cim):
        if src and src.is_file():
            shutil.copy2(src, dest / src.name)
            links.append(f"{CARPETA_NORMATIVA}/{src.name}")
    return links


def copiar_entregables_n0(n0: Path, salida: Path) -> pd.DataFrame:
    dest_root = salida / CARPETA_ENTREGABLES
    dest_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []

    for rel, descripcion in ARCHIVOS_ENTREGABLES:
        src = n0 / rel
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
        dst = dest_root / rel
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


def leer_control_pipeline(n0: Path) -> dict:
    """Reporte legacy de electoral_nivel0 (complemento, no normativa v3)."""
    path = n0 / "reporte_calidad.md"
    out: dict = {"existe": path.exists(), "qa": [], "checklist": [], "nota": ""}
    if not path.exists():
        out["nota"] = "Sin reporte_calidad.md del pipeline."
        return out
    text = path.read_text(encoding="utf-8")
    if "## Pruebas de control de calidad" in text:
        block = text.split("## Pruebas de control de calidad", 1)[1].split("## Cobertura", 1)[0]
        out["qa"] = _parse_md_table(block.splitlines())
    if "## Checklist ejecutivo" in text:
        block = text.split("## Checklist ejecutivo", 1)[1].split("##", 1)[0]
        for line in block.splitlines():
            if line.strip().startswith("- **"):
                out["checklist"].append(re.sub(r"^-\s*", "", line.strip()))
    m = re.search(r"_Generado:\s*(.+?)_", text)
    if m:
        out["nota"] = f"Pipeline N0 generado: {m.group(1).strip()}"
    return out


def tabla_entregables(n0: Path) -> pd.DataFrame:
    rows = []
    for nombre, archivos in ENTREGABLES_V3:
        detalle = []
        ok = True
        for name in archivos:
            p = n0 / name
            if p.exists():
                detalle.append(
                    f"{name} ({count_csv_rows(p):,} filas)"
                    if name.endswith(".csv")
                    else name
                )
            else:
                ok = False
                detalle.append(f"{name} (FALTA)")
        rows.append(
            {
                "entregable_v3_2_3": nombre,
                "archivos_en_repo": "; ".join(detalle),
                "estado": "Presente" if ok else "Incompleto",
            }
        )
    return pd.DataFrame(rows)


def _tiene_tres_cantidades(n0: Path) -> bool:
    p = n0 / "base_maestra_largo.csv"
    if not p.exists():
        return False
    cols = pd.read_csv(p, nrows=0, encoding="utf-8-sig").columns
    need = {"voto_marca_unica", "voto_combinado_coalicion", "voto_legal_distribuido"}
    return need.issubset(set(cols))


def pruebas_normativas_v3(repo: Path, n0: Path, d4_vig: pd.DataFrame) -> pd.DataFrame:
    """Checklist operativo según Instrucciones v3 §1.5 y §2.1 (sobre artefactos actuales)."""
    marco, cim = rutas_normativas_v3(repo)
    tres = _tiene_tres_cantidades(n0)
    dup_d4 = int(d4_vig.duplicated(subset=["seccion", "anio"], keep=False).sum())
    interp = n0 / "base_seccion_anio_interpolada.csv"
    dup_interp = 0
    if interp.exists():
        df_i = pd.read_csv(interp, usecols=["seccion", "anio", "cargo"], encoding="utf-8-sig", low_memory=False)
        dup_interp = int(df_i.duplicated(subset=["seccion", "anio", "cargo"], keep=False).sum())

    rows = [
        (
            "Normativa v3 disponible",
            "00 Marco + 01 Cimientos en repo",
            "OK" if marco and cim else "FALTA carpeta Instrucciones v3",
        ),
        (
            "D7 · tres cantidades",
            "voto_marca_unica, voto_combinado_coalicion, voto_legal_distribuido",
            "OK" if tres else "PENDIENTE (re-ingesta Excel INE; base actual colapsada)",
        ),
        (
            "Unicidad D4 vigente diputado",
            "Una fila sección+año",
            "OK" if dup_d4 == 0 else f"REVISAR ({dup_d4} duplicados)",
        ),
        (
            "N0.5 · duplicados sección+año+cargo",
            "Prueba de rechazo v3 §2.1",
            "OK" if dup_interp == 0 else f"REVISAR ({dup_interp})",
        ),
        (
            "Outliers no borrados",
            "flag_outlier documentado (v3 §1.4)",
            f"{int(d4_vig.get('flag_outlier', pd.Series(0)).fillna(0).sum())} fila(s) D4",
        ),
        (
            "Secciones D4 2024",
            "Cartografía vigente en serie campaña",
            f"{d4_vig.loc[d4_vig['anio'] == 2024, 'seccion'].nunique()} secciones",
        ),
    ]
    return pd.DataFrame(rows, columns=["prueba", "criterio", "resultado"])


def control_d4_vigente(df: pd.DataFrame) -> pd.DataFrame:
    dup = df.duplicated(subset=["seccion", "anio"], keep=False).sum()
    n = len(df)
    outlier = int(df.get("flag_outlier", pd.Series(0)).fillna(0).astype(float).sum())
    incompletos = int(df.get("flag_datos_incompletos", pd.Series(0)).fillna(0).astype(float).sum())
    rows = [
        ("Secciones únicas (D4 vigente)", "Una fila por sección+año (diputado)", "OK" if dup == 0 else f"REVISAR ({dup})"),
        ("Filas D4 vigente", "Gráficos 1–2b", f"{n:,} filas"),
        ("Outliers marcados", "flag_outlier = 1", f"{outlier} fila(s)"),
        ("Datos incompletos", "flag_datos_incompletos = 1", f"{incompletos} fila(s)"),
    ]
    return pd.DataFrame(rows, columns=["prueba", "criterio", "resultado"])


def checklist_v3(repo: Path, n0: Path, entregables: pd.DataFrame) -> list[str]:
    marco, cim = rutas_normativas_v3(repo)
    n_ok = int((entregables["estado"] == "Presente").sum()) if not entregables.empty else 0
    n_tot = len(entregables)
    return [
        f"**Normativa:** {marco.name if marco else '?'} + {cim.name if cim else '?'} (Instrucciones v3).",
        "**D7 (vital):** re-ingesta desde Excel INE con tres cantidades por emblema; sin eso no hay rastreo de satélites 2027.",
        f"**Entregables §2.3:** {n_ok}/{n_tot} grupos presentes en `analisis/nivel0/`.",
        "**N0.5:** interpolación dasimétrica → `base_seccion_anio_interpolada.csv` + `interpolacion_proporciones.csv`.",
        "**Demarcación:** doble corte institucional vs `distrito_local_vigente` (Adenda A / D5 en Marco v3).",
        "**Colores estratégicos (N3+):** no aplican en esta auditoría de cimientos; ver Marco v3 §1 D3.",
    ]


def copiar_reporte_calidad(n0: Path, salida: Path) -> Path | None:
    src = n0 / "reporte_calidad.md"
    if not src.exists():
        return None
    dst = salida / "control_calidad_jalisco_n0.md"
    shutil.copy2(src, dst)
    return dst


def texto_marco_v3(repo: Path) -> str:
    marco_t, cim_t = rutas_normativas_texto(repo)
    return (
        "Auditoría alineada a **Instrucciones v3** (normativa vigente): "
        f"«{marco_t}» y «{cim_t}». "
        "Consolida N0/N0.5 aprobados; reemplaza el PDF Nivel 0 v1. "
        f"Copias locales: `salida/{CARPETA_NORMATIVA}/` (textos normativos) y "
        f"`salida/{CARPETA_ENTREGABLES}/` (artefactos del pipeline). "
        "La narrativa D4 usa la serie interpolada; el cumplimiento D7 (tres cantidades) "
        "se reporta explícitamente hasta completar re-ingesta."
    )
