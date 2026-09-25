def f(s, m):
    if s <= 15: return m% 2 == 0
    elif m == 0: return 0
    h = [f(s-3, m-1), f(s-7, m-1), f(s // 4, m-1)]
    return any(h) if (m - 1) % 2 == 0 else all(h)

print([s for s in range(16, 1000) if not f(s, 1) and f(s, 2)])