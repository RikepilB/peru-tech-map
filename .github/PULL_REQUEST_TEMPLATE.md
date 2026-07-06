<!--
Thanks for contributing to Peru Grid! Fill out the relevant section below.
All PRs are reviewed by the maintainer before merging.
-->

## What Kind Of Change Is This?

- [ ] Adding a new company/place
- [ ] Correcting an existing entry (coordinates, funding/category, domain, etc.)
- [ ] Updating the ticker
- [ ] Code / design change
- [ ] Other (describe below)

---

## If Adding Or Editing A Company

**Name:**

**City:** <!-- Lima or Arequipa -->

**Address (In The Mapped Area):**

**Website / Domain:**

**Category:** <!-- Startup, Consultancy, Coworking, Incubator, Nonprofit, Fund, or Acquired -->

**Source:** <!-- link to announcement, company site, press release, etc. -->

### Checklist

- [ ] Coordinates fall inside the city's core bbox — Lima `[-77.20,-12.35]→[-76.90,-11.95]`, Arequipa `[-71.60,-16.50]→[-71.45,-16.30]`
- [ ] `domain` (if set) is a bare domain (no `https://`, no `www`) that resolves to a real favicon
- [ ] This entry isn't already in `companies.json` (no duplicate)
- [ ] JSON is valid: `python3 -m json.tool companies.json > /dev/null` passes
- [ ] I ran it locally and confirmed the pin lands in the right place

---

## If A Code / Design Change

**What Does It Do?**

**How Did You Test It?**

- [ ] Ran locally over HTTP and confirmed the map loads and the loader dismisses
- [ ] Markers stay pixel-locked when panning/zooming
- [ ] No new dependencies; still a single self-contained `index.html`
- [ ] Solarium green (`#056540`) remains the only accent color

---

## Anything Else?

<!-- Context, screenshots, questions for the maintainer -->
