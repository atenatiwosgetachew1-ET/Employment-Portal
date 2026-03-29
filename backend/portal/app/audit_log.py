import logging

from django.contrib.auth.models import User

from .models import AuditLog

logger = logging.getLogger("app")


def log_audit(
    actor: User | None,
    action: str,
    *,
    resource_type: str = "",
    resource_id: int | None = None,
    summary: str = "",
    metadata: dict | None = None,
) -> AuditLog:
    logger.info(
        "audit action=%s resource=%s id=%s actor=%s",
        action,
        resource_type,
        resource_id,
        getattr(actor, "username", None) if actor else None,
    )
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        resource_type=resource_type or "",
        resource_id=resource_id,
        summary=summary[:2000] if summary else "",
        metadata=metadata or {},
    )
