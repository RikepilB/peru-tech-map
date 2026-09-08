<!--
¡Gracias por contribuir a Peru Grid! Completa la sección correspondiente abajo.
Todos los PRs son revisados por el mantenedor antes de fusionarse.
-->

## ¿Qué Tipo De Cambio Es Este?

- [ ] Agregar una nueva empresa/lugar
- [ ] Corregir una entrada existente (coordenadas, funding/categoría, dominio, etc.)
- [ ] Actualizar el ticker
- [ ] Cambio de código / diseño
- [ ] Otro (describir abajo)

---

## Si Agregas O Editas Una Empresa

**Nombre:**

**Ciudad:** <!-- Lima o Arequipa -->

**Dirección (Dentro Del Área Mapeada):**

**Sitio Web / Dominio:**

**Categoría:** <!-- Startup, Consultancy, Coworking, Incubator, Nonprofit, Fund, o Acquired -->

**Fuente:** <!-- enlace al anuncio, sitio de la empresa, comunicado de prensa, etc. -->

### Checklist

- [ ] Las coordenadas caen dentro del bbox central de la ciudad — Lima `[-77.20,-12.35]→[-76.90,-11.95]`, Arequipa `[-71.60,-16.50]→[-71.45,-16.30]`
- [ ] `domain` es un dominio sin esquema con ruta opcional segura; el favicon se obtiene del hostname
- [ ] Esta entrada no está ya en `companies.json` (sin duplicados)
- [ ] `python scripts/validate_data.py` pasa para ambos datasets
- [ ] Lo corrí localmente y confirmé que el pin cae en el lugar correcto

---

## Si Es Un Cambio De Código / Diseño

**¿Qué Hace?**

**¿Cómo Lo Probaste?**

- [ ] Lo corrí localmente por HTTP y confirmé que el mapa carga y el loader desaparece
- [ ] Los marcadores se mantienen fijos al hacer pan/zoom
- [ ] Sin dependencias nuevas; sigue siendo un `index.html` único y autocontenido
- [ ] El verde Solarium (`#056540`) sigue siendo el único color de acento

---

## ¿Algo Más?

<!-- Contexto, capturas, preguntas para el mantenedor -->
