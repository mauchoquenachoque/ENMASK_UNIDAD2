import traceback
from datetime import datetime, timezone
from typing import Any, Dict, List

from workers.celery_app import celery_app
from app.core.logging import logger


@celery_app.task(bind=True, name="workers.tasks.masking_tasks.execute_masking_job", max_retries=3)
def execute_masking_job(self, job_id: str, connection_id: str, rule_ids: List[str], owner_id: str) -> Dict[str, Any]:
    import asyncio

    async def _run() -> Dict[str, Any]:
        from app.api.deps import (
            get_connection_repository,
            get_rule_repository,
            get_job_repository,
            get_audit_repository,
            get_user_repository,
            get_vault_repository,
        )
        from app.application.services.job_orchestrator import JobOrchestrator

        connection_repo = await get_connection_repository()
        rule_repo = await get_rule_repository()
        job_repo = await get_job_repository()
        audit_repo = await get_audit_repository()
        user_repo = await get_user_repository()
        vault_repo = await get_vault_repository()

        orchestrator = JobOrchestrator(
            connection_repository=connection_repo,
            rule_repository=rule_repo,
            job_repository=job_repo,
            audit_repository=audit_repo,
            user_repository=user_repo,
            vault_repository=vault_repo,
        )

        await orchestrator.run_job(job_id, owner_id)
        return {"job_id": job_id, "status": "completed"}

    try:
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(_run())
            return result
        finally:
            loop.close()
    except Exception as exc:
        logger.error("Masking job %s failed: %s", job_id, str(exc))
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, name="workers.tasks.masking_tasks.execute_unmasking_job", max_retries=3)
def execute_unmasking_job(self, job_id: str, owner_id: str) -> Dict[str, Any]:
    import asyncio

    async def _run() -> Dict[str, Any]:
        from app.api.deps import (
            get_connection_repository,
            get_rule_repository,
            get_job_repository,
            get_audit_repository,
            get_user_repository,
            get_vault_repository,
        )
        from app.application.services.job_orchestrator import JobOrchestrator

        connection_repo = await get_connection_repository()
        rule_repo = await get_rule_repository()
        job_repo = await get_job_repository()
        audit_repo = await get_audit_repository()
        user_repo = await get_user_repository()
        vault_repo = await get_vault_repository()

        orchestrator = JobOrchestrator(
            connection_repository=connection_repo,
            rule_repository=rule_repo,
            job_repository=job_repo,
            audit_repository=audit_repo,
            user_repository=user_repo,
            vault_repository=vault_repo,
        )

        await orchestrator.unmask_job(job_id, owner_id)
        return {"job_id": job_id, "status": "unmasked"}

    try:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_run())
        finally:
            loop.close()
    except Exception as exc:
        logger.error("Unmasking job %s failed: %s", job_id, str(exc))
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, name="workers.tasks.masking_tasks.run_discovery_scan", max_retries=2)
def run_discovery_scan(self, connection_id: str, owner_id: str) -> Dict[str, Any]:
    import asyncio

    async def _run() -> Dict[str, Any]:
        from app.api.deps import get_connection_repository
        from app.application.services.connection_service import ConnectionService

        repo = await get_connection_repository()
        service = ConnectionService(repo)
        suggestions = await service.discover_pii(connection_id, owner_id)

        return {
            "connection_id": connection_id,
            "pii_columns_found": len(suggestions),
            "suggestions": [
                {
                    "table": s.target_table,
                    "column": s.target_column,
                    "strategy": s.strategy.value if hasattr(s.strategy, "value") else str(s.strategy),
                }
                for s in suggestions
            ],
        }

    try:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_run())
        finally:
            loop.close()
    except Exception as exc:
        logger.error("Discovery scan for connection %s failed: %s", connection_id, str(exc))
        self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
