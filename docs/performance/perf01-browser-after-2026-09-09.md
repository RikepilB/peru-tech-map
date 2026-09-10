# PERF-01: datos tempranos y fuentes de edificios estables

Fecha: 2026-09-09. Implementación medida: `db3baa547be7ec68f4752e160472c71a53ff7ff9`;
base PERF-00: `4a9a40b757c7c022effa710fe93185581db254fc`.
Datos crudos: [perf01-browser-after-2026-09-09.json](perf01-browser-after-2026-09-09.json).

## Cambio comprobado

Las peticiones únicas de `companies.json` y `ticker.json` comienzan antes de construir el mapa.
La lista y el loader dejan de esperar a `map.load`; cualquier error posterior del mapa vuelve a
mostrar el loader con una acción de recarga. Las fuentes GeoJSON de edificios comparan el payload
completo y omiten `setData()` cuando la vista no cambió.

El mismo recorrido también comprueba el CTA **Agregar espacio** de la vista Trabajar remoto. Abre
el formulario revisado con Coworking Space, On-Site y la ciudad activa, usa mensajes específicos
para espacios y restaura el borrador previo al volver a Agregar empresa. Coworking Scout permanece
como origen de datos y verificación; no se exponen sus credenciales ni su interfaz técnica.

## Protocolo

Se repitió el protocolo PERF-00 en el mismo host: cinco contextos fríos y cinco recargas calientes,
Chromium, red pública bloqueada y un doble de MapLibre con `load` a 200 ms. Cada navegación exige
una sola respuesta de cada JSON, lista/conteo/marcadores coherentes y contenido útil antes de la
carga sintética del mapa. Cinco eventos `idle` estables deben producir cero escrituras propias.

## Resultado

| Escenario | PERF-00 | PERF-01 | Cambio | MAD / p95 PERF-01 |
|---|---:|---:|---:|---:|
| Primera lista útil, carga fría | 344,1 ms | 204,1 ms | -40,7 % | 6,5 / 210,6 ms |
| Primera lista útil, carga caliente | 353,7 ms | 160,0 ms | -54,8 % | 2,5 / 162,5 ms |
| Añadir Coworking, handler | 2,3 ms | 2,1 ms | -8,7 % | — |
| Cambiar a Trabajar remoto, handler | 10,6 ms | 10,0 ms | -5,7 % | — |
| Quitar Café, handler | 1,0 ms | 0,8 ms | -20,0 % | — |

Las diez muestras mostraron la lista y ocultaron el loader antes de `map.load`. La mutación inicial
del conteo tuvo mediana de 72,0 ms en frío y 28,3 ms en caliente. El gate vuelve a leer la red al
final de cada navegación completa —incluidos conteos, interacciones y trace— y encontró exactamente
una respuesta para `companies.json` y una para `ticker.json` en cada recorrido.

Los cinco estados `idle` estables produjeron **cero** llamadas a `setData()` en ambas fuentes de
edificios; PERF-00 producía cinco por fuente. El control positivo agregó una geometría con una
escritura por fuente, omitió la repetición estable y escribió una colección vacía al retirar la
geometría. Así se comprueba que la optimización conserva la invalidación real.

La vista inicial siguió mostrando 38 resultados; agregar Coworking dio 55; Trabajar remoto dio 8;
quitar Café dio 5. La validación separada pasó con 89 empresas y 16 titulares, 44 pruebas unitarias
y 18 pruebas DOM en Chromium.

El trace se versiona como [perf01-browser-trace.zip](perf01-browser-trace.zip), SHA-256
`4fc39674f376953e5a4a521409027bb7356e3e4c43d5c172009baa33fbddaa81`.

## Límites

El retraso fijo aísla el shell, JSON, DOM y scheduling de la aplicación. No mide CDN, tiles reales,
descarga de MapLibre ni WebGL. La comparación de tiempos solo es válida frente a PERF-00 en este
mismo host y protocolo; el gate de orden y las transiciones GeoJSON sí son deterministas.

## Repetición

```powershell
python scripts/benchmark_performance.py `
  --runs 5 `
  --require-list-before-map-load `
  --require-no-repeated-set-data `
  --output docs/performance/perf01-browser-after-2026-09-09.json `
  --trace docs/performance/perf01-browser-trace.zip `
  --trace-versioned
```
