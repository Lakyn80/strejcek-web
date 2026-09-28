"""Real ARES REST client for production company lookups."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from accounting_api.integrations.ares.provider import (
    AresCompanyNotFoundError,
    AresUnavailableError,
    InvalidCompanyNameError,
    normalize_company_name,
    normalize_ico,
)
from accounting_api.schemas import AresCompanyLookupResponse


class RealAresProvider:
    """Lookup against the public ARES ekonomicke-subjekty REST API."""

    def __init__(
        self,
        *,
        base_url: str = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty",
        search_url: str = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/vyhledat",
        timeout_seconds: float = 10.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._search_url = search_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def lookup_company(self, ico: str) -> AresCompanyLookupResponse:
        normalized = normalize_ico(ico)
        payload = self._get_json(f"{self._base_url}/{normalized}")
        return self._map_company(payload, source="ares")

    def search_companies(self, company_name: str) -> list[AresCompanyLookupResponse]:
        query = normalize_company_name(company_name)
        if len(query) < 2:
            raise InvalidCompanyNameError("Company name query is too short.")
        body = json.dumps({"obchodniJmeno": company_name.strip(), "pocet": 20}).encode("utf-8")
        payload = self._post_json(self._search_url, body)
        items = payload.get("ekonomickeSubjekty") or payload.get("ekonomicke_subjekty") or []
        if not isinstance(items, list):
            return []
        results: list[AresCompanyLookupResponse] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                results.append(self._map_company(item, source="ares"))
            except Exception:
                continue
        return results

    def _map_company(self, payload: dict[str, Any], *, source: str) -> AresCompanyLookupResponse:
        ico = str(payload.get("ico") or payload.get("icoId") or "").strip()
        if not ico:
            raise AresCompanyNotFoundError("ARES response did not contain IČO.")
        name = str(payload.get("obchodniJmeno") or "").strip()
        sidlo = payload.get("sidlo") if isinstance(payload.get("sidlo"), dict) else {}
        city = str(sidlo.get("nazevObce") or "").strip()
        zip_code = str(sidlo.get("psc") or "").strip()
        address_line = str(sidlo.get("textovaAdresa") or "").strip()
        if not address_line:
            house = sidlo.get("cisloDomovni")
            street_parts = [str(part) for part in (sidlo.get("nazevUlice"), house) if part]
            address_line = ", ".join(street_parts) if street_parts else ""
        country = str(sidlo.get("nazevStatu") or "Česká republika").strip()
        dic = payload.get("dic")
        if dic is not None:
            dic = str(dic).strip() or None
        return AresCompanyLookupResponse(
            ico=normalize_ico(ico),
            dic=dic,
            company_name=name or f"IČO {ico}",
            address_line=address_line or city or f"IČO {ico}",
            city=city,
            zip=zip_code,
            country=country or "Česká republika",
            data_box=None,
            source="ares",
        )

    def _get_json(self, url: str) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "pvm-deal-accounting/1.0"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise AresCompanyNotFoundError(f"Company was not found in ARES ({url}).") from exc
            raise AresUnavailableError(f"ARES lookup failed with HTTP {exc.code}.") from exc
        except Exception as exc:  # noqa: BLE001 - map transport failures
            raise AresUnavailableError(f"ARES lookup unavailable: {exc}") from exc

    def _post_json(self, url: str, body: bytes) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "pvm-deal-accounting/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise AresUnavailableError(f"ARES search unavailable: {exc}") from exc
