# Reconciliación DATA-01: sedes y candidatos

Fecha de revisión: 2026-09-09. Alcance: issues [#11](https://github.com/RikepilB/peru-tech-map/issues/11)
y [#12](https://github.com/RikepilB/peru-tech-map/issues/12), más los pins históricos de baja
confianza detectados durante la integración con Coworking Scout.

## Criterio

Una sede se publica solo cuando tiene identidad, dirección y coordenadas de una fuente pública
compatible con el dataset. Cada sucursal conserva un `site_id` propio aunque comparta marca.
Una dirección sin coordenada exacta queda pendiente; no se usa el centro de Lima ni una sede
parecida. Precios, horarios, Wi-Fi y otras condiciones variables quedan fuera mientras no exista
evidencia atribuible y vigente.

Los campos `sources` de `companies.json` apuntan a objetos de OpenStreetMap porque sus datos se
pueden redistribuir bajo ODbL. Las páginas oficiales enlazadas abajo corroboran identidad y
dirección, pero no se copian como si otorgaran por sí solas derechos sobre todos sus contenidos.

## Sedes para trabajar

| Candidato | Decisión | Resultado y evidencia |
|---|---|---|
| WeWork San Isidro genérico | Reemplazar | Se divide en sedes reales; el pin genérico se retira. El [listado oficial de Lima](https://www.wework.com/es-LA/l/commercial-real-estate/lima) muestra cuatro ubicaciones. |
| WeWork Jorge Basadre 349 | Agregar | Dirección corroborada por [WeWork](https://www.wework.com/es-LA/buildings/jorge-basadre-349--lima); coordenada exacta en [OSM node 12074331669](https://www.openstreetmap.org/node/12074331669). |
| WeWork Real 2 | Agregar | Dirección corroborada por [WeWork](https://www.wework.com/buildings/real-2--lima); entrada 147 con coordenada exacta en [OSM node 6051577985](https://www.openstreetmap.org/node/6051577985). |
| WeWork José Larco 1232 | Pendiente | La [sede oficial](https://www.wework.com/es-LA/buildings/jose-larco-1232--lima) existe, pero el pin requiere revisión visual antes de publicar. |
| WeWork Andrés Reyes 338 | Pendiente | La [sede oficial](https://www.wework.com/es-LA/buildings/andres-reyes-338--lima) existe, pero el pin requiere revisión visual antes de publicar. |
| Regus Real Ocho | Corregir | Dirección corroborada por [Regus](https://www.regus.com/en-us/peru/lima/real-ocho-3244); torre y coordenada en [OSM way 465801675](https://www.openstreetmap.org/way/465801675). |
| Otras sedes Regus | Pendiente | El [listado oficial](https://www.regus.com/en/pe/lima/matasango/office-space) cambia por producto; cada sede necesita dirección y pin propios. |
| Vallejo Librería-Café | Conservar | Dirección corroborada por [Heraldos Negros](https://www.heraldosnegros.com/especial/nuestras-tiendas/29/); coordenada en [OSM node 4332749851](https://www.openstreetmap.org/node/4332749851). |
| La Bodega Verde | Conservar | Dirección incluida en la [guía municipal](https://cdn.www.gob.pe/uploads/document/file/5599435/4970567-guia-de-cafeterias-bares-y-heladerias-esp.pdf); coordenada en [OSM node 4264082491](https://www.openstreetmap.org/node/4264082491). |
| Sofá Café Barranco | Corregir | Dirección corroborada por [Sofá Café](https://www.sofacafeperu.com/ubicaciones); coordenada en [OSM node 4264659693](https://www.openstreetmap.org/node/4264659693). |
| Biblioteca Municipal de Barranco | Corregir | Dirección corroborada por la [Municipalidad de Barranco](https://munibarranco.gob.pe/portal/cultura-biblioteca/); coordenada en [OSM way 512088042](https://www.openstreetmap.org/way/512088042). |
| Biblioteca Municipal de San Isidro | Agregar | Servicio y sede corroborados en [gob.pe](https://www.gob.pe/47898-acceder-a-los-servicios-de-la-biblioteca-municipal-de-san-isidro); coordenada en [OSM node 2545745705](https://www.openstreetmap.org/node/2545745705). |
| Café Sur | Pendiente | La [Librería Sur](https://www.libreriasur.com.pe/) permite corroborar la sede, pero no se encontró un POI exacto redistribuible. |
| Casatomada Librería-Café | Pendiente | El [contacto oficial](https://casatomadalibreriacafe.com/contacto-2/) publica la dirección; falta validar un pin exacto. |
| Caleta Dolsa | Pendiente | La dirección pública difiere entre 223 y 227 de Av. San Martín; la [guía municipal](https://cdn.www.gob.pe/uploads/document/file/5599435/4970567-guia-de-cafeterias-bares-y-heladerias-esp.pdf) no resuelve el conflicto. |
| Cafetería de Consumo Mínimo | Rechazar | Descripción genérica sin identidad, dirección ni fuente de una entidad individual. |

## Empresas y pins históricos

| Candidato | Decisión | Resultado y evidencia |
|---|---|---|
| MindQube | Retirar pin | El producto vigente se presenta como [Noobelab](https://noobelab.com/) y publica una dirección distinta; no existe un pin exacto verificado para reingresarlo. |
| Talently | Retirar pin | La [política oficial](https://talently.tech/en/privacy-policy) no demuestra una oficina pública vigente en el pin genérico de Lima. |
| uDocz | Retirar pin | El [contacto oficial](https://www.udocz.com/contact) no publica oficina física; el pin genérico carecía de evidencia. |
| Tekton Labs | Pendiente | El [contacto oficial](https://www.tektonlabs.com/contact-us) resuelve la dirección contradictoria anterior, pero falta un pin exacto. |
| Netzun | Pendiente | Los [términos publicados](https://develop.netzun.com/terminos-y-condiciones) y otros perfiles muestran direcciones incompatibles; también se corrige el nombre candidato “Netzum”. |
| TuRuta / TuMicro | Pendiente | El [sitio actual](https://turuta.org/) no publica una oficina física vigente. |
| Juntoz | Rechazar como startup independiente | Sus [términos](https://juntoz.com/contenido/terminos-y-condiciones-604) identifican a Axis Representaciones S.A.C. como operador. |
| Hub UDEP | Rechazar por ciudad | La [operación documentada por UDEP](https://www.udep.edu.pe/vidauniversitaria/piura/emprendedores/) está en Piura, fuera del alcance Lima/Arequipa. |
| Phantasia | Rechazar como entidad independiente | [WPP adquirió la mayoría](https://www.wpp.com/en/news/2015/01/wunderman-acquires-majority-stake-in-digital-marketing-agency-phantasia-in-peru) y luego integró las marcas en VML. |
| IMPAQTO | Rechazar como sede peruana | El [listado oficial](https://impaqto.net/coworking/) muestra sedes propias en Ecuador; Perú figura como aliado sin dirección propia. |
| Wynwood House | Rechazar del lote de ecosistema | Sus [términos](https://wynwood-house.com/terms-of-service/?lang=en) corresponden a alojamiento y no publican una oficina visitable de coworking o tecnología en Lima. |

## Resultado aplicado

- 89 entidades: 37 startups y 19 lugares de trabajo, sin perder las demás categorías.
- Ocho sedes con el grupo completo `site_id`, `organization_id`, `workspace_type` y `sources`.
- Dos sucursales WeWork independientes, Regus Real Ocho corregido y dos bibliotecas municipales.
- MindQube, Talently y uDocz salen del mapa hasta que exista evidencia geográfica suficiente.
- Los pendientes continúan como backlog editorial y no se convierten en coordenadas aproximadas.
