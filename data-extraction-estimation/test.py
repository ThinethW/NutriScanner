def main():
    funcs = [a(), b(), c()]
    v = []
    for func in funcs:
        i = func
        print(i)
        v.append(i)
        if i == "b":
            break
    print(v)


def a():

    return "a"


def b():

    return "b"


def c():

    return "c"

main()