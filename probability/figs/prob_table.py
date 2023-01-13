p_d = {True: .05, False: .95}
p_z_d = {True: .99, False: .1}


def row(d, z):
    if z:
        return(p_d[d] * (p_z_d[d]))
    else:
        return(p_d[d] * (1 - p_z_d[d]))

a = row(True, True)
b = row(True, False)
c = row(False, True)
d = row(False, False)

print(a)
print(b)
print(c)
print(d)

