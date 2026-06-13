from fastapi import APIRouter

from app.api.v2.endpoints import connections, rules, jobs, reports, discovery, schedules, plugins

router = APIRouter()

router.include_router(connections.router, prefix="/connections", tags=["v2 Connections"])
router.include_router(rules.router, prefix="/rules", tags=["v2 Rules"])
router.include_router(jobs.router, prefix="/jobs", tags=["v2 Jobs"])
router.include_router(reports.router, prefix="/reports", tags=["v2 Reports"])
router.include_router(discovery.router, prefix="/discover", tags=["v2 Discovery"])
router.include_router(schedules.router, prefix="/schedules", tags=["v2 Schedules"])
router.include_router(plugins.router, prefix="/plugins", tags=["v2 Plugins"])
