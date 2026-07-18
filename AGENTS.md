# Guía del repositorio

> Instrucciones compartidas por **Claude Code** y **Codex**. Deben ser independientes de la
> herramienta; el flujo específico de Claude Code vive en `.claude/CLAUDE.md`.

## Estructura del proyecto y módulos

La aplicación vive en `index.html`; los datos están en `companies.json` y `ticker.json`.
No hay módulos, backend ni paso de compilación. Las pruebas futuras se organizan en `tests/`.

## Ejecución y validación

Sirve el proyecto mediante HTTP: `python -m http.server 8000`. La CI valida el JSON y los
campos obligatorios de las empresas en cada push y pull request.

## Estilo y convenciones

Respeta la arquitectura de un único archivo y el estilo existente. Usa español en la prosa de
cara al repositorio; conserva los identificadores y valores literales del esquema cuando sean
compatibles con el código.

## Pruebas

Agrega pruebas focalizadas cerca de la lógica modificada cuando existan. Ejecuta las
validaciones aplicables antes de entregar cambios importantes.

## Commits y pull requests

Usa commits convencionales (`feat:`, `fix:`, `docs:`, `test:`, `chore:`). Los PR deben incluir
el cambio visible, comandos de verificación, issue relacionado y notas de migración o UI.

## Seguridad y configuración

Nunca confirmes `.env*`, claves API, secretos OAuth ni artefactos subidos. Documenta las
variables requeridas en `.env.example`.
