#!/usr/bin/env python3
"""Извлечение задач из билетов и раскладка по темам (номерам заданий экзамена)."""

import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
TICKETS = BASE / "Билеты" / "Билеты markdown"
OUT = BASE / "задачи"

TOPICS = {
    1: {
        "file": "01_комбинаторика_и_классическая_вероятность.md",
        "title": "Комбинаторика и классическая вероятность",
        "method": "Сочетания $C_n^k$, размещения $A_n^k$, гипергеометрия, классическая схема $P(A)=m/n$.",
        "lecture": "[лекция_01](../Лекции%20markdown/лекция_01.md), [лекция_03](../Лекции%20markdown/лекция_03.md)",
    },
    2: {
        "file": "02_независимые_события.md",
        "title": "Независимые события и операции над событиями",
        "method": "$P(AB)=P(A)P(B)$; «хотя бы один»: $1-P(\\bar A_1\\bar A_2\\ldots)$; $P(A\\cup B)=P(A)+P(B)-P(AB)$.",
        "lecture": "[лекция_02](../Лекции%20markdown/лекция_02.md)",
    },
    3: {
        "file": "03_полная_вероятность_и_байес.md",
        "title": "Полная вероятность и формула Байеса",
        "method": "$P(A)=\\sum P(H_i)P(A|H_i)$; $P(H_k|A)=\\dfrac{P(H_k)P(A|H_k)}{\\sum P(H_i)P(A|H_i)}$.",
        "lecture": "[лекция_02](../Лекции%20markdown/лекция_02.md)",
    },
    4: {
        "file": "04_дискретная_СВ_закон_распределения.md",
        "title": "Дискретная СВ: закон распределения, $M$, $D$, $F(x)$",
        "method": "Бернулли, гипергеометрия, независимые испытания с разными $p_i$; $M[X]=\\sum x_i p_i$, $D[X]=M[X^2]-(M[X])^2$.",
        "lecture": "[лекция_04](../Лекции%20markdown/лекция_04.md), [лекция_03](../Лекции%20markdown/лекция_03.md)",
    },
    5: {
        "file": "05_непрерывная_СВ.md",
        "title": "Непрерывная СВ: $F(x)$, $f(x)$, $M$, $D$",
        "method": "$f(x)=F'(x)$; $P(a<X<b)=F(b)-F(a)$; $M[X]=\\int x f(x)\\,dx$; нормировка $\\int f=1$.",
        "lecture": "[лекция_04](../Лекции%20markdown/лекция_04.md), [лекция_05](../Лекции%20markdown/лекция_05.md)",
    },
    6: {
        "file": "06_схема_бернулли_наивероятнейшее_число.md",
        "title": "Схема Бернулли: наивероятнейшее число успехов",
        "method": "$P_n(k)=C_n^k p^k q^{n-k}$; сравнение $\\dfrac{P_n(k)}{P_n(k-1)}=\\dfrac{n-k+1}{k}\\cdot\\dfrac{p}{1-p}$; $k^*\\approx\\lfloor(n+1)p\\rfloor$.",
        "lecture": "[лекция_03](../Лекции%20markdown/лекция_03.md)",
    },
    7: {
        "file": "07_вариационный_ряд.md",
        "title": "Вариационный ряд: $\\bar{x}$, размах, мода",
        "method": "$\\bar{x}=\\dfrac{1}{n}\\sum x_i n_i$; $R=x_{\\max}-x_{\\min}$; мода — вариант с max $n_i$.",
        "lecture": "[лекция_11](../Лекции%20markdown/лекция_11.md)",
    },
    8: {
        "file": "08_точечные_оценки.md",
        "title": "Точечные оценки $M$ и $D$ генеральной совокупности",
        "method": "$\\hat{\\mu}=\\bar{x}$; $\\hat{\\sigma}^2=s^2=\\dfrac{1}{n-1}\\sum n_i(x_i-\\bar{x})^2$.",
        "lecture": "[лекция_12](../Лекции%20markdown/лекция_12.md)",
    },
    9: {
        "file": "09_тесты_ОВ_часть_1.md",
        "title": "Тесты ОВ (задание 9): свойства $M$, $D$, законы",
        "method": "$M[aX+b]=aM[X]+b$; $D[aX+b]=a^2D[X]$; биномиальная СВ — дискретная; $\\sum p_i=1$.",
        "lecture": "[лекция_04](../Лекции%20markdown/лекция_04.md), [лекция_05](../Лекции%20markdown/лекция_05.md)",
    },
    10: {
        "file": "10_тесты_ОВ_часть_2.md",
        "title": "Тесты ОВ (задание 10): нормальное распределение",
        "method": "$M[X]=\\mu$ — абсцисса максимума плотности; $h=\\dfrac{1}{\\sigma\\sqrt{2\\pi}}\\Rightarrow\\sigma^2=\\dfrac{1}{2\\pi h^2}$; $N(0,1)$: $M=0$.",
        "lecture": "[лекция_05](../Лекции%20markdown/лекция_05.md)",
    },
}

