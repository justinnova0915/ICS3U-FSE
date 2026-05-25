BORDERS = [('#', 10), ('=', 15)]
BORDERS.reverse()

def getHeader(title: str) -> str:
    header = f" {title} "
    length = 0
    for char, num in BORDERS:
        length += num * 2
        header = f" {header:{char}^{length}} "
        length += 2
    return header[1:-1]

while (title := input("Enter header title: ")) != "quit":
    print(getHeader(title.upper()))