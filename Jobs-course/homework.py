from fnmatch import fnmatch
ans = []

for x in range(1234, 10** 10, 1234):
    if fnmatch(str(x), '4*5*6') and fnmatch(str(x), '?74*68?'):
        ans.append([x, x//1234])
    
ans.reverse()

for a, b in ans:
    print(a, b)
