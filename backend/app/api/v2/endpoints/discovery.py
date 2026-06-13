import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from pydantic import BaseModel

from app.api.deps import get_connection_repository, get_connection_service, require_permission
from app.application.services.connection_service import ConnectionService
from app.core.exceptions import ResourceNotFoundError
from app.core.rbac import Permission
from app.domain.entities.user import User
from app.domain.interfaces.repository import ConnectionRepository
from app.domain.services.pii_detector import pii_detector
from app.domain.value_objects.compliance_framework import ComplianceFramework

router = APIRouter()

_scan_results: Dict[str, Dict[str, Any]] = {}


class ScanRequest(BaseModel):
    connection_id: str
    tables: Optional[List[str]] = None


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str


class ScanResultResponse(BaseModel):
    scan_id: str
    connection_id: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_tables: int
    total_columns_scanned: int
    pii_columns_found: int
    suggestions: List[Dict[str, Any]]


class ClassifyRequest(BaseModel):
    connection_id: str
    framework: ComplianceFramework


class ClassifyResponse(BaseModel):
    connection_id: str
    framework: str
    classifications: List[Dict[str, Any]]


@router.post("/scan", response_model=ScanResponse)
async def scan_database(
    body: ScanRequest,
    user: User = Depends(require_permission(Permission.CONNECTION_READ)),
    service: ConnectionService = Depends(get_connection_service),
):
    try:
        conn = await service.get_connection(body.connection_id, user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    scan_id = uuid.uuid4().hex
    _scan_results[scan_id] = {
        "scan_id": scan_id,
        "connection_id": body.connection_id,
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "owner_id": user.id,
        "total_tables": 0,
        "total_columns_scanned": 0,
        "pii_columns_found": 0,
        "suggestions": [],
    }

    try:
        discovery_rules = await service.discover_pii(body.connection_id, user.id)

        suggestions = []
        for rule in discovery_rules:
            suggestions.append({
                "table": rule.target_table,
                "column": rule.target_column,
                "strategy": rule.strategy.value if hasattr(rule.strategy, "value") else str(rule.strategy),
                "options": rule.strategy_options,
            })

        _scan_results[scan_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "total_tables": len(set(r.target_table for r in discovery_rules)),
            "total_columns_scanned": len(discovery_rules),
            "pii_columns_found": len(discovery_rules),
            "suggestions": suggestions,
        })
    except Exception as e:
        _scan_results[scan_id]["status"] = "failed"
        _scan_results[scan_id]["error"] = str(e)

    return ScanResponse(scan_id=scan_id, status="started", message="Scan initiated")


@router.get("/results/{scan_id}", response_model=ScanResultResponse)
async def get_scan_results(
    scan_id: str,
    user: User = Depends(require_permission(Permission.CONNECTION_READ)),
):
    result = _scan_results.get(scan_id)
    if not result or result.get("owner_id") != user.id:
        raise HTTPException(status_code=404, detail="Scan not found")

    return ScanResultResponse(
        scan_id=result["scan_id"],
        connection_id=result["connection_id"],
        status=result["status"],
        started_at=result.get("started_at"),
        completed_at=result.get("completed_at"),
        total_tables=result.get("total_tables", 0),
        total_columns_scanned=result.get("total_columns_scanned", 0),
        pii_columns_found=result.get("pii_columns_found", 0),
        suggestions=result.get("suggestions", []),
    )


@router.post("/classify", response_model=ClassifyResponse)
async def classify_columns(
    body: ClassifyRequest,
    user: User = Depends(require_permission(Permission.COMPLIANCE_VIEW)),
    repository: ConnectionRepository = Depends(get_connection_repository),
):
    connection = await repository.get_by_id(body.connection_id)
    if not connection or getattr(connection, "owner_id", None) != user.id:
        raise HTTPException(status_code=404, detail="Connection not found")

    from app.application.schemas import RuleCreate
    from app.domain.value_objects.compliance_framework import _COMPLIANCE_MAP

    try:
        from app.api.deps import get_connection_service as _gcs
        service = await _gcs.__wrapped__(repository=repository) if hasattr(_gcs, "__wrapped__") else ConnectionService(repository)
    except Exception:
        service = ConnectionService(repository)

    try:
        raw_rules = await service.discover_pii(body.connection_id, user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Discovery failed: {str(e)}")

    classifications = []
    from app.domain.value_objects.data_type import DataType
    from app.domain.services.pii_detector import _COMPLIANCE_MAP as CM

    for rule in raw_rules:
        dt = None
        for pattern, data_type, *_ in pii_detector._COLUMN_PATTERNS if hasattr(pii_detector, "_COLUMN_PATTERNS") else []:
            if pattern.search(rule.target_column):
                dt = data_type
                break

        frameworks = CM.get(dt, []) if dt else []
        relevant = body.framework in frameworks

        classifications.append({
            "table": rule.target_table,
            "column": rule.target_column,
            "data_type": dt.value if dt else "unknown",
            "is_pii": True,
            "relevant_to_framework": relevant,
            "compliance_frameworks": [f.value for f in frameworks],
        })

    return ClassifyResponse(
        connection_id=body.connection_id,
        framework=body.framework.value,
        classifications=classifications,
    )
