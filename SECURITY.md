# Security Policy

Peru Grid is a static, zero-dependency site (`index.html` + two JSON data files, no
backend, no database, no auth). The attack surface is small, but if you find something,
please report it responsibly.

## Reporting A Vulnerability

**Do not open a public issue for security reports.** Instead, use GitHub's private
reporting flow:

👉 [Report a vulnerability](../../security/advisories/new)

This includes things like:
- XSS or injection vectors in `index.html`'s rendering of `companies.json`/`ticker.json`
- Issues with the "Add A Company" form submission flow
- Any way to make the site load/execute untrusted content

You'll get a response as soon as the maintainer sees it — this is a solo-maintained
project, so there's no formal SLA, but reports are taken seriously and prioritized over
feature work.

## Supported Versions

There's only one deployed version (`master`, live at [perugrid.com](https://perugrid.com)).
Fixes land there directly — there's no older version to backport to.

## Scope

Out of scope: the third-party services this site depends on (MapLibre GL, OpenFreeMap
tile hosting, FormSubmit, Vercel). Report those upstream to their own maintainers.
