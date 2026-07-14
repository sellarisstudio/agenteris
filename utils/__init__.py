"""
Utility: human‑readable sizes
"""


def fmt_size(n: int) -> str:
    if n < 1024:
        return f'{n}B'
    if n < 1024 ** 2:
        return f'{n // 1024}KB'
    return f'{n // (1024 ** 2)}MB'
