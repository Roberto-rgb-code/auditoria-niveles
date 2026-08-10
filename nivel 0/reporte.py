"""Informe HTML y PDF de auditoria N0."""
from __future__ import annotations

import html
from datetime import date
from pathlib import Path

import pandas as pd

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def _esc(s: str) -> str:
    return html.escape(str(s))


def _inline_md_bold(text: str) -> str:
    """Convierte **negrita** a <strong> tras escapar HTML."""
    out: list[str] = []
    i = 0
    while i < len(text):
        start = text.find("**", i)
        if start == -1:
            out.append(_esc(text[i:]))
            break
        out.append(_esc(text[i:start]))
        end = text.find("**", start + 2)
        if end == -1:
            out.append(_esc(text[start:]))
            break
        out.append(f"<strong>{_esc(text[start + 2 : end])}</strong>")
        i = end + 2
    return "".join(out)


def _nota_html(nota: str) -> str:
    blocks = []
    for block in nota.strip().split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("QUE ES:"):
            blocks.append(f"<p><strong>Que es:</strong> {_esc(block[7:].strip())}</p>")
        elif block.startswith("COMO LEERLO:"):
            blocks.append(f"<p><strong>Como leerlo:</strong> {_esc(block[13:].strip())}</p>")
        elif block.startswith("EN PLANO:"):
            blocks.append(f"<p><strong>En plano:</strong> {_esc(block[9:].strip())}</p>")
        elif block.startswith("NO CONFUNDIR:"):
            blocks.append(f"<p><strong>No confundir:</strong> {_esc(block[13:].strip())}</p>")
        elif block.startswith("LA LINEA GRIS:"):
            blocks.append(f"<p><strong>La linea gris:</strong> {_esc(block[14:].strip())}</p>")
        elif block.startswith("PARA UN LECTOR NO TECNICO:"):
            blocks.append(f"<p><strong>En sencillo:</strong> {_esc(block[28:].strip())}</p>")
        else:
            blocks.append(f"<p>{_esc(block)}</p>")
    return '  <div class="nota">\n    ' + "\n    ".join(blocks) + "\n  </div>\n"


def _bloque_cumplimiento_html(
    *,
    marco_pdf: str,
    entregables: pd.DataFrame | None,
    qa_v3: pd.DataFrame | None,
    qa_jalisco: list[tuple[str, str, str]] | None,
    qa_d4: pd.DataFrame | None,
    checklist: list[str] | None,
    nota_calidad: str,
    manifest_entregables: pd.DataFrame | None = None,
    normativa_links: list[str] | None = None,
) -> list[str]:
    if not marco_pdf:
        return []
    parts = [
        '  <h2 id="cumplimiento-v3">Cumplimiento Instrucciones v3 (N0 / N0.5)</h2>\n',
        '  <div class="pdf-cumplimiento">\n',
        f"    <p>{_inline_md_bold(marco_pdf)}</p>\n",
        "    <p class=\"meta\">Normativa: "
        "<code>analisis/Instrucciones v3/Instrucciones v3/</code> "
        "(00 Marco general + 01 Cimientos N0-N0.5). "
        f"Copias: <code>instrucciones_v3/</code>, <code>entregables_n0/</code>, "
        "manifiesto <code>entregables_n0_manifest.csv</code>.</p>\n",
        "  </div>\n",
    ]
    if normativa_links:
        parts.append("  <ul class=\"lista-entregables\">\n")
        for link in normativa_links:
            parts.append(f'    <li><a href="{_esc(link)}">{_esc(link.split("/")[-1])}</a></li>\n')
        parts.append("  </ul>\n")
    if entregables is not None and not entregables.empty:
        parts.append("  <h3>Entregables cimientos (v3 §2.3)</h3>\n")
        parts.append(entregables.to_html(index=False).replace('class="dataframe"', ""))

    if manifest_entregables is not None and not manifest_entregables.empty:
        parts.append('  <h3 id="archivos-n0">Archivos copiados en salida/entregables_n0/</h3>\n')
        parts.append("  <p>Descarga o abre cada entregable desde esta carpeta (misma copia que analisis/nivel0/).</p>\n")
        parts.append("  <ul class=\"lista-entregables\">\n")
        for _, r in manifest_entregables.iterrows():
            link = str(r.get("copia_local") or "")
            nombre = _esc(str(r["archivo"]))
            desc = _esc(str(r["descripcion"]))
            det = _esc(str(r["detalle"]))
            est = str(r["estado"])
            if link and est == "Copiado":
                parts.append(
                    f'    <li><a href="{_esc(link)}">{nombre}</a> — {desc} '
                    f"<span class=\"meta\">({det})</span></li>\n"
                )
            else:
                parts.append(f"    <li>{nombre} — {desc} <strong>{_esc(est)}</strong></li>\n")
        parts.append("  </ul>\n")
    if qa_v3 is not None and not qa_v3.empty:
        parts.append("  <h3>Control normativo v3 (§1.5 N0 + §2.1 N0.5)</h3>\n")
        parts.append(qa_v3.to_html(index=False).replace('class="dataframe"', ""))
    if qa_jalisco:
        parts.append("  <h3>Control pipeline legacy (reporte_calidad.md)</h3>\n")
        if nota_calidad:
            parts.append(f"  <p class=\"meta\">{_esc(nota_calidad)}</p>\n")
        qa_df = pd.DataFrame(qa_jalisco, columns=["Prueba", "Criterio", "Resultado"])
        parts.append(qa_df.to_html(index=False).replace('class="dataframe"', ""))
    if qa_d4 is not None and not qa_d4.empty:
        parts.append("  <h3>Control · corte D4 vigente (diputado)</h3>\n")
        parts.append(
            "  <p>Complemento local: mismas banderas, filtradas al distrito 4 con cartografía vigente.</p>\n"
        )
        parts.append(qa_d4.to_html(index=False).replace('class="dataframe"', ""))
    if checklist:
        parts.append('  <h3 id="checklist-v3">Checklist v3 + operación</h3>\n')
        parts.append("  <ul>\n")
        for item in checklist:
            parts.append(f"    <li>{_inline_md_bold(item)}</li>\n")
        parts.append("  </ul>\n")
    return parts


