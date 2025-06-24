import asyncio


async def print_one():
    for _ in range(10):
        print(1)
        await asyncio.sleep(0)  # Yield to the event loop


async def print_two():
    for _ in range(10):
        print(2)
        await asyncio.sleep(0)  # Yield to the event loop


async def main():
    await asyncio.gather(print_one(), print_two())

asyncio.run(main())
