import asyncio


async def foo():
    await asyncio.sleep(2)
    print('foo')

async def bar():
    await asyncio.sleep(2)
    print('bar')


async def main():
    t1 = asyncio.create_task(foo())
    t2 = asyncio.create_task(bar())
    await asyncio.gather(t1, t2)

asyncio.run(main())