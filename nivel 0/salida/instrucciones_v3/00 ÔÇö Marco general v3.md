# Instrucciones v3 — 00. Marco general

> La v3 **consolida** la v2 + Adenda A (demarcación) + Adenda B (piso
> estructural) en un solo cuerpo, y agrega dos cambios de fondo aprobados por el
> cliente: **piso por régimen electoral** y el modelo **color × atributos** que
> reemplaza a los 20 subtipos. Objetivo operativo: asesorar dos campañas con el
> mismo motor — **alcaldía de Zapopan** y **diputación por el Distrito 4** —
> con storytelling accionable y métrica defendible.

## 1. Decisiones congeladas (aprobadas; no se reabren sin bitácora)

| # | Decisión | Detalle |
|---|---|---|
| D1 | **Quiebre de régimen** | Municipal y Diputación: **2015→**. Gubernatura: **2012→** (declarativo: su serie ya es 2012/2018/2024). El quiebre es propiedad del sistema de partidos, documentada y uniforme. |
| D2 | **Ventana única para todos los bloques (camino A)** | El rival (4T) se mide en la misma ventana; su ascenso (0→33% en la 2979) se lee como **tendencia**, no como piso. Nada de ventanas por partido. |
| D3 | **Color × atributos** | 5 colores (acción/presupuesto) + 4 banderas ortogonales (`volumen`, `riesgo_2027`, `emergente`, `movilizable`) + `confianza`. Los 20 subtipos v1 desaparecen; la narrativa se autogenera. |
| D4 | **Graneros simétricos** | Aporte de votos **absolutos** propio y rival como salida de primera línea. "Los porcentajes no votan; las personas sí." |
| D5 | **Doble demarcación** | Base limpia estatal; clasificación corrida **dos veces**: vara Zapopan y vara D4, salidas etiquetadas (`demarcacion_umbral`). |
| D6 | **Satélites: serie completa** | El rastreo de marca única (PVEM, PT, Hagamos, Futuro…) usa 2009-2024 **sin corte de régimen** — la erosión de largo plazo ES el dato de negociación 2027. Vía paralela, por demarcación. |
| D7 | **Re-ingesta N0 = prerrequisito vital** | Las tres cantidades de voto solo existen re-ingiriendo desde los Excel INE/IEPC. La base en nube ya colapsó la marca única. Sin este paso no hay rastreo de satélites. |

## 2. Prueba de sensibilidad del quiebre (corrida 2026-07-04, Zapopan)

| Boleta | corr(piso 2015+, piso 2012+) | Cambian de lado del P75 | Veredicto |
|---|---|---|---|
| Municipal | 0.934 | 34/444 (7.7%) | Robusto: 2015 congruente |
| Diputación | 0.807 | 76/444 (17.1%) | Sensible — y esa sensibilidad **confirma** que 2012 es otro régimen para boletas locales (MC ganó 0 secciones municipales en 2012); excluirlo es el punto |
| Gubernatura | n/a | n/a | Corte 2012 no excluye nada (serie 2012/2018/2024) |

**Efecto sobre el problema que motivó todo (las 151 "gris sin patrón" municipales):**
74 superan el P75 del piso de régimen; 59 quedan entre mediana y P75; solo 18
bajo mediana. El gris residual queda chico y honesto.

**Hallazgo adicional (obliga a la regla de dominio, ver 03):** la 2979 tiene
piso de régimen 45.6% y AUN ASÍ queda bajo el P75 (49.0%) — porque en una
demarcación dominada por el cliente, la vara relativa crea escasez artificial
de Azules (solo el 25% puede ser "élite" por construcción). El Azul v3 tiene
**dos rutas**: élite relativa O dominio sostenido.

## 3. Arquitectura (capas y vía paralela)

```
EXCELS INE/IEPC ──► N0 hecho atómico (3 cantidades × emblema)  ──┐
                     │                                            │ VÍA SATÉLITES
                     ▼                                            │ (marca única,
                    N0.5 interpolación dasimétrica                │  serie completa
                     │   (masa ≥99.5%, censo por época)           │  2009-2024, por
                     ▼                                            │  demarcación)
                    N1 descriptivos (por bloque + por emblema) ───┤
                     ▼                                            │
                    N2 históricos: piso_historico / piso_regimen  │
                        / piso_estructural / prima_arrastre ──────┤
                     ▼                                            │
                    N3 color × atributos + graneros  ×2 corridas  │
                        (vara Zapopan | vara D4)                  │
                     ▼                                            ▼
                    N4 índices → N5 metas y escenarios E1-E4 → N6 arquetipos
```

## 4. El contrato de storytelling (la línea por sección)

Cada sección sale con: `color · volumen · riesgo_2027 · emergente · movilizable
· confianza · demarcación` + narrativa autogenerada. Casos testigo:

- **2979** → `Azul (dominio) · volumen alto · riesgo_2027 alto · confianza alta · vara Zapopan`
  *"Territorio PRI/PAN hasta 2012, conquistado por MC en 2015, 4/4 victorias con
  márgenes +19 a +41. Movilizar fuerte. Ojo 2027: la 4T pasó de 0 a 33% y parte
  de la ventaja monta la marea MC."*
- **3698** → `Azul · emergente · confianza baja` — *"Fraccionamiento nuevo, 3/3
  en 2024 con +29. Validar en campo antes de invertir."*

## 5. Mapa v2 → v3 y orden de implementación

| Documento v3 | Consolida |
|---|---|
| 01 Cimientos (N0-N0.5) | N0 v2 + N0.5 v2 + Adenda A (columnas distrito) |
| 02 Métricas (N1-N2) | N1 v2 + N2 v2 + Adenda B + **régimen (D1/D2)** |
| 03 Clasificación (N3) | N3 v2 + Adendas A/B + **color × atributos + graneros + regla de dominio** |
| 04 Estrategia (N4-N6) | N4/N5/N6 v2 con insumos v3 |

Orden de implementación: (1) re-ingesta N0 con tres cantidades [D7, vital] →
(2) interpolación corregida N0.5 → (3) N1-N2 con doble piso → (4) N3 dual
Zapopan/D4 + reporte de diferencias v2→v3 → (5) N4-N6. Los docs v2 y adendas
quedan como historial; **la v3 es la versión normativa**.
