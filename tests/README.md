# Pruebas

> Las pruebas definen el comportamiento esperado y son una señal de calidad para los agentes.

- `unit/`: funciones puras, componentes y lógica aislada.
- `integration/`: rutas API, operaciones de base de datos y límites entre módulos.
- `e2e/`: flujos críticos de usuario de extremo a extremo.

## Ejecución

Todavía no hay una suite de pruebas automatizada. La CI actual valida los dos archivos JSON y
los campos obligatorios de `companies.json`.
