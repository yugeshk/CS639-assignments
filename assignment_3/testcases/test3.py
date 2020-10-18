d = 0
d_cmp = d >= 3
if d_cmp:
    print(a)
else:
    d_cmp = d >= 2
    if d_cmp:
        a = b
    else:
        d_cmp = d>=1
        if d_cmp:
            b = c
        else:
            c = input()