from random import randint, uniform


def get_random_number(value):
    if value == "pi":
        return uniform(0, 3.14159)
    if isint(value):
        number = int(value)
        if number <= 0:
            raise Exception("Ingrese un numero mayor a 0")
        return randint(0, int(value))
    if isfloat(value):
        return uniform(0, float(value))
    return randint(0, 100)


def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True


def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b
