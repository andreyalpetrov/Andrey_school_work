# ДЛЯ ВСЕХ: если спрашивают "хотя бы" -> вместо all пишем ANY!
# задача на ДЕЛ(а, х) (простая)
for a in range(1, 1000):
    for x in range(1, 1000000):
        f = (x % a != 0) <= ((x % 6 == 0) <= (x % 4 != 0))
        if f == 0:
            break
    
    else:   #эта часть выполняется только в случае если for
            #не остановился досрочо. Else применяется именно к FOR
        print(a)

# Более кототкий вариант решения:

def f(x):
    return (x % a != 0) <= ((x % 6 == 0) <= (x % 4 != 0))

for a in range(1, 1000):
    if all(f(x) == 1 for x in range(1, 10**6)):
        print(a)


#----------------------------------------------------------

# случай с отрезком [70; 80] и нахождение, когда формула *ложна* 


def f(x):
    return (x % 12 == 0) and (70 <= x <= 80) and (x % a != 0)

for a in range(1, 1000):
    if all (f(x) == 0 for x in range(1, 10**6)):
        print(a)


#----------------------------------------------------------

# задачка на поразрядную конъюнкцию

def f(x):
    return ((x & 84653 != 0) or (x & 51763 != 0)) <= (x & a >0)

for a in range(1, 10000000):
    if all(f(x) == 1 for x in range(10** 7)):
        print(a)


#много поразрядной конъюнкции

def f(x):
    return ((x & 112 != 0) or (x & 86 != 0)) <= ((x & 65 ==0) <= (x % a != 0))

for a in range(1, 1000):
    if all(f(x) == 1 for x in range(1, 10**6)):
        print(a)



#----------------------------------------------------------

# задачка на неравенство с x , y

def f(x, y):
    return (3*y + 2*x < a) or (x > 8) or (y > 12)

for a in range(1, 1000):
    if all(f(x,y) == 1 for x in range(1, 1000) for y in range(1, 1000)):
        print(a)

#----------------------------------------------------------

# ЗАДАЧА НА ТРЕУГОЛЬНИКИ!!!! :

def tr(n, m, k):
    return n+m>k and n + k > m and m + k > n

def f(x):
    return not((tr(x,11,18) == (max(x,5)>68)) and tr(x, a, 5))

for a in range(1, 1000):
    if all(f(x) == 1 for x in range(1, 10**6)):
        print(a)