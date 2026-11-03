# -------------------------------
#  simple tasks with masks

from fnmatch import *

for x in range(18579, 10**10, 18579):
    if fnmatch(str(x), '54?1?3*7'):
        print(x, x // 18579)


# ! если нужно по убыванию:

from fnmatch import fnmatch
ans = []

for x in range(1234, 10** 10, 1234):
    if fnmatch(str(x), '4*5*6') and fnmatch(str(x), '?74*68?'):
        ans.append([x, x//1234])
    
ans.reverse()

for a, b in ans:
    print(a, b)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from fnmatch import *
ans = []

for x in range(117, 10**8, 117):
    if x % 119 != 0 and x % 121 != 0 and fnmatch(str(x), '1?58*129'):
        ans.append([x, x // 117])

for x in range(119, 10**8, 119):
    if x % 117 != 0 and x % 121 != 0 and fnmatch(str(x), '1?58*129'):
        ans.append([x, x // 119])

for x in range(121, 10**8, 121):
    if x % 119 != 0 and x % 119 != 0 and fnmatch(str(x), '1?58*129'):
        ans.append([x, x // 121])

ans.sort()
for a, b in ans:
    print(a, b)

# -------------------------------
# variant without fnmatch

for a1 in '0123456789':
    for a2 in '0123456789':
        x = int(f'1{a1}34567{a2}9')
        if x % 17 == 0:
            print(x, x //17)