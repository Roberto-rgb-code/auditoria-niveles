"""Textos en lenguaje sencillo para resultados y graficos N0."""
from __future__ import annotations

import pandas as pd


def guia_rapida(agg: pd.DataFrame, ganador: pd.Series, flags: pd.DataFrame) -> str:
    r24 = agg.loc[agg["anio"] == 2024].iloc[0]
    mc_s = int(ganador.get("MC", 0))
    m4_s = int(ganador.get("MORENA_4T", 0))
    pct_mc = float(r24["pct_mc"])
    pct_4t = float(r24["pct_4t"])

    return (
        "Estamos mirando solo el Distrito Local 4 (Zapopan y zona aledana en la cartografia vigente), "
        "cargo diputado local, usando datos oficiales ya limpiados.\n\n"
        f"En 2024 hubo {int(r24['secciones'])} secciones con datos. Sumando todo el distrito, "
        f"Movimiento Ciudadano (MC) obtuvo aprox. {pct_mc:.1f}% de los votos validos y la coalicion "
        f"MORENA-4T aprox. {pct_4t:.1f}% — casi empate en votos totales.\n\n"
        f"Pero si cuentas 'quien gano cada casilla/seccion' (mini-territorios), MC gano {mc_s} secciones "
        f"y MORENA-4T gano {m4_s}. Eso puede ser 84 vs 83 aunque los porcentajes totales sean parejos.\n\n"
        "Los graficos de abajo cuentan la misma historia año por año. Las 'banderas' al final son avisos "
        "de datos raros en actas; no cambian el ganador por si solas."
    )


def explicacion_tabla_numeros() -> str:
    return (
        "Cada fila es un año de eleccion. No es una persona: es la suma de todas las secciones del D4.\n\n"
        "• anio: año de la elección.\n"
        "• secciones: cuantas secciones electorales entran en el conteo ese año (167 es el D4 completo hoy).\n"
        "• validos: total de votos validos sumados en todo el distrito (numero grande, no porcentaje).\n"
        "• pct_mc / pct_4t: de cada 100 votos validos del distrito, cuantos fueron para MC o para MORENA-4T.\n"
        "• outliers: cuantas secciones-año tuvieron un dato sospechoso (ver glosario); en 2021 aparece 1."
    )


def explicacion_ganador_2024(ganador: pd.Series) -> str:
    total = int(ganador.sum())
    lines = [f"En 2024 hay {total} secciones en el D4 vigente. Por cada una se mira quien tuvo mas votos:"]
    for bloque, n in ganador.items():
        pct = 100 * n / total if total else 0
        lines.append(f"  — {bloque}: {int(n)} secciones ({pct:.1f}% del territorio en piezas).")
    lines.append(
        "Importante: ganar mas secciones no siempre significa mas votos en total; "
        "se puede ganar muchas secciones chicas y perder en votos si el rival gana secciones muy pobladas."
    )
    return "\n".join(lines)


