from fnmatch import *

for x in range(347, 10 ** 8 + 1, 347):
    if fnmatch(str(x), '12??1*56'):
        print(x, x // 347)

# ---------------------------------

from fnmatch import *


def d(x):
    d = set()
    for i in range(2, int(x ** 0.5) + 1):
        if x % i == 0:
            d |= {i, x // i}
    return sorted(d)


for x in range(1, 10 ** 7 + 1):
    if fnmatch(str(x), '12?*45'):
        a = d(x)
        if len(a) == 18:
            print(x, a[-1])

# ---------------------------------


from fnmatch import *

k = 0

for x in range(10980, 10 ** 10, 10980):
    if fnmatch(str(x), '20[13759][13759]22*'):
        if len(str(x)) > 6 and all(z in '02468' for z in str(x)[6:]):
            print(x, x // 10980)
        k += 1
        if k == 6: break

# -----------------------------------

# с семеричной СС

from fnmatch import *


def f(n):
    ot = ''
    ss = 7
    while n != 0:
        ot = str(n % ss) + ot
        n //= ss
    return ot


nch = '13579'
ch = '02468'

for i in range(333, 10 ** 9 + 1, 333):
    s = str(i)
    sm = f(i)
    if fnmatch(sm, '?213*5664'):
        print(i, i // 333)

# ---------------------------------


# тяжелая, без fnmatch
from itertools import *

ch1 = [x for x in '0123456789']
ch2 = [x + y for x in '0123456789' for y in '0123456789']
ch3 = [x + y + z for x in '0123456789' for y in '0123456789' for z in '0123456789']

comb = [''] + ch1 + ch2 + ch3

rez = []

for x in '013456789':
    for z in comb:
        q = int(f'123{x}4{z}5679')
        if q % 4013 == 0:
            rez.append([q, q // 4013])

print(*sorted(rez), sep='\n')

# 123441015679, 30760283
# 123641665679, 30810283
# 123842315679, 30860283

# ---------------------------------

from fnmatch import *

st = 10 ** 10 // 11071 * 11071
k = 0

for x in range(st, 1, -11071):
    if fnmatch(str(x), '?136*1') and str(x)[0] in '13579' and str(x)[-2] in '02468':
        print(x, x // 11071)
        k += 1
        if k == 5: break

# ---------------------------------


for c1 in '2468':
    for c2 in '0123456789':
        for c3 in '0123456789':
            for c4 in '13579':
                for c5 in '02468':
                    x = int(f'{c1}9{c2}23{c3}23{c4}{c5}')
                    if x % 1984 == 0:
                        print(x, x // 1984)