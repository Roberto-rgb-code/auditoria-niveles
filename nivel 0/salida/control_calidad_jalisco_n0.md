# Reporte de calidad de datos — Nivel 0 (Multi-cargo)

_Generado: 2026-07-05T15:05:11_

Universo: 15 elecciones, Jalisco.

Cargos: Diputación local MR, Gobernador, Presidente Municipal.

Años: 2009, 2012, 2015, 2018, 2021, 2024.

## Pruebas de control de calidad (PDF Nivel 0, §0.6)

| Prueba | Criterio | Resultado |
|---|---|---|
| Secciones únicas | Sin duplicados por sección+año+cargo | OK |
| Totales consistentes | válidos+nulos+no_reg ≈ total | 1110 filas con diferencia (2.08%) |
| Lista nominal válida | sin cero/negativo injustificado | 0 secciones-año-cargo con LN cero |
| Participación válida | entre 0% y 100% | 26 fuera de rango (0.05%) |
| Bloques homologados | todo partido tiene bloque | OK |
| Elecciones clasificadas | tipo, año, cargo, comparabilidad | OK (15/15) |
| Geografía consistente | sección en cartografía actual | 1595 secciones-año-cargo sin cartografía |
| Redistritación | distrito local estable entre años | 1704 secciones cambiaron de distrito (ver catálogo) |
| Secciones sin histórico | identificadas y separadas | 655 secciones |

## Cobertura por elección

| Año | Cargo | Secciones | Casillas | Válidos | Lista nominal | Coaliciones |
|---|---|---|---|---|---|---|
| 2009 | Diputacion local MR | 3346 | 8642 | 2,544,842 | no | PRI-NAL |
| 2009 | Presidente Municipal | 3346 | 8658 | 2,548,101 | no | PRD-PT; PRIN-NAL; PT-CON |
| 2012 | Diputacion local MR | 3476 | 8903 | 3,185,555 | no | PRI-PVEM (Compromiso por Jalisco); PT-MC |
| 2012 | Gobernador | 3476 | 8903 | 3,307,992 | no | PRI-PVEM (Compromiso por Jalisco); PT-MC |
| 2012 | Presidente Municipal | 3476 | 8892 | 3,271,190 | no | PRI-PVEM (Compromiso por Jalisco); PT-MC |
| 2015 | Diputacion local MR | 3546 | 9343 | 2,819,900 | no | PAN-PRD; PRI-PVEM |
| 2015 | Presidente Municipal | 3546 | 9343 | 2,827,430 | no | PAN-PRD; PRI-PVEM |
| 2018 | Diputacion local MR | 3545 | 9808 | 3,185,315 | no | Juntos Haremos Historia (PT-MORENA-PES); Por Jalisco al Frente (PAN-PRD-MC) |
| 2018 | Gobernador | 3567 | 9829 | 3,353,290 | no | PES-PT-MORENA (Juntos Haremos Historia) |
| 2018 | Presidente Municipal | 3545 | 9808 | 3,348,558 | no | PAN-PRD-MC; PES-PT-MORENA |
| 2021 | Diputacion local MR | 3600 | 10208 | 2,907,942 | sí | — |
| 2021 | Presidente Municipal | 3598 | 10203 | 2,821,080 | sí | — |
| 2024 | Diputacion local MR | 3783 | 10883 | 3,691,343 | sí | Fuerza y Corazon por Jalisco (PAN-PRI-PRD); Sigamos Haciendo Historia (PVEM-PT-MORENA-HAGAMOS-FUTURO) |
| 2024 | Gobernador | 3783 | 10883 | 3,670,576 | sí | Fuerza y Corazon por Jalisco (PAN-PRI-PRD); Sigamos Haciendo Historia (PVEM-PT-MORENA-HAGAMOS-FUTURO) |
| 2024 | Presidente Municipal | 3783 | 10863 | 3,575,521 | sí | Fuerza y Corazon por Jalisco (PAN-PRI-PRD); Sigamos Haciendo Historia (PVEM-PT-MORENA-HAGAMOS-FUTURO) |

## Faltantes en variables críticas

| Variable | Filas faltantes | % |
|---|---|---|
| lista_nominal | 34869 | 65.28% |
| votos_validos (≤0) | 66 | 0.12% |

> La lista nominal falta estructuralmente en 2009, 2012, 2015 y 2018 (la fuente no la incluye a nivel casilla). Se marca con bandera; la participación solo se calcula en 2021 y 2024.

## Resumen de anomalías

| Tipo de anomalía | Casos |
|---|---|
| totales_inconsistentes | 1110 |
| sin_votos_validos | 66 |
| participacion_mayor_100 | 26 |
| participacion_muy_baja | 11 |

_Detalle completo en `reporte_anomalias.csv`._

## Checklist ejecutivo (PDF Nivel 0, §0.8)

- **¿Cuántas secciones tenemos?** 4245 en el catálogo (3900 con datos electorales; 345 solo en cartografía).
- **¿Cuántas elecciones históricas comparables?** 15 (3 cargos: Diputación MR, Gobernador, Municipal).
- **¿Qué partidos/coaliciones se homologaron?** Ver `homologacion_partidos_bloques.csv` (bloques: MC, MORENA_4T, PAN, PRI, OTROS).
- **¿Hay secciones nuevas/sin histórico?** 655 con presencia parcial; ver `catalogo_secciones.csv`.
- **¿% de datos faltantes?** lista_nominal 65.28% (estructural); válidos 0.12%.
- **¿Anomalías electorales?** participación>100%: 26; totales inconsistentes: 1110; secciones con redistritación: 1704.
- **¿Se puede calcular participación y voto por bloque?** Voto por bloque: sí (todos los años/cargos). Participación: solo 2021 y 2024.
- **¿La base puede auditarse y replicarse?** Sí: pipeline único (`electoral_nivel0.py`) + bitácora + reportes.
