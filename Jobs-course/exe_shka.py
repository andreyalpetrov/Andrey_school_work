for a1 in '0123456789':
    for a2 in '0123456789':
        x = int(f'1{a1}34567{a2}9')
        if x % 17 == 0:
            print(x, x //17)