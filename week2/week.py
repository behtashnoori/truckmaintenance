def main():
    number = get_number()
    meow(number)


def get_number():
    while True:
        n = int(input("what is n:"))
        if n > 0:
            break
            # از خود حلقه کامل خارج میشه
    return n

def meow(n):
    for _ in range(n):
        print("meow")
main()