def notas_figuras(
    agg: pd.DataFrame,
    ganador: pd.Series,
    flags: pd.DataFrame,
    n_inst: int,
    n_vig: int,
) -> dict[str, str]:
    r24 = agg.loc[agg["anio"] == 2024].iloc[0]
    total_filas = int(n_vig)
    n_ln = int(flags.loc[flags["flag"] == "flag_lista_nominal_faltante", "n"].sum() or 0)
    n_coal = int(flags.loc[flags["flag"] == "flag_coalicion_compleja", "n"].sum() or 0)
    n_out = int(flags.loc[flags["flag"] == "flag_outlier", "n"].sum() or 0)
    pct_ln = 100 * n_ln / total_filas if total_filas else 0
    pct_coal = 100 * n_coal / total_filas if total_filas else 0

    nota1 = (
        "QUE ES: Barras naranja = porcentaje de MC; barras vino = porcentaje MORENA-4T; "
        "linea gris = cuantas secciones sumamos ese año.\n\n"
        "COMO LEERLO: Mira de izquierda a derecha (2009 → 2024). Si una barra sube, ese bloque "
        "se llevo mas proporcion del pastel de votos validos del distrito entero ese año.\n\n"
        "EN PLANO: MC casi no aparece en 2009 (barra bajita). Crece hasta 2015–2021. MORENA-4T "
        "despega fuerte en 2018 (cuando ya compite como bloque homologado). En "
        f"{int(r24['anio'])} las dos barras miden casi lo mismo ({float(r24['pct_mc']):.1f}% vs "
        f"{float(r24['pct_4t']):.1f}%) — carrera muy cerrada a nivel distrito.\n\n"
        "LA LINEA GRIS: Si en un año hay menos de 167 secciones, faltan pedazos del mapa actual "
        "(años viejos antes del redistritaje); no es que 'faltaran votos', sino que ese territorio "
        "pertenecia a otro distrito en esa epoca."
    )

    nota2 = (
        "QUE ES: Cada columna es un año; la altura total es todos los votos validos del D4; "
        "colores = PAN, PRI, Otros, MC y MORENA-4T apilados.\n\n"
        "COMO LEERLO: Columna mas alta = año con mas votos validos en total (mas gente voto o "
        "crecio el padron). El color que 'come' mas espacio es el bloque con mas votos ese año.\n\n"
        "EN PLANO: Arriba del todo suele dominar MC + MORENA-4T en años recientes; abajo quedan "
        "PAN/PRI/Otros. Sirve para ver no solo el duelo MC–4T sino donde se fueron los votos "
        "del resto de partidos."
    )

    mc_s = int(ganador.get("MC", 0))
    m4_s = int(ganador.get("MORENA_4T", 0))
    nota3 = (
        "QUE ES: Pastel de 2024: cada rebanada = cuantas secciones gano cada bloque "
        "(gana quien tuvo mas votos en esa seccion).\n\n"
        f"COMO LEERLO: MC {mc_s} rebanadas vs MORENA-4T {m4_s} — casi mitad y mitad del territorio "
        "en 'mini-elecciones' locales.\n\n"
        "NO CONFUNDIR: Esto NO es 'MC tuvo 50% de votos en Jalisco'. Es solo conteo de secciones "
        "ganadas dentro del D4. Los porcentajes de votos reales estan en el grafico 1."
    )

    nota4 = (
        f"QUE ES: NO es un grafico de votos ni de quien gano. Es un chequeo del archivo: "
        f"tenemos {total_filas:,} 'filas' en total (cada fila = una seccion en un año de eleccion, "
        f"solo diputado D4). El sistema pone etiquetas cuando algo falta o es confuso en la acta.\n\n"
        "COMO LEERLO: Cada barra dice 'en cuantas filas aparecio este aviso'. El numero entre "
        "parentesis es de esas filas totales. Ejemplo: "
        f"{n_ln:,} ({pct_ln:.0f}%) significa que en {pct_ln:.0f} de cada 100 filas no venia "
        "lista nominal (padron) en la fuente original — tipico en elecciones viejas, no significa "
        f"fraude. {n_coal:,} ({pct_coal:.0f}%) = boleta con coaliciones donde repartir votos a MC/4T "
        "es mas trabajoso. {n_out:,} fila(s) = numeros de acta raros (revisar a mano).\n\n"
        "EN PLANO: Imagina 975 hojas de Excel (sección × año). 641 hojas dicen 'no traigo padron'; "
        "475 dicen 'boleta complicada'; 1 dice 'ojo, numeros raros'. Igual usamos los votos de esas "
        "hojas en los graficos 1–3; solo sabemos que hay que interpretar con cuidado.\n\n"
        "NO CONFUNDIR: Barra grande NO quiere decir 'MC perdio esas secciones'. No habla de ganadores; "
        "solo de calidad del registro electoral."
    )

    nota5 = (
        "QUE ES: Comparacion de cuantas secciones entran al analisis cada año. Gris = corte "
        "institucional (como decia el acta de ese año); azul = corte vigente (mapa D4 de hoy).\n\n"
        "COMO LEERLO: Cuando las barras azules llegan a 167, ya tienes el distrito completo actual. "
        "Gris mas bajo en años viejos = parte del territorio de hoy votaba en otro distrito entonces.\n\n"
        f"EN PLANO: En total hay {n_vig:,} filas vigentes vs {n_inst:,} institucionales en la base — "
        "la campana usa el corte azul para hablar siempre del mismo D4 de 167 secciones."
    )

    return {
        "01_evolucion_pct_mc_4t.png": nota1,
        "02_votos_absolutos.png": nota2,
        "03_ganador_2024.png": nota3,
        "04_banderas_calidad.png": nota4,
        "05_secciones_inst_vs_vigente.png": nota5,
    }
