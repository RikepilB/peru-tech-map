"""Validación de datasets V1, reutilizable por CI e importadores; nunca modifica datos."""
import argparse
import json
import math
from pathlib import Path
import re
import sys
import unicodedata
from datetime import datetime
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
BBOXES = {
    "lima": (-77.20, -12.35, -76.90, -11.95),
    "arequipa": (-71.60, -16.50, -71.45, -16.30),
}
FUNDING_TYPES = {"Startup", "Consultancy", "Coworking", "Incubator", "Nonprofit", "Fund", "Acquired", "Public"}
STAGES = {"Pre-Seed", "Seed", "Series A", "Series A+", "Series B", "Series C+",
          "Late Stage", "Revenue", "Acquired", "Public"}
CATEGORIES = {"Startup", "Incubator", "Accelerator", "VC", "Nonprofit",
              "Technology Consultancy", "Coworking Space"}
STARTUP_SUBCATEGORIES = {"Pre-Seed", "Seed", "Bootstrap", "Series A+"}
OPERATING_MODELS = {"On-Site", "Hybrid", "Remote"}
SCOUT_WORKSPACE_TYPES = {"coworking", "cafe", "library"}
SCOUT_SOURCE_FIELDS = {"provider", "source_url", "observed_at", "provenance_class",
                       "use_classification", "export_eligible"}
SCOUT_COMPANY_FIELDS = {"site_id", "organization_id", "workspace_type", "sources"}
COMPANY_FIELDS = {"name", "city", "lat", "lng", "funding", "domain", "logo", "logoDark",
                  "address", "tag", "tag_es", "operating_model", "category", "subcategory",
                  *SCOUT_COMPANY_FIELDS}
DOMAIN = re.compile(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}(?:/[a-zA-Z0-9._~/-]*)?", re.ASCII | re.IGNORECASE)
LOGO = re.compile(r"assets/logos/[a-zA-Z0-9][a-zA-Z0-9_-]*\.(?:png|jpg|jpeg|webp|gif)")


def safe_domain_url(value: object) -> str | None:
    """Dominio ASCII sin esquema, con ruta opcional heredada; contrato también probado en JS."""
    if not isinstance(value, str) or len(value) > 2048 or not DOMAIN.fullmatch(value):
        return None
    if len(value.split("/", 1)[0]) > 253:
        return None
    return "https://" + value


def safe_logo_path(value: object) -> str | None:
    if not isinstance(value, str) or len(value) > 255 or not LOGO.fullmatch(value):
        return None
    return value


def _finite_number(value: object) -> bool:
    return type(value) is int or (type(value) is float and math.isfinite(value))


def _text(value: object, maximum: int) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= maximum


def _normal_name(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def company_identity(row: dict) -> tuple:
    """Identidad estable usada por el validador y los importadores."""
    return (_normal_name(row["name"]), row["city"], row["lat"], row["lng"])


def _extra_fields(row: dict, allowed: set[str], path: str, errors: list[str]) -> None:
    if any(key not in allowed for key in row):
        errors.append(f"{path}: campos desconocidos")


def _is_google_provider(value: str) -> bool:
    compact = re.sub(r"[^a-z0-9]+", "", value.casefold())
    return compact.startswith("google")


def _safe_public_source_url(value: object) -> bool:
    if not isinstance(value, str) or not value or len(value) > 2048:
        return False
    if any(char.isspace() for char in value) or "\\" in value:
        return False
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.hostname
        and parsed.netloc
        and parsed.username is None
        and parsed.password is None
        and port is None
        and not parsed.query
        and not parsed.fragment
    )


def _timezone_timestamp(value: object) -> bool:
    if not isinstance(value, str) or "T" not in value or len(value) > 80:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def validate_scout_source(source: object, path: str) -> list[str]:
    """Valida una referencia pública de Scout sin consultar red ni modificarla."""
    if not isinstance(source, dict):
        return [f"{path}: debe ser un objeto"]
    errors: list[str] = []
    _extra_fields(source, SCOUT_SOURCE_FIELDS, path, errors)
    provider = source.get("provider")
    if not _text(provider, 200) or _is_google_provider(provider):
        errors.append(f"{path}.provider: proveedor público no permitido")
    if not _safe_public_source_url(source.get("source_url")):
        errors.append(f"{path}.source_url: URL HTTPS pública no permitida")
    if not _timezone_timestamp(source.get("observed_at")):
        errors.append(f"{path}.observed_at: timestamp ISO 8601 con zona requerido")
    if source.get("provenance_class") != "public":
        errors.append(f"{path}.provenance_class: debe ser public")
    if source.get("use_classification") != "redistributable":
        errors.append(f"{path}.use_classification: debe ser redistributable")
    if source.get("export_eligible") is not True:
        errors.append(f"{path}.export_eligible: debe ser true")
    return errors


