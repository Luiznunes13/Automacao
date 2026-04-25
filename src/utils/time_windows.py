"""
Utilitários para manipulação de janelas de tempo

Helpers para calcular períodos de coleta de mensagens
"""

from datetime import datetime, timedelta, time
from typing import Tuple
import pytz


def get_last_work_week(
    reference_date: datetime = None,
    timezone: str = "America/Sao_Paulo"
) -> Tuple[datetime, datetime]:
    """
    Retorna a última semana de trabalho completa (segunda 00h00 a sexta 23h59).
    
    Args:
        reference_date: Data de referência (padrão: hoje)
        timezone: Timezone para cálculo (padrão: America/Sao_Paulo)
        
    Returns:
        Tupla (start_datetime, end_datetime)
        
    Exemplo:
        Se hoje é segunda-feira 28/04/2025, retorna:
        - Início: segunda 21/04/2025 00:00:00
        - Fim: sexta 25/04/2025 23:59:59
    """
    tz = pytz.timezone(timezone)
    
    if reference_date is None:
        reference_date = datetime.now(tz)
    elif reference_date.tzinfo is None:
        reference_date = tz.localize(reference_date)
    
    # Encontrar a segunda-feira anterior
    days_since_monday = reference_date.weekday()  # 0 = segunda, 6 = domingo
    
    # Se hoje é segunda, pegar semana anterior
    if days_since_monday == 0:
        days_to_subtract = 7
    else:
        days_to_subtract = days_since_monday + (7 if days_since_monday < 5 else 0)
    
    # Segunda 00:00:00
    last_monday = reference_date - timedelta(days=days_to_subtract)
    start_date = tz.localize(
        datetime.combine(last_monday.date(), time(0, 0, 0))
    )
    
    # Sexta 23:59:59
    last_friday = start_date + timedelta(days=4)
    end_date = tz.localize(
        datetime.combine(last_friday.date(), time(23, 59, 59))
    )
    
    return start_date, end_date


def get_week_range(
    week_offset: int = 0,
    timezone: str = "America/Sao_Paulo"
) -> Tuple[datetime, datetime]:
    """
    Retorna o intervalo de uma semana de trabalho com offset.
    
    Args:
        week_offset: Offset de semanas (0 = esta semana, -1 = semana passada)
        timezone: Timezone
        
    Returns:
        Tupla (start_datetime, end_datetime)
    """
    tz = pytz.timezone(timezone)
    today = datetime.now(tz)
    
    # Encontrar segunda da semana atual
    days_since_monday = today.weekday()
    this_monday = today - timedelta(days=days_since_monday)
    
    # Aplicar offset
    target_monday = this_monday + timedelta(weeks=week_offset)
    
    start_date = tz.localize(
        datetime.combine(target_monday.date(), time(0, 0, 0))
    )
    
    end_date = start_date + timedelta(days=4, hours=23, minutes=59, seconds=59)
    
    return start_date, end_date


def format_period(start: datetime, end: datetime) -> str:
    """
    Formata período para exibição.
    
    Args:
        start: Data inicial
        end: Data final
        
    Returns:
        String formatada ex: "21/04/2025 a 25/04/2025"
    """
    return f"{start.strftime('%d/%m/%Y')} a {end.strftime('%d/%m/%Y')}"


def is_work_day(date: datetime) -> bool:
    """
    Verifica se a data é dia útil (segunda a sexta).
    
    Args:
        date: Data a verificar
        
    Returns:
        True se for dia útil
    """
    return date.weekday() < 5  # 0-4 = seg-sex


def get_current_week_progress(timezone: str = "America/Sao_Paulo") -> dict:
    """
    Retorna informações sobre o progresso da semana atual.
    
    Returns:
        Dict com informações da semana
    """
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    
    days_since_monday = now.weekday()
    this_monday = now - timedelta(days=days_since_monday)
    
    start_date = tz.localize(
        datetime.combine(this_monday.date(), time(0, 0, 0))
    )
    
    end_date = start_date + timedelta(days=4, hours=23, minutes=59, seconds=59)
    
    return {
        "week_start": start_date,
        "week_end": end_date,
        "current_day": now.strftime("%A"),
        "days_elapsed": days_since_monday + 1 if days_since_monday < 5 else 5,
        "is_work_week": is_work_day(now),
        "formatted_period": format_period(start_date, end_date)
    }