SOLUTIONS = {1: True, 3: True}


def parse_variant(path: Path) -> tuple[int, dict[int, str]]:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"Вариант\s*№?\s*(\d+)", text)
    num = int(m.group(1)) if m else 0
    tasks: dict[int, str] = {}
    parts = re.split(r"\n###\s+(\d+)\.", text)
    for i in range(1, len(parts), 2):
        task_num = int(parts[i])
        body = parts[i + 1].strip()
        body = re.sub(r"\n---\s*$", "", body).strip()
        # Убрать строку с типом/баллами — она в шапке файла
        body = re.sub(
            r"^\([^)]+\)\s*\n+",
            "",
            body,
            count=1,
        )
        tasks[task_num] = body
    return num, tasks


def points_line(_body: str, full_text: str, task_num: int) -> str:
    m = re.search(rf"###\s+{task_num}\.\s*\([^)]*—\s*(\d+)", full_text)
    if not m:
        m = re.search(rf"###\s+{task_num}\.\s*\([^)]*(\d+)\s*балл", full_text, re.IGNORECASE)
    return m.group(1) if m else "?"


def task_type(body: str) -> str:
    if "ОВ" in body[:120]:
        return "ОВ"
    return "СКО"


def main():
    OUT.mkdir(exist_ok=True)
    all_tasks: dict[int, list[tuple[int, str, str]]] = {i: [] for i in range(1, 11)}

    for ticket in sorted(TICKETS.glob("вариант_*.md")):
        full = ticket.read_text(encoding="utf-8")
        var_num, tasks = parse_variant(ticket)
        for tnum, body in tasks.items():
            if 1 <= tnum <= 10:
                all_tasks[tnum].append((var_num, body, full))

    for tnum, meta in TOPICS.items():
        pts = points_line("", all_tasks[tnum][0][2], tnum) if all_tasks[tnum] else "?"
        ttype = task_type(all_tasks[tnum][0][1]) if all_tasks[tnum] else "?"
        lines = [
            f"# Задание {tnum}. {meta['title']}",
            "",
            f"**Баллы на экзамене:** {pts} · **Тип:** {ttype}",
            "",
            "## Метод",
            "",
            meta["method"],
            "",
            f"**Лекции:** {meta['lecture']}",
            "",
            "---",
            "",
        ]
        for var_num, body, _full in sorted(all_tasks[tnum], key=lambda x: x[0]):
            sol = ""
            if SOLUTIONS.get(var_num) and (OUT.parent / "решения" / f"вариант_{var_num}.md").exists():
                sol = f" · [решение](../решения/вариант_{var_num}.md#{tnum}-задание-{tnum})"
            lines += [
                f"## Вариант {var_num}{sol}",
                "",
                body,
                "",
                "---",
                "",
            ]
        (OUT / meta["file"]).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        print(f"OK: {meta['file']} ({len(all_tasks[tnum])} задач)")

    readme = """# Задачи по темам (из билетов)

Задачи из 7 вариантов экзамена, сгруппированные по **номеру задания** (как на контрольной).

| № | Тема | Файл | Решения |
|---|------|------|---------|
"""
    for tnum, meta in TOPICS.items():
        solved = sum(1 for v, _, _ in all_tasks[tnum] if SOLUTIONS.get(v))
        readme += f"| {tnum} | {meta['title']} | [{meta['file'].replace('.md','')}]({meta['file']}) | {solved}/{len(all_tasks[tnum])} |\n"

    readme += """
**Полные билеты:** [Билеты markdown/](../Билеты/Билеты%20markdown/)  
**Справочник:** [подготовка_к_экзамену.md](../подготовка_к_экзамену.md)
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    print("OK: README.md")


if __name__ == "__main__":
    main()
