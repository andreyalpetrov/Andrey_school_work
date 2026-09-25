def f(x):
    return (((x % (a-21) == 0)and (x % (40 - a) == 0)) <= (x % 90 == 0))

for a in range(22, 39):
    if all(f(x)==1 for x in range(1, 10**5)):
        print(a)