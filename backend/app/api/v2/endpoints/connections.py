from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional

from pydantic import BaseModel

from app.api.deps import get_connection_service, get_connection_repository, require_permission
from app.application.schemas import ConnectionCreate, ConnectionResponse
from app.application.services.connection_service import ConnectionService
from app.core.exceptions import ResourceNotFoundError
from app.core.rbac import Permission
from app.domain.entities.user import User
from app.domain.entities.connection import ConnectionStatus
from app.domain.value_objects.database_type import DatabaseType
from app.domain.interfaces.repository import ConnectionRepository

router = APIRouter()


class PaginatedResponse(BaseModel):
    items: List[ConnectionResponse]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class BulkDeleteRequest(BaseModel):
    connection_ids: List[str]


class BulkDeleteResponse(BaseModel):
    deleted: int
    failed: List[str]


@router.get("/", response_model=PaginatedResponse)
async def list_connections(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    conn_type: Optional[DatabaseType] = None,
    status_filter: Optional[ConnectionStatus] = Query(None, alias="status"),
    sort_by: Optional[str] = Query("created_at", regex="^(name|type|status|created_at)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.CONNECTION_READ)),
    repository: ConnectionRepository = Depends(get_connection_repository),
):
    all_connections = await repository.get_all()
    filtered = [c for c in all_connections if getattr(c, "owner_id", None) == user.id]

    if conn_type:
        filtered = [c for c in filtered if c.type == conn_type]
    if status_filter:
        filtered = [c for c in filtered if c.status == status_filter]

    reverse = sort_order == "desc"
    filtered.sort(key=lambda c: getattr(c, sort_by, "") or "", reverse=reverse)

    total = len(filtered)
    page = filtered[skip : skip + limit]
    items = [ConnectionResponse.model_validate(c.model_dump()) for c in page]

    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    data: ConnectionCreate,
    user: User = Depends(require_permission(Permission.CONNECTION_CREATE)),
    service: ConnectionService = Depends(get_connection_service),
):
    return await service.create_connection(data, user.id)


@router.get("/{conn_id}", response_model=ConnectionResponse)
async def get_connection(
    conn_id: str,
    user: User = Depends(require_permission(Permission.CONNECTION_READ)),
    service: ConnectionService = Depends(get_connection_service),
):
    try:
        return await service.get_connection(conn_id, user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{conn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    conn_id: str,
    user: User = Depends(require_permission(Permission.CONNECTION_DELETE)),
    service: ConnectionService = Depends(get_connection_service),
):
    try:
        await service.delete_connection(conn_id, user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{conn_id}/test")
async def test_connection(
    conn_id: str,
    user: User = Depends(require_permission(Permission.CONNECTION_TEST)),
    service: ConnectionService = Depends(get_connection_service),
):
    try:
        conn = await service.get_connection(conn_id, user.id)
        return {"status": "ok", "connection_id": conn_id}
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_connections(
    body: BulkDeleteRequest,
    user: User = Depends(require_permission(Permission.CONNECTION_DELETE)),
    service: ConnectionService = Depends(get_connection_service),
):
    deleted = 0
    failed: List[str] = []
    for conn_id in body.connection_ids:
        try:
            await service.delete_connection(conn_id, user.id)
            deleted += 1
        except Exception:
            failed.append(conn_id)
    return BulkDeleteResponse(deleted=deleted, failed=failed)
