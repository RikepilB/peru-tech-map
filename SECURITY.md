# Política De Seguridad

Peru Grid es un sitio estático, sin dependencias (`index.html` + dos archivos de datos
JSON, sin backend, sin base de datos, sin autenticación). La superficie de ataque es
pequeña, pero si encuentras algo, repórtalo de manera responsable.

## Reportar Una Vulnerabilidad

**No abras un issue público para reportes de seguridad.** En su lugar, usa el flujo de
reporte privado de GitHub:

👉 [Reportar una vulnerabilidad](../../security/advisories/new)

Esto incluye cosas como:
- Vectores de XSS o inyección en cómo `index.html` renderiza `companies.json`/`ticker.json`
- Problemas con el flujo de envío del formulario "Agregar Empresa"
- Cualquier forma de hacer que el sitio cargue/ejecute contenido no confiable

Recibirás una respuesta tan pronto como el mantenedor lo vea — este es un proyecto
mantenido por una sola persona, así que no hay un SLA formal, pero los reportes se toman en
serio y se priorizan por encima del trabajo de nuevas funcionalidades.

## Versiones Soportadas

Solo hay una versión desplegada (`master`, en vivo en [perugrid.com](https://perugrid.com)).
Las correcciones se aplican ahí directamente — no hay una versión anterior a la cual
retroportar.

## Alcance

Fuera de alcance: los servicios de terceros de los que depende este sitio (MapLibre GL,
hosting de tiles de OpenFreeMap, FormSubmit, Vercel). Repórtalos directamente a sus propios
mantenedores.
