# Rediseño Costa Verde — diseño (aprobado el 2026-07-08)

Sustituye la dirección Nazca Desert (`index-nazca.html`, conservado solo como referencia).
Inspiración: `docs/design.md`, `Map Project Storybook U.md` y
`docs/Gemini_Generated_Image_vel0pcvel0pcvel0.png`.

## Causa raíz resuelta

`themeBaseLayers()` en `index-nazca.html` recoloreaba agua, tierra y edificios con tonos arena
casi idénticos, eliminando el contraste: el terreno parecía un desierto plano. La rampa 3D de
`building-3d` (`#D8C9A8` a `#A38E6C`) se mezclaba con el mismo fondo y hacía que los edificios
parecieran desaparecer aunque el modo 3D estuviera activo.

## Decisiones

1. **Terreno del mapa intacto.** El prototipo clona el `index.html` real: tiles naturales de
   `openfreemap/liberty` y edificios 3D funcionales. El estilo Costa Verde se aplica solo a la
   interfaz flotante: encabezado, barra lateral, controles, barra de estado, ticker, modal,
   cargador y marcadores.
2. **Tipografía:** Plus Jakarta Sans para encabezados, etiquetas e interfaz; JetBrains Mono para
   coordenadas, estado y datos. Se descartó el giro posterior a serif editorial del Storybook
   (Playfair Display + Sánchez): sans + mono coincide mejor con la referencia y supone menos
   riesgo.
3. **Color de acento:** un único acento. Se reemplazó Solarium (`#056540`/`#0FA968`) por Cyber
   Emerald (`#1DA842`/`#05DC60`). Se eliminaron los acentos coral y ámbar para respetar la regla
   arquitectónica de un solo color de acento.
4. **Archivo:** se creó `index-costaverde.html` como hermano de `index.html`; el original no se
   tocó hasta aprobar el prototipo final.

## Tokens

```
--bg:           #1B222C   (antes #070A08)
--panel:        rgba(43,51,66,0.65)   (vidrio; antes #0C110D sólido)
--line:         #2B3342   (antes #16281D)
--green:        #1DA842   (antes #056540)
--green-bright: #05DC60   (antes #0FA968)
--text:         #F4F6F9   (antes #D6E2D8)
--muted:        #7C8794   (antes #6B7A6E)
--sans:         'Plus Jakarta Sans', system-ui, sans-serif
--mono:         'JetBrains Mono', ui-monospace, monospace   (antes Geist Mono)
--radius:       12px
--blur:         12px
```

## Componentes modificados

- `.brand`, `.ctl`/`#toggle3d`, `#panel`, `.modal`, `.loader`: bordes cuadrados a
  `border-radius: 12px`; fondo sólido a vidrio mediante `var(--panel)` y
  `backdrop-filter: blur(12px)`; borde de 1.5 px.
- `.panel-head h1`, `.modal-head h2`, `.brand`: fuente `--sans`; la mono queda reservada para
  telemetría real.
- `.statusbar`/`.ticker`: conservan el blur y la fuente mono; se reajustan a los nuevos tokens.
- `.co-marker`, `.co .logo`: anillo y borde pasan a esmeralda; la forma no cambia.

## Sin cambios

Archivos de datos, lógica JavaScript —carga de empresas, selector de ciudad y cálculo de
posicionamiento de marcadores— y campos del modal para agregar empresa: solo cambió la capa visual.
