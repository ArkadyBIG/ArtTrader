a = list(range(101))

n = 10
a = [a[i: i + n] for i in range(0, len(a), n)]


print(a)


