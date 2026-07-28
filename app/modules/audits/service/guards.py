from app.infrastructure.database.model import TaskAuditModel, UserAuditModel
from app.modules.audits.exceptions import UserAuditNotFoundError


class AuditGuards:
    """Класс бизнес правил аудита"""

    @staticmethod
    def require_user_audit_exist(obj: UserAuditModel | None) -> UserAuditModel:
        if obj is None:
            raise UserAuditNotFoundError('User audits obj cant found')

        return obj

    @staticmethod
    def require_task_audit_exist(obj: TaskAuditModel | None) -> TaskAuditModel:
        if obj is None:
            raise UserAuditNotFoundError('User audits obj cant found')

        return obj
