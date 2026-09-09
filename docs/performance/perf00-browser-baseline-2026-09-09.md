# PERF-00: línea base reproducible del navegador

Fecha: 2026-09-09. Harness medido: `4a9a40b757c7c022effa710fe93185581db254fc`;
base de comparación: `c4ea0553f0060c2bb2bc799c7e657a5e7feca344`.
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
| Primera lista útil, carga fría | 344,1 ms | 7,5 ms | 363,4 ms | 38 filas y 38 marcadores |
| Primera lista útil, carga caliente | 353,7 ms | 6,8 ms | 363,4 ms | 38 filas y 38 marcadores |
| Añadir Coworking, handler | 2,3 ms | 0,1 ms | 4,8 ms | 55 resultados |
| Cambiar a Trabajar remoto, handler | 10,6 ms | 0,6 ms | 11,2 ms | 8 resultados |
| Quitar Café, handler | 1,0 ms | 0,1 ms | 1,1 ms | 5 resultados |

Un recorrido diagnóstico deriva primero los conteos esperados usando los controles reales y queda
fuera de las muestras. Por eso «fría» significa un contexto nuevo dentro de un proceso Chromium
ya iniciado. Se conservan las cinco ejecuciones, no la mejor. Los tres recorridos de filtro quedan
por debajo del presupuesto propuesto de 100 ms en este dataset.

Cinco eventos `idle` con vista y datos estables produjeron cinco llamadas idénticas a `setData`
en cada fuente de edificios, diez escrituras repetidas en total. El doble no contiene geometría
de edificios, por lo que las diez cargas fueron `FeatureCollection` vacías. Esto demuestra que
falta comparar payloads estables; no mide el coste de repetir geometría real. PERF-01 debe
eliminar esas escrituras sin ocultar cambios reales de geometría.

Los archivos propios medidos ocupan 151.680 bytes sin compresión: `index.html` 96.019,
`companies.json` 53.624 y `ticker.json` 2.037. CDP registró 160.930 bytes HTTP por navegación al
incluir cabeceras y un logo local. Tanto frío como caliente devolvieron cuatro respuestas 200 sin
hits de disco o 304 en `http.server`; esta recarga local no demuestra reutilización de caché ni
equivale al Brotli de Vercel. El recorrido bloqueó o sustituyó 615 solicitudes externas entre
diez navegaciones, principalmente la librería, fuente y favicons; ningún tile público escapó del
doble determinista.

El trace diagnóstico separado se versiona como [perf00-browser-trace.zip](perf00-browser-trace.zip),
SHA-256 `c5b57190f3700827795993036d81945b6c152451535c822dabf6a73cb508875d`. CI genera un trace
smoke nuevo y lo conserva como artifact durante 14 días.

## Repetición

```powershell
python scripts/benchmark_performance.py `
  --runs 5 `
  --output docs/performance/perf00-browser-baseline-2026-09-09.json `
  --trace docs/performance/perf00-browser-trace.zip `
  --trace-versioned
```

Después de PERF-01, el mismo detector puede convertirse en gate:

```powershell
python scripts/benchmark_performance.py --runs 5 --require-no-repeated-set-data
```
