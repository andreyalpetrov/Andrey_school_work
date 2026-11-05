# нахождение делителей числа
def d(x):
    d=set()
    for i in range(2, int(x**0.5)+1):
        if x % i == 0:
            d |= {i, x//i}
    return sorted(d)

# кластеризация

def f(n):
    a = []
    d = 2
    while d**2<=n:
        while n%d == 0:
            n //= d
            a.append(d)
        d+=1
    if n!=1:
        a.append(n)
    return a