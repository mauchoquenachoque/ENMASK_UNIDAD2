import pytest
from app.core.rbac import Permission, check_permission, get_user_permissions, ROLE_PERMISSIONS


class TestAdminPermissions:
    def test_admin_has_all_permissions(self):
        for perm in Permission:
            assert check_permission("admin", perm) is True

    def test_admin_permissions_count(self):
        perms = get_user_permissions("admin")
        assert len(perms) == len(Permission)


class TestSecurityOfficerPermissions:
    def test_has_security_permissions(self):
        assert check_permission("security_officer", Permission.RULE_CREATE) is True
        assert check_permission("security_officer", Permission.RULE_UPDATE) is True
        assert check_permission("security_officer", Permission.RULE_DELETE) is True
        assert check_permission("security_officer", Permission.AUDIT_READ) is True
        assert check_permission("security_officer", Permission.COMPLIANCE_VIEW) is True
        assert check_permission("security_officer", Permission.USER_MANAGE) is True
        assert check_permission("security_officer", Permission.SYSTEM_CONFIG) is True

    def test_lacks_job_run(self):
        assert check_permission("security_officer", Permission.JOB_RUN) is False

    def test_lacks_connection_create(self):
        assert check_permission("security_officer", Permission.CONNECTION_CREATE) is False


class TestAuditorPermissions:
    def test_has_read_only(self):
        assert check_permission("auditor", Permission.CONNECTION_READ) is True
        assert check_permission("auditor", Permission.RULE_READ) is True
        assert check_permission("auditor", Permission.JOB_READ) is True
        assert check_permission("auditor", Permission.AUDIT_READ) is True
        assert check_permission("auditor", Permission.COMPLIANCE_VIEW) is True

    def test_no_write_permissions(self):
        assert check_permission("auditor", Permission.CONNECTION_CREATE) is False
        assert check_permission("auditor", Permission.RULE_CREATE) is False
        assert check_permission("auditor", Permission.JOB_RUN) is False
        assert check_permission("auditor", Permission.USER_MANAGE) is False


class TestOperatorPermissions:
    def test_has_connection_rule_job_permissions(self):
        assert check_permission("operator", Permission.CONNECTION_CREATE) is True
        assert check_permission("operator", Permission.CONNECTION_READ) is True
        assert check_permission("operator", Permission.CONNECTION_DELETE) is True
        assert check_permission("operator", Permission.RULE_CREATE) is True
        assert check_permission("operator", Permission.RULE_READ) is True
        assert check_permission("operator", Permission.RULE_UPDATE) is True
        assert check_permission("operator", Permission.RULE_DELETE) is True
        assert check_permission("operator", Permission.JOB_CREATE) is True
        assert check_permission("operator", Permission.JOB_READ) is True
        assert check_permission("operator", Permission.JOB_RUN) is True
        assert check_permission("operator", Permission.JOB_SHARE) is True

    def test_lacks_admin_permissions(self):
        assert check_permission("operator", Permission.USER_MANAGE) is False
        assert check_permission("operator", Permission.SYSTEM_CONFIG) is False
        assert check_permission("operator", Permission.AUDIT_READ) is False


class TestViewerPermissions:
    def test_read_only(self):
        assert check_permission("viewer", Permission.CONNECTION_READ) is True
        assert check_permission("viewer", Permission.RULE_READ) is True
        assert check_permission("viewer", Permission.JOB_READ) is True

    def test_no_write(self):
        assert check_permission("viewer", Permission.CONNECTION_CREATE) is False
        assert check_permission("viewer", Permission.CONNECTION_DELETE) is False
        assert check_permission("viewer", Permission.RULE_CREATE) is False
        assert check_permission("viewer", Permission.JOB_RUN) is False
        assert check_permission("viewer", Permission.AUDIT_READ) is False


class TestInvalidRole:
    def test_unknown_role_returns_empty(self):
        perms = get_user_permissions("nonexistent_role")
        assert len(perms) == 0

    def test_unknown_role_check_returns_false(self):
        assert check_permission("nonexistent_role", Permission.CONNECTION_READ) is False
