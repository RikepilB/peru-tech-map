# PERF-02: caché pública e invalidación comprobable

Fecha: 2026-09-10
Entorno: Vercel, `https://www.perugrid.com`

## Resultado

PeruGrid declara `Cache-Control: public, max-age=0, must-revalidate` para `/`,
`/index.html`, `/companies.json` y `/ticker.json`. Las URLs siguen siendo estables y cada
navegación puede reutilizar una representación almacenada únicamente después de revalidar su
ETag. Esto permite retirar una sede en el siguiente despliegue sin una ventana de datos viejos.

No se añadió service worker, Redis, manifest ni TTL relajado. El tamaño actual de 89 lugares no
justifica esas capas y un TTL permitiría mostrar temporalmente un retiro ya publicado.

## Evidencia anterior al cambio

El reporte [perf02-cache-before-2026-09-10.json](perf02-cache-before-2026-09-10.json) corresponde
al despliegue `dpl_BD5mfg7khkkk6ViE8zT7aHqAY5FP`, commit
`fe4bd622e23b6f84f3560a132136a414c62aa2b3`.

| Recurso | Respuesta | Revalidación | ETag | Estado Vercel |
|---|---:|---:|---|---|
| `/` | 200, 98.401 bytes | 304 sin cuerpo | `4106e25f…` | HIT |
| `/index.html` | 200, 98.401 bytes | 304 sin cuerpo | `4106e25f…` | HIT |
| `/companies.json` | 200, 89 registros | 304 sin cuerpo | `7af06a81…` | HIT |
| `/ticker.json` | 200, 16 registros | 304 sin cuerpo | `beb43f1d…` | HIT |

El verificador también confirmó que ambos JSON desplegados coinciden semánticamente con los
archivos revisados del repositorio y que `WeWork San Isidro`, `MindQube`, `Talently` y `uDocz`
siguen ausentes. El reporte conserva hashes, tamaños, headers, commit y despliegue; nunca guarda
los cuerpos recibidos.

## Evidencia del preview

El reporte [perf02-cache-preview-2026-09-10.json](perf02-cache-preview-2026-09-10.json) verificó
el despliegue protegido `dpl_AVRLx5PQcvvX4uupnTxhJ1XLd2CW`, commit
`30bbbb3fc397cb99f9501459777d178e1de3a4f9`, mediante `vercel curl` autenticado. Los cuatro
recursos devolvieron la política exacta, 304 sin cuerpo y una repetición HIT. Los 89 lugares y 16
titulares coincidieron semánticamente con el checkout y conservaron sus hashes de contenido.

La respuesta HTML protegida añadió 163 bytes y presentó como débil el mismo ETag de contenido;
por eso la comparación registra `/` e `/index.html` como distintos del dominio público. Este
efecto del preview no se interpreta como un cambio del `index.html` fuente.

## Evidencia de producción

El reporte [perf02-cache-production-2026-09-10.json](perf02-cache-production-2026-09-10.json)
verificó `https://www.perugrid.com` después del merge, en el despliegue
`dpl_7Wn4GD8TjhEs7KsU35MXTgq99iKK` y commit
`1b083826159a00f01dba9e2f910601e74ed8fa64`. Los cuatro cuerpos y ETags coincidieron con la
línea base; cada primera lectura fue MISS, la repetición fue HIT y la revalidación devolvió 304
sin cuerpo. Los JSON coincidieron con el checkout y los cuatro retiros históricos continuaron
ausentes. Con esta evidencia queda cerrado PERF-02.

## Gate de despliegue

Desde la raíz del checkout que representa el despliegue:

```powershell
python scripts/verify_cache.py `
  --expect-local-data `
  --require-vercel `
  --expect-absent-name "WeWork San Isidro" `
  --expect-absent-name "MindQube" `
  --deployment-id <deployment-id> `
  --git-commit <commit> `
  --output cache-report.json
```

Para un preview protegido, el Vercel CLI debe estar autenticado y el checkout enlazado al proyecto.
`--vercel-deployment` delega el acceso a `vercel curl`; el verificador no lee ni imprime el
token de bypass, no enlaza el checkout automáticamente y registra el target realmente consultado.

Cada recurso debe responder 200 con ETag y las tres directivas declaradas. La repetición debe
conservar cuerpo y ETag; `If-None-Match` debe devolver 304 sin cuerpo. Este 304 es el gate HTTP de
reutilización: el navegador puede usar su representación almacenada después de validarla. El
benchmark local no simula CDN y no sustituye esta prueba contra el despliegue real.

Para una publicación que cambie el dataset y retire una sede:

```powershell
python scripts/verify_cache.py `
  --base-url <immutable-preview-url> `
  --vercel-deployment <dpl-id> `
  --require-vercel `
  --compare cache-before.json `
  --expect-changed /companies.json `
  --expect-local-data `
  --expect-absent-site-id <site-id> `
  --output cache-after.json
```

El comando falla si cambia el cuerpo sin cambiar el ETag, si cambia el ETag sin cambiar el
cuerpo, si cambia un recurso inesperado, si el JSON público difiere del aprobado localmente o si
el registro retirado todavía aparece. Para comprobar un rollback:

```powershell
python scripts/verify_cache.py --expect-rollback cache-before.json
```

`deployment-id` y `git-commit` son anotaciones del operador; se contrastan con la inspección del
despliegue y no se deducen de los headers. El verificador HTTP no registra CDP; el 304 sin cuerpo
es el gate de protocolo para que un cliente reutilice su representación validada.

El rollback debe restaurar exactamente hashes y ETags. Una pestaña que ya está abierta conserva
su dataset en memoria hasta navegar o recargar; PERF-02 no añade polling en segundo plano.
