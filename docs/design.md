# Proyecto de mapa Costa Verde: marca y sistema de diseño

## Resumen

- **Concepto:** sistema de mapas digitales que mezcla la Costa Verde de Lima —acantilados,
  océano y parques urbanos— con una estética tecnológica limpia y de alto rendimiento.
- **Paleta:** esmeralda cibernético, pizarra oceánica profunda y blanco costero, con detalles de
  neón de alta visibilidad.
- **Identidad visual:** topografía geométrica, iconografía minimalista y layouts estructurados
  para una experiencia clara y fluida.

---

## 1. Concepto y visión de marca

El proyecto traduce la geografía singular de la costa del Pacífico limeño a una interfaz digital
precisa y moderna. Equilibra la energía orgánica de los acantilados con tecnología estructural y
basada en datos.

- **Aspecto natural:** gradientes de océano profundo, acantilados grises con vegetación y
  horizontes abiertos.
- **Aspecto tecnológico:** redes vectoriales, superposiciones de datos nítidas, paneles de alto
  contraste y telemetría interactiva continua.

El sistema se aleja de los mapas retro para crear una plataforma profesional de navegación urbana
y análisis geoespacial.

---

## 2. Paleta de color

La paleta reúne océano Pacífico, vegetación costera e infraestructura tecnológica. Combina tonos
estructurales contenidos con acentos eléctricos que facilitan leer datos.

### Colores principales

- **Esmeralda cibernético (`#1DA842` / `#05DC60`):** representa parques de acantilado y zonas
  de parapente; aporta brillo neón a acentos, botones y rutas de datos activas.
- **Pizarra oceánica (`#2B3342` / `#1B222C`):** azul grisáceo profundo usado en fondos,
  paneles oscuros y estructura tipográfica principal.
- **Concha de acantilado (`#F4F6F9`):** blanco frío que reduce el brillo de pantalla y mantiene
  los layouts nítidos.

### Acentos de datos y estado

- **Coral de parapente (`#FF6B6B`):** avisos visibles, marcadores POI y rutas críticas de
  telemetría.
- **Faro (`#FFB400`):** resaltados de búsqueda, foco de ubicación y capas interactivas
  secundarias.

---

## 3. Tipografía

La tipografía usa sans serif geométricas y limpias para conservar legibilidad durante el paneo y
zoom interactivos.

### Fuente principal de interfaz y display: **Inter / Plus Jakarta Sans**

- **Uso:** encabezados, capas del mapa, coordenadas y tarjetas de datos.
- **Características:** altura x alta, contraformas abiertas y claridad en escalas pequeñas.
- **Escala:**
  - `H1 (títulos principales)`: 22 pt, negrita, tracking `-0.02em`.
  - `H2 (encabezados de sección)`: 14 pt, seminegrita, tracking `-0.01em`.
  - `H3 (subtítulos / tarjetas)`: 11 pt, peso medio, tracking `0`.
  - `Texto base`: 10 pt, regular, interlineado `1.5`.

### Fuente monoespaciada y telemetría: **JetBrains Mono / SF Mono**

- **Uso:** latitud/longitud, registros de estado, distancias de capas y métricas calculadas.
- **Características:** ancho fijo para evitar saltos de texto durante actualizaciones de métricas.

---

## 4. Iconografía y símbolos

Los iconos siguen un enfoque minimalista de cuadrícula vectorial. Todos usan un grosor uniforme
(1.5 px o 2 px) y formas abiertas que evocan planos técnicos o un HUD.

- **El faro:** representa comando central, puntos de anclaje o ubicaciones base del usuario.
- **Arco de parapente:** simboliza anillos de alcance, campo de visión, cobertura o cambios de
  elevación en tiempo real.
- **Gradiente del acantilado:** vectores topográficos paralelos que muestran elevación, escaleras
  y rampas de acceso en la costa.
- **Vía costera (Circuito de Playas):** rutas dobles con iluminación neón para autopistas,
  trayectos rápidos y vectores de tráfico.

---

## 5. Arquitectura de interfaz y cuadrícula

La interfaz minimalista, orientada a cuadrícula, funciona como una ventana transparente sobre el
mapa.

- **Paneles de vidrio flotante:** barras laterales y controles con `backdrop-filter: blur(12px)`
  y bordes finos `#2B3342`, legibles sin bloquear el terreno.
- **Composición:** paneles a la izquierda para herramientas y filtros; zonas inferiores derechas
  para telemetría, zoom y escala.
- **Listas con franjas:** datos tabulares con tintes alternos sutiles, sin líneas pesadas.

---

## 6. Filosofía de composición y fotografía

Los visuales mezclan tomas de dron de alto contraste de la costa limeña con gráficos vectoriales
limpios.

- **Ángulos:** vistas aéreas amplias y elevadas que enfatizan el borde entre ciudad y océano.
- **Composición:** diagonales fuertes que siguen la curva de los acantilados para aportar ritmo.
- **Texturas:** mar suave frente a concreto geométrico y asfalto organizado.
