from random import Random

random = Random(4342)


def roll(dice: str, modifier: int):
    res = 0

    if dice.__eq__("d4"):
        res = random.randint(1, 4)
    elif dice.__eq__("d6"):
        res = random.randint(1, 6)
    elif dice.__eq__("d8"):
        res = random.randint(1, 8)
    elif dice.__eq__("d12"):
        res = random.randint(1, 12)
    elif dice.__eq__("d20"):
        res = random.randint(1, 20)
    elif dice.__eq__("d100"):
        res = random.randint(1, 100)

    res = res + modifier
    return res


def main():
    res = roll("d6", 0)
    res += roll("d6", 0)
    res2 = roll("d6", 0)
    res2 += roll("d6", 0)
    res2 += roll("d6", 0)
    print(res)
    print(res2)

if __name__ == '__main__':
    main()
