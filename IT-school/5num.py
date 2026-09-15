def f(n):
    if n == 0:
        return "0"
    digits = "0123456789abcde"
    result = ""

    while n > 0:
        result += digits[n % 15]
        n //= 15
    return result[::-1]

mini=10**10
for n in range(15, 10001):
    r = f(n)
    if n % 15 == 0:
        r += r[:2]
    else:r+=f((n%15)*13)
    r=int(r, 15)
    if r>700 and r<mini:mini=r
print(mini)