from typing import Any, Dict, List, Optional

import httpx

from enmask.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConnectionError,
    EnmaskError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from enmask.models import (
    AuthResponse,
    ComplianceReport,
    Connection,
    MaskingJob,
    MaskingRule,
    ScanResult,
    SummaryReport,
)


class EnmaskClient:
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.token = token
        self._client = httpx.Client(timeout=timeout)
        self._headers: Dict[str, str] = {"Content-Type": "application/json"}
        if api_key:
            self._headers["X-API-Key"] = api_key
        if token:
            self._headers["Authorization"] = f"Bearer {token}"

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        try:
            response = self._client.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=self._headers,
            )
            self._handle_errors(response)
            return response.json() if response.content else None
        except httpx.RequestError as e:
            raise ConnectionError(f"Request failed: {e}")

    def _handle_errors(self, response: httpx.Response) -> None:
        if response.is_success:
            return
        status = response.status_code
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        if status == 401:
            raise AuthenticationError(detail)
        if status == 403:
            raise AuthorizationError(detail)
        if status == 404:
            raise NotFoundError(detail)
        if status == 422:
            raise ValidationError(detail)
        if status == 429:
            raise RateLimitError(detail)
        if status >= 500:
            raise ServerError(detail)
        raise EnmaskError(detail, status_code=status)

    def _set_token(self, token: str) -> None:
        self.token = token
        self._headers["Authorization"] = f"Bearer {token}"

    def login(self, email: str, password: str) -> AuthResponse:
        data = self._request("POST", "/api/v2/auth/login", json={"email": email, "password": password})
        self._set_token(data["access_token"])
        return AuthResponse(**data)

    def login_google(self, id_token: str) -> AuthResponse:
        data = self._request("POST", "/api/v2/auth/google", json={"id_token": id_token})
        self._set_token(data["access_token"])
        return AuthResponse(**data)

    def list_connections(self) -> List[Connection]:
        data = self._request("GET", "/api/v2/connections")
        return [Connection(**c) for c in data]

    def create_connection(self, data: Dict[str, Any]) -> Connection:
        result = self._request("POST", "/api/v2/connections", json=data)
        return Connection(**result)

    def delete_connection(self, id: str) -> None:
        self._request("DELETE", f"/api/v2/connections/{id}")

    def test_connection(self, id: str) -> bool:
        result = self._request("POST", f"/api/v2/connections/{id}/test")
        return result.get("success", False)

    def discover_pii(self, id: str) -> List[Dict[str, Any]]:
        return self._request("POST", f"/api/v2/connections/{id}/discover")

    def list_rules(self) -> List[MaskingRule]:
        data = self._request("GET", "/api/v2/rules")
        return [MaskingRule(**r) for r in data]

    def create_rule(self, data: Dict[str, Any]) -> MaskingRule:
        result = self._request("POST", "/api/v2/rules", json=data)
        return MaskingRule(**result)

    def update_rule(self, id: str, data: Dict[str, Any]) -> MaskingRule:
        result = self._request("PUT", f"/api/v2/rules/{id}", json=data)
        return MaskingRule(**result)

    def delete_rule(self, id: str) -> None:
        self._request("DELETE", f"/api/v2/rules/{id}")

    def list_jobs(self) -> List[MaskingJob]:
        data = self._request("GET", "/api/v2/jobs")
        return [MaskingJob(**j) for j in data]

    def create_job(self, data: Dict[str, Any]) -> MaskingJob:
        result = self._request("POST", "/api/v2/jobs", json=data)
        return MaskingJob(**result)

    def run_job(self, id: str) -> None:
        self._request("POST", f"/api/v2/jobs/{id}/run")

    def unmask_job(self, id: str) -> None:
        self._request("POST", f"/api/v2/jobs/{id}/unmask")

    def get_job_status(self, id: str) -> MaskingJob:
        result = self._request("GET", f"/api/v2/jobs/{id}")
        return MaskingJob(**result)

    def share_job(self, id: str, email: str) -> None:
        self._request("POST", f"/api/v2/jobs/{id}/share", json={"email": email})

    def get_summary(self) -> SummaryReport:
        data = self._request("GET", "/api/v2/reports/summary")
        return SummaryReport(**data)

    def get_compliance_report(self, framework: str) -> ComplianceReport:
        data = self._request("GET", f"/api/v2/reports/compliance/{framework}")
        return ComplianceReport(**data)

    def scan_database(self, connection_id: str) -> ScanResult:
        data = self._request("POST", f"/api/v2/discovery/scan", json={"connection_id": connection_id})
        return ScanResult(**data)

    def get_scan_results(self, scan_id: str) -> ScanResult:
        data = self._request("GET", f"/api/v2/discovery/scans/{scan_id}")
        return ScanResult(**data)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "EnmaskClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
