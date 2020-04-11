def fun(st, st2, *_):
    fun2(st, st2, *_)


def fun2(st1: str, st2: str):
    print("{} {}".format(st1, st2))


fun("a", "b")
#fun("a", "b", ())

