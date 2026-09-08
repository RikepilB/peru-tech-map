# Cómo Contribuir A Peru Grid

Gracias por querer ayudar a mapear el ecosistema tech del Perú. Cualquiera puede abrir un
pull request o issue — el mantenedor revisa y fusiona todo (ver [CODEOWNERS](./CODEOWNERS)).

Al participar, aceptas seguir el [Código de Conducta](./CODE_OF_CONDUCT.md).

---

## Formas De Contribuir

- **Agregar un lugar** — una startup, consultora, espacio de coworking, incubadora, fondo,
  u ONG con presencia real en Lima o Arequipa.
- **Corregir una entrada** — coordenadas incorrectas, dominio desactualizado, categoría
  desactualizada.
- **Reportar un bug** — algo roto en el mapa, la barra lateral, o el flujo de agregar empresa.
- **Mejorar el código** — `index.html` es toda la app (sin paso de compilación, sin framework).

Ninguna contribución es demasiado pequeña. Correcciones de typos y de un solo campo son
bienvenidas.

---

## Reglas Base

Este es un **sitio estático sin dependencias** — `index.html`, `companies.json`,
`ticker.json`, nada más. Los PRs que introduzcan un paso de compilación, un framework, o
una dependencia npm serán rechazados sin importar qué tan buena sea la idea. Si crees que
esta restricción necesita cambiar, abre un issue para discutirlo primero — no construyas
en contra de ella especulativamente.

---

## Agregar O Editar Un Lugar

1. Haz **fork** del repo y crea una rama: `add/<nombre-de-la-empresa>` o
   `fix/<qué-cambió>`.
2. Edita `companies.json` directamente — ver la sección [Formato De Datos](./README.md#formato-de-datos)
   en el README para el esquema y campos requeridos.
3. Valida tu JSON antes de abrir un PR:
   ```bash
   python scripts/validate_data.py
   ```
4. Corre el sitio localmente y confirma que tu pin cae en el lugar correcto:
   ```bash
   python3 -m http.server 8000   # luego abre http://localhost:8000
   ```
5. Abre un PR usando la plantilla — llena **nombre, ciudad, coordenadas, fuente**. Un
   enlace de fuente (sitio de la empresa, comunicado de prensa, LinkedIn) acelera mucho la
   revisión.

**Qué se acepta:**
- ✅ Empresas/lugares reales con presencia genuina y verificable en Lima o Arequipa.
- ✅ Correcciones de coordenadas/detalles a entradas existentes.
- ❌ Entradas fuera de los bounding boxes de las dos ciudades (ver README).
- ❌ Afirmaciones no verificables, copy de marketing, o entradas duplicadas.

---

## Cambios De Código / Diseño

1. Crea una rama desde `master` — nunca hagas commit directo a ella.
2. Mantén la arquitectura de un solo archivo: todo vive dentro del `<script>` y `<style>`
   inline de `index.html`. No lo dividas en módulos ni agregues un bundler.
3. Mantén el verde Solarium (`#056540` / `#0FA968`) como único color de acento.
4. Prueba localmente por HTTP (no `file://` — la app obtiene JSON en tiempo de ejecución y
   necesita CORS).
5. Abre un PR describiendo qué cambió y cómo lo probaste.

---

## Proceso De Pull Request

- CI ejecuta `scripts/validate_data.py` (JSON estricto, tipos, bbox, enums, URLs y duplicados),
  sus regresiones y pruebas DOM de render seguro. Ver [tests/README.md](tests/README.md).
  Playwright es solo una herramienta de pruebas; el sitio sigue sin framework ni compilación.
- [CODEOWNERS](./CODEOWNERS) solicita automáticamente la revisión del mantenedor en cada
  PR — nada se fusiona sin ella.
- Usa el estilo [Conventional Commits](https://www.conventionalcommits.org/) para los
  mensajes de commit (`feat:`, `fix:`, `docs:`, `chore:`, etc.) cuando sea práctico.
- Mantén los PRs enfocados — una empresa agregada, un bug corregido, una funcionalidad. Los
  PRs grandes y mixtos son más lentos de revisar.

---

## Reportar Issues

Usa las [plantillas de issue](../../issues/new/choose) — elige **Agregar Empresa**,
**Reportar Bug**, o **Solicitar Funcionalidad** según lo que estés reportando. Para
vulnerabilidades de seguridad, ve a [SECURITY.md](./SECURITY.md) en vez de abrir un issue
público.

---

## ¿Preguntas?

Abre una [discusión o issue](../../issues) — ninguna pregunta es demasiado básica.
