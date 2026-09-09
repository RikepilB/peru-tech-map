"""Importa un paquete público y revisado de Coworking Scout a PeruGrid."""
from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.validate_data import (
    BBOXES,
    canonical_scout_id,
    canonical_scout_text,
    company_identity,
    load_json,
    parse_json,
    validate_companies,
    validate_scout_sources,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "perugrid.scout.v1"
PACKAGE_FIELDS = {"schema_version", "records"}
RECORD_FIELDS = {
    "site_id", "organization_id", "name", "city", "workspace_type", "address",
    "lat", "lng", "review_state", "export_eligible", "sources",
}
CITY_MAP = {"Lima": "lima", "Arequipa": "arequipa"}
WORKSPACE_TYPES = {"coworking", "cafe", "library"}
MAX_RECORDS = 1000
MAX_PACKAGE_BYTES = 10 * 1024 * 1024
MAX_VALIDATION_ERRORS = 100


class ScoutImportError(ValueError):
    """El paquete no puede incorporarse sin violar el contrato publicado."""


@dataclass(frozen=True)
class ImportResult:
    companies: list[dict]
    records: int
    added: int
    unchanged: int

    @property
    def total(self) -> int:
        return len(self.companies)


def _finite_number(value: object) -> bool:
    return type(value) is int or (
        type(value) is float and value == value and value not in (float("inf"), float("-inf"))
    )


def _exact_fields(value: dict, fields: set[str], path: str, errors: list[str]) -> None:
    missing = fields - value.keys()
    extra = value.keys() - fields
    if missing:
        errors.append(f"{path}: faltan campos requeridos")
    if extra:
        errors.append(f"{path}: campos desconocidos")


def validate_scout_package(package: object) -> list[str]:
    """Devuelve errores deterministas para el contrato público de Scout."""
    if not isinstance(package, dict):
        return ["package: debe ser un objeto"]
    errors: list[str] = []
    _exact_fields(package, PACKAGE_FIELDS, "package", errors)
    if package.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"package.schema_version: debe ser {SCHEMA_VERSION}")
    records = package.get("records")
    if not isinstance(records, list):
        errors.append("package.records: debe ser un array")
        return errors
    if len(records) > MAX_RECORDS:
        errors.append(f"package.records: máximo {MAX_RECORDS} registros")

    seen_site_ids: set[str] = set()
    for index, record in enumerate(records[:MAX_RECORDS]):
        path = f"package.records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{path}: debe ser un objeto")
            continue
        _exact_fields(record, RECORD_FIELDS, path, errors)
        for field, maximum in (("site_id", 200), ("organization_id", 200),
                               ("name", 200), ("address", 500)):
            if not canonical_scout_text(record.get(field), maximum):
                errors.append(f"{path}.{field}: texto canónico requerido")
        site_id = record.get("site_id")
        if canonical_scout_text(site_id, 200):
            site_identity = canonical_scout_id(site_id)
            if site_identity in seen_site_ids:
                errors.append(f"{path}.site_id: identificador duplicado")
            seen_site_ids.add(site_identity)

        city = record.get("city")
        if not isinstance(city, str) or city not in CITY_MAP:
            errors.append(f"{path}.city: debe ser Lima o Arequipa")
        workspace_type = record.get("workspace_type")
        if not isinstance(workspace_type, str) or workspace_type not in WORKSPACE_TYPES:
            errors.append(f"{path}.workspace_type: valor no permitido")
        if record.get("review_state") != "verified":
            errors.append(f"{path}.review_state: debe ser verified")
        if record.get("export_eligible") is not True:
            errors.append(f"{path}.export_eligible: debe ser true")

        coordinates_ok = True
        for field in ("lat", "lng"):
            if not _finite_number(record.get(field)):
                errors.append(f"{path}.{field}: número finito requerido")
                coordinates_ok = False
        if isinstance(city, str) and city in CITY_MAP and coordinates_ok:
            bbox = BBOXES[CITY_MAP[city]]
            if not (bbox[0] <= record["lng"] <= bbox[2]
                    and bbox[1] <= record["lat"] <= bbox[3]):
                errors.append(f"{path}: coordenadas fuera del bbox de la ciudad")

        errors.extend(validate_scout_sources(record.get("sources"), f"{path}.sources"))
    if len(errors) > MAX_VALIDATION_ERRORS:
        return errors[:MAX_VALIDATION_ERRORS] + ["package: errores adicionales omitidos"]
    return errors