def validate_companies(data: object) -> list[str]:
    """Devuelve errores con rutas estables; lista vacía significa contrato V1 válido.

    Verifica estructura, no la veracidad ni los derechos de publicación de los hechos.
    Los textos pueden contener HTML literal: el consumidor debe renderizarlos con seguridad.
    """
    if not isinstance(data, list):
        return ["companies: debe ser un array"]
    errors: list[str] = []
    seen: set[tuple] = set()
    seen_site_ids: set[str] = set()
    for index, row in enumerate(data):
        path = f"companies[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{path}: debe ser un objeto")
            continue
        _extra_fields(row, COMPANY_FIELDS, path, errors)
        if not _text(row.get("name"), 200):
            errors.append(f"{path}.name: texto requerido, máximo 200 caracteres")
        city = row.get("city")
        bbox = BBOXES.get(city) if isinstance(city, str) else None
        if bbox is None:
            errors.append(f"{path}.city: ciudad no permitida")
        for field in ("lat", "lng"):
            if not _finite_number(row.get(field)):
                errors.append(f"{path}.{field}: número finito requerido")
        coordinates_ok = all(_finite_number(row.get(field)) for field in ("lat", "lng"))
        if bbox and coordinates_ok:
            if not (bbox[0] <= row["lng"] <= bbox[2] and bbox[1] <= row["lat"] <= bbox[3]):
                errors.append(f"{path}: coordenadas fuera del bbox de la ciudad")
        category = row.get("category")
        if not isinstance(category, str) or category not in CATEGORIES:
            errors.append(f"{path}.category: valor requerido no permitido")
        if "subcategory" in row:
            subcategory = row["subcategory"]
            if (not isinstance(subcategory, str) or subcategory not in STARTUP_SUBCATEGORIES
                    or category != "Startup"):
                errors.append(f"{path}.subcategory: valor permitido solo para Startup")
        # `funding` queda aceptado y requerido durante la fase expand/contract. Los lectores
        # prefieren category/subcategory; retirarlo requiere una migración posterior explícita.
        funding = row.get("funding")
        if not isinstance(funding, dict):
            errors.append(f"{path}.funding: objeto requerido")
        else:
            _extra_fields(funding, {"type", "stage"}, path + ".funding", errors)
            kind = funding.get("type")
            if not isinstance(kind, str) or kind not in FUNDING_TYPES:
                errors.append(f"{path}.funding.type: valor no permitido")
            if "stage" in funding:
                stage = funding["stage"]
                if not isinstance(stage, str) or stage not in STAGES or kind != "Startup":
                    errors.append(f"{path}.funding.stage: etapa permitida solo para Startup")
        for field, limit in (("address", 500), ("tag", 2000), ("tag_es", 2000)):
            if field in row and not _text(row[field], limit):
                errors.append(f"{path}.{field}: texto no vacío, máximo {limit} caracteres")
        for field, validator in (("domain", safe_domain_url), ("logo", safe_logo_path)):
            if field in row and validator(row[field]) is None:
                errors.append(f"{path}.{field}: formato de enlace no permitido")
        if "logoDark" in row and not isinstance(row["logoDark"], bool):
            errors.append(f"{path}.logoDark: booleano requerido")
        if "operating_model" in row:
            model = row["operating_model"]
            if not isinstance(model, str) or model not in OPERATING_MODELS:
                errors.append(f"{path}.operating_model: valor no permitido")
        for field in ("site_id", "organization_id"):
            if field in row and not _text(row[field], 200):
                errors.append(f"{path}.{field}: texto no vacío, máximo 200 caracteres")
        if "workspace_type" in row:
            workspace_type = row["workspace_type"]
            if not isinstance(workspace_type, str) or workspace_type not in SCOUT_WORKSPACE_TYPES:
                errors.append(f"{path}.workspace_type: valor no permitido")
        if "sources" in row:
            sources = row["sources"]
            if not isinstance(sources, list) or not sources:
                errors.append(f"{path}.sources: array no vacío requerido")
            elif len(sources) > 100:
                errors.append(f"{path}.sources: máximo 100 fuentes")
            else:
                for source_index, source in enumerate(sources):
                    errors.extend(validate_scout_source(source, f"{path}.sources[{source_index}]"))
        if _text(row.get("site_id"), 200):
            if row["site_id"] in seen_site_ids:
                errors.append(f"{path}.site_id: identificador duplicado")
            seen_site_ids.add(row["site_id"])
        # Coordenadas compartidas no son duplicados: existen oficinas con varias empresas.
        if bbox and coordinates_ok and _text(row.get("name"), 200):
            identity = company_identity(row)
            if identity in seen:
                errors.append(f"{path}: sede duplicada (nombre, ciudad y coordenadas)")
            seen.add(identity)
    return errors


def validate_ticker(data: object) -> list[str]:
    if not isinstance(data, list):
        return ["ticker: debe ser un array"]
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    for index, row in enumerate(data):
        path = f"ticker[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{path}: debe ser un objeto")
            continue
        _extra_fields(row, {"label", "text"}, path, errors)
        for field, limit in (("label", 80), ("text", 1000)):
            if not _text(row.get(field), limit):
                errors.append(f"{path}.{field}: texto requerido, máximo {limit} caracteres")
        if _text(row.get("label"), 80) and _text(row.get("text"), 1000):
            identity = (_normal_name(row["label"]), _normal_name(row["text"]))
            if identity in seen:
                errors.append(f"{path}: titular duplicado")
            seen.add(identity)
    return errors


def _unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON contiene una clave duplicada")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("JSON contiene un número no finito")


def _parse_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("JSON contiene un número no finito")
    return number


def load_json(path: str | Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object,
                      parse_constant=_reject_constant, parse_float=_parse_float)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--companies", type=Path, default=ROOT / "companies.json")
    parser.add_argument("--ticker", type=Path, default=ROOT / "ticker.json")
    args = parser.parse_args(argv)
    errors: list[str] = []
    counts = []
    for name, path, validate in (("companies", args.companies, validate_companies),
                                  ("ticker", args.ticker, validate_ticker)):
        try:
            data = load_json(path)
            errors.extend(validate(data))
            counts.append(f"{name}={len(data) if isinstance(data, list) else 0}")
        except (OSError, ValueError) as exc:
            # No volcar contenido ni mensajes del parser que puedan reflejar datos externos.
            errors.append(f"{name}: no se pudo leer JSON válido ({type(exc).__name__})")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("OK — " + ", ".join(counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
