# Roadmap V2 — Plataforma Administrada

> Milestone: [V2 — Plataforma Administrada](https://github.com/RikepilB/peru-tech-map/milestone/1)
> Epic: [#23](https://github.com/RikepilB/peru-tech-map/issues/23)

## Objetivo

Convertir Peru Grid de un sitio estático (`companies.json` + `index.html`) a una plataforma
administrada: Django + PostgreSQL + Django Admin como back-office interno, con un mapa público
que sigue siendo estático en el frontend (MapLibre) pero consume datos verificados desde base
de datos en vez de un JSON versionado a mano.

## Por qué

El flujo actual (editar `companies.json` a mano, PR, merge) no escala más allá de un
mantenedor solo. Cada dato nuevo requiere edición manual de JSON, verificación humana y
un ciclo de PR completo. V2 mueve esa verificación a un panel interno con estados
borrador → en revisión → publicado, sin abrir contribuciones públicas todavía.

## Orden de fases (dependencias)

```
#24 Fundación Django/Postgres/despliegue
        │
        ▼
#25 Modelo de datos + migración desde companies.json
        │
        ▼
#26 Back-office interno (Django Admin)
        │
        ▼
#27 API pública + mapa 3D
        │              │
        ▼              ▼
#28 Modo Trabajar   #29 Localización +
    remoto              longevidad
        │              │
        └──────┬───────┘
               ▼
     #30 Pruebas, seguridad,
         preparación de lanzamiento
```

- **#24 → #25**: no hay datos que migrar sin una app Django ejecutable primero.
- **#25 → #26**: el back-office edita lo que el modelo de datos define.
- **#26 → #27**: el mapa público solo debe leer registros ya publicados desde el back-office.
- **#27 → #28, #29**: ambos dependen de que el mapa público ya sirva datos publicados;
  pueden avanzar en paralelo entre sí.
- **#28, #29 → #30**: el lanzamiento requiere que las features estén completas para
  cubrirlas con pruebas y checklist de producción.

## Qué pasa con el backlog de V1 mientras tanto

V1 (el sitio estático actual) sigue siendo la fuente de verdad y se mantiene como fallback
hasta que V2 pase #30. La taxonomía de #17/#19 y las decisiones de DATA-01/#12 ya forman parte
de esa fuente y se migrarán desde `companies.json`. El backlog V1 que sigue abierto es:

- [#11](https://github.com/RikepilB/peru-tech-map/issues/11) — entradas de coworking/café
  pendientes de verificar (Regus/WeWork sedes adicionales, Casatomada, Caleta Dolsa,
  Biblioteca San Isidro — direcciones sin confirmar con precisión de pin).

El modo Trabajar remoto ya existe en V1. #28 conserva alcance V2 para migrar esa experiencia a
datos publicados por el backend/API, sin rebajar las reglas actuales de fuente y revisión.

Cualquier dato añadido a `companies.json` antes de [#25] se migra automáticamente — esa
migración parte precisamente de las 89 entradas actuales, no de un snapshot congelado.

## Fuera de alcance para V2 (explícito en los issues)

- Sin cuentas públicas ni contribuciones externas al back-office (#26).
- Sin precios/horarios/amenities de coworking sin fuente verificable (#28).
- Sin permisos granulares por usuario — un único set de administradores internos (#26).

## Criterio de "V2 listo para lanzar"

Todos los criterios de aceptación de #24–#30 cumplidos, CI verde, V1 sigue disponible como
rollback, y el checklist de producción de #30 completo.
