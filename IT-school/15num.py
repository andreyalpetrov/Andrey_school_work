def f (x):
    a = set()
    for i in range(2, int(x ** 0.5) + 1):
        if x % i == 0:
            a |= {i, x // i}
    return a

b = f(161)
for y in range(1, 10000):
    C = f(y)
    if len(C) > 0:
        for x in range(1, 30000):
            F = ((x not in b) and (6 <= x <= 46)) or (not(x in C))
            if F != 1:
                break

        else:
            print(y)



# --------------------------

for a in range(0, 10000):
    m = 1
    for x in range(1, 6999):
        for y in range(1, 7000):
            F = (x + y <= 30) or (y <= 2 +x) or (y >= a)
            if F != 1:
                m = 0
                break

        if not m:
            break

    if m: print(a)
