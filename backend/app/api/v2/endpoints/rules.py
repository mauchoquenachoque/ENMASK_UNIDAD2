from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional

from pydantic import BaseModel

from app.api.deps import get_masking_service, get_rule_repository, require_permission
from app.application.schemas import RuleCreate, RuleResponse
from app.application.services.masking_service import MaskingService
from app.core.exceptions import ResourceNotFoundError
from app.core.rbac import Permission
from app.domain.entities.user import User
from app.domain.interfaces.repository import RuleRepository
from app.domain.value_objects.masking_algorithm import MaskingAlgorithm
from app.domain.value_objects.compliance_framework import ComplianceFramework

router = APIRouter()


class PaginatedRuleResponse(BaseModel):
    items: List[RuleResponse]
    total: int
    skip: int
    limit: int


class BulkCreateRequest(BaseModel):
    rules: List[RuleCreate]


class BulkCreateResponse(BaseModel):
    created: int
    failed: int
    errors: List[str]


@router.get("/", response_model=PaginatedRuleResponse)
async def list_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    strategy: Optional[MaskingAlgorithm] = None,
    data_type: Optional[str] = None,
    compliance_framework: Optional[ComplianceFramework] = None,
    user: User = Depends(require_permission(Permission.RULE_READ)),
    repository: RuleRepository = Depends(get_rule_repository),
):
    all_rules = await repository.get_all()
    filtered = [r for r in all_rules if getattr(r, "owner_id", None) == user.id]

    if strategy:
        filtered = [r for r in filtered if r.strategy == strategy]
    if data_type:
        filtered = [r for r in filtered if r.data_type and r.data_type.value == data_type]
    if compliance_framework:
        filtered = [
            r for r in filtered
            if r.compliance_frameworks and compliance_framework in r.compliance_frameworks
        ]

    total = len(filtered)
    page = filtered[skip : skip + limit]
    items = [RuleResponse.model_validate(r.model_dump()) for r in page]

    return PaginatedRuleResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    data: RuleCreate,
    user: User = Depends(require_permission(Permission.RULE_CREATE)),
    service: MaskingService = Depends(get_masking_service),
):
    return await service.create_rule(data, user.id)


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: str,
    user: User = Depends(require_permission(Permission.RULE_READ)),
    service: MaskingService = Depends(get_masking_service),
):
    try:
        return await service.get_rule(rule_id, user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: str,
    data: RuleCreate,
    user: User = Depends(require_permission(Permission.RULE_UPDATE)),
    service: MaskingService = Depends(get_masking_service),
):
    try:
        return await service.update_rule(rule_id, data, user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: str,
    user: User = Depends(require_permission(Permission.RULE_DELETE)),
    service: MaskingService = Depends(get_masking_service),
):
    try:
        await service.delete_rule(rule_id, user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/bulk-create", response_model=BulkCreateResponse)
async def bulk_create_rules(
    body: BulkCreateRequest,
    user: User = Depends(require_permission(Permission.RULE_CREATE)),
    service: MaskingService = Depends(get_masking_service),
):
    created = 0
    errors: List[str] = []
    for rule_data in body.rules:
        try:
            await service.create_rule(rule_data, user.id)
            created += 1
        except Exception as e:
            errors.append(str(e))
    return BulkCreateResponse(created=created, failed=len(errors), errors=errors)
