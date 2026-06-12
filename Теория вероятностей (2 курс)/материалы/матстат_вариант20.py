#!/usr/bin/env python3
"""Вариант 20: интервалы от 0, таблица в горизонтальном формате."""
import math
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

OUT = Path(__file__).parent / "матстат_вар20_результаты"
GAMMA = 0.93
ALPHA = 1 - GAMMA

DATA = np.array(
    [
        0,
        0,
        0,
        0.003,
        0.011,
        0.042,
        0.191,
        0.405,
        0.002,
        0.432,
        0.517,
        0.456,
        0.047,
        0.162,
        0.097,
        0.261,
        0.168,
        0.028,
        0.324,
        0.125,
        0.438,
        0.136,
        0.019,
        0.269,
        0.092,
        0.653,
        0.376,
        0.099,
        0.812,
        0.438,
        0.092,
        0.134,
        0.307,
        0.181,
        0.327,
        0.338,
        0.539,
        0.250,
        0.450,
        0.096,
        0.125,
        0.174,
        0.159,
        0.091,
        0.229,
        0.468,
        0.283,
        0.151,
        0.244,
        0.261,
    ]
)


def fmt(x: float, d: int = 3) -> str:
    return f"{x:.{d}f}".replace(".", ",")


def frac(ni: int, n: int) -> str:
    g = math.gcd(ni, n)
    return f"{ni // g}/{n // g}" if g else f"{ni}/{n}"


def merge_intervals(edges, counts, min_freq=3):
    edges, counts = list(edges), list(counts)
    changed = True
    while changed:
        changed = False
        for i in range(len(counts)):
            if counts[i] < min_freq and len(counts) > 1:
                if i == 0:
                    counts[1] += counts[0]
                    del counts[0]
                    del edges[1]
                elif i == len(counts) - 1:
                    counts[i - 1] += counts[i]
                    del counts[i]
                    del edges[i]
                else:
                    counts[i + 1] += counts[i]
                    del counts[i]
                    del edges[i + 1]
                changed = True
                break
    mids = [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]
    return edges, mids, np.array(counts, dtype=int)


def round_delta(h_exact: float) -> float:
    """Фиксированный шаг по заданию: Δ = 0,1."""
    return 0.1


def build_from_zero(data: np.ndarray, h: float):
    """Полуинтервалы [0; ...), шаг h, без отрицательных границ."""
    x_min, x_max = float(data.min()), float(data.max())
    edges = [0.0]
    while edges[-1] + h < x_max + 1e-12:
        edges.append(round(edges[-1] + h, 10))
    edges.append(round(edges[-1] + h, 10))

    counts = []
    for i in range(len(edges) - 1):
        if i < len(edges) - 2:
            mask = (data >= edges[i]) & (data < edges[i + 1])
        else:
            mask = (data >= edges[i]) & (data <= x_max)
        counts.append(int(mask.sum()))
    return x_min, x_max, edges, counts


def print_horizontal_table(n, edges, mids, counts):
    k = len(counts)
    cum = np.cumsum(counts)
    widths = [edges[i + 1] - edges[i] for i in range(k)]
    density = counts / (n * np.array(widths))

    cols = " | ".join(f"**{j + 1}**" for j in range(k))
    print(f"\n| | {cols} |")
    print(f"|---|{'|'.join(['---'] * k)}|")

    intervals = []
    for i in range(k):
        a, b = edges[i], edges[i + 1]
        # короткая запись: 0,1 вместо 0,100
        intervals.append(
            f"[{fmt(a, 1) if a == int(a) or round(a, 1) == a else fmt(a)}; "
            f"{fmt(b, 1) if b == int(b) or round(b, 1) == b else fmt(b)})"
        )
    print("| **Полуинтервал, X_i** | " + " | ".join(intervals) + " |")

    print("| **Середины C_i** | " + " | ".join(fmt(m) for m in mids) + " |")
    print("| **Абсолютные частоты W_i** | " + " | ".join(str(c) for c in counts) + " |")
    print(
        "| **Относительные W_x** | "
        + " | ".join(frac(int(c), n) for c in counts)
        + " |"
    )
    print("| **Накопленная частота** | " + " | ".join(str(int(s)) for s in cum) + " |")
    print(
        "| **Эмпирическая F*** | "
        + " | ".join(frac(int(s), n) for s in cum)
        + " |"
    )
    print(
        "| **Эмпирическая f*** | "
        + " | ".join(fmt(d, 2) for d in density)
        + " |"
    )


def main():
    OUT.mkdir(exist_ok=True)
    data = DATA
    n = len(data)
    sorted_d = np.sort(data)

    x_min, x_max = float(data.min()), float(data.max())
    k_formula = 1 + 1.44 * math.log(n)
    h_exact = (x_max - x_min) / k_formula
    h = round_delta(h_exact)

    _, _, edges, counts = build_from_zero(data, h)
    edges, mids, counts = merge_intervals(edges, counts, min_freq=3)
    k = len(counts)

    rel = counts / n
    cum = np.cumsum(counts)
    cum_rel = cum / n
    widths = np.diff(edges)
    density = counts / (n * widths)

    x_bar = np.sum(np.array(mids) * counts) / n
    m2 = np.sum(((np.array(mids) - x_bar) ** 2) * counts) / n
    s2 = m2 * n / (n - 1)
    s = math.sqrt(s2)

    print("=" * 70)
    print("Вариант 20 | n = 50 | выбросы не удаляем | Δ = 0,1 | границы от 0")
    print("=" * 70)
    print(f"\nXmin = {fmt(x_min)}, Xmax = {fmt(x_max)}")
    print(f"ln(n) = {math.log(n):.6f}".replace(".", ","))
    print(f"k = 1 + 1,44·ln(n) = {fmt(k_formula, 6)}")
    print(
        f"Δ_точн = (Xmax−Xmin)/k = ({fmt(x_max)}−{fmt(x_min)})/{fmt(k_formula, 3)} "
        f"= {fmt(h_exact, 4)}"
    )
    print(f"Δ = {fmt(h, 1)}  (округление до удобной длины полуинтервала)")
    print("\n### Таблица (горизонтальный формат)\n")
    print_horizontal_table(n, edges, mids, counts)

    print(f"\n### x̄ = {fmt(x_bar, 5)}, s² = {fmt(s2, 5)}, s = {fmt(s, 5)}")

    # графики
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(mids, counts, width=widths * 0.92, edgecolor="black", alpha=0.75)
    ax.plot(mids, counts, "ro-", label="Полигон")
    ax.set_xlabel("x")
    ax.set_ylabel("W_i")
    ax.set_title("Вариант 20: гистограмма и полигон (границы ≥ 0)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.savefig(OUT / "01_гистограмма_полигон.png", dpi=150, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.step(
        np.r_[edges[0], mids, edges[-1]],
        np.r_[0, cum_rel, 1],
        where="mid",
    )
    ax.set_xlabel("x")
    ax.set_ylabel("F*_n")
    ax.set_title("Эмпирическая функция распределения")
    ax.grid(True, alpha=0.3)
    fig.savefig(OUT / "02_кумулята.png", dpi=150, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(mids, density, width=widths * 0.92, edgecolor="black", alpha=0.75)
    ax.plot(mids, density, "r.-")
    ax.set_xlabel("x")
    ax.set_ylabel("f*_n")
    ax.set_title("Эмпирическая плотность")
    ax.grid(True, alpha=0.3)
    fig.savefig(OUT / "03_плотность.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"\nГрафики: {OUT}")


if __name__ == "__main__":
    main()
