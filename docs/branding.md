# Marca

> Nombre, voz, audiencia e identidad visual. Quien escriba textos, mensajes de error o páginas
> de difusión debe usar este documento para mantener la coherencia de la marca.

## Nombre y lema

Peru Grid — «Donde están quienes construyen», en Lima y Arequipa.

## Audiencia

Personas que exploran el ecosistema tecnológico peruano: fundadores que buscan pares,
consultoras o coworkings; quienes buscan trabajo; y público curioso. No es una herramienta de
captación de leads ni un directorio comercial.

## Voz y tono

Operador de terminal, directo, técnico y sin exageraciones. Ejemplos: `GRID ONLINE ✓`,
`18 LUGARES INDEXADOS`, `[grid] Foo omitida: coordenadas fuera del bbox central`. Sin adjetivos
de marketing ni signos de exclamación.

## Identidad visual

Consola monocromática casi negra con verde Cyber Emerald como único acento: `#1DA842` para
CTAs, chips y estados activos, y `#05DC60` para enlaces, foco y estados destacados. La interfaz
usa Plus Jakarta Sans y reserva JetBrains Mono para datos de consola. Aún no hay logo de marca.

## Problema y solución

El ecosistema startup y tecnológico peruano —Lima y, cada vez más, Arequipa mediante incubadoras
universitarias— no tenía un índice visual único de dónde están quienes construyen. Peru Grid lo
resuelve con un mapa autocontenido, sin backend: se elige una ciudad, se ven los lugares
indexados como pines y se consulta su actividad y organización.

## Página Scout — intención de diseño

Audiencia: personas que quieren investigar lugares y operadores que aportan evidencia al mapa.
Acción principal: comenzar con Scout local; secundaria: volver al mapa para explorar sin instalar.
La página /scout/ explica investigar → revisar → exportar, seguida por una guía CLI breve y enlaces
al contrato real. Inspiración estructural: Voidscape docs/agents/index.md y README, que separan
primer resultado, comandos y capacidades disponibles. Se conserva la marca PeruGrid: fondo carbón,
verde, Plus Jakarta Sans, terminal monoespaciada y tipografía grande alineada a la izquierda.
Sin claims de integraciones listas ni formulario que simule una API remota. Una guía estática con
comandos copiables es el alcance; el motor Scout se ejecuta localmente. Responsive a 390/1440 px,
contraste legible, foco visible, anchors nativos y copia con error accesible. No recoge datos nuevos.


Revisión Scout: PASS visual a 1440 y 390 px; jerarquía izquierda, terminales con wrap y sin overflow.
PASS funcional: anchors, detalles nativos, copia y denegación del portapapeles. La CI incluye el
recorrido. Title, description, canonical /scout/, favicon y enlaces a contratos reales presentes.
Privacidad/antibot: no aplica a esta página sin formulario; no se añade analítica. Operación: el
mismo despliegue estático y rollback de docs/operations.md. Comandos status/list/export comprobados
con Scout instalado y base temporal; no se ejecutaron APIs pagadas ni conectores remotos.
