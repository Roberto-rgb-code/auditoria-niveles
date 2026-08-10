# Auditoría por niveles (pipeline v3)

Informes reproducibles en Python (pandas + matplotlib) sobre los CSV de `analisis/`.

**Especificación Nivel 0 (marco v3):** en el monorepo miguel-gis,  
`analisis/Instrucciones v1/Instrucciones v1/Nivel 0.pdf`

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

Salida: `nivel 0/salida/` — HTML, PDF, PNG y CSV.

## Remoto

https://github.com/Roberto-rgb-code/auditoria-niveles
