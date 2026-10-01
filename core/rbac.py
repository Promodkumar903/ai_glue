# ============================================================
# AI GLUE v8.0 — RBAC/ABAC ENGINE
# ============================================================
# Engine: E-05
# Purpose: Permission enforcement with Scope Hierarchy
# ============================================================

import os
import yaml
from typing import List, Dict, Optional

class RBACEngine:
    _permissions = None

    # Scope Hierarchy — Higher Scope covers Lower Scope
    SCOPE_HIERARCHY = {
        "SELF": 1,
        "CASE": 2,
        "TEAM": 3,
        "ORGANIZATION": 4,
        "TENANT": 5,
        "SYSTEM": 6,
    }

    @classmethod
    def load_permissions(cls) -> List[Dict]:
        if cls._permissions is not None:
            return cls._permissions

        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'permissions.yaml')
        if not os.path.exists(config_path):
            print(f"⚠️ Permissions file not found: {config_path}")
            return []  # Fallback to strict deny

        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            cls._permissions = data.get('permissions', [])
        return cls._permissions

    @classmethod
    def has_permission(cls, roles: List[str], resource: str, action: str, scope: str) -> bool:
        """
        Check if any of the given roles has permission.
        
        Args:
            roles: List of role codes (e.g., ['BROKER', 'AGENT'])
            resource: Resource name (e.g., 'USER_ADMIN', 'APPLICATION')
            action: Action name (e.g., 'READ', 'CREATE')
            scope: Required scope (e.g., 'SELF', 'ORGANIZATION', 'SYSTEM')
        
        Returns:
            True if permission granted, False otherwise (default DENY)
        """
        permissions = cls.load_permissions()
        required_level = cls.SCOPE_HIERARCHY.get(scope.upper(), 0)

        for role in roles:
            for perm in permissions:
                if perm.get('role') != role:
                    continue
                if perm.get('resource') != resource:
                    continue
                if action not in perm.get('actions', []):
                    continue

                # Check scope hierarchy — allowed scope can be >= required
                allowed_scope = perm.get('scope', 'SELF').upper()
                allowed_level = cls.SCOPE_HIERARCHY.get(allowed_scope, 0)

                if allowed_level >= required_level:
                    return True

        return False  # Default DENY (C-06)

    @classmethod
    def get_permissions_for_role(cls, role: str) -> List[Dict]:
        """Get all permissions for a role."""
        permissions = cls.load_permissions()
        return [p for p in permissions if p.get('role') == role]

    @classmethod
    def reload(cls):
        """Force reload permissions from file (for development)."""
        cls._permissions = None
        cls.load_permissions()

# Singleton
rbac = RBACEngine()