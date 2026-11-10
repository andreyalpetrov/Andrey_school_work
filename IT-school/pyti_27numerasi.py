f = open('27_31521.txt')

from math import dist
a = []

for s in f:
    x, y, vx, vy, m, p = s.replace(',','.').split()
    x, y, vx, vy, m = map(float, [x, y, vx, vy, m])
    e = 0.5 * m * (vx**2 + vy**2)
    a.append( [x, y, vx, vy, m, p, e] )


def rast(t1, t2):
    x1, y1, vx, vy, m, p, e = t1
    x2, y2, vx, vy, m, p, e = t2
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

def centr(cl):
    mn = 10**10
    for t1 in cl:
        s = 0
        for t2 in cl:
            s += abs(t2[-1]-t1[-1])
        if s<mn:
            mn = s
            ot = t1
    return ot

r = 2
# a.sort(key = lambda x: x[-1])


kl = []
while a:
    kl.append( [a.pop(0)] )
    for t1 in kl[-1]:
        for t2 in a:
            mi = kl[-1][0] #min(kl[-1], key=lambda x: x[-1])
            if abs(t2[-1] - mi[-1]) <= r:

                kl[-1].append(t2)
                a.remove(t2)


c= [centr(cl) for cl in kl]

q1 = - 10**10
q2 = max(c, key = lambda x: x[-1])[-1]

for i in range(len(kl)):
    for t1 in kl[i]:
        if t1[-2] == 'II':
            for t2 in kl[i]:
                if t2[-2] == 'II':
                    q1 = max(q1, rast(t1, t2))

print(int(q1*10000), int(q2*10000))

