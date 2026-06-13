from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from pydantic import BaseModel

from app.api.deps import require_permission
from app.core.config import settings
from app.core.rbac import Permission
from app.domain.entities.user import User
from app.core.exceptions import PluginError

router = APIRouter()


class PluginInfo(BaseModel):
    name: str
    version: str
    description: str
    enabled: bool
    connectors: List[str]
    strategies: List[str]


class PluginInstallRequest(BaseModel):
    plugin_name: str


class PluginConfigRequest(BaseModel):
    config: Dict[str, Any]


@router.get("/", response_model=List[PluginInfo])
async def list_plugins(
    user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
):
    from app.infrastructure.plugins.loader import plugin_loader

    plugins = plugin_loader.list_plugins()
    return [
        PluginInfo(
            name=p["name"],
            version=p["version"],
            description=p["description"],
            enabled=p["enabled"],
            connectors=p.get("connectors", []),
            strategies=p.get("strategies", []),
        )
        for p in plugins
    ]


@router.get("/{plugin_name}", response_model=PluginInfo)
async def get_plugin(
    plugin_name: str,
    user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
):
    from app.infrastructure.plugins.loader import plugin_loader

    info = plugin_loader.get_plugin_info(plugin_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' not found")
    return PluginInfo(
        name=info["name"],
        version=info["version"],
        description=info["description"],
        enabled=info["enabled"],
        connectors=info.get("connectors", []),
        strategies=info.get("strategies", []),
    )


@router.post("/install", response_model=PluginInfo, status_code=status.HTTP_201_CREATED)
async def install_plugin(
    body: PluginInstallRequest,
    user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
):
    from app.infrastructure.plugins.loader import plugin_loader

    try:
        plugin = plugin_loader.load_plugin(body.plugin_name)
        info = plugin_loader.get_plugin_info(body.plugin_name)
        return PluginInfo(
            name=info["name"],
            version=info["version"],
            description=info["description"],
            enabled=info["enabled"],
            connectors=info.get("connectors", []),
            strategies=info.get("strategies", []),
        )
    except PluginError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{plugin_name}", status_code=status.HTTP_204_NO_CONTENT)
async def uninstall_plugin(
    plugin_name: str,
    user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
):
    from app.infrastructure.plugins.loader import plugin_loader

    try:
        plugin_loader.unload_plugin(plugin_name)
    except PluginError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{plugin_name}/configure")
async def configure_plugin(
    plugin_name: str,
    body: PluginConfigRequest,
    user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
):
    from app.infrastructure.plugins.loader import plugin_loader

    try:
        plugin_loader.configure_plugin(plugin_name, body.config)
        return {"status": "ok", "plugin": plugin_name, "message": "Configuration updated"}
    except PluginError as e:
        raise HTTPException(status_code=400, detail=str(e))
