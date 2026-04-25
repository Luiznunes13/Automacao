"""
Utilitários gerais do sistema
"""

from .time_windows import (
    get_last_work_week,
    get_week_range,
    format_period,
    is_work_day,
    get_current_week_progress
)

__all__ = [
    'get_last_work_week',
    'get_week_range',
    'format_period',
    'is_work_day',
    'get_current_week_progress'
]
