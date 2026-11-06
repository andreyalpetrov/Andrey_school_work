from math import dist


def centr(cl):
    m = []
    for p in cl:
        s = sum(dist(p, p1) for p1 in cl)
        m.append([s, p])

    return min(m)[1]

b = [[],[],[]]
for s in open('filetxt'):
    x, y = [float(d) for d in s.replace(',', '.').split()]

    if x > 5: b[0].append([x, y])
    elif x<= 1.5 and y < 2.5 or x > 1.5 and y < 5.5: b[1].append([x, y])

    else: b[2].append([x, y])
