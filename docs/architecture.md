# Arquitectura

> Patrones del sistema, límites lógicos y decisiones. Este documento es la referencia para
> planificar cambios y refleja, para personas, `.claude/rules/peru-tech-map-architecture.md`.

## Resumen

Un único HTML estático (`index.html`) y dos archivos de datos JSON (`companies.json`,
`ticker.json`). No hay compilación, framework, backend ni gestor de paquetes. MapLibre GL JS
renderiza el mapa y OpenFreeMap sirve los tiles vectoriales. La estructura parte de
[BUILD416](https://github.com/MapleBudget/toronto-tech-map) y añade el selector Lima/Arequipa.

## Módulos y límites

No hay módulos por diseño: todo vive en el único bloque `<script>` de `index.html`. Sus secciones
lógicas son: inicio y tematización del mapa; edificios/3D; carga de empresas y guardia de bbox;
marcadores con despliegue para coordenadas superpuestas; barra lateral; ticker; barra de estado;
modal para agregar empresa mediante FormSubmit; y cargador de arranque.

## Flujo de datos

1. `map.on("load")` aplica el tema oscuro, oculta las etiquetas POI y limita las etiquetas de
   vías a las principales.
2. `companies.json` se carga una vez en `ALL_COMPANIES`; `ticker.json` se carga por separado y
   se muestra como una cinta sin filtro por ciudad.
3. `applyCity(city)` filtra la ciudad activa, descarta entradas fuera de su bbox, reconstruye
   marcadores y barra lateral, y ajusta cámara, límites y zoom inicial.
4. Al seleccionar una fila o marcador, `selectCompany(i, fly)` desplaza la cámara, abre el popup
   temático y sincroniza el estado activo del marcador y de la barra lateral.

## Decisiones y restricciones

- **Taxonomía explícita.** `category` describe el tipo de entidad y `subcategory` solo una etapa
  respaldada de Startup. `funding` se conserva temporalmente para compatibilidad y no determina
  el valor público cuando existe la taxonomía nueva.
- **Sin logos locales.** Los marcadores usan el favicon de Google según `domain` y, cuando no
  existe, una ficha con la inicial; así se evita empaquetar logos de terceros.
- **Formulario activo.** `FORM_ENDPOINT` apunta a FormSubmit y requiere que el destinatario haya
  completado su verificación. Las contribuciones siguen revisándose manualmente antes de entrar
  al dataset.
