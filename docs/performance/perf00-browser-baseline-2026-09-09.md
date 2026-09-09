# PERF-00: línea base reproducible del navegador

Fecha: 2026-09-09. Commit medido: `c4ea0553f0060c2bb2bc799c7e657a5e7feca344`.
Datos crudos: [perf00-browser-baseline-2026-09-09.json](perf00-browser-baseline-2026-09-09.json).

## Protocolo

`scripts/benchmark_performance.py` sirve el repositorio por HTTP y ejecuta cinco pares de carga
fría/caliente en Chromium. Un doble local de MapLibre introduce 200 ms antes de `load`; las
fuentes, favicons y tiles públicos no se descargan. Cada muestra exige que el conteo, las filas y
los marcadores coincidan. Las interacciones esperan dos frames antes de declarar el resultado.

Este protocolo aísla el shell, el JSON, el DOM y la lógica de la aplicación. No mide WebGL, la
red pública ni el peso real de MapLibre/OpenFreeMap. Los tiempos sirven para comparar commits en
este mismo entorno, no como cifra de producción.

## Resultado

| Escenario | Mediana | MAD | p95 | Resultado comprobado |
|---|---:|---:|---:|---|
| Primera lista, carga fría | 267,4 ms | 6,5 ms | 557,8 ms | 38 filas y 38 marcadores |
| Primera lista, carga caliente | 233,3 ms | 2,1 ms | 248,3 ms | 38 filas y 38 marcadores |
| Añadir Coworking, handler | 1,8 ms | 0,0 ms | 2,0 ms | 55 resultados |
| Cambiar a Trabajar remoto, handler | 8,9 ms | 0,3 ms | 9,3 ms | 8 resultados |
| Quitar Café, handler | 0,9 ms | 0,1 ms | 1,0 ms | 5 resultados |

La primera muestra fría incluye el arranque inicial de Chromium y eleva el p95; se conserva en
vez de elegir la mejor ejecución. Los tres recorridos de filtro quedan por debajo del presupuesto
propuesto de 100 ms en este dataset.

Cinco eventos `idle` con vista y datos estables produjeron cinco llamadas idénticas a `setData`
en cada fuente de edificios, diez escrituras repetidas en total. PERF-01 debe eliminar esas
escrituras sin ocultar cambios reales de geometría.

Los archivos propios medidos ocupan 151.680 bytes sin compresión: `index.html` 96.019,
`companies.json` 53.624 y `ticker.json` 2.037. Esto no equivale al Brotli de Vercel. El recorrido
bloqueó o sustituyó 615 solicitudes externas entre diez navegaciones, principalmente la librería,
fuente y favicons; ningún tile público escapó del doble determinista.

## Repetición

```powershell
python scripts/benchmark_performance.py `
  --runs 5 `
  --output docs/performance/perf00-browser-baseline-2026-09-09.json
```

Después de PERF-01, el mismo detector puede convertirse en gate:

```powershell
python scripts/benchmark_performance.py --runs 5 --require-no-repeated-set-data
```