def _load_scout_package(path: str | Path) -> object:
    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_PACKAGE_BYTES + 1)
    if len(raw) > MAX_PACKAGE_BYTES:
        raise ScoutImportError("paquete Scout supera el límite de 10 MiB")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("JSON no usa UTF-8") from exc
    return parse_json(text)


def _mapped_company(record: dict) -> dict:
    return {
        "name": record["name"],
        "city": CITY_MAP[record["city"]],
        "address": record["address"],
        "lat": record["lat"],
        "lng": record["lng"],
        "category": "Coworking Space",
        "funding": {"type": "Coworking"},
        "site_id": record["site_id"],
        "organization_id": record["organization_id"],
        "workspace_type": record["workspace_type"],
        "sources": copy.deepcopy(record["sources"]),
    }


def _contract_error(prefix: str, errors: list[str]) -> ScoutImportError:
    return ScoutImportError(prefix + ":\n" + "\n".join(errors))


def plan_import(package: object, companies: object) -> ImportResult:
    package_errors = validate_scout_package(package)
    if package_errors:
        raise _contract_error("paquete Scout inválido", package_errors)
    company_errors = validate_companies(companies)
    if company_errors:
        raise _contract_error("dataset PeruGrid inválido", company_errors)
    assert isinstance(package, dict) and isinstance(companies, list)

    prospective = copy.deepcopy(companies)
    by_site_id = {
        canonical_scout_id(row["site_id"]): row for row in prospective
        if isinstance(row, dict) and "site_id" in row
    }
    identities = {company_identity(row) for row in prospective}
    added = 0
    unchanged = 0
    for record in sorted(package["records"], key=lambda item: item["site_id"]):
        mapped = _mapped_company(record)
        site_identity = canonical_scout_id(mapped["site_id"])
        existing = by_site_id.get(site_identity)
        if existing is not None:
            if existing == mapped:
                unchanged += 1
                continue
            raise ScoutImportError("conflicto: site_id existente tiene datos diferentes")
        identity = company_identity(mapped)
        if identity in identities:
            raise ScoutImportError("colisión: nombre, ciudad y coordenadas ya existen")
        prospective.append(mapped)
        by_site_id[site_identity] = mapped
        identities.add(identity)
        added += 1

    prospective_errors = validate_companies(prospective)
    if prospective_errors:
        raise _contract_error("resultado PeruGrid inválido", prospective_errors)
    return ImportResult(
        companies=prospective,
        records=len(package["records"]),
        added=added,
        unchanged=unchanged,
    )


def _atomic_json_write(path: Path, data: list[dict]) -> None:
    temp_name: str | None = None
    try:
        if path.is_symlink():
            raise ScoutImportError("destino companies: no se permite un enlace simbólico")
        destination_mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else None
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="\n", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temp_name = handle.name
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        if path.is_symlink():
            raise ScoutImportError("destino companies: no se permite un enlace simbólico")
        if destination_mode is not None:
            os.chmod(temp_name, destination_mode)
        os.replace(temp_name, path)
    except Exception:
        if temp_name:
            Path(temp_name).unlink(missing_ok=True)
        raise


def import_package(
    package_path: str | Path,
    companies_path: str | Path = ROOT / "companies.json",
    *,
    write: bool = False,
) -> ImportResult:
    destination = Path(companies_path)
    if write and destination.is_symlink():
        raise ScoutImportError("destino companies: no se permite un enlace simbólico")
    package = _load_scout_package(package_path)
    companies = load_json(destination)
    result = plan_import(package, companies)
    if write and result.added:
        _atomic_json_write(destination, result.companies)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--companies", type=Path, default=ROOT / "companies.json")
    parser.add_argument("--write", action="store_true",
                        help="reemplaza companies.json atómicamente; por defecto solo simula")
    args = parser.parse_args(argv)
    try:
        result = import_package(args.package, args.companies, write=args.write)
    except ScoutImportError as exc:
        print(f"ERROR — {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"ERROR — no se pudo leer o escribir JSON válido ({type(exc).__name__})", file=sys.stderr)
        return 1
    mode = "write" if args.write else "dry-run"
    print(f"OK — mode={mode}, records={result.records}, added={result.added}, "
          f"unchanged={result.unchanged}, total={result.total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
