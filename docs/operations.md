# Operación y rollback

Producción se publica desde `master` en Vercel y no tiene backend propio. Ante una regresión,
primero identifica el commit y deployment afectados en GitHub Actions y Vercel. Si el cambio aún
no está fusionado, no lo promociones. Si ya está en producción, restaura desde Vercel el último
deployment `Ready` conocido o prepara un `revert` en una rama y pásalo por el PR y CI normales;
no reescribas `master` ni fuerces un push.

Después de cada publicación comprueba la carga en escritorio y móvil, los dos JSON, el formulario
sin enviar datos de prueba y el contrato de caché descrito en
[`docs/performance/perf02-cache-contract-2026-09-10.md`](performance/perf02-cache-contract-2026-09-10.md).
Las excepciones del navegador y fallos de assets se inspeccionan en DevTools; el estado de build y
los logs de despliegue viven en Vercel. Vulnerabilidades siguen el canal privado de
[`SECURITY.md`](../SECURITY.md).
