import csv
import io
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from app.api.deps import (
    get_connection_repository,
    get_rule_repository,
    get_audit_repository,
    require_permission,
)
from app.core.rbac import Permission
from app.domain.entities.user import User
from app.domain.interfaces.repository import (
    ConnectionRepository,
    JobRepository,
    RuleRepository,
    AuditLogRepository,
)
from app.domain.value_objects.compliance_framework import ComplianceFramework

router = APIRouter()


class ComplianceReport(BaseModel):
    framework: str
    generated_at: str
    total_rules: int
    compliant_rules: int
    non_compliant_rules: int
    coverage_percentage: float
    details: List[Dict]


class RiskAssessment(BaseModel):
    risk_level: str
    total_sensitive_columns: int
    masked_columns: int
    unmasked_columns: int
    risk_score: float
    recommendations: List[str]


class CoverageMetrics(BaseModel):
    total_tables: int
    tables_with_masking: int
    total_columns: int
    masked_columns: int
    coverage_percentage: float
    by_framework: Dict[str, float]


@router.get("/compliance/{framework}", response_model=ComplianceReport)
async def compliance_report(
    framework: ComplianceFramework,
    user: User = Depends(require_permission(Permission.COMPLIANCE_VIEW)),
    rule_repository: RuleRepository = Depends(get_rule_repository),
):
    all_rules = await rule_repository.get_all()
    user_rules = [r for r in all_rules if getattr(r, "owner_id", None) == user.id]

    relevant = [
        r for r in user_rules
        if r.compliance_frameworks and framework in r.compliance_frameworks
    ]

    total = len(relevant)
    compliant = sum(1 for r in relevant if r.is_active)

    details = []
    for r in relevant:
        details.append({
            "rule_id": r.id,
            "table": r.target_table,
            "column": r.target_column,
            "strategy": r.strategy.value if r.strategy else None,
            "is_active": r.is_active,
        })

    coverage = (compliant / total * 100) if total > 0 else 0.0

    return ComplianceReport(
        framework=framework.value,
        generated_at=datetime.utcnow().isoformat(),
        total_rules=total,
        compliant_rules=compliant,
        non_compliant_rules=total - compliant,
        coverage_percentage=round(coverage, 2),
        details=details,
    )


@router.get("/risk-assessment", response_model=RiskAssessment)
async def risk_assessment(
    user: User = Depends(require_permission(Permission.COMPLIANCE_VIEW)),
    rule_repository: RuleRepository = Depends(get_rule_repository),
):
    all_rules = await rule_repository.get_all()
    user_rules = [r for r in all_rules if getattr(r, "owner_id", None) == user.id]

    tables = set(r.target_table for r in user_rules)
    total_sensitive = len(user_rules)
    masked = sum(1 for r in user_rules if r.is_active)
    unmasked = total_sensitive - masked

    risk_score = (unmasked / total_sensitive * 100) if total_sensitive > 0 else 0.0

    if risk_score >= 50:
        risk_level = "critical"
    elif risk_score >= 25:
        risk_level = "high"
    elif risk_score >= 10:
        risk_level = "medium"
    else:
        risk_level = "low"

    recommendations = []
    if unmasked > 0:
        recommendations.append(f"Activate {unmasked} inactive masking rules")
    if len(tables) > 0 and masked < total_sensitive:
        recommendations.append("Review and apply masking to all sensitive columns")

    return RiskAssessment(
        risk_level=risk_level,
        total_sensitive_columns=total_sensitive,
        masked_columns=masked,
        unmasked_columns=unmasked,
        risk_score=round(risk_score, 2),
        recommendations=recommendations,
    )


@router.get("/coverage", response_model=CoverageMetrics)
async def coverage_metrics(
    user: User = Depends(require_permission(Permission.COMPLIANCE_VIEW)),
    rule_repository: RuleRepository = Depends(get_rule_repository),
    connection_repository: ConnectionRepository = Depends(get_connection_repository),
):
    all_rules = await rule_repository.get_all()
    user_rules = [r for r in all_rules if getattr(r, "owner_id", None) == user.id]

    all_connections = await connection_repository.get_all()
    user_connections = [c for c in all_connections if getattr(c, "owner_id", None) == user.id]

    tables = set(r.target_table for r in user_rules)
    masked_rules = [r for r in user_rules if r.is_active]

    by_framework: Dict[str, float] = {}
    for fw in ComplianceFramework:
        fw_rules = [r for r in user_rules if r.compliance_frameworks and fw in r.compliance_frameworks]
        fw_active = [r for r in fw_rules if r.is_active]
        if fw_rules:
            by_framework[fw.value] = round(len(fw_active) / len(fw_rules) * 100, 2)
        else:
            by_framework[fw.value] = 0.0

    total_cols = len(user_rules)
    masked_cols = len(masked_rules)

    return CoverageMetrics(
        total_tables=len(tables),
        tables_with_masking=len(set(r.target_table for r in masked_rules)),
        total_columns=total_cols,
        masked_columns=masked_cols,
        coverage_percentage=round((masked_cols / total_cols * 100) if total_cols > 0 else 0.0, 2),
        by_framework=by_framework,
    )


@router.get("/export")
async def export_report(
    report_type: str = Query("compliance", regex="^(compliance|risk|coverage)$"),
    format: str = Query("json", regex="^(json|csv|excel|pdf)$"),
    framework: Optional[ComplianceFramework] = None,
    user: User = Depends(require_permission(Permission.COMPLIANCE_VIEW)),
    rule_repository: RuleRepository = Depends(get_rule_repository),
):
    all_rules = await rule_repository.get_all()
    user_rules = [r for r in all_rules if getattr(r, "owner_id", None) == user.id]

    if framework:
        user_rules = [
            r for r in user_rules
            if r.compliance_frameworks and framework in r.compliance_frameworks
        ]

    report_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "report_type": report_type,
        "framework": framework.value if framework else "all",
        "rules": [
            {
                "id": r.id,
                "table": r.target_table,
                "column": r.target_column,
                "strategy": r.strategy.value if r.strategy else None,
                "data_type": r.data_type.value if r.data_type else None,
                "is_active": r.is_active,
                "compliance": [f.value for f in r.compliance_frameworks] if r.compliance_frameworks else [],
            }
            for r in user_rules
        ],
    }

    if format == "csv":
        output = io.StringIO()
        if report_data["rules"]:
            writer = csv.DictWriter(output, fieldnames=report_data["rules"][0].keys())
            writer.writeheader()
            writer.writerows(report_data["rules"])
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=report_{report_type}.csv"},
        )

    if format == "excel":
        output = io.StringIO()
        if report_data["rules"]:
            writer = csv.DictWriter(output, fieldnames=report_data["rules"][0].keys())
            writer.writeheader()
            writer.writerows(report_data["rules"])
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.ms-excel",
            headers={"Content-Disposition": f"attachment; filename=report_{report_type}.xls"},
        )

    return report_data
