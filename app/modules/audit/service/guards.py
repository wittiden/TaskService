from app.infrastructure.database.model import UserAuditModel
from app.modules.audit.exceptions import UserAuditNotFoundError


class AuditGuards:
    """Класс бизнес правил аудита"""

    @staticmethod
    def require_user_audit_exist(obj: UserAuditModel | None) -> UserAuditModel:
        if obj is None:
            raise UserAuditNotFoundError('User audit obj cant found')

        return obj
