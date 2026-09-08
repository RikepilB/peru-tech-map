# Decisiones (registro ADR)

> Una entrada por decisión relevante. La más reciente va arriba. Solo se agregan entradas.

## Plantilla

```
### <AAAA-MM-DD> — <título de decisión>
- **Contexto:** por qué surgió
- **Decisión:** qué se eligió
- **Alternativas:** qué se descartó y por qué
- **Consecuencias:** a qué nos compromete
```

### 2026-09-08 — Taxonomía explícita con migración expand/contract

- **Contexto:** `funding.type` mezclaba categoría, etapa y estado de adquisición. PG-02 debía
  migrar 90 entradas sin perder compatibilidad ni inventar etapas.
- **Decisión:** cada fila recibe `category`; `subcategory` queda limitada a Startup con
  `Pre-Seed`, `Seed`, `Bootstrap` o `Series A+`. Se conservó `funding` como campo heredado y el
  lector prefiere la taxonomía nueva con fallback a la anterior. El resultado es: 40 Startup,
  12 Technology Consultancy, 17 Coworking Space, 8 Incubator, 3 Accelerator, 4 VC y 6 Nonprofit.
  Belatrix se clasificó como consultora; Dentito y Joinnus como startups adquiridas; UTEC
  Ventures, Wayra y LIQUID como aceleradoras; PECAP como Nonprofit por ser una asociación.
  Los demás registros Incubator permanecen así cuando el texto existente no permite separar con
  certeza incubación de aceleración. Los tres valores heredados `Revenue` no se convirtieron a
  `Bootstrap`: se omitió `subcategory` porque facturación no demuestra autofinanciación.
- **Alternativas:** convertir todo `Fund` a VC, todo `Incubator` a Accelerator o `Revenue` a
  Bootstrap. Se descartaron porque transformarían asociaciones, programas mixtos o falta de
  evidencia en hechos nuevos.
- **Consecuencias:** el formulario y el validador aceptan solo la taxonomía pública. PG-03 puede
  rediseñar filtros sobre ella; retirar `funding` requiere una fase contract posterior.

### 2026-07-06 — Se omitieron seis entidades de un directorio de Lima aportado por el usuario

- **Contexto:** se recibió un directorio de unas 30 startups, fondos y aceleradoras de Lima. Dos
  agentes de investigación contrastaron cada entrada con SUNAT/RUC, sitios oficiales,
  Crunchbase/YC/PitchBook y LinkedIn antes de añadir un pin.
- **Decisión:** se añadieron 20 entidades en `companies.json` y se omitieron seis:
  - **Ovenfo:** sin LinkedIn, Crunchbase ni dominio funcional; la única fuente era un blog con
    texto genérico reutilizado. Probablemente no es una empresa activa y diferenciada.
  - **Artificio:** existe y tiene cobertura, pero no hay oficina verificable; no se pueden crear
    coordenadas.
  - **Domus AI:** existe y recibió reconocimiento de Forbes Perú y StartUp Perú, pero no hay
    distrito ni dirección verificable.
  - **Syntax** (`usesyntax.com`): existió, pero su propia página principal comunica su cierre.
  - **GoJom:** el dominio dirige a una venta de dominio; PitchBook la lista como cerrada en junio
    de 2024 y LinkedIn indica traslado de sede a Ciudad de México.
  - **MrPink VC:** es un fondo real, pero su sede está en Punta del Este, Uruguay; no corresponde
    a un mapa de Lima solo por tener inversiones peruanas.
- **Alternativas:** incluirlas con un pin de centro de ciudad o como fila sin pin. Se rechazaron:
  la primera inventa coordenadas y la segunda rompe la interacción central del mapa.
- **Consecuencias:** Artificio, Domus AI o Syntax podrán añadirse si aparece una dirección actual.
  Ovenfo y GoJom se mantienen excluidos salvo nueva evidencia. Talently y uDocz usan una
  coordenada genérica del centro de Lima por falta de dirección confirmada; Winnipeg Capital se
  colocó en San Isidro con evidencia de baja confianza. MindQube conserva el nombre y descripción
  de la lista original aunque su dominio redirige a Noobelab; debe verificarse antes de tratarlo
  como actual.
- **Valor nuevo de `funding.type`:** se añadió `Fund` para Salkantay Ventures, Winnipeg Capital,
  AVP Ventures y PECAP; usa el chip neutro como Startup, Consultancy, Coworking, Incubator y
  Nonprofit. Se actualizaron `MUTED_FUNDING_TYPES`, el selector del formulario, README y la
  plantilla de PR. Esta solución temporal se sustituirá por la taxonomía de `PLAN.md`.

### 2026-07-06 — `funding.type` se reutiliza como categoría

- **Contexto:** el esquema de BUILD416 exige una ronda VC real (`Seed`, `Series A`, `Public`,
  etc.). Muchas entradas de Lima y Arequipa son startups sin financiación conocida, consultoras,
  coworkings o incubadoras universitarias; inventar rondas contradiría la regla de no inventar
  hechos.
- **Decisión:** se conservó el objeto `funding` por compatibilidad visual, pero `type` pasó a
  contener categorías: `Startup`, `Consultancy`, `Coworking`, `Incubator`, `Nonprofit` o
  `Acquired` para Dentito. Las cinco primeras usan un chip neutro y `Acquired`/`Public` uno verde.
- **Alternativas:** inventar importes de financiación o eliminar el chip. Se rechazaron por
  fabricación de datos y pérdida de una señal visual útil, respectivamente.
- **Consecuencias:** el esquema se aleja del significado original de BUILD416. Está documentado
  en README y arquitectura para no confundirlo con financiación real; `PLAN.md` define la salida
  de esta solución temporal.

### 2026-07-06 — Sin logos locales; solo fallback del servicio de favicons

- **Contexto:** BUILD416 incluye `assets/logos/*.png` para empresas cuyos favicons no se ven bien.
  Descargar o redistribuir logos de terceros sin confirmar cada archivo no era apropiado y muchas
  entradas no tienen un activo público disponible.
- **Decisión:** usar el servicio `s2/favicons` de Google a partir de `domain`; si no existe, usar
  una ficha con la inicial. Varias entradas de Arequipa no tienen sitio público confirmado.
- **Alternativas:** descargar logos por empresa o no mostrar logos/iniciales. Se descartaron por
  derechos, consentimiento, mantenimiento y peor diferenciación visual.
- **Consecuencias:** la calidad visual depende de la disponibilidad y cobertura de Google. Un
  colaborador puede añadir `assets/logos/<nombre>.png` y un campo `logo` si necesita reemplazar
  un caso concreto.
