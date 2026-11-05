def f(curr, end):
    if curr > end : return 0
    elif curr == end: return 1
    else: return f(curr + 2, end) + f(curr*2, end)

print(f(1,24))