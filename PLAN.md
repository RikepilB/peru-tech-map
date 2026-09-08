# Plan de implementación

## Objetivo

Consolidar a Peru Grid como un producto y repositorio orientados al público peruano: interfaz y
documentación en español, descripciones de empresas localizadas y una taxonomía de entidades que
no sobrecargue `funding.type`.

## Alcance y límites

- La prosa de usuario y la documentación activa del repositorio se mantiene en español.
- Los identificadores de código, valores literales del esquema, licencias y el historial
  inmutable de `docs/handoff/` no se traducen automáticamente.
- Se conserva la arquitectura estática: sin framework, backend ni paso de compilación.

## Fase 1 — Documentación y base de idioma

**Resultado:** documentación activa en español y el español como idioma inicial de la interfaz.

1. Traducir los documentos activos que todavía contienen prosa en inglés y corregir referencias
   que contradigan el comportamiento real del formulario.
2. Cambiar el idioma inicial del producto a español sin eliminar el selector EN/ES ni la
   preferencia guardada del usuario.
3. Verificar JSON, carga local por HTTP y los flujos principales en ambos idiomas.

**Riesgo:** el formulario de FormSubmit ya usa un destinatario real; la documentación debe
describirlo con precisión sin exponer información adicional.

## Fase 2 — Descripciones bilingües de empresas

**Resultado:** cada empresa puede mostrar una descripción en español sin romper los datos actuales.

1. Definir un campo de descripción localizado, compatible con las entradas existentes.
2. Actualizar el renderizado de marcador, panel lateral y popup para elegir el idioma activo.
3. Traducir y revisar las 75 descripciones, preservando nombres propios y términos técnicos.
4. Añadir validaciones de estructura para el nuevo campo.

**Dependencia:** fase 1.

## Fase 3 — Taxonomía y filtros

**Resultado:** categorías explícitas y subcategorías de financiación para startups.

1. Definir el esquema: `Startup` con subcategorías Pre-Seed, Seed, Bootstrap o Series A+, y
   categorías pares Incubator, Accelerator, VC, Nonprofit, Technology Consultancy y Coworking Space.
2. Migrar y verificar las 90 entradas sin inventar financiación ni coordenadas.
3. Reemplazar los toggles heredados por filtros coherentes con la nueva taxonomía.
4. Actualizar documentación, formulario de alta y CI.

**Dependencia:** fase 2 para evitar dos migraciones incompatibles del dataset.

## Endurecimiento transversal

Antes de ampliar contribuciones externas, incluir validaciones de valores permitidos, bbox,
duplicados y contenido seguro; escapar los valores provenientes de JSON antes de insertarlos en
HTML. Activar protección de rama en `master` requiere una acción del mantenedor en GitHub.

## Verificación por fase

- `python -m json.tool companies.json` y `python -m json.tool ticker.json`.
- Validación de campos obligatorios equivalente a `.github/workflows/ci.yml`.
- Servir localmente con `python -m http.server 8000` y comprobar carga, selector de ciudad,
  filtros, popup y formulario.
