# Mapa del proyecto: guía Storybook de interfaz

Este documento es la fuente de verdad para agentes de layout y herramientas de generación de
código. Estructura el concepto de marca de `watermarked_img_18090315783402885778.png` en estados
de componentes, jerarquías tipográficas y tokens de assets, siguiendo la cuadrícula estructurada
de `image_fa34a6.jpg`.

## 1. Tokens centrales y configuración global

```json
{
  "project": "Sistema de interfaz del mapa Costa Verde",
  "theme": "Tecnología oscura / cuadrícula minimalista",
  "layout_rules": {
    "grid_unit": "8px",
    "border_radius": "12px",
    "backdrop_blur": "12px",
    "border_weight": "1.5px"
  },
  "color_palette": {
    "background_main": "#1B222C",
    "panel_bg": "rgba(43, 51, 66, 0.65)",
    "panel_border": "#2B3342",
    "cyber_emerald": "#1DA842",
    "neon_teal": "#05DC60",
    "paraglider_coral": "#FF6B6B",
    "lighthouse_beacon": "#FFB400",
    "text_primary": "#F4F6F9"
  }
}
```

## 2. Especificaciones de componentes

### A. Sistema tipográfico

Los agentes deben respetar esta jerarquía; no usar tamaños ni pesos fuera de estos tokens.

- **Título de display:** `Plus Jakarta Sans`, 700.
  - H1: 22 pt, tracking `-0.02em`, variante de mayúsculas.
  - H2: 14 pt, tracking `-0.01em`, estilo oración.
- **Lecturas de datos:** `JetBrains Mono`, 500.
  - Etiqueta de telemetría: 11 pt, color `#05DC60`.
  - Coordenadas: 10 pt, tracking `0`, sin espacios finales.

### B. Inventario de iconos y assets

Al incluir marcas del sistema o gráficos en paneles, usar estos nombres y claves literalmente.

| Símbolo / clave | Uso | Asset asociado |
| --- | --- | --- |
| `logo_costaverde` | Marca del encabezado | `watermarked_img_18090315783402885778.png` |
| `icon_lighthouse` | POI de anclaje / centro de control | `watermarked_img_18090315783402885778.png` |
| `icon_paraglider` | Indicador de cobertura / alcance | `watermarked_img_18090315783402885778.png` |
| `map_concept_topo` | Tarjeta de capa topográfica | `watermarked_img_18090315783402885778.png` |
| `layout_inspiration` | Arquitectura de cuadrícula oscura | `image_fa34a6.jpg` |

### C. Estados de interfaz

1. **Panel de vidrio flotante (`.panel-map-control`)**
   - Fondo: `rgba(43, 51, 66, 0.65)`.
   - Borde: `1.5px solid #2B3342`.
   - Filtro: `blur(12px)`.
   - Layout: flex vertical, 16 px de padding interno.
2. **Flujo de telemetría activo (`.data-row-active`)**
   - Texto: `#F4F6F9`.
   - Señal: barra izquierda `#05DC60`.
   - Filas pares con franja `rgba(27, 34, 44, 0.4)`.
3. **Marcador POI de aviso/crítico (`.marker-critical`)**
   - Color: `#FF6B6B`.
   - Asset: vector `icon_paraglider` embebido.
   - Estado: animación pulsante al recibir foco.

### Restricciones de layout

- El mapa cubre el 100 % del viewport; los controles viven únicamente en una capa absoluta
  flotante alineada a una cuadrícula de 8 px.
- En tarjetas con datos tabulares se usan divisores horizontales de 1 px en `#2B3342`, no
  bloques de color pesados.
- Las lecturas de telemetría usan métricas de ancho fijo para que los números no salten durante
  actualizaciones rápidas.

## Actualización editorial

La propuesta posterior explora una visualización geoespacial editorial de alta gama: serifas de
alto contraste para reflejar los acantilados de Lima junto a variables monoespaciadas precisas.
Este enfoque es de referencia; la implementación actual conserva la pareja sans + mono aprobada
en `docs/plans/2026-07-06-costa-verde-rebrand-design.md`.

```json
{
  "project": "Sistema de interfaz del mapa Costa Verde",
  "theme": "Tecnología editorial / cuadrícula geográfica de lujo",
  "typography_philosophy": "Contraste estructural: serifas dramáticas para la Costa Verde y monoespaciadas estrictas para precisión técnica."
}
```

### Pareja tipográfica editorial de referencia

1. **Marca y encabezados estructurales:** Playfair Display, Bodoni FLF o The Seasons; serif de
   alto contraste, negrita o cursiva. Se usaría en logo, zonas geográficas y títulos principales.

   ```css
   h1.brand-title {
     font-family: 'Playfair Display', 'Bodoni FLF', serif;
     font-weight: 700;
     letter-spacing: -0.03em;
     text-transform: none;
   }
   ```

2. **Subencabezados estructurados:** Sánchez, serif slab regular para títulos de tarjetas,
   telemetría y categorías de filtros.
3. **Telemetría y salida geoespacial:** JetBrains Mono, Nano Light o Geo Light para latitud,
   longitud, elevación, escala y registros de estado.

   ```css
   .telemetry-readout {
     font-family: 'JetBrains Mono', monospace;
     font-weight: 300;
     text-transform: uppercase;
     letter-spacing: 0.05em;
   }
   ```

### Boceto de cuadrícula visual

```text
+-----------------------------------------------------------------------+
|  [COSTA VERDE] (Playfair Display en negrita editorial)                |
|  Ancla El Faro // sistema de telemetría v2.06                         |
+-----------------------------------------------------------------------+
|                                                                       |
|   [ PANEL: ZONA DE VUELO ] (subencabezado Sánchez)                   |
|   -----------------------------------------------------------------   |
|   ALTITUD: 148 m        LAT: -12.1287                                |
|   VELOCIDAD: 24 nudos   LON: -77.0315                                |
|   [JetBrains Mono — bloques de datos de ancho fijo]                  |
|                                                                       |
+-----------------------------------------------------------------------+
```

### Refinamientos de componentes

- **Encabezado (`.ui-header-main`):** alinea el título de marca con una serifa cruda sobre fondo
  oscuro para lograr una interfaz geoespacial editorial.
- **Etiquetas de datos (`.label-mono-mini`):** usa `letter-spacing: 0.1em` para equilibrar las
  serifas de alto contraste. Evita fuentes sans de relleno.
