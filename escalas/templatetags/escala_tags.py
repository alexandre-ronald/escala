# escala_enfermagem/templatetags/escala_tags.py
from django import template
from datetime import date

register = template.Library()

@register.filter
def split(value, delimiter):
    """
    Divide uma string por um delimitador e retorna uma lista.
    Uso: {{ "01/4"|split:"/" }} -> ['01', '4']
    """
    if value is None:
        return []
    return str(value).split(delimiter)

@register.filter
def day_number(value):
    """
    Extrai o número do dia de uma string no formato "DD/MM" e remove zeros à esquerda.
    Uso: {{ "01/4"|day_number }} -> '1'
    """
    if value is None:
        return '1'
    split_value = str(value).split('/')
    if split_value:
        return str(split_value[0]).lstrip('0') or '1'
    return '1'

@register.filter
def weekday(value, mes):
    """
    Calcula o dia da semana (0=dom, 6=sáb) para um dia do mês.
    Uso: {{ "1"|weekday:mes_atual }} -> 0 (se for domingo)
    """
    try:
        dia = int(value)
        mes = int(mes)
        ano = date.today().year  # Use o ano atual; ajuste se necessário para ano variável
        dia_semana = date(ano, mes, dia).weekday()
        return dia_semana
    except (ValueError, IndexError):
        return 0

@register.filter
def short_weekday(value):
    """
    Converte o número do dia da semana para abreviação curta.
    Uso: {{ 0|short_weekday }} -> 'DOM'
    """
    dias = ['DOM', 'SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB']
    try:
        return dias[int(value) % 7]
    except (ValueError, IndexError):
        return 'SEG'

@register.filter
def month_name(value):
    """
    Converte número do mês para nome.
    Uso: {{ 4|month_name }} -> 'Abril'
    """
    meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    try:
        return meses.get(int(value), '')
    except ValueError:
        return ''