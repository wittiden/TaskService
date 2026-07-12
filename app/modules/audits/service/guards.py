from app.infrastructure.database.model import UserAuditModel
from app.modules.audits.exceptions import UserAuditNotFoundError


class AuditGuards:
    """Класс бизнес правил аудита"""

    @staticmethod
    def require_user_audit_exist(obj: UserAuditModel | None) -> UserAuditModel:
        if obj is None:
            raise UserAuditNotFoundError('User audits obj cant found')

        return obj
