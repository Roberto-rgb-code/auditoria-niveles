# Instrucciones v3 — 01. Cimientos: Nivel 0 (hecho atómico) y Nivel 0.5 (interpolación)

> Consolida N0 v2, N0.5 v2 y las columnas de distrito de la Adenda A. Sin
> cambios conceptuales respecto a lo ya aprobado — este documento es la única
> referencia normativa de la capa de datos.

## 1. Nivel 0 — Hecho atómico con tres cantidades

**Regla madre:** el N0 produce hechos inmutables. Nunca colapsa, nunca reparte,
nunca asigna bloque dentro del hecho.

### 1.1 Las tres cantidades (por emblema × sección × año × cargo)

| Cantidad | Qué es | Para qué |
|---|---|---|
| `voto_marca_unica` | Solo su emblema marcado | Fuerza autónoma / negociación (satélites) |
| `voto_combinado_coalicion` | ≥2 emblemas del convenio | Propiedad de la coalición; ganador/márgenes |
| `voto_legal_distribuido` | Reparto legal LGPP 87.13 | SOLO umbral 3% / registro |

**⚠️ PRERREQUISITO VITAL (D7):** esto exige **re-ingesta desde los Excel**
(`Bases de datos/*.xls*`), que sí traen las columnas separadas. La
`electoral_base_maestra` actual ya las colapsó (reparto igualitario en
`electoral_data.py` §778) y no es recuperable. **Sin re-ingesta no hay rastreo
de satélites ni tablero de negociación 2027.** Es el paso 1 del plan.

### 1.2 Capa de interpretación (tablas, no columnas del hecho)

- `catalogo_coalicion` (año, cargo, emblema → coalición, bloque, es_satelite):
  editable/versionada; los bloques y ganadores son agregaciones sobre hecho +
  catálogo. La tabla de homologación v1 (validada en auditoría) se conserva:
  PAN/PRI separados hasta 2024, PVEM a la 4T solo desde 2024, CON→MC en 2009.
- `registro_satelites` (PVEM, PT, HAGAMOS, FUTURO, PES, NA, PRD tardío): marca
  única %, coalición del año, bloque receptor, estatus 3%, peso swing.
- Cliente/rival = config de campaña (N1), jamás columna del hecho.

### 1.3 Territorio (Adenda A integrada)

- `catalogo_secciones` (4,245 secciones estatales): `distrito_local_vigente`
  (cartografía 2024, fija; 0 nulos) y fase 2 `distrito_federal_vigente`.
- En el hecho: `distrito_local_del_anio` (histórico institucional). Para 2024,
  `vigente == del_anio` en 100% de secciones.
- D4 de referencia: 149 secciones = 116 previas + 21 ex-D6 + ~12 emergentes.

### 1.4 Reglas de limpieza y banderas (heredadas, vigentes)

Sección 0 (extranjero) se excluye; participación >100% se marca; totales
inconsistentes se marcan; outliers nunca se borran; lista nominal solo real
2021/2024 (`flag_lista_nominal_faltante` antes; nunca imputar). Banderas v2
completas + `flag_marca_unica_no_recuperable` donde aplique.

### 1.5 Control de calidad N0

- Conservación por cantidad: Σ marca_única + Σ combinado ≈ Σ válidos por
  año/cargo (gap de independientes documentado, ~2-2.6% en 2015/2021/2024-mun).
- Σ legal_distribuido por coalición = Σ combinado de esa coalición.
- Cero bloque horneado; cero `municipio_id = -1`; unicidad
  sección+año+cargo+emblema.

## 2. Nivel 0.5 — Interpolación dasimétrica

**Regla madre:** los votos viajan a la cartografía 2024 ponderados por **dónde
vivía la gente**, no por área; y la masa se conserva.

### 2.1 Especificación (sin cambios respecto a v2, integrada)

1. **Consolidación SOLO por (sección_destino, año, cargo, emblema).** Los
   metadatos del destino salen de la cartografía 2024, nunca del groupby. (Este
   fue el bug v1: 5,029 filas duplicadas, 15.8% del N2 inflado.)
2. **Peso dasimétrico:** población de manzana (capa 20 ya cargada, `CVEGEO`),
   con `VIV` de AGEB como corrector de forma. **Censo por época:** 2010 →
   elecciones 2009/2012; intercensal 2015 → 2015/2018; 2020 → 2021/2024. Nunca
   usar 2020 para repartir 2009.
3. **Calibración a padrón** solo donde existe (2021/2024): la población estimada
   de las manzanas de una sección suma su lista nominal. Antes de 2021:
   `flag_interp_sin_ancla_padron=1`.
4. **Rescate universal:** ninguna sección con votos se cae por falta de cruce
   geométrico (el inner-join v1 perdió hasta 4.7% de 2021); lo no cruzado se
   reporta, no se descarta en silencio.
5. **Pruebas de rechazo (no advertencias):** conservación de masa ≥99.5% por
   año/cargo; cero duplicados; cero `municipio_id=-1`.

### 2.2 Banderas territoriales que nacen aquí (las consume todo el pipeline)

- `flag_seccion_emergente` (≤2 años electorales con datos propios)
- `pct_historia_heredada` (0-1, proporción de la serie que es estimación)
- `flag_seccion_hija_redistritacion`
- `flag_seccion_nueva_en_demarcacion` (vigente ≠ del_año previo al redistritaje,
  o emergente — la "zona nueva" del D4: 21 + 12)

### 2.3 Entregables de la capa de cimientos

Hecho atómico, `catalogo_coalicion`, `registro_satelites`, catálogos de
secciones (con distritos) y elecciones, base interpolada con banderas, reporte
de conservación de masa, `catalogo` de proporciones dasimétricas auditable,
diccionario y bitácora. Publicación a Railway como versión canónica única.