def build_html(
    out_path: Path,
    *,
    titulo: str,
    secciones: list[tuple[str, str]],
    guia: str,
    explicacion_tabla: str,
    explicacion_ganador: str,
    agg: pd.DataFrame,
    flags: pd.DataFrame,
    ganador: pd.Series,
    imagenes: list[tuple[str, Path, str]],
    marco_pdf: str = "",
    entregables: pd.DataFrame | None = None,
    qa_jalisco: list[tuple[str, str, str]] | None = None,
    qa_d4: pd.DataFrame | None = None,
    checklist: list[str] | None = None,
    nota_calidad: str = "",
    manifest_entregables: pd.DataFrame | None = None,
    qa_v3: pd.DataFrame | None = None,
    normativa_links: list[str] | None = None,
    version_informe: str = "2026-08-09-v3-r2",
) -> None:
    agg_html = agg.to_html(index=False, float_format=lambda x: f"{x:,.2f}" if isinstance(x, float) else f"{x:,}")
    flags_html = flags.to_html(index=False)
    gan_html = ganador.to_frame("secciones").to_html()

    guia_paras = "".join(f"  <p>{_esc(p.strip())}</p>\n" for p in guia.strip().split("\n\n"))
    body_parts = [
        f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta http-equiv="Cache-Control" content="no-cache, must-revalidate"/>
  <title>{_esc(titulo)}</title>
  <style>
    body {{ font-family: Georgia, 'Segoe UI', serif; max-width: 920px; margin: 2rem auto; padding: 0 1.25rem; color: #1e293b; line-height: 1.55; }}
    h1 {{ color: #001834; border-bottom: 3px solid #1090D0; padding-bottom: 0.35rem; }}
    h2 {{ color: #334e68; margin-top: 2rem; }}
    h3 {{ color: #627d98; }}
    .meta {{ color: #64748b; font-size: 0.95rem; }}
    .badge {{ display: inline-block; background: #059669; color: #fff; font-size: 0.8rem; font-weight: 600; padding: 0.25rem 0.6rem; border-radius: 4px; margin-left: 0.5rem; vertical-align: middle; }}
    .indice {{ background: #f0fdf4; border: 1px solid #86efac; padding: 0.85rem 1rem; margin: 1rem 0 1.5rem; font-size: 0.95rem; }}
    .indice a {{ color: #047857; }}
    .pdf-cumplimiento {{ background: #ecfdf5; border-left: 5px solid #059669; padding: 1rem 1.15rem; margin: 0.5rem 0 1.25rem; }}
    .lista-entregables {{ font-size: 0.92rem; line-height: 1.45; }}
    .lista-entregables a {{ font-weight: 600; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.9rem; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 0.4rem 0.6rem; text-align: left; }}
    th {{ background: #f1f5f9; }}
    img {{ max-width: 100%; height: auto; margin: 1rem 0; border: 1px solid #e2e8f0; }}
    .nota {{ background: #fffbeb; border-left: 4px solid #f59e0b; padding: 1rem 1.1rem; margin: 0.75rem 0 1.5rem; font-size: 0.95rem; }}
    .guia {{ background: #eff6ff; border-left: 4px solid #1090D0; padding: 1rem 1.1rem; margin: 1.25rem 0; }}
    p {{ text-align: justify; }}
  </style>
</head>
<body>
  <h1>{_esc(titulo)}<span class="badge">Instrucciones v3</span></h1>
  <p class="meta">Generado: {date.today().isoformat()} · Versión informe: {_esc(version_informe)} · Fuente: <code>analisis/nivel0/</code></p>
  <nav class="indice" aria-label="Indice">
    <strong>Indice:</strong>
    <a href="#cumplimiento-v3">Cumplimiento v3</a> ·
    <a href="#checklist-v3">Checklist</a> ·
    <a href="#guia-rapida">Guía rápida D4</a> ·
    <a href="#graficos">Gráficos</a> ·
    <a href="#tabla-anios">Tabla por año</a> ·
    <a href="#metodologia">Detalle metodológico</a>
  </nav>
"""
    ]

    cumplimiento = _bloque_cumplimiento_html(
        marco_pdf=marco_pdf,
        entregables=entregables,
        qa_v3=qa_v3,
        qa_jalisco=qa_jalisco,
        qa_d4=qa_d4,
        checklist=checklist,
        nota_calidad=nota_calidad,
        manifest_entregables=manifest_entregables,
        normativa_links=normativa_links,
    )
    body_parts.extend(cumplimiento)

    body_parts.append('  <h2 id="guia-rapida">Guia rapida (lee esto primero)</h2>\n')
    body_parts.append('  <div class="guia">\n')
    body_parts.append(guia_paras)
    body_parts.append("  </div>\n")

    body_parts.append('  <h2 id="graficos">Graficos · que mirar y que significa</h2>\n')
    body_parts.append(
        "  <p>Cada figura va seguida de una nota en caja amarilla. No hace falta ser experto: "
        "lee <strong>Que es</strong>, luego <strong>Como leerlo</strong>, luego <strong>En plano</strong>.</p>\n"
    )
    for cap, rel, nota in imagenes:
        name = rel.name
        body_parts.append(f"  <h3>{_esc(cap)}</h3>\n")
        body_parts.append(f'  <img src="{_esc(name)}" alt="{_esc(cap)}"/>\n')
        body_parts.append(_nota_html(nota))

    body_parts.append("  <h2>Como leer la tabla de numeros</h2>\n")
    for para in explicacion_tabla.strip().split("\n\n"):
        body_parts.append(f"  <p>{_esc(para.strip())}</p>\n")
    body_parts.append('  <h2 id="tabla-anios">Tabla de numeros por año</h2>\n')
    body_parts.append(agg_html.replace('class="dataframe"', ""))

    body_parts.append("  <h2>Ganador por seccion en 2024</h2>\n")
    for para in explicacion_ganador.strip().split("\n\n"):
        body_parts.append(f"  <p>{_esc(para.strip())}</p>\n")
    body_parts.append(gan_html)

    body_parts.append("  <h2>Banderas de calidad (conteo)</h2>\n")
    body_parts.append(
        "  <p>Piensa en esto como 'alarmas suaves' en los datos. El numero dice cuantas veces "
        "aparecio esa alarma en alguna seccion y año del D4.</p>\n"
    )
    body_parts.append(flags_html)

    body_parts.append('  <h2 id="metodologia">Detalle metodologico</h2>\n')
    for heading, text in secciones:
        body_parts.append(f"  <h3>{_esc(heading)}</h3>\n")
        for para in text.strip().split("\n\n"):
            body_parts.append(f"  <p>{_esc(para.strip())}</p>\n")

    body_parts.append("</body>\n</html>")
    out_path.write_text("".join(body_parts), encoding="utf-8")


def build_pdf(
    out_path: Path,
    *,
    titulo: str,
    secciones: list[tuple[str, str]],
    guia: str,
    explicacion_tabla: str,
    explicacion_ganador: str,
    agg: pd.DataFrame,
    imagenes: list[tuple[str, Path, str]],
    marco_pdf: str = "",
    entregables: pd.DataFrame | None = None,
    qa_jalisco: list[tuple[str, str, str]] | None = None,
    qa_d4: pd.DataFrame | None = None,
    checklist: list[str] | None = None,
    nota_calidad: str = "",
    qa_v3: pd.DataFrame | None = None,
) -> bool:
    if not HAS_REPORTLAB:
        return False

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], textColor=colors.HexColor("#001834"), spaceAfter=12)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor("#334E68"), spaceBefore=14, spaceAfter=8)
    body = ParagraphStyle("Body", parent=styles["Normal"], alignment=TA_JUSTIFY, fontSize=10, leading=14)
    meta = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#64748B"))
    nota = ParagraphStyle(
        "Nota",
        parent=body,
        fontSize=9,
        leading=12,
        leftIndent=0.3 * cm,
        backColor=colors.HexColor("#FFFBEB"),
        borderPadding=6,
    )

    story = [
        Paragraph(titulo, h1),
        Paragraph(f"Fecha: {date.today().isoformat()} · Datos: analisis/nivel0/", meta),
        Spacer(1, 0.4 * cm),
        Paragraph("Guia rapida (lee esto primero)", h2),
    ]
    for para in guia.strip().split("\n\n"):
        story.append(Paragraph(para.strip(), body))
        story.append(Spacer(1, 0.12 * cm))

    story.append(Paragraph("Graficos · que mirar y que significa", h2))
    for cap, img_path, nota_txt in imagenes:
        if not img_path.exists():
            continue
        story.append(Paragraph(cap, h2))
        story.append(Image(str(img_path), width=16 * cm, height=16 * cm * 0.55))
        story.append(Spacer(1, 0.15 * cm))
        for block in nota_txt.strip().split("\n\n"):
            story.append(Paragraph(block.strip().replace("\n", " "), nota))
            story.append(Spacer(1, 0.08 * cm))
        story.append(Spacer(1, 0.25 * cm))

    story.append(Paragraph("Como leer la tabla de numeros", h2))
    for para in explicacion_tabla.strip().split("\n\n"):
        story.append(Paragraph(para.strip(), body))
        story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph("Tabla por año (D4 vigente)", h2))
    cols = ["Año", "Secc.", "Validos", "% MC", "% 4T", "Outliers"]
    data = [cols]
    for _, r in agg.iterrows():
        data.append(
            [
                str(int(r["anio"])),
                str(int(r["secciones"])),
                f"{int(r['validos']):,}",
                f"{r['pct_mc']:.2f}",
                f"{r['pct_4t']:.2f}",
                str(int(r["outliers"])),
            ]
        )
    t = Table(data, colWidths=[2 * cm, 2.2 * cm, 3 * cm, 2 * cm, 2 * cm, 2 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 0.35 * cm))

    story.append(Paragraph("Ganador por seccion en 2024", h2))
    for para in explicacion_ganador.strip().split("\n\n"):
        story.append(Paragraph(para.strip(), body))
        story.append(Spacer(1, 0.1 * cm))

    if marco_pdf:
        story.append(Paragraph("Cumplimiento Instrucciones v3", h2))
        story.append(Paragraph(marco_pdf.replace("**", ""), body))
        story.append(Spacer(1, 0.15 * cm))

    if entregables is not None and not entregables.empty:
        story.append(Paragraph("Entregables v3 §2.3", h2))
        col_ent = "entregable_v3_2_3" if "entregable_v3_2_3" in entregables.columns else entregables.columns[0]
        tdata = [["Entregable", "Estado"]]
        for _, r in entregables.iterrows():
            tdata.append([str(r[col_ent]), str(r["estado"])])
        t = Table(tdata, colWidths=[10 * cm, 5 * cm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 0.2 * cm))

    if qa_v3 is not None and not qa_v3.empty:
        story.append(Paragraph("Control normativo v3", h2))
        tdata = [["Prueba", "Resultado"]]
        for _, r in qa_v3.iterrows():
            tdata.append([str(r["prueba"]), str(r["resultado"])])
        t = Table(tdata, colWidths=[8 * cm, 7 * cm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 0.2 * cm))

    if qa_jalisco:
        story.append(Paragraph("Control pipeline legacy", h2))
        if nota_calidad:
            story.append(Paragraph(nota_calidad, meta))
        tdata = [["Prueba", "Resultado"]]
        for prueba, _crit, res in qa_jalisco:
            tdata.append([prueba, res])
        t = Table(tdata, colWidths=[8 * cm, 7 * cm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 0.2 * cm))

    if qa_d4 is not None and not qa_d4.empty:
        story.append(Paragraph("Control D4 vigente", h2))
        tdata = [["Prueba", "Resultado"]]
        for _, r in qa_d4.iterrows():
            tdata.append([str(r["prueba"]), str(r["resultado"])])
        t = Table(tdata, colWidths=[8 * cm, 7 * cm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 0.2 * cm))

    if checklist:
        story.append(Paragraph("Checklist v3 + operacion", h2))
        for item in checklist:
            story.append(Paragraph(f"• {item.replace('**', '')}", body))
            story.append(Spacer(1, 0.06 * cm))

    story.append(Paragraph("Detalle metodologico", h2))
    for heading, text in secciones:
        story.append(Paragraph(heading, h2))
        for para in text.strip().split("\n\n"):
            story.append(Paragraph(para.strip(), body))
            story.append(Spacer(1, 0.12 * cm))

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    doc.build(story)
    return True


def narrativa(
    *,
    fuentes: list[dict],
    n_acta: int,
    n_interp: int,
    n_inst_d4: int,
    n_vig_d4: int,
    cargos: pd.DataFrame,
) -> list[tuple[str, str]]:
    fuente_txt = "\n".join(
        f"• {f['archivo']}: {f['filas']:,} filas — {f['descripcion']}"
        for f in fuentes
        if f["existe"]
    )
    cargo_txt = "\n".join(
        f"• {r['cargo']}: {int(r['filas']):,} filas en {int(r['anios'])} años."
        for _, r in cargos.head(5).iterrows()
    )

    return [
        (
            "1. Que es el Nivel 0",
            "Capa de cimientos según Instrucciones v3 (doc 01): hecho atómico N0 + interpolación "
            "N0.5. No incluye colores estratégicos ni índices (N1+). Esta auditoría cruza narrativa "
            "D4 (diputado) con entregables en analisis/nivel0/ y la normativa v3 (Marco general + "
            "Cimientos). Decisión D7: re-ingesta con tres cantidades por emblema cuando el pipeline "
            "electoral lo complete.",
        ),
        (
            "2. Fuentes de datos (repo)",
            fuente_txt
            + f"\n\nEn total, base_seccion_anio tiene {n_acta:,} filas (todas las demarcaciones y cargos agregados). "
            "La interpolada (N0.5) tiene "
            f"{n_interp:,} filas porque reasigna historicos a la cartografia vigente (distrito_local_vigente).",
        ),
        (
            "3. Dos formas de cortar el D4",
            "Institucional: distrito_local_del_anio == 4 en el acta de cada eleccion (como estaba "
            "en urna ese año). Vigente (producto): distrito_local_vigente == 4 en base_seccion_anio_interpolada.csv "
            "(167 secciones desde 2015; 2009–2012 parciales por redistritacion). "
            f"Para diputado, filas D4 institucional: {n_inst_d4:,}; filas D4 vigente: {n_vig_d4:,}. "
            "Para narrativa de campana y mapas D4 se usa la serie vigente.",
        ),
        (
            "4. Cargos en base_seccion_anio",
            cargo_txt or "Sin desglose de cargos.",
        ),
        (
            "5. Lectura de la serie historica",
            "Los porcentajes pct_mc y pct_4t son votos del bloque sobre la suma de votos validos "
            "del distrito en ese año (no es 'cuantos votaron del padron'; eso seria participacion). "
            "Antes de 2018 MORENA 4T aparece bajo o en cero porque el bloque se arma con reglas de "
            "coalicion del pipeline v3. Entre 2018 y 2024 sube la competencia MC vs 4T; en 2024 los "
            "votos validos agregados reflejan la eleccion mas reciente con cartografia completa. "
            "La columna outliers en la tabla resume cuantas filas (sección-año) quedaron marcadas "
            "como outlier en ese año (ver glosario).",
        ),
        (
            "6. Ganador 2024 por seccion",
            "Cada fila de 2024 trae ganador_bloque: el bloque (MC, MORENA_4T, etc.) que mas votos "
            "validos obtuvo en esa seccion. Contar secciones ganadas no es lo mismo que contar votos "
            "totales del distrito; por eso puede haber empate tecnico (84 vs 83 secciones) aunque "
            "los porcentajes agregados de votos esten muy parejos.",
        ),
        (
            "7. Glosario · terminos tecnicos en lenguaje claro",
            "Bloque homologado: agrupacion de partidos/coaliciones para comparar en el tiempo "
            "(MC, MORENA 4T, PAN, PRI, OTROS). No es el nombre del partido en boleta, sino la "
            "etiqueta analitica despues de limpiar datos.\n\n"
            "Votos validos: votos que cuentan para el resultado (sin nulos ni no registrados). "
            "Los porcentajes pct_mc / pct_4t dividen votos del bloque entre la suma de validos.\n\n"
            "Flag (bandera): columna si/no (1 o 0) que avisa un problema o una condicion especial "
            "en esa fila. No borra el dato; solo dice 'revisar con cuidado' o 'contexto raro'.\n\n"
            "Outlier (valor atipico): en N0, flag_outlier = 1 cuando hay una anomalia 'dura': "
            "participacion imposible (>100%), totales que no cuadran (validos+nulos+no registrados "
            "muy distintos del total), o cero votos validos. Es una fila sospechosa de acta o "
            "de captura, no un juicio politico.\n\n"
            "flag_participacion_anomala: votos totales mayores que lista nominal (mas del 100% "
            "de participacion).\n\n"
            "flag_totales_inconsistentes: la suma de componentes no coincide con el total de urna "
            "mas alla de una tolerancia pequena.\n\n"
            "flag_datos_incompletos: no hay votos validos en esa sección-año-cargo.\n\n"
            "flag_coalicion_compleja: en esa eleccion hubo marcas o reparto de votos entre bloques "
            "dificil de leer (coaliciones cruzadas); el dato se conserva pero el desglose exige "
            "mirar catalogo de coaliciones.\n\n"
            "flag_lista_nominal_faltante: la fuente original no traia lista nominal; participacion "
            "no se puede calcular con rigor.\n\n"
            "Institucional vs vigente: institucional = distrito en el acta de ese año; vigente = "
            "secciones reasignadas al mapa electoral actual (interpolada N0.5) para contar siempre "
            "las mismas 167 secciones del D4 de hoy.\n\n"
            "Interpolada (N0.5): CSV base_seccion_anio_interpolada.csv; remapea historico al "
            "distrito_local_vigente. Es la serie que usa la app para historia del D4 en mapas.",
        ),
        (
            "8. Banderas de calidad · que significan los numeros del grafico",
            "Los conteos suman cuantas filas del D4 vigente tienen cada flag en 1. Muchas "
            "flag_lista_nominal_faltante en años viejos es normal (fuentes sin padron). "
            "flag_coalicion_compleja alto indica elecciones donde MC/4T no se leen como un solo "
            "partido en boleta. Un outlier aislado (p. ej. 1 fila en 2021) conviene cruzarlo con "
            "reporte_anomalias.csv en analisis/nivel0/ si se quiere la seccion exacta.",
        ),
        (
            "9. Por que esta auditoria no incluye mapas",
            "Nivel 0 es una capa de tablas (CSV): numeros por seccion, sin geometria. Los mapas "
            "necesitan poligonos de seccion (shapefile / PostGIS geo_geofeature) y un paso que "
            "una clave seccion + atributo electoral → color en el mapa. Eso ocurre en otros "
            "artefactos: capas 'Resultados electorales' en PostGIS, scripts mapas_presentacion_d4.py "
            "(analisis/presentacion-d4/), electoral_secciones.json en el backend, y niveles superiores "
            "cuando ya hay scores (N3–N5). Esta auditoria N0 responde: 'los archivos base cuadran y "
            "la serie D4 diputado se entiende en numeros'. Los mapas D4 de campana se auditan aparte "
            "(geometria + pintado), no dentro del CSV puro de N0. Si quieres mapas en una carpeta "
            "auditoria/, el siguiente paso seria una hoja 'N0 + cartografia' que cruce catalogo_secciones "
            "con la capa SECCION y genere un mapa de ganador 2024 por seccion.",
        ),
        (
            "10. Conclusiones",
            "La auditoria confirma lectura local de N0: archivos presentes, filtros D4 reproducibles "
            "y graficos alineados con la presentacion D4 en cifras. Siguiente paso natural: N1 "
            "(electoral_nivel1) y, si se desea mapa en informe, modulo de cruce con geometria. "
            "PostGIS puede desactualizar nombres de columnas respecto al CSV v3; la fuente de verdad "
            "para esta revision es analisis/nivel0/.",
        ),
    ]
