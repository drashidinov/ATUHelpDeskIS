import re

CYR_UP = 'А-ЯӘІҢҒҮҰҚӨҺ'
CYR_LOW = 'а-яәіңғүұқөһ'

TEACHER_RE = re.compile(
    rf'([{CYR_UP}][{CYR_LOW}]{{2,}})\s*((?:[{CYR_UP}]\.?\s?){{1,2}})'
)

STOP_WORDS = {
    'Модуль','Введение','Основы','Технология','Технологии','Организация','Разработка',
    'Программирование','Архитектура','История','Иностр','Иностранный','Физическая','Ауд','Аудитория',
    'Практика','Лекция','Дискретная','Линейная','Инженерная','Компьютерные','Высокопроизводительные',
    'Устойчивое','Государственное','Типология','Визуальное','Компьютерная',
}

def extract_teacher(text):
    """Best-effort heuristic: last 'Фамилия И.О.'-like token before end of cell text.
    Not 100% reliable across all schedule formats — used only to group possible
    teacher clashes, not as authoritative source of truth."""
    if not text:
        return None
    matches = list(TEACHER_RE.finditer(text))
    for m in reversed(matches):
        surname = m.group(1)
        initials = m.group(2).strip()
        if surname in STOP_WORDS or not initials:
            continue
        return f"{surname} {initials}"
    return None
