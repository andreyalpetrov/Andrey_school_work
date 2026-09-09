from itertools import *

числа = '346 45 16 12567 24 1347 46'.split()
ребра = 'ГЖ ЖЕ ГЕ ГВ ЕВ ЕД ВД ВА ВБ АБ'.split()

print('1 2 3 4 5 6 7')
for p in permutations('АБВГДЕЖ'):
    if all(str(p.index(a) + 1) in числа[p.index(b)] for a, b in ребра):
        print(*p)
        
# код выдаёт номера Нас пунктов