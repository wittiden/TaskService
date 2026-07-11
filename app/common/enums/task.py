from enum import StrEnum


class TaskImportantLevelEnum(StrEnum):
    """Енум для перечисления уровней важности задачи"""

    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    TRIVIAL = 'trivial'


class TaskScheduleEnum(StrEnum):
    """Енум для перечисления типов задач"""

    URGENT = 'urgent'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'
    POSTPONED = 'postponed'
    BACKLOG = 'backlog'
