# Pruebas

Desde la raíz, con Python 3.12 o posterior:

```powershell
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

El validador solo usa la biblioteca estándar. Rechaza JSON ambiguo, tipos inválidos,
coordenadas fuera de bbox, enums desconocidos, etapas incompatibles, sedes/titulares duplicados
y URLs no admitidas. No modifica ni sanea los archivos. Una sede duplicada tiene el mismo
nombre normalizado, ciudad y coordenadas; sucursales distintas y empresas que comparten
coordenadas son válidas. Verificación de fuentes y duplicados aproximados requiere revisión.

Para las pruebas de renderizado en un navegador real:

```powershell
python -m pip install -r tests/requirements.txt
python -m playwright install chromium
python tests/browser/test_render.py -v
```

La CI ejecuta ambos grupos. Playwright es una dependencia exclusiva de pruebas; no agrega
JavaScript ni un paso de compilación al sitio. En Linux CI se usa `install --with-deps chromium`.

`browser/test_render.py` ejecuta el bloque inline real de renderizado de `index.html` en
Chromium. Dobla MapLibre y bloquea la red: verifica DOM, inyección, enlaces, fallback de logos,
ciudad/filtros, descripción ES/EN y errores de carga. **No** verifica WebGL, tiles, rendimiento
ni FormSubmit real; esos requieren smoke test separado por HTTP.

`fixtures/security.json` contiene datos de ataque **sintéticos**, no instrucciones.
El contrato de URLs usa los mismos vectores en Python y JavaScript. El texto con etiquetas
es válido como texto literal: el render debe protegerlo incluso sin pasar por CI.

## Reutilización por Scout u otro importador

Importar `validate_companies`, `validate_ticker` y `load_json` desde
`scripts/validate_data.py` en este checkout. Los validadores retornan una lista de errores
(vacía si pasa); `load_json` lanza `ValueError` para JSON inválido/ambiguo y `OSError` si falla
la lectura. No copiar reglas a otro repositorio. También existe la interfaz CLI:

```powershell
python scripts/validate_data.py --companies ruta/candidatos.json --ticker ticker.json
```

Salida 0 si pasa; 1 ante un error, con rutas de campos en stderr. El importador debe validar
su candidato antes de reemplazar un destino y conservarlo intacto si hay errores.
El esquema V1 aún requiere coordenadas para toda entrada publicada, incluso si el formulario
acepta una propuesta remota sin pin.

## Importación desde Coworking Scout

`scripts/import_scout.py` consume únicamente `perugrid.scout.v1`. Por defecto realiza un
dry-run; `--write` es la única forma de reemplazar atómicamente el destino:

```powershell
python scripts/import_scout.py --package ruta/scout.json
python scripts/import_scout.py --package ruta/scout.json --companies ruta/companies.json --write
```

El contrato exige sedes verificadas y elegibles, coordenadas dentro de Lima o Arequipa y todas
sus fuentes públicas, redistribuibles y elegibles. Rechaza proveedores Google, URLs con
credenciales, puerto, query o fragmento, versiones/campos desconocidos y conflictos de sede.
Una segunda importación idéntica informa `added=0, unchanged=1` y no reescribe el archivo.

`fixtures/scout_perugrid_v1.json` se generó con el exportador real de Scout a partir de su
fixture `synthetic_perugrid_candidate.json`; contiene solo nombres, URLs e IDs sintéticos. La
prueba integral usa una copia temporal de las 90 entradas y nunca agrega la sede a este repo.
