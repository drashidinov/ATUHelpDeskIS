# Target computer-class rooms (техподдержка)
ROOMS_2B = ["304-2Б","301-2Б","303-2Б","310-2Б","311-2Б","312-2Б","316-2Б","318-2Б","425-2Б",
            "302-2Б","306-2Б","313-2Б","320-2Б","324-2Б","314-2Б","319-2Б","307-2Б","317-2Б",
            "323-2Б","207-2Б","225-2Б","305-2Б","308-2Б","321-2Б","322-2Б"]
ROOMS_GUK = ["508 ГУК","510 ГУК","607 ГУК","610 ГУК"]
ROOMS_2C = ["401-2C","402-2C","403-2C","404-2C","406-2C","407-2C","503-2C","504-2C",
            "405-2C","501-2C","502-2C","505-2C","506-2C","507-2C","508-2C"]

BUILDINGS = {
    "2Б": {"name": "Учебный корпус 2Б", "address": "г. Алматы, мкр-н Тастак-1, ул. Фурката, 348/4"},
    "ГУК": {"name": "Главный учебный корпус", "address": "г. Алматы, ул. Толе би, 100"},
    "2C": {"name": "Учебный корпус 2C", "address": "г. Алматы, мкр-н Тастак-1, ул. Фурката, 348/4"},
}

ALL_ROOMS = []
for r in ROOMS_2B:
    ALL_ROOMS.append({"raw": r, "building": "2Б"})
for r in ROOMS_GUK:
    ALL_ROOMS.append({"raw": r, "building": "ГУК"})
for r in ROOMS_2C:
    ALL_ROOMS.append({"raw": r, "building": "2C"})

CYR2LAT_EQUIV = str.maketrans({
    "А":"A","В":"B","С":"C","Е":"E","К":"K","М":"M","Н":"H","О":"O","Р":"P","Т":"T","Х":"X","У":"Y",
})

def normalize(s: str) -> str:
    s = s.upper()
    s = s.translate(CYR2LAT_EQUIV)
    s = s.replace(" ", "").replace("АУД.", "").replace("АУДИТОРИЯ", "")
    s = s.replace("-", "")
    return s

NORM_TO_RAW = {}
for room in ALL_ROOMS:
    NORM_TO_RAW[normalize(room["raw"])] = room["raw"]

if __name__ == "__main__":
    print(len(ALL_ROOMS), "rooms total")
    for k,v in list(NORM_TO_RAW.items())[:5]:
        print(k, "->", v)

import re

# Matches like 304-2Б, 401-2C, 405 2с, 304а-2Б etc.
RE_BLD = re.compile(r'(\d{3,4}[аА]?)\s*-?\s*(2\s*-?\s*)?([БCСбс])\b')
# Matches like 508 ГУК, ГУК 510, 508ГУК
RE_GUK = re.compile(r'(\d{3})\s*ГУК|ГУК\s*(\d{3})', re.IGNORECASE)

def find_target_rooms_in_text(text: str):
    """Return list of matched canonical room strings (from ALL_ROOMS) found in text."""
    if not text:
        return []
    found = []
    for m in RE_BLD.finditer(text):
        num, letter = m.group(1), m.group(3)
        token = f"{num}-2{letter}"  # canonical form; '2' prefix optional in source, normalized here
        norm = normalize(token)
        if norm in NORM_TO_RAW:
            found.append(NORM_TO_RAW[norm])
    for m in RE_GUK.finditer(text):
        num = m.group(1) or m.group(2)
        token = f"{num} ГУК"
        norm = normalize(token)
        if norm in NORM_TO_RAW:
            found.append(NORM_TO_RAW[norm])
    return found

if __name__ == "__main__":
    tests = [
        "Линейная алгебра лекция Рустемова К, ауд. 523-2б",
        "Архитектура и организация компьютерных систем лабораторная Ибекеев С.Е. 508-С",
        "лекция Онлайн Амирханов Бауржан",
        "ауд. 405-2C",
        "ауд. 508 ГУК",
        "практика ГУК610",
        "ауд. 304-2Б",
    ]
    for t in tests:
        print(t, "->", find_target_rooms_in_text(t))
