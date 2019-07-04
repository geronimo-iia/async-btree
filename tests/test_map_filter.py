from async_btree import afilter, amap


async def inc(a):
    return a + 1


async def even(a):
    return a % 2 == 0


def test_amap_on_iterable(kernel):
    async def process():
        return [i async for i in amap(inc, [1, 2])]

    assert kernel.run(process) == [2, 3]


def test_afilter_on_iterable(kernel):
    async def process():
        return [i async for i in afilter(even, [0, 1, 2, 3, 4])]

    assert kernel.run(process) == [0, 2, 4]


def test_afilter_amap_aiter(kernel):
    async def process1():
        return [i async for i in afilter(even, amap(inc, [0, 1, 2, 3, 4]))]

    async def process2():
        return [i async for i in amap(inc, afilter(even, [0, 1, 2, 3, 4]))]

    assert kernel.run(process1) == [2, 4]
    assert kernel.run(process2) == [1, 3, 5]
