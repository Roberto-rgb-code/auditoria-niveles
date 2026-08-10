# Auditoría por niveles (pipeline v3)

Informes reproducibles en Python (pandas + matplotlib) sobre los CSV de `analisis/`.

**Especificación Nivel 0 (normativa v3):**

- `analisis/Instrucciones v3/Instrucciones v3/00 — Marco general v3.md`
- `analisis/Instrucciones v3/Instrucciones v3/01 — Cimientos N0-N0.5 v3.md`

(Sustituye el PDF Nivel 0 v1.)

## Requisitos

- Python 3.10+
- Datos en el repo principal **miguel-gis**: carpeta `analisis/nivel0/` (CSVs generados por `scripts/electoral_nivel0.py`)
- Paquetes: `pandas`, `matplotlib`, `reportlab`

```bash
pip install pandas matplotlib reportlab
```

## Nivel 0

```bash
# Desde miguel-gis (monorepo):
python "auditoria/nivel 0/ejecutar_auditoria.py"

# Repo clonado solo (auditoria-niveles):
set MIGUEL_GIS_ROOT=C:\ruta\a\miguel-gis
python "nivel 0/ejecutar_auditoria.py"
```

Salida: `nivel 0/salida/` — informe, gráficos, CSV de campaña D4 y **`entregables_n0/`** con copia de todos los archivos de `analisis/nivel0/` (base maestra, catálogos, reportes, bitácora, N0.5).

## Remoto

https://github.com/Roberto-rgb-code/auditoria-niveles
