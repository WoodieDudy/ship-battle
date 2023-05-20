
cells = []
m = [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0],
    ]
X = 1
Y = 1
for x in range(-1, len(m[0]) + 1):
    for y in range(-1, len(m) + 1):
        if 0 <= y < len(m) and 0 <= x < len(m[0]) and m[y][x] == 1:
            continue
        if any((
                m[y + j][x + i] == 1
                for i in [-1, 0, 1]
                for j in [-1, 0, 1]
                if 0 <= y + j < len(m) and 0 <= x + i < len(m[0])
        )):
            cells.append((X + x, Y + y))

m2 = [
    [0 for _ in range(len(m[0]) + 2)]
    for _ in range(len(m) + 2)
]

for x, y in cells:
    m2[y][x] = 1

for row in m2:
    print(row)